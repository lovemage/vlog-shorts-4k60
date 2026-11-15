# -*- coding: utf-8 -*-
"""Download the default fonts (SIL Open Font License) from the google/fonts repo into assets/fonts/.
Noto Sans TC (variable weight) for Traditional Chinese, Kanit for Latin + Thai.
Swap for your languages: Noto Sans SC / JP / KR, or another script font, then edit content.py.
Usage: python tools/get_fonts.py"""
import os, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FILES = {
    "NotoSansTC.ttf": "notosanstc/NotoSansTC%5Bwght%5D.ttf",
    "Kanit-SemiBold.ttf": "kanit/Kanit-SemiBold.ttf",
    "Kanit-Bold.ttf": "kanit/Kanit-Bold.ttf",
    "Kanit-Black.ttf": "kanit/Kanit-Black.ttf",
}
d = os.path.join(ROOT, "assets", "fonts")
os.makedirs(d, exist_ok=True)
for name, path in FILES.items():
    dst = os.path.join(d, name)
    if os.path.exists(dst):
        print("kept", name); continue
    urllib.request.urlretrieve(BASE + path, dst + ".part")
    os.replace(dst + ".part", dst)
    print("saved", name, os.path.getsize(dst) // 1024, "KB")
