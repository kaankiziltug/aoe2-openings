"""Each rule, and the order they are checked in, on hand-built games."""

from collections import Counter

import pytest

from aoe2_openings import RULES, classify, openings, signals
from aoe2_openings import ids

MIN = 60_000


def game(civ="Franks", feudal=10 * MIN, castle=20 * MIN, dark=None, f_units=None, f_build=None, c_units=None, c_build=None):
    return classify(signals(
        civ=civ,
        feudal_ms=feudal,
        castle_ms=castle,
        dark_units=Counter(dark or {}),
        feudal_units=Counter(f_units or {}),
        feudal_buildings=Counter(f_build or {}),
        castle_units=Counter(c_units or {}),
        castle_buildings=Counter(c_build or {}),
    ))


RANGE, STABLE = 10, 86

CASES = [
    ("serjeant_rush", dict(civ="Sicilians", f_build={ids.DONJON: 1})),
    ("serjeant_rush", dict(civ="Sicilians", f_units={ids.SERJEANT: 2})),
    ("elephant_rush", dict(civ="Khmer", c_units={ids.BATTLE_ELEPHANT: 4})),
    ("cumans_2tc", dict(civ="Cumans", f_build={ids.TOWN_CENTER: 1})),
    ("roman_siege", dict(civ="Romans", c_units={ids.SCORPION: 2, ids.CAPPED_RAM: 1})),
    ("hoang_rush", dict(f_build={ids.SIEGE_WORKSHOP: 1})),
    ("tower_rush", dict(f_build={ids.WATCH_TOWER: 3})),
    ("drush_fc", dict(dark={ids.MILITIA: 3}, castle=17 * MIN)),
    ("drush_archers", dict(dark={ids.MILITIA: 3}, f_units={ids.ARCHER: 3})),
    ("drush_maa", dict(dark={ids.MILITIA: 3}, f_units={ids.MAN_AT_ARMS: 2})),
    ("drush", dict(dark={ids.MILITIA: 3})),
    ("maa_archers", dict(f_units={ids.MAN_AT_ARMS: 2, ids.ARCHER: 3})),
    ("maa_rush", dict(f_units={ids.MILITIA: 1, ids.MAN_AT_ARMS: 3})),
    ("archer_rush", dict(f_units={ids.ARCHER: 2, ids.CROSSBOWMAN: 2})),
    ("scout_rush", dict(f_units={ids.SCOUT_CAVALRY: 3}, f_build={STABLE: 1})),
    ("maa_scouts", dict(f_units={ids.MAN_AT_ARMS: 2, ids.SCOUT_CAVALRY: 2})),
    ("pike_skirm", dict(f_units={ids.SKIRMISHER: 2, ids.SPEARMAN: 2})),
    ("fc_boom", dict(castle=18 * MIN, c_build={ids.TOWN_CENTER: 1})),
    ("fast_castle", dict(castle=18 * MIN)),
    ("monk_rush", dict(f_build={ids.MONASTERY: 1})),
    ("archer_rush_light", dict(f_units={ids.ARCHER: 2}, f_build={RANGE: 1})),
    ("scout_rush_light", dict(f_units={ids.SCOUT_CAVALRY: 2}, f_build={STABLE: 1})),
    ("maa_rush_light", dict(f_units={ids.MAN_AT_ARMS: 2})),
    ("archer_opening", dict(f_build={RANGE: 1})),
    ("scout_opening", dict(f_build={STABLE: 1})),
    ("scouts_into_archers", dict(f_build={RANGE: 1, STABLE: 1})),
    ("other", dict()),
]


@pytest.mark.parametrize("rule, kwargs", CASES, ids=[f"{r}-{i}" for i, (r, _) in enumerate(CASES)])
def test_each_rule(rule, kwargs):
    assert game(**kwargs).rule == rule


def test_every_rule_has_a_case():
    assert {r.id for r in RULES} | {"other"} == {rule for rule, _ in CASES}


def test_civ_openings_need_the_civ():
    assert game(civ="Franks", f_build={ids.DONJON: 1}).rule == "other"
    assert game(civ="Franks", c_units={ids.BATTLE_ELEPHANT: 6}).rule == "other"


def test_order_decides_overlaps():
    # Militia in the Dark Age and archers after: the drush rule comes first.
    assert game(dark={ids.MILITIA: 3}, f_units={ids.ARCHER: 5}).rule == "drush_archers"
    # A Feudal siege workshop outranks everything after it.
    assert game(dark={ids.MILITIA: 4}, f_build={ids.SIEGE_WORKSHOP: 1}).rule == "hoang_rush"
    # Archers and men-at-arms together are their own opening.
    assert game(f_units={ids.MAN_AT_ARMS: 4, ids.ARCHER: 4}).rule == "maa_archers"


def test_fast_castle_needs_both_ages_and_little_army():
    assert not game(feudal=None, castle=None).signals.fast_castle
    assert game(castle=18 * MIN, f_units={ids.ARCHER: 4}).rule == "archer_rush"
    assert game(castle=19 * MIN + 1).rule != "fast_castle"


def test_opening_explains_itself():
    o = game(dark={ids.MILITIA: 3}, f_units={ids.ARCHER: 3})
    data = o.to_dict()
    assert data["name"] == "Drush Archers"
    assert data["signals"]["dark_militia"] == 3 and data["signals"]["drush"] is True
    assert "Militia" in data["reason"]


def test_openings_list():
    names = openings()
    assert names[0] == "Serjeant Rush" and names[-1] == "Other"
    assert len(names) == len(set(names))
