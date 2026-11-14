#!/usr/bin/env python3
"""Joenell Studio site builder. Edit the data/text here, run `python3 build.py`, upload the `site/` folder (plus _worker.js) to Cloudflare Pages.
Pages: home, packages, photographers, photographer profile (flipbook), request a booking, join (photographers), how it works + FAQ, terms, privacy, 404.
"""
import json, os, html, datetime, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")
DOMAIN = "https://joenellstudio.com"
EMAIL = "hello@joenellstudio.com"  # public contact address (set up forwarding in Cloudflare Email Routing)
VER = "20261114a"  # bump to bust caches after CSS/JS changes
SIZES = json.load(open(os.path.join(ROOT, "image-sizes.json")))

# ---------------------------------------------------------------- data
PACKAGES = [
    dict(id="city-hall", name="City Hall / Elopement", short="Short coverage · one location", img="cl-wedding-vows",
         items=["Around 1–2 hours of coverage", "One location", "City hall, a park or a small ceremony", "Online gallery to download and share"],
         blurb="For city hall vows, a short ceremony or a simple elopement with the two of you."),
    dict(id="adventure", name="Adventure Elopement", short="Half day · more than one location", img="jh-lookout",
         items=["Around 3+ hours of coverage", "More than one location (think Stanley Park, Sea-to-Sky)", "Help planning locations and timing", "Online gallery to download and share"],
         blurb="Vows somewhere that feels like you, with time to explore the coast or the mountains."),
    dict(id="micro-wedding", name="Micro-Wedding", short="Ceremony to reception · smaller guest list", img="cl-wedding-dance",
         items=["From the ceremony to the first dance", "Smaller weddings, around 50 guests or fewer", "Longer coverage options", "Online gallery to download and share"],
         blurb="A small wedding with the people who matter most, from the ceremony to the first dance."),
]
PKG = {p["id"]: p for p in PACKAGES}

# Each photographer lists their OWN packages and prices (owner, Nov 14). Each package is tagged with the
# platform category it fits (city-hall / adventure / micro-wedding / other); "from" prices = lowest in each category.
PHOTOGRAPHERS = [
    dict(slug="joenell-photography", name="Joenell Photography", person="Joenell", area="Vancouver, BC",
         site="https://www.joenellphotography.ca/", tags=["Natural & candid", "Warm, bright colour", "Surprise proposals"],
         # = the live joenellphotography.ca/pricing page (single source of truth, reconciled Nov 6 2026)
         packages=[
            dict(cat="city-hall", name="Intimate Elopement", price=850, detail="90 minutes · 50+ edited photos"),
            dict(cat="adventure", name="Adventure Elopement", price=1250, detail="3 hours · 2 locations · 100+ edited photos"),
            dict(cat="micro-wedding", name="The Vow", price=1000, detail="2 hours · ceremony + portraits · 75+ edited photos"),
            dict(cat="micro-wedding", name="The Story", price=1450, detail="4 hours · 160+ edited photos"),
            dict(cat="micro-wedding", name="The Complete Story", price=1950, detail="6 hours · 250+ edited photos"),
            dict(cat="other", name="Engagement session", price=225, detail="60 minutes · 30+ edited photos"),
            dict(cat="other", name="Surprise proposal", price=250, detail="45 minutes · 20+ edited photos"),
         ],
         extras=["Rush editing +$150", "Travel beyond Metro Vancouver quoted per trip"],
         deposit_note="20% non-refundable deposit holds your date. Balance due 2 weeks before weddings and elopements, 1 week before engagements and proposals. Photo counts are minimums.",
         cover=["cl-wedding-path", "jh-lookout", "st-03"],
         bio=["Joenell Photography is a Vancouver wedding and couples photographer, and the first photographer on Joenell Studio. "
              "The style is natural and warm: gentle direction, real moments and bright, true-to-life colour.",
              "From city hall vows to a garden wedding in autumn and a surprise proposal at Bowen Lookout, the aim is the same: "
              "photos that feel like the day felt. Coverage across Metro Vancouver and the Sea-to-Sky, and elsewhere in BC by request."],
         album=[
            ("Getting ready & ceremony", "The quiet minutes before, then the vows.",
             [("full", "cl-wedding-veil", "Getting ready"), ("full", "cl-wedding-bride", ""), ("mat", "cl-wedding-walk", "The walk down the aisle"),
              ("full", "cl-wedding-vows", "The vows"), ("mat", "cl-wedding-rings", "Rings on")]),
            ("Portraits", "A few unhurried minutes for the two of you.",
             [("mat", "cl-wedding-cover", ""), ("full", "cl-wedding-kiss", ""), ("mat", "cl-wedding-path", "Through the garden"),
              ("duo", ("cl-wedding-dip", "cl-wedding-bench"), "Between ceremony and dinner"), ("full", "cl-wedding-portrait", "Autumn light")]),
            ("Reception & details", "Cake, toasts, the first dance and the little things.",
             [("mat", "cl-wedding-cake", "Mr & Mrs"), ("mat", "cl-wedding-dance", "The first dance"), ("full", "cl-engagement-hands", "Hand in hand"),
              ("mat", "st-bench", "A quiet moment"), ("mat", "st-cover", "Among the tulips")]),
            ("Engagements", "By the water, in the gardens and under the willows.",
             [("full", "st-03", ""), ("mat", "cl-engagement-silhouette", "Golden hour"), ("full", "je-1", ""), ("mat", "st-10", "In full bloom"),
              ("mat", "je-cover", "Together"), ("full", "st-07", "Shoes in hand"), ("mat", "cl-engagement-embrace", "Last light")]),
            ("Surprise proposals", "Hidden nearby until the question is asked.",
             [("mat", "jh-cover", "The question"), ("full", "jh-kiss", "Yes"), ("full", "jh-gaze", ""), ("mat", "jh-engaged", "Just engaged"),
              ("mat", "jh-lookout", "Bowen Lookout")]),
         ]),
]

