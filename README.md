# Game_Assets2

Art assets for the brawler game.

## Folders

- `brawlers/` - character cards (one PNG per brawler, name on the card)
- `cards/` - draft pick cards (transparent PNG, one per brawler, with the count badge)
- `animations/<Name>/` - walk / run / attack sprite sheets (transparent PNG, 4 frames per row: row 1 walk, row 2 run, row 3 attack; `_right` and mirrored `_left`) plus GIF previews
- `maps/` - battle maps (PNG). `castle_island_map.png` is the big scrolling map (4096x4096), `castle_island_map_1024.png` is the original 1024x1024 it was upscaled from
- `maps/assets/<group>/` - the map's objects as separate transparent PNGs, in groups `buildings`, `nature` and `structures`
- `effects/<group>/` - effect animations without characters (transparent PNG). Per effect: `<name>_sheet.png` (4 frames in one strip: appear, grow, peak, fade), `<name>_1.png` to `<name>_4.png` (single frames) and `<name>.gif` (preview)

## Brawlers

| Brawler | What it is | Role |
| --- | --- | --- |
| Beam | lighthouse keeper | long-range light beam |
| Dough | baker with a rolling pin | close-range |
| Soot | chimney sweep | fast, sneaky |
| Honey | beekeeper | long-range bees |
| Nana | grandma with a slipper | medium-range thrower |
| Capy | capybara | calm tank |
| Axo | axolotl | healer |
| Pango | pangolin | armored roller |
| Bill | shoebill | stare stun |
| Tardi | tardigrade | tank |
| Octo | octopus | ink squirt |
| Peep | chick | swarm pecker |
| Dragon | baby dragon | fire puff |
| Spooky | hooded ghost | boo scare |

![All brawlers](brawlers/_overview.png)

## Pick cards

![All pick cards](cards/_overview.jpg)

## Animations

Every brawler has walk, run and attack rows. Nana only holds her slipper in the attack row.

![All animation sheets](animations/_overview.jpg)

## Effects

| Group | Effects |
| --- | --- |
| `movement/` | `walk_dust`, `run_dust`, `landing_puff`, `speed_lines` |
| `hit/` | `hit_spark`, `impact_burst`, `slash_arc`, `critical_hit` |
| `defeat/` | `smoke_poof`, `star_pop`, `soul_wisp`, `sparkle_ring` |
| `attacks/` | `beam_light`, `dough_flour`, `soot_cloud`, `honey_bees`, `nana_slipper`, `capy_bonk`, `axo_heart`, `pango_dust`, `bill_shockwave`, `tardi_bubble`, `octo_ink`, `dragon_fire` |
| `support/` | `heal_sparkles`, `shield_up`, `spawn_poof`, `level_up` |

Each frame is centered in its cell, so travel (a slipper flying, a soul floating up, a beam moving right) is done by moving the sprite in the game. Effects that point somewhere point right; mirror them for left.

![All effects](effects/_overview.jpg)

## Map

Castle Island: the castle base on the island is where brawlers spawn, four gates and roads lead to four stone bridges, and the mainland around the lake has wide roads, ring roads, bridge plazas with watchtowers, villages (blue roofs left, red roofs right), farms, forests, cliffs and water exits (docks, beaches, stone steps).

![Castle Island map](maps/castle_island_map_1024.png)

## Map assets

38 separate objects in the style of the Castle Island map, one transparent PNG each.

| Group | Assets |
| --- | --- |
| `buildings/` | `castle`, `house_blue`, `house_red`, `bakery`, `barn`, `windmill`, `lighthouse`, `watchtower`, `market_stall`, `well`, `tent_campfire`, `bridge_gate` |
| `nature/` | `tree_round`, `tree_pine`, `tree_orange`, `bush`, `boulder`, `rocks`, `haystack`, `wheat_field`, `vegetable_patch`, `pumpkin_patch`, `beehives`, `flowers` |
| `structures/` | `bridge`, `plaza`, `stone_wall`, `fence`, `hedge`, `hedge_diagonal`, `dock`, `stone_steps`, `rowboat`, `barrels_crate`, `ruins`, `signpost`, `cliff`, `anvil` |

![Map assets](maps/assets/_overview.jpg)

## Design laws

- Minimal: one simple blob body, dot eyes, no small details.
- 3 colors per brawler plus the dark outline.
- 3/4 side view facing right (mirror the image for left).

Note: the `brawlers/` PNGs are screen captures (about 507x681); Peep, Dragon and Spooky are not in `brawlers/` (they use the original art from the game).
