"""Rebuild animations/_overview.jpg (unarmed sheets) and animations/_armed_overview.jpg.
usage: python3 -I tools/build_overviews.py [REPO]"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

BG, PANEL, TXT = (40, 44, 53), (70, 88, 110), (255, 255, 255)

def font(sz):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def cells(sheet, rows):
    w, h = sheet.size
    cw, ch = w // 4, h // rows
    return [[sheet.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)) for c in range(4)] for r in range(rows)]

def unarmed(repo, names):
    pw, cols, gap, title = 420, 4, 10, 34
    panels = []
    for n in names:
        p = f'{repo}/animations/{n}/{n}_sheet_right.png'
        if not os.path.exists(p):
            continue
        s = Image.open(p).convert('RGBA')
        sw = pw - 20
        s = s.resize((sw, round(s.height * sw / s.width)), Image.LANCZOS)
        pan = Image.new('RGBA', (pw, title + s.height + 10), PANEL)
        pan.alpha_composite(s, (10, title))
        ImageDraw.Draw(pan).text((8, 6), n, font=font(20), fill=TXT)
        panels.append(pan)
    rows = [panels[i:i + cols] for i in range(0, len(panels), cols)]
    rh = [max(p.height for p in r) for r in rows]
    W = gap + cols * (pw + gap)
    out = Image.new('RGBA', (W, gap + sum(h + gap for h in rh)), BG)
    y = gap
    for r, h in zip(rows, rh):
        for i, p in enumerate(r):
            out.alpha_composite(p, (gap + i * (pw + gap), y))
        y += h + gap
    out.convert('RGB').save(f'{repo}/animations/_overview.jpg', quality=90)

def armed(repo, names):
    H, gap, cols = 220, 8, 3
    panels = []
    for n in names:
        p = f'{repo}/animations/{n}/{n}_armed_sheet_right.png'
        if not os.path.exists(p):
            continue
        c = cells(Image.open(p).convert('RGBA'), 2)
        picks = [c[0][0], c[0][2], c[1][1]]
        sc = H / picks[0].height
        picks = [f.resize((round(f.width * sc), H), Image.LANCZOS) for f in picks]
        pan = Image.new('RGBA', (sum(f.width for f in picks) + 20, H + 10), PANEL)
        x = 10
        for f in picks:
            pan.alpha_composite(f, (x, 5)); x += f.width
        panels.append(pan)
    rows = [panels[i:i + cols] for i in range(0, len(panels), cols)]
    W = max(sum(p.width for p in r) + gap * (len(r) + 1) for r in rows)
    out = Image.new('RGBA', (W, gap + len(rows) * (H + 10 + gap)), BG)
    y = gap
    for r in rows:
        x = gap
        for p in r:
            out.alpha_composite(p, (x, y)); x += p.width + gap
        y += H + 10 + gap
    out.convert('RGB').save(f'{repo}/animations/_armed_overview.jpg', quality=90)

if __name__ == '__main__':
    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    names = sorted(d for d in os.listdir(f'{repo}/animations') if os.path.isdir(f'{repo}/animations/{d}'))
    unarmed(repo, names)
    armed(repo, names)
    print('overviews rebuilt for', ', '.join(names))
