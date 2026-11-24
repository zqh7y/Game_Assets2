"""Attach each brawler's weapon to its animation sheet and build the armed animations.

usage: python3 -I tools/attach_gun.py REPO OUTDIR [Name ...]

Reads  REPO/animations/<Name>/<Name>_sheet_right.png (3 rows x 4 frames: walk, run, attack)
       REPO/weapons/<gun>.png, REPO/weapons/muzzle_flash.png,
       REPO/weapons/bullets/<name>_bullet.png, REPO/effects/weapons/<name>_hit_2.png
Writes OUTDIR/<Name>/<Name>_armed_sheet_right.png / _left.png (rows: walk, run, shoot),
       <Name>_armed_{walk,run,shoot}_{right,left}.gif, <Name>_armed_preview.gif
       and OUTDIR/<Name>/_check_<Name>.jpg (look at it; never commit it).

Per brawler config (CFG):
  gun     weapon file name in weapons/
  w       gun width as a fraction of the body width
  at      where the grip sits on the body, as fractions of the body box (x, y)
  grip    grip point inside the gun image, as fractions (x, y)
  muzzle  muzzle point inside the gun image, as fractions (x, y)
  hand    hand colour drawn over the grip, or None (mounted guns, tentacles)
  tint    muzzle flash colour
  rot     resting rotation of the gun in degrees (counter-clockwise, muzzle up)
"""
import sys, math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

OUTLINE = (58, 40, 36, 255)
BG = (246, 178, 115, 255)

CFG = {
    'Beam':   dict(gun='beam_lighthouse_sniper',    w=1.35, at=(0.55, 0.82), grip=(0.38, 0.72), muzzle=(1.0, 0.40), hand='#F4B183', tint='#FFD93B'),
    'Dough':  dict(gun='dough_rollingpin_shotgun',  w=1.05, at=(0.48, 0.83), grip=(0.12, 0.80), muzzle=(1.0, 0.38), hand='#F4B183', tint='#FFFFFF'),
    'Soot':   dict(gun='soot_chimney_smg',          w=1.00, at=(0.62, 0.85), grip=(0.40, 0.75), muzzle=(1.0, 0.42), hand='#F4B183', tint='#8A8A92'),
    'Honey':  dict(gun='honey_honeycomb_ak',        w=1.25, at=(0.55, 0.79), grip=(0.33, 0.62), muzzle=(1.0, 0.25), hand='#FFFFFF', tint='#F6B93B'),
    'Nana':   dict(gun='nana_slipper_launcher',     w=1.20, at=(0.72, 0.88), grip=(0.18, 0.85), muzzle=(1.0, 0.35), hand='#F4B183', tint='#C9A7E0'),
    'Capy':   dict(gun='capy_citrus_minigun',       w=0.80, at=(0.55, 0.86), grip=(0.45, 0.92), muzzle=(1.0, 0.60), hand=None,      tint='#F28C28'),
    'Axo':    dict(gun='axo_bubble_blaster',        w=0.75, at=(0.74, 0.90), grip=(0.22, 0.85), muzzle=(1.0, 0.42), hand='#F9C6D3', tint='#F0629A'),
    'Pango':  dict(gun='pango_pinecone_bazooka',    w=0.90, at=(0.60, 0.85), grip=(0.33, 0.88), muzzle=(1.0, 0.40), hand='#F3E2B8', tint='#FF8A1F'),
    'Bill':   dict(gun='bill_harpoon_gun',          w=1.25, at=(0.42, 0.72), grip=(0.33, 0.80), muzzle=(1.0, 0.40), hand='#5E7F98', tint='#BFE6FF'),
    'Tardi':  dict(gun='tardi_ray_gun',             w=0.80, at=(0.40, 0.10), grip=(0.20, 0.95), muzzle=(1.0, 0.45), hand=None,      tint='#7FE8E0'),
    'Octo':   dict(gun='octo_ink_soaker',           w=1.00, at=(0.70, 0.78), grip=(0.22, 0.85), muzzle=(1.0, 0.45), hand=None,      tint='#4A4690'),
    'Dragon': dict(gun='dragon_chili_flamethrower', w=0.95, at=(0.70, 0.86), grip=(0.20, 0.85), muzzle=(1.0, 0.50), hand='#E23B33', tint='#FF8A1F'),
}


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def body_mask(frame):
    a = np.asarray(frame)[..., 3] > 60
    lab, k = ndimage.label(a)
    if k == 0:
        return a
    sizes = ndimage.sum(a, lab, range(1, k + 1))
    return lab == (1 + int(np.argmax(sizes)))


def anchor(mask):
    ys, xs = np.where(mask)
    top = ys.min()
    h = ys.max() - top + 1
    head = xs[ys < top + 0.4 * h]
    return float(head.mean()), int(top)


