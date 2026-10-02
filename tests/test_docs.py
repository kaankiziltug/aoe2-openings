"""OPENINGS.md describes every rule, in the order the classifier checks them."""

from pathlib import Path

from aoe2_openings import RULES

DOC = (Path(__file__).parent.parent / "OPENINGS.md").read_text(encoding="utf-8")


def test_every_rule_is_documented_in_order():
    positions = [DOC.find(f"`{r.id}`") for r in RULES]
    assert -1 not in positions, [r.id for r, p in zip(RULES, positions) if p == -1]
    assert positions == sorted(positions)
