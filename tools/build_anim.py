"""usage: build_anim.py SRC NAME OUTDIR [rowmap e.g. 0,1,2 or -] [cleanwalk]"""
import sys, numpy as np
CLEAN_WALK = False
from PIL import Image
from scipy import ndimage

def key(im):
    a = np.asarray(im.convert('RGB')).astype(np.int32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    c = a[:10, :10].reshape(-1, 3).mean(0)
    green = c[1] > c[0] and c[1] > c[2]
    k = (G - np.maximum(R, B)) if green else (np.minimum(R, B) - G)
    alpha = np.clip(255 - (k - 40) * 255 // 50, 0, 255)
    spill = np.clip(k, 0, None)
    if green:
        G = np.where(k > 15, G - spill, G)
    else:
        R = np.where(k > 15, R - spill, R); B = np.where(k > 15, B - spill, B)
    return Image.fromarray(np.dstack([np.clip(R, 0, 255), np.clip(G, 0, 255), np.clip(B, 0, 255), alpha]).astype(np.uint8), 'RGBA')

def bands(v, gap=6):
    b = []; inside = False; z = 0
    for i, x in enumerate(v):
        if x > 0:
            if not inside: s = i; inside = True
            z = 0
        elif inside:
            z += 1
            if z > gap: b.append((s, i - z + 1)); inside = False
    if inside: b.append((s, len(v)))
    return b

def build(src, name, outdir, rowmap=None, cols=4, names=('walk', 'run', 'attack'), bg=(246, 178, 115)):
    rgba = key(Image.open(src))
    A = np.asarray(rgba); al = A[..., 3] > 40
    H, W = al.shape
    allb = bands(al.sum(1))
    rb = [list(b) for b in allb if b[1] - b[0] > H / 12]
    for b in allb:
        if b[1] - b[0] <= H / 12 and b[1] - b[0] > 4:
            j = min(range(len(rb)), key=lambda i: min(abs(rb[i][0] - b[1]), abs(b[0] - rb[i][1])))
            rb[j] = [min(rb[j][0], b[0]), max(rb[j][1], b[1])]
    rb = [tuple(b) for b in rb]
    print(name, 'row bands', rb)
    if rowmap is None: rowmap = list(range(len(names)))
    rb = [rb[i] for i in rowmap]
    frames = []
    for r, (r0, r1) in enumerate(rb):
        rowA = A[r0:r1]; ra = rowA[..., 3] > 40
        lab, n = ndimage.label(ndimage.binary_dilation(ra, iterations=2))
        lab = lab * ra
        ids = [i for i in range(1, n + 1) if (lab == i).any()]
        sizes = {i: int((lab == i).sum()) for i in ids}
        big = [i for i in ids if sizes[i] > 0.25 * max(sizes.values())]
        subs = []
        if len(big) == cols:
            boxes = {}
            for i in ids:
                ys, xs = np.where(lab == i); boxes[i] = (xs.min(), xs.max(), ys.min(), ys.max())
            big.sort(key=lambda i: boxes[i][0] + boxes[i][1])
            owner = {i: i for i in big}
            for i in ids:
                if i in big: continue
                b = boxes[i]; best = None
                for j in big:
                    q = boxes[j]
                    dx = max(q[0] - b[1], b[0] - q[1], 0); dy = max(q[2] - b[3], b[2] - q[3], 0)
                    d = (dx * dx + dy * dy) ** 0.5
                    if best is None or d < best[0]: best = (d, j)
                owner[i] = best[1]
            for j in big:
                keep = [i for i in ids if owner[i] == j and (i == j or not (CLEAN_WALK and r == 0))]
                m = np.isin(lab, keep)
                sub = rowA.copy(); sub[..., 3] = np.where(m, sub[..., 3], 0)
                xs = np.where(m.any(0))[0]
                subs.append((sub[:, xs.min():xs.max() + 1], lab[:, xs.min():xs.max() + 1] == j))
        else:
            print('  row', r, 'fallback to column cuts; big comps:', len(big))
            dens = ra.sum(0); cuts = [0]
            for kx in range(1, cols):
                e = W * kx // cols; lo, hi = e - 55, e + 55
                seg = dens[lo:hi]; mn = seg.min()
                cand = np.where(seg == mn)[0] + lo
                cuts.append(int(cand[np.argmin(np.abs(cand - e))]))
            cuts.append(W)
            for c in range(cols):
                sub = rowA[:, cuts[c]:cuts[c + 1]].copy(); sa = sub[..., 3] > 40
                l2, n2 = ndimage.label(sa)
                sz = ndimage.sum(sa, l2, range(1, n2 + 1))
                subs.append((sub, l2 == (1 + int(np.argmax(sz)))))
        for c, (sub, bigm) in enumerate(subs):
            ys, xs = np.where(bigm)
            top = ys.min(); h = ys.max() - top + 1
            ax = np.where(bigm[top:top + int(h * 0.4)])[1].mean()
            xsall = np.where((sub[..., 3] > 40).any(0))[0]
            frames.append((r, c, sub, ax, xsall.min(), xsall.max()))
    left = int(max(f[3] - f[4] for f in frames)) + 12
    right = int(max(f[5] - f[3] for f in frames)) + 12
    cw = left + right; ch = max(b[1] - b[0] for b in rb) + 16
    R = len(names)
    sheet = Image.new('RGBA', (cw * cols, ch * R), (0, 0, 0, 0)); cells = {}
    for r, c, sub, ax, _, _ in frames:
        cell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        fi = Image.fromarray(sub, 'RGBA')
        cell.paste(fi, (int(round(left - ax)), ch - 8 - sub.shape[0]), fi)
        cells[(r, c)] = cell; sheet.paste(cell, (c * cw, r * ch))
    sheet.save(f'{outdir}/{name}_sheet_right.png')
    sl = Image.new('RGBA', sheet.size, (0, 0, 0, 0))
    for (r, c), cell in cells.items(): sl.paste(cell.transpose(Image.FLIP_LEFT_RIGHT), (c * cw, r * ch))
    sl.save(f'{outdir}/{name}_sheet_left.png')
    def comp(cell, flip=False):
        im = Image.new('RGBA', (cw, ch), bg + (255,))
        im.alpha_composite(cell.transpose(Image.FLIP_LEFT_RIGHT) if flip else cell); return im.convert('RGB')
    dur = {'walk': 140, 'run': 90, 'attack': 150}
    for r, nm in enumerate(names):
        for flip, side in ((False, 'right'), (True, 'left')):
            fr = [comp(cells[(r, c)], flip) for c in range(cols)]
            d = [dur.get(nm, 120)] * cols
            if nm == 'attack': d[-1] = 450
            fr[0].save(f'{outdir}/{name}_{nm}_{side}.gif', save_all=True, append_images=fr[1:], duration=d, loop=0, disposal=2)
    prev = []
    for c in range(cols):
        im = Image.new('RGB', (cw * 2 + 30, ch * R + 10 * (R + 1)), (30, 30, 30))
        for r in range(R):
            im.paste(comp(cells[(r, c)], True), (10, 10 + r * (ch + 10)))
            im.paste(comp(cells[(r, c)], False), (20 + cw, 10 + r * (ch + 10)))
        prev.append(im)
    prev[0].save(f'{outdir}/{name}_preview.gif', save_all=True, append_images=prev[1:], duration=130, loop=0)
    chk = Image.new('RGBA', sheet.size, (70, 90, 110, 255)); chk.alpha_composite(sheet)
    chk.convert('RGB').save(f'{outdir}/_check_{name}.jpg', quality=85)
    print(name, 'cell', (cw, ch), 'sheet', sheet.size)

if __name__ == '__main__':
    rm = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 and sys.argv[4] != '-' else None
    if len(sys.argv) > 5 and sys.argv[5] == 'cleanwalk':
        globals()['CLEAN_WALK'] = True
    build(sys.argv[1], sys.argv[2], sys.argv[3], rm)
