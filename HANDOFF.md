# Handoff for the next Claude session

Read this first. It says what exists, how it was made, and the rules to keep.
Last updated: Nov 25, 2026.

## Start here

1. `git pull --rebase origin main` before you touch anything. More than one Claude session
   pushes to this repo (one made the brawler art, one made the map).
2. Read this file, then skim `README.md` and look at the overview images:
   `brawlers/_overview.jpg`, `animations/_overview.jpg`, `weapons/_overview.jpg`,
   `effects/combat/_overview.jpg`, `maps/assets/_overview.jpg`.
3. Ask Artem what he wants next. Don't start redoing finished work on your own.

## The project

Art for Artem's own mobile game: a 9:16 PvP brawler where small squads fight on a
castle-island map.

This repo (`zqh7y/Game_Assets2`, branch `main`) holds the art. Push finished work to
`main` as you go: commit, `git pull --rebase origin main`, then push.

## Working with Artem

- He writes short and casual ("bro", "ofc") and wants short, casual answers back.
- For a big task, write your plan or ideas first and wait for his OK. He often says
  "Done" or "ok done" to mean "go".
- Only change what he asks for. He gets annoyed when finished things get redone unasked,
  and he stops work he doesn't want mid-way (on Nov 24 he stopped the pick cards: "dont do
  the cards" - don't make pick cards unless he asks again).
- Send him a preview image or GIF of every result, then a short summary that names any
  flaws honestly.
- Gemini quota is tight: get as much as possible out of each image (several brawlers or
  items per sheet) without hurting quality.
- He said he will tell you which brawlers to replace. Replacing one means: one new
  character (attach `brawlers/_overview.jpg` so the style matches), one 4x4 animation
  sheet, and maybe a new weapon.

## The roster (made Nov 24-25, super minimal style)

12 brawlers. Artem dropped the old pet roster (Beam, Dough, Soot, Honey, Nana, Capy,
Pango, Bill, Tardi, Octo, Mossy); its files are in `old_roster/` and must not come back
into the main folders.

| Brawler | Who | Look | Weapon | Role |
| --- | --- | --- | --- | --- |
| Rook | castle guard | grey helmet, red outfit | AK-47 | all-rounder |
| Bram | blacksmith | curly brown hair, red headband, brown apron | sledgehammer | tank, melee |
| Hood | forest outlaw | green hood | sniper rifle | sniper |
| Barley | farmer | yellow straw hat, blue overalls | double-barrel shotgun | close range |
| Wick | sailor | navy beanie, eye patch, striped shirt | revolver | mid range |
| Ash | rogue | dark grey hood, red scarf | combat knife | assassin, melee |
| Sage | village healer | curly hair, leaf headband, green robe | pistol, heals | healer |
| Chop | lumberjack | fur cap, big orange beard, red outfit | axe | bruiser, melee |
| Tusk | mercenary | horned helmet, fur collar | minigun | heavy |
| Pip | castle messenger | red cap with a feather, yellow outfit | Uzi | fast flanker |
| Fuse | bombardier | leather cap with goggles, orange scarf | RPG | area damage |
| Jinx | castle jester | green and yellow jester hat, white mask | grenade launcher | thrower |

`stats/brawlers.json` has each one's starting numbers and every asset path.

## Artem's design laws (never break these)

- Super minimal, copied from his reference (little cavemen): short bean body, the top is
  a hat or hair that hides the eyes, a plain skin-colored face strip with NO eyes, mouth or
  nose, one flat outfit color, two tiny stick legs, NO arms, two small floating round hands.
- No small details: no folds, stitches, buttons, straps, patterns. Thick dark brown
  outline, flat colors. It must match the castle island map.
- Seen a little from above, facing RIGHT (mirror for left).
- Weapons are plain real-world weapons with NO skins (grey/black metal, brown wood), held
  low between the floating hands, never covering the face.
- Characters stay small in the frame. His first reaction to a detailed version was "thats
  too much details and they look big" - when in doubt, simpler and smaller.

