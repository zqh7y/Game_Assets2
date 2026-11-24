"""Cut a key-colour sprite sheet into separate transparent PNGs.
usage: python3 cut_assets.py SHEET.png OUTDIR [name1,name2,...] [merge_px]
Without names it only prints the detected objects (row by row) and writes _check_.jpg."""
import sys, os, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
src, outdir = sys.argv[1], sys.argv[2]
names = sys.argv[3].split(',') if len(sys.argv) > 3 and sys.argv[3] != '-' else None
merge = int(sys.argv[4]) if len(sys.argv) > 4 else 15
os.makedirs(outdir, exist_ok=True)
im = Image.open(src).convert('RGB'); a = np.asarray(im).astype(np.float32)
H, W = a.shape[:2]; S = max(1, W // 1024)
key = np.median(a[:8*S, :8*S].reshape(-1, 3), axis=0)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
k = np.minimum(R, B) - G                      # how magenta a pixel is
# alpha straight from how magenta a pixel is (also clears enclosed pockets), then unmix the key colour
alpha = np.clip((110.0 - k) / 90.0, 0, 1).astype(np.float32)
f = np.clip(k / 255.0, 0, 0.6)[..., None]
rgb = np.clip((a - f * key) / (1 - f), 0, 255)
k2 = np.clip(np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1], 0, None)   # leftover magenta tint
rgb[..., 0] -= k2; rgb[..., 2] -= k2
alpha[alpha < 0.04] = 0
rgba = np.dstack([rgb, alpha * 255]).round().astype(np.uint8)
# group parts into objects on a small mask
small = (alpha > 0.5)[::S, ::S]
grp, n = ndimage.label(ndimage.binary_dilation(small, iterations=merge))
grp = np.where(small, grp, 0)
objs = []
for i, sl in enumerate(ndimage.find_objects(grp), 1):
    if sl is None: continue
    area = int((grp[sl] == i).sum())
    if area < 400: continue
    objs.append(dict(id=i, y0=sl[0].start, y1=sl[0].stop, x0=sl[1].start, x1=sl[1].stop, area=area))
objs.sort(key=lambda o: (o['y0'] + o['y1']) / 2)
rows = []
for o in objs:
    cy = (o['y0'] + o['y1']) / 2
    if rows and cy < max(p['y1'] for p in rows[-1]) - 0.25 * (o['y1'] - o['y0']) and cy - np.mean([(p['y0']+p['y1'])/2 for p in rows[-1]]) < 110: rows[-1].append(o)
    else: rows.append([o])
order = [o for r in rows for o in sorted(r, key=lambda o: o['x0'])]
chk = im.resize((1024, 1024)); d = ImageDraw.Draw(chk)
for j, o in enumerate(order):
    d.rectangle((o['x0'], o['y0'], o['x1'], o['y1']), outline=(255, 255, 0), width=2); d.text((o['x0']+4, o['y0']+2), str(j+1), fill=(255, 255, 255))
    print(j+1, 'row', [i for i, r in enumerate(rows) if o in r][0]+1, (o['x0'], o['y0'], o['x1'], o['y1']), o['area'], names[j] if names and j < len(names) else '')
chk.save(os.path.join(outdir, '_check_' + os.path.basename(src).replace('.png', '.jpg')), quality=85)
if names:
    assert len(names) == len(order), (len(names), len(order))
    big = np.kron(grp, np.ones((S, S), dtype=grp.dtype)) if S > 1 else grp
    P = 6 * S
    for nm_, o in zip(names, order):
        if nm_ == 'skip': continue
        y0, y1, x0, x1 = max(o['y0']*S-P, 0), min(o['y1']*S+P, H), max(o['x0']*S-P, 0), min(o['x1']*S+P, W)
        crop = rgba[y0:y1, x0:x1].copy()
        own = ndimage.binary_dilation(big[y0:y1, x0:x1] == o['id'], iterations=3*S)
        crop[..., 3] = np.where(own, crop[..., 3], 0)
        ys, xs = np.where(crop[..., 3] > 0)
        crop = crop[max(ys.min()-4, 0):ys.max()+5, max(xs.min()-4, 0):xs.max()+5]
        Image.fromarray(crop, 'RGBA').save(os.path.join(outdir, nm_ + '.png'), optimize=True)
        print('saved', nm_, crop.shape[1], 'x', crop.shape[0])
