# joenellstudio.com — Joenell Studio (parent brand)

Since 2026-11-25 Joenell Studio is the parent brand of Joenell's photography (owner decision). The booking platform for other photographers is removed (its code is in this branch's history, commit 15d5b1b).

- `site/` = the whole site. Since 2026-11-25 (later the same evening) the homepage is a MAGAZINE you flip through (page curl, assets/flipbook.js): cover → welcome → contents (tap to jump) → 01 Wedding photography (opener, Joenell Photography page with link, 8 photo pages, link page) → 02 Event photography (coming soon + email) → 03 More to come → back cover. Edit pages in `site/build.py` (PAGES list), run it → index.html. `_redirects` sends old platform URLs home. `joenellstudio-site-v4.zip` = the upload zip (no build.py/template) for Cloudflare Pages project "joenellstudio".
- To add a style later (e.g. events): replace its "coming soon" pages with an opener + photo pages + a link page, and fix the page numbers on the contents page.
- Wedding photography card → https://www.joenellphotography.ca/ (the wedding site). Event photography = "coming soon" card. Add new styles as new cards in index.html.
