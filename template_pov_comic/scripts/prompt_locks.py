# -*- coding: utf-8 -*-
"""Production Locks & Prompt Builder for 2D ink-line POV animations (Flow / MiniMax H3)."""
import argparse, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

STYLE_LOCK_CORE = "2D ink-line comic animation, bold black ink outlines, flat cel colours, halftone dot shading"
POV_HANDS_LOCK = "first-person POV of a protagonist whose striped sleeves and hands appear at the bottom edge"
RULE_LOCKS = "Nobody smiles, deadpan serious expressions only, consistent outfits matching the first frame"
H3_ANTI_DRIFT_LOCK = "Keep exact art style, character faces, hair and outfits from the first frame; small gentle camera movement only, no sudden close-ups in the final 3 seconds."
H3_NEGATIVE_AUDIO_TEXT = "No speech, no voices, no singing, no music, no text, no subtitles, no writing on any screen."


def valid_h3_frames(seconds: float, fps: int = 24) -> int:
    target = max(22, int(round(seconds * fps)))
    n = max(1, round((target - 5) / 17))
    return 17 * n + 5


def build_h3_prompt(scene, beats=None, extra_locks="", sound="", camera="", pov_hands=True):
    parts = [STYLE_LOCK_CORE, "exactly the art style, characters and location of the first frame"]
    if pov_hands: parts.append(POV_HANDS_LOCK)
    chunks = [", ".join(parts) + ". " + RULE_LOCKS + (f"; {extra_locks.strip()}" if extra_locks else "") + "."]
    chunks.append(scene.strip().rstrip(".") + ".")
    if beats: chunks.append(" ".join(b.strip().rstrip(".") + "." for b in beats))
    chunks.append((camera.strip().rstrip(".") + ". " if camera else "") + H3_ANTI_DRIFT_LOCK)
    if sound: chunks.append("Sound: " + sound.strip().rstrip(".") + ".")
    chunks.append(H3_NEGATIVE_AUDIO_TEXT)
    return " ".join(chunks)


def build_flow_prompt(scene, framing="9:16 vertical first-person POV", extra_locks="", pov_hands=True):
    parts = [f"{STYLE_LOCK_CORE}, {framing}", scene.strip().rstrip(".")]
    if pov_hands: parts.append(POV_HANDS_LOCK)
    parts.append(RULE_LOCKS)
    if extra_locks: parts.append(extra_locks.strip().rstrip("."))
    parts.append("Clean image, no speech bubbles, no text, no watermark")
    return ". ".join(parts) + "."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=float)
    ap.add_argument("--mode", choices=["h3", "flow"])
    ap.add_argument("--scene", default="")
    ap.add_argument("--beats", nargs="*", default=[])
    ap.add_argument("--locks", default="")
    ap.add_argument("--sound", default="")
    ap.add_argument("--camera", default="")
    ap.add_argument("--sec", type=float)
    ap.add_argument("--no-pov-hands", action="store_true")
    args = ap.parse_args()
    if args.frames is not None:
        f = valid_h3_frames(args.frames)
        print(f"target={args.frames:.2f}s -> H3 frames={f} ({f/24:.2f}s at 24fps, n={(f-5)//17})")
        if not args.mode: return
    pov = not args.no_pov_hands
    if args.mode == "h3":
        if args.sec:
            f = valid_h3_frames(args.sec)
            print(f"# H3 frames: {f} ({f/24:.2f}s at 24fps)")
        print(build_h3_prompt(args.scene, beats=args.beats, extra_locks=args.locks, sound=args.sound, camera=args.camera, pov_hands=pov))
    elif args.mode == "flow":
        print(build_flow_prompt(args.scene, extra_locks=args.locks, pov_hands=pov))
    elif args.frames is None:
        ap.print_help()


if __name__ == "__main__":
    main()
