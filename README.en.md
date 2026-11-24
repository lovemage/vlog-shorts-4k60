<p align="center"><img src="docs/images/pov/hero_banner.png" alt="vlog-shorts-4k60 v2 — Real Vlog 4K60 + AI 2D POV Comic" width="100%"></p>

<h1 align="center">vlog-shorts-4k60 (v2)</h1>

<p align="center">
  <a href="README.md">繁體中文</a> ·
  <b>English</b> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.th.md">ภาษาไทย</a>
</p>

<p align="center">A <b>dual-mode open-source AI Agent Skill</b> (Xgentrade, Claude Code, Codex, Antigravity, Cursor) for sharp vertical short-form videos:<br><b>Mode A</b> cuts phone clips into <b>4K 60fps 3-language Vlog Shorts</b>; <b>Mode B</b> turns scripts into <b>2D ink-line POV interactive comic animations</b> with zero-extra-GPU bilingual forking for TikTok & YouTube Shorts.</p>

<p align="center"><img src="docs/images/pov/demo_preview.gif" alt="Real EP7 Output Preview" width="260"></p>

---

## Why This Pipeline Exists (One Golden Rule)

Whether you shoot phone vlogs or generate AI 2D animations, routing video footage through a browser renderer or asking AI video models to render subtitles causes **soft video, garbled text, and doubled GPU costs for multi-language publishing**. Both modes enforce one rule:

> **Footage (phone clips OR AI video) never goes through the browser, and AI never renders text.** The browser (HyperFrames / Playwright) renders ONLY a transparent RGBA UI/subtitle layer, composited onto high-bitrate footage with `ffmpeg`.

| Mode | Best For | Footage Source | Transparent UI Layer | Output |
|---|---|---|---|---|
| **Mode A: Real Vlog 4K60** (`template/`) | Markets, festivals, food, travel vlogs | Original phone files via `ffmpeg` lanczos 4K60 + `shake.py` | HyperFrames ProRes 4444 alpha | `2160×3840` 60fps (Shorts + TikTok) |
| **Mode B: AI 2D POV Comic** (`template_pov_comic/`) | Daily serialized interactive animations | Flow Nano Banana + MiniMax H3 (`17n+5` beat-locked) | Playwright `1080×1920` RGBA PNGs | `1080×1920` 30fps, `-14 LUFS` (Zero-Extra-GPU Bilingual) |

---

## Mode B (New in v2): AI 2D Ink-Line POV Interactive Comic

### 1. Separate AI Video from Code-Rendered UI
AI generates clean, text-free 2D ink-line footage (`unsharp=5:5:0.45` applied to footage ONLY). Playwright renders razor-sharp HUD badges, dual-language subtitles, and interactive voting cards on a transparent layer—zero text blur, 100% editable.

<p align="center"><img src="docs/images/pov/layer_breakdown.png" alt="AI Video + Code UI Layer Breakdown" width="100%"></p>

### 2. Zero-Extra-GPU Bilingual Forking
One set of AI clips and stills feeds a single `audio/lines.json`. Running `python build.py --all` outputs both **TikTok (`--lang th`)** and **YouTube Shorts (`--lang en`)** with localized dubs, synced timelines, and dual subtitles at **zero extra GPU cost**.

<p align="center"><img src="docs/images/pov/bilingual_fork.png" alt="Zero Extra GPU Bilingual Forking" width="100%"></p>

### 3. 5-Beat Interactive POV Episode Arc
0–5s continuity hook paying off last episode's top vote → instant conflict → deadpan comedy beats → cliffhanger → 4s binary choice card (`1` vs `2`).

<p align="center"><img src="docs/images/pov/storyboard_strip.png" alt="5-Beat Interactive POV Episode Arc" width="100%"></p>

### Architecture

```mermaid
flowchart LR
  subgraph ModeB["Mode B: AI 2D POV Interactive Comic (v2)"]
    B1["1. Script & Cast<br>audio/lines.json"] --> B2["2. Production Locks<br>prompt_locks.py"]
    B2 --> B3["3. AI Keyframes & Video<br>Flow / MiniMax H3 (17n+5)"]
    B1 --> B4["4. Pre-Flight Validator<br>validate.py"]
    B3 --> B4
    B4 --> B5["5. Cached TTS + Timeline<br>vo.py -> timeline.json"]
    B5 --> B6A["6A. Fast Shot Preview<br>preview_shot.py"]
    B5 --> B6B["6B. Code UI Layer<br>Playwright RGBA"]
    B3 --> B7["7. Composite & Master<br>CRF 12 + Suno BGM (-14 LUFS)"]
    B6B --> B7
    B7 --> B8A["TikTok (--lang th)"]
    B7 --> B8B["YT Shorts (--lang en)"]
  end
```

### Bundled CLI Tools (`template_pov_comic/scripts/`)

| Tool | Purpose | Example |
|---|---|---|
| `validate.py` | Environment doctor (`--doctor`) & pre-flight checks (`17n+5`, banned words, missing assets) | `python template_pov_comic/scripts/validate.py <ep_dir> --lang th,en` |
| `prompt_locks.py` | Flow / MiniMax H3 style & character locks + automatic `17n+5` frame snapping | `python template_pov_comic/scripts/prompt_locks.py --frames 8.5` |
| `preview_shot.py` | Fast single-shot preview (Section-Level Revision in seconds) | `python template_pov_comic/scripts/preview_shot.py <ep_dir> --shot s2a --lang th` |

---

## Mode A: Real Phone Vlog 4K60 (`template/`)

<p align="center"><img src="docs/images/hero.jpg" alt="Mode A Real Vlog 4K60" width="90%"></p>

- `tools/shake.py` stability & sharpness scan (0.5s windows)
- Single `edl.py` + `content.py` outputting both YouTube Shorts and TikTok 4K60 cuts
- 3-language subtitles, local-info tags, optional cloned-voice narration (`fal.ai`), sidechain-ducked BGM + 2-pass loudnorm

---

## Quick Install (Xgentrade / Claude Code / Codex / Antigravity / Cursor)

```text
Install this Skill for me: https://github.com/lovemage/vlog-shorts-4k60
```

```bash
git clone https://github.com/lovemage/vlog-shorts-4k60 ~/.claude/skills/vlog-shorts-4k60
python ~/.claude/skills/vlog-shorts-4k60/template_pov_comic/scripts/validate.py --doctor
```

## License

MIT License
