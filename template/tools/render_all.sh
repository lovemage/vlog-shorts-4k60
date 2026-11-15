#!/usr/bin/env bash
# Render one or more cuts end to end:
#   footage -> overlay + mix -> HyperFrames graphics layer (4K, ProRes 4444 with alpha) -> ffmpeg composite
# Usage: bash tools/render_all.sh [shorts tiktok ...]     (default: every variant in edl.py)
# Env:   HF      command that runs the HyperFrames CLI (default: pinned npx version)
#        PYTHON  python interpreter (default: python3, else python)
set -euo pipefail
cd "$(dirname "$0")/.."
HF="${HF:-npx --yes hyperframes@0.8.141}"
PY="${PYTHON:-$(command -v python3 || command -v python)}"
CUTS="${*:-$("$PY" -c 'import edl; print(" ".join(edl.VARIANTS))')}"
read -r W H FPS < <("$PY" -c 'import edl; print(edl.OUT_W, edl.OUT_H, edl.OUT_FPS)')
RES="portrait-4k"; [ "$H" -le 1920 ] && RES="portrait"
for CUT in $CUTS; do
  export CUT
  echo "== $CUT: footage"
  "$PY" tools/cut.py | tail -1
  echo "== $CUT: overlay + mix"
  "$PY" tools/build_overlay.py
  "$PY" tools/subset_font.py
  "$PY" tools/mix.py
  echo "== $CUT: graphics layer ($RES ${FPS}fps, ProRes 4444 alpha)"
  $HF render --variables '{"footage":false}' --format mov --resolution "$RES" --fps "$FPS" --quiet -o "work/$CUT/overlay.mov"
  echo "== $CUT: composite"
  "$PY" tools/final.py 2>&1 | tail -1
done
