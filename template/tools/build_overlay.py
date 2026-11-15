# -*- coding: utf-8 -*-
"""Build the graphics layer (hook title, 3-language subtitles, local-info tags, stickers, end card)
from edl.py + content.py (+ vo/script.json narration, if voiced).

Writes:
  compositions/overlay.html   the layer as a sub-composition (transparent background)
  index.html                  root composition: optional 1080p footage proxy + the overlay
  work/<CUT>/overlay_cues.json  cue times for tools/mix.py (pop SFX on tags) and QA
The layer is authored at 1080x1920 CSS px and rendered by HyperFrames at portrait-4k (2160x3840),
so text is rasterised at full delivery resolution -- it is never upscaled.
Usage: [CUT=tiktok] python tools/build_overlay.py"""
import html, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from edl import timeline, WORK, CUT, OUT_FPS
import content as C

TL, TOTAL = timeline()
SEG = {s["id"]: s for s in TL}


def at(sid, off=0.0):
    if sid not in SEG:
        sys.exit(f"content.py refers to segment {sid!r}, which is not in CUT={CUT}")
    return round(SEG[sid]["start"] + off, 3)


def span(a, b):
    return at(a), round(SEG[b]["start"] + SEG[b]["dur"] - SEG[a]["start"], 3)


def e(x):
    return html.escape(x or "", quote=True)


def langs(t, cls=("l1", "l2", "l3"), split=False):
    out = []
    for c, x in zip(cls, t):
        if not x:
            continue
        if split and c == cls[0]:
            inner = "".join('<span class="ln">%s</span>' % e(p) for p in x.split("|"))
        else:
            inner = e(x.replace("|", ""))
        out.append('<div class="%s">%s</div>' % (c, inner))
    return "".join(out)


# ---------------------------------------------------------------- cues
SUBS = []
for sg, off, d, t in C.SUBS:
    if sg in SEG:
        SUBS.append((at(sg, off), d, t, False))
    else:
        print(f"  - subtitle {t[0][:16]!r} skipped (segment {sg} not in CUT={CUT})")
VOS = []
vs_p, vt_p = os.path.join(ROOT, "vo", "script.json"), os.path.join(ROOT, "vo", "timeline.json")
if os.path.exists(vs_p) and os.path.exists(vt_p):
    VT = json.load(open(vt_p, encoding="utf-8"))
    for l in json.load(open(vs_p, encoding="utf-8")):
        if l["seg"] in SEG and l["id"] in VT:
            VOS.append((at(l["seg"], l["off"]), round(VT[l["id"]]["dur"] + 0.12, 3), tuple(l["sub"]), True))
ALL = sorted(SUBS + VOS, key=lambda x: x[0])
for (a1, d1, *_), (b1, *_) in zip(ALL, ALL[1:]):
    if a1 + d1 > b1 + 0.01:
        print(f"  ! subtitle at {a1:.2f} overlaps the next one at {b1:.2f}")

TAGS = []
for a, b, kind, t, note in C.TAGS:
    if a not in SEG or b not in SEG:
        print(f"  - tag {t[0]} skipped (segment not in CUT={CUT})")
        continue
    s, d = span(a, b)
    TAGS.append((round(s + 0.12, 3), round(d - 0.20, 3), kind, t, note))

# ---------------------------------------------------------------- markup
FONTS = '@font-face{font-family:"%s";src:url("assets/fonts/%s");font-weight:100 900}\n' % (
    C.FONT_MAIN[0], os.path.splitext(C.FONT_MAIN[1])[0] + "-sub.ttf")
FONTS += "".join('@font-face{font-family:"%s";src:url("assets/fonts/%s");font-weight:%s}\n' % f for f in C.FONT_ALT)
MAIN, ALT = C.FONT_MAIN[0], C.FONT_ALT[0][0]
K = C.COLORS

