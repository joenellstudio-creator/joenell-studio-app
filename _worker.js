// Joenell Studio — backend (Cloudflare Pages "advanced mode" worker).
// Phase 1:
//   POST /api/request  couple booking request  -> stored in R2 (binding UPLOADS) under requests/
//   POST /api/apply    photographer application -> stored in R2 under applications/
//   GET  /admin        private list of requests + applications (HTTP Basic: any username, password = ADMIN_PASSWORD)
//   GET  /admin/item?key=...  one entry in full
// Optional email alert per submission via Resend: set RESEND_API_KEY, ALERT_TO (where alerts go) and ALERT_FROM (a verified sender).
// Everything else is served from the static site (env.ASSETS).

const MAX_BODY = 20000;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const PACKAGES = { "city-hall": "City Hall / Elopement", "adventure": "Adventure Elopement", "micro-wedding": "Micro-Wedding" };

const FORMS = {
  request: {
    prefix: "requests/", title: "New booking request",
    required: ["package", "date", "location", "name", "email", "consent"],
    fields: ["package", "date", "photographer", "location", "guests", "start_time", "addons", "name", "partner", "email", "phone", "notes", "heard", "page"],
    check: (d) => {
      if (!PACKAGES[d.package]) return "Please choose a package.";
      if (!/^\d{4}-\d{2}-\d{2}$/.test(d.date)) return "Please choose your wedding date.";
      return null;
    },
    summary: (d) => `${d.name}${d.partner ? " & " + d.partner : ""} · ${PACKAGES[d.package] || d.package} · ${d.date}`,
  },
  apply: {
    prefix: "applications/", title: "New photographer application",
    required: ["name", "business", "email", "phone", "city", "years", "full_gallery", "weddings_lead", "insurance", "consent"],
    fields: ["name", "business", "email", "phone", "site", "instagram", "city", "years", "full_gallery", "portfolio", "weddings_lead", "insurance", "interest", "notes", "page"],
    check: () => null,
    summary: (d) => `${d.name} · ${d.business} · ${d.city}`,
  },
};

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const clean = (v) => (Array.isArray(v) ? v.map(clean).join(", ") : String(v ?? "").trim().slice(0, 3000));

async function handleForm(kind, request, env) {
  const form = FORMS[kind];
  const len = Number(request.headers.get("content-length") || 0);
  if (len > MAX_BODY) return json({ ok: false, error: "That's too much text. Please shorten your message." }, 413);
  let raw;
  try { raw = await request.json(); } catch { return json({ ok: false, error: "Please try again." }, 400); }
  if (raw && raw.website) return json({ ok: true }); // honeypot: bots fill the hidden field
  const d = {};
  for (const k of form.fields) d[k] = clean(raw[k]);
  d.consent = clean(raw.consent);
  for (const k of form.required) if (!d[k]) return json({ ok: false, error: "Please fill in all the required fields." }, 400);
  if (!EMAIL_RE.test(d.email)) return json({ ok: false, error: "Please check your email address." }, 400);
  const bad = form.check(d);
  if (bad) return json({ ok: false, error: bad }, 400);

  if (!env.UPLOADS) return json({ ok: false, error: "Our form is being set up." }, 503);
  const now = new Date();
  const id = now.toISOString().replace(/[:.]/g, "-") + "-" + crypto.randomUUID().slice(0, 8);
  const record = { id, kind, received_at: now.toISOString(), country: request.cf?.country || "", ...d };
  await env.UPLOADS.put(form.prefix + id + ".json", JSON.stringify(record, null, 2), {
    httpMetadata: { contentType: "application/json" },
    customMetadata: { summary: form.summary(d).slice(0, 250), email: d.email },
  });
  await alertEmail(env, form, record).catch(() => {});
  return json({ ok: true, id });
}

async function alertEmail(env, form, r) {
  if (!env.RESEND_API_KEY || !env.ALERT_TO || !env.ALERT_FROM) return;
  const rows = form.fields.concat("received_at").filter((k) => r[k]).map((k) => `<tr><td style="padding:4px 12px 4px 0;color:#777">${esc(k)}</td><td>${esc(r[k])}</td></tr>`).join("");
  await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({
      from: env.ALERT_FROM, to: env.ALERT_TO.split(",").map((s) => s.trim()), reply_to: r.email,
      subject: `${form.title}: ${form.summary(r)}`,
      html: `<h2 style="font-family:Georgia,serif">${esc(form.title)}</h2><table>${rows}</table><p>All entries: https://joenellstudio.com/admin</p>`,
    }),
  });
}

