# Handoff for the next Claude session

Read this first. It says what exists, how it was made, and the rules to keep.
Last updated: Nov 24, 2026.

## Start here

1. `git pull --rebase origin main` before you touch anything. More than one Claude session
   pushes to this repo (one made the brawler art, one made the map).
2. Read this file, then skim `README.md` (every folder and file type) and look at the
   overview images: `brawlers/_overview.png`, `cards/_overview.jpg`,
   `animations/_overview.jpg`, `animations/_armed_overview.jpg`, `weapons/_overview.jpg`,
   `maps/assets/_overview.jpg`.
3. Ask Artem what he wants next. Don't start redoing finished work on your own.

## The project

Art for Artem's own mobile game: a 9:16 PvP brawler where players draft brawlers from
pick cards and small squads fight on a castle-island map.

This repo (`zqh7y/Game_Assets2`, branch `main`) holds the art. Push finished work to
`main` as you go: commit, `git pull --rebase origin main`, then push.

## Working with Artem

- He writes short and casual ("bro", "ofc") and wants short, casual answers back.
- For a big task, write your plan or suggestions first and wait for his OK. He often
  says "Done" or "ok then done" to mean "go".
- Only change what he asks for. He gets annoyed when finished things get redone
  unasked ("why u redo the octo?").
- Send him a preview image or GIF of every result, then a short summary that names any
  flaws honestly.
- Gemini quota is tight: get as much as possible out of each image (several brawlers or
  items per sheet) without hurting quality.

## What already exists (all done, don't redo)

- `brawlers/` - reference art for the 11 brawlers: Beam, Dough, Soot, Honey, Nana, Capy,
  Pango, Bill, Tardi, Octo, Mossy. Peep, Dragon, Spooky and Axo were removed on Artem's
  request (Nov 24) - don't add them back.
- `cards/` - `<Name>_card.png` for all 11: transparent, arch-shaped gold-rim pick card
  with a name ribbon and a count badge.
- `animations/<Name>/` - for all 11: `<Name>_sheet_right.png` and `_sheet_left.png`
  (transparent, 3 rows x 4 frames, uniform cells: row 1 walk, row 2 run, row 3 attack),
  GIFs for walk / run / attack in both directions, and `<Name>_preview.gif`.
  Timing used in the GIFs: walk 140 ms per frame, run 90 ms, attack 150 ms with the
  last frame held 450 ms. Mossy's row 3 is a heal pulse instead of an attack.
- Armed animations: `animations/<Name>/<Name>_armed_sheet_right.png` / `_left.png` (row 1
  walk with the weapon, row 2 shoot or melee attack), `<Name>_armed_{walk,run,shoot}` GIFs
  (`_attack_` for melee) and `<Name>_armed_preview.gif` (shot, bullet, hit). Capy and Tardi
  stand upright in their armed sheets (Artem chose that so they hold the gun in their
  paws); their unarmed sheets are still four-legged.
- `weapons/` - one weapon per brawler, skinned in that brawler's colors: 8 toy blasters
  (side view, barrel right) and 3 melee weapons (Dough rolling-pin bat, Soot sooty knife,
  Bill frozen fish club), plus `muzzle_flash.png`, `weapon_crate.png`, `ammo_box.png`.
  `weapons/bullets/` has each gun's projectile.
- `effects/<group>/` - effects without characters. Per effect: `<name>_sheet.png`
  (4-frame strip: appear, grow, peak, fade), `<name>_1.png` to `<name>_4.png`,
  `<name>.gif`. Groups: `movement`, `hit`, `defeat`, `attacks`, `support` (incl.
  `heal_heart`), `spawn` (POOF bursts when a brawler appears: white, blue team, red team,
  ground dust), `weapons` (each weapon's 3-frame hit effect, the 3 melee swing arcs,
  `mossy_muzzle.png`). Frames are centered in their cell, so travel (slipper flying, soul
  rising) is done by moving the sprite in code. Effects that point somewhere point right.
- `stats/weapons.json` - starting balance (about 100 damage per second for guns, melee a
  bit higher, Mossy low damage plus 25 heal per shot) and the asset paths per brawler.
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
- `tools/` - the Python scripts that cut the raw Gemini images (see the end of this file).
- `game/` - the game prototype (TypeScript + Phaser 4 + Vite), started Nov 24 on Artem's
  request: the scrollable, zoomable map with the 11 armed brawlers standing near the castle,
  tap one to play its shoot row. See `game/README.md`. Artem said he'll say what to fix
  next; don't extend it unasked.