for _ph in PHOTOGRAPHERS:
    _ph["prices"] = {}
    for _k in ("city-hall", "adventure", "micro-wedding"):
        _v = [x["price"] for x in _ph["packages"] if x["cat"] == _k]
        if _v: _ph["prices"][_k] = min(_v)
def from_price(pid): return min(p["prices"][pid] for p in PHOTOGRAPHERS if pid in p["prices"])

# ---------------------------------------------------------------- helpers
e = html.escape
def money(n): return f"${n:,}"
def img(name, alt, eager=False, sizes="(max-width:700px) 100vw, 50vw"):
    w, h = SIZES[name]
    return (f'<img src="/images/{name}-s.jpg" srcset="/images/{name}-s.jpg 640w, /images/{name}.jpg {max(w, h)}w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{e(alt)}" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async">')

NAV = [("/photographers", "Find a photographer"), ("/packages", "Packages"), ("/how-it-works", "How it works"), ("/join", "For photographers")]

def page(path, title, desc, body, active=None, extra_head="", og_img="jh-lookout", schema=None):
    url = DOMAIN + ("/" if path == "/index" else path)
    nav = "".join(f'<a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in NAV)
    sch = f'<script type="application/ld+json">{json.dumps(schema)}</script>\n' if schema else ""
    return f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Joenell Studio">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{DOMAIN}/images/{og_img}.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#fbf8f3">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;1,6..96,400&family=Jost:wght@300;400;500&family=Pinyon+Script&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={VER}">
{extra_head}{sch}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
  <a class="logo" href="/" aria-label="Joenell Studio home"><b>JOENELL</b><span>Studio · Vancouver</span></a>
  <nav class="main" id="nav">{nav}<a class="btn" href="/book">Request a booking</a></nav>
  <button class="menu-btn" aria-controls="nav" aria-expanded="false" aria-label="Menu">☰</button>
</div></header>
<main id="main">
{body}
</main>
<footer class="site"><div class="wrap">
  <div class="cols">
    <div><a class="logo" href="/"><b>JOENELL</b><span>Studio · Vancouver</span></a>
      <p style="margin-top:16px;max-width:300px">Vetted Vancouver wedding and elopement photographers at honest, fixed prices.</p></div>
    <div><h4>Couples</h4><a href="/photographers">Find a photographer</a><a href="/packages">Packages</a><a href="/how-it-works">How it works</a><a href="/book">Request a booking</a></div>
    <div><h4>Photographers</h4><a href="/join">Join Joenell Studio</a><a href="/join#apply">Apply</a><a href="/how-it-works#faq">FAQ</a></div>
    <div><h4>Contact</h4><a href="mailto:{EMAIL}">{EMAIL}</a><a href="/terms">Terms</a><a href="/privacy">Privacy</a></div>
  </div>
  <div class="base"><span>© <span data-year>2026</span> Joenell Studio · Vancouver, British Columbia</span><span>Photos belong to the photographers who made them.</span></div>
</div></footer>
<script src="/assets/site.js?v={VER}" defer></script>
</body>
</html>
"""

def write(path, content):
    fp = os.path.join(OUT, path.lstrip("/") + ".html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w").write(content)

def pkg_cards():
    out = []
    for p in PACKAGES:
        lis = "".join(f"<li>{e(i)}</li>" for i in p["items"])
        out.append(f"""<article class="pkg reveal">{img(p['img'], p['name'] + ' photography in Vancouver', sizes='(max-width:900px) 100vw, 33vw')}
<div class="body"><p class="eyebrow">{e(p['short'])}</p><h3>{e(p['name'])}</h3><p class="muted">{e(p['blurb'])}</p>
<div class="price"><small>from</small> {money(from_price(p['id']))} <small>CAD</small></div><ul>{lis}</ul>
<a class="btn" href="/book?package={p['id']}">Choose this package</a></div></article>""")
    return f'<div class="pkgs">{"".join(out)}</div>'

def addon_chips():
    return '<div class="addons"><span>Extras like more hours, a second shooter or an engagement session are listed on each photographer\'s profile</span></div>'

def photographer_card(ph):
    c = ph["cover"]
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in ph["tags"])
    return f"""<a class="pcard reveal" href="/photographers/{ph['slug']}">
<div class="imgs">{img(c[0], ph['name'] + ' wedding photo', sizes='(max-width:620px) 66vw, 22vw')}{img(c[1], ph['name'] + ' proposal photo', sizes='15vw')}{img(c[2], ph['name'] + ' engagement photo', sizes='15vw')}</div>
<div class="body"><h3>{e(ph['name'])}</h3><p class="muted small" style="margin:0">{e(ph['area'])} · <span class="tag gold">First on Joenell</span></p>
<div class="tags">{tags}</div><p class="from" style="margin:0">Packages from <b>{money(min(ph['prices'].values()))}</b> CAD</p></div></a>"""

TRUST = """<div class="trust">
<div><i>✓</i><span><b>Vetted by hand</b>Every photographer shows a full wedding gallery and meets us first.</span></div>
<div><i>↺</i><span><b>Protected deposit</b>If your photographer can't fulfil your booking, you get your full deposit back or choose another photographer.</span></div>
<div><i>§</i><span><b>One clear agreement</b>The same contract for every booking, with delivery time and photo rights in plain words.</span></div>
<div><i>$</i><span><b>Clear prices</b>Every photographer lists their prices up front. No booking fee for couples.</span></div>
</div>"""

FAQ_COUPLES = [
    ("What does “vetted” mean?", "Before anyone joins, Joenell reviews one complete wedding or elopement gallery from them in private, looks through their portfolio, checks they carry liability insurance and meets them. Only photographers who can cover a whole day well are accepted."),
    ("How do prices work?", "Each photographer lists their own packages and prices on their profile, so you see the price before you ask. Search by type (city hall, adventure elopement or micro-wedding) to compare “from” prices."),
    ("Do couples pay a booking fee?", "No. You pay the photographer's package price and nothing on top."),
    ("How do I book?", "Send a booking request with your date and package. The photographer replies within 48 hours. Once they accept, you get the agreement to sign online and a secure link to pay your deposit. Your date is held as soon as the deposit is paid."),
    ("How do deposits work?", "Each photographer sets a deposit of at least 20% of the package price. The deposit holds your date and is non-refundable if you cancel. The balance is due before the wedding, as shown in your agreement."),
    ("What if my photographer can't make it?", "If your photographer can't fulfil your booking, they refund your full deposit. You can also choose another photographer on Joenell Studio for your date."),
    ("Where do your photographers work?", "Metro Vancouver and the Sea-to-Sky corridor, including Whistler. Other places in BC can be arranged with your photographer."),
    ("Who owns the photos?", "Your agreement covers this in plain words: you get your edited photos to keep, print and share, and the photographer keeps the copyright."),
]

def faq_html(items):
    return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items) + "</div>"

def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

# ---------------------------------------------------------------- pages
def home():
    pk_opts = "".join(f'<option value="{p["id"]}">{e(p["name"])}</option>' for p in PACKAGES)
    body = f"""
<section class="hero"><div class="wrap hero-grid">
  <div>
    <p class="eyebrow">Vancouver weddings &amp; elopements</p>
    <h1>Vetted photographers at <em>honest, fixed</em> prices.</h1>
    <p class="lead">Pick a package and your date. We match you with a hand-picked photographer who is free that day, so you can stop searching and start planning.</p>
    <form class="search" action="/book" method="get">
      <label><span>Your date</span><input type="date" name="date" aria-label="Wedding date"></label>
      <label><span>Package</span><select name="package" aria-label="Package">{pk_opts}</select></label>
      <button class="btn" type="submit">Find my photographer</button>
    </form>
    <p class="small muted" style="margin-top:14px">No booking fee for couples · Replies within 48 hours</p>
  </div>
  <div class="collage" aria-hidden="true">
    <figure class="a">{img('st-03', '', eager=True, sizes='25vw')}</figure>
    <figure class="b">{img('jh-lookout', '', eager=True, sizes='25vw')}</figure>
    <figure class="c">{img('cl-wedding-path', '', sizes='25vw')}</figure>
    <figure class="d">{img('je-cover', '', sizes='25vw')}</figure>
  </div>
</div></section>

<div class="wrap">{TRUST}</div>

<section><div class="wrap center">
  <p class="eyebrow">How it works</p><h2>Booked in three simple steps</h2>
  <div class="steps" style="text-align:left">
    <div class="step reveal"><h3>Choose a package and date</h3><p class="muted">City hall, an adventure elopement or a micro-wedding. Every package has a clear price.</p></div>
    <div class="step reveal"><h3>Meet your photographer</h3><p class="muted">See who is free on your date and flip through their work, chapter by chapter, like a real album.</p></div>
    <div class="step reveal"><h3>Sign and hold your date</h3><p class="muted">One standard agreement and a secure deposit, and your photographer is booked.</p></div>
  </div>
</div></section>

<section style="background:var(--bg-2)"><div class="wrap center">
  <p class="eyebrow">Packages</p><h2>Three packages, no guesswork</h2>
  <p class="lead">Each photographer lists their own packages and prices. You always see them up front.</p>
  {pkg_cards()}
  {addon_chips()}
</div></section>

<section><div class="wrap">
  <p class="eyebrow">Photographers</p><h2>Meet the first photographer on Joenell</h2>
  <p class="lead">More vetted Vancouver photographers are joining this winter. Each one goes live as soon as they're approved.</p>
  <div class="pcards">{photographer_card(PHOTOGRAPHERS[0])}
    <div class="pcard empty reveal"><div><h3>New on Joenell</h3><p>Newly approved photographers appear here first, so great new talent never gets buried.</p></div></div>
    <a class="pcard empty reveal" href="/join"><div><h3>Are you a photographer?</h3><p>Join free and pay only when you're booked.</p><span class="btn ghost" style="margin-top:8px">Apply to join</span></div></a>
  </div>
</div></section>

<section class="tight"><div class="wrap"><div class="band">
  <div><p class="eyebrow">For photographers</p><h2>Get booked without paying to be seen</h2>
  <p>Ads and directory listings cost money before a single booking comes in. On Joenell Studio you join free and pay a 15% commission only when a couple books you.</p>
  <a class="btn" href="/join">Apply to join</a></div>
  <ul><li>Free to join, no monthly fees</li><li>You set your own prices</li><li>A flipbook portfolio that shows your work like a real album</li><li>Blog and Instagram features to help couples find you</li></ul>
</div></div></section>

<section><div class="wrap center">
  <p class="eyebrow">Questions</p><h2>Good to know</h2>
  {faq_html(FAQ_COUPLES[:5])}
  <p style="margin-top:28px"><a href="/how-it-works#faq">More questions and answers →</a></p>
</div></section>
"""
    schema = {"@context": "https://schema.org", "@type": "Organization", "name": "Joenell Studio", "url": DOMAIN,
              "email": EMAIL, "areaServed": "Vancouver, British Columbia",
              "description": "Booking platform for vetted Vancouver wedding and elopement photographers at fixed prices."}
    write("/index", page("/index", "Joenell Studio · Vetted Vancouver wedding & elopement photographers",
                         "Book a vetted Vancouver wedding or elopement photographer at an honest, fixed price. Pick a package and date, meet who's free, and hold your date.",
                         body, schema=schema))

def packages():
    body = f"""
<section class="phead"><div class="wrap center"><p class="eyebrow">Packages</p><h1>Clear packages, honest prices</h1>
<p class="lead">Three ways to celebrate. Every photographer lists their own packages and prices, and the price you see is the price you pay. There's no booking fee for couples.</p></div></section>
<section style="padding-top:0"><div class="wrap center">{pkg_cards()}
{addon_chips()}
</div></section>
<section style="background:var(--bg-2)"><div class="wrap"><div class="two">
<div><p class="eyebrow">Included with every booking</p><h2>Peace of mind, built in</h2>
<ul style="padding-left:20px"><li>A photographer vetted by hand, with liability insurance</li><li>One standard agreement that spells out delivery time and photo rights</li><li>Your full deposit back if your photographer can't fulfil the booking, or another photographer of your choice</li><li>A secure card deposit to hold your date</li><li>An online gallery of your edited photos</li></ul></div>
<div><div class="sticky-book"><h3>Not sure which package?</h3><p class="muted">Tell us your date, your plans and roughly how many guests. We'll suggest the right package and photographer.</p><a class="btn" href="/book">Request a booking</a></div></div>
</div></div></section>"""
    write("/packages", page("/packages", "Wedding & elopement photography packages · Joenell Studio",
                            "City hall, adventure elopement and micro-wedding photography packages in Vancouver, with clear prices set by each vetted photographer.",
                            body, active="/packages", og_img="cl-wedding-vows"))

def photographers():
    cards = "".join(photographer_card(p) for p in PHOTOGRAPHERS)
    body = f"""
<section class="phead"><div class="wrap"><p class="eyebrow">Find a photographer</p><h1>Vancouver photographers you can trust</h1>
<p class="lead">Every photographer here is vetted by hand. Photographers with better reviews show first, and new ones get their own row so they're easy to find.</p></div></section>
<section style="padding-top:12px"><div class="wrap">
<div class="pcards">{cards}
<div class="pcard empty reveal"><div><h3>New on Joenell</h3><p>More vetted photographers are joining this winter. They'll appear here as soon as they're approved.</p></div></div>
<a class="pcard empty reveal" href="/book"><div><h3>Not sure who to pick?</h3><p>Send your date and package, and we'll match you with a photographer who's free.</p><span class="btn ghost" style="margin-top:8px">Get matched</span></div></a>
</div></div></section>"""
    write("/photographers", page("/photographers", "Find a vetted Vancouver wedding photographer · Joenell Studio",
                                 "Browse vetted Vancouver wedding and elopement photographers, see their flipbook portfolios and fixed package prices, and request a booking.",
                                 body, active="/photographers"))

def album_data(ph):
    mark = ph["name"].upper().replace(" PHOTOGRAPHY", "")
    pages = [dict(t="cover", img=ph["cover"][0], our="The portfolio", title="Love stories", mark=mark, meta="Photography · Vancouver"),
             dict(t="txt", html=f'<p class="eb">{e(ph["name"])} · Joenell Studio</p><h2>A wedding day, told in chapters.</h2><div class="rule"></div>'
                                '<p>Photos are grouped by the moments of the day, from different weddings and sessions, so you can judge every part of it.</p>'
                                '<p class="how">Drag a bottom corner to turn the page</p>')]
    chapters = []
    for i, (label, desc, items) in enumerate(ph["album"], 1):
        chapters.append(dict(label=label, at=len(pages)))
        pages.append(dict(t="chap", eb=f"Chapter {i}", names=label.split(" &")[0], kind=desc, d=""))
        for kind, im, cap in items:
            pages.append(dict(t="duo", imgs=list(im), cap=cap) if kind == "duo" else dict(t=kind, img=im, cap=cap))
    pages.append(dict(t="txt", html=f'<p class="eb">Your day</p><h2>Like what you see?</h2><div class="rule"></div><p>Send a booking request with your date and package. {e(ph["person"])} replies within 48 hours.</p><a class="cta" href="/book?photographer={ph["slug"]}">Request a booking</a>'))
    if len(pages) % 2 == 0: pages.append(dict(t="txt", html='<p class="eb">Joenell Studio</p><h2>Vetted photographers, honest prices.</h2><div class="rule"></div><p>joenellstudio.com</p>'))
    pages.append(dict(t="backc", title="Thank you", meta="joenellstudio.com"))
    used = {p.get("img") for p in pages} | {x for p in pages for x in p.get("imgs", [])}
    imgs = {n: {"w": SIZES[n][0], "h": SIZES[n][1], "src": f"/images/{n}.jpg"} for n in used if n}
    return dict(el="album", chapBar=".chapters", imgs=imgs, pages=pages, chapters=chapters)

def profile(ph):
    data = album_data(ph)
    rows = "".join(f'<tr><td>{e(x["name"])}<small>{e(x["detail"])}</small></td><td>{money(x["price"])}</td></tr>' for x in ph["packages"])
    rows += "".join(f'<tr><td>{e(x)}<small>Extra</small></td><td></td></tr>' for x in ph.get("extras", []))
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in ph["tags"])
    bio = "".join(f"<p>{e(p)}</p>" for p in ph["bio"])
    body = f"""
<div class="wrap"><div class="profile-head">
  <img class="avatar" src="/images/{ph['cover'][2]}-s.jpg" alt="" width="110" height="110">
  <div><p class="eyebrow" style="margin-bottom:6px">{e(ph['area'])}</p><h1>{e(ph['name'])}</h1>
  <div class="badges"><span class="tag gold">First on Joenell</span><span class="tag">Vetted</span>{tags}</div></div>
  <a class="btn" href="/book?photographer={ph['slug']}">Request a booking</a>
</div></div>
<section style="padding-top:20px"><div class="wrap">
  <div class="album" id="album" aria-label="{e(ph['name'])} portfolio flipbook">
    <div class="chapters" role="group" aria-label="Jump to a chapter"></div>
    <div class="stage"><div class="book"></div></div>
    <div class="ctrl"><button class="prev" aria-label="Previous page">&#8249;</button><span class="count">Cover</span><button class="next" aria-label="Next page">&#8250;</button></div>
    <p class="hint"><b>Drag a bottom corner</b> to turn the page, or jump to a chapter</p>
  </div>
</div></section>
<section style="padding-top:20px"><div class="wrap"><div class="two">
  <div><p class="eyebrow">About</p><h2>Hello from {e(ph['person'])}</h2>{bio}
    <p class="small muted">Website: <a href="{ph['site']}" rel="noopener" target="_blank">{e(ph['site'].replace('https://www.', '').rstrip('/'))}</a></p>
    <h2 style="margin-top:44px">Packages &amp; prices</h2><table class="ptable">{rows}</table>
    <p class="small muted" style="margin-top:12px">Prices in CAD, set by {e(ph['person'])}. {e(ph['deposit_note'])}</p></div>
  <div><div class="sticky-book"><h3>Check {e(ph['person'])}'s availability</h3><p class="muted">Send your date and package. You'll hear back within 48 hours.</p>
    <a class="btn" href="/book?photographer={ph['slug']}" style="width:100%">Request a booking</a>
    <p class="note" style="margin-top:18px">Backed by Joenell Studio: one standard agreement, a secure deposit, and your full deposit back if the photographer can't fulfil the booking.</p></div></div>
</div></div></section>"""
    head = (f'<link rel="stylesheet" href="/assets/flipbook.css?v={VER}">\n'
            f'<script>window.ALBUM={json.dumps(data, separators=(",", ":"))};</script>\n'
            f'<script src="/assets/flipbook.js?v={VER}" defer></script>\n')
    schema = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": ph["name"], "url": DOMAIN + "/photographers/" + ph["slug"],
              "sameAs": [ph["site"]], "address": {"@type": "PostalAddress", "addressLocality": "Vancouver", "addressRegion": "BC", "addressCountry": "CA"},
              "priceRange": f"{money(min(ph['prices'].values()))}–{money(max(ph['prices'].values()))} CAD"}
    write(f"/photographers/{ph['slug']}", page(f"/photographers/{ph['slug']}", f"{ph['name']} · Vancouver wedding & elopement photographer · Joenell Studio",
          f"{ph['name']} on Joenell Studio: a vetted Vancouver wedding and elopement photographer. Flip through the portfolio by chapter and see fixed package prices.",
          body, active="/photographers", extra_head=head, og_img=ph["cover"][0], schema=schema))

def book():
    radios = "".join(f'<label><input type="radio" name="package" value="{p["id"]}" required><b>{e(p["name"])}</b><span>{e(p["short"])} · from {money(from_price(p["id"]))}</span></label>' for p in PACKAGES)
    phs = "".join(f'<option value="{p["slug"]}">{e(p["name"])}</option>' for p in PHOTOGRAPHERS)
    body = f"""
<section class="phead"><div class="wrap center"><p class="eyebrow">Request a booking</p><h1>Tell us about your day</h1>
<p class="lead">It takes about two minutes. Your photographer replies within 48 hours, and nothing is charged until you've seen and signed the agreement.</p></div></section>
<section style="padding-top:8px"><div class="wrap"><div class="formcard">
<form data-endpoint="/api/request" data-done="book-done" data-prefill novalidate>
  <fieldset><legend>Your package</legend><div class="pkgpick">{radios}</div></fieldset>
  <fieldset><legend>Date and place</legend><div class="grid2">
    <div class="field"><label for="b-date">Wedding date</label><input id="b-date" type="date" name="date" required></div>
    <div class="field"><label for="b-ph">Photographer</label><select id="b-ph" name="photographer"><option value="match">Match me with someone free</option>{phs}</select></div>
    <div class="field full"><label for="b-loc">Where <span class="opt">(venue, city hall, a park… or “not sure yet”)</span></label><input id="b-loc" name="location" required maxlength="200"></div>
    <div class="field"><label for="b-guests">Guests <span class="opt">(roughly)</span></label><input id="b-guests" name="guests" inputmode="numeric" maxlength="20"></div>
    <div class="field"><label for="b-start">Start time <span class="opt">(if you know it)</span></label><input id="b-start" name="start_time" maxlength="40"></div>
  </div></fieldset>
  <fieldset><legend>About you</legend><div class="grid2">
    <div class="field"><label for="b-n1">Your name</label><input id="b-n1" name="name" required maxlength="100" autocomplete="name"></div>
    <div class="field"><label for="b-n2">Partner's name <span class="opt">(optional)</span></label><input id="b-n2" name="partner" maxlength="100"></div>
    <div class="field"><label for="b-em">Email</label><input id="b-em" type="email" name="email" required maxlength="200" autocomplete="email"></div>
    <div class="field"><label for="b-tel">Phone <span class="opt">(optional, for a quick text)</span></label><input id="b-tel" type="tel" name="phone" maxlength="40" autocomplete="tel"></div>
    <div class="field full"><label for="b-notes">Anything else? <span class="opt">(your plans, style, questions)</span></label><textarea id="b-notes" name="notes" maxlength="3000"></textarea></div>
    <div class="field full"><label for="b-how">How did you hear about us? <span class="opt">(optional)</span></label><input id="b-how" name="heard" maxlength="200"></div>
  </div></fieldset>
  <div class="hp" aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
  <label class="choice"><input type="checkbox" name="consent" value="yes" required> I agree that Joenell Studio may share these details with the photographer to arrange my booking (<a href="/privacy">privacy</a>).</label>
  <button class="btn" type="submit" style="margin-top:20px;width:100%">Send booking request</button>
  <div class="msg" role="alert"></div>
</form>
<div class="done" id="book-done" role="status"><div class="tick">✓</div><h2>Request sent</h2><p class="lead" style="margin:0 auto">Thank you! Your photographer will reply by email within 48 hours. Check your spam folder just in case.</p><p style="margin-top:20px"><a class="btn ghost" href="/photographers">Browse photographers</a></p></div>
</div></div></section>"""
    write("/book", page("/book", "Request a booking · Joenell Studio", "Request a vetted Vancouver wedding or elopement photographer for your date. Replies within 48 hours, no booking fee.", body))

def join():
    body = f"""
<section class="phead"><div class="wrap"><div class="two" style="align-items:center">
<div><p class="eyebrow">For photographers</p><h1>Get booked. Pay only when you are.</h1>
<p class="lead">Joenell Studio sends Vancouver couples to vetted wedding and elopement photographers. Joining is free. When a couple books you through the platform, Joenell Studio keeps a 15% commission. That's it.</p>
<a class="btn" href="#apply">Apply to join</a></div>
<div class="collage" aria-hidden="true"><figure class="a">{img('st-07', '', sizes='25vw')}</figure><figure class="b">{img('cl-wedding-dance', '', sizes='25vw')}</figure><figure class="c">{img('jh-gaze', '', sizes='25vw')}</figure><figure class="d">{img('cl-wedding-rings', '', sizes='25vw')}</figure></div>
</div></div></section>
<section style="background:var(--bg-2)"><div class="wrap">
<div class="steps">
  <div class="step reveal"><h3>Free to join</h3><p class="muted">No monthly fee and nothing to pay to be seen. 15% of the package price, only on bookings made through Joenell Studio, taken from the couple's deposit.</p></div>
  <div class="step reveal"><h3>Your packages, your prices</h3><p class="muted">List your own packages and prices, the same as on your own website, and set your own deposit (at least 20%).</p></div>
  <div class="step reveal"><h3>Get seen</h3><p class="muted">A flipbook portfolio, a “New on Joenell” spot, a welcome post on Instagram and 3 free blog and Instagram features every quarter.</p></div>
</div></div></section>
<section><div class="wrap"><div class="two">
<div><p class="eyebrow">What we ask</p><h2>Our standards</h2>
<ul style="padding-left:20px">
<li><b>One full gallery, in private.</b> Send one complete wedding or elopement gallery. It's never published, it only shows you can cover a whole day.</li>
<li><b>A chapter portfolio.</b> At least 5 photos for each moment: getting ready, ceremony, portraits, details and reception. Photos can come from different weddings.</li>
<li><b>Liability insurance.</b> Many venues ask for it, so we do too.</li>
<li><b>A short meeting</b> with Joenell, in person or on video.</li>
<li><b>Fast replies.</b> Accept or decline booking requests within 48 hours.</li>
<li><b>The standard agreement</b> for every Joenell Studio booking, and delivery on time.</li>
</ul>
<p class="muted">Newer photographers are welcome. If you're not ready to lead full weddings yet, the second-shooter roster is a great way to build experience.</p></div>
<div><div class="sticky-book"><h3>Example</h3><p class="muted">Adventure Elopement at $1,400 with a 20% deposit ($280):</p>
<table class="ptable"><tr><td>Joenell Studio commission (15%)<small>Taken from the deposit</small></td><td>$210</td></tr><tr><td>Rest of the deposit<small>Paid to you</small></td><td>$70</td></tr><tr><td>Balance from the couple<small>Before the wedding</small></td><td>$1,120</td></tr><tr><td><b>You earn</b></td><td>$1,190</td></tr></table>
<p class="small muted" style="margin-top:10px">Card fees are covered by Joenell Studio.</p></div></div>
</div></div></section>
<section id="apply" style="background:var(--bg-2)"><div class="wrap">
<div class="center" style="margin-bottom:30px"><p class="eyebrow">Apply</p><h2>Apply to join Joenell Studio</h2><p class="lead">We review every application by hand and reply within a week.</p></div>
<div class="formcard">
<form data-endpoint="/api/apply" data-done="apply-done" novalidate>
  <fieldset><legend>About you</legend><div class="grid2">
    <div class="field"><label for="a-name">Your name</label><input id="a-name" name="name" required maxlength="100" autocomplete="name"></div>
    <div class="field"><label for="a-biz">Business name</label><input id="a-biz" name="business" required maxlength="120"></div>
    <div class="field"><label for="a-em">Email</label><input id="a-em" type="email" name="email" required maxlength="200" autocomplete="email"></div>
    <div class="field"><label for="a-tel">Phone</label><input id="a-tel" type="tel" name="phone" required maxlength="40" autocomplete="tel"></div>
    <div class="field"><label for="a-web">Website <span class="opt">(optional)</span></label><input id="a-web" name="site" maxlength="200" placeholder="https://"></div>
    <div class="field"><label for="a-ig">Instagram <span class="opt">(optional)</span></label><input id="a-ig" name="instagram" maxlength="100" placeholder="@"></div>
    <div class="field"><label for="a-city">Where you're based</label><input id="a-city" name="city" required maxlength="100" placeholder="e.g. Burnaby"></div>
    <div class="field"><label for="a-years">Years photographing weddings</label><select id="a-years" name="years" required><option value="">Choose…</option><option>Less than 1</option><option>1–2</option><option>3–5</option><option>6+</option></select></div>
  </div></fieldset>
  <fieldset><legend>Your work</legend><div class="grid2">
    <div class="field full"><label for="a-gal">Link to one full wedding or elopement gallery</label><input id="a-gal" name="full_gallery" required maxlength="400" placeholder="Pixieset, Pic-Time, Google Drive…"><p class="hint">Kept private. Add the gallery password in the notes if it has one.</p></div>
    <div class="field full"><label for="a-port">Link to your portfolio <span class="opt">(optional)</span></label><input id="a-port" name="portfolio" maxlength="400"></div>
    <div class="field"><label for="a-wed">Weddings or elopements shot as lead</label><input id="a-wed" name="weddings_lead" inputmode="numeric" maxlength="20" required></div>
    <div class="field"><label for="a-ins">Liability insurance</label><select id="a-ins" name="insurance" required><option value="">Choose…</option><option>Yes, I have it</option><option>Not yet, I'll get it before joining</option></select></div>
    <div class="field full"><label>I'm interested in</label>
      <label class="choice"><input type="checkbox" name="interest" value="lead"> Lead photographer bookings</label>
      <label class="choice"><input type="checkbox" name="interest" value="second-shooter"> Second-shooter roster</label></div>
    <div class="field full"><label for="a-notes">Tell us about your style <span class="opt">(and anything else we should know)</span></label><textarea id="a-notes" name="notes" maxlength="3000"></textarea></div>
  </div></fieldset>
  <div class="hp" aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
  <label class="choice"><input type="checkbox" name="consent" value="yes" required> I agree to the <a href="/terms">terms</a> and to Joenell Studio storing my application (<a href="/privacy">privacy</a>).</label>
  <button class="btn" type="submit" style="margin-top:20px;width:100%">Send my application</button>
  <div class="msg" role="alert"></div>
</form>
<div class="done" id="apply-done" role="status"><div class="tick">✓</div><h2>Application received</h2><p class="lead" style="margin:0 auto">Thank you! Joenell will review your gallery and reply by email within a week.</p></div>
</div></div></section>"""
    write("/join", page("/join", "Join Joenell Studio · For Vancouver wedding photographers",
                        "Vancouver wedding and elopement photographers: join Joenell Studio free and pay a 15% commission only when you're booked. Apply today.",
                        body, active="/join", og_img="st-07"))

def how():
    body = f"""
<section class="phead"><div class="wrap center"><p class="eyebrow">How it works</p><h1>Simple for couples, fair for photographers</h1>
<p class="lead">Joenell Studio connects Vancouver couples with vetted photographers at fixed prices, and stands behind every booking.</p></div></section>
<section style="padding-top:10px"><div class="wrap"><h2>For couples</h2>
<div class="steps"><div class="step"><h3>Pick a package and date</h3><p class="muted">City Hall / Elopement, Adventure Elopement or Micro-Wedding.</p></div>
<div class="step"><h3>Choose or get matched</h3><p class="muted">Request a photographer you like, or let us match you with someone who's free on your date.</p></div>
<div class="step"><h3>Hear back within 48 hours</h3><p class="muted">The photographer accepts or declines within 48 hours. If they can't, we suggest someone else.</p></div>
<div class="step"><h3>Sign and pay the deposit</h3><p class="muted">One standard agreement, signed online, and a secure card deposit (at least 20%) to hold your date.</p></div>
<div class="step"><h3>Enjoy your day</h3><p class="muted">Reminders before the wedding. If your photographer can't fulfil the booking, you get your full deposit back or choose another photographer.</p></div>
<div class="step"><h3>Get your photos, leave a review</h3><p class="muted">Your gallery arrives on time, and you can leave a verified review to help other couples.</p></div></div>
</div></section>
<section style="background:var(--bg-2)"><div class="wrap"><h2>For photographers</h2>
<div class="steps"><div class="step"><h3>Apply</h3><p class="muted">Send one full gallery in private, your portfolio and proof of insurance.</p></div>
<div class="step"><h3>Get approved</h3><p class="muted">After a short meeting, your profile and flipbook go live right away, with a welcome post on Instagram.</p></div>
<div class="step"><h3>Get booked</h3><p class="muted">Booking requests arrive by email. 15% is taken from the deposit only when you're booked.</p></div></div>
<p style="margin-top:26px"><a class="btn" href="/join">Learn more and apply</a></p></div></section>
<section id="faq"><div class="wrap center"><p class="eyebrow">FAQ</p><h2>Questions and answers</h2>{faq_html(FAQ_COUPLES)}</div></section>"""
    write("/how-it-works", page("/how-it-works", "How Joenell Studio works · Booking a Vancouver wedding photographer",
                                "How booking works on Joenell Studio: fixed packages, vetted photographers, one standard agreement, secure deposits and a protected deposit if a photographer can't attend.",
                                body, active="/how-it-works", schema=faq_schema(FAQ_COUPLES)))

def legal():
    today = "November 14, 2026"
    terms = f"""<section class="phead"><div class="wrap prose"><p class="eyebrow">Terms</p><h1>Terms of use</h1><p class="muted">Last updated {today}</p></div></section>
<section style="padding-top:0"><div class="wrap prose">
<p>Joenell Studio (“we”) runs joenellstudio.com, a platform that connects couples with independent wedding and elopement photographers in British Columbia. By using the site you agree to these terms.</p>
<h2>What we do</h2><p>We vet photographers, show their work and prices, pass booking requests to them and handle deposits. Each photographer is an independent business. The photography itself is provided by the photographer under the standard Joenell Studio booking agreement, which you sign before paying.</p>
<h2>Booking requests</h2><p>A booking request is not a booking. Your date is only held once the photographer has accepted, you have signed the agreement and your deposit is paid.</p>
<h2>Deposits and payments</h2><ul><li>Each photographer sets a deposit of at least 20% of the package price.</li><li>Deposits are non-refundable if the couple cancels. If the photographer can't fulfil the booking, the couple gets the full deposit back.</li><li>Joenell Studio's 15% commission is taken from the deposit. Couples pay no booking fee.</li><li>The balance is due before the wedding, as set out in the agreement.</li></ul>
<h2>If a photographer can't fulfil a booking</h2><p>Deposits are non-refundable, except when the photographer can't fulfil the agreement: then the photographer refunds the couple's full deposit. The couple can also choose another photographer on Joenell Studio for their date.</p>
<h2>Photographers</h2><p>Photographers must stay vetted (insurance, quality, on-time delivery and replies within 48 hours) and use the standard agreement for bookings made through Joenell Studio. We may remove a photographer from the platform after repeated poor reviews or broken commitments.</p>
<h2>Photos and content</h2><p>Photos on this site belong to the photographers who made them. Please don't copy them without permission. Photographers confirm they have the right to show the photos they upload.</p>
<h2>Reviews</h2><p>Only couples with a real booking can leave a review. Reviews must be honest and respectful.</p>
<h2>Contact</h2><p>Questions about these terms: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></section>"""
    privacy = f"""<section class="phead"><div class="wrap prose"><p class="eyebrow">Privacy</p><h1>Privacy policy</h1><p class="muted">Last updated {today}</p></div></section>
<section style="padding-top:0"><div class="wrap prose">
<h2>What we collect</h2><p>Only what you type into our forms: for couples, your names, contact details, wedding date, location and notes; for photographers, your application details and links.</p>
<h2>How we use it</h2><p>To arrange your booking, we share a couple's request with the photographer it's for (or the photographers we match you with). We use photographers' applications to review them. We don't sell or rent your information, and we don't use it for advertising.</p>
<h2>Where it's kept</h2><p>Form entries are stored securely with our hosting provider, Cloudflare. Payments are handled by Stripe. We never see or store full card numbers.</p>
<h2>Cookies and analytics</h2><p>This site doesn't use advertising cookies. We may use privacy-friendly analytics that count visits without tracking you across sites.</p>
<h2>Private galleries</h2><p>Full galleries sent with a photographer application are only used for vetting and are never published.</p>
<h2>Your choices</h2><p>You can ask to see, correct or delete your information at any time by emailing <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></section>"""
    write("/terms", page("/terms", "Terms of use · Joenell Studio", "Terms of use for Joenell Studio, the Vancouver wedding photographer booking platform.", terms))
    write("/privacy", page("/privacy", "Privacy policy · Joenell Studio", "How Joenell Studio collects, uses and protects your information.", privacy))
    nf = """<section class="phead"><div class="wrap center"><p class="eyebrow">Page not found</p><h1>This page wandered off</h1><p class="lead">Let's get you back on track.</p><p style="margin-top:24px"><a class="btn" href="/">Go to the homepage</a></p></div></section>"""
    write("/404", page("/404", "Page not found · Joenell Studio", "Page not found.", nf))

def extras():
    urls = ["/", "/photographers", "/packages", "/how-it-works", "/join", "/book", "/terms", "/privacy"] + [f"/photographers/{p['slug']}" for p in PHOTOGRAPHERS]
    d = datetime.date.today().isoformat()
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"  <url><loc>{DOMAIN}{u}</loc><lastmod>{d}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nDisallow: /admin\nDisallow: /api/\nSitemap: {DOMAIN}/sitemap.xml\n")
    open(os.path.join(OUT, "favicon.svg"), "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#3e4a40"/><text x="32" y="45" text-anchor="middle" font-family="Georgia,serif" font-size="38" fill="#fbf8f3">J</text></svg>')
    for src, dst in (("assets", "assets"), ("images", "images")):
        shutil.copytree(os.path.join(ROOT, src), os.path.join(OUT, dst), dirs_exist_ok=True)
    shutil.copy(os.path.join(ROOT, "_worker.js"), os.path.join(OUT, "_worker.js"))

if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    home(); packages(); photographers(); book(); join(); how(); legal()
    for p in PHOTOGRAPHERS: profile(p)
    extras()
    print("built", sum(len(f) for _, _, f in os.walk(OUT)), "files in", OUT)
