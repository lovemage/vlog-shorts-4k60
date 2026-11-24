# -*- coding: utf-8 -*-
"""Pre-flight validator & environment doctor for vlog-shorts-4k60 (Mode B: POV Comic)."""
import argparse, ast, json, os, re, shutil, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CAMERA_BRANDING_RE = re.compile(r"\bshot\s+on\s+\w+", re.IGNORECASE)


class Report:
    def __init__(self):
        self.ok, self.warn, self.err = [], [], []
    def add_ok(self, m): self.ok.append(m)
    def add_warn(self, m): self.warn.append(m)
    def add_err(self, m): self.err.append(m)
    def print_summary(self, title):
        print(f"\n=== {title} ===")
        for m in self.ok: print(f"  [OK]   {m}")
        for m in self.warn: print(f"  [WARN] {m}")
        for m in self.err: print(f"  [ERR]  {m}")
        print(f"--- Summary: {len(self.ok)} ok, {len(self.warn)} warn, {len(self.err)} err ---")


def run_doctor():
    rep = Report()
    for bin_name in ("ffmpeg", "ffprobe", "node", "python"):
        (rep.add_ok if shutil.which(bin_name) else rep.add_err)(f"binary {'found' if shutil.which(bin_name) else 'missing'}: {bin_name}")
    env_file = os.environ.get("ENV_FILE")
    if env_file and os.path.exists(env_file):
        rep.add_ok("ENV_FILE exists (contents not inspected)")
    elif os.environ.get("FAL_KEY"):
        rep.add_ok("FAL_KEY environment variable is set")
    else:
        rep.add_warn("Neither ENV_FILE nor FAL_KEY is set (optional unless running fal.ai TTS)")
    rep.print_summary("Environment Doctor")
    return rep


def _ast_extract_assignments(py_path, names):
    with open(py_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=py_path)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in names:
                    try: out[t.id] = ast.literal_eval(node.value)
                    except Exception: pass
    return out


def check_lines(ep_dir, langs, rep, banned_words=None):
    p = os.path.join(ep_dir, "audio", "lines.json")
    if not os.path.exists(p):
        rep.add_err("audio/lines.json missing"); return None
    cfg = json.load(open(p, encoding="utf-8"))
    voices, lines = cfg.get("voices", {}), cfg.get("lines", [])
    if not lines: rep.add_err("audio/lines.json has no lines"); return cfg
    seen, missing = set(), {lg: [] for lg in langs}
    for i, ln in enumerate(lines):
        lid, who = ln.get("id"), ln.get("who")
        if not lid or lid in seen: rep.add_err(f"invalid/duplicate line id at index {i}: {lid}")
        else: seen.add(lid)
        if who not in voices: rep.add_err(f"line '{lid}' speaker '{who}' not in voices")
        for lg in langs:
            if not (ln.get(lg) or "").strip(): missing[lg].append(lid)
            for bw in (banned_words or []):
                if bw and bw in (ln.get(lg) or ""):
                    rep.add_err(f"line '{lid}' [{lg}] contains banned word '{bw}'")
    for lg, ids in missing.items():
        if ids: rep.add_err(f"lines missing '{lg}' text: {', '.join(ids)}")
    rep.add_ok(f"audio/lines.json: {len(lines)} lines, {len(voices)} voices checked")
    return cfg


def check_h3_queue(ep_dir, rep):
    p = os.path.join(ep_dir, "h3", "queue.py")
    if not os.path.exists(p): rep.add_warn("h3/queue.py not found (skipping H3 checks)"); return
    data = _ast_extract_assignments(p, {"STY", "END", "SHOTS"})
    shots = data.get("SHOTS")
    if not isinstance(shots, dict): rep.add_warn("h3/queue.py: could not parse SHOTS"); return
    comb = (str(data.get("STY", "")) + " " + str(data.get("END", ""))).lower()
    if not all(k in comb for k in ("no speech", "no music", "no text")):
        rep.add_warn("h3/queue.py STY/END missing 'No speech / no music / no text' negative lock")
    bad_f, miss_in, miss_out, miss_beats = [], [], [], []
    for k, spec in shots.items():
        L, first, last, text = spec[0], spec[1], spec[2], str(spec[3])
        if not isinstance(L, int) or L < 22 or (L - 5) % 17 != 0: bad_f.append(f"{k}={L}")
        if first and not os.path.exists(os.path.join(ep_dir, "h3", "in", first)): miss_in.append(f"{k}:{first}")
        if last and not os.path.exists(os.path.join(ep_dir, "h3", "in", last)): miss_in.append(f"{k}:{last}")
        if not os.path.exists(os.path.join(ep_dir, "h3", "out", f"{k}.mp4")): miss_out.append(k)
        if isinstance(L, int) and L >= 175 and not re.search(r"\d+\s*[-–]\s*\d+\s*s", text, re.IGNORECASE):
            miss_beats.append(f"{k} ({L}f/{L/24:.1f}s)")
    if bad_f: rep.add_err(f"h3/queue.py violates 17n+5 rule: {', '.join(bad_f)}")
    else: rep.add_ok(f"h3/queue.py: all {len(shots)} shots pass 17n+5 frame rule")
    if miss_in: rep.add_warn(f"h3/in missing frames: {', '.join(miss_in)}")
    if miss_out: rep.add_warn(f"h3/out clips missing ({len(miss_out)}/{len(shots)}): {', '.join(miss_out)}")
    else: rep.add_ok(f"h3/out: all {len(shots)} clips present")
    if miss_beats: rep.add_warn(f"h3/queue.py long clips (>=7.3s) without per-second beats: {', '.join(miss_beats)}")


