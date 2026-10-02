# How openings are called

Every player in a replay gets exactly one opening. The rules below are checked
from the top; the first one that matches names the opening, and the result
carries that rule's ID and the counts it looked at, so you can always see why.

These are the rules [AoE2Meta](https://kaankiziltug.com/blog/aoe2meta) used on
more than half a million ranked 1v1 games. On Arabia, about one opening in ten
fell through to **Other**.

## What the rules count

All counts are **units queued** or **buildings placed** by the player, in the
age they were in at the time. A unit queued and then cancelled still counts.

| Signal | Counts |
|---|---|
| Dark Age militia | Militia queued before the Feudal Age |
| Feudal archers | Archers and Crossbowmen queued in the Feudal Age |
| Feudal men-at-arms | Militia and Men-at-Arms queued in the Feudal Age |
| Feudal scouts | Scout Cavalry and Light Cavalry queued in the Feudal Age |
| Feudal skirmishers, spears | Skirmishers; Spearmen and Pikemen, in the Feudal Age |
| Feudal towers | Watch Towers, Guard Towers and Keeps placed in the Feudal Age |
| Feudal buildings | Archery Range, Stable, Siege Workshop, Monastery, Town Center, Donjon placed in the Feudal Age |
| Castle Age units | Battle Elephants, Scorpions and Rams queued in the Castle Age |
| Castle Town Center | A Town Center placed in the Castle Age |
| Feudal to Castle | Time from clicking Feudal Age to clicking Castle Age |

Two signals are combinations:

- **Drush:** 3 or more Dark Age militia.
- **Fast castle:** Feudal to Castle in under 9 minutes, with fewer than 4
  Feudal archers, men-at-arms and scouts combined.

## The rules, in order

| # | Rule | Opening | When |
|---|---|---|---|
| 1 | `serjeant_rush` | Serjeant Rush | Sicilians with a Donjon or 2+ Serjeants in the Feudal Age |
| 2 | `elephant_rush` | Elephant Rush | Khmer, Burmese, Malay or Vietnamese with 4+ Battle Elephants in the Castle Age |
| 3 | `cumans_2tc` | 2TC Feudal Boom | Cumans with a second Town Center in the Feudal Age |
| 4 | `roman_siege` | Scorpions & Rams | Romans with 2+ Scorpions and a Ram in the Castle Age |
| 5 | `hoang_rush` | Hoang Rush | A Siege Workshop in the Feudal Age |
| 6 | `tower_rush` | Tower Rush | 3+ towers in the Feudal Age |
| 7 | `drush_fc` | Drush FC | Drush, then a fast castle |
| 8 | `drush_archers` | Drush Archers | Drush, then 3+ Feudal archers |
| 9 | `drush_maa` | Drush M@A | Drush, then 2+ Feudal men-at-arms |
| 10 | `drush` | Drush | Drush |
| 11 | `maa_archers` | M@A Archers | 2+ men-at-arms and 3+ archers in the Feudal Age |
| 12 | `maa_rush` | M@A Rush | 4+ men-at-arms in the Feudal Age |
| 13 | `archer_rush` | Archer Rush | 4+ archers in the Feudal Age |
| 14 | `scout_rush` | Scout Rush | 3+ scouts in the Feudal Age, with a Stable |
| 15 | `maa_scouts` | M@A Scouts | 2+ men-at-arms and 2+ scouts in the Feudal Age |
| 16 | `pike_skirm` | Pike Skirm | 2+ skirmishers and 2+ spears in the Feudal Age |
| 17 | `fc_boom` | FC Boom | Fast castle, then a Town Center in the Castle Age |
| 18 | `fast_castle` | Fast Castle | Fast castle |
| 19 | `monk_rush` | Monk Rush | A Feudal Monastery, with fewer than 2 each of archers, men-at-arms and scouts |
| 20 | `archer_rush_light` | Archer Rush | 2+ Feudal archers, with an Archery Range |
| 21 | `scout_rush_light` | Scout Rush | 2+ Feudal scouts, with a Stable |
| 22 | `maa_rush_light` | M@A Rush | 2+ Feudal men-at-arms |
| 23 | `archer_opening` | Archer Opening | An Archery Range and no Stable in the Feudal Age |
| 24 | `scout_opening` | Scout Opening | A Stable and no Archery Range in the Feudal Age |
| 25 | `scouts_into_archers` | Scouts into Archers | A Stable and an Archery Range in the Feudal Age |
| | `other` | Other | Nothing above matched |

Rules 20 to 22 repeat an opening from higher up with a looser threshold, so a
smaller version of the same idea still gets its name; the rule ID tells the two
apart.

## Known gaps

- **Order matters.** Civilization openings win over everything, so a Sicilian
  drush into a Donjon is a Serjeant Rush. Drush combinations win over Feudal
  army openings.
- **Queued is not built.** Counts come from production commands, so cancelled
  units and queues that never finish count the same.
- **Team games.** The rules were tuned on 1v1 Random Map, where openings are
  the clearest. They run on any game, but in team games a player's role (flank
  or pocket) shapes their opening more than their plan does.
- **Hybrids.** An archer rush that turns into a fast castle takes the first
  rule it matches. Edge cases get a different name than a caster might give.

Disagree with a threshold? Open an issue or a pull request with the games that
show it.
