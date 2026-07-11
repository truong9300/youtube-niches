---
name: free-youtube-japan-series
description: "Production pipeline for a faceless YouTube documentary series about Japan (Hidden Japan / 隠された日本), built entirely on FREE resources: edge-tts for Japanese narration, Pexels free stock video via API for B-roll, ffmpeg for assembly, and an OpenAI-compatible free LLM router. Zero paid API cost. Use when building/narrating/assembling stock-footage YouTube videos, especially Japanese-language niche content, with no budget."
version: 1.0.0
author: Quan Vu
license: MIT
platforms: [linux, macos, android-termux]
metadata:
  hermes:
    tags: [youtube, faceless, documentary, japanese, tts, stock-video, pexels, ffmpeg, free, automation]
    homepage: https://github.com/truong9300/youtube-niches
---

# Free YouTube Japan Series Pipeline

Produce a faceless YouTube documentary series ("Hidden Japan" / 隠された日本) using **100% free resources**. No paid TTS, no paid video gen, no paid LLM.

## What this does

1. **Script** — written/translated to Japanese (or any language) by a free LLM.
2. **Narration (TTS)** — `edge-tts` ja-JP-NanamiNeural (free, no API key).
3. **B-roll footage** — downloaded free from Pexels via their API (license = free for commercial use, no attribution required).
4. **Assembly** — `ffmpeg` concatenates + slow-motions clips to match narration length.
5. **LLM router** (optional) — OpenAI-compatible proxy that rotates free models (Gemini/Groq/DeepSeek) so the agent itself runs free.

## Why free

| Component | Paid alt | Free choice | Cost |
|-----------|-----------|-------------|------|
| Narration | OpenAI TTS ($15/1M chars) | edge-tts Nanami | $0 |
| Footage | PixVerse/LTX ($0.005–0.06/s) | Pexels stock API | $0 |
| LLM | Nous Portal credits | Gemini 2.5 Flash free | $0 |

## Prerequisites

- Python 3.10+, `pip install edge-tts`
- `ffmpeg` with libx264 (Termux: `pkg install ffmpeg`)
- A **Pexels API key** (free, 1 min): https://www.pexels.com/api/
- A **Gemini API key** (free) for the LLM router: https://aistudio.google.com/apikey

## Pipeline (numbered steps)

### Step 1 — Write/translate the script
Write the narration in the target language. For Japanese documentary tone, keep sentences short and use `。` punctuation. Save as `tts-video-NN-jp.txt`.

Example (video #2 Aokigahara):
```
富士山の麓に、あまりに密で静かなためコンパスが効かなくなる森があります。
ようこそ、青木ヶ原樹海へ——日本の「樹の海」です。
```

### Step 2 — Generate Japanese TTS (free)
```bash
cd <project>/audio
python3 -c "
import asyncio, edge_tts
text = open('../tts-video-02-jp.txt', encoding='utf-8').read()
async def gen():
    tts = edge_tts.Communicate(text, 'ja-JP-NanamiNeural', rate='-10%')
    await tts.save('tts-video-02-jp.ogg')
asyncio.run(gen())
print('done')
"
```
- Voice `ja-JP-NanamiNeural` = best free Japanese. `rate='-10%'` slows it slightly for documentary feel.
- If text is long (>1000 chars) and times out, split at a `。` boundary into two halves and merge later with ffmpeg.

### Step 3 — Download free stock footage (Pexels)
Use `scripts/pexels_download.py` (copy into project). Set `API_KEY` in the script or via env.
```bash
export PEXELS_API_KEY="your_key"
python3 pexels_download.py
```
It downloads ~4 HD clips per video into `stock-v2/vN_name/`. Skips files >200MB to avoid huge 4K/8K clips.

**License note (important for handoff):** Pexels license = free for commercial use, no attribution required, modification allowed. Safe for YouTube monetization. Do NOT sell unaltered clips or imply endorsement.

### Step 4 — Assemble video
Use `scripts/assemble.py <num>`:
```bash
python3 assemble.py 2   # builds video-02-aokigahara.mp4
```
The script:
1. Reads TTS duration (target length).
2. Picks stock clips, loops them to cover target.
3. Concats + scales to 1080p (pad to avoid aspect distortion).
4. Applies 1.5x slow-mo to stretch footage.
5. Muxes with the TTS audio (`-shortest` so it ends on narration).

Run in background — encoding is slow on ARM/Termux (~0.2x realtime for 4K→1080p).

### Step 5 (optional) — Free LLM router
See `scripts/router.py`. Runs an OpenAI-compatible server on `:8080` that routes to free models with auto-fallback. Point Hermes at it:
```bash
hermes config set model.provider custom:llm-router
hermes config set model.base_url http://localhost:8080
```
Supported free models: `gemini-2.5-flash` (60 req/min), `llama-3.3-70b` / `mixtral-8x7b` (Groq, 30 req/min), `deepseek-chat` ($0.14/M tok).

## Pitfalls

- **edge-tts needs network** — it is a Microsoft cloud API, not local. Works on Termux with internet.
- **Pexels API 403 without User-Agent** — the download script must send a UA header or requests get blocked.
- **4K/8K clips explode file size** — a single 4320x7680 clip concatenated 3x = 1.9GB temp. Always skip >200MB and scale to 1080p.
- **ffmpeg concat of mixed framerates** — force `-vsync cfr` and `-r 30` on final output or duration metadata breaks (shows 35000s). Re-encode if needed:
  ```bash
  ffmpeg -y -i broken.mp4 -r 30 -vsync cfr -c:v libx264 -crf 23 -c:a aac fixed.mp4
  ```
- **Slow-mo 1.5x may not be enough** — if narration is 95s and you have 4×10s clips, loop them and/or raise slow-mo factor.
- **Gemini free tier has no `system` role** — the router maps system→user.

## Verification

After assembly, verify each output:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video-02-aokigahara.mp4
# Should be ~95 (matches TTS), NOT 35000
```
Check the audio track is present and the video ends roughly when narration ends.

## Project layout (reference)

```
japan-channel/
├── tts-video-0N-jp.txt      # JP narration scripts
├── audio/tts-video-0N-jp.ogg # edge-tts output
├── stock-v2/
│   ├── pexels_download.py
│   ├── assemble.py
│   ├── v2_aokigahara/        # downloaded clips
│   ├── v3_food/
│   └── v4_zen/
├── video-01-yakushima-jp.mp4
├── video-02-aokigahara.mp4
├── video-03-food.mp4
└── video-04-zen.mp4
```

Full working code lives at the GitHub repo above. This skill is the transferable procedure; clone the repo for the exact scripts.