## Brawlers and roles

| Brawler | What it is | Role | Weapon | Attack effect |
| --- | --- | --- | --- | --- |
| Beam | lighthouse keeper | long-range | lighthouse sniper | `beam_light` |
| Dough | baker | close-range | rolling-pin bat (melee) | `dough_flour` |
| Soot | chimney sweep | fast, sneaky | sooty knife (melee) | `soot_cloud` |
| Honey | beekeeper | long-range | honeycomb AK | `honey_bees` |
| Nana | grandma with a slipper | thrower | slipper launcher | `nana_slipper` |
| Capy | capybara | calm tank | citrus minigun | `capy_bonk` |
| Pango | pangolin | armored roller | pinecone bazooka | `pango_dust` |
| Bill | shoebill | stare stun | frozen fish club (melee) | `bill_shockwave` |
| Tardi | tardigrade | tank | ray gun | `tardi_bubble` |
| Octo | octopus | ink squirt | ink soaker | `octo_ink` |
| Mossy | garden snail | healer (replaced Axo) | dew-drop sprayer | none yet (use `support/heal_heart`) |

## Artem's design laws (never break these)

- Minimal: one simple blob body, dot eyes, no small details.
- 3 colors per brawler plus a thick dark rounded outline. Flat 2D vector look, one
  slightly darker flat shade per color, no gradients, no texture, no 3D.
- 3/4 side view facing RIGHT (mirror for left). Never facing the camera.
- Unique characters that other games barely use.
- Weapons are held low in the hands and never cover the face.

## Known small flaws (fix only if Artem asks)

- Octo's gun is drawn very small, near its mouth, in its armed sheet.
- Dough's armed sheet reuses his old rolling-pin walk and swing frames, so his bat there is
  a plain rolling pin without the cloth grip of the weapon icon.
- The armed "run" GIFs are the armed walk frames played faster (no real armed run row).
- Mossy's yellow shell flower is in every animation frame except the big heal-burst frame
  (row 3, frame 3 of `Mossy_sheet_right.png`). Mossy has no entry in `effects/attacks/`.
- The last `heal_sparkles` frame is greyish; tiny dust balls keep a faint pink rim.
- Nana holds her slipper only in the attack row (on purpose, it fixed an inconsistency).

## How new art gets made

Art is generated in Gemini inside Artem's Chrome through the Claude in Chrome
extension. Artem gave permission for this and for downloading the images.

Accounts (each gives roughly 5-6 images before a rolling limit; exact reset times are
on `gemini.google.com/u/N/usage`; when one runs out move to the next):

- `/u/0` and `/u/1` - Russian UI ("Создание изображений" = Create image,
  "Скачать изображение в полном размере" = Download full size image).
- `/u/2` and `/u/3` - English UI. `/u/3` shows a "Keep in mind ... Got it" terms box:
  leave it alone, never click it.

The flow that works:

1. Open `gemini.google.com/u/N/app` (a fresh chat) and take a screenshot first. A limit
   banner or a popup shifts the layout, and a blind click can send a suggested prompt.
2. Click `+`, choose "Create image". Without it Gemini sometimes answers with text only.
3. Click `+` again, find the hidden "Upload files" file input with `find`, attach the
   reference images with `file_upload` (files must be inside your home folder, not
   `/tmp`), press Escape.
4. Click the prompt box and type the prompt in two `type` actions (one very long type
   action can time out).
5. Press Enter, wait about 90 seconds, screenshot, then click "Download full size image".
6. The file lands in `C:\Users\ytevi\Downloads\Gemini_Generated_Image_*.jpg` on Artem's
   PC. List that folder, take the newest file, and stage it into the session. If it isn't
   there, re-open the chat URL and download again.

Prompt rules that worked:

- One fresh chat per image. Gemini gets worse in long chats.
- Always a huge, fully detailed prompt: character description, exact colors, layout,
  view, every frame described, background, "no text anywhere".
- Attach reference images and say they are "my own original characters".
- Ask for a solid pure magenta `#FF00FF` background. Use pure green `#00FF00` when the
  subject is pink or purple. Tell Gemini not to use the key color in the art.
