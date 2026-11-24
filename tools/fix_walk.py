"""Replace walk frames 2 and 4 (weapon missing) with frames 1 and 3 lifted a few pixels.
usage: fix_walk.py SRC.jpg OUT.jpg ROW[,ROW...] (rows counted from 0 in a 4x4 sheet)"""
import os, sys, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_fx import key
src, out, rows = sys.argv[1], sys.argv[2], [int(r) for r in sys.argv[3].split(',')]
im = Image.open(src).convert('RGB'); a = np.asarray(im).copy()
al = key(im)[..., 3] > 60
H, W = al.shape
# row bands from the emptiest lines
prof = al.sum(1)
bounds = [0]
for k in (1, 2, 3):
    c = H * k // 4; lo, hi = c - H // 10, c + H // 10
    bounds.append(lo + int(np.argmin(prof[lo:hi])))
bounds.append(H)
for r in rows:
    y0, y1 = bounds[r], bounds[r + 1]
    band = al[y0:y1]
    lab, n = ndimage.label(ndimage.binary_dilation(band, iterations=10))
    objs = sorted([s for s in ndimage.find_objects(lab) if (s[1].stop - s[1].start) > 40], key=lambda s: s[1].start)
    if len(objs) != 4: print('row', r, 'found', len(objs)); continue
    def box(s): return (s[1].start, s[1].stop, s[0].start, s[0].stop)
    bg = np.array([255, 0, 255], np.uint8)
    for dst, srcf in ((1, 0), (3, 2)):
        sx0, sx1, sy0, sy1 = box(objs[srcf]); dx0, dx1, dy0, dy1 = box(objs[dst])
        patch = a[y0 + sy0:y0 + sy1, sx0:sx1].copy(); pm = band[sy0:sy1, sx0:sx1]
        # clear destination
        reg = a[y0 + dy0:y0 + dy1, dx0:dx1]; reg[band[dy0:dy1, dx0:dx1]] = bg
        # paste source centered at destination centre x, bottom aligned to source bottom, lifted 4 px
        cx = (dx0 + dx1) // 2 - (sx1 - sx0) // 2; ty = y0 + sy0 - 4
        tgt = a[ty:ty + patch.shape[0], cx:cx + patch.shape[1]]
        tgt[pm] = patch[pm]
    print('row', r, 'fixed')
Image.fromarray(a).save(out, quality=97)
