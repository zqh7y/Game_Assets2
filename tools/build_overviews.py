"""Rebuild the overview images:
  animations/_overview.jpg   every brawler's <Name>_sheet_right.png (row 1 walk, row 2 attack)
  weapons/_overview.jpg      every weapon and projectile, with its file name
  effects/combat/_overview.jpg  every combat effect strip, with its name
usage: python3 -I tools/build_overviews.py [REPO]"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

BG, PANEL, TXT = (40, 44, 53), (70, 88, 110), (255, 255, 255)


def font(sz):
    p = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def grid(panels, cols, gap=10):
    rows = [panels[i:i + cols] for i in range(0, len(panels), cols)]
    cw = max(p.width for p in panels)
    rh = [max(p.height for p in r) for r in rows]
    out = Image.new('RGBA', (gap + cols * (cw + gap), gap + sum(h + gap for h in rh)), BG)
    y = gap
    for r, h in zip(rows, rh):
        for i, p in enumerate(r):
            out.alpha_composite(p, (gap + i * (cw + gap), y))
        y += h + gap
    return out.convert('RGB')


def labeled(img, label, width, title=30, pad=10):
    s = img.convert('RGBA')
    k = min(1.0, (width - 2 * pad) / s.width)
    s = s.resize((max(1, round(s.width * k)), max(1, round(s.height * k))), Image.LANCZOS)
    pan = Image.new('RGBA', (width, title + s.height + pad), PANEL)
    pan.alpha_composite(s, ((width - s.width) // 2, title))
    ImageDraw.Draw(pan).text((8, 5), label, font=font(18), fill=TXT)
    return pan


def animations(repo):
    root = f'{repo}/animations'
    names = sorted(d for d in os.listdir(root) if os.path.isdir(f'{root}/{d}'))
    panels = [labeled(Image.open(f'{root}/{n}/{n}_sheet_right.png'), n, 520)
              for n in names if os.path.exists(f'{root}/{n}/{n}_sheet_right.png')]
    if panels:
        grid(panels, 3).save(f'{root}/_overview.jpg', quality=90)


def weapons(repo):
    root = f'{repo}/weapons'
    files = sorted(f for f in os.listdir(root) if f.endswith('.png'))
    files += ['projectiles/' + f for f in sorted(os.listdir(f'{root}/projectiles')) if f.endswith('.png')]
    panels = [labeled(Image.open(f'{root}/{f}'), f[:-4].replace('projectiles/', ''), 300) for f in files]
    if panels:
        grid(panels, 6).save(f'{root}/_overview.jpg', quality=90)


def effects(repo):
    root = f'{repo}/effects/combat'
    names = sorted(f[:-10] for f in os.listdir(root) if f.endswith('_sheet.png'))
    panels = [labeled(Image.open(f'{root}/{n}_sheet.png'), n, 900) for n in names]
    if panels:
        grid(panels, 1).save(f'{root}/_overview.jpg', quality=90)


if __name__ == '__main__':
    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    animations(repo)
    weapons(repo)
    effects(repo)
    print('overviews rebuilt')
