# -*- coding: utf-8 -*-
"""Narration in your own cloned voice (fal.ai MiniMax speech) -- optional.

Voices every line in vo/script.json, trims edge silence and loudness-matches it to on-camera dialogue
(~-17 LUFS), then writes vo/timeline.json (line id -> file + duration) for build_overlay.py and mix.py.
Lines are cached by (voice, text, speed), so re-running only voices changed lines.

Env: VOICE_ID   your MiniMax custom voice id (clone it once on fal.ai; keep it out of git)
     VOICE_SPEED default 1.2     VOICE_LANG  language_boost, default "Chinese"
Usage: VOICE_ID=... python tools/make_vo.py"""
import hashlib, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_ID = os.environ.get("VOICE_ID") or sys.exit("set VOICE_ID (your fal.ai MiniMax voice id)")
SPEED = float(os.environ.get("VOICE_SPEED", "1.2"))
LANG = os.environ.get("VOICE_LANG", "Chinese")


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip())


def tts(text):
    h = hashlib.md5(("%s|%s|%.2f" % (VOICE_ID, text, SPEED)).encode()).hexdigest()[:12]
    p = os.path.join(ROOT, "vo", "cache", h + ".mp3")
    if not os.path.exists(p):
        import fal
        r = fal.run("fal-ai/minimax/speech-2.8-hd", {
            "prompt": text,
            "voice_setting": {"voice_id": VOICE_ID, "speed": SPEED, "vol": 1.0, "pitch": 0},
            "language_boost": LANG,
            "audio_setting": {"format": "mp3", "sample_rate": 44100, "channel": 1, "bitrate": 128000},
            "normalization_setting": {"enabled": True, "target_loudness": -18.0},
            "output_format": "url"})
        fal.fetch(r["audio"]["url"], p)
    return p


def one(line):
    say = line.get("say") or line["sub"][0].replace("|", "")
    src = tts(say)
    norm = os.path.join(ROOT, "vo", "norm", line["id"] + ".wav")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-af",
                    "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                    "loudnorm=I=-17:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "1", norm], check=True)
    return line["id"], {"file": os.path.relpath(norm, ROOT).replace(os.sep, "/"), "dur": round(dur(norm), 3), "say": say}


lines = json.load(open(os.path.join(ROOT, "vo", "script.json"), encoding="utf-8"))
os.makedirs(os.path.join(ROOT, "vo", "cache"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "vo", "norm"), exist_ok=True)
with ThreadPoolExecutor(4) as ex:
    out = dict(ex.map(one, lines))
for k, v in out.items():
    print("%-5s %.2fs  %s" % (k, v["dur"], v["say"]))
json.dump(out, open(os.path.join(ROOT, "vo", "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total narration %.1fs" % sum(v["dur"] for v in out.values()))