def check_assemble_and_timeline(ep_dir, langs, rep):
    asm = os.path.join(ep_dir, "assemble.py")
    plan = _ast_extract_assignments(asm, {"PLAN"}).get("PLAN") if os.path.exists(asm) else None
    if isinstance(plan, list):
        miss = []
        for slot, kind, src, opts in plan:
            if kind == "still" and src and not os.path.exists(os.path.join(ep_dir, "stills_src", src)): miss.append(f"{slot}:stills_src/{src}")
            elif kind == "clip" and src:
                if not os.path.exists(os.path.join(ep_dir, "h3", "out", src)): miss.append(f"{slot}:h3/out/{src}")
                if isinstance(opts, dict) and opts.get("lead_still") and not os.path.exists(os.path.join(ep_dir, "stills_src", opts["lead_still"][0])):
                    miss.append(f"{slot}:stills_src/{opts['lead_still'][0]}")
        if miss: rep.add_warn(f"assemble.py PLAN missing assets: {', '.join(miss)}")
        else: rep.add_ok(f"assemble.py PLAN: all {len(plan)} slots have required assets")
    for lg in langs:
        tl_p = os.path.join(ep_dir, "audio", lg, "timeline.json")
        if not os.path.exists(tl_p): rep.add_warn(f"audio/{lg}/timeline.json not generated yet"); continue
        tl = json.load(open(tl_p, encoding="utf-8"))
        dur, marks = tl.get("duration", 0), tl.get("marks", {})
        if dur < 60 or dur > 105: rep.add_warn(f"[{lg}] timeline {dur:.2f}s outside typical 60-105s range")
        else: rep.add_ok(f"[{lg}] timeline.json: {dur:.2f}s, {len(tl.get('lines', []))} lines, {len(marks)} marks")
        if isinstance(plan, list):
            mm = [p[0] for p in plan if p[0] not in marks] + (["end"] if "end" not in marks else [])
            if mm: rep.add_err(f"[{lg}] timeline.json missing marks: {', '.join(mm)}")


def check_captions(ep_dir, rep):
    for fn in ("caption.txt", "caption_en.txt"):
        p = os.path.join(ep_dir, fn)
        if not os.path.exists(p): continue
        txt = open(p, encoding="utf-8").read()
        if CAMERA_BRANDING_RE.search(txt): rep.add_err(f"{fn} contains forbidden camera branding ('Shot on ...')")
        rep.add_ok(f"{fn} checked ({len(txt)} chars)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep_dir", nargs="?")
    ap.add_argument("--doctor", action="store_true")
    ap.add_argument("--lang", default="th,en")
    ap.add_argument("--ban", default="")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    failed = False
    if args.doctor or not args.ep_dir:
        r = run_doctor()
        failed = failed or bool(r.err or (args.strict and r.warn))
    if args.ep_dir:
        langs = [x.strip() for x in args.lang.split(",") if x.strip()]
        banned = [x.strip() for x in args.ban.split(",") if x.strip()]
        r = Report()
        d = os.path.abspath(args.ep_dir)
        if not os.path.isdir(d): r.add_err(f"folder not found: {d}")
        else:
            check_lines(d, langs, r, banned)
            check_h3_queue(d, r)
            check_assemble_and_timeline(d, langs, r)
            check_captions(d, r)
        r.print_summary(f"Validate {os.path.basename(d)} ({','.join(langs)})")
        failed = failed or bool(r.err or (args.strict and r.warn))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
