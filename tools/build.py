"""Собирает HTML-страницы сайта из одного шаблона.

Страницы статические: текст, заголовки и описания лежат прямо в HTML, чтобы их видели
поисковики, а цифры подставляет assets/app.js из открытых данных бота. Запуск:

    python tools/build.py

Адрес сайта в SITE: borderqueue.app (куплен 05.10.2026), он же в файле CNAME.
"""
from pathlib import Path

SITE = "https://borderqueue.app"
ROOT = Path(__file__).resolve().parent.parent

# Пункт, его пара на той стороне, страница, метка для бота, «в ком/чём» для заголовков.
CHECKPOINTS = [
    ("Brest", "Брест", "Тересполь, Польша", "brest", "site_brest", "Бресте"),
    ("Bruzgi", "Брузги", "Кузница, Польша", "bruzgi", "site_bruzgi", "Брузгах"),
    ("KamennyLog", "Каменный лог", "Мядининкай, Литва", "kamenny-log", "site_kamlog", "Каменном логе"),
    ("Benyakoni", "Бенякони", "Шальчининкай, Литва", "benyakoni", "site_benyakoni", "Бенякони"),
    ("Berestovitsa", "Берестовица", "Бобровники, Польша", "berestovitsa", "site_berestovitsa", "Берестовице"),
    ("Grigorovshchina", "Григоровщина", "Патерниеки, Латвия", "grigorovshchina", "site_grigorovshchina", "Григоровщине"),
]

LOGO = """<svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#1e3a8a"/><path d="M9 21.5h14M9 16h10M9 10.5h6" stroke="#93c5fd" stroke-width="2.6" stroke-linecap="round"/></svg>"""
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='9' fill='%231e3a8a'/%3E%3Cpath d='M9 21.5h14M9 16h10M9 10.5h6' "
           "stroke='%2393c5fd' stroke-width='2.6' stroke-linecap='round'/%3E%3C/svg%3E")
# Значок Telegram на кнопке: узнаваемая форма, а не эмодзи (правило скилла: иконки только SVG).
TG = """<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M21.4 4.6 2.9 11.7c-1.3.5-1.2 1.2-.2 1.5l4.7 1.5 1.8 5.6c.2.6.4.8.8.8.4 0 .6-.2.9-.5l2.3-2.2 4.8 3.5c.9.5 1.5.2 1.7-.8l3.1-14.7c.3-1.3-.5-1.9-1.4-1.6zM9.6 14.3l8.8-5.6c.4-.3.8-.1.5.2l-7.3 6.6-.3 3.2-1.7-4.4z"/></svg>"""

NAV = [("index.html", "Сейчас", "hide-sm"), ("weekend.html", "Выходные", ""), ("accuracy.html", "Точность", "hide-sm"), ("guide.html", "Справка", "hide-sm")]
BOT = "https://t.me/BorderTimerBot"


def page(file, title, description, body, data, active=None):
    nav = "".join(
        f'<a href="{href}" class="{cls}"{" aria-current=\"page\"" if href == active else ""}>{label}</a>'
        for href, label, cls in NAV)
    cp_links = " ".join(f'<a href="{slug}.html">{name}</a>' for _, name, _, slug, _, _ in CHECKPOINTS)
    canonical = f"{SITE}/" if file == "index.html" else f"{SITE}/{file}"
    attrs = " ".join(f'data-{k}="{v}"' for k, v in data.items())
    html = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="BorderQueue">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="BorderQueue: очередь на границе Беларуси сейчас">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f8fafc">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@600;700&amp;family=Onest:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="preconnect" href="https://borderqueueapi.onrender.com" crossorigin>
<link rel="stylesheet" href="assets/style.css">
<script src="assets/app.js" defer></script>
</head>
<body {attrs}>
<header class="top">
  <div class="wrap">
    <a class="brand" href="index.html">{LOGO}<span>BorderQueue</span></a>
    <nav class="nav" aria-label="Разделы">{nav}<a class="nav-bot" data-bot href="{BOT}">Бот</a></nav>
  </div>
</header>
<main class="wrap">
{body}
<section class="cta" aria-labelledby="cta-title">
  <div>
    <h2 id="cta-title">Бот следит за очередью за тебя</h2>
    <ul class="features">
      <li><strong>Напомнит, когда регистрироваться.</strong> Скажи, к какому времени хочешь быть на границе, и бот напишет, когда пора вставать в очередь.</li>
      <li><strong>Напишет, когда очередь дорастёт.</strong> Выбери пункт и число машин, и бот сообщит, как только очередь до него дойдёт.</li>
      <li><strong>Разбудит звонком.</strong> Если сообщение можно проспать, позвонит на телефон. Первый звонок бесплатно.</li>
    </ul>
  </div>
  <a class="btn" data-bot href="{BOT}">{TG}Открыть бота</a>
