---
name: vlog-shorts-4k60
description: >-
  Dual-mode AI Agent Skill for sharp vertical short-form videos (TikTok, YouTube Shorts, Reels):
  (Mode A) Real phone vlog clips to 4K 60fps vertical Shorts with 3-language subtitles, local-info tags,
  cloned-voice narration, and HyperFrames transparent graphics layer;
  (Mode B) AI 2D ink-line POV interactive comic animations (1080x1920 30fps, 70-95s) combining
  Flow / MiniMax H3 (17n+5) with Playwright RGBA HUD/subtitles, zero-extra-GPU bilingual forking
  (--lang th|en), Suno BGM voice-ducking (-14 LUFS), pre-flight validation, and fast single-shot preview.
  Use for "剪成 Shorts", "做成 vlog", "4K60 短影音", "POV 漫畫動畫", "雙語互動短影音", or multi-platform cuts.
---

# Vlog Shorts 4K60 + POV Comic Director (v2)

Two production modes sharing **one golden rule**:

> **Footage (phone clips OR AI-generated 2D video) never goes through the browser.** The browser (HyperFrames / Playwright) renders ONLY the transparent UI/subtitle/HUD layer, composited at full resolution with `ffmpeg`.

| Mode | Best For | Footage Source | UI Layer | Output |
|---|---|---|---|---|
| **Mode A: Real Vlog 4K60** (`template/`) | Travel, markets, food, festivals | Phone clips (`ffmpeg` lanczos 4K60) | HyperFrames ProRes 4444 alpha | `2160×3840` 60fps (`Shorts` + `TikTok`) |
| **Mode B: AI 2D POV Comic** (`template_pov_comic/`) | Daily serialized POV interactive animations | Flow Nano Banana + MiniMax H3 (`17n+5`) | Playwright `1080×1920` RGBA PNGs | `1080×1920` 30fps, `-14 LUFS` (`--lang th` + `--lang en` from 1 AI render) |

---

## Mode A: Real Phone Vlog 4K60 (`template/`)

Phone clips in → `renders/<title>_Shorts_4K60.mp4` (+ a longer TikTok cut), `影片資訊.txt`, cover.

The one rule that shapes everything: **footage never goes through the browser.** HTML-to-video renderers
(HyperFrames, Remotion, …) screenshot a page and re-encode it; phone video that takes that path comes out
soft, and a 1080p30 default makes it worse. So:

| Layer | Made by | Format |
|---|---|---|
| Picture | ffmpeg, straight from the original files: lanczos to 2160×3840, centre crop, light luma unsharp | x264 CRF 12, 60 fps |
| Graphics (titles, subtitles, tags, end card) | HyperFrames, transparent, rasterised at portrait-4k | ProRes 4444 + alpha, 60 fps |
| Sound | ffmpeg: dialogue / ambience / SFX / ducked BGM buses, 2-pass loudnorm | 48 kHz 24-bit |
| Delivery | ffmpeg overlay in yuv444, then yuv420p | x264 CRF 14 high@5.2, AAC 320k |

Text is never sharpened or upscaled; footage is never re-rendered by a browser.

## Requirements

ffmpeg/ffprobe (with zscale for HDR sources), Python 3.10+ (`python3` on macOS/Linux) with `opencv-python numpy fonttools`, Node 20+ (for `npx hyperframes`).
Optional: fal.ai key (`FAL_KEY`) for BGM/SFX and cloned-voice narration. If the HyperFrames skills are
installed, read `/hyperframes` and `/hyperframes-core` before editing composition HTML.

## Workflow

Copy `template/` into a `short/` folder next to the clips (the default `SRC_DIR` is the parent folder),
then work through the steps. Each step is a script; every script reads `CUT=<variant>` (default: the first
variant in `edl.py`), keeps its files in `work/<CUT>/`, and shares the segment cache `work/seg/`.

1. **Brief.** Ask for or confirm: place (a Google Maps link is ideal), languages (l1/l2/l3), length
   (YouTube Shorts ≤ 60–75 s; a longer TikTok cut is optional), what to show, house rules. Write them into
   `BRIEF.md` (see `template/BRIEF.md`). Never invent facts about the place or event.
2. **Research.** Look up the place, the event name in the local language, dates, entry fee, what is
   on. Cross-check against what people say on camera. If something such as opening hours is not
   officially published, leave it out. Details: `references/research-and-info.md`.
