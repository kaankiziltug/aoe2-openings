"""Object and technology IDs from Age of Empires II: Definitive Edition.

Each opening rule is written in terms of these. Where a unit or building has
more than one ID (for example the three Archery Range objects), all of them
count.
"""

# Age-up technologies. Researching one moves the player into that age.
FEUDAL_AGE = 101
CASTLE_AGE = 102
IMPERIAL_AGE = 103

# Villagers (male and female).
VILLAGERS = frozenset({83, 293})

# Units.
MILITIA = 74
MAN_AT_ARMS = 75
ARCHER = 4
CROSSBOWMAN = 24
SKIRMISHER = 7
SPEARMAN = 93
PIKEMAN = 358
SCOUT_CAVALRY = 448
LIGHT_CAVALRY = 37
SERJEANT = 1658  # Sicilians
BATTLE_ELEPHANT = 1132
SCORPION = 279
HEAVY_SCORPION = 542
BATTERING_RAM = 35
CAPPED_RAM = 422
SIEGE_RAM = 548

# Buildings.
ARCHERY_RANGES = frozenset({10, 14, 87})
STABLES = frozenset({86, 101, 153})
WATCH_TOWER = 79
GUARD_TOWER = 234
KEEP = 235
SIEGE_WORKSHOP = 49
MONASTERY = 104
DONJON = 1665  # Sicilians
# The Town Center a player builds; the one they start with has another ID.
TOWN_CENTER = 621

# Civilizations with Battle Elephants early enough to rush with them.
ELEPHANT_CIVS = frozenset({"Khmer", "Burmese", "Malay", "Vietnamese"})