## What exists

- `brawlers/<Name>.png` - the 12 brawlers holding their weapons, transparent, about
  270x310 px, plus `_overview.jpg`.
- `animations/<Name>/` - `<Name>_sheet_right.png` / `_left.png` (2 rows x 4 frames,
  uniform cells: row 1 walk, row 2 attack), GIFs `<Name>_walk_{right,left}`,
  `<Name>_run_*` (walk at 85 ms), `<Name>_shoot_*` (`<Name>_attack_*` for Bram, Ash, Chop)
  and `<Name>_preview.gif` (shot, projectile, hit; melee: walk then swing).
- `weapons/<weapon>.png` - the 12 weapons on their own, side view pointing right.
  `weapons/projectiles/` - `bullet_small`, `bullet_sniper`, `pellets_shotgun`, `rocket`,
  `grenade`, `bullet_heal`.
- `effects/combat/` - `muzzle_flash`, `bullet_hit`, `explosion`, `melee_swing`, `heal`
  (4 frames each: appear, grow, peak, fade).
- `effects/{movement,hit,defeat,support,spawn}/` - older generic effects (dust, sparks,
  spawn poofs, defeat poofs). They were made for the old roster and are a bit busier than
  the new style, but have no characters in them.
- `maps/` - `castle_island_map.png` (4096x4096 scrolling map) and
  `castle_island_map_1024.png` (the original Gemini image). Castle base on a long island
  in a lake, 4 gates and roads to 4 stone bridges, big mainland with villages, farms,
  forests and water exits. To change it, attach the 1024 file in a new Gemini chat and ask
  for edits that keep everything else the same.
- `maps/assets/<group>/` - 38 map objects as transparent PNGs. Not made yet: ground pieces
  (road, water, sand, cobblestone), hay bales, mooring posts, statue, lookout platform.
- No pick cards (Artem said not to make them).

## Known small flaws (fix only if Artem asks)

- Bram's, Ash's, Tusk's and Fuse's walk frames 2 and 4 are copies of frames 1 and 3 lifted
  a few pixels (Gemini dropped the weapon in those frames; fixed with `tools/fix_walk.py`),
  so their walk is a little stiffer than the others'.
- Wick shows one eye next to his eye patch, and Jinx's mask has eye holes - the only faces
  with any feature.
- The run GIFs are the walk played faster (no separate run row).
- There is no idle, hurt or death animation yet; `effects/defeat/` can cover deaths.
- The `rocket` projectile was cut from the loaded RPG (warhead plus the launch flame).
- The far tip of the heal bullet trail keeps a very faint pink tint.

## How new art gets made

Art is generated in Gemini inside Artem's Chrome through the Claude in Chrome
extension. Artem gave permission for this and for downloading the images.

Accounts (each gives roughly 5-6 images before a rolling limit; exact reset times are
on `gemini.google.com/u/N/usage`; when one runs out move to the next):

- `/u/0` and `/u/1` - Russian UI ("Создание изображений" = Create image).
- `/u/2` and `/u/3` - English UI. `/u/3` sometimes shows a "Keep in mind ... Got it" terms
  box or a "Students ... Claim offer" box: leave them alone, never click them.
- Feature popups like "Search your mail, calendar and photos" can be closed with "Not now".

The flow that works:

1. Open `gemini.google.com/u/N/app` (a fresh chat) and take a screenshot first. A limit
   banner or a popup shifts the layout, and a blind click can send a suggested prompt.
2. Click `+` (about 298,443 on a 958x888 viewport), choose "Create image" (about 344,584).
3. Click `+` again (about 298,801), find the hidden "Upload files" file input with `find`,
   attach the images with `file_upload` (files must be inside your home folder, not
   `/tmp`), press Escape.
4. Click the prompt box and type the prompt in two `type` actions (one very long type
   action can time out).