CSS = """
#ov{--yel:%(yel)s;--pink:%(pink)s;--ink:%(ink)s;--card:%(card)s;--l3:%(l3)s;font-family:"%(MAIN)s","%(ALT)s",sans-serif;color:#fff}
#ov .alt,#ov .l2,#ov .l3{font-family:"%(ALT)s","%(MAIN)s",sans-serif}
/* safe zones (1080x1920 px): top 220, bottom 440, right rail 150 -- platform UI lives there */
#ov .subwrap{z-index:5;position:absolute;left:56px;right:150px;bottom:440px;display:flex;justify-content:center}
#ov .sub{position:relative;max-width:874px;padding:14px 30px 18px;border-radius:24px;text-align:center;background:var(--card)}
#ov .sub .l1{font-size:48px;font-weight:900;line-height:1.22}
#ov .sub .l1 .ln{display:inline-block}
#ov .sub .l2,#ov .sub .l3{text-wrap:balance}
#ov .sub .l2{font-size:29px;font-weight:600;line-height:1.3;color:var(--yel)}
#ov .sub .l3{font-size:29px;font-weight:500;line-height:1.35;color:var(--l3)}
#ov .sub.vo{box-shadow:8px 8px 0 var(--yel)}
#ov .sub.vo .bar{background:var(--pink)}
#ov .sub .bar{position:absolute;left:24px;right:24px;bottom:7px;height:5px;border-radius:5px;background:var(--yel);transform-origin:left center}
#ov .tagwrap{position:absolute;left:56px;top:300px;right:150px}
#ov .tag{position:relative;display:inline-block;max-width:874px;padding:16px 28px 18px 36px;border-radius:22px;background:var(--card);box-shadow:8px 8px 0 var(--yel)}
#ov .tag::before{content:"";position:absolute;left:0;top:18px;bottom:18px;width:9px;border-radius:0 6px 6px 0;background:var(--pink)}
#ov .tag .k{display:inline-block;font-size:24px;font-weight:700;letter-spacing:.06em;color:var(--ink);background:var(--yel);border-radius:10px;padding:2px 12px;margin-bottom:8px}
#ov .tag .l1{font-size:54px;font-weight:900;line-height:1.15}
#ov .tag .l2{font-size:30px;font-weight:600;line-height:1.3;color:var(--yel)}
#ov .tag .l3{font-size:30px;font-weight:500;line-height:1.35;color:var(--l3)}
#ov .tag .note{margin-top:10px;padding-top:10px;border-top:2px solid rgba(255,255,255,.18)}
#ov .tag .note .l1{font-size:26px;font-weight:500;line-height:1.38;color:rgba(255,255,255,.92)}
#ov .tag .note .l2,#ov .tag .note .l3{font-size:24px;font-weight:500;color:rgba(255,255,255,.78)}
#ov .tag.bonus{box-shadow:8px 8px 0 var(--pink)}
#ov .tag.bonus .k{background:var(--pink);color:#fff}
#ov .hook{position:absolute;left:56px;right:150px;top:470px}
#ov .hook .pill{display:inline-flex;align-items:center;gap:14px;padding:12px 26px;border-radius:999px;background:var(--ink);border:3px solid var(--yel);font-size:36px;font-weight:900}
#ov .hook .pill i{width:18px;height:18px;border-radius:50%%;background:var(--pink);display:block}
#ov .hook .big{margin-top:22px;font-weight:900;font-size:112px;line-height:1.05;color:var(--yel);
  text-shadow:6px 6px 0 var(--pink),0 0 2px var(--ink);-webkit-text-stroke:3px var(--ink);paint-order:stroke fill}
#ov .hook .main{margin-top:10px;font-size:84px;font-weight:900;line-height:1.1;color:#fff;-webkit-text-stroke:3px var(--ink);paint-order:stroke fill;text-shadow:5px 5px 0 var(--ink)}
#ov .hook .small{margin-top:12px;font-size:36px;font-weight:700;color:#fff;-webkit-text-stroke:2px var(--ink);paint-order:stroke fill}
#ov .stk{position:absolute;width:260px;height:260px;border-radius:50%%;background:#e8262d;display:flex;flex-direction:column;align-items:center;justify-content:center;
  box-shadow:8px 8px 0 var(--ink);outline:4px dashed #fff;outline-offset:-16px;text-align:center}
#ov .stk .a{font-size:40px;font-weight:900;line-height:1.1}
#ov .stk .b{font-size:58px;font-weight:900;line-height:1;color:var(--yel);margin:6px 0}
#ov .stk .c{font-size:24px;font-weight:700;letter-spacing:.08em}
#ov .hook-stk{right:150px;top:850px}
#ov .date-stk{right:150px;top:300px}
#ov .end{z-index:1;position:absolute;inset:0;background:radial-gradient(120%% 80%% at 50%% 0%%,#5a1830 0%%,#2a0f22 45%%,#120814 100%%)}
#ov .end .dots{position:absolute;inset:0;opacity:.35;background-image:radial-gradient(circle,rgba(255,210,31,.55) 0 3px,transparent 4px);background-size:72px 72px}
#ov .end .box{position:absolute;left:70px;right:150px;top:300px}
#ov .end .k{display:inline-block;font-size:26px;font-weight:700;letter-spacing:.08em;color:var(--ink);background:var(--yel);border-radius:10px;padding:3px 14px}
#ov .end .l1{margin-top:22px;font-size:58px;font-weight:900;line-height:1.18;color:var(--yel)}
#ov .end .l2{margin-top:14px;font-size:44px;font-weight:900;line-height:1.25;color:#fff}
#ov .end .l3{margin-top:10px;font-size:30px;font-weight:600;line-height:1.3;color:var(--l3)}
#ov .end .rows{margin-top:40px;display:flex;flex-direction:column;gap:22px}
#ov .end .row{display:flex;gap:22px;align-items:flex-start;padding:20px 24px;border-radius:20px;background:rgba(255,255,255,.07);border:2px solid rgba(255,255,255,.12)}
#ov .end .row svg{flex:0 0 52px;width:52px;height:52px}
#ov .end .row .t1{font-size:38px;font-weight:900;line-height:1.2}
#ov .end .row .t2{font-size:26px;font-weight:600;line-height:1.35;color:rgba(255,255,255,.82)}
""" % dict(K, MAIN=MAIN, ALT=ALT)

