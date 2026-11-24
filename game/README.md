# Castle Island game prototype

TypeScript + [Phaser 4](https://phaser.io) + Vite. Right now it shows the battle map,
which you can scroll and zoom, with the 11 armed brawlers standing near the castle.

## Run it

Needs Node 20 or newer.

```bash
cd game
npm install
npm run dev
```

Open the URL Vite prints. `npm run dev` also prints a network URL, so you can open it on a
phone on the same Wi-Fi.

- `npm run build` - typecheck and build to `game/dist/` (relative paths, so it can be hosted from any folder)
- `npm run preview` - serve the build
- `npm run typecheck` - TypeScript only

## Controls

- Drag (mouse or one finger) to scroll; release fast to fling.
- Mouse wheel or pinch to zoom. The camera never shows anything outside the map.
- Tap a brawler to play its shoot (or melee swing) row once.

## Where things are

| File | What it does |
| --- | --- |
| `src/config.ts` | Every tunable number: resolution, start view, zoom limits, drag feel, timings, shadow |
| `src/brawlers.ts` | The roster: where each brawler stands, which way it faces, its on-map height |
| `src/Brawler.ts` | One brawler: slices its armed sheet, stands on its feet, idle bob, shoot on tap |
| `src/CameraControl.ts` | Drag, fling, pinch, wheel zoom, tap detection |
| `src/scenes/MapScene.ts` | Loads the map and sheets, places everything |
| `scripts/make_map_tiles.py` | Cuts `maps/castle_island_map.png` into the 4 JPEG tiles in `public/map/` |

The game reads the brawler sheets straight from `../animations/<Name>/<Name>_armed_sheet_right.png`,
so a redrawn sheet shows up without copying anything. Cell size and where the feet are
are measured from the sheet when the game loads.

The map is served as four 2048 px JPEG tiles (2.7 MB) instead of the 14 MB PNG, which is too
heavy for phones. After changing the map, rerun from the repo root:

```bash
python3 -I game/scripts/make_map_tiles.py
```

## Screen size

The game is 9:16 portrait (1080x1920 internal). On phones taller than 9:16 it grows to fill
the screen (Phaser `EXPAND`); on wide screens it shows a centered 9:16 column.