3. **Shot log.** `python edl.py --sources`, ffprobe every clip, look at 2–3 frames per clip, and write
   `影片素材初步分析.md`: resolution, fps, length, content, speech, duplicates. Mark landscape and
   60/120 fps clips. Note HDR clips (HLG/HDR10). `cut.py` tone-maps them to SDR.
   **Tell the user if the sources are only 1080p or soft.** The output is still 4K,
   but upscaling doesn't add detail.
4. **Stability scan.** `python tools/shake.py` prints, for each clip, a map of 0.5 s windows:
   `.` steady, `o` usable, `X` too fast or shaky, `b` blurred. Cut only from `.` and short `o` windows.
   Pick one shot from each group of duplicates.
5. **EDL.** Edit `SEGS` in `edl.py`: `(id, section, src, in, dur, volume)`. Typical structure: a 3–4 s hook
   built from the best shots → host intro → sections → host wrap-up → end card (`src=None`) → bonus shot.
   Shots run 0.9–2.5 s and talking shots run longer. Put L/J-cuts of the host's voice over b-roll in `AUDIO`.
   For the longer cut, put the extra stable shots in `VARIANTS["tiktok"]["insert_after"]`.
   `python edl.py` prints the timeline.
6. **Narration (optional).** Write lines for the gaps where nobody talks on camera in `vo/script.json`
   (copy `vo/script.example.json`; fields `id`, `seg`, `off`, `say`, `sub`: [l1, l2, l3]; `|` in l1 marks a manual line break). Then
   `VOICE_ID=… python tools/make_vo.py`. Narration subtitles get a yellow drop shadow and a pink progress
   bar, so viewers can tell them apart from on-camera speech.
7. **Words on screen.** Edit `content.py`: `HOOK`, `SUBS` (on-camera speech), `TAGS` (local food, places
   and customs, each with a short explanation in all three languages), `DATE_STICKER`, `END`. Every cue
   is tied to a segment id, so retiming the cut never moves a caption. Rules: don't retype prices that
   are already visible in the shot; explain local things briefly; keep to the safe zones (top 220 px,
   bottom 440 px, right 150 px of the 1080×1920 layout).
8. **Music & SFX.** Put a track at `assets/music/bgm.wav`, or run `python tools/gen_audio.py` (fal.ai
   stable-audio; describe regional instruments and bpm). Each variant's `bgm_in` in `edl.py` defaults to
   auto, so the track's ending lands on the last frame. In `tools/mix.py`, set `TARGET_LUFS` to the loudest
   Short already on the channel.
9. **Fonts.** `python tools/get_fonts.py` (Noto Sans TC + Kanit for Thai/Latin). For other languages,
   swap in Noto Sans SC/JP/KR or another script font and set `FONT_MAIN`/`FONT_ALT` in `content.py`.
10. **Preview.** `python tools/cut.py && python tools/build_overlay.py && python tools/subset_font.py &&
    python tools/mix.py && python tools/proxy.py`, then `npx --yes hyperframes@0.8.141 preview --background`
    and `npm run check` (same pinned version as the render). Fix every error before rendering.
11. **Render.** `bash tools/render_all.sh` (all variants), or `bash tools/render_all.sh shorts`. Verify:
    ffprobe shows 2160×3840 at 60/1, the length matches `python edl.py`, loudness hits the target
    (`ffmpeg -i out.mp4 -af ebur128=peak=true -f null -`), and frames grabbed from the hook, a tag and
    the end card look right. Look at those frames yourself before handing anything over.
12. **Upload text & cover.** Write `影片資訊.txt`: 2–3 title options, the description, a local-knowledge
    list, event info, a map link, and the AI disclosure (AI music/voice). Template:
    `references/research-and-info.md`. For the cover, use the user's image model and add the title in
    code (`references/cover.md`).

## Guardrails

- `cut.py` stops if any segment runs past the end of its source clip. That would silently shorten the
  whole cut and push every caption and audio event out of sync.
- `build_overlay.py` warns when subtitles overlap. Fix every overlap before rendering.
- Keep secrets out of the project: `FAL_KEY` and `VOICE_ID` come from environment variables. `.gitignore`
  already excludes `work/`, `renders/`, the voice cache and `.env`.
