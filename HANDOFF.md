# Handoff for the next Claude session

Read this first. It says what exists, how it was made, and the rules to keep.

## The project

Art for Artem's own mobile game: a 9:16 PvP brawler where players draft brawlers from
pick cards and small squads fight. Artem likes short, casual answers.

This repo (`zqh7y/Game_Assets2`, branch `main`) holds the art. Push finished work to
`main` as you go. `README.md` lists every folder and file type.

## What already exists (all done, don't redo)

- `brawlers/` - reference art for Beam, Dough, Soot, Honey, Nana, Capy, Axo, Pango,
  Bill, Tardi, Octo.
  Peep, Dragon and Spooky (Artem's older originals) were removed from the repo on Artem's request (Nov 24) - don't add them back.
- `cards/` - `<Name>_card.png` for all 11: transparent, arch-shaped gold-rim pick card
  with a name ribbon and a count badge.
- `animations/<Name>/` - for all 11: `<Name>_sheet_right.png` and `_sheet_left.png`
  (transparent, 3 rows x 4 frames, uniform cells: row 1 walk, row 2 run, row 3 attack),
  GIFs for walk / run / attack in both directions, and `<Name>_preview.gif`.
  Timing used in the GIFs: walk 140 ms per frame, run 90 ms, attack 150 ms with the
  last frame held 450 ms.
- `effects/<group>/` - 31 effects without characters. Per effect: `<name>_sheet.png`
  (4-frame strip: appear, grow, peak, fade), `<name>_1.png` to `<name>_4.png`,
  `<name>.gif`. Groups: `movement`, `hit`, `defeat`, `attacks`, `support`, `spawn`
  (POOF bursts for when a brawler appears: white, blue team, red team, ground dust).
  Frames are centered in their cell, so travel (slipper flying, soul rising) is done
  by moving the sprite in code. Effects that point somewhere point right.
- `maps/` - `castle_island_map.png` (4096x4096, the scrolling battle map) and
  `castle_island_map_1024.png` (the original Gemini image). Square map: castle base on a
  long island in a lake, 4 gates and roads to 4 stone bridges, big mainland with wide
  roads, plazas, villages, farms, forests and water exits. Gemini only outputs 1024 px,
  so the big file is a 4x Real-ESRGAN (anime_6B) upscale; small details are a bit soft.
  To change the map, attach the 1024 file in a new Gemini chat and ask for edits that
  keep everything else the same.
- `maps/assets/<group>/` - 38 map objects as separate transparent PNGs (`buildings`,
  `nature`, `structures`), plus `_overview.jpg`. Made by attaching the 1024 map in Gemini
  and asking for a 4x3 sprite sheet on magenta "redrawn in exactly the same style", then
  a 4x upscale and `tools/cut_assets.py`. They are redraws, not cut-outs of the map.
  Not made yet: ground pieces (road, water, sand, cobblestone), hay bales, mooring
  posts, statue, lookout platform.
- `weapons/` - one toy blaster per brawler, skinned in that brawler's colors (side view, barrel
  right), plus `muzzle_flash.png`, `weapon_crate.png`, `ammo_box.png`. `weapons/bullets/` has each
  gun's projectile. `effects/weapons/` has each gun's hit effect (3 frames).
- Armed animations: `animations/<Name>/<Name>_armed_sheet_right.png` / `_left.png` (rows: walk with
  gun, run with gun, shoot), GIFs, and `<Name>_armed_preview.gif`. The guns were attached in code
  with `tools/attach_gun.py` (per-brawler size and position in its `CFG` table), not redrawn.
- `stats/weapons.json` - starting balance numbers (about 100 damage per second each) and asset paths.
- `tools/` - the Python scripts that cut the raw Gemini images (see below).

## Brawlers and roles

| Brawler | What it is | Role | Attack effect |
| --- | --- | --- | --- |
| Beam | lighthouse keeper | long-range light beam | `beam_light` |
| Dough | baker with a rolling pin | close-range | `dough_flour` |
| Soot | chimney sweep | fast, sneaky | `soot_cloud` |
| Honey | beekeeper | long-range bees | `honey_bees` |
| Nana | grandma with a slipper | thrower | `nana_slipper` |
| Capy | capybara | calm tank | `capy_bonk` |
| Axo | axolotl | healer | `axo_heart` |
| Pango | pangolin | armored roller | `pango_dust` |
| Bill | shoebill | stare stun | `bill_shockwave` |
| Tardi | tardigrade | tank | `tardi_bubble` |
| Octo | octopus | ink squirt | `octo_ink` |

