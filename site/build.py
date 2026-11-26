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
VER = "20261125p"

P = [
 # 0
 dict(t="mcover", html=f'''<img class="bleed" src="/images/cl-wedding-kiss.jpg" alt="" draggable="false"><div class="shade"></div>
<div class="mast"><span class="m1">JOENELL</span><span class="m2">STUDIO</span></div>
<div class="issue">Issue 01 · Vancouver, BC</div>
<div class="lines"><p><b>Weddings</b> by Joenell Photography</p><p><b>Events</b> coming soon</p><p class="small">Drag the corner to open</p></div>'''),
 # 1
 dict(t="txt", html='''<p class="eb">From the studio</p><h2>One studio, every kind of story.</h2><div class="rule"></div>
<p>Joenell Studio is the home of my photography in Vancouver. Every section of this magazine is a different kind of photography: a different moment, the same eye for what's real.</p>
<p>Turn the page to see what the studio covers, or jump straight to a section.</p><p class="sig">Joenell</p>'''),
 # 2
 dict(t="txt", cls="contents", html='''<p class="eb">In this issue</p><h2>Contents</h2><div class="rule"></div>
<a class="toc" data-page="3"><span class="n">01</span><span class="t">Wedding photography<small>by Joenell Photography</small></span><span class="p">p. 3</span></a>
<a class="toc" data-page="12"><span class="n">02</span><span class="t">Event photography<small>Coming soon</small></span><span class="p">p. 12</span></a>
<a class="toc" data-page="14"><span class="n">03</span><span class="t">More to come<small>New styles over time</small></span><span class="p">p. 14</span></a>
<p class="how">Tap a section to jump there</p>'''),
 # 3
 dict(t="opener", html='''<img class="bleed" src="/images/cl-wedding-veil.jpg" alt="" draggable="false"><div class="shade"></div>
<div class="otext"><span class="onum">01</span><h2>Wedding<br>photography</h2><p>by Joenell Photography</p></div>'''),
 # 4
 dict(t="txt", html=f'''<p class="eb">01 · Wedding photography</p><h2>Joenell Photography</h2><div class="rule"></div>
<p>Weddings, elopements, engagement sessions and surprise proposals across Vancouver and British Columbia.</p>
<p>Natural, warm and true to how the day felt: gentle direction, real moments and bright, true-to-life colour.</p>
<a class="cta" href="{WED}">Visit joenellphotography.ca</a>'''),
 # 5-12 photos
 dict(t="mat", img="cl-wedding-path", cap="Through the garden", sub="An autumn wedding in Vancouver"),
 dict(t="duo", imgs=["cl-wedding-dip", "cl-wedding-bench"], cap="A few minutes for the two of you"),
 dict(t="full", img="jh-kiss", cap="Surprise proposals"),
 dict(t="mat", img="jh-lookout", cap="She said yes", sub="Bowen Lookout · Cypress Mountain"),
 dict(t="full", img="st-03", cap="Engagements"),
 dict(t="full", img="cl-engagement-embrace", cap="Golden hour"),
 # 13
 dict(t="txt", html=f'''<p class="eb">Your wedding</p><h2>Let's tell your story.</h2><div class="rule"></div>
<p>See full galleries, collections and prices, and check your date with Joenell Photography.</p>
<a class="cta" href="{WED}">Visit Joenell Photography</a>'''),
 # 14
 dict(t="dark", html='''<div class="otext"><span class="onum">02</span><h2>Event<br>photography</h2><p>Coming soon</p></div>'''),
 # 15
 dict(t="txt", html=f'''<p class="eb">02 · Event photography</p><h2>Your event, captured.</h2><div class="rule"></div>
<p>Galas, launches, fundraisers and celebrations, photographed with the same eye for real moments. This section is coming soon.</p>
<a class="cta" href="{MAIL}">Ask about your event</a>'''),
 # 16
 dict(t="txt", html='''<p class="eb">03 · More to come</p><h2>The next chapter.</h2><div class="rule"></div>
<p>New kinds of photography join the studio over time. Each one gets its own section of this magazine.</p>
<a class="toc back" data-page="2"><span class="t">Back to contents</span></a>'''),
 # 17
 dict(t="backc", title="Joenell Studio", meta="joenellstudio.com · Vancouver"),
]
assert len(P) % 2 == 0

used = {p.get("img") for p in P} | {x for p in P for x in p.get("imgs", [])}
IMG = {}
for n in sorted(x for x in used if x):
    w, h = Image.open(os.path.join(ROOT, "images", n + ".jpg")).size
    IMG[n] = {"w": w, "h": h, "src": f"/images/{n}.jpg"}
for p in P:  # engine reads p.html for unknown types; keep class for styling
    if "cls" in p: p["t"] = p["t"] + " " + p.pop("cls")
ALBUM = dict(el="mag", chapBar=".chapters", imgs=IMG, pages=P, chapters=[{"label": "Contents", "at": 2}, {"label": "Weddings", "at": 3}, {"label": "Events", "at": 12}])

HTML = open(os.path.join(ROOT, "template.html")).read()
out = HTML.replace("__ALBUM__", json.dumps(ALBUM, separators=(",", ":"))).replace("__VER__", VER).replace("__WED__", WED).replace("__MAIL__", MAIL)
open(os.path.join(ROOT, "index.html"), "w").write(out)
print("pages", len(P))
