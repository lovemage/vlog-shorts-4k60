# -*- coding: utf-8 -*-
"""Fast single-shot preview renderer (Section-Level Revision) for Mode B: POV Comic."""
import argparse, ast, json, os, shutil, subprocess, sys, tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FPS = 30


def _read_plan_order(ep_dir):
    asm = os.path.join(ep_dir, "assemble.py")
    if not os.path.exists(asm): return None
    try:
        tree = ast.parse(open(asm, encoding="utf-8").read(), filename=asm)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "PLAN":
                        return [p[0] for p in ast.literal_eval(node.value)] + ["end"]
    except Exception:
        return None
    return None


def _resolve_range(ep_dir, marks, dur, shot, to_shot=None):
    if shot not in marks: raise SystemExit(f"Shot '{shot}' not in marks: {list(marks)}")
    order = _read_plan_order(ep_dir) or sorted(marks, key=lambda k: marks[k])
    t0, end_key = marks[shot], (to_shot or shot)
    if end_key not in marks: raise SystemExit(f"End shot '{end_key}' not in marks")
    if end_key in order:
        idx = order.index(end_key)
        t1 = marks[order[idx + 1]] if idx + 1 < len(order) and order[idx + 1] in marks else dur
    else:
        later = [v for v in marks.values() if v > marks[end_key]]
        t1 = min(later) if later else dur
    return round(t0, 3), round(t1, 3)


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep_dir")
    ap.add_argument("--shot", required=True)
    ap.add_argument("--to", dest="to_shot")
    ap.add_argument("--lang", default="th")
    ap.add_argument("--no-overlay", action="store_true")
    ap.add_argument("--no-bgm", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    ep_dir, lg = os.path.abspath(args.ep_dir), args.lang
    tl = json.load(open(os.path.join(ep_dir, "audio", lg, "timeline.json"), encoding="utf-8"))
    t0, t1 = _resolve_range(ep_dir, tl["marks"], tl["duration"], args.shot, args.to_shot)
    dur = round(t1 - t0, 3)
    tag = f"{args.shot}_{args.to_shot}" if args.to_shot else args.shot

    work_dir = os.path.join(ep_dir, "work", lg)
    prev_dir = tempfile.mkdtemp(prefix=f"pov_preview_{tag}_")
    seg_mp4, seg_wav = os.path.join(work_dir, "seg", f"{args.shot}.mp4"), os.path.join(work_dir, "seg", f"{args.shot}.wav")
    base_mp4, amb_wav = os.path.join(work_dir, "base.mp4"), os.path.join(work_dir, "h3_amb.wav")
    vid_src, amb_src = os.path.join(prev_dir, "base.mp4"), os.path.join(prev_dir, "amb.wav")

    if not args.to_shot and os.path.exists(seg_mp4):
        shutil.copy2(seg_mp4, vid_src)
        if os.path.exists(seg_wav): shutil.copy2(seg_wav, amb_src)
        else: run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo", amb_src], ep_dir)
    elif os.path.exists(base_mp4):
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(t0), "-t", str(dur), "-i", base_mp4, "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), vid_src], ep_dir)
        if os.path.exists(amb_wav): run(["ffmpeg", "-y", "-v", "error", "-ss", str(t0), "-t", str(dur), "-i", amb_wav, "-ac", "2", "-ar", "48000", amb_src], ep_dir)
        else: run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo", amb_src], ep_dir)
    else:
        raise SystemExit(f"Missing {seg_mp4} and {base_mp4}. Run assemble.py --lang {lg} first.")

    vid_ready = vid_src
    if not args.no_overlay and os.path.exists(os.path.join(ep_dir, "render_overlay.js")):
        ovl_dir = os.path.join(prev_dir, "ovl")
        run(["node", "render_overlay.js", "--lang", lg, "--from", str(t0), "--to", str(t1), "--out", ovl_dir], ep_dir)
        vid_ovl = os.path.join(prev_dir, "video_ovl.mp4")
        run(["ffmpeg", "-y", "-v", "error", "-i", vid_src, "-framerate", str(FPS), "-i", os.path.join(ovl_dir, "f%05d.png"),
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]",
             "-map", "[v]", "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), vid_ovl], ep_dir)
        vid_ready = vid_ovl

    vo_lines = [ln for ln in tl.get("lines", []) if ln["t"] + ln["d"] > t0 and ln["t"] < t1]
    inputs, filters, mix_labels, idx = ["-i", amb_src], ["[0:a]volume=0.35[a0]"], ["[a0]"], 1
    bgm_wav = os.path.join(work_dir, "bgm.wav")
    if not args.no_bgm and os.path.exists(bgm_wav):
        inputs += ["-ss", str(t0), "-t", str(dur), "-i", bgm_wav]
        filters.append(f"[{idx}:a]volume=0.35[a{idx}]"); mix_labels.append(f"[a{idx}]"); idx += 1
    for ln in vo_lines:
        vp = os.path.join(ep_dir, "audio", lg, "vo_proc", f"{ln['id']}.wav")
        if not os.path.exists(vp): continue
        delay_ms, trim_s = max(0, int(round((ln["t"] - t0) * 1000))), max(0.0, round(t0 - ln["t"], 3))
        inputs += ["-ss", str(trim_s), "-i", vp]
        filters.append(f"[{idx}:a]aformat=channel_layouts=stereo:sample_rates=48000,adelay={delay_ms}|{delay_ms},volume=1.0[a{idx}]")
        mix_labels.append(f"[a{idx}]"); idx += 1

    mix_wav = os.path.join(prev_dir, "mix.wav")
    fc = ";".join(filters) + ";" + "".join(mix_labels) + f"amix=inputs={len(mix_labels)}:duration=first:normalize=0,atrim=duration={dur}[aout]"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[aout]", "-ar", "48000", "-ac", "2", mix_wav], ep_dir)

    out_mp4 = os.path.abspath(args.out) if args.out else os.path.join(work_dir, f"preview_{tag}.mp4")
    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)
    run(["ffmpeg", "-y", "-v", "error", "-i", vid_ready, "-i", mix_wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_mp4], ep_dir)
    shutil.rmtree(prev_dir, ignore_errors=True)
    print(f"PREVIEW DONE [{lg}]: {out_mp4}  ({t0:.2f}s -> {t1:.2f}s, {dur:.2f}s)")


if __name__ == "__main__":
    main()
