"""Real replays, if there are any to test with.

Put .aoe2record files in tests/replays/, or point AOE2_REPLAYS at a folder
of them. Without any, these tests are skipped.
"""

import json
import os
from pathlib import Path

import pytest

from aoe2_openings import ReplayError, analyze, game_dict
from aoe2_openings.cli import main

FOLDERS = [Path(__file__).parent / "replays"] + ([Path(os.environ["AOE2_REPLAYS"])] if os.environ.get("AOE2_REPLAYS") else [])
REPLAYS = sorted(p for folder in FOLDERS if folder.is_dir() for p in folder.glob("*.aoe2record"))

needs_replays = pytest.mark.skipif(not REPLAYS, reason="no replays in tests/replays or AOE2_REPLAYS")


@needs_replays
@pytest.mark.parametrize("path", REPLAYS, ids=[p.name for p in REPLAYS])
def test_replay(path):
    game = analyze(path)
    assert game.duration_ms > 0
    assert len(game.players) >= 2
    for p in game.players:
        assert p.opening is not None and p.opening.name
        assert p.civ and not p.civ.startswith("Civ ")
        ages = [t for t in (p.feudal_ms, p.castle_ms, p.imperial_ms) if t is not None]
        assert ages == sorted(ages)
    # Everything survives the trip to JSON.
    json.dumps(game_dict(game, with_timeline=True))


@needs_replays
def test_cli(capsys):
    assert main([str(REPLAYS[0])]) == 0
    assert "why:" in capsys.readouterr().out
    assert main([str(REPLAYS[0]), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["players"]


def test_not_a_replay(tmp_path):
    bad = tmp_path / "bad.aoe2record"
    bad.write_bytes(b"not a replay")
    with pytest.raises(ReplayError):
        analyze(bad)
