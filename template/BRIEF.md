---
workflow: general-video
flow: automation
storyboard: no
message: "<one sentence: what this video is about>"
destination: youtube
aspect: "9:16"
language: zh-Hant
length: "60-75s"
---

# <Title> · Shorts

## Intent
- Place: <Google Maps link → official name in local language + English>
- Event: <local-language name, edition, dates (cross-checked with what is said on camera)>
- Structure: hook → host intro → <sections> → host wrap → info card → bonus
- House rules: subtitles in <l1/l2/l3>; skip shaky / fast-moving shots; watch for duplicates;
  don't retype prices visible in the shot; explain local things in text.

## Assets
- <N> clips, <resolution>, <fps>. Note any landscape or 60/120 fps clips, and whether the sources are only 1080p.
- BGM: <file or generator + prompt>, starting at <BGM_IN> s. SFX: whoosh, pop.

## Customizations
- Delivery 4K 60fps. Footage: ffmpeg from the originals (lanczos → 2160×3840, light unsharp, CRF 12).
  HyperFrames renders only the graphics layer (portrait-4k 60fps ProRes 4444) for compositing.
- Audio: BGM + host sync sound, BGM ducked under dialogue; loudness target <LUFS>.
- Variants: CUT=shorts (<s>), CUT=tiktok (<s>).

## Notes
- <unclear words, facts you couldn't verify and left out, user decisions>
