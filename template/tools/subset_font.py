# -*- coding: utf-8 -*-
"""Subset the primary (CJK) font to every character used by the overlay, across all variants (+ ASCII).
Characters accumulate in work/chars.txt, so building one cut never drops glyphs another cut needs.
Usage: python tools/subset_font.py   (run after build_overlay.py; needs `pip install fonttools`)"""
import html, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import content as C

src = os.path.join(ROOT, "assets", "fonts", C.FONT_MAIN[1])
dst = os.path.join(ROOT, "assets", "fonts", os.path.splitext(C.FONT_MAIN[1])[0] + "-sub.ttf")
chars = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz！？，。：（）「」・—–-/&'.,!?:() ")
store = os.path.join(ROOT, "work", "chars.txt")
if os.path.exists(store):
    chars |= set(open(store, encoding="utf-8").read())
s = open(os.path.join(ROOT, "compositions", "overlay.html"), encoding="utf-8").read()
s = re.sub(r"<style>.*?</style>|<script>.*?</script>", " ", s, flags=re.S)
chars |= set(html.unescape(re.sub(r"<[^>]+>", " ", s)))
chars.discard("\n")
open(store, "w", encoding="utf-8").write("".join(sorted(chars)))
subprocess.run([sys.executable, "-m", "fontTools.subset", src, f"--text-file={store}", f"--output-file={dst}",
                "--layout-features=*"], check=True)
print("subset", len(chars), "chars ->", os.path.basename(dst))
