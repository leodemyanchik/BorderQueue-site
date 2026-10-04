"""Собирает HTML-страницы сайта из одного шаблона.

Страницы статические: текст, заголовки и описания лежат прямо в HTML, чтобы их видели
поисковики, а цифры подставляет assets/app.js из открытых данных бота. Запуск:

    python tools/build.py

Адрес сайта меняется в SITE: сейчас это GitHub Pages, после покупки домена borderqueue.app.
"""
from pathlib import Path

SITE = "https://leodemyanchik.github.io/BorderQueue-site"
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

LOGO = """<svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#1e293b"/><path d="M8 22h16M8 16h11M8 10h6" stroke="#22c55e" stroke-width="3" stroke-linecap="round"/></svg>"""
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='8' fill='%231e293b'/%3E%3Cpath d='M8 22h16M8 16h11M8 10h6' "
           "stroke='%2322c55e' stroke-width='3' stroke-linecap='round'/%3E%3C/svg%3E")

NAV = [("index.html", "Сейчас", ""), ("weekend.html", "Выходные", ""), ("accuracy.html", "Точность", "hide-sm")]


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
<meta name="theme-color" content="#1e293b">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700&amp;display=swap&amp;subset=cyrillic" rel="stylesheet">
<link rel="preconnect" href="https://borderqueueapi.onrender.com" crossorigin>
<link rel="stylesheet" href="assets/style.css">
<script src="assets/app.js" defer></script>
</head>
<body {attrs}>
<header class="top">
  <div class="wrap">
    <a class="brand" href="index.html">{LOGO}<span>BorderQueue</span></a>
    <nav class="nav" aria-label="Разделы">{nav}<a data-bot href="https://t.me/BorderTimerBot">Бот</a></nav>
  </div>
</header>
<main class="wrap">
{body}
<section class="cta" aria-label="Телеграм-бот">
  <p><strong>Бот подскажет, когда регистрироваться</strong>Скажи, к какому времени хочешь быть на границе, и бот напишет, когда пора вставать в очередь. А если сообщение можно проспать, позвонит на телефон. Первый звонок бесплатно.</p>
  <a class="btn" data-bot href="https://t.me/BorderTimerBot">Открыть бота в Telegram</a>
</section>
</main>
<footer>
  <div class="wrap">
    <p id="totals">Ожидание измерено по сотням тысяч машин: от регистрации до вызова, как было на самом деле.</p>
    <p>Данные электронной очереди на границе Беларуси, обновление каждые 5 минут. Это не официальный сайт пунктов пропуска: зарегистрироваться можно только через официальный сервис.</p>
    <div class="links">{cp_links} <a href="weekend.html">Выходные</a> <a href="accuracy.html">Точность прогноза</a> <a data-bot href="https://t.me/BorderTimerBot">Телеграм-бот</a></div>
  </div>
</footer>
</body>
</html>
"""
    (ROOT / file).write_text(html, encoding="utf-8")


STATUS = """<p class="status-line" id="updated">Загружаю данные…</p>
<div class="stale" id="stale" role="status" hidden></div>"""

NOSCRIPT = """<noscript><p class="muted">Цифры подгружаются скриптом. Включи JavaScript или открой бота в Telegram.</p></noscript>"""

page("index.html",
     "Очередь на границе Беларуси сейчас: Брест, Брузги, Каменный лог, Бенякони",
     "Сколько машин в зоне ожидания на каждом пункте пропуска Беларуси с ЕС, сколько ждать вызова и сколько на самом деле ждали. Обновление каждые 5 минут.",
     f"""<h1>Очередь на границе Беларуси сейчас</h1>
<p class="lead">Сколько машин стоит в электронной очереди на каждом пункте пропуска с ЕС, сколько ждать вызова, если зарегистрироваться сейчас, и сколько на самом деле ждали те, кого вызвали за последние три часа.</p>
{STATUS}
{NOSCRIPT}
<div class="grid" id="cards" aria-live="polite">
  <div class="card"><span class="skeleton">Загрузка</span></div>
  <div class="card"><span class="skeleton">Загрузка</span></div>
