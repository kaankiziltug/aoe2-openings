"""Read an Age of Empires II: Definitive Edition replay and name each player's opening.

    from aoe2_openings import analyze

    game = analyze("game.aoe2record")
    for player in game.players:
        print(player.name, player.civ, player.opening.name, player.opening.reason)
"""

from .classify import RULES, Opening, Signals, classify, openings, signals
from .parse import Game, Player, ReplayError, analyze
from .report import game_dict

__version__ = "0.1.0"

__all__ = [
    "RULES",
    "Game",
    "Opening",
    "Player",
    "ReplayError",
    "Signals",
    "analyze",
    "classify",
    "game_dict",
    "openings",
    "signals",
]