</section>
</main>
<footer>
  <div class="wrap">
    <p id="totals">Ожидание измерено по сотням тысяч машин: от регистрации до вызова, как было на самом деле.</p>
    <p>Данные электронной очереди на границе Беларуси, обновление каждые 5 минут. Это не официальный сайт пунктов пропуска: зарегистрироваться можно только через официальный сервис.</p>
    <div class="links">{cp_links} <a href="weekend.html">Выходные</a> <a href="accuracy.html">Точность прогноза</a> <a href="guide.html">Как зарегистрироваться</a> <a data-bot href="{BOT}">Телеграм-бот</a></div>
  </div>
</footer>
</body>
</html>
"""
    (ROOT / file).write_text(html, encoding="utf-8")


def hero(eyebrow, h1, lead, status=True, button=True):
    parts = ['<section class="hero">', f'<p class="eyebrow">{eyebrow}</p>', f"<h1>{h1}</h1>", f'<p class="lead">{lead}</p>']
    if button:
        parts.append(f'<div class="hero-actions"><a class="btn" data-bot href="{BOT}">{TG}Напомнить в Telegram</a></div>')
    if status:
        parts.append('<p class="status-line" id="updated" role="status"><span class="live" aria-hidden="true"></span><span>Загружаю данные…</span></p>')
        parts.append('<div class="stale" id="stale" role="status" hidden></div>')
    parts.append("</section>")
    return "\n".join(parts)


NOSCRIPT = """<noscript><p class="muted">Цифры подгружаются скриптом. Включи JavaScript или открой бота в Telegram.</p></noscript>"""
SKELETON = '<div class="card"><span class="skeleton"></span></div>'

page("index.html",
     "Очередь на границе Беларуси сейчас: Брест, Брузги, Каменный лог, Бенякони",
     "Сколько машин в зоне ожидания на каждом пункте пропуска Беларуси с ЕС, сколько ждать вызова и сколько на самом деле ждали. Обновление каждые 5 минут.",
     hero("Граница Беларуси с ЕС", "Очередь на границе сейчас",
          "Сколько ждать вызова, если зарегистрироваться сейчас, и сколько на самом деле ждали те, кого вызвали за последние три часа. По всем шести пунктам пропуска.")
     + f"""
{NOSCRIPT}
<div class="grid" id="cards" aria-live="polite">{SKELETON}{SKELETON}{SKELETON}</div>
<h2>Как читать цифры</h2>
<p><strong>Ждать вызова, если встать сейчас</strong>: прогноз для машины, которая регистрируется прямо сейчас. Считается по тому, сколько машин в час вызывали за последние часы и дни, с поправкой для каждого пункта.</p>
<p><strong>Ждали за 3 часа</strong>: не прогноз, а факт. Сколько прошло от регистрации до вызова у машин, которых вызвали за последние три часа. Когда очередь быстро растёт или тает, эта цифра отстаёт от прогноза.</p>
<p>Насколько прогнозу можно верить, показано на странице <a href="accuracy.html">точности</a>: на коротких очередях он почти всегда попадает в пределах часа, на длинных ошибается на часы.</p>""",
     {"page": "index", "start": "site"}, "index.html")

for code, name, other, slug, start, loc in CHECKPOINTS:
    extra = ""
    if code == "Grigorovshchina":
        extra = '<p class="muted">Через Григоровщину обычно ездит мало машин, поэтому очередь здесь часто пустая, а прогноз считать не по чему.</p>'
    page(f"{slug}.html",
         f"Очередь в {loc} сейчас: сколько машин и сколько ждать | BorderQueue",
         f"Очередь на пункте пропуска {name} ({other}): машины в зоне ожидания сейчас, прогноз ожидания вызова, сколько ждали на самом деле и когда регистрироваться на выходные.",
         hero(f"Пункт пропуска · {other}", f"Очередь в {loc} сейчас",
              "Легковые машины в электронной очереди, прогноз ожидания вызова и сколько на самом деле ждали. Обновляется каждые 5 минут.")
         + f"""
{NOSCRIPT}
{extra}
<div id="cp" aria-live="polite">{SKELETON}</div>
<div class="watch">
  <div>
    <h3>Не хочется следить за очередью?</h3>
    <p>Бот напишет, когда очередь в {loc} дорастёт до нужного тебе числа машин. Один раз, без лишних сообщений.</p>
  </div>
  <a class="btn" data-bot href="{BOT}">{TG}Поставить дозор</a>
