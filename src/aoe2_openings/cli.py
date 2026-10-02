"""aoe2-openings: read replays from the command line.

    aoe2-openings game.aoe2record              a short summary per player
    aoe2-openings game.aoe2record --json       everything, as JSON
    aoe2-openings *.aoe2record --json --timeline
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .parse import ReplayError, analyze
from .report import clock, game_dict


def _summary(path: str, game) -> str:
    head = " · ".join(x for x in (game.map or "Unknown map", clock(game.duration_ms), "rated" if game.rated else None) if x)
    lines = [path, f"  {head}"]
    for p in game.players:
        result = {True: "won", False: "lost"}.get(p.won, "")
        ages = "  ".join(
            f"{label} {clock(ms) or '-'}"
            for label, ms in (("Feudal", p.feudal_ms), ("Castle", p.castle_ms), ("Imperial", p.imperial_ms))
        )
        lines.append(f"  {p.number}. {p.name or '(no name)'} ({p.civ})  {result}".rstrip())
        lines.append(f"     {p.opening.name}  ·  {ages}  ·  {sum(p.villagers.values())} villagers  ·  {p.apm(game.duration_ms)} APM")
        lines.append(f"     why: {p.opening.reason}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aoe2-openings", description="Read Age of Empires II: DE replays.")
    parser.add_argument("replays", nargs="+", help=".aoe2record files")
    parser.add_argument("--json", action="store_true", help="print everything as JSON")
    parser.add_argument("--timeline", action="store_true", help="with --json: add army and villager totals every 30 s")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    results, failed = [], 0
    for path in args.replays:
        try:
            game = analyze(path)
        except (OSError, ReplayError) as e:
            print(f"{path}: {e}", file=sys.stderr)
            failed += 1
            continue
        if args.json:
            results.append({"file": path, **game_dict(game, with_timeline=args.timeline)})
        else:
            print(_summary(path, game), end="\n\n")

    if args.json:
        print(json.dumps(results[0] if len(results) == 1 else results, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
