# -*- coding: utf-8 -*-
"""One-click dual-language builder template for Mode B (POV Comic)."""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.environ.get("POV_SKILL_SCRIPTS", os.path.join(HERE, "scripts"))
PY = sys.executable


def run(cmd):
    print(">>>", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=HERE, check=True)


def build_one(lang, skip_vo=False, ep_name="episode"):
    if not skip_vo: run([PY, "vo.py", "--lang", lang])
    run([PY, "layout.py", "--lang", lang])
    os.makedirs(os.path.join(HERE, "work", lang), exist_ok=True)
    run([PY, "assemble.py", "--lang", lang])
    run(["node", "render_overlay.js", "--lang", lang])
    run([PY, "assemble.py", "--lang", lang, "--final"])
    run([PY, "sound.py", "--lang", lang])
    out_mp4 = os.path.join(HERE, f"{ep_name}_{lang}.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", f"work/{lang}/video.mp4", "-i", f"audio/{lang}/mix.wav",
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out_mp4])
    print(f"DONE: {out_mp4}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="th")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--skip-vo", action="store_true")
    ap.add_argument("--skip-validate", action="store_true")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--shot")
    ap.add_argument("--to", dest="to_shot")
    args = ap.parse_args()
    langs = ["th", "en"] if args.all else [args.lang]
    if args.validate_only or not args.skip_validate:
        run([PY, os.path.join(SCRIPTS, "validate.py"), HERE, "--lang", ",".join(langs)])
        if args.validate_only: sys.exit(0)
    if args.shot:
        cmd = [PY, os.path.join(SCRIPTS, "preview_shot.py"), HERE, "--shot", args.shot, "--lang", langs[0]]
        if args.to_shot: cmd += ["--to", args.to_shot]
        run(cmd); sys.exit(0)
    for lg in langs: build_one(lg, skip_vo=args.skip_vo)