</div>
<h2>Как читать цифры</h2>
<p><strong>Ждать, если встать сейчас</strong>: прогноз, через сколько вызовут машину, которая регистрируется прямо сейчас. Он считается по тому, сколько машин в час вызывали за последние часы и дни, с поправкой для каждого пункта.</p>
<p><strong>Ждали вызванные за 3 часа</strong>: не прогноз, а факт. Сколько прошло от регистрации до вызова у машин, которых вызвали за последние три часа. Если очередь быстро растёт или тает, эта цифра отстаёт от прогноза.</p>
<p>Насколько прогнозу можно верить, показано на странице <a href="accuracy.html">точности</a>: на коротких очередях он почти всегда попадает в пределах часа, на длинных ошибается на часы.</p>""",
     {"page": "index", "start": "site"}, "index.html")

for code, name, other, slug, start, loc in CHECKPOINTS:
    extra = ""
    if code == "Grigorovshchina":
        extra = "<p>Через Григоровщину обычно ездит мало машин, поэтому очередь здесь часто пустая, а прогноз считать не по чему.</p>"
    page(f"{slug}.html",
         f"Очередь в {loc} сейчас: сколько машин и сколько ждать | BorderQueue",
         f"Очередь на пункте пропуска {name} ({other}): машины в зоне ожидания сейчас, прогноз ожидания вызова, сколько ждали на самом деле и когда регистрироваться на выходные.",
         f"""<h1>Очередь в {loc} сейчас</h1>
<p class="lead">Пункт пропуска {name}, на той стороне {other}. Легковые машины в электронной очереди, прогноз ожидания вызова и сколько на самом деле ждали.</p>
{STATUS}
{NOSCRIPT}
{extra}
<div id="cp" aria-live="polite"><div class="card"><span class="skeleton">Загрузка</span></div></div>
<div id="cp-weekend"></div>
<p class="small muted"><a href="index.html">Все пункты пропуска</a></p>""",
         {"page": "checkpoint", "code": code, "start": start})

page("weekend.html",
     "Когда регистрироваться в очередь на границе на выходные | BorderQueue",
     "Сколько ждали вызова в пятницу вечером, в субботу и в воскресенье в зависимости от времени регистрации. По реально измеренным ожиданиям за последние три выходных.",
     """<h1>Когда регистрироваться на выходные</h1>
<p class="lead">Сколько ждали вызова те, кто регистрировался в субботу и воскресенье в разное время дня. Это измеренные ожидания, а не прогноз: от регистрации до вызова, по каждой машине.</p>
<p class="muted small">Медиана за три последних прошедших выходных: <span id="weekends">…</span>. Под цифрой разброс между этими выходными. Три выходных это мало: когда граница меняет режим, как в августе, картина меняется вместе с ней.</p>
<div class="legend" aria-hidden="true"><span><i class="sw ok"></i>до часа</span><span><i class="sw warn"></i>1–4 часа</span><span><i class="sw bad"></i>больше 4 часов</span></div>
<noscript><p class="muted">Таблицы подгружаются скриптом. Включи JavaScript.</p></noscript>
<div id="weekend" aria-live="polite"><div class="card"><span class="skeleton">Загрузка</span></div></div>""",
     {"page": "weekend", "start": "site_weekend"}, "weekend.html")

page("accuracy.html",
     "Насколько точен прогноз очереди на границе | BorderQueue",
     "Как часто прогноз ожидания вызова попадает в пределах часа на коротких и длинных очередях. Проверено по реальным машинам за последние две недели.",
     """<h1>Насколько точен прогноз</h1>
<p class="lead">Каждой машине, которая встала в очередь за последние <span id="acc-days">14</span> дней, сравниваем прогноз, который бот показывал в момент её регистрации, с тем, сколько она ждала на самом деле. Проверено на <span id="acc-cars">…</span> машинах.</p>
<h2>Прогноз попал в пределах часа</h2>
<noscript><p class="muted">Цифры подгружаются скриптом. Включи JavaScript.</p></noscript>
<div class="card"><div class="bars" id="accuracy" aria-live="polite"><span class="skeleton">Загрузка</span></div></div>
<h2>Что из этого следует</h2>
<p>На коротких очередях прогноз почти всегда точен. На длинных он ошибается на часы: очередь в несколько сотен машин успевает ускориться или встать, пока до тебя дойдёт.</p>
<p>Поэтому бот не предлагает будить звонком к точному времени, когда в очереди больше 400 машин: надёжно доставленное неверное время это не услуга.</p>
<p class="small muted">Машины, которые ещё стоят в очереди, в проверку не попадают: их ожидание пока неизвестно. Из-за этого самые долгие ожидания последних дней немного недоучтены.</p>""",
     {"page": "accuracy", "start": "site_accuracy"}, "accuracy.html")

urls = ["", "weekend.html", "accuracy.html"] + [f"{c[3]}.html" for c in CHECKPOINTS]
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE}/{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
(ROOT / ".nojekyll").write_text("", encoding="utf-8")
print("built", len(urls), "pages")
