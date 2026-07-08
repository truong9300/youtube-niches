# 🇦🇺 PRODUCTION WORKFLOW — KÊNH YOUTUBE ÚC

## TỔNG QUAN THƯ MỤC

```
australia-channel/
├── script-video-01-superannuation.md    ✅ Script
├── script-video-02-salary-sacrifice.md  ✅ Script
├── script-video-03-industry-vs-retail.md ✅ Script
├── script-video-04-how-much-super.md    ✅ Script
├── publishing-plan.md                   ✅ Kế hoạch 10 video
├── production-workflow.md               ← File này
├── assets/
│   ├── thumbnail-video-01.png  ✅
│   ├── thumbnail-video-02.png  ✅
│   ├── thumbnail-video-03.png  ✅
│   └── thumbnail-video-04.png  ✅
```

---

## 🏭 QUY TRÌNH SẢN XUẤT 1 VIDEO

### Bước 1: Script → Chia cảnh

Từ script, chia thành ~30-40 cảnh (scene), mỗi cảnh tương ứng 1 lần gen Seedance:

| Cảnh | Thời gian | Mô tả visual | Prompt Seedance |
|:----:|:---------:|-------------|----------------|
| 1 | 00:00-00:30 | Hook visual | "Australian dollars flying into a superannuation account, animated infographic style" |
| 2 | 00:30-01:00 | Lịch sử super | "Timeline animation showing Australian superannuation history 1992 to 2026" |
| ... | ... | ... | ... |

### Bước 2: Gen Voiceover (TTS)

Dùng OpenAI TTS qua Nous Portal:

```
Có thể dùng terminal hoặc để em gen sau
Giọng: "alloy" (neutral English) hoặc "echo" (Australian-ish)
```

### Bước 3: Gen Video Clip (Seedance 2.0)

Mỗi cảnh gen 1 clip Seedance:
- Duration: 10-15s/clip
- Resolution: 720p (cân bằng chất lượng/giá)
- Tổng 30-40 clip/video

**Cách gen thủ công qua Hermes:**
```
🎬 Anh nói "Tạo video: [prompt]" → em sẽ gen từng clip
```

### Bước 4: Edit trong CapCut

1. Import TTS audio làm track chính
2. Xếp các clip Seedance theo thứ tự script
3. Căn chỉnh visual khớp với voiceover
4. Thêm text overlay cho số liệu quan trọng
5. Thêm background music (CapCut có sẵn free)
6. Export 1080p 30fps MP4

### Bước 5: Upload YouTube

1. Title: Tiêu đề video
2. Thumbnail: Đã gen sẵn
3. Description: Template SEO bên dưới
4. Tags: Từ khoá superannuation
5. Schedule: Thứ 3 hoặc Thứ 5, 8:00 AM AEST

---

## 🎯 SEO TEMPLATE (CHO MỖI VIDEO)

**Title:**
```
Australian Superannuation Explained: [VIDEO SUBJECT] (2026)
```

**Description template:**
```
[2-3 câu mô tả video]

In this video, we cover:
00:00 - [Section 1]
01:30 - [Section 2]
...

Resources mentioned:
- ATO Super Calculator: https://www.ato.gov.au/...
- myGov: https://my.gov.au

#australiansuper #superannuation #personalfinance #australia #retirementplanning #salarysacrifice #financialeducation
```

**Tags:**
```
australian superannuation, how super works australia, salary sacrifice australia, best super fund australia, superannuation explained, retirement australia, ATO super, financial education australia, personal finance australia
```

---

## ⏱ THỜI GIAN SẢN XUẤT ƯỚC TÍNH

| Công đoạn | Thời gian | Ghi chú |
|-----------|:---------:|---------|
| Script (em làm) | $0, vài phút | Đã có sẵn |
| TTS voiceover | 15 phút | Gen 10 phút audio |
| Gen clip Seedance | 45-60 phút | 30-40 clip, mỗi clip ~30s gen |
| Edit CapCut | 2-3 giờ | Công đoạn tốn thời gian nhất |
| Upload + SEO | 15 phút | |
| **Tổng/video** | **~3-4 giờ** | |

---

## 💰 CHI PHÍ CHI TIẾT (TỪ $10 ĐÃ NẠP)

### 4 video đầu tiên

| Khoản | Số lượng | Đơn giá | Thành tiền |
|-------|:--------:|:-------:|:---------:|
| Script | 4 | $0 | $0 |
| TTS voiceover | 120 phút | $0 (Nous Portal) | $0 |
| Seedance 2.0 clip | 160 clip (40/video) | $0.0147 | **$2.35** |
| Thumbnail Flux 2 Klein | 4 ảnh | $0.006 | $0.024 |
| **Tổng 4 video** | | | **~$2.37** |

### Còn lại trong $10

```
$10.00 - $2.37 = $7.63
→ Đủ cho ~13 video nữa (tổng 17 video)
```

---

## 🚀 AUTO HOÁ VỚI HERMES

Em có thể giúp anh nhiều phần trong quy trình này:

| Việc | Em làm được? |
|------|:-----------:|
| ✅ Viết script | ✅ Có — đã làm 4 script |
| ✅ Tạo thumbnail | ✅ Có — đã làm 4 thumbnail |
| ✅ Gen TTS voiceover | ✅ Có — qua Nous Portal |
| ✅ Gen clip Seedance | ✅ Có — từng câu lệnh |
| ❌ Edit CapCut | ❌ Anh tự làm |
| ❌ Upload YouTube | ❌ Anh tự làm |
| ⏰ Nhắc lịch xuất bản | ✅ Có — qua cron job Telegram |

---

## LỜI KHUYÊN KHI EDIT

1. **Đừng cố ghép clip hoàn hảo** — người xem không để ý transition đâu
2. **Âm thanh > Hình ảnh** — TTS chất lượng + music nền quan trọng hơn visual
3. **Text overlay số liệu** — mỗi khi đọc số, hiện chữ to trên màn hình
4. **Background music** — CapCut search "corporate", "cinematic", "documentary"
5. **Tốc độ nói** — 150-160 từ/phút, chậm hơn nói chuyện bình thường
6. **Hook 15 giây đầu** — quyết định retention rate

---

## NHẮC VIỆC

Anh có thể nhờ em:
- `/cron "mỗi thứ 3 và thứ 5" "Nhắc Quan đăng video YouTube kênh Úc"` 
- Gửi script tiếp theo
- Gen TTS cho script mới
- Gen Seedance clip theo danh sách prompt

---

*Production workflow — tạo ngày 08/07/2026 bởi Hermes Agent*  
*Dành riêng cho Quan Vũ — YouTube Niche Australia 🇦🇺*
