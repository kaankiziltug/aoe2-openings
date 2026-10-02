"""Turn a Game into plain data: names next to IDs, times as m:ss, ready for JSON."""

from __future__ import annotations

from collections import Counter

from .names import object_name, resource_name, tech_name
from .parse import AGES, Game, Player


def clock(ms: int | None) -> str | None:
    """Game time as m:ss (or h:mm:ss), or None."""
    if ms is None:
        return None
    s = ms // 1000
    h, m, s = s // 3600, s // 60 % 60, s % 60
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


def _named(counts: Counter, name) -> list[dict]:
    rows = [{"id": i, "name": name(i), "count": c} for i, c in counts.items()]
    return sorted(rows, key=lambda r: (-r["count"], r["name"]))


def timeline(player: Player, duration_ms: int, step_ms: int = 30_000) -> list[dict]:
    """Running totals of military units and villagers queued, every step_ms."""
    events = sorted(player.production)
    rows, military, villagers, i = [], 0, 0, 0
    for t in range(0, duration_ms + step_ms, step_ms):
        while i < len(events) and events[i][0] <= t:
            _, _, amount, villager = events[i]
            if villager:
                villagers += amount
            else:
                military += amount
            i += 1
        rows.append({"ms": t, "military": military, "villagers": villagers})
    return rows


def player_dict(p: Player, duration_ms: int, *, with_timeline: bool = False) -> dict:
    trade = lambda t: {**t, "resource": resource_name(t["resource_id"]), "time": clock(t["ms"])}
    out = {
        "number": p.number,
        "name": p.name,
        "profile_id": p.profile_id,
        "civ": p.civ,
        "civ_id": p.civ_id,
        "team": p.team,
        "color": p.color,
        "won": p.won,
        "resigned": p.resigned,
        "opening": p.opening.to_dict() if p.opening else None,
        "ages": {
            "feudal": {"ms": p.feudal_ms, "time": clock(p.feudal_ms)},
            "castle": {"ms": p.castle_ms, "time": clock(p.castle_ms)},
            "imperial": {"ms": p.imperial_ms, "time": clock(p.imperial_ms)},
        },
        "villagers": {**p.villagers, "total": sum(p.villagers.values())},
        "units": {age: _named(p.units[age], object_name) for age in AGES},
        "buildings": {age: _named(p.buildings[age], object_name) for age in AGES},
        "techs": {age: _named(p.techs[age], tech_name) for age in AGES},
        "market": {"buys": [trade(t) for t in p.market_buys], "sells": [trade(t) for t in p.market_sells]},
        "tributes": [{**t, "time": clock(t["ms"])} for t in p.tributes],
        "wall_segments": p.wall_segments,
        "deletions": p.deletions,
        "actions": p.actions,
        "apm": p.apm(duration_ms),
    }
    if with_timeline:
        out["timeline"] = timeline(p, duration_ms)
    return out


def game_dict(game: Game, *, with_timeline: bool = False) -> dict:
    return {
        "map": game.map,
        "map_id": game.map_id,
        "rated": game.rated,
        "duration": {"ms": game.duration_ms, "time": clock(game.duration_ms)},
        "game_version": game.game_version,
        "save_version": game.save_version,
        "players": [player_dict(p, game.duration_ms, with_timeline=with_timeline) for p in game.players],
    }
