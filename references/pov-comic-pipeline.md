# Mode B: AI 2D POV Interactive Comic Pipeline

> Technical runbook for producing `1080×1920`, `30 fps`, `70–95s`, `-14 LUFS` 2D ink-line POV interactive animations with zero-extra-GPU bilingual forking.

## 1. Episode Directory Layout

```text
<ep_dir>/
├── audio/
│   ├── lines.json                # Single source of truth for dialogue, speakers, emotions & voice configs
│   ├── vo_cache/                 # MD5-cached raw TTS mp3s (shared across rebuilds)
│   └── <lang>/
│       ├── vo_proc/              # Silence-squeezed, tempo-adjusted 48kHz WAV clips
│       ├── durations.json        # Measured processed durations per line
│       ├── timeline.json         # Master timeline (marks + lines + total duration)
│       ├── bgm_plan.json         # Auto-aligned multi-segment BGM cues
│       └── mix.wav               # Final mastered stereo track (-14 LUFS)
├── props/                        # Isolated prop references
├── stills_src/                   # High-res 2K still frames (Flow / I2I) for Ken Burns zooms & lead-ins
├── h3/
│   ├── in/                       # First/last keyframes for image-to-video
│   ├── out/                      # Generated raw video clips (s1a.mp4, s2a.mp4...)
│   └── queue.py                  # Batch ComfyUI / I2V queue script
├── work/<lang>/
│   ├── seg/                      # Per-shot conformed segments
│   ├── ovl/                      # Playwright-rendered transparent 1080x1920 RGBA UI frames
│   ├── base.mp4                  # Conformed video without UI
│   ├── video.mp4                 # Final video with crisp UI composited
│   └── bgm.wav                   # Crossfaded BGM bed
├── vo.py / layout.py / assemble.py / sound.py / build.py
├── overlay.html / overlay.js / render_overlay.js
└── partN_<lang>.mp4              # Final deliverables
```

## 2. Quality & Encoding Standards

| Parameter | Standard | Why |
|---|---|---|
| Resolution & FPS | `1080×1920`, `30 fps` | Native 9:16 vertical for TikTok, YT Shorts, Reels |
| Scaling | `lanczos` | Preserves sharp 2D ink-line edges during upscaling |
| Sharpening | `unsharp=5:5:0.45` on **AI footage only** | Adds crispness to video clips without halos on text/UI |
| Intermediate Codec | `libx264`, `CRF 12`, `yuv420p` | Virtually lossless intermediate before final mux |
| Audio Mastering | `-14 LUFS`, `AAC 256k`, `48 kHz` | Platform-standard loudness with automatic BGM voice ducking |
| H3 Frame Counts | `17n + 5` at `24 fps` (e.g. `141`, `175`, `192`, `209`, `243`) | Required by MiniMax H3 temporal VAE architecture |

## 3. Guardrails & Fast Iteration

```bash
python template_pov_comic/scripts/validate.py --doctor
python template_pov_comic/scripts/validate.py <ep_dir> --lang th,en
python template_pov_comic/scripts/prompt_locks.py --frames 8.5
python template_pov_comic/scripts/preview_shot.py <ep_dir> --shot s2a --lang th
cd <ep_dir> && python build.py --all
```
