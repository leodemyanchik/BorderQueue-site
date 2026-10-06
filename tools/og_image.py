"""Рисует картинку для превью ссылок (og:image) в стиле сайта: assets/og.png, 1200×630.

Шрифты Manrope и Onest (Google Fonts, OFL) нужны рядом, в tools/fonts/, или путь в FONTS:

    python tools/og_image.py

Линия графика нарисована, а не взята из живых данных: превью кешируют Telegram и соцсети,
и настоящая очередь на картинке через час уже была бы неправдой.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
W, H = 1200, 630
S = 2  # рисуем вдвое крупнее и уменьшаем: так края букв и линий гладкие

BG = (248, 250, 252)
HEADING = (30, 58, 138)
TEXT2 = (71, 85, 105)
BLUE = (59, 130, 246)
LINE = (226, 232, 240)
LOGO_BAR = (147, 197, 253)


def font(name, size, weight):
    f = ImageFont.truetype(str(FONTS / name), size * S)
    f.set_variation_by_axes([weight])
    return f


img = Image.new("RGB", (W * S, H * S), BG)
d = ImageDraw.Draw(img)
X = 80 * S

# Логотип и название
d.rounded_rectangle([X, 72 * S, X + 64 * S, 136 * S], radius=18 * S, fill=HEADING)
for y, x2 in ((122, 46), (104, 40), (86, 30)):
    d.line([X + 18 * S, y * S, X + x2 * S + 0 * S, y * S], fill=LOGO_BAR, width=6 * S)
    d.ellipse([X + 15 * S, y * S - 3 * S, X + 21 * S, y * S + 3 * S], fill=LOGO_BAR)
    d.ellipse([X + x2 * S - 3 * S, y * S - 3 * S, X + x2 * S + 3 * S, y * S + 3 * S], fill=LOGO_BAR)
d.text((X + 84 * S, 104 * S), "BorderQueue", font=font("Manrope.ttf", 36, 700), fill=HEADING, anchor="lm")

# Надпись
d.text((X, 210 * S), "ГРАНИЦА БЕЛАРУСИ С ЕС", font=font("Onest.ttf", 24, 600), fill=BLUE, anchor="ls")
title = font("Manrope.ttf", 76, 700)
d.text((X, 300 * S), "Очередь на границе", font=title, fill=HEADING, anchor="ls")
d.text((X, 390 * S), "сейчас", font=title, fill=HEADING, anchor="ls")
d.text((X, 456 * S), "Сколько ждать вызова на всех шести пунктах пропуска",
       font=font("Onest.ttf", 30, 400), fill=TEXT2, anchor="ls")

# Линия очереди за сутки: пусто ночью, утренний рост, вечерний спад
pts = [0, 0, 1, 1, 2, 6, 18, 40, 62, 78, 86, 90, 92, 91, 88, 85, 83, 80, 74, 66, 60, 55]
gx0, gx1, gy0, gy1 = 80, 1120, 590, 500
xs = [gx0 + (gx1 - gx0) * i / (len(pts) - 1) for i in range(len(pts))]
ys = [gy0 - (gy0 - gy1) * v / 100 for v in pts]
poly = [(x * S, y * S) for x, y in zip(xs, ys)]
fill = Image.new("RGBA", img.size, (0, 0, 0, 0))
ImageDraw.Draw(fill).polygon(poly + [(gx1 * S, gy0 * S), (gx0 * S, gy0 * S)], fill=BLUE + (26,))
img.paste(fill, (0, 0), fill)
d = ImageDraw.Draw(img)
d.line(poly, fill=BLUE, width=4 * S, joint="curve")
d.line([gx0 * S, gy0 * S, gx1 * S, gy0 * S], fill=LINE, width=2 * S)

# Адрес сайта
d.text((1120 * S, 104 * S), "borderqueue.app", font=font("Onest.ttf", 28, 500), fill=TEXT2, anchor="rm")

img = img.resize((W, H), Image.LANCZOS)
out = ROOT / "assets" / "og.png"
img.save(out, optimize=True)
print(out, out.stat().st_size)