def tinted(flash, colour):
    a = np.asarray(flash).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    coloured = (mx > 110) & ((mx - mn) > 60)          # the yellow edge, not white, not outline
    c = hexrgb(colour)
    for i in range(3):
        a[..., i] = np.where(coloured, c[i] * (mx / 255.0), a[..., i])
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')


def place(canvas, img, pivot, target, angle=0.0):
    """Paste img on canvas so that its pivot point lands on target, rotated by angle around the pivot."""
    R = int(math.hypot(img.width, img.height)) + 4
    big = Image.new('RGBA', (2 * R, 2 * R), (0, 0, 0, 0))
    big.alpha_composite(img, (int(round(R - pivot[0])), int(round(R - pivot[1]))))
    if angle:
        big = big.rotate(angle, resample=Image.BICUBIC, center=(R, R))
    ox, oy = int(round(target[0] - R)), int(round(target[1] - R))
    # crop to canvas
    x0, y0 = max(0, -ox), max(0, -oy)
    x1, y1 = min(big.width, canvas.width - ox), min(big.height, canvas.height - oy)
    if x1 > x0 and y1 > y0:
        canvas.alpha_composite(big.crop((x0, y0, x1, y1)), (ox + x0, oy + y0))


def rot(vx, vy, angle):
    t = math.radians(-angle)          # image coordinates: y down, PIL rotates counter-clockwise
    return vx * math.cos(t) - vy * math.sin(t), vx * math.sin(t) + vy * math.cos(t)


def gif(frames, path, durations):
    out = []
    for f in frames:
        bg = Image.new('RGBA', f.size, BG)
        bg.alpha_composite(f)
        out.append(bg.convert('P', palette=Image.ADAPTIVE))
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations, loop=0, disposal=2)


