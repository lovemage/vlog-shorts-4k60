# -*- coding: utf-8 -*-
"""Everything the viewer READS: hook title, subtitles, local-info tags, sticker, end card.
tools/build_overlay.py turns this into the transparent HyperFrames graphics layer.

Every visible text is a tuple of up to 3 lines, rendered as
  l1 = primary language (big, white)   l2 = second language (yellow)   l3 = third language (pink)
Use "|" inside l1 to force a line break point (CJK text does not wrap nicely on its own).
Positions are anchored to EDL segment ids, so retiming the cut never breaks the captions.
"""

# ------------------------------------------------------------------ fonts & colours
# Files live in assets/fonts/. FONT_MAIN is subset by tools/subset_font.py (CJK fonts are huge).
FONT_MAIN = ("Noto Sans TC", "NotoSansTC.ttf")            # l1: primary language (variable weight)
FONT_ALT = [                                               # l2/l3: Latin + local script
    ("Kanit", "Kanit-SemiBold.ttf", "500 600"),
    ("Kanit", "Kanit-Bold.ttf", "700 800"),
    ("Kanit", "Kanit-Black.ttf", "900"),
]
COLORS = {"yel": "#ffd21f", "pink": "#ff4fa0", "ink": "#170c14", "card": "rgba(23,12,20,.84)", "l3": "#ffc6de"}
LANG = "zh-Hant"

# ------------------------------------------------------------------ hook title (over the first segments)
HOOK = {
    "until": "i1",                                   # hook ends where this segment starts
    "pill": "清邁一年一度的市集",
    "big": "ปลายฝน ต้นหนาว",                          # local-language headline
    "main": "雨季尾・冬季初",
    "small": "LATE RAIN · EARLY WINTER FAIR 2026",
    "sticker": ("只有 9 天", "9 DAYS", "NOV 9 – 17"),  # round sticker, or None
}

# ------------------------------------------------------------------ on-camera speech subtitles
# (segment, offset, duration, (l1, l2, l3))
SUBS = [
    ("i1", 0.08, 3.70, ("今天來到清邁一年一度的活動", "Today: Chiang Mai's once-a-year fair", "วันนี้มางานประจำปีของเชียงใหม่")),
]

# ------------------------------------------------------------------ local-info tags (top-left cards)
# (from_segment, to_segment, kind, (l1, l2, l3), note (l1, l2, l3) or None)
KINDS = {"pin": "LOCATION", "food": "在地小吃 LOCAL FOOD", "zone": "現場 ON SITE", "bonus": "彩蛋 BONUS"}
TAGS = [
    ("f1", "f1", "food", ("泰式烤蛋", "Kai Ping · grilled eggs", "ไข่ปิ้ง"),
     ("蛋液調味後倒回蛋殼，串起來烤", "beaten, seasoned, poured back into the shell", "ตีไข่ปรุงรส ใส่กลับในเปลือกแล้วปิ้ง")),
    ("f2", "f2", "food", ("竹筒糯米飯", "Khao Lam · bamboo sticky rice", "ข้าวหลาม"), None),
]

# ------------------------------------------------------------------ date sticker (optional)
# (from_segment, to_segment, (a, b, c)) or None
DATE_STICKER = None   # e.g. ("w1", "w2", ("只到", "11/17", "NOV 9 – 17"))

# ------------------------------------------------------------------ end card (on a src=None segment)
END = {
    "seg": "e1",
    "kicker": "活動資訊 EVENT INFO",
    "title": ("雨季尾・冬季初市集", "Late Rain, Early Winter Fair", "งานปลายฝน ต้นหนาว"),
    "rows": [   # (icon: cal|pin|tix, line1, line2)
        ("cal", "2026 / 11 / 9 – 11 / 17　9 天 9 夜", "9 days & 9 nights"),
        ("pin", "清邁府行政機構公園", "Chiang Mai PAO Park · สวน อบจ.เชียงใหม่"),
        ("tix", "免費入場", "Free entry · เข้าชมฟรี"),
    ],
}
