# joenellstudio.com — site source (Phase 1, built 2026-11-14)

- Edit text/prices/photographers in `build.py`, then run `python3 build.py` → writes `site/`.
- `site/` is what goes to Cloudflare Pages (includes `_worker.js`). `joenellstudio-site-v2.zip` = zipped `site/` for a direct upload.
- Photos: `images/` (resized from the owner's full Lightroom exports in Joenell Photography/portfolio-album/images; never screenshots). `-s.jpg` = 640px, plain = 1400px.
- Backend (`_worker.js`): /api/request, /api/apply store entries in R2 binding `UPLOADS`; /admin (password = env `ADMIN_PASSWORD`).
  Optional email alerts: env `RESEND_API_KEY`, `ALERT_TO`, `ALERT_FROM`.
- Flipbook: `assets/flipbook.js` + `flipbook.css` (page-curl engine from the Joenell Photography portfolio album). Chapters per photographer in `build.py` → `album`.
