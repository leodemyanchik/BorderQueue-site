// BorderQueue: данные берутся у сервиса бота. Он считает их в фоне и отдаёт из памяти,
// так что сайт можно обновлять сколько угодно. Страница сама определяет, что рисовать,
// по атрибутам <body data-page="..." data-code="...">.

const API = "https://borderqueueapi.onrender.com/api/public";
const BOT = "https://t.me/BorderTimerBot";

// Порядок по тому, сколько людей через пункт ездит, а не по алфавиту.
const ORDER = ["Brest", "Bruzgi", "KamennyLog", "Benyakoni", "Berestovitsa", "Grigorovshchina"];
const PAGES = {
  Brest: "brest.html", Bruzgi: "bruzgi.html", KamennyLog: "kamenny-log.html",
  Benyakoni: "benyakoni.html", Berestovitsa: "berestovitsa.html", Grigorovshchina: "grigorovshchina.html",
};
const STALE_MINUTES = 15;
const FAIL = `<p class="muted">Не удалось загрузить данные. Обнови страницу через минуту.</p>`;

const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function load(name, tries = 4) {
  for (let i = 0; i < tries; i++) {
    try {
      const r = await fetch(`${API}/${name}`, { cache: "no-cache" });
      if (r.ok) return await r.json();
      // 503 значит, что сервис только перезапустился и ещё считает. Подождать и спросить снова.
    } catch (e) { /* сеть: попробуем ещё раз */ }
    await new Promise((res) => setTimeout(res, 3000 * (i + 1)));
  }
  return null;
}

// ---------- форматирование ----------

function dur(min) {
  if (min == null) return "нет данных";
  min = Math.round(min);
  if (min <= 5) return "почти сразу";
  if (min < 60) return `${min} мин`;
  const h = Math.floor(min / 60), m = min % 60;
  if (h >= 10 || m === 0) return `${h} ч`;
  return `${h} ч ${String(m).padStart(2, "0")} мин`;
}

function short(min) {
  if (min == null) return "—";
  min = Math.round(min);
  if (min <= 5) return "0 мин";
  if (min < 60) return `${min} мин`;
  const h = min / 60;
  return h < 10 ? `${h.toFixed(1).replace(".", ",")} ч` : `${Math.round(h)} ч`;
}

// Разброс коротко, чтобы помещался в ячейку на телефоне: «1,9–7,6 ч», «10–53 мин», «0,7–3,7 ч».
function span(lo, hi) {
  const a = short(lo), b = short(hi);
  const unit = (s) => (s.endsWith(" ч") ? " ч" : s.endsWith(" мин") ? " мин" : "");
  if (unit(a) && unit(a) === unit(b)) return `${a.slice(0, -unit(a).length)}–${b}`;
  // Разные единицы: обе границы в часах, иначе строка не влезает в ячейку.
  const hrs = (m) => (Math.round(m) <= 5 ? "0" : (m / 60).toFixed(1).replace(".", ",").replace(",0", ""));
  return `${hrs(lo)}–${hrs(hi)} ч`;
}

function level(min) {
  if (min == null) return "none";
  if (min < 60) return "ok";
  if (min < 240) return "warn";
  return "bad";
}

function plural(n, one, few, many) {
  const a = Math.abs(n) % 100, b = a % 10;
  if (a > 10 && a < 20) return many;
  if (b > 1 && b < 5) return few;
  if (b === 1) return one;
  return many;
}

const cars = (n) => `${n.toLocaleString("ru-RU")} ${plural(n, "машина", "машины", "машин")}`;

function clock(unix) {
  return new Date(unix * 1000).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Minsk" });
}

function ago(unix) {
  const m = Math.max(0, Math.round((Date.now() / 1000 - unix) / 60));
  return m < 1 ? "только что" : `${m} мин назад`;
}

// Статус словами, а не только цветом: цвет на солнце и для части людей не различим.
function pill(cp) {
  if (cp.cars === 0) return `<span class="pill ok">без очереди</span>`;
  const l = level(cp.waitMinutes);
  const text = { ok: "до часа", warn: "1–4 часа", bad: "больше 4 часов", none: "без прогноза" }[l];
  return `<span class="pill ${l}">${text}</span>`;
}