_SV = '<svg viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">' % K["yel"]
ICON = {
    "cal": _SV + '<rect x="3" y="4.5" width="18" height="16" rx="2.5"/><path d="M3 9.5h18M8 2.8v3.4M16 2.8v3.4"/></svg>',
    "pin": _SV + '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.6"/></svg>',
    "tix": _SV + '<path d="M3 8a2 2 0 0 0 0 4v0a2 2 0 0 1 0 4v2h18v-2a2 2 0 0 1 0-4 2 2 0 0 1 0-4V6H3z"/><path d="M14 6v12" stroke-dasharray="2 2.4"/></svg>',
}

parts, n = [], 0


def clip(t, d, cls, inner, track):
    global n
    n += 1
    return ('<div class="clip %s" id="ov-%s%d" data-start="%.3f" data-duration="%.3f" data-track-index="%d">%s</div>'
            % (cls, cls.split()[0], n, t, d, track, inner))


H = C.HOOK
if H and H["until"] not in SEG:
    print(f"  - hook skipped (segment {H['until']} not in CUT={CUT})")
    H = None
if H:
    hd = at(H["until"])
    parts.append(clip(0.15, hd - 0.25, "hook", (
        '<div class="in">'
        '<div class="pill a1"><i></i>%s</div><div class="big alt a2">%s</div>'
        '<div class="main a3">%s</div><div class="small alt a4">%s</div></div>'
        % (e(H["pill"]), e(H["big"]), e(H["main"]), e(H["small"]))), 10))
    if H.get("sticker"):
        a, b, c = H["sticker"]
        parts.append(clip(0.6, hd - 0.7, "hookstk",
                          '<div class="stk hook-stk in"><div class="a">%s</div><div class="b alt">%s</div><div class="c alt">%s</div></div>'
                          % (e(a), e(b), e(c)), 11))

