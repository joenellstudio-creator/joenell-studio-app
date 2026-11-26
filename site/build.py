#!/usr/bin/env python3
"""Joenell Studio — magazine homepage. Edit PAGES below, run `python3 build.py` → writes index.html.
The magazine uses assets/flipbook.js (page curl by dragging a bottom corner). Page types:
  mcover  full-bleed cover photo with masthead          opener  full-bleed section opener photo with big title
  dark    dark typographic page (e.g. coming soon)      txt     text page (html)
  full    photo filling the page                        mat     photo in a white mat with caption
  duo     two photos with caption                       backc   back cover
Links: <a class="cta" href="https://..."> opens a site; <a data-page="N"> jumps to page N.
"""
import json, os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
WED = "https://www.joenellphotography.ca/"
MAIL = "mailto:joenellstudio@gmail.com?subject=Event%20photography%20enquiry"
VER = "20261125r"

JP = "https://www.joenellphotography.ca"
def opener(img, num, title, by, pos="50% 30%"):
    return dict(t="opener", html=f'''<img class="bleed" src="/images/{img}.jpg" style="object-position:{pos}" alt="" draggable="false"><div class="shade"></div>
<div class="otext"><span class="onum">{num}</span><h2>{title}</h2><p>{by}</p></div>''')
def linkpage(eb, h, paras, url, label):
    body = "".join(f"<p>{x}</p>" for x in paras)
    return dict(t="txt", html=f'''<p class="eb">{eb}</p><h2>{h}</h2><div class="rule"></div>{body}<a class="cta" href="{url}">{label}</a>''')
def toc(page, n, title, small):
    return f'<a class="toc" data-page="{page}"><span class="n">{n}</span><span class="t">{title}<small>{small}</small></span><span class="p">p. {page}</span></a>'

P = [
 # 0 cover
 dict(t="mcover", html='''<img class="bleed" src="/images/cl-wedding-kiss.jpg" alt="" draggable="false"><div class="shade"></div>
<div class="mast"><span class="m1">JOENELL</span><span class="m2">STUDIO</span></div>
<div class="lines"><p><b>Weddings · Engagements · Proposals</b> by Joenell Photography</p><p><b>Events</b> coming soon</p></div>
<div class="foot-line"><span>Issue 01</span><span>Vancouver, BC</span></div>'''),
 # 1 welcome
 dict(t="txt", html='''<p class="eb">From the studio</p><h2>One studio, every kind of story.</h2><div class="rule"></div>
<p>Joenell Studio is the home of my photography in Vancouver. Every section of this magazine is a different kind of photography: a different moment, the same eye for what's real.</p>
<p>Turn the page to see what the studio covers, or jump straight to a section.</p><p class="sig">Joenell</p>'''),
 # 2 contents
 dict(t="txt contents", html='<p class="eb">In this issue</p><h2>Contents</h2><div class="rule"></div>'
   + toc(3, "01", "Weddings", "by Joenell Photography")
   + toc(7, "02", "Engagements", "by Joenell Photography")
   + toc(11, "03", "Surprise proposals", "by Joenell Photography")
   + toc(15, "04", "Event photography", "Coming soon")
   + toc(17, "05", "More to come", "New styles over time")
   + '<p class="how">Tap a section to jump there</p>'),
 # 3-6 weddings
 opener("cl-wedding-veil", "01", "Wedding<br>photography", "by Joenell Photography"),
 linkpage("01 · Weddings", "Your wedding day", ["Garden weddings, city celebrations and everything in between, across Vancouver and British Columbia.",
   "Natural, warm and true to how the day felt: gentle direction, real moments and bright, true-to-life colour."], JP + "/weddings", "See wedding photography"),
 dict(t="mat", img="cl-wedding-path", cap="Through the garden", sub="An autumn wedding in Vancouver"),
 dict(t="duo", imgs=["cl-wedding-dip", "cl-wedding-bench"], cap="A few minutes for the two of you"),
 # 7-10 engagements
 opener("st-03", "02", "Engagement<br>sessions", "by Joenell Photography", "50% 20%"),
 linkpage("02 · Engagements", "Before the big day", ["A relaxed session for the two of you: in the gardens, by the water or somewhere that means something to you.",
   "Perfect for save-the-dates, and a chance to get comfortable in front of the camera."], JP + "/engagements", "See engagement sessions"),
 dict(t="full", img="cl-engagement-embrace", cap="Golden hour on the water"),
 dict(t="mat", img="je-cover", cap="Together", sub="An engagement session in Vancouver"),
 # 11-14 proposals
 opener("jh-gaze", "03", "Surprise<br>proposals", "by Joenell Photography", "50% 25%"),
 linkpage("03 · Surprise proposals", "The moment she says yes", ["I plan the spot and the timing with you, stay hidden nearby, and capture the question, the answer and the happy minutes after.",
   "From Bowen Lookout to the seawall, the surprise stays a surprise."], JP + "/engagements", "Plan your proposal"),
 dict(t="mat", img="jh-lookout", cap="The question", sub="Bowen Lookout · Cypress Mountain"),
 dict(t="full", img="jh-kiss", cap="She said yes"),
 # 15-16 events
 dict(t="dark", html='''<div class="otext"><span class="onum">04</span><h2>Event<br>photography</h2><p>Coming soon</p></div>'''),
 linkpage("04 · Event photography", "Your event, captured.", ["Galas, launches, fundraisers and celebrations, photographed with the same eye for real moments. This section is coming soon."], MAIL, "Ask about your event"),
 # 17-18
 dict(t="txt", html='''<p class="eb">05 · More to come</p><h2>The next chapter.</h2><div class="rule"></div>
<p>New kinds of photography join the studio over time. Each one gets its own section of this magazine.</p>
<a class="toc back" data-page="2"><span class="t">Back to contents</span></a>'''),
 linkpage("Get in touch", "Let's talk about your day.", ["Weddings, engagements and proposals: check your date with Joenell Photography.", "Events and anything else: send an email."], JP + "/contact", "Book your date"),
 # 19
 dict(t="backc", title="Joenell Studio", meta="joenellstudio.com · Vancouver"),
]
assert len(P) % 2 == 0

used = {p.get("img") for p in P} | {x for p in P for x in p.get("imgs", [])}
IMG = {}
for n in sorted(x for x in used if x):
    w, h = Image.open(os.path.join(ROOT, "images", n + ".jpg")).size
    IMG[n] = {"w": w, "h": h, "src": f"/images/{n}.jpg"}
ALBUM = dict(el="mag", chapBar=".chapters", imgs=IMG, pages=P, chapters=[{"label": "Contents", "at": 2}, {"label": "Weddings", "at": 3}, {"label": "Engagements", "at": 7}, {"label": "Proposals", "at": 11}, {"label": "Events", "at": 15}])

HTML = open(os.path.join(ROOT, "template.html")).read()
out = HTML.replace("__ALBUM__", json.dumps(ALBUM, separators=(",", ":"))).replace("__VER__", VER).replace("__WED__", WED).replace("__MAIL__", MAIL)
open(os.path.join(ROOT, "index.html"), "w").write(out)
print("pages", len(P))
