# -*- coding: utf-8 -*-
"""Camera-motion + sharpness scan of every source clip -> work/shake.json, plus a one-line map per clip.

Per 0.5 s window:
  speed = median global translation between frames (phase correlation), % of frame width per second
  jerk  = mean frame-to-frame change of that motion (hand shake)
  sharp = median Laplacian variance at 540 px width (focus / motion blur)
Map legend:  .  steady   o  moving but usable   X  too fast / shaky   b  soft (blurred)
Usage: python tools/shake.py [id ...]"""
import json, os, sys
import cv2
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from edl import SRC

STEADY, USABLE, SOFT = (8, 8), (20, 15), 60      # (speed, jerk) thresholds, sharpness floor
ids = sys.argv[1:] or list(SRC)
dst = os.path.join(ROOT, "work", "shake.json")
out = json.load(open(dst)) if os.path.exists(dst) else {}
for sid in ids:
    f = SRC[sid]
    cap = cv2.VideoCapture(f)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    prev, rows, k, win = None, [], 0, None
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        h, w = g.shape
        sm = cv2.resize(g, (240, int(240 * h / w)), interpolation=cv2.INTER_AREA).astype(np.float32)
        sharp = cv2.Laplacian(cv2.resize(g, (540, int(540 * h / w))), cv2.CV_64F).var()
        if prev is not None:
            if win is None:
                win = cv2.createHanningWindow(sm.shape[::-1], cv2.CV_32F)
            (dx, dy), _ = cv2.phaseCorrelate(prev, sm, win)
            rows.append((k / fps, dx / 240 * 100 * fps, dy / 240 * 100 * fps, sharp))
        prev, k = sm, k + 1
    cap.release()
    if not rows:
        continue
    t, vx, vy, sh = (np.array(c) for c in zip(*rows))
    sp = np.hypot(vx, vy)
    wins = []
    for a in np.arange(0, t[-1], 0.5):
        m = (t >= a) & (t < a + 0.5)
        if m.sum() < 3:
            continue
        jerk = np.hypot(np.diff(vx[m]), np.diff(vy[m])).mean()
        wins.append(dict(t=round(float(a), 2), speed=round(float(np.median(sp[m])), 1),
                         jerk=round(float(jerk), 1), sharp=round(float(np.median(sh[m])), 0)))
    out[sid] = dict(file=os.path.basename(f), fps=round(fps, 2), dur=round(k / fps, 2), wins=wins)

    def mark(w):
        c = "." if w["speed"] < STEADY[0] and w["jerk"] < STEADY[1] else "o" if w["speed"] < USABLE[0] and w["jerk"] < USABLE[1] else "X"
        return c + ("" if w["sharp"] > SOFT else "b")
    print(f"{sid} {os.path.basename(f)} {k / fps:5.1f}s | {' '.join(mark(w) for w in wins)}", flush=True)
json.dump(out, open(dst, "w"), indent=0)
print("->", dst)
