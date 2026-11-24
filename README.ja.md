<p align="center"><img src="docs/images/pov/hero_banner.png" alt="vlog-shorts-4k60 v2 — Real Vlog 4K60 + AI 2D POV Comic" width="100%"></p>

<h1 align="center">vlog-shorts-4k60 (v2)</h1>

<p align="center">
  <a href="README.md">繁體中文</a> ·
  <a href="README.en.md">English</a> ·
  <b>日本語</b> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.th.md">ภาษาไทย</a>
</p>

<p align="center">Xgentrade・Claude Code・Codex・Antigravity・Cursor対応の<b>デュアルモード縦型ショート動画制作Skill</b>：<br><b>モードA</b>はスマホ実写素材を<b>4K 60fps 3言語Vlog Shorts</b>に編集、<b>モードB</b>は台本から<b>2D墨線コミックPOVインタラクティブ短編アニメ</b>を制作し、追加GPUコストゼロでTikTok・YouTube Shortsの多言語版を同時出力します。</p>

<p align="center"><img src="docs/images/pov/demo_preview.gif" alt="実際の完成動画プレビュー" width="260"></p>

---

## なぜこのパイプラインなのか？

実写VlogでもAIアニメでも、映像をブラウザ経由で再エンコードしたり、AIに字幕を描かせたりすると**画質劣化・文字崩れ・多言語化コスト倍増**が起きます。両モード共通の鉄則はただ一つ：

> **映像素材（スマホ実写もAI動画も）はブラウザを通さない。AIに文字を描かせない。** ブラウザは透明なUI・字幕レイヤーだけを描画し、`ffmpeg` で高画質合成します。

### 1. AI映像とコード描画UIの完全分離
<p align="center"><img src="docs/images/pov/layer_breakdown.png" alt="AI映像とコードUIのレイヤー合成" width="100%"></p>

### 2. 追加GPUコストゼロの多言語分岐（Zero-Extra-GPU）
1セットのAI映像・静止画と `audio/lines.json` から `python build.py --all` でTikTok版（`--lang th`）とYouTube Shorts版（`--lang en`）を同時生成します。
<p align="center"><img src="docs/images/pov/bilingual_fork.png" alt="追加GPUコストゼロの多言語出力" width="100%"></p>

### 3. コメントが次回を決める5ビート構成
<p align="center"><img src="docs/images/pov/storyboard_strip.png" alt="5ビートインタラクティブ構成" width="100%"></p>

### 全体アーキテクチャ

```mermaid
flowchart LR
  subgraph ModeB["モードB：AI 2DコミックPOVアニメ (v2)"]
    B1["1. 台本・セリフ<br>audio/lines.json"] --> B2["2. 視覚ロック生成<br>prompt_locks.py"]
    B2 --> B3["3. AIキーフレーム＆動画<br>Flow / MiniMax H3 (17n+5)"]
    B1 --> B4["4. 事前バリデーション<br>validate.py"]
    B3 --> B4
    B4 --> B5["5. キャッシュTTS＋タイムライン<br>vo.py -> timeline.json"]
    B5 --> B6A["6A. 単一ショット高速プレビュー<br>preview_shot.py"]
    B5 --> B6B["6B. 透明UIレイヤー<br>Playwright RGBA"]
    B3 --> B7["7. 合成＆マスタリング<br>CRF 12 + Suno BGM (-14 LUFS)"]
    B6B --> B7
    B7 --> B8A["TikTok版 (--lang th)"]
    B7 --> B8B["YT Shorts版 (--lang en)"]
  end
```

---

## インストール

```text
このSkillをインストールしてください: https://github.com/lovemage/vlog-shorts-4k60
```

```bash
git clone https://github.com/lovemage/vlog-shorts-4k60 ~/.claude/skills/vlog-shorts-4k60
python ~/.claude/skills/vlog-shorts-4k60/template_pov_comic/scripts/validate.py --doctor
```

## ライセンス

MIT License
