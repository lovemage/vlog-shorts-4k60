# -*- coding: utf-8 -*-
"""1080x1920 preview proxy (footage + mix) for HyperFrames Studio -> assets/preview/footage_proxy_<CUT>.mp4.
Only for previewing timing in Studio; the delivery render never uses it.
Usage: [CUT=tiktok] python tools/proxy.py"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from edl import WORK, CUT, OUT_FPS

dst = os.path.join(ROOT, "assets", "preview", f"footage_proxy_{CUT}.mp4")
os.makedirs(os.path.dirname(dst), exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(WORK, "footage.mp4"), "-i", os.path.join(WORK, "mix.wav"),
                "-map", "0:v", "-map", "1:a", "-vf", "scale=1080:1920:flags=lanczos", "-r", str(OUT_FPS),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-g", str(OUT_FPS),
                "-c:a", "aac", "-b:a", "160k", "-shortest", dst], check=True)
print("wrote", dst)
