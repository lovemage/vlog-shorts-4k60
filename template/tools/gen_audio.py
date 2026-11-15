# -*- coding: utf-8 -*-
"""Instrumental BGM + SFX via fal.ai stable-audio 2.5 -> assets/music/bgm.wav, assets/sfx/{pop,whoosh}.wav.
Edit BGM_PROMPT for the place/mood (mention regional instruments, bpm, "instrumental only, no vocals",
"steady beat from the first second, clean ending"). Existing files are kept; delete one to regenerate.
Usage: python tools/gen_audio.py"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fal
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BGM_PROMPT = ("Bright festive Northern Thai Lanna fair music, plucked salo and phin melody with a modern pop groove, "
              "tight drums with claps, warm bass, small gongs and hand percussion, 108 bpm, happy evening festival mood, "
              "instrumental only, no vocals, steady beat from the first second, clean ending")
JOBS = [
    ("music/bgm.wav", 95, 5101, BGM_PROMPT),
    ("sfx/pop.wav", 2, 52, "single short soft bubble pop sound effect, clean, no music"),
    ("sfx/whoosh.wav", 2, 53, "single fast swoosh whoosh transition sound effect, short airy, no music"),
]


def one(j):
    rel, secs, seed, prompt = j
    dst = os.path.join(ROOT, "assets", rel)
    if os.path.exists(dst):
        return rel + " (kept)"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    r = fal.run("fal-ai/stable-audio-25/text-to-audio", {"prompt": prompt, "seconds_total": secs, "seed": seed})
    url = (r.get("audio_file") or r.get("audio") or {}).get("url")
    fal.fetch(url, dst + ".part")
    os.replace(dst + ".part", dst)
    return rel


with ThreadPoolExecutor(3) as ex:
    for x in ex.map(one, JOBS):
        print("saved", x, flush=True)
