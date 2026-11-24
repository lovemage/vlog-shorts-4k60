<p align="center"><img src="docs/images/pov/hero_banner.png" alt="vlog-shorts-4k60 v2 — Real Vlog 4K60 + AI 2D POV Comic" width="100%"></p>

<h1 align="center">vlog-shorts-4k60 (v2)</h1>

<p align="center">
  <a href="README.md">繁體中文</a> ·
  <a href="README.en.md">English</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <b>ภาษาไทย</b>
</p>

<p align="center"><b>AI Agent Skill แบบโอเพนซอร์ส 2 โหมด</b> สำหรับ Xgentrade, Claude Code, Codex, Antigravity และ Cursor:<br><b>โหมด A</b> ตัดคลิปมือถือเป็น <b>Vlog Shorts 4K 60fps 3 ภาษา</b> และ <b>โหมด B</b> เปลี่ยนบทเป็น<b>แอนิเมชันคอมิก 2D แนว POV แบบอินเทอร์แอคทีฟ</b> แตกเวอร์ชันสองภาษาลง TikTok และ YouTube Shorts โดย<b>ไม่เสียค่า GPU เพิ่ม</b></p>

<p align="center"><img src="docs/images/pov/demo_preview.gif" alt="ตัวอย่างผลงานจริง" width="260"></p>

---

## ทำไมต้องออกแบบเวิร์กโฟลว์แบบนี้?

ไม่ว่าจะเป็นคลิป Vlog จากมือถือหรือแอนิเมชัน AI หากให้เบราว์เซอร์เรนเดอร์วิดีโอซ้ำหรือให้ AI เขียนซับไตเติลลงภาพตรงๆ ภาพจะเบลอ ตัวหนังสือเพี้ยน และต้องเสียค่า GPU ซ้ำเมื่อทำหลายภาษา ทั้งสองโหมดจึงยึดกฎเหล็กข้อเดียวกัน:

> **ไฟล์วิดีโอต้นฉบับ (คลิปมือถือหรือวิดีโอ AI) จะไม่ผ่านเบราว์เซอร์ และไม่ให้ AI สร้างตัวหนังสือเด็ดขาด** เบราว์เซอร์ทำหน้าที่เรนเดอร์เฉพาะเลเยอร์ UI/ซับไตเติลพื้นหลังโปร่งใส แล้วรวมภาพความละเอียดสูงด้วย `ffmpeg`

### 1. แยกวิดีโอ AI ออกจาก UI ที่เรนเดอร์ด้วยโค้ด
<p align="center"><img src="docs/images/pov/layer_breakdown.png" alt="การแยกเลเยอร์วิดีโอ AI และ UI โค้ด" width="100%"></p>

### 2. แตกเวอร์ชันสองภาษาโดยไม่เสียค่า GPU เพิ่ม (Zero-Extra-GPU)
ใช้คลิป AI และภาพนิ่งชุดเดียวกันทั้งหมด ขับเคลื่อนจาก `audio/lines.json` เพียงไฟล์เดียว รัน `python build.py --all` เพื่อสร้างทั้ง **TikTok (`--lang th`)** และ **YouTube Shorts (`--lang en`)** ในคำสั่งเดียว
<p align="center"><img src="docs/images/pov/bilingual_fork.png" alt="แตกเวอร์ชันสองภาษาโดยไม่เสียค่า GPU เพิ่ม" width="100%"></p>

### 3. โครงสร้างเรื่อง 5 จังหวะที่ให้คอมเมนต์กำหนดตอนต่อไป
<p align="center"><img src="docs/images/pov/storyboard_strip.png" alt="โครงสร้าง 5 จังหวะของตอนอินเทอร์แอคทีฟ" width="100%"></p>

### สถาปัตยกรรมระบบ

```mermaid
flowchart LR
  subgraph ModeB["โหมด B: แอนิเมชันคอมิก 2D แนว POV (v2)"]
    B1["1. บทและคำพูด<br>audio/lines.json"] --> B2["2. ล็อกสไตล์และตัวละคร<br>prompt_locks.py"]
    B2 --> B3["3. ภาพตั้งต้น & วิดีโอ AI<br>Flow / MiniMax H3 (17n+5)"]
    B1 --> B4["4. ตรวจสอบก่อนเรนเดอร์<br>validate.py"]
    B3 --> B4
    B4 --> B5["5. เสียงพากย์แคช + ไทม์ไลน์<br>vo.py -> timeline.json"]
    B5 --> B6A["6A. พรีวิวทีละช็อตแบบไว<br>preview_shot.py"]
    B5 --> B6B["6B. เลเยอร์ UI โค้ด<br>Playwright RGBA"]
    B3 --> B7["7. รวมภาพและมาสเตอร์เสียง<br>CRF 12 + Suno BGM (-14 LUFS)"]
    B6B --> B7
    B7 --> B8A["TikTok (--lang th)"]
    B7 --> B8B["YT Shorts (--lang en)"]
  end
```

---

## ติดตั้งอย่างรวดเร็ว

```text
ติดตั้ง Skill นี้ให้หน่อย: https://github.com/lovemage/vlog-shorts-4k60
```

```bash
git clone https://github.com/lovemage/vlog-shorts-4k60 ~/.claude/skills/vlog-shorts-4k60
python ~/.claude/skills/vlog-shorts-4k60/template_pov_comic/scripts/validate.py --doctor
```

## สัญญาอนุญาต

MIT License
