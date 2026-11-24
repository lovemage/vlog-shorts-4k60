<p align="center"><img src="docs/images/pov/hero_banner.png" alt="vlog-shorts-4k60 v2 — Real Vlog 4K60 + AI 2D POV Comic" width="100%"></p>

<h1 align="center">vlog-shorts-4k60 (v2)</h1>

<p align="center">
  <a href="README.md">繁體中文</a> ·
  <a href="README.en.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <b>한국어</b> ·
  <a href="README.th.md">ภาษาไทย</a>
</p>

<p align="center">Xgentrade, Claude Code, Codex, Antigravity, Cursor에서 바로 쓰는 <b>듀얼 모드 세로형 숏폼 제작 AI Agent Skill</b>:<br><b>모드 A</b>는 스마트폰 촬영본을 <b>4K 60fps 3개국어 Vlog Shorts</b>로 편집하고, <b>모드 B</b>는 대본을 <b>2D 잉크라인 POV 인터랙티브 애니메이션</b>으로 제작해 추가 GPU 비용 0원으로 TikTok과 YouTube Shorts 다국어 버전을 동시 출력합니다.</p>

<p align="center"><img src="docs/images/pov/demo_preview.gif" alt="실제 완성 영상 프리뷰" width="260"></p>

---

## 왜 이렇게 설계했나요?

실사 브이로그든 AI 애니메이션이든 영상 원본을 브라우저로 재렌더링하거나 AI 모델에 자막을 직접 그리게 하면 **화질 저하, 글자 깨짐, 다국어 GPU 비용 2배** 문제가 발생합니다. 두 모드는 하나의 원칙을 공유합니다:

> **영상 소스(스마트폰 원본·AI 영상)는 절대 브라우저를 거치지 않으며, AI에게 글자를 맡기지 않습니다.** 브라우저는 투명 RGBA UI/자막 레이어만 렌더링하고 `ffmpeg`로 고화질 합성합니다.

### 1. AI 영상과 코드 렌더링 UI의 완전 분리
<p align="center"><img src="docs/images/pov/layer_breakdown.png" alt="AI 영상과 코드 UI 레이어 합성" width="100%"></p>

### 2. 추가 GPU 비용 0원의 다국어 분기
하나의 AI 영상·스틸 세트와 `audio/lines.json`으로 `python build.py --all` 한 번에 **TikTok(`--lang th`)**과 **YouTube Shorts(`--lang en`)** 버전을 동시 생성합니다.
<p align="center"><img src="docs/images/pov/bilingual_fork.png" alt="추가 GPU 비용 없는 다국어 분기" width="100%"></p>

### 3. 댓글이 다음 화를 결정하는 5비트 인터랙티브 구조
<p align="center"><img src="docs/images/pov/storyboard_strip.png" alt="5비트 인터랙티브 구조" width="100%"></p>

### 전체 아키텍처

```mermaid
flowchart LR
  subgraph ModeB["모드 B: AI 2D POV 인터랙티브 애니메이션 (v2)"]
    B1["1. 대본 & 대사<br>audio/lines.json"] --> B2["2. 비주얼 락 프롬프트<br>prompt_locks.py"]
    B2 --> B3["3. AI 키프레임 & 영상<br>Flow / MiniMax H3 (17n+5)"]
    B1 --> B4["4. 사전 검증<br>validate.py"]
    B3 --> B4
    B4 --> B5["5. 캐시 TTS + 타임라인<br>vo.py -> timeline.json"]
    B5 --> B6A["6A. 단일 샷 빠른 프리뷰<br>preview_shot.py"]
    B5 --> B6B["6B. 투명 UI 레이어<br>Playwright RGBA"]
    B3 --> B7["7. 합성 & 마스터링<br>CRF 12 + Suno BGM (-14 LUFS)"]
    B6B --> B7
    B7 --> B8A["TikTok (--lang th)"]
    B7 --> B8B["YT Shorts (--lang en)"]
  end
```

---

## 빠른 설치

```text
이 Skill을 설치해 줘: https://github.com/lovemage/vlog-shorts-4k60
```

```bash
git clone https://github.com/lovemage/vlog-shorts-4k60 ~/.claude/skills/vlog-shorts-4k60
python ~/.claude/skills/vlog-shorts-4k60/template_pov_comic/scripts/validate.py --doctor
```

## 라이선스

MIT License
