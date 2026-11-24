"""Build the armed (gun in hands) animations from a Gemini sheet.

usage: python3 -I tools/build_armed.py SHEET.jpg REPO OUTROOT NameA [NameB] [--melee]

SHEET.jpg is a keyed sheet with 4 frames per row:
  two brawlers:  row 1 A walk, row 2 A shoot, row 3 B walk, row 4 B shoot
  one brawler:   row 1 walk, row 2 shoot
Writes OUTROOT/<Name>/<Name>_armed_sheet_right.png / _left.png (row 1 walk, row 2 shoot),
<Name>_armed_{walk,run,shoot}_{right,left}.gif (run = the walk frames played faster),
<Name>_armed_preview.gif (shot, bullet, hit) and _check_<Name>.jpg (look at it; never commit it).
With --melee row 2 is the melee attack: the GIF is named _armed_attack_ and no bullet is drawn.
Needs REPO/weapons/bullets/<name>_bullet.png and REPO/effects/weapons/<name>_hit_2.png.
"""
import sys, os, subprocess, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BG = (246, 178, 115, 255)


def gif(frames, path, durations):
    out = []
    for f in frames:
        bg = Image.new('RGBA', f.size, BG)
        bg.alpha_composite(f)
        out.append(bg.convert('P', palette=Image.ADAPTIVE))
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations, loop=0, disposal=2)


def one(src_img, repo, outroot, name, melee=False):
    low = name.lower()
    act = 'attack' if melee else 'shoot'
    tmp = tempfile.mkdtemp()
    src_img.save(f'{tmp}/src.jpg', quality=97)
    subprocess.run([sys.executable, '-I', f'{HERE}/build_anim.py', f'{tmp}/src.jpg', name, tmp, '0,0,1'],
                   check=True, stdout=subprocess.DEVNULL)
    sheet = Image.open(f'{tmp}/{name}_sheet_right.png').convert('RGBA')
    cw, ch = sheet.width // 4, sheet.height // 3
    walk = [sheet.crop((k * cw, 0, (k + 1) * cw, ch)) for k in range(4)]
    shoot = [sheet.crop((k * cw, 2 * ch, (k + 1) * cw, 3 * ch)) for k in range(4)]
    out = f'{outroot}/{name}'
    os.makedirs(out, exist_ok=True)
    right = Image.new('RGBA', (cw * 4, ch * 2), (0, 0, 0, 0))
    left = Image.new('RGBA', (cw * 4, ch * 2), (0, 0, 0, 0))
    for r, row in enumerate((walk, shoot)):
        for k, f in enumerate(row):
            right.alpha_composite(f, (k * cw, r * ch))
            left.alpha_composite(f.transpose(Image.FLIP_LEFT_RIGHT), (k * cw, r * ch))
    right.save(f'{out}/{name}_armed_sheet_right.png')
    left.save(f'{out}/{name}_armed_sheet_left.png')
    for label, row, dur in (('walk', walk, [140] * 4), ('run', walk, [85] * 4), (act, shoot, [220, 80, 120, 260])):
        gif(row, f'{out}/{name}_armed_{label}_right.gif', dur)
        gif([f.transpose(Image.FLIP_LEFT_RIGHT) for f in row], f'{out}/{name}_armed_{label}_left.gif', dur)

    if melee:
        w2, h2 = max(f.width for f in walk + shoot), ch
        gif(walk + walk + shoot, f'{out}/{name}_armed_preview.gif', [140] * 8 + [220, 90, 140, 500])
        chk = Image.new('RGBA', (cw * 6, ch), (70, 88, 110, 255))
        for i, f in enumerate(walk[:2] + shoot):
            chk.alpha_composite(f, (i * cw, 0))
        chk.convert('RGB').save(f'{out}/_check_{name}.jpg', quality=88)
        print(name, 'cell', (cw, ch), 'melee')
        return
    # muzzle = right-most point of the aim frame
    a = np.asarray(shoot[0])[..., 3] > 60
    xs = np.where(a.any(0))[0]
    mx = int(xs.max())
    my = int(np.where(a[:, max(0, mx - 6):mx + 1].any(1))[0].mean())
    bw = int(xs.max() - xs.min())
    bullet = Image.open(f'{repo}/weapons/bullets/{low}_bullet.png').convert('RGBA')
    s = 0.30 * bw / bullet.width
    bullet = bullet.resize((int(bullet.width * s), int(bullet.height * s)), Image.LANCZOS)
    hit = Image.open(f'{repo}/effects/weapons/{low}_hit_2.png').convert('RGBA')
    s = 0.55 * bw / hit.width
    hit = hit.resize((int(hit.width * s), int(hit.height * s)), Image.LANCZOS)
    travel = int(2.2 * bw)
    pw = cw + travel + hit.width
    top = max(0, hit.height // 2 - my + 4)

    def canvas(cell, extra=None, at=0.0, scale=1.0):
        cv = Image.new('RGBA', (pw, ch + top), (0, 0, 0, 0))
        cv.alpha_composite(cell, (0, top))
        if extra is not None:
            e = extra if scale == 1.0 else extra.resize((max(1, int(extra.width * scale)), max(1, int(extra.height * scale))), Image.LANCZOS)
            cv.alpha_composite(e, (int(mx + at * travel + (bullet.width if extra is bullet else hit.width // 2) - e.width / 2 + 6),
                                   int(top + my - e.height / 2)))
        return cv
    seq = [canvas(shoot[0]), canvas(shoot[1]), canvas(shoot[2], bullet, 0.15), canvas(shoot[3], bullet, 0.5),
           canvas(shoot[3], bullet, 0.82), canvas(shoot[3], hit, 1.0, 0.6), canvas(shoot[3], hit, 1.0, 1.0),
           canvas(shoot[3], hit, 1.0, 1.2), canvas(shoot[3])]
    gif(seq, f'{out}/{name}_armed_preview.gif', [260, 80, 80, 70, 70, 70, 110, 90, 450])

    chk = Image.new('RGBA', (cw * 6, ch), (70, 88, 110, 255))
    for i, f in enumerate(walk[:2] + shoot):
        chk.alpha_composite(f, (i * cw, 0))
    chk.convert('RGB').save(f'{out}/_check_{name}.jpg', quality=88)
    print(name, 'cell', (cw, ch))


def main():
    src, repo, outroot, names = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
    melee = '--melee' in names
    names = [n for n in names if n != '--melee']
    im = Image.open(src).convert('RGB')
    if len(names) == 1:
        one(im, repo, outroot, names[0], melee)
        return
    a = np.asarray(im).astype(np.int32)
    c = a[:10, :10].reshape(-1, 3).mean(0)
    green = c[1] > c[0] and c[1] > c[2]
    k = (a[..., 1] - np.maximum(a[..., 0], a[..., 2])) if green else (np.minimum(a[..., 0], a[..., 2]) - a[..., 1])
    solid = (k < 60).sum(1)
    H = im.height
    lo, hi = H // 2 - H // 12, H // 2 + H // 12
    cut = lo + int(np.argmin(solid[lo:hi]))
    one(im.crop((0, 0, im.width, cut)), repo, outroot, names[0], melee)
    one(im.crop((0, cut, im.width, H)), repo, outroot, names[1], melee)


if __name__ == '__main__':
    main()
