# aoe2-openings

Read an Age of Empires II: Definitive Edition replay and get, for every player,
the **opening** they played, their **age-up times**, the **army, buildings and
technologies** of each age, and their **economy**: market trades, tributes, APM.

Every opening comes with the rule that named it and the counts behind it, so a
call is never a black box:

```text
$ aoe2-openings game.aoe2record
game.aoe2record
  Arabia · 22:33 · rated
  1. Player 1 (Chinese)  won
     Scout Rush  ·  Feudal 6:14  Castle 15:24  Imperial -  ·  43 villagers  ·  99.3 APM
     why: 3+ Scouts in the Feudal Age, with a Stable
  2. Player 2 (Britons)  lost
     Archer Rush  ·  Feudal 6:38  Castle 17:50  Imperial -  ·  48 villagers  ·  74.6 APM
     why: 4+ Archers in the Feudal Age
```

Age times are when the player clicked to advance, in game time.

These are the rules [AoE2Meta](https://kaankiziltug.com/blog/aoe2meta) used to
classify more than half a million ranked 1v1 games and show which play styles
win, by civilization, map and ELO. [OPENINGS.md](OPENINGS.md) lists all 25 of
them in plain English.

## Install

Not on PyPI yet; install it straight from GitHub:

```bash
pip install git+https://github.com/kaankiziltug/aoe2-openings
```

Python 3.10 or newer. It reads replays with
[mgz-fast](https://github.com/AoEInsights/aoc-mgz), AoE2Insights' fork of
[mgz](https://github.com/happyleavesaoc/aoc-mgz) that keeps up with the
latest game patches, and names units, maps and civilizations with
[aocref](https://github.com/SiegeEngineers/aoc-reference-data).

## Use it

From the command line, for one replay or many:

```bash
aoe2-openings game.aoe2record                      # a short summary
aoe2-openings game.aoe2record --json               # everything, as JSON
aoe2-openings replays/*.aoe2record --json --timeline > games.json
```

From Python:

```python
from aoe2_openings import analyze

game = analyze("game.aoe2record")      # a path, bytes, or an open binary file
print(game.map, game.duration_ms)

for p in game.players:
    print(p.name, p.civ, p.opening.name)
    print("  why:", p.opening.reason)           # 3+ Militia in the Dark Age, ...
    print("  feudal at", p.feudal_ms, "ms")      # None if they never got there
    print("  feudal army:", dict(p.units["feudal"]))   # {unit id: count}
```

`game_dict(game)` gives the same thing as plain data, with names next to every
ID and times as `m:ss`, the way `--json` prints it.

To classify from counts you already have, without a replay, build the signals
yourself:

```python
from aoe2_openings import classify, signals

opening = classify(signals(
    civ="Franks", feudal_ms=600_000, castle_ms=1_080_000,
    dark_units={74: 3},             # 3 Militia
    feudal_units={4: 5},            # 5 Archers
    feudal_buildings={10: 1},       # an Archery Range
))
opening.name    # "Drush Archers"
opening.rule    # "drush_archers"
```

## What comes out of a replay

| | Per player |
|---|---|
| Match | Map, duration, rated or not, game and save version |
| Player | Name, profile ID, civilization, team, colour, result |
| Ages | When they clicked Feudal, Castle and Imperial Age |
| Villagers | Queued in each age, and in total |
| Army | Every unit queued, by age |
| Buildings | Every building and wall segment placed, by age |
| Technologies | Every technology researched, by age |
| Economy | Market buys and sells, tributes sent |
| Activity | Commands issued, APM, deletions |
| Timeline | Running totals of army and villagers every 30 seconds (`--timeline`) |
| Opening | Its name, the rule that matched, the reason and the signals |

## Limits worth knowing

- **Counts are commands.** A replay is a log of what players told the game
  to do, not what happened. A unit queued and then cancelled still counts,
  and nothing about resources at a given moment can be read without
  replaying the match in the game.
- **The result is inferred.** A replay doesn't say who won. A side whose
  players all resigned lost; if exactly one side is left, it won. Otherwise
  `won` is `None`.
- **APM is raw.** Every command counts, so it runs higher than an effective
  (eAPM) figure.
- **Names follow aocref.** After a patch adds a civilization or map, update
  aocref to get its name.
- **Tuned on 1v1.** The opening rules were built on ranked 1v1 Random Map;
  [OPENINGS.md](OPENINGS.md) has the known gaps.

## Tests

```bash
pip install -e ".[test]"
pytest
```

Every rule has a test built from hand-made counts. To also run the tests on
real games, put `.aoe2record` files in `tests/replays/` or point
`AOE2_REPLAYS` at a folder of them.

## How it was made

I built this, like AoE2Meta, by vibe coding with Claude: I knew the game and
what I wanted out of it, and Claude wrote the code. The full story is in
[the write-up](https://kaankiziltug.com/blog/aoe2meta).

Thanks to [happyleavesaoc](https://github.com/happyleavesaoc/aoc-mgz) for mgz,
which does the hard part of reading replays, to
[AoEInsights](https://github.com/AoEInsights/aoc-mgz) for keeping its fast
parser current, and to the
[Siege Engineers](https://github.com/SiegeEngineers/aoc-reference-data) for the
reference data.

## License

MIT. Age of Empires II: Definitive Edition is a trademark of Microsoft
Corporation. This is an independent fan project, not affiliated with or
endorsed by Microsoft, made under Microsoft's
[Game Content Usage Rules](https://www.xbox.com/en-US/developers/rules).