for t, d, kind, txt, note in TAGS:
    nt = '<div class="note">%s</div>' % langs(note) if note else ""
    parts.append(clip(t, d, "tagwrap", '<div class="tag%s in"><div class="k alt">%s</div>%s%s</div>'
                      % (" bonus" if kind == "bonus" else "", e(C.KINDS[kind]), langs(txt), nt), 20))

if C.DATE_STICKER and C.DATE_STICKER[0] in SEG and C.DATE_STICKER[1] in SEG:
    a_, b_, (a, b, c) = C.DATE_STICKER
    t, d = span(a_, b_)
    parts.append(clip(t + 0.3, d - 0.4, "datestk",
                      '<div class="stk date-stk in"><div class="a">%s</div><div class="b alt">%s</div><div class="c alt">%s</div></div>'
                      % (e(a), e(b), e(c)), 21))

for t, d, txt, vo in ALL:
    parts.append(clip(t, d, "subwrap", '<div class="sub%s in">%s<div class="bar"></div></div>'
                      % (" vo" if vo else "", langs(txt, split=True)), 30))

END = C.END
if END and END["seg"] in SEG:
    t, d = span(END["seg"], END["seg"])
    rows = "".join('<div class="row r%d">%s<div><div class="t1">%s</div><div class="t2 alt">%s</div></div></div>'
                   % (i, ICON[ic], e(a), e(b)) for i, (ic, a, b) in enumerate(END["rows"]))
    parts.append(clip(t, d, "end", '<div class="dots"></div><div class="box"><div class="k alt e1">%s</div>%s<div class="rows">%s</div></div>'
                      % (e(END["kicker"]), langs(END["title"], cls=("l1 e2", "l2 e3", "l3 e4")), rows), 40))

BODY = "\n".join(parts)

JS = """
(function(){
  const tl = gsap.timeline({paused:true});
  const R = document.getElementById("ov");
  const Q = s => Array.from(R.querySelectorAll(s));
  const T = el => parseFloat(el.dataset.start), D = el => parseFloat(el.dataset.duration);
  Q(".subwrap").forEach(el => {
    const b = el.querySelector(".sub"), bar = el.querySelector(".bar"), t = T(el), d = D(el);
    tl.fromTo(b, {y:26, scale:.94, opacity:0}, {y:0, scale:1, opacity:1, duration:.22, ease:"back.out(2)"}, t);
    tl.fromTo(bar, {scaleX:0}, {scaleX:1, duration:Math.max(.2, d - .1), ease:"none"}, t);
    tl.to(b, {opacity:0, y:-8, duration:.12, ease:"power1.in"}, t + d - .12);
  });
  Q(".tagwrap").forEach(el => {
    const b = el.querySelector(".tag"), t = T(el), d = D(el);
    tl.fromTo(b, {x:-60, opacity:0}, {x:0, opacity:1, duration:.32, ease:"back.out(1.6)"}, t);
    tl.to(b, {opacity:0, x:-24, duration:.18, ease:"power1.in"}, t + d - .18);
  });
  Q(".hookstk, .datestk").forEach(el => {
    const b = el.querySelector(".stk"), t = T(el), d = D(el);
    tl.fromTo(b, {scale:0, rotation:-25}, {scale:1, rotation:-8, duration:.42, ease:"back.out(2.2)"}, t);
    tl.to(b, {scale:.9, opacity:0, duration:.16, ease:"power1.in"}, t + d - .16);
  });
  Q(".hook").forEach(el => {
    const t = T(el), d = D(el);
    tl.fromTo(Q(".hook .a1, .hook .a2, .hook .a3, .hook .a4"), {y:40, opacity:0}, {y:0, opacity:1, duration:.34, stagger:.12, ease:"power3.out"}, t);
    tl.to(el.querySelector(".in"), {opacity:0, y:-20, duration:.2, ease:"power1.in"}, t + d - .2);
  });
  Q(".end").forEach(el => {
    const t = T(el), d = D(el);
    tl.fromTo(el.querySelector(".box"), {opacity:0}, {opacity:1, duration:.2}, t);
    tl.fromTo(Q(".end .e1, .end .e2, .end .e3, .end .e4"), {y:30, opacity:0}, {y:0, opacity:1, duration:.32, stagger:.1, ease:"power3.out"}, t + .1);
    tl.fromTo(Q(".end .row"), {x:-50, opacity:0}, {x:0, opacity:1, duration:.3, stagger:.14, ease:"back.out(1.5)"}, t + .6);
    tl.fromTo(el.querySelector(".dots"), {backgroundPosition:"0px 0px"}, {backgroundPosition:"0px -72px", duration:d, ease:"none"}, t);
    tl.to(el.querySelector(".box"), {opacity:0, duration:.25}, t + d - .25);
  });
  tl.set({}, {}, %TOTAL%);
  window.__timelines = window.__timelines || {};
  window.__timelines["overlay"] = tl;
})();
""".replace("%TOTAL%", str(TOTAL))

