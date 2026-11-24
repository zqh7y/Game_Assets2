"""Effects sheet slicer.
Usage: python3 -I build_fx.py SRC.jpg OUTDIR name1,name2,name3,name4 [cols=4]
SRC is a keyed (magenta or green) sheet with one effect per row, `cols` frames per row.
Outputs per effect: OUTDIR/<name>_sheet.png (transparent strip), OUTDIR/<name>_1..N.png,
OUTDIR/<name>.gif, plus OUTDIR/_check_<first name>.jpg (look at it!).
"""
import sys
import numpy as np
from PIL import Image


def key(im):
    a = np.asarray(im.convert('RGB')).astype(np.int32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    c = a[:10, :10].reshape(-1, 3).mean(0)
    green = c[1] > c[0] and c[1] > c[2]
    k = (G - np.maximum(R, B)) if green else (np.minimum(R, B) - G)
    alpha = np.clip(255 - (k - 40) * 255 // 50, 0, 255)
    spill = np.clip(k, 0, None)
    out = a.copy()
    m = k > 15
    if green:
        out[..., 1] = np.where(m, G - spill, G)
    else:
        out[..., 0] = np.where(m, R - spill, R)
        out[..., 2] = np.where(m, B - spill, B)
    return np.dstack([np.clip(out, 0, 255), alpha]).astype(np.uint8)


def cuts(density, n, slack):
    """n-1 cut positions near the even grid lines, at the emptiest spot within +-slack."""
    L = len(density)
    res = [0]
    for k in range(1, n):
        c = L * k // n
        lo, hi = max(0, c - slack), min(L, c + slack)
        seg = density[lo:hi]
        mn = seg.min()
        idx = np.where(seg == mn)[0]
        res.append(lo + int(idx[np.argmin(np.abs(idx - (c - lo)))]))
    res.append(L)
    return res


def main():
    src, outdir, names = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
    cols = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    rgba = key(Image.open(src))
    solid = rgba[..., 3] > 60
    H, W = solid.shape
    rows = cuts(solid.sum(1), len(names), H // (len(names) * 4))
    checks = []
    for r, name in enumerate(names):
        y0, y1 = rows[r], rows[r + 1]
        band = solid[y0:y1]
        xs = cuts(band.sum(0), cols, W // (cols * 5))
        frames = []
        for c in range(cols):
            cell = rgba[y0:y1, xs[c]:xs[c + 1]]
            m = cell[..., 3] > 60
            if m.any():
                yy, xx = np.where(m)
                cell = cell[max(0, yy.min() - 2):yy.max() + 3, max(0, xx.min() - 2):xx.max() + 3]
            else:
                cell = np.zeros((4, 4, 4), np.uint8)
            frames.append(Image.fromarray(cell, 'RGBA'))
        cw = max(f.width for f in frames) + 8
        ch = max(f.height for f in frames) + 8
        cells = []
        for f in frames:  # centered in a uniform cell
            cimg = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
            cimg.alpha_composite(f, ((cw - f.width) // 2, (ch - f.height) // 2))
            cells.append(cimg)
        strip = Image.new('RGBA', (cw * cols, ch), (0, 0, 0, 0))
        for i, cimg in enumerate(cells):
            strip.alpha_composite(cimg, (i * cw, 0))
            cimg.save(f'{outdir}/{name}_{i + 1}.png')
        strip.save(f'{outdir}/{name}_sheet.png')
        gif = []
        for cimg in cells:
            bg = Image.new('RGBA', (cw, ch), (246, 178, 115, 255))
            bg.alpha_composite(cimg)
            gif.append(bg.convert('P', palette=Image.ADAPTIVE))
        gif[0].save(f'{outdir}/{name}.gif', save_all=True, append_images=gif[1:],
                    duration=[110] * (cols - 1) + [400], loop=0, disposal=2)
        chk = Image.new('RGBA', strip.size, (70, 88, 110, 255))
        chk.alpha_composite(strip)
        checks.append(chk.convert('RGB'))
        print(name, 'cell', (cw, ch))
    w = max(c.width for c in checks)
    out = Image.new('RGB', (w, sum(c.height for c in checks) + 10 * len(checks)), (40, 44, 52))
    y = 0
    for c in checks:
        out.paste(c, (0, y))
        y += c.height + 10
    out.save(f'{outdir}/_check_{names[0]}.jpg', quality=88)


if __name__ == '__main__':
    main()
