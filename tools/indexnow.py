"""Сообщает Яндексу через IndexNow, что страницы сайта обновились.

Яндекс Вебмастер с 12.10.2026 не открывается, а сайта в индексе Яндекса всё ещё нет. IndexNow
работает без Вебмастера: достаточно положить ключ файлом в корень сайта и отправить список
адресов. Запуск:

    python tools/indexnow.py

Адреса уходят на два адреса приёма. Общий api.indexnow.org сам раздаёт их всем поисковикам протокола,
Яндексу тоже. Прямой адрес Яндекса нужен на случай, если раздача до него не дойдёт; 13.10.2026 он
обрывал соединение на любой запрос, тогда как общий принимал.

Адреса берутся из sitemap.xml, его пишет tools/build.py. Запускает GitHub Actions после выкладки
(.github/workflows/pages.yml): при каждом пуше и раз в сутки, но не каждые 30 минут, чтобы не
частить с одними и теми же адресами.
"""
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = "https://borderqueue.app"
ROOT = Path(__file__).resolve().parent.parent
# Ключ не секрет: протокол требует, чтобы он лежал открытым файлом на сайте.
KEY = "bq7f3a9c1e5d2b8046a1c9e7f2d4b6a0"
ENDPOINTS = ["https://api.indexnow.org/indexnow", "https://yandex.com/indexnow"]

if (ROOT / f"{KEY}.txt").read_text(encoding="utf-8").strip() != KEY:
    sys.exit(f"{KEY}.txt в корне сайта не совпадает с KEY")

ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = [loc.text for loc in ET.parse(ROOT / "sitemap.xml").getroot().iterfind("s:url/s:loc", ns)]
body = json.dumps({"host": SITE.removeprefix("https://"), "key": KEY,
                   "keyLocation": f"{SITE}/{KEY}.txt", "urlList": urls}).encode()

broken = []
for endpoint in ENDPOINTS:
    req = urllib.request.Request(endpoint, data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            # 200: принято; 202: принято, ключ ещё проверяется (так бывает в первый раз).
            print("indexnow:", endpoint, r.status, len(urls), "urls")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        # 429 и ответы 5xx проходят сами, их не стоит превращать в красную сборку. Остальные 4xx
        # значат, что что-то не так у нас: ключ, его файл или адреса.
        if e.code == 429 or e.code >= 500:
            print(f"::warning::indexnow: {endpoint} {e.code} {detail}")
        else:
            print(f"::error::indexnow: {endpoint} {e.code} {detail}")
            broken.append(endpoint)
    except OSError as e:  # обрыв соединения, таймаут, DNS: сбой на той стороне
        print(f"::warning::indexnow: {endpoint} {type(e).__name__}: {e}")

if broken:
    sys.exit(1)
