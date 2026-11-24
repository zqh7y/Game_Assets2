"""Cut every separate object on a keyed sheet into its own PNG, in reading order.
usage: cut_blobs.py SRC OUTDIR name1,name2,... [merge_px] [row_tol]"""
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_fx import key

src, out, names = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
merge = int(sys.argv[4]) if len(sys.argv) > 4 else 14
rtol = int(sys.argv[5]) if len(sys.argv) > 5 else 80
rgba = key(Image.open(src))
solid = rgba[..., 3] > 60
lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=merge))
objs = []
for k, sl in enumerate(ndimage.find_objects(lab), 1):
    m = (lab[sl] == k) & solid[sl]
    if m.sum() < 1500: continue
    objs.append((sl, k))
objs.sort(key=lambda o: (o[0][0].start + o[0][0].stop) / 2)
rows, cur = [], []
for o in objs:
    cy = (o[0][0].start + o[0][0].stop) / 2
    if cur and cy - (cur[-1][0][0].start + cur[-1][0][0].stop) / 2 > rtol:
        rows.append(cur); cur = []
    cur.append(o)
if cur: rows.append(cur)
order = [o for r in rows for o in sorted(r, key=lambda o: o[0][1].start)]
print('found', len(order), 'objects')
os.makedirs(out, exist_ok=True)
for name, (sl, k) in zip(names, order):
    if name == '-': continue
    y0, y1, x0, x1 = max(0, sl[0].start - 3), sl[0].stop + 3, max(0, sl[1].start - 3), sl[1].stop + 3
    a = rgba[y0:y1, x0:x1].copy()
    a[..., 3] = np.where(lab[y0:y1, x0:x1] == k, a[..., 3], 0)
    Image.fromarray(a, 'RGBA').save(f'{out}/{name}.png')
    print(name, a.shape[1], a.shape[0])
