"""Read a replay into a Game: every player's ages, army, buildings and economy.

Built on the fast parser from mgz (via the mgz-fast package), which walks the
replay's action log from start to end. Nothing is simulated: the counts are the commands players gave (units
queued, buildings placed, technologies researched), which is why a unit that
was queued and then cancelled still counts.
"""

from __future__ import annotations

import io
from collections import Counter
from dataclasses import dataclass, field
from os import PathLike
from typing import BinaryIO

from . import ids
from .classify import Opening, classify, signals
from .names import civ_name, map_name

AGES = ("dark", "feudal", "castle", "imperial")


class ReplayError(Exception):
    """The file could not be read as an Age of Empires II: DE replay."""


@dataclass
class Player:
    number: int
    name: str
    profile_id: int
    civ_id: int
    civ: str
    team: int
    color: int
    # Milliseconds of game time; None if the player never got there.
    feudal_ms: int | None = None
    castle_ms: int | None = None
    imperial_ms: int | None = None
    # Per age: villagers queued, and other units, buildings and technologies by ID.
    villagers: dict[str, int] = field(default_factory=lambda: dict.fromkeys(AGES, 0))
    units: dict[str, Counter] = field(default_factory=lambda: {a: Counter() for a in AGES})
    buildings: dict[str, Counter] = field(default_factory=lambda: {a: Counter() for a in AGES})
    techs: dict[str, Counter] = field(default_factory=lambda: {a: Counter() for a in AGES})
    market_buys: list[dict] = field(default_factory=list)
    market_sells: list[dict] = field(default_factory=list)
    tributes: list[dict] = field(default_factory=list)
    wall_segments: int = 0
    deletions: int = 0
    actions: int = 0
    resigned: bool = False
    # True or False only when it can be read off resignations; otherwise None.
    won: bool | None = None
    opening: Opening | None = None
    # Every unit queued: (game ms, unit ID, amount, is villager).
    production: list[tuple[int, int, int, bool]] = field(default_factory=list)

    def apm(self, duration_ms: int) -> float:
        """Commands per minute of game time. Every command counts, so this is
        raw APM rather than an effective (eAPM) figure."""
        return round(self.actions / max(duration_ms / 60_000, 1), 1)


@dataclass
class Game:
    duration_ms: int
    map_id: int | None
    map: str | None
    rated: bool | None
    game_version: str
    save_version: float | None
    players: list[Player]


def _read(source: str | PathLike | bytes | BinaryIO) -> bytes:
    if isinstance(source, bytes):
        return source
    if hasattr(source, "read"):
        return source.read()
    with open(source, "rb") as f:
        return f.read()


def analyze(source: str | PathLike | bytes | BinaryIO) -> Game:
    """Parse a .aoe2record (a path, the bytes, or an open binary file)."""
    data = _read(source)
    try:
        from mgz.fast import Action, Operation, meta, operation
        from mgz.fast.header import parse as parse_header

        buf = io.BytesIO(data)
        header = parse_header(buf)
        body = io.BytesIO(data[buf.tell():])
        de = header.get("de") or {}

        players: dict[int, Player] = {}
        for p in de.get("players", []):
            number = p.get("number", 0)
            if number < 1:
                continue
            raw = p.get("name", b"")
            name = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
            civ_id = p.get("civilization_id", 0)
            players[number] = Player(
                number=number,
                name=name.strip("\x00").strip(),
                profile_id=p.get("profile_id", 0) or 0,
                civ_id=civ_id,
                civ=civ_name(civ_id),
                team=p.get("team_id", -1),
                color=p.get("color_id", number - 1),
            )
        if not players:
            raise ReplayError("no players in the replay header")

        age = dict.fromkeys(players, "dark")
        game_ms = 0
        meta(body)
        while True:
            try:
                op, payload = operation(body)
            except EOFError:
                break
            if op == Operation.SYNC:
                game_ms += payload[0]
                continue
            if op != Operation.ACTION:
                continue

            action, a = payload
            player = players.get(a.get("player_id", 0))
            if player is None:
                continue
            player.actions += 1
            current = age[player.number]

            if getattr(action, "name", "") == "RESIGN":
                player.resigned = True
            elif action == Action.RESEARCH:
                tech = a.get("technology_id", 0)
                if tech == ids.FEUDAL_AGE and player.feudal_ms is None:
                    player.feudal_ms, current = game_ms, "feudal"
                elif tech == ids.CASTLE_AGE and player.castle_ms is None:
                    player.castle_ms, current = game_ms, "castle"
                elif tech == ids.IMPERIAL_AGE and player.imperial_ms is None:
                    player.imperial_ms, current = game_ms, "imperial"
                age[player.number] = current
                # The age-up itself is counted in the age it leads to.
                player.techs[current][tech] += 1
            elif action in (Action.DE_QUEUE, Action.QUEUE, Action.MULTIQUEUE):
                unit = a.get("unit_id", 0)
                amount = a.get("amount", 1)
                villager = unit in ids.VILLAGERS
                if villager:
                    player.villagers[current] += amount
                else:
                    player.units[current][unit] += amount
                player.production.append((game_ms, unit, amount, villager))
            elif action == Action.BUILD:
                player.buildings[current][a.get("building_id", 0)] += 1
            elif action == Action.WALL:
                player.buildings[current][a.get("building_id", 0)] += 1
                player.wall_segments += 1
            elif action in (Action.BUY, Action.SELL):
                trade = {"resource_id": a.get("resource_id", 0), "amount": a.get("amount", 0), "ms": game_ms}
                (player.market_buys if action == Action.BUY else player.market_sells).append(trade)
            elif action == Action.DE_TRIBUTE:
                player.tributes.append({
                    "to": a.get("player_id_to", 0),
                    **{r: a.get(r, 0) for r in ("food", "wood", "stone", "gold")},
                    "ms": game_ms,
                })
            elif action == Action.DELETE:
                player.deletions += len(a.get("object_ids") or []) or 1
    except ReplayError:
        raise
    except Exception as e:  # mgz raises many kinds of errors on unreadable files
        raise ReplayError(f"could not parse the replay: {e}") from e

    _settle_outcome(players)
    for player in players.values():
        player.opening = classify(signals(
            civ=player.civ,
            feudal_ms=player.feudal_ms,
            castle_ms=player.castle_ms,
            dark_units=player.units["dark"],
            feudal_units=player.units["feudal"],
            feudal_buildings=player.buildings["feudal"],
            castle_units=player.units["castle"],
            castle_buildings=player.buildings["castle"],
        ))

    map_id = de.get("rms_map_id")
    return Game(
        duration_ms=game_ms,
        map_id=map_id,
        map=map_name(map_id),
        rated=de.get("rated"),
        game_version=str(header.get("game_version", "")),
        save_version=header.get("save_version"),
        players=sorted(players.values(), key=lambda p: p.number),
    )


def _settle_outcome(players: dict[int, Player]) -> None:
    """Who won, as far as resignations tell. A team whose players all
    resigned lost; if exactly one team is left standing, it won. Anything
    else (no resignations, or more than one team left) stays unknown."""
    teams: dict[int, list[Player]] = {}
    for p in players.values():
        # Players without a team play for themselves.
        teams.setdefault(p.team if p.team > 1 else -p.number, []).append(p)
    lost = {t for t, members in teams.items() if all(m.resigned for m in members)}
    standing = set(teams) - lost
    if not lost or len(standing) != 1:
        return
    for team, members in teams.items():
        for m in members:
            m.won = team in standing