- Don't add camera or phone credits ("Shot on …") unless the user asks for them.
- Footage edits (colour, stabilisation, slow motion with 60/120 fps sources) belong in the `VF` chain in
  `cut.py`, never in the HTML layer.

## Files

```
template/
  edl.py            the cut: sources, segments, variants, extra audio
  content.py        everything on screen: hook, subtitles, tags, stickers, end card, fonts, colours
  vo/script.example.json
  tools/  shake.py cut.py build_overlay.py subset_font.py mix.py proxy.py final.py render_all.sh
          make_vo.py gen_audio.py fal.py get_fonts.py
  BRIEF.md package.json hyperframes.json meta.json .gitignore
references/
  research-and-info.md   place research + 影片資訊 template
  cover.md               cover recipe
  pov-comic-pipeline.md  Mode B full AI 2D POV comic production runbook
  pov-script-rules.md    Mode B interactive POV storytelling rules
  pov-character-bible.md Mode B character lock & voice profile template
template_pov_comic/
  build.py               one-click dual-language builder (--all / --lang / --shot / --validate-only)
  audio/lines.example.json
  scripts/
    validate.py          environment doctor + pre-flight episode validator (17n+5, banned words, assets)
    prompt_locks.py      Production Locks for Flow / MiniMax H3 + automatic 17n+5 frame snapping
    preview_shot.py      fast single-shot preview (Section-Level Revision)
```

---

## Mode B: AI 2D Ink-Line POV Interactive Comic (`template_pov_comic/`)

For daily serialized 2D ink-line POV animations (`1080×1920`, `30 fps`, `70–95s`, `-14 LUFS`) where viewer comments decide the next episode. Full technical details in `references/pov-comic-pipeline.md`.

### Why This Architecture
1. **Zero Text Blur**: AI models generate clean, text-free 2D ink-line footage (`unsharp=5:5:0.45` on footage ONLY); Playwright renders razor-sharp dual-language subtitles, HUD badges, and interactive choice cards onto a transparent RGBA layer.
2. **Zero-Extra-GPU Bilingual Forking**: Generate AI keyframes and H3 video clips **once**, then fork `--lang th` (TikTok: Thai dub + TH/EN subs) and `--lang en` (YouTube Shorts: EN dub + ZH/EN subs) from the same `audio/lines.json`.
3. **Production Locks & Pre-Flight Guardrails**: Enforce `17n+5` H3 frame counts, deadpan expressions, outfit consistency, and platform word filters before spending GPU/TTS credits.
4. **Section-Level Preview**: Audition a single `@shot` (video + overlay + VO + ambient + BGM) in seconds instead of re-rendering the entire episode.

### Mode B Workflow
1. **Doctor**: `python template_pov_comic/scripts/validate.py --doctor`
2. **Script & Cast**: Follow `references/pov-script-rules.md` and `references/pov-character-bible.md` → write `<ep_dir>/audio/lines.json` (0–5s vote-payoff hook → deadpan comedy beats → cliffhanger → 4s binary choice card).
3. **Production Locks & Keyframes**: Use `python template_pov_comic/scripts/prompt_locks.py --mode flow ...` to generate a panoramic establishing sheet first, then props (`props/`) and per-shot first frames (`h3/in/`, `stills_src/`).
4. **AI Video (`17n+5` Beat-Locked)**: Snap target durations with `python template_pov_comic/scripts/prompt_locks.py --frames <sec>` and queue MiniMax H3 clips with timed beats (`0–3s: ...; 3–6s: ...`), small camera motion, anti-drift ending lock, and `No speech, no voices, no singing, no music, no text, no subtitles`. Save to `h3/out/<shot>.mp4`.
5. **Pre-Flight Validate**: `python template_pov_comic/scripts/validate.py <ep_dir> --lang th,en`
6. **Single-Shot Preview**: `python template_pov_comic/scripts/preview_shot.py <ep_dir> --shot s2a --lang th`
7. **Full Dual-Language Build**: `cd <ep_dir> && python build.py --all` → outputs `partN_th.mp4` + `partN_en.mp4` (`CRF 12`, `-14 LUFS`, Suno BGM voice-ducking).
8. **Cover Safe Zone**: Keep all cover titles and faces within the **3:4 vertical safe zone (15%–85% height)**; no camera branding (`Shot on ...`).