- Sprite sheets: ask for EXACTLY 3 rows x 4 columns. Gemini often returns 4 rows
  anyway, so look at the result and pick the right rows with the rowmap argument.
- Effects sheets: 4 rows x 4 frames, one effect per row, no characters.
- If Gemini refuses, reword (call an attack a "move", drop angry words) and retry once.
  After two refusals skip it and tell Artem.
- If the page hangs on "Creating your image", reload the chat URL.
- Never click terms or "Got it" boxes, never type passwords, never upgrade plans.

### Fixing one thing in a finished sheet

Attach the finished sheet plus the brawler's card, and write: "REDRAW THE FIRST IMAGE AS
THE SAME SPRITE SHEET. KEEP EXACTLY THE SAME: (list grid, poses, colors, background...).
CHANGE ONLY THIS ONE THING: ...". Gemini keeps the layout, so the same cut commands work
again. This is how Mossy's shell flower was added back.

### Armed sheets (weapons held in the hands)

This took four tries, do it this way. Artem rejected guns pasted on in code ("cheap") and
Gemini sheets where the gun sits on the chest and covers the face ("they're not holding
it"). Gemini ignores text like "hold it below the chin". What worked: build a DRAFT sheet
in code with the gun pasted LOW in front of the brawler, two brawlers per image (4 rows x 4
frames: A walk, A shoot, B walk, B shoot), upload only that draft and ask Gemini to redraw
the same sheet keeping the gun's position, size and angle and changing only the arms: both
sleeves reach down to the gun, near fist closed around the grip, far fist under the
barrel. For new poses with no draft (melee, Capy and Tardi upright, Mossy) attach a
finished armed sheet as the POSE REFERENCE plus the weapon PNG and the brawler's card.

## Tools

Need Python 3 with `numpy`, `Pillow` and `scipy`. Run them with `python3 -I`. They read a
raw Gemini JPG with a magenta or green background and detect the key color from the
top-left corner.

- `tools/cut_card.py SRCDIR OUTDIR Name [Name ...]` - reads `SRCDIR/<Name>.jpg`, cuts
  the card out, writes `OUTDIR/<Name>_card.png` and `OUTDIR/_all_cards.jpg`.
- `tools/build_anim.py SRC.jpg Name OUTDIR [rowmap] [cleanwalk]` - slices a character
  sheet into aligned frames and writes both sheets, all GIFs and `_check_<Name>.jpg`.
  `rowmap` picks which rows are walk, run, attack (for a 4-row result use `0,1,3` or
  `0,1,2`; for a 2-row walk + attack sheet use `0,0,1`; `-` for the default).
  `cleanwalk` drops stray specks from the walk row.
- `tools/build_armed.py SHEET.jpg REPO OUTROOT NameA [NameB] [--melee]` - cuts an armed
  sheet (two brawlers: 4 rows; one brawler: 2 rows) into the armed sheets, GIFs and
  preview. Needs the brawler's bullet and hit effect in the repo first.
- `tools/build_fx.py SRC.jpg OUTDIR name1,name2,name3,name4` - slices an effects sheet,
  one effect per row, and writes the strips, frames, GIFs and a `_check_` image.
- `tools/cut_items.py SRC.jpg OUTDIR COLS ROWS name1,name2,...` - cuts a grid of loose
  items (weapons, bullets, hit effects) into one transparent PNG per cell; `-` skips a cell.
- `tools/cut_assets.py SHEET.png OUTDIR [name1,name2,...] [merge_px]` - cuts a magenta
  sprite sheet of loose objects into one transparent PNG per object. Run it without names
  first: it prints the objects it found in reading order and writes a `_check_` image.
  `merge_px` (default 15) is how far apart parts may be and still count as one object;
  lower it (9-13) when two neighbours get merged.
- `tools/build_overviews.py [REPO]` - rebuilds `animations/_overview.jpg` and
  `animations/_armed_overview.jpg` from every brawler folder in `animations/`. Run it after
  adding or changing any brawler's sheets.

Always open the `_check_` image before copying anything into the repo. Don't commit
`_check_` files (they're in `.gitignore`).

## Ideas Artem hasn't asked for yet (offer, don't do)

- Redraw Octo's armed sheet with a bigger gun held low.
- A real armed run row for everyone.
- A Mossy entry in `effects/attacks/`.
- The missing map pieces listed under `maps/assets/`.