// ---------- admin ----------
function authorized(request, env) {
  if (!env.ADMIN_PASSWORD) return false;
  const h = request.headers.get("authorization") || "";
  if (!h.startsWith("Basic ")) return false;
  try { const [, pass] = atob(h.slice(6)).split(/:(.*)/s); return pass === env.ADMIN_PASSWORD; } catch { return false; }
}
const unauth = () => new Response("Sign in required", { status: 401, headers: { "www-authenticate": 'Basic realm="Joenell Studio admin"', "cache-control": "no-store" } });
const adminPage = (title, body) => new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>${esc(title)}</title>
<style>body{font-family:system-ui,sans-serif;margin:0;padding:24px;background:#fbf8f3;color:#24221f}h1{font-family:Georgia,serif;font-weight:400}h2{font-family:Georgia,serif;font-weight:400;margin-top:36px}
table{border-collapse:collapse;width:100%;background:#fff;border:1px solid #e6ded2}td,th{padding:10px 12px;border-bottom:1px solid #eee;text-align:left;vertical-align:top;font-size:15px}th{background:#f4eee5;font-weight:500}
a{color:#3e4a40}pre{white-space:pre-wrap;background:#fff;border:1px solid #e6ded2;padding:16px;border-radius:8px}.muted{color:#777}</style>${body}`,
  { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex" } });

async function listPrefix(env, prefix) {
  const out = []; let cursor;
  do {
    const r = await env.UPLOADS.list({ prefix, cursor, include: ["customMetadata"] });
    out.push(...r.objects); cursor = r.truncated ? r.cursor : undefined;
  } while (cursor && out.length < 1000);
  return out.sort((a, b) => (a.key < b.key ? 1 : -1));
}

async function admin(request, env, url) {
  if (!authorized(request, env)) return unauth();
  if (!env.UPLOADS) return adminPage("Admin", "<h1>Storage not connected</h1><p>Add the R2 binding UPLOADS to this Pages project.</p>");
  if (url.pathname === "/admin/item") {
    const key = url.searchParams.get("key") || "";
    if (!/^(requests|applications)\/[\w-]+\.json$/.test(key)) return adminPage("Not found", "<p>Not found</p>");
    const obj = await env.UPLOADS.get(key);
    if (!obj) return adminPage("Not found", "<p>Not found</p>");
    const data = await obj.json();
    const rows = Object.entries(data).map(([k, v]) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`).join("");
    return adminPage(key, `<p><a href="/admin">← All entries</a></p><h1>${esc(data.kind === "apply" ? "Photographer application" : "Booking request")}</h1><table>${rows}</table>`);
  }
  const section = async (prefix, title) => {
    const items = await listPrefix(env, prefix);
    if (!items.length) return `<h2>${title}</h2><p class="muted">None yet.</p>`;
    const rows = items.map((o) => `<tr><td>${esc(o.uploaded.toISOString().slice(0, 16).replace("T", " "))} UTC</td><td><a href="/admin/item?key=${encodeURIComponent(o.key)}">${esc(o.customMetadata?.summary || o.key)}</a></td><td>${esc(o.customMetadata?.email || "")}</td></tr>`).join("");
    return `<h2>${title} (${items.length})</h2><table><tr><th>Received</th><th>Summary</th><th>Email</th></tr>${rows}</table>`;
  };
  return adminPage("Joenell Studio admin", `<h1>Joenell Studio · admin</h1>${await section("requests/", "Booking requests")}${await section("applications/", "Photographer applications")}`);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www.joenellstudio.com") { url.hostname = "joenellstudio.com"; return Response.redirect(url.toString(), 301); }
    if (url.pathname === "/api/request" || url.pathname === "/api/apply") {
      if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405);
      return handleForm(url.pathname === "/api/request" ? "request" : "apply", request, env);
    }
    if (url.pathname === "/admin" || url.pathname.startsWith("/admin/")) return admin(request, env, url);
    return env.ASSETS.fetch(request);
  },
};