5. Press Enter, wait about 90 seconds (in two batches; one very long batch of waits can
   lose the connection), screenshot, then click the download icon at the top right of the
   image (about 712,275).
6. The file lands in `C:\Users\ytevi\Downloads\Gemini_Generated_Image_*.jpg` on Artem's
   PC. List that folder, take the newest file by mtime, and stage it into the session.

Prompt rules that worked for this style:

- One fresh chat per image. Gemini gets worse in long chats.
- Always a huge, fully detailed prompt. Attach Artem's style reference (the cavemen
  screenshots) or `brawlers/_overview.jpg`, and say "my own original game characters".
- Spell out the minimal rules every time (bean body, no eyes, no mouth, stick legs,
  floating round hands, no small details, small in the cell).
- Ask for a solid pure magenta `#FF00FF` background and "do not use magenta or pink
  anywhere on the characters".
- Animation sheets: attach a clean picture of the two brawlers side by side on magenta
  (cut PNGs pasted on a 1024x512 magenta canvas), ask for 4 columns x 4 rows (A walk,
  A attack, B walk, B attack), and say "the weapon is VISIBLE IN EVERY SINGLE FRAME".
  Gemini still sometimes drops the weapon in walk frames 2 and 4; fix with
  `tools/fix_walk.py` instead of regenerating.
- Line-ups: Gemini may return 3 rows instead of 2 with duplicates; just pick the good ones.
- If Gemini refuses, reword and retry once. After two refusals skip it and tell Artem.
- Never click terms or offer boxes, never type passwords, never upgrade plans.

## Tools

Need Python 3 with `numpy`, `Pillow` and `scipy`. Run them with `python3 -I`. They read a
raw Gemini JPG with a magenta or green background and detect the key color from the
top-left corner.

- `tools/cut_blobs.py SRC.jpg OUTDIR name1,name2,... [merge_px] [row_tol]` - cuts every
  separate object (characters, weapons) into its own PNG in reading order. Use it for
  line-ups and item sheets; it doesn't care how many rows Gemini drew.
- `tools/build_armed.py SHEET.jpg REPO OUTROOT NameA [NameB] [--melee]` - cuts a 4-row
  pair sheet (or a 2-row single sheet) into the 2-row sheets, GIFs and preview. It looks
  for `REPO/weapons/bullets/<name>_bullet.png` and `REPO/effects/weapons/<name>_hit_2.png`
  (old layout) - point REPO at a scratch folder that has copies of the right projectile
  and hit frame under those names. Its output files are named `<Name>_armed_*`; drop the
  `_armed` part when copying into `animations/<Name>/`. For a pair with one melee and one
  gun brawler, split the sheet into halves and run it once per brawler.
- `tools/fix_walk.py SRC.jpg OUT.jpg ROW[,ROW]` - on a 4x4 sheet, replaces walk frames 2
  and 4 of the given rows with frames 1 and 3 lifted a few pixels.
- `tools/build_fx.py SRC.jpg OUTDIR name1,name2,...` - slices an effects sheet, one effect
  per row, and writes the strips, frames, GIFs and a `_check_` image.
- `tools/cut_items.py SRC.jpg OUTDIR COLS ROWS name1,...` - cuts a strict grid of items.
- `tools/cut_assets.py SHEET.png OUTDIR [names] [merge_px]` - cuts map objects.
- `tools/build_anim.py`, `tools/cut_card.py` - used for the old roster's unarmed sheets
  and pick cards.
- `tools/build_overviews.py [REPO]` - rebuilds `animations/_overview.jpg`,
  `weapons/_overview.jpg` and `effects/combat/_overview.jpg`.

Always open the `_check_` image before copying anything into the repo. Don't commit
`_check_` files (they're in `.gitignore`).

## Ideas Artem hasn't asked for yet (offer, don't do)

- Idle, hurt and death animations for the 12.
- A real run row instead of the sped-up walk.
- New-style spawn and defeat effects.
- The missing map pieces listed above.
- Start the game prototype itself using these assets.
