# -*- coding: utf-8 -*-
"""Composite: ffmpeg 4K footage + HyperFrames graphics layer (ProRes 4444 alpha) + mix -> delivery MP4.
Graphics go on AFTER the footage sharpening, so text is never sharpened, scaled down twice or re-softened.
Usage: [CUT=tiktok] python tools/final.py"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from edl import WORK, VARIANT, OUT_W as W, OUT_H as H, OUT_FPS as FPS

out = os.path.join(ROOT, "renders", VARIANT["file"])
os.makedirs(os.path.dirname(out), exist_ok=True)
gop = FPS * 2
cmd = ["ffmpeg", "-v", "error", "-stats", "-y",
       "-i", os.path.join(WORK, "footage.mp4"), "-i", os.path.join(WORK, "overlay.mov"), "-i", os.path.join(WORK, "mix.wav"),
       "-filter_complex",
       f"[1:v]fps={FPS},scale={W}:{H}:flags=lanczos,format=yuva444p[o];"
       "[0:v]format=yuv444p[f];[f][o]overlay=format=yuv444:shortest=1,format=yuv420p,setsar=1[v]",
       "-map", "[v]", "-map", "2:a",
       "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high", "-level:v", "5.2",
       "-x264-params", f"keyint={gop}:min-keyint={FPS}",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out]
subprocess.run(cmd, check=True)
print("wrote", out)