## Artem's design laws (never break these)

- Minimal: one simple blob body, dot eyes, no small details.
- 3 colors per brawler plus a thick dark rounded outline. Flat 2D vector look, one
  slightly darker flat shade per color, no gradients, no texture, no 3D.
- 3/4 side view facing RIGHT (mirror for left). Never facing the camera.
- Unique characters that other games barely use.

## Known small flaws (fix only if Artem asks)

- The last `heal_sparkles` frame is greyish; tiny dust balls keep a faint pink rim.
- Guns are pasted over the old frames, so Beam still carries his lantern, Dough his rolling pin
  and Soot his brush next to their guns. Redrawing those three in Gemini would look cleaner.
- Nana holds her slipper only in the attack row (on purpose, it fixed an
  inconsistency).

## How new art gets made

Art is generated in Gemini inside Artem's Chrome through the Claude in Chrome
extension. He has several Google accounts at `gemini.google.com/u/0/app`, `/u/1/app`
and so on. Each gives roughly 5-8 images before a limit; reset times are on
`/u/N/usage`. When one account hits its limit, move to the next.

Rules that worked:

- One fresh chat per image. Gemini gets worse in long chats.
- Always a huge, fully detailed prompt: character description, exact colors, layout,
  view, every frame described, background, "no text anywhere".
- Select the "Create image" tool in the + menu before typing. Without it Gemini
  sometimes answers with text only.
- Attach reference images and say they are "my own original characters".
- Ask for a solid pure magenta `#FF00FF` background. Use pure green `#00FF00` when the
  subject is pink or purple. Tell Gemini not to use the key color in the art.
- Sprite sheets: ask for EXACTLY 3 rows x 4 columns. Gemini often returns 4 rows
  anyway, so look at the result and pick the right rows with the rowmap argument.
- Effects sheets: 4 rows x 4 frames, one effect per row, no characters.
- If Gemini refuses, reword (call an attack a "move", drop angry words) and retry once.
  After two refusals skip it and tell Artem.
- If the page hangs on "Creating your image", reload the chat URL.
- Download the full-size image, wait about 18 seconds, then confirm the file really
  landed in the Downloads folder before moving on. Re-download from the chat URL if
  it is missing.
- Look at the cut result before pushing, and send Artem a preview.
- Never click terms or "Got it" boxes, never type passwords, never upgrade plans.

## Tools

Need Python 3 with `numpy`, `Pillow` and `scipy`. All three read a raw Gemini JPG with
a magenta or green background and detect the key color from the top-left corner.

- `tools/cut_card.py SRCDIR OUTDIR Name [Name ...]` - reads `SRCDIR/<Name>.jpg`, cuts
  the card out, writes `OUTDIR/<Name>_card.png` and `OUTDIR/_all_cards.jpg`.
- `tools/build_anim.py SRC.jpg Name OUTDIR [rowmap] [cleanwalk]` - slices a character
  sheet into aligned frames and writes both sheets, all GIFs and `_check_<Name>.jpg`.
  `rowmap` picks which rows are walk, run, attack (for a 4-row result use `0,1,3` or
  `0,1,2`; use `-` for the default). `cleanwalk` drops stray specks from the walk row.
- `tools/build_fx.py SRC.jpg OUTDIR name1,name2,name3,name4` - slices an effects sheet,
  one effect per row, and writes the strips, frames, GIFs and a `_check_` image.

- `tools/cut_assets.py SHEET.png OUTDIR [name1,name2,...] [merge_px]` - cuts a magenta
  sprite sheet of loose objects into one transparent PNG per object. Run it without names
  first: it prints the objects it found in reading order and writes a `_check_` image.
  `merge_px` (default 15) is how far apart parts may be and still count as one object;
  lower it (9-13) when two neighbours get merged.

Always open the `_check_` image before copying anything into the repo. Don't commit
`_check_` files.