</div>
<div id="cp-weekend"></div>
<p class="small" style="margin-top:32px"><a class="link-arrow" href="index.html">← Все пункты пропуска</a></p>""",
         {"page": "checkpoint", "code": code, "start": start})

page("weekend.html",
     "Когда регистрироваться в очередь на границе на выходные | BorderQueue",
     "Сколько ждали вызова в пятницу вечером, в субботу и в воскресенье в зависимости от времени регистрации. По реально измеренным ожиданиям за последние три выходных.",
     hero("Выходные", "Когда регистрироваться на выходные",
          "Сколько ждали вызова те, кто регистрировался в субботу и воскресенье в разное время дня. Это измеренные ожидания, а не прогноз.", status=False)
     + """
<p class="muted small">Медиана за три последних прошедших выходных: <span id="weekends">…</span>. Мелко под цифрой разброс между ними. Три выходных это мало: когда граница меняет режим, как в августе, картина меняется вместе с ней.</p>
<div class="legend" aria-hidden="true"><span><i class="sw ok"></i>до часа</span><span><i class="sw warn"></i>1–4 часа</span><span><i class="sw bad"></i>больше 4 часов</span></div>
<noscript><p class="muted">Таблицы подгружаются скриптом. Включи JavaScript.</p></noscript>
<div id="weekend" aria-live="polite">""" + SKELETON + "</div>",
     {"page": "weekend", "start": "site_weekend"}, "weekend.html")

page("accuracy.html",
     "Насколько точен прогноз очереди на границе | BorderQueue",
     "Как часто прогноз ожидания вызова попадает в пределах часа на коротких и длинных очередях. Проверено по реальным машинам за последние две недели.",
     hero("Проверка", "Насколько точен прогноз",
          'Для каждой машины, вставшей в очередь за последние <span id="acc-days">14</span> дней, сравниваем прогноз, который бот показывал в момент её регистрации, с тем, сколько она ждала на самом деле. Проверено на <span id="acc-cars">…</span> машинах.',
          status=False, button=False)
     + """
<noscript><p class="muted">Цифры подгружаются скриптом. Включи JavaScript.</p></noscript>
<div class="card"><h3 style="margin-bottom:24px">Прогноз попал в пределах часа</h3><div class="bars" id="accuracy" aria-live="polite"><span class="skeleton"></span></div></div>
<h2>Что из этого следует</h2>
<p>На коротких очередях прогноз почти всегда точен. На длинных он ошибается на часы: очередь в несколько сотен машин успевает ускориться или встать, пока до тебя дойдёт.</p>
<p>Поэтому бот не предлагает будить звонком к точному времени, когда в очереди больше 400 машин: надёжно доставленное неверное время это не услуга.</p>
<p class="small muted">Машины, которые ещё стоят в очереди, в проверку не попадают: их ожидание пока неизвестно. Из-за этого самые долгие ожидания последних дней немного недоучтены.</p>""",
     {"page": "accuracy", "start": "site_accuracy"}, "accuracy.html")

# Справка: раньше жила на Telegraph, переехала сюда 06.10.2026. Текст лежит в content/guide.html,
# потому что это единственная страница сайта, где всё содержимое статично: её целиком видят
# поисковики, и именно её люди ищут («как зарегистрироваться в электронную очередь»).
page("guide.html",
     "Электронная очередь на границе Беларуси: как зарегистрироваться и сколько стоит | BorderQueue",
     "Как зарегистрироваться в электронную очередь на границе Беларуси онлайн, сколько стоит регистрация, сколько времени даётся после вызова и сколько машин вызывают в час.",
     hero("Справка", "Электронная очередь на границе: как это работает",
          "Сколько стоит регистрация, как пройти её онлайн, сколько времени даётся после вызова и сколько на самом деле ждут.",
          status=False, button=False)
     + (ROOT / "content" / "guide.html").read_text(encoding="utf-8"),
     {"page": "guide", "start": "site_guide"}, "guide.html")

urls = ["", "weekend.html", "accuracy.html", "guide.html"] + [f"{c[3]}.html" for c in CHECKPOINTS]
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE}/{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
(ROOT / ".nojekyll").write_text("", encoding="utf-8")
print("built", len(urls), "pages")
