"""Readable names for the IDs in a replay, from the aoc-reference-data project.

A replay stores civilizations, maps, units, buildings and technologies as
numbers. The names come from aocref's Definitive Edition dataset, so they are
only as current as the installed aocref: after a new civilization or map is
added to the game, update aocref to get its name.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

RESOURCES = {0: "Food", 1: "Wood", 2: "Stone", 3: "Gold"}


@lru_cache(maxsize=1)
def _dataset() -> dict:
    import aocref

    path = Path(aocref.__file__).parent / "data" / "datasets" / "100.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _lookup(section: str, key: int) -> str | None:
    value = _dataset().get(section, {}).get(str(key))
    if isinstance(value, dict):
        value = value.get("name")
    return value or None


def civ_name(civ_id: int) -> str:
    """The civilization's name. Keys follow the replay header's numbering
    (1 = Britons, 2 = Franks, ...), not aocref's own ``id`` field."""
    return _lookup("civilizations", civ_id) or f"Civ {civ_id}"


def map_name(map_id: int | None) -> str | None:
    return _lookup("maps", map_id) if map_id is not None else None


def object_name(object_id: int) -> str:
    return _lookup("objects", object_id) or f"Object {object_id}"


def tech_name(tech_id: int) -> str:
    return _lookup("technologies", tech_id) or f"Technology {tech_id}"


def resource_name(resource_id: int) -> str:
    return RESOURCES.get(resource_id, f"Resource {resource_id}")
