# -*- coding: utf-8 -*-
"""Edit decision list (EDL) -- the single source of truth for the cut.

Source ids are 2-digit numbers in filename order (phone files are named by capture time, so this is
shooting order). `python edl.py --sources` prints the id -> file table; keep it next to your shot log.
Times are seconds. Every tool in tools/ imports this file and reads the env var CUT (default: first key
of VARIANTS) so one EDL can produce several versions (e.g. YouTube Shorts + a longer TikTok cut).
"""
import os, sys

# ------------------------------------------------------------------ project settings
SRC_DIR = os.environ.get("SRC_DIR") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VIDEO_EXT = (".mp4", ".mov", ".m4v")
OUT_W, OUT_H, OUT_FPS = 2160, 3840, 60          # delivery: 4K 9:16 at 60 fps
TITLE = "my-vlog"                                # used for render file names

# Output file per variant (written to renders/)
VARIANTS = {
    "shorts": {"file": f"{TITLE}_Shorts_4K60.mp4"},
    "tiktok": {"file": f"{TITLE}_TikTok_4K60.mp4",
               # longer cut: insert extra stable shots AFTER a given id, or change lengths
               "insert_after": {
                   # "f2": [("f2b", "food", "05", 1.00, 1.40, 0.3)],
               },
               "length": {
                   # "c1": 3.5,
               }},
}

# ------------------------------------------------------------------ sources
_files = sorted(f for f in os.listdir(SRC_DIR) if f.lower().endswith(VIDEO_EXT)) if os.path.isdir(SRC_DIR) else []
# Optional: force a file to a given position (e.g. a clip shot earlier on another camera app)
FIRST = []                                       # e.g. ["VID_20261112_184752.mp4"]
_order = FIRST + [f for f in _files if f not in FIRST]
SRC = {f"{i:02d}": os.path.join(SRC_DIR, f) for i, f in enumerate(_order, 1)}

# ------------------------------------------------------------------ the cut
# (id, section, src, in, dur, ambience volume)
#   section : name used for whoosh SFX on section changes
#   src     : source id, or None for a designed full-screen card (black footage under the graphics)
#   volume  : clip's own sound. 0 = mute, <1 = ambience bus (under music), >=1 = dialogue bus (ducks BGM)
SEGS = [
    ("h1", "hook", "01", 0.30, 0.95, 0.5),
    ("h2", "hook", "02", 0.20, 0.85, 0.5),
    ("i1", "intro", "03", 0.20, 3.50, 1.0),     # host talks to camera: sync sound at full volume
    ("f1", "food", "04", 0.00, 1.60, 0.3),
    ("f2", "food", "05", 1.00, 1.40, 0.3),
    ("e1", "endcard", None, 0.00, 4.50, 0.0),
]

# Extra audio not tied to its own picture (L/J-cuts, host voice over b-roll):
# (src, in, dur, at_segment, offset_in_segment, volume)
AUDIO = [
    # ("03", 4.90, 2.45, "f1", 0.0, 1.0),
]

# ------------------------------------------------------------------ do not edit below
CUT = os.environ.get("CUT", next(iter(VARIANTS)))
if CUT not in VARIANTS:
    sys.exit(f"CUT={CUT!r} is not one of {list(VARIANTS)}")
VARIANT = VARIANTS[CUT]
ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, "work", CUT)
os.makedirs(WORK, exist_ok=True)

_ins, _len = VARIANT.get("insert_after", {}), VARIANT.get("length", {})
if _ins or _len:
    _new = []
    for _s in SEGS:
        _s = (_s[0], _s[1], _s[2], _s[3], _len.get(_s[0], _s[4]), _s[5])
        _new.append(_s)
        _new.extend(_ins.get(_s[0], []))
    SEGS = _new


def timeline():
    """-> ([{id, sec, src, inn, dur, vol, start}], total_seconds)"""
    t, out = 0.0, []
    seen = set()
    for sid, sec, src, a, d, vol in SEGS:
        if sid in seen:
            sys.exit(f"duplicate segment id {sid}")
        seen.add(sid)
        if src is not None and src not in SRC:
            sys.exit(f"segment {sid}: unknown source id {src} (have {len(SRC)} files in {SRC_DIR})")
        out.append(dict(id=sid, sec=sec, src=src, inn=a, dur=d, vol=vol, start=round(t, 4)))
        t += d
    return out, round(t, 4)


if __name__ == "__main__":
    if "--sources" in sys.argv:
        for k, v in SRC.items():
            print(k, os.path.basename(v))
        sys.exit()
    tl, total = timeline()
    for s in tl:
        print(f'{s["start"]:6.2f} {s["id"]:5s} {s["sec"]:8s} {s["src"] or "--"} {s["inn"]:5.2f} +{s["dur"]:.2f}  vol {s["vol"]}')
    print(f"CUT={CUT} TOTAL {total:.2f}s")
