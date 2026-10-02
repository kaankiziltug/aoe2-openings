"""Name a player's opening from what they built in the first three ages.

The classifier is a list of rules, checked in order; the first one that
matches names the opening. Every rule reads the same handful of signals
(militia in the Dark Age, archers in the Feudal Age, how long Feudal to Castle
took, and so on), and the result says which rule matched and what the signals
were, so any call can be checked and argued with. OPENINGS.md lists the rules
in plain English.

These are the rules AoE2Meta used to classify more than half a million ranked
1v1 games, unchanged, so results line up with what the site showed.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass

from . import ids

# Feudal to Castle in less than this, with almost no army, is a fast castle.
FAST_CASTLE_MS = 9 * 60_000


@dataclass(frozen=True)
class Signals:
    """What the rules look at. Unit counts are units queued, per age."""

    civ: str
    dark_militia: int
    feudal_archers: int  # Archers and Crossbowmen
    feudal_men_at_arms: int  # Militia and Men-at-Arms queued in the Feudal Age
    feudal_scouts: int  # Scout Cavalry and Light Cavalry
    feudal_skirmishers: int
    feudal_spears: int  # Spearmen and Pikemen
    feudal_serjeants: int
    feudal_towers: int  # Watch Towers, Guard Towers and Keeps placed
    feudal_archery_range: bool
    feudal_stable: bool
    feudal_siege_workshop: bool
    feudal_monastery: bool
    feudal_town_center: bool
    feudal_donjon: bool
    castle_elephants: int
    castle_scorpions: int
    castle_rams: int
    castle_town_center: bool
    feudal_to_castle_ms: int | None  # None if the player never reached both ages

    @property
    def drush(self) -> bool:
        return self.dark_militia >= 3

    @property
    def fast_castle(self) -> bool:
        army = self.feudal_men_at_arms + self.feudal_archers + self.feudal_scouts
        return (
            self.feudal_to_castle_ms is not None
            and self.feudal_to_castle_ms < FAST_CASTLE_MS
            and army < 4
        )


@dataclass(frozen=True)
class Rule:
    id: str
    opening: str
    test: Callable[[Signals], bool]
    reason: str


@dataclass(frozen=True)
class Opening:
    name: str
    rule: str
    reason: str
    signals: Signals

    def to_dict(self) -> dict:
        signals = asdict(self.signals)
        signals["drush"] = self.signals.drush
        signals["fast_castle"] = self.signals.fast_castle
        return {"name": self.name, "rule": self.rule, "reason": self.reason, "signals": signals}


# Checked top to bottom; the first match wins. Civilization openings come
# first, then the openings a single building gives away, then the strongest
# army signals, and the loosest guesses last.
RULES: tuple[Rule, ...] = (
    # Civilization openings
    Rule("serjeant_rush", "Serjeant Rush",
         lambda s: s.civ == "Sicilians" and (s.feudal_donjon or s.feudal_serjeants >= 2),
         "Sicilians with a Donjon or 2+ Serjeants in the Feudal Age"),
    Rule("elephant_rush", "Elephant Rush",
         lambda s: s.civ in ids.ELEPHANT_CIVS and s.castle_elephants >= 4,
         "Khmer, Burmese, Malay or Vietnamese with 4+ Battle Elephants in the Castle Age"),
    Rule("cumans_2tc", "2TC Feudal Boom",
         lambda s: s.civ == "Cumans" and s.feudal_town_center,
         "Cumans building a second Town Center in the Feudal Age"),
    Rule("roman_siege", "Scorpions & Rams",
         lambda s: s.civ == "Romans" and s.castle_scorpions >= 2 and s.castle_rams >= 1,
         "Romans with 2+ Scorpions and a Ram in the Castle Age"),
    # A building gives it away
    Rule("hoang_rush", "Hoang Rush",
         lambda s: s.feudal_siege_workshop,
         "A Siege Workshop in the Feudal Age"),
    Rule("tower_rush", "Tower Rush",
         lambda s: s.feudal_towers >= 3,
         "3+ towers placed in the Feudal Age"),
    # Dark Age militia, and what followed
    Rule("drush_fc", "Drush FC",
         lambda s: s.drush and s.fast_castle,
         "3+ Militia in the Dark Age, then a fast castle"),
    Rule("drush_archers", "Drush Archers",
         lambda s: s.drush and s.feudal_archers >= 3,
         "3+ Militia in the Dark Age, then 3+ Archers in the Feudal Age"),
    Rule("drush_maa", "Drush M@A",
         lambda s: s.drush and s.feudal_men_at_arms >= 2,
         "3+ Militia in the Dark Age, then 2+ Men-at-Arms in the Feudal Age"),
    Rule("drush", "Drush",
         lambda s: s.drush,
         "3+ Militia in the Dark Age"),
    # Feudal Age army
    Rule("maa_archers", "M@A Archers",
         lambda s: s.feudal_men_at_arms >= 2 and s.feudal_archers >= 3,
         "2+ Men-at-Arms and 3+ Archers in the Feudal Age"),
    Rule("maa_rush", "M@A Rush",
         lambda s: s.feudal_men_at_arms >= 4,
         "4+ Men-at-Arms in the Feudal Age"),
    Rule("archer_rush", "Archer Rush",
         lambda s: s.feudal_archers >= 4,
         "4+ Archers in the Feudal Age"),
    Rule("scout_rush", "Scout Rush",
         lambda s: s.feudal_scouts >= 3 and s.feudal_stable,
         "3+ Scouts in the Feudal Age, with a Stable"),
    Rule("maa_scouts", "M@A Scouts",
         lambda s: s.feudal_men_at_arms >= 2 and s.feudal_scouts >= 2,
         "2+ Men-at-Arms and 2+ Scouts in the Feudal Age"),
    Rule("pike_skirm", "Pike Skirm",
         lambda s: s.feudal_skirmishers >= 2 and s.feudal_spears >= 2,
         "2+ Skirmishers and 2+ Spearmen in the Feudal Age"),
    # Fast castle
    Rule("fc_boom", "FC Boom",
         lambda s: s.fast_castle and s.castle_town_center,
         "Feudal to Castle in under 9 minutes with fewer than 4 military units, then a new Town Center"),
    Rule("fast_castle", "Fast Castle",
         lambda s: s.fast_castle,
         "Feudal to Castle in under 9 minutes with fewer than 4 military units"),
    # Looser signals
    Rule("monk_rush", "Monk Rush",
         lambda s: s.feudal_monastery and s.feudal_archers < 2
         and s.feudal_men_at_arms < 2 and s.feudal_scouts < 2,
         "A Monastery in the Feudal Age and almost no other army"),
    Rule("archer_rush_light", "Archer Rush",
         lambda s: s.feudal_archers >= 2 and s.feudal_archery_range,
         "2+ Archers in the Feudal Age, with an Archery Range"),
    Rule("scout_rush_light", "Scout Rush",
         lambda s: s.feudal_scouts >= 2 and s.feudal_stable,
         "2+ Scouts in the Feudal Age, with a Stable"),
    Rule("maa_rush_light", "M@A Rush",
         lambda s: s.feudal_men_at_arms >= 2,
         "2+ Men-at-Arms in the Feudal Age"),
    # Only the buildings to go on
    Rule("archer_opening", "Archer Opening",
         lambda s: s.feudal_archery_range and not s.feudal_stable,
         "An Archery Range but no Stable in the Feudal Age, and no army to match"),
    Rule("scout_opening", "Scout Opening",
         lambda s: s.feudal_stable and not s.feudal_archery_range,
         "A Stable but no Archery Range in the Feudal Age, and no army to match"),
    Rule("scouts_into_archers", "Scouts into Archers",
         lambda s: s.feudal_archery_range and s.feudal_stable,
         "A Stable and an Archery Range in the Feudal Age, and no army to match"),
)

OTHER = Rule("other", "Other", lambda s: True, "None of the rules matched")


def _count(units: Mapping[int, int], *unit_ids: int) -> int:
    return sum(units.get(u, 0) for u in unit_ids)


def _has(buildings: Mapping[int, int], building_ids) -> bool:
    return any(buildings.get(b, 0) > 0 for b in building_ids)


def signals(
    *,
    civ: str,
    feudal_ms: int | None,
    castle_ms: int | None,
    dark_units: Mapping[int, int],
    feudal_units: Mapping[int, int],
    feudal_buildings: Mapping[int, int],
    castle_units: Mapping[int, int] | None = None,
    castle_buildings: Mapping[int, int] | None = None,
) -> Signals:
    """Reduce per-age unit and building counts to what the rules read."""
    castle_units = castle_units or Counter()
    castle_buildings = castle_buildings or Counter()
    return Signals(
        civ=civ,
        dark_militia=_count(dark_units, ids.MILITIA),
        feudal_archers=_count(feudal_units, ids.ARCHER, ids.CROSSBOWMAN),
        feudal_men_at_arms=_count(feudal_units, ids.MILITIA, ids.MAN_AT_ARMS),
        feudal_scouts=_count(feudal_units, ids.SCOUT_CAVALRY, ids.LIGHT_CAVALRY),
        feudal_skirmishers=_count(feudal_units, ids.SKIRMISHER),
        feudal_spears=_count(feudal_units, ids.SPEARMAN, ids.PIKEMAN),
        feudal_serjeants=_count(feudal_units, ids.SERJEANT),
        feudal_towers=_count(feudal_buildings, ids.WATCH_TOWER, ids.GUARD_TOWER, ids.KEEP),
        feudal_archery_range=_has(feudal_buildings, ids.ARCHERY_RANGES),
        feudal_stable=_has(feudal_buildings, ids.STABLES),
        feudal_siege_workshop=_has(feudal_buildings, {ids.SIEGE_WORKSHOP}),
        feudal_monastery=_has(feudal_buildings, {ids.MONASTERY}),
        feudal_town_center=_has(feudal_buildings, {ids.TOWN_CENTER}),
        feudal_donjon=_has(feudal_buildings, {ids.DONJON}),
        castle_elephants=_count(castle_units, ids.BATTLE_ELEPHANT),
        castle_scorpions=_count(castle_units, ids.SCORPION, ids.HEAVY_SCORPION),
        castle_rams=_count(castle_units, ids.BATTERING_RAM, ids.CAPPED_RAM, ids.SIEGE_RAM),
        castle_town_center=_has(castle_buildings, {ids.TOWN_CENTER}),
        feudal_to_castle_ms=(castle_ms - feudal_ms) if feudal_ms and castle_ms else None,
    )


def classify(s: Signals) -> Opening:
    """The first rule that matches, as an Opening that says why."""
    rule = next((r for r in RULES if r.test(s)), OTHER)
    return Opening(name=rule.opening, rule=rule.id, reason=rule.reason, signals=s)


def openings() -> list[str]:
    """Every opening the classifier can return, in rule order."""
    return list(dict.fromkeys([r.opening for r in RULES] + [OTHER.opening]))
