# Free YouTube Japan Series — Transfer Guide

Skill này giúp bạn tạo seri YouTube documentary tiếng Nhật (faceless) **hoàn toàn miễn phí**.

## Yêu cầu (Prerequisites)

1. **Python 3.10+**
   ```bash
   pip install edge-tts
   ```

2. **ffmpeg** (có libx264)
   - Termux: `pkg install ffmpeg`
   - Ubuntu: `apt install ffmpeg`
   - macOS: `brew install ffmpeg`

3. **Pexels API key** (free, 1 phút)
   - Đăng ký: https://www.pexels.com/api/
   - Copy key vào `scripts/pexels_download.py` (biến `API_KEY`)

4. **Gemini API key** (free) — chỉ cần nếu dùng LLM router
   - Lấy: https://aistudio.google.com/apikey
   - Set env: `export GEMINI_API_KEY="..."`

## Cách dùng

### Tạo 1 video mới

```bash
# 1. Viết script tiếng Nhật → tts-video-NN-jp.txt
# 2. Gen TTS (edge-tts, free)
cd audio && python3 -c "
import asyncio, edge_tts
text = open('../tts-video-NN-jp.txt', encoding='utf-8').read()
async def gen():
    tts = edge_tts.Communicate(text, 'ja-JP-NanamiNeural', rate='-10%')
    await tts.save('tts-video-NN-jp.ogg')
asyncio.run(gen())
"

# 3. Tải stock video (Pexels free)
cd stock-v2 && python3 pexels_download.py

# 4. Ghép video
python3 assemble.py NN
```

Output: `../video-NN-<tên>.mp4`

### Dùng LLM Router (tùy chọn)

```bash
cd scripts
export GEMINI_API_KEY="your_key"
python3 router.py &
# Rồi point Hermes vào: hermes config set model.base_url http://localhost:8080
```

## Lưu ý bản quyền

✅ Pexels: free cho mọi mục đích (kể cả commercial/YouTube monetization)
✅ Không cần ghi công
✅ Được phép chỉnh sửa (đã ghép + slow-mo + TTS)
❌ Không bán clip gốc không chỉnh sửa
❌ Không dùng người nhận diện vào mục đích xấu

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|------|-----------|-----|
| edge-tts timeout | Script quá dài | Chia đôi tại dấu `。` |
| Pexels 403 | Thiếu User-Agent | Script đã thêm UA, check lại |
| Video duration = 35000s | Framerate lỗi | `ffmpeg -i in.mp4 -r 30 -vsync cfr out.mp4` |
| File quá nặng (1.9GB) | Clip 4K/8K | Skip >200MB, scale 1080p |
| Encode chậm (0.2x) | ARM/Termux | Chạy background, đợi |

## Cấu trúc

```
skills/free-youtube-japan-series/
├── SKILL.md              # Quy trình chi tiết
├── scripts/
│   ├── pexels_download.py  # Tải stock free
│   ├── assemble.py          # Ghép video
│   └── router.py           # LLM free router
└── README.md             # File này
```

Full code + video mẫu: https://github.com/truong9300/youtube-niches
