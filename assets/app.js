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
  if (m < 1) return "только что";
  return `${m} мин назад`;
}

function badge(cp) {
  if (cp.cars === 0) return `<span class="badge ok">без очереди</span>`;
  const l = level(cp.waitMinutes);
  const text = { ok: "до часа", warn: "1–4 часа", bad: "больше 4 часов", none: "без прогноза" }[l];
  return `<span class="badge ${l}">${text}</span>`;
}

// ---------- график за сутки ----------

function spark(series, big = false) {
  if (!series || series.length < 4) return "";
  const w = 300, h = big ? 140 : 56, pad = 4;
  const ys = series.map((p) => p.cars);
  const max = Math.max(...ys, 10), min = 0;
  const x = (i) => pad + (i * (w - 2 * pad)) / (series.length - 1);
  const y = (v) => h - pad - ((v - min) * (h - 2 * pad)) / (max - min || 1);
  const line = series.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.cars).toFixed(1)}`).join("");
  const area = `${line}L${x(series.length - 1).toFixed(1)},${h - pad}L${x(0).toFixed(1)},${h - pad}Z`;
  const now = ys[ys.length - 1], peak = Math.max(...ys), low = Math.min(...ys);
  const label = `Очередь за сутки: от ${cars(low)} до ${cars(peak)}, сейчас ${cars(now)}.`;
  return `
    <svg class="spark${big ? " big" : ""}" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" role="img" aria-label="${esc(label)}">
      <path d="${area}" fill="var(--chart-fill)"></path>
      <path d="${line}" fill="none" stroke="var(--chart)" stroke-width="2" vector-effect="non-scaling-stroke" stroke-linejoin="round"></path>
    </svg>
    <div class="spark-cap"><span>сутки назад</span><span>пик ${peak.toLocaleString("ru-RU")}</span><span>сейчас</span></div>`;
}

// ---------- карточка пункта ----------

function figures(cp, wide = false) {
  const forecast = cp.cars === 0 ? "почти сразу" : dur(cp.waitMinutes);
  const recent = cp.recentWaitMinutes == null ? "мало данных" : dur(cp.recentWaitMinutes);
  return `
    <div class="figures">
      <div class="fig${wide ? " wide" : ""}"><div class="v num">${cp.cars.toLocaleString("ru-RU")}</div><div class="l">${plural(cp.cars, "машина", "машины", "машин")} в очереди</div></div>
      <div class="fig"><div class="v num">${forecast}</div><div class="l">ждать, если встать сейчас</div></div>
      <div class="fig"><div class="v num">${recent}</div><div class="l">ждали вызванные за 3 часа</div></div>
    </div>`;
}

function card(cp) {
  const trucks = cp.trucks > 0 ? `<div class="truck">Грузовых в очереди: <span class="num">${cp.trucks}</span></div>` : "";
  return `
    <a class="card" href="${PAGES[cp.code]}">
      <div class="card-head"><h3>${esc(cp.name)}</h3>${badge(cp)}</div>
      ${figures(cp)}
      ${spark(cp.series)}
      ${trucks}
    </a>`;
}

function sorted(list) {
  return [...list].sort((a, b) => ORDER.indexOf(a.code) - ORDER.indexOf(b.code));
}

function staleCheck(now) {
  const box = $("#stale");
  if (!box || !now) return;
  const newest = Math.max(...now.checkpoints.map((c) => c.snapshotAt));
  const m = Math.round((Date.now() / 1000 - newest) / 60);
  if (m > STALE_MINUTES) {
    box.hidden = false;
    box.textContent = `Данные не обновлялись ${m} мин. Источник мог временно не отвечать, цифры ниже могут быть устаревшими.`;
  }
}

function statusLine(now) {
  const el = $("#updated");
  if (!el || !now) return;
  const newest = Math.max(...now.checkpoints.map((c) => c.snapshotAt));
  el.innerHTML = `<span class="dot" aria-hidden="true"></span>Обновлено в ${clock(newest)} по Минску, ${ago(newest)}. Данные каждые 5 минут.`;
}

// ---------- страницы ----------

async function pageIndex() {
  const now = await load("now");
  const box = $("#cards");
  if (!now) { box.innerHTML = `<p class="muted">Не удалось загрузить данные. Обнови страницу через минуту.</p>`; return; }
  box.innerHTML = sorted(now.checkpoints).map(card).join("");
  statusLine(now); staleCheck(now);
}

function weekendTable(cpw, windows) {
  const cell = (c) => {
    if (!c || c.medianMinutes == null) return `<td><span class="m">—</span><span class="r">мало машин</span></td>`;
    const vals = c.perWeekend.filter((v) => v != null);
    const lo = Math.min(...vals), hi = Math.max(...vals);
    const range = vals.length > 1 && short(lo) !== short(hi) ? `от ${short(lo)} до ${short(hi)}` : "";
    return `<td class="${level(c.medianMinutes)}"><span class="m num">${short(c.medianMinutes)}</span><span class="r">${range}</span></td>`;
  };
  return `
    <div class="table-scroll">
      <table class="wk">
        <thead><tr><th scope="col">Регистрация</th>${windows.map((w) => `<th scope="col">${esc(w)}</th>`).join("")}</tr></thead>
        <tbody>
          <tr><th scope="row">Суббота</th>${cpw.saturday.map(cell).join("")}</tr>
          <tr><th scope="row">Воскресенье</th>${cpw.sunday.map(cell).join("")}</tr>
        </tbody>
      </table>
    </div>
    <p class="small muted">Пятница вечером, после 17:00: <strong class="num">${cpw.friday.medianMinutes == null ? "мало данных" : dur(cpw.friday.medianMinutes)}</strong>.</p>`;
}

async function pageWeekend() {
  const wk = await load("weekend");
  const box = $("#weekend");
  if (!wk) { box.innerHTML = `<p class="muted">Не удалось загрузить данные. Обнови страницу через минуту.</p>`; return; }
  $("#weekends").textContent = wk.weekends.join(", ");
  box.innerHTML = [...wk.checkpoints]
    .sort((a, b) => ORDER.indexOf(a.code) - ORDER.indexOf(b.code))
    .filter((c) => c.code !== "Grigorovshchina")
    .map((c) => `<section class="card" style="margin-bottom:12px"><div class="card-head"><h3><a href="${PAGES[c.code]}">${esc(c.name)}</a></h3></div>${weekendTable(c, wk.windows)}</section>`)
    .join("");
}

async function pageAccuracy() {
  const acc = await load("accuracy");
  const box = $("#accuracy");
  if (!acc) { box.innerHTML = `<p class="muted">Не удалось загрузить данные. Обнови страницу через минуту.</p>`; return; }
  $("#acc-cars").textContent = acc.cars.toLocaleString("ru-RU");
  $("#acc-days").textContent = acc.days;
  box.innerHTML = acc.bands.map((b) => {
    const pct = b.hitShare == null ? null : Math.round(b.hitShare * 100);
    return `
      <div class="bar-row">
        <div class="top-line"><span>Очередь ${esc(b.label)}</span><strong class="num">${pct == null ? "мало данных" : pct + "%"}</strong></div>
        <div class="bar" role="img" aria-label="${pct == null ? "мало данных" : `${pct} процентов прогнозов в пределах часа`}"><i style="width:${pct ?? 0}%"></i></div>
        <div class="small muted">${cars(b.cars)}, обычная ошибка ${dur(b.medianErrorMinutes).replace("почти сразу", "меньше 5 мин")}</div>
      </div>`;
  }).join("");
}

async function pageCheckpoint(code) {
  const [now, wk] = await Promise.all([load("now"), load("weekend")]);
  const cp = now?.checkpoints.find((c) => c.code === code);
  const box = $("#cp");
  if (!cp) { box.innerHTML = `<p class="muted">Не удалось загрузить данные. Обнови страницу через минуту.</p>`; return; }
  const trucks = cp.trucks > 0 ? `<p class="truck">Грузовых в очереди: <span class="num">${cp.trucks}</span></p>` : "";
  box.innerHTML = `
    <div class="card">
      <div class="card-head"><h2 style="margin:0;font-size:19px">Сейчас</h2>${badge(cp)}</div>
      ${figures(cp, true)}
      ${spark(cp.series, true)}
      ${trucks}
    </div>`;
  statusLine(now); staleCheck(now);
  const cpw = wk?.checkpoints.find((c) => c.code === code);
  const wbox = $("#cp-weekend");
  if (wbox && cpw && code !== "Grigorovshchina") {
    wbox.innerHTML = `<h2>Выходные: когда регистрироваться</h2>
      <p class="lead">Сколько ждали вызова те, кто регистрировался в это время. Медиана за три последних выходных (${esc(wk.weekends.join(", "))}), ниже разброс между ними.</p>
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
