#!/usr/bin/env python3
"""Assembly Hidden Japan Video #1 — Yakushima."""
import os, subprocess

BASE = "/data/data/com.termux/files/home/japan-channel/video1-clips"
AUDIO = "/data/data/com.termux/files/home/japan-channel/audio"
OUT = "/data/data/com.termux/files/home/japan-channel"
FONT = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"

# 12 clips with section labels
sections = [
    ("01-aerial.mp4",  "🌲 Ancient Forests of Yakushima"),
    ("02-jomon.mp4",   "🌳 Jomon Sugi — 7,000 Year Old Cedar"),
    ("03-trail.mp4",   "🥾 Hiking Through Sacred Forest"),
    ("04-forest.mp4",  "🎬 Princess Mononoke Inspiration"),
    ("05-rain.mp4",    "🌧️ The Rainiest Place on Earth"),
    ("06-monkeys.mp4", "🐒 Snow Monkeys of Jigokudani"),
    ("07-jigokudani.mp4","❄️ Winter at the Monkey Park"),
    ("08-cicada.mp4",  "🦗 The Song of Japanese Cicadas"),
    ("09-hashima-aerial.mp4","🏗️ Hashima — Battleship Island"),
    ("10-hashima-int.mp4","🏚️ Abandoned City"),
    ("11-hashima-sunset.mp4","🌅 Sunset Over Gunkanjima"),
    ("12-outro.mp4",   "📺 Hidden Japan Series"),
]

# Slow-mo + freeze per clip: 1s → 0.25x slow (4s) + 18s freeze = 22s
print("Creating extended clips (slow-mo + freeze)...")
for i, (clip, label) in enumerate(sections):
    inp = f"{BASE}/{clip}"
    out = f"{BASE}/ext_{i:02d}.mp4"
    subprocess.run([
        "ffmpeg","-y","-i",inp,
        "-vf","setpts=4*PTS,tpad=stop_mode=clone:stop_duration=18",
        "-c:v","libx264","-preset","ultrafast","-crf","26",
        out
    ], capture_output=True)
    print(f"  {i+1}/12 {label}")

# Concat with crossfade (2s)
inputs = []
for i in range(12):
    inputs.extend(["-i", f"{BASE}/ext_{i:02d}.mp4"])

# Build xfade filter chain
filters = []
for i in range(11):
    if i == 0:
        filters.append(f"[0][1]xfade=transition=fade:duration=2:offset=20[v{i:02d}]")
    else:
        filters.append(f"[v{i-1:02d}][{i+1}]xfade=transition=fade:duration=2:offset={20*(i+1)}[v{i:02d}]")

print("Concatenating with cross-fade...")
subprocess.run([
    "ffmpeg","-y"] + inputs + [
    "-filter_complex", ";".join(filters),
    "-map", f"[v09]",
    "-c:v","libx264","-preset","ultrafast","-crf","24","-pix_fmt","yuv420p",
    f"{BASE}/video-nosound.mp4"
], capture_output=True)

# Check duration
r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",f"{BASE}/video-nosound.mp4"], capture_output=True, text=True)
vid_dur = float(r.stdout.strip())
print(f"  Video: {vid_dur:.0f}s ({vid_dur/60:.1f} min)")

# Add TTS (2 parts concatenated)
print("Adding TTS voiceover...")
tts1 = f"{AUDIO}/tts-video-01-p1.ogg"
tts2 = f"{AUDIO}/tts-video-01-p2.ogg"

# Concat TTS parts
subprocess.run([
    "ffmpeg","-y","-i",tts1,"-i",tts2,
    "-filter_complex","[0][1]concat=n=2:v=0:a=1",
    "-c:a","aac","-b:a","128k",
    f"{BASE}/tts-full.mp3"
], capture_output=True)

# Get audio duration
r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",f"{BASE}/tts-full.mp3"], capture_output=True, text=True)
audio_dur = float(r.stdout.strip())
print(f"  Audio: {audio_dur:.0f}s")

# Add audio to video (omit -shortest to keep full video length)
subprocess.run([
    "ffmpeg","-y","-i",f"{BASE}/video-nosound.mp4","-i",f"{BASE}/tts-full.mp3",
    "-c:v","libx264","-preset","ultrafast","-crf","24",
    "-c:a","aac","-b:a","128k",
    "-map","0:v:0","-map","1:a:0",
    f"{BASE}/video-with-audio.mp4"
], capture_output=True)

# Add text overlays (section labels at bottom)
filters_text = []
for i, (_, label) in enumerate(sections):
    st = i * 22
    en = st + 22
    filters_text.append(
        f"drawtext=text='{label}':fontfile={FONT}:fontsize=24:fontcolor=white:"
        f"box=1:boxcolor=black@0.5:boxborderw=6:"
        f"x=(w-text_w)/2:y=h-60:enable='between(t,{st},{en})'"
    )

out_path = f"{OUT}/video-01-yakushima-final.mp4"
subprocess.run([
    "ffmpeg","-y","-i",f"{BASE}/video-with-audio.mp4",
    "-vf", ",".join(filters_text),
    "-c:v","libx264","-preset","ultrafast","-crf","24",
    "-c:a","copy",
    out_path
], capture_output=True)

r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",out_path], capture_output=True, text=True)
final_dur = float(r.stdout.strip())
mb = os.path.getsize(out_path)/(1024*1024)

print(f"\n{'='*50}")
print(f"✅ HIDDEN JAPAN — VIDEO #1 COMPLETE!")
print(f"📏 Duration: {final_dur:.0f}s ({final_dur/60:.1f} min)")
print(f"💾 Size: {mb:.1f}MB")
print(f"📁 {out_path}")
print(f"{'='*50}")

# Cleanup
for f in os.listdir(BASE):
    if f.startswith("ext_") or f in ["video-nosound.mp4","video-with-audio.mp4","tts-full.mp3"]:
        os.remove(f"{BASE}/{f}")