GSAP = '<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'

SUBCOMP = """<template id="overlay-template">
<div id="ov" data-composition-id="overlay" data-start="0" data-duration="%(T)s" data-width="1080" data-height="1920" style="position:absolute;inset:0;overflow:hidden">
<style>
%(FONTS)s
%(CSS)s
</style>
%(BODY)s
<script>%(JS)s</script>
</div>
</template>
""" % dict(T=TOTAL, FONTS=FONTS, CSS=CSS, BODY=BODY, JS=JS)

INDEX = """<!DOCTYPE html>
<html lang="%(LANG)s" data-composition-variables='[{"id":"footage","type":"boolean","label":"Show footage proxy","default":true}]'>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, height=1920">
<title>%(CUT)s preview</title>
%(GSAP)s
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
#root{position:relative;width:100%%;height:100%%;overflow:hidden;background:#000}
#footage{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%(T)s" data-fps="%(FPS)s" data-width="1080" data-height="1920">
  <div id="fwrap" style="position:absolute;inset:0">
    <video id="footage" class="clip" src="assets/preview/footage_proxy_%(CUT)s.mp4" data-start="0" data-duration="%(T)s" data-track-index="0" data-has-audio="true" playsinline></video>
  </div>
  <div id="overlay" data-composition-id="overlay" data-composition-src="compositions/overlay.html" data-start="0" data-duration="%(T)s" data-track-index="1" data-width="1080" data-height="1920"></div>
</div>
<script>
  // footage=false -> graphics layer only on a transparent background (ProRes 4444 render for compositing)
  (function(){
    var v = (window.__hyperframes && window.__hyperframes.getVariables) ? window.__hyperframes.getVariables() : {};
    if (v.footage === false) {
      document.getElementById("fwrap").style.display = "none";
      ["root"].forEach(function(id){ document.getElementById(id).style.background = "transparent"; });
      document.documentElement.style.background = "transparent";
      document.body.style.background = "transparent";
    }
  })();
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = gsap.timeline({paused:true});
</script>
</body>
</html>
""" % dict(LANG=C.LANG, CUT=CUT, GSAP=GSAP, T=TOTAL, FPS=OUT_FPS)

os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
open(os.path.join(ROOT, "compositions", "overlay.html"), "w", encoding="utf-8").write(SUBCOMP)
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(INDEX)
json.dump({"total": TOTAL, "subs": [x[:3] for x in ALL], "tags": [t[:4] for t in TAGS]},
          open(os.path.join(WORK, "overlay_cues.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"overlay built: CUT={CUT} total {TOTAL}s, {len(SUBS)} subs, {len(VOS)} narration subs, {len(TAGS)} tags")
