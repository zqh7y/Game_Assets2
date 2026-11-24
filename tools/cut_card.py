import sys, numpy as np
from PIL import Image
from scipy import ndimage

def cut(src, out):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.int32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    corner = a[:12, :12].reshape(-1, 3).mean(0)
    green = corner[1] > corner[0] and corner[1] > corner[2]
    k = (G - np.maximum(R, B)) if green else (np.minimum(R, B) - G)
    strong = k > 70
    lab, n = ndimage.label(strong)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    border = border[border > 0]
    bg = np.isin(lab, border) | (k > 150)
    edge = ndimage.binary_dilation(bg, iterations=3) & ~bg
    alpha = np.full(k.shape, 255, np.int32)
    alpha[bg] = 0
    alpha[edge] = np.clip(255 - (k[edge] - 20) * 255 // 60, 0, 255)
    spill = np.clip(k, 0, None)
    out_rgb = a.copy()
    if green:
        out_rgb[..., 1] = np.where(edge & (k > 10), G - spill, G)
    else:
        out_rgb[..., 0] = np.where(edge & (k > 10), R - spill, R)
        out_rgb[..., 2] = np.where(edge & (k > 10), B - spill, B)
    rgba = np.dstack([np.clip(out_rgb, 0, 255), alpha]).astype(np.uint8)
    res = Image.fromarray(rgba, 'RGBA')
    ys, xs = np.where(alpha > 40)
    res = res.crop((max(xs.min() - 4, 0), max(ys.min() - 4, 0), min(xs.max() + 5, res.width), min(ys.max() + 5, res.height)))
    res.save(out)
    return res, ('green' if green else 'magenta')

if __name__ == '__main__':
    names = sys.argv[3:]
    thumbs = []
    for n in names:
        res, key = cut(f'{sys.argv[1]}/{n}.jpg', f'{sys.argv[2]}/{n}_card.png')
        print(n, res.size, key)
        t = Image.new('RGBA', res.size, (40, 44, 52, 255)); t.alpha_composite(res)
        thumbs.append(t.convert('RGB').resize((400, int(400 * res.height / res.width))))
    h = max(t.height for t in thumbs)
    sheet = Image.new('RGB', (410 * 5 + 10, (h + 10) * ((len(thumbs) + 4) // 5) + 10), (40, 44, 52))
    for i, t in enumerate(thumbs):
        sheet.paste(t, (10 + (i % 5) * 410, 10 + (i // 5) * (h + 10)))
    sheet.save(f'{sys.argv[2]}/_all_cards.jpg', quality=90)
