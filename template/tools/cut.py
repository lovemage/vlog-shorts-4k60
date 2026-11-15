# -*- coding: utf-8 -*-
"""Cut every EDL segment straight from the ORIGINAL camera files -> work/<CUT>/footage.mp4 (video only).

Footage never passes through the browser. Per segment:
  fps -> OUT_FPS, scale to cover OUT_W x OUT_H (lanczos, accurate rounding, full chroma), centre crop,
  light luma-only unsharp, x264 CRF 12 intermediate.
Segments are cached in work/seg/ by (source, in-point, frame count) and shared by all variants.
Usage: [CUT=tiktok] python tools/cut.py"""
import hashlib, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from edl import timeline, SRC, WORK, OUT_W as W, OUT_H as H, OUT_FPS as FPS

SEG_DIR = os.path.join(ROOT, "work", "seg")
os.makedirs(SEG_DIR, exist_ok=True)
tl, total = timeline()
VF = (f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos+accurate_rnd+full_chroma_int,"
      f"crop={W}:{H},unsharp=5:5:0.45:5:5:0.0,setsar=1,format=yuv420p")
# HDR phone footage (iPhone HLG, Android HDR10) -> SDR bt709 before scaling, or it looks grey and washed out
TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p10le,")
HDR_TRC = ("arib-std-b67", "smpte2084")
ENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "12", "-profile:v", "high", "-r", str(FPS), "-an",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]


def probe(path, entries, stream="v:0"):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", entries,
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return r.stdout.strip()


def src_dur(path):
    return float(probe(path, "format=duration") or 0)


def vf_for(path):
    return (TONEMAP + VF) if probe(path, "stream=color_transfer") in HDR_TRC else VF


# fail early: an in-point + duration past the end of a source would silently shorten the whole cut
bad = [f'{s["id"]}: src {s["src"]} is {d:.2f}s, segment wants {s["inn"]:.2f}+{s["dur"]:.2f}'
       for s in tl if s["src"] for d in [src_dur(SRC[s["src"]])] if s["inn"] + s["dur"] > d - 0.02]
if bad:
    sys.exit("segments run past the end of their source:\n  " + "\n  ".join(bad))
for sid in sorted({s["src"] for s in tl if s["src"]}):
    if probe(SRC[sid], "stream=color_transfer") in HDR_TRC:
        print(f"  HDR source {sid} -> tone-mapped to SDR bt709")


def one(s):
    n = round(s["dur"] * FPS)
    name = os.path.splitext(os.path.basename(SRC[s["src"]]))[0] if s["src"] else "black"
    vf = vf_for(SRC[s["src"]]) if s["src"] else "black"
    tag = hashlib.md5(f"{vf}|{ENC}".encode()).hexdigest()[:8]   # editing VF/ENC invalidates the cache
    dst = os.path.join(SEG_DIR, f'{name}_{s["inn"]:.2f}_{n}_{W}x{H}_{tag}.mp4')
    s["file"] = dst
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return s["id"], n, "cached"
    if s["src"] is None:
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}",
               "-frames:v", str(n), "-vf", "format=yuv420p", *ENC, dst + ".part.mp4"]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f'{s["inn"]:.3f}', "-i", SRC[s["src"]],
               "-frames:v", str(n), "-vf", vf, *ENC, dst + ".part.mp4"]
    subprocess.run(cmd, check=True)
    got = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                              "stream=nb_read_frames", "-of", "csv=p=0", dst + ".part.mp4"], capture_output=True, text=True).stdout.strip() or 0)
    if got != n:
        sys.exit(f'{s["id"]}: expected {n} frames, got {got}')
    os.replace(dst + ".part.mp4", dst)
    return s["id"], n, "cut"


with ThreadPoolExecutor(4) as ex:
    for sid, n, how in ex.map(one, tl):
        print(how, sid, n, flush=True)
lst = os.path.join(WORK, "concat.txt")
with open(lst, "w", encoding="utf-8") as f:
    f.write("".join("file '%s'\n" % s["file"].replace(os.sep, "/") for s in tl))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                os.path.join(WORK, "footage.mp4")], check=True)
print("footage frames", sum(round(s["dur"] * FPS) for s in tl), "->", os.path.join(WORK, "footage.mp4"))
