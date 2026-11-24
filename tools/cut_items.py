"""Cut a keyed grid sheet (weapons, bullets, hit effects...) into one transparent PNG per cell.
usage: python3 -I tools/cut_items.py SRC.jpg OUTDIR COLS ROWS name1,name2,...
Names go row by row; use - to skip a cell. Everything whose centre lies in a cell becomes that cell's PNG."""
import os, sys, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_fx import key, cuts

def main():
    src, out, cols, rows = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    names = sys.argv[5].split(',')
    rgba = key(Image.open(src))
    solid = rgba[..., 3] > 60
    H, W = solid.shape
    ry = cuts(solid.sum(1), rows, H // (rows * 4))
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=3))
    i = 0
    for r in range(rows):
        band = solid[ry[r]:ry[r + 1]]
        cx = cuts(band.sum(0), cols, W // (cols * 4))
        for c in range(cols):
            name = names[i]; i += 1
            if name == '-': continue
            # all components whose centre lies in this cell
            cell = np.zeros_like(solid)
            ids = np.unique(lab[ry[r]:ry[r + 1], cx[c]:cx[c + 1]])
            for k in ids:
                if k == 0: continue
                ys, xs = np.where(lab == k)
                my, mx = ys.mean(), xs.mean()
                if ry[r] <= my < ry[r + 1] and cx[c] <= mx < cx[c + 1]:
                    cell |= (lab == k)
            m = cell & solid
            if not m.any(): print('EMPTY', name); continue
            ys, xs = np.where(m)
            y0, y1, x0, x1 = max(0, ys.min() - 3), ys.max() + 4, max(0, xs.min() - 3), xs.max() + 4
            a = rgba[y0:y1, x0:x1].copy()
            a[..., 3] = np.where(cell[y0:y1, x0:x1], a[..., 3], 0)
            Image.fromarray(a, 'RGBA').save(f'{out}/{name}.png')
            print(name, a.shape[1], a.shape[0])

if __name__ == '__main__':
    main()