def build(repo, outroot, name):
    c = CFG[name]
    low = name.lower()
    sheet = Image.open(f'{repo}/animations/{name}/{name}_sheet_right.png').convert('RGBA')
    cw, ch = sheet.width // 4, sheet.height // 3
    frames = [[sheet.crop((k * cw, r * ch, (k + 1) * cw, (r + 1) * ch)) for k in range(4)] for r in range(3)]
    ref = frames[0][1]
    rm = body_mask(ref)
    ys, xs = np.where(rm)
    bx0, by0, bw, bh = xs.min(), ys.min(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    rax, rtop = anchor(rm)

    gun = Image.open(f'{repo}/weapons/{c["gun"]}.png').convert('RGBA')
    s = c['w'] * bw / gun.width
    gun = gun.resize((max(1, int(gun.width * s)), max(1, int(gun.height * s))), Image.LANCZOS)
    grip = (c['grip'][0] * gun.width, c['grip'][1] * gun.height)
    muz = (c['muzzle'][0] * gun.width - grip[0], c['muzzle'][1] * gun.height - grip[1])
    flash = tinted(Image.open(f'{repo}/weapons/muzzle_flash.png').convert('RGBA'), c['tint'])
    fs = 0.42 * bw / flash.width
    flash = flash.resize((int(flash.width * fs), int(flash.height * fs)), Image.LANCZOS)
    rest = c.get('rot', 0.0)

    padl, padt = int(0.12 * bw) + 6, int(max(0, grip[1] - (by0 + c['at'][1] * bh)) + 0.12 * bh) + 6
    padr = int(max(0, bx0 + c['at'][0] * bw + muz[0] + flash.width * 0.9 - cw)) + 12
    ncw, nch = cw + padl + padr, ch + padt

    def compose(base, dx=0.0, bob=0.0, body_dx=0, gdx=0.0, angle=0.0, fire=False):
        cell = Image.new('RGBA', (ncw, nch), (0, 0, 0, 0))
        cell.alpha_composite(base, (padl + body_dx, padt))
        tx = padl + body_dx + bx0 + c['at'][0] * bw + dx + gdx
        ty = padt + by0 + c['at'][1] * bh + bob
        place(cell, gun, grip, (tx, ty), rest + angle)
        if c['hand']:
            r = max(7, int(0.075 * bw))
            hand = Image.new('RGBA', (4 * r, 4 * r), (0, 0, 0, 0))
            d = ImageDraw.Draw(hand)
            lw = max(3, int(0.022 * bw))
            d.ellipse((r, r, 3 * r, 3 * r - r // 4), fill=hexrgb(c['hand']) + (255,), outline=OUTLINE, width=lw)
            cell.alpha_composite(hand, (int(tx - 2 * r), int(ty - 2 * r - 0.02 * bh)))
        if fire:
            mx, my = rot(muz[0], muz[1], rest + angle)
            place(cell, flash, (flash.width * 0.12, flash.height / 2), (tx + mx, ty + my), rest + angle)
        return cell, (tx, ty)

    rows = []
    for r in range(2):                                   # walk, run
        row = []
        for k in range(4):
            ax, top = anchor(body_mask(frames[r][k]))
            cell, _ = compose(frames[r][k], dx=ax - rax, bob=top - rtop, angle=(1.5 if k % 2 else -1.5))
            row.append(cell)
        rows.append(row)
    shoot, muzzle_pts = [], []
    for body_dx, gdx, angle, fire in [(0, 0, 0, False), (-3, -0.07 * bw, 8, True), (-1, -0.03 * bw, 3, False), (0, 0, 0, False)]:
        cell, (tx, ty) = compose(ref, body_dx=body_dx, gdx=gdx, angle=angle, fire=fire)
        shoot.append(cell)
        mx, my = rot(muz[0], muz[1], rest + angle)
        muzzle_pts.append((tx + mx, ty + my))
    rows.append(shoot)

    out = f'{outroot}/{name}'
    os.makedirs(out, exist_ok=True)
    right = Image.new('RGBA', (ncw * 4, nch * 3), (0, 0, 0, 0))
    left = Image.new('RGBA', (ncw * 4, nch * 3), (0, 0, 0, 0))
    for r in range(3):
        for k in range(4):
            right.alpha_composite(rows[r][k], (k * ncw, r * nch))
            left.alpha_composite(rows[r][k].transpose(Image.FLIP_LEFT_RIGHT), (k * ncw, r * nch))
    right.save(f'{out}/{name}_armed_sheet_right.png')
    left.save(f'{out}/{name}_armed_sheet_left.png')
    for r, (label, dur) in enumerate([('walk', [140] * 4), ('run', [90] * 4), ('shoot', [160, 80, 90, 260])]):
        gif(rows[r], f'{out}/{name}_armed_{label}_right.gif', dur)
        gif([f.transpose(Image.FLIP_LEFT_RIGHT) for f in rows[r]], f'{out}/{name}_armed_{label}_left.gif', dur)

    # preview: shoot, bullet flies, hit
    bullet = Image.open(f'{repo}/weapons/bullets/{low}_bullet.png').convert('RGBA')
    bs = 0.34 * bw / bullet.width
    bullet = bullet.resize((int(bullet.width * bs), int(bullet.height * bs)), Image.LANCZOS)
    hit = Image.open(f'{repo}/effects/weapons/{low}_hit_2.png').convert('RGBA')
    hs = 0.62 * bw / hit.width
    hit = hit.resize((int(hit.width * hs), int(hit.height * hs)), Image.LANCZOS)
    travel = int(2.4 * bw)
    pw = ncw + travel + hit.width // 2 + 10
    mx0, my0 = muzzle_pts[0]
    seq, durs = [], []

    def canvas(cell):
        cv = Image.new('RGBA', (pw, nch), (0, 0, 0, 0))
        cv.alpha_composite(cell, (0, 0))
        return cv
    seq.append(canvas(shoot[0])); durs.append(260)
    seq.append(canvas(shoot[1])); durs.append(80)
    for i, t in enumerate((0.2, 0.5, 0.8)):
        cv = canvas(shoot[2] if i == 0 else shoot[3])
        place(cv, bullet, (bullet.width / 2, bullet.height / 2), (mx0 + t * travel, my0))
        seq.append(cv); durs.append(70)
    for sc, d in ((0.6, 70), (1.0, 110), (1.2, 90)):
        cv = canvas(shoot[3])
        h2 = hit.resize((max(1, int(hit.width * sc)), max(1, int(hit.height * sc))), Image.LANCZOS)
        place(cv, h2, (h2.width / 2, h2.height / 2), (mx0 + travel, my0))
        seq.append(cv); durs.append(d)
    seq.append(canvas(shoot[3])); durs.append(450)
    gif(seq, f'{out}/{name}_armed_preview.gif', durs)

    chk = Image.new('RGBA', (ncw * 3 + pw, nch), (70, 88, 110, 255))
    for i, cell in enumerate((rows[0][0], rows[1][1], shoot[1])):
        chk.alpha_composite(cell, (i * ncw, 0))
    chk.alpha_composite(seq[3], (3 * ncw, 0))
    chk.convert('RGB').save(f'{out}/_check_{name}.jpg', quality=88)
    print(name, 'cell', (ncw, nch), 'body', (bw, bh))


if __name__ == '__main__':
    repo, outroot = sys.argv[1], sys.argv[2]
    for n in (sys.argv[3:] or list(CFG)):
        build(repo, outroot, n)