const forecast = (cp) => (cp.cars === 0 ? "почти сразу" : dur(cp.waitMinutes));
const measured = (cp) => (cp.recentWaitMinutes == null ? "мало данных" : dur(cp.recentWaitMinutes));

// ---------- график за сутки ----------

function spark(series, big = false) {
  if (!series || series.length < 4) return "";
  const w = 300, h = big ? 120 : 44, pad = 3;
  const ys = series.map((p) => p.cars);
  const max = Math.max(...ys, 10);
  const x = (i) => pad + (i * (w - 2 * pad)) / (series.length - 1);
  const y = (v) => h - pad - (v * (h - 2 * pad)) / max;
  const line = series.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.cars).toFixed(1)}`).join("");
  const area = `${line}L${x(series.length - 1).toFixed(1)},${h - pad}L${x(0).toFixed(1)},${h - pad}Z`;
  const now = ys[ys.length - 1], peak = Math.max(...ys), low = Math.min(...ys);
  const label = `Очередь за сутки: от ${cars(low)} до ${cars(peak)}, сейчас ${cars(now)}.`;
  return `
    <svg class="spark${big ? " big-chart" : ""}" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" role="img" aria-label="${esc(label)}">
      <path d="${area}" fill="var(--chart-fill)"></path>
      <path d="${line}" fill="none" stroke="var(--chart)" stroke-width="1.75" vector-effect="non-scaling-stroke" stroke-linejoin="round"></path>
    </svg>
    <div class="spark-cap"><span>сутки назад</span><span>пик ${peak.toLocaleString("ru-RU")}</span><span>сейчас</span></div>`;
}

// ---------- карточка пункта ----------

// Главная цифра одна: сколько ждать, если встать сейчас. Ради неё человек и открыл страницу.
function card(cp) {
  const trucks = cp.trucks > 0 ? `<span>грузовых <b class="num">${cp.trucks}</b></span>` : "";
  return `
    <a class="card" href="${PAGES[cp.code]}">
      <div class="card-head"><h3>${esc(cp.name)}</h3>${pill(cp)}</div>
      <div class="big num">${forecast(cp)}</div>
      <div class="big-label">ждать вызова, если встать сейчас</div>
      <div class="facts">
        <span>в очереди <b class="num">${cp.cars.toLocaleString("ru-RU")}</b></span>
        <span>ждали за 3 часа <b class="num">${measured(cp)}</b></span>
        ${trucks}
      </div>
      ${spark(cp.series)}
    </a>`;
}

const sorted = (list) => [...list].sort((a, b) => ORDER.indexOf(a.code) - ORDER.indexOf(b.code));
const newest = (now) => Math.max(...now.checkpoints.map((c) => c.snapshotAt));

function staleCheck(now) {
  const box = $("#stale");
  if (!box || !now) return;
  const m = Math.round((Date.now() / 1000 - newest(now)) / 60);
  box.hidden = m <= STALE_MINUTES;
  if (m > STALE_MINUTES) {
    box.textContent = `Данные не обновлялись ${m} мин. Источник мог временно не отвечать, цифры ниже могут быть устаревшими.`;
  }
}

// Время последнего снимка. «Минут назад» пересчитывается каждые полминуты, а данные
// перечитываются раз в минуту, так что открытая страница не застывает на старых цифрах.
let lastSnapshot = null;

// Очередь одной фразой: «в очереди 334 машины, ждать вызова около 15 ч». Ровно так же её пишет
// tools/build.py, когда подставляет цифры в HTML для поисковиков: живой скрипт потом лишь
// обновляет ту же фразу, а не рисует другую.
function summary(cp) {
  if (cp.cars === 0) return "очереди нет, вызывают почти сразу";
  const wait = cp.waitMinutes == null ? "" : `, ждать вызова около ${dur(cp.waitMinutes)}`;
  return `в очереди ${cars(cp.cars)}${wait}`;
}

let lastCp = null;

function statusLine(now, cp) {
  if (now) lastSnapshot = newest(now);
  if (cp) lastCp = cp;
  const el = $("#updated");
  if (!el || lastSnapshot == null) return;
  const what = lastCp ? `: ${summary(lastCp)}.` : ".";
  el.innerHTML = `<span class="live" aria-hidden="true"></span><span>Обновлено в ${clock(lastSnapshot)} по Минску, ${ago(lastSnapshot)}${what} Источник опрашивается раз в 5 минут.</span>`;
}

// Короткие строки у ссылок на пункты на главной: «334 машины, около 15 ч».
function snaps(now) {
  document.querySelectorAll("[data-snap]").forEach((el) => {
    const cp = now.checkpoints.find((c) => c.code === el.dataset.snap);
    if (!cp) return;
    el.textContent = cp.cars === 0 ? "без очереди"
      : cp.waitMinutes == null ? cars(cp.cars) : `${cars(cp.cars)}, около ${dur(cp.waitMinutes)}`;
  });
}

function live(refresh) {
  setInterval(refresh, 60_000);
  setInterval(() => statusLine(null), 30_000);
  // Вкладка, вернувшаяся из фона, сразу показывает свежее, а не ждёт следующей минуты.
  document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(); });
}

// ---------- страницы ----------

async function pageIndex() {
  const render = async (first) => {
    const now = await load("now", first ? 4 : 1);
    const box = $("#cards");
    // При фоновом обновлении неудача оставляет прежние цифры, а не стирает их.
    if (!now) { if (first) box.innerHTML = FAIL; return; }
    box.innerHTML = sorted(now.checkpoints).map(card).join("");
    statusLine(now); staleCheck(now); snaps(now);
  };
  await render(true);
  live(() => render(false));
}

function weekendTable(cpw, windows) {
  const cell = (c) => {
    if (!c || c.medianMinutes == null) return `<td><span class="m">—</span><span class="r">мало машин</span></td>`;
    const vals = c.perWeekend.filter((v) => v != null);
    const lo = Math.min(...vals), hi = Math.max(...vals);
    const range = vals.length > 1 && short(lo) !== short(hi) ? span(lo, hi) : "";
    return `<td class="${level(c.medianMinutes)}"><span class="m num">${short(c.medianMinutes)}</span><span class="r num">${range}</span></td>`;
  };
  return `
    <div class="table-scroll">
      <table class="wk">
        <thead><tr><th scope="col"><span class="visually-hidden">День</span></th>${windows.map((w) => `<th scope="col">${esc(w.replace("до 9:00", "0–9"))}</th>`).join("")}</tr></thead>
        <tbody>
          <tr><th scope="row">Сб</th>${cpw.saturday.map(cell).join("")}</tr>
          <tr><th scope="row">Вс</th>${cpw.sunday.map(cell).join("")}</tr>
        </tbody>
      </table>
    </div>
    <p class="note">Пятница после 17:00: <b class="num">${cpw.friday.medianMinutes == null ? "мало данных" : dur(cpw.friday.medianMinutes)}</b></p>`;
}

async function pageWeekend() {
  const wk = await load("weekend");
  const box = $("#weekend");
  if (!wk) { box.innerHTML = FAIL; return; }
  $("#weekends").textContent = wk.weekends.join(", ");
  box.innerHTML = sorted(wk.checkpoints)
    .filter((c) => c.code !== "Grigorovshchina")
    .map((c) => `<section class="card wk-card"><h3><a href="${PAGES[c.code]}">${esc(c.name)}</a></h3>${weekendTable(c, wk.windows)}</section>`)
    .join("");
}

async function pageAccuracy() {
  const acc = await load("accuracy");
  const box = $("#accuracy");
  if (!acc) { box.innerHTML = FAIL; return; }
  $("#acc-cars").textContent = acc.cars.toLocaleString("ru-RU");
  $("#acc-days").textContent = acc.days;
  box.innerHTML = acc.bands.map((b) => {
    const pct = b.hitShare == null ? null : Math.round(b.hitShare * 100);
    return `
      <div>
        <div class="bar-top"><span>Очередь ${esc(b.label)}</span><strong class="num">${pct == null ? "—" : pct + "%"}</strong></div>
        <div class="bar" role="img" aria-label="${pct == null ? "мало данных" : `${pct} процентов прогнозов в пределах часа`}"><i style="width:${pct ?? 0}%"></i></div>
        <div class="bar-sub">${cars(b.cars)}, обычная ошибка ${dur(b.medianErrorMinutes).replace("почти сразу", "меньше 5 мин")}</div>
      </div>`;
  }).join("");
}

async function pageCheckpoint(code) {
  const [now, wk] = await Promise.all([load("now"), load("weekend")]);
  if (!renderCheckpoint(code, now)) { $("#cp").innerHTML = FAIL; return; }
  live(async () => { const fresh = await load("now", 1); if (fresh) renderCheckpoint(code, fresh); });
  renderWeekend(code, wk);
}

function renderCheckpoint(code, now) {
  const cp = now?.checkpoints.find((c) => c.code === code);
  const box = $("#cp");
  if (!cp) return false;
  const trucks = cp.trucks > 0 ? `<p class="note">Грузовых в очереди: <b class="num">${cp.trucks}</b></p>` : "";
  // Автобусы только в Бресте: на остальных пунктах их в зоне ожидания почти не бывает.
  const buses = code === "Brest" && cp.buses != null
    ? `<p class="note">Автобусов в зоне ожидания: <b class="num">${cp.buses}</b>. Дольше всего автобусы обычно стоят на самом переходе, а этого электронная очередь не видит.</p>`
    : "";
  box.innerHTML = `
    <div class="card">
      <div class="card-head"><h3>Сейчас</h3>${pill(cp)}</div>
      <div class="detail" style="margin-top:16px">
        <div><div class="big num">${forecast(cp)}</div><div class="big-label">ждать вызова, если встать сейчас</div></div>
        <div><div class="big num">${cp.cars.toLocaleString("ru-RU")}</div><div class="big-label">${plural(cp.cars, "машина", "машины", "машин")} в очереди</div></div>
        <div><div class="big num">${measured(cp)}</div><div class="big-label">ждали вызванные за последние 3 часа</div></div>
      </div>
      ${spark(cp.series, true)}
      ${trucks}
      ${buses}
    </div>`;
  statusLine(now, cp); staleCheck(now);
  return true;
}

function renderWeekend(code, wk) {
  const cpw = wk?.checkpoints.find((c) => c.code === code);
  const wbox = $("#cp-weekend");
  if (wbox && cpw && code !== "Grigorovshchina") {
    wbox.innerHTML = `<h2>Когда регистрироваться на выходные</h2>
      <p class="muted">Сколько ждали вызова те, кто регистрировался в это время. Медиана за три последних выходных (${esc(wk.weekends.join(", "))}), мелко разброс между ними.</p>
      <div class="card">${weekendTable(cpw, wk.windows)}</div>`;
  }
}

async function totals() {
  const el = $("#totals");
  if (!el) return;
  const t = await load("totals", 2);
  if (!t) return;
  const since = new Date(t.since * 1000).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" });
  el.textContent = `Ожидание измерено у ${t.measuredCars.toLocaleString("ru-RU")} легковых машин с ${since}: от регистрации до вызова, как было на самом деле.`;
}

// Ссылки на бота с меткой страницы, чтобы бот видел, сколько людей пришло с сайта.
function botLinks() {
  const tag = document.body.dataset.start || "site";
  document.querySelectorAll("a[data-bot]").forEach((a) => { a.href = `${BOT}?start=${tag}`; });
}

botLinks();
const page = document.body.dataset.page;
if (page === "index") pageIndex();
if (page === "weekend") pageWeekend();
if (page === "accuracy") pageAccuracy();
if (page === "checkpoint") pageCheckpoint(document.body.dataset.code);
totals();
