/* static/assets/js/app.js
 * Minimal reliable state + ticket storage for ATU Queue (client)
 */
console.log("LOADED STATIC APP.JS v2");


const STORAGE_KEY = "atuq_state_v1";
const LAST_TICKET_KEY = "atuq_last_ticket";
const TICKETS_KEY = "atuq_tickets_v1"; // список всех заявок/талонов

window.APP = window.APP || {};
APP.state = APP.state || {
  lang: "kz",
  verified: false,
  fio: "",
  phone: "",
  category: "",
  service: "",
  ticket: null
};

// ----------------------
// basic helpers
// ----------------------
function safeParseJSON(raw, fallback = null) {
  try { return JSON.parse(raw); } catch (e) { return fallback; }
}

function go(url) {
  window.location.href = url;
}

// ----------------------
// State persistence
// ----------------------
APP.load = function () {
  const raw = localStorage.getItem(STORAGE_KEY);
  const obj = safeParseJSON(raw, null);
  if (obj && typeof obj === "object") {
    APP.state = { ...APP.state, ...obj };
  }
  return APP.state;
};

APP.save = function () {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(APP.state));
};

APP.clear = function () {
  // don't wipe sequences (ticket counters), only user state + last ticket
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(LAST_TICKET_KEY);
  APP.state = {
    lang: "kz",
    verified: false,
    fio: "",
    phone: "",
    category: "",
    service: "",
    ticket: null
  };
};

// ----------------------
// Ticket ID generator (A-xxx / C-xxx / G-xxx / O-xxx)
// ----------------------
function makeTicketId(prefix) {
  const p = (prefix || "T").toUpperCase();
  const seqKey = "atuq_seq_" + p; // separate sequences per type
  const last = Number(localStorage.getItem(seqKey) || "100");
  const next = last + 1;
  localStorage.setItem(seqKey, String(next));
  return `${p}-${next}`;
}

// ----------------------
// Tickets list storage (FIXED: null-safe)
// ----------------------
function getTickets() {
  const v = safeParseJSON(localStorage.getItem(TICKETS_KEY), []);
  return Array.isArray(v) ? v : [];
}

function setTickets(arr) {
  localStorage.setItem(TICKETS_KEY, JSON.stringify(Array.isArray(arr) ? arr : []));
}

function updateTicketInList(ticketObj) {
  if (!ticketObj?.number) return;
  const arr = getTickets(); // всегда массив
  const i = arr.findIndex(t => t.number === ticketObj.number);
  if (i >= 0) arr[i] = ticketObj;
  else arr.push(ticketObj);
  setTickets(arr);
}

// ----------------------
// Ticket storage (last + list + state)
// ----------------------
function saveTicket(ticketObj) {
  if (!ticketObj || typeof ticketObj !== "object") return;

  // 1) state
  APP.state.ticket = ticketObj;
  APP.save();

  // 2) explicit last ticket
  localStorage.setItem(LAST_TICKET_KEY, JSON.stringify(ticketObj));

  // 3) list
  updateTicketInList(ticketObj);
}

function getLastTicket() {
  // prefer state ticket
  APP.load();
  if (APP.state && APP.state.ticket) return APP.state.ticket;

  // fallback
  const raw = localStorage.getItem(LAST_TICKET_KEY);
  return safeParseJSON(raw, null);
}

// ----------------------
// Config loader (flags + desks + secretaries, etc.)
// ----------------------
async function loadConfig() {
  // base from static (desks routing)
  let base = null;
  try {
    const r = await fetch("/static/config/config.json?ts=" + Date.now());
    if (r.ok) base = await r.json();
  } catch (e) {}

  // admin overrides from DB
  let db = null;
  try {
    const r2 = await fetch("/api/config/?ts=" + Date.now(), { cache: "no-store" });
    if (r2.ok) db = await r2.json();
  } catch (e) {}

  // merge
  const merged = base || {
    flags: {},
    desks: {
      design: [1, 2],
      foreign: [11, 12],
      master: [15],
      army: [5],
      default: [3,4,6,7,8,9,10,13,14,16,17,18,19,20,21,22,23,24,25]
    }
  };

  // если в БД есть flags — перезаписываем
  if (db?.flags) merged.flags = { ...(merged.flags || {}), ...db.flags };

  // ui не нужен тут (его берёт i18n.js), но можно оставить:
  if (db?.ui) merged.ui = db.ui;

  return merged;
}



// ----------------------
// Desk routing helpers
// ----------------------
function pickFrom(list) {
  if (!Array.isArray(list) || list.length === 0) return null;
  return list[Math.floor(Math.random() * list.length)];
}

// Consultation routing (C-...)
function pickDeskForConsultation(category, direction, cfg) {
  const d = cfg?.desks || {};

  if (direction === "design") return pickFrom(d.design);
  if (category === "foreign") return pickFrom(d.foreign);
  if (category === "master") return pickFrom(d.master);
  if (category === "army") return pickFrom(d.army);

  return pickFrom(d.default);
}

// Admission routing (A-...)
function pickDeskForAdmission(payType, category, profile, cfg) {
  const d = cfg?.desks || {};

  if (profile === "creative") return pickFrom(d.design);
  if (category === "foreign") return pickFrom(d.foreign);
  if (category === "master") return pickFrom(d.master);
  if (category === "army") return pickFrom(d.army);

  return pickFrom(d.default);
}

// ----------------------
// API: create ticket in Django (DRF)
// ----------------------
async function apiCreateTicket(ticket) {
  const res = await fetch("/api/tickets/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ticket),
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || "API error");
  }
  return await res.json();
}

// ----------------------
// Expose globally (used in pages)
// ----------------------
window.go = window.go || go;
window.makeTicketId = window.makeTicketId || makeTicketId;
window.saveTicket = window.saveTicket || saveTicket;
window.getLastTicket = window.getLastTicket || getLastTicket;
window.getTickets = window.getTickets || getTickets;
window.updateTicketInList = window.updateTicketInList || updateTicketInList;
window.loadConfig = window.loadConfig || loadConfig;

window.pickDeskForConsultation = window.pickDeskForConsultation || pickDeskForConsultation;
window.pickDeskForAdmission = window.pickDeskForAdmission || pickDeskForAdmission;

window.apiCreateTicket = window.apiCreateTicket || apiCreateTicket;

// Load on start
APP.load();
