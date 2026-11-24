"""Cut the 4096x4096 castle island map into JPEG tiles the game can load.

The source PNG is 14 MB and a single 4096 texture is too big for some phones,
so the game loads a 2x2 grid of 2048 px JPEG tiles instead.

Run from the repo root:  python3 -I game/scripts/make_map_tiles.py
"""
import sys
from pathlib import Path

from PIL import Image

TILE = 2048
QUALITY = 88

repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
src = repo / "maps" / "castle_island_map.png"
out = repo / "game" / "public" / "map"
out.mkdir(parents=True, exist_ok=True)

im = Image.open(src).convert("RGB")
w, h = im.size
for ty in range(h // TILE):
    for tx in range(w // TILE):
        tile = im.crop((tx * TILE, ty * TILE, (tx + 1) * TILE, (ty + 1) * TILE))
        path = out / f"map_{tx}_{ty}.jpg"
        tile.save(path, quality=QUALITY, optimize=True, progressive=True)
        print(path.relative_to(repo), f"{path.stat().st_size / 1e6:.2f} MB")
