# -*- coding: utf-8 -*-
"""Audio mix from edl.py -> work/<CUT>/mix.wav (48 kHz, 24-bit, loudness-matched).

buses
  dialogue  (segments with volume >= 1, AUDIO events, narration)  -> EQ + compressor, keys the BGM ducking
  ambience  (segments with 0 < volume < 1)                         -> low bed under the music
  sfx       whoosh on every section change, soft pop on every local-info tag
  bgm       starts at BGM_IN so the track's natural ending lands on the last frame; sidechain-ducked by dialogue
loudness    two-pass loudnorm to TARGET_LUFS / -1 dBTP + limiter.
            Match TARGET_LUFS to the loudest Short already on your channel, so videos don't jump in volume.
Usage: [CUT=tiktok] python tools/mix.py"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from edl import timeline, SRC, AUDIO, WORK

# ---------------------------------------------------------------- settings
BGM = os.path.join(ROOT, "assets", "music", "bgm.wav")
BGM_IN = 0.0          # seconds into the music file where the cut starts (pick it so the ending lines up)
BGM_VOL = 0.55
TARGET_LUFS = -14.0   # YouTube reference level; louder channels often sit around -13 .. -12.5
WHOOSH = (os.path.join(ROOT, "assets", "sfx", "whoosh.wav"), 0.55)
POP = (os.path.join(ROOT, "assets", "sfx", "pop.wav"), 0.315)

tl, TOTAL = timeline()
SEG = {s["id"]: s for s in tl}

events = []  # (path, in, dur, at, volume, bus)
for s in tl:
    if s["src"] and s["vol"] > 0:
        events.append((SRC[s["src"]], s["inn"], s["dur"], s["start"], s["vol"], "dlg" if s["vol"] >= 1 else "amb"))
for src, a, d, seg, off, v in AUDIO:
    if seg in SEG:
        events.append((SRC[src], a, d, SEG[seg]["start"] + off, v, "dlg"))

vs_p, vt_p = os.path.join(ROOT, "vo", "script.json"), os.path.join(ROOT, "vo", "timeline.json")
if os.path.exists(vs_p) and os.path.exists(vt_p):
    VT = json.load(open(vt_p, encoding="utf-8"))
    for l in json.load(open(vs_p, encoding="utf-8")):
        if l["seg"] in SEG and l["id"] in VT:
            events.append((os.path.join(ROOT, VT[l["id"]]["file"]), 0.0, VT[l["id"]]["dur"], SEG[l["seg"]]["start"] + l["off"], 1.0, "dlg"))

cues_p = os.path.join(WORK, "overlay_cues.json")
cues = json.load(open(cues_p, encoding="utf-8")) if os.path.exists(cues_p) else {"tags": []}
sections, prev = [], None
for s in tl:
    if prev is not None and s["sec"] != prev:
        sections.append(s["start"])
    prev = s["sec"]
sfx = []
if os.path.exists(WHOOSH[0]):
    sfx += [(WHOOSH[0], max(0.0, t - 0.18), WHOOSH[1]) for t in sections]
if os.path.exists(POP[0]):
    sfx += [(POP[0], t[0], POP[1]) for t in cues["tags"]]

args, fc, buses, k = ["ffmpeg", "-v", "error", "-y"], [], {"dlg": [], "amb": [], "fx": []}, 0
for path, a, d, at, v, bus in events:
    args += ["-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", path]
    ms = int(round(at * 1000))
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},"
              f"afade=t=in:d=0.03,afade=t=out:st={max(0, d - 0.04):.3f}:d=0.04,adelay={ms}|{ms}[e{k}]")
    buses[bus].append(f"[e{k}]"); k += 1
for path, at, v in sfx:
    args += ["-i", path]
    ms = int(round(at * 1000))
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={ms}|{ms}[e{k}]")
    buses["fx"].append(f"[e{k}]"); k += 1

SIL = f"anullsrc=r=48000:cl=stereo,atrim=0:{TOTAL:.3f}"


def bus(name, chain=""):
    ins = buses[name]
    if not ins:
        fc.append(f"{SIL}[{name}]")
        return
    fc.append(f"{''.join(ins)}amix=inputs={len(ins)}:normalize=0{chain},apad,atrim=0:{TOTAL:.3f}[{name}]")


bus("dlg", ",highpass=f=90,equalizer=f=3000:t=q:w=1.2:g=3,acompressor=threshold=0.08:ratio=3.5:attack=5:release=120,volume=2.3")
fc.append("[dlg]asplit=2[dlgA][dlgK]")
bus("amb")
bus("fx")
outs = ["[dlgA]", "[amb]", "[fx]"]
if os.path.exists(BGM):
    args += ["-ss", f"{BGM_IN}", "-t", f"{TOTAL:.3f}", "-i", BGM]
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={BGM_VOL},afade=t=in:d=0.25,"
              f"afade=t=out:st={max(0, TOTAL - 1.2):.3f}:d=1.2,apad,atrim=0:{TOTAL:.3f}[bgm0]")
    fc.append("[bgm0][dlgK]sidechaincompress=threshold=0.02:ratio=12:attack=30:release=500:makeup=1[bgm]")
    outs.append("[bgm]")
else:
    print("  ! no assets/music/bgm.wav -- mixing without music")
    fc.append("[dlgK]anullsink")
fc.append(f"{''.join(outs)}amix=inputs={len(outs)}:normalize=0,atrim=0:{TOTAL:.3f},aresample=48000[out]")
pre = os.path.join(WORK, "mix_pre.wav")
args += ["-filter_complex", ";".join(fc), "-map", "[out]", "-c:a", "pcm_f32le", "-ar", "48000", pre]
subprocess.run(args, check=True)

# pass 2: measured loudnorm, then a true-peak limiter
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af",
                    f"loudnorm=I={TARGET_LUFS}:TP=-1.0:LRA=7:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
mj = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = (f"loudnorm=I={TARGET_LUFS}:TP=-1.0:LRA=7:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
      f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true,"
      "aresample=48000,alimiter=limit=0.89:level=false")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af", af, "-c:a", "pcm_s24le", "-ar", "48000",
                os.path.join(WORK, "mix.wav")], check=True)
print(f"mix done: {len(events)} events, {len(sfx)} sfx, sections at {[round(x, 2) for x in sections]}")
