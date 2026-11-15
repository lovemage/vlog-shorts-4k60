#!/usr/bin/env bash
# Render one or more cuts end to end:
#   overlay + mix  ->  HyperFrames graphics layer (4K, ProRes 4444 with alpha)  ->  ffmpeg composite
# Usage: bash tools/render_all.sh [shorts tiktok ...]     (default: every variant in edl.py)
# Env:   HF  command that runs the HyperFrames CLI (default: pinned npx version)
set -euo pipefail
cd "$(dirname "$0")/.."
HF="${HF:-npx --yes hyperframes@0.8.141}"
CUTS="${*:-$(python -c 'import edl; print(" ".join(edl.VARIANTS))')}"
read -r W H FPS < <(python -c 'import edl; print(edl.OUT_W, edl.OUT_H, edl.OUT_FPS)')
RES="portrait-4k"; [ "$H" -le 1920 ] && RES="portrait"
for CUT in $CUTS; do
  export CUT
  echo "== $CUT: footage"
  python tools/cut.py | tail -1
  echo "== $CUT: overlay + mix"
  python tools/build_overlay.py
  python tools/subset_font.py
  python tools/mix.py
  echo "== $CUT: graphics layer ($RES ${FPS}fps, ProRes 4444 alpha)"
  $HF render --variables '{"footage":false}' --format mov --resolution "$RES" --fps "$FPS" --quiet -o "work/$CUT/overlay.mov"
  echo "== $CUT: composite"
  python tools/final.py 2>&1 | tail -1
done
