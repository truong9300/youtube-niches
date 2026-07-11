#!/usr/bin/env python3
# assemble.py — Ghép stock videos + TTS JP + subtitles cho Hidden Japan #2-4
# Usage: python3 assemble.py <num>

import os, subprocess, sys

JAPAN = "/data/data/com.termux/files/home/japan-channel"
AUDIO = os.path.join(JAPAN, "audio")
STOCK = os.path.join(JAPAN, "stock-v2")

# Config cho từng video
CONFIG = {
    "2": {
        "name": "v2_aokigahara",
        "audio": "tts-video-02-jp.ogg",
        "title": "Japan's Most Mysterious Forest - Aokigahara",
        "out": "video-02-aokigahara.mp4",
    },
    "3": {
        "name": "v3_food",
        "audio": "tts-video-03-jp.ogg",
        "title": "The Science of Japanese Food",
        "out": "video-03-food.mp4",
    },
    "4": {
        "name": "v4_zen",
        "audio": "tts-video-04-jp.ogg",
        "title": "The Secret of Zen Gardens",
        "out": "video-04-zen.mp4",
    },
}

def get_clips(folder):
    """Lấy danh sách clips, sắp xếp theo tên. Bỏ clip >200MB."""
    clips = []
    for f in sorted(os.listdir(folder)):
        if f.endswith(".mp4"):
            path = os.path.join(folder, f)
            size = os.path.getsize(path)
            if size > 200 * 1024 * 1024:  # Skip >200MB
                print(f"  ⚠️ Skip {f} ({size//1024//1024}MB)")
                continue
            clips.append(path)
    return clips

def analyze_clips(clips):
    """Lấy duration của từng clip."""
    durations = []
    for c in clips:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", c],
                            capture_output=True, text=True)
        try:
            durations.append(float(out.stdout.strip()))
        except:
            durations.append(10.0)
    return durations

def build_timeline(clips, durations, target_dur):
    """Chọn clips để kéo dài ~target_dur, lặp lại nếu cần."""
    timeline = []
    total = 0
    i = 0
    while total < target_dur:
        c = clips[i % len(clips)]
        d = durations[i % len(durations)]
        timeline.append((c, d))
        total += d
        i += 1
        if i > len(clips) * 3:  # safety
            break
    return timeline

def make_concat(timeline, out_path):
    """Tạo file concat + ghép (scale 1080p)."""
    # Tạo file list
    list_path = os.path.join(STOCK, "concat_list.txt")
    with open(list_path, "w") as f:
        for c, d in timeline:
            f.write(f"file '{c}'\n")
    
    # Concat với scale để đồng nhất resolution
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
                   "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                   "-c:v", "libx264", "-preset", "fast", "-crf", "23", out_path], check=True)

def add_slowmo(input_path, output_path, factor=1.5):
    """Thêm slow motion để kéo dài."""
    subprocess.run(["ffmpeg", "-y", "-i", input_path,
                   "-filter:v", f"setpts={factor}*PTS", "-an", output_path], check=True)

def main():
    num = sys.argv[1] if len(sys.argv) > 1 else "2"
    cfg = CONFIG[num]
    
    audio_path = os.path.join(AUDIO, cfg["audio"])
    stock_folder = os.path.join(STOCK, cfg["name"])
    out_path = os.path.join(JAPAN, cfg["out"])
    
    # Lấy audio duration
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                         "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                        capture_output=True, text=True)
    target = float(out.stdout.strip())
    print(f"🎯 Target duration: {target:.1f}s")
    
    # Lấy clips
    clips = get_clips(stock_folder)
    print(f"📁 Found {len(clips)} clips")
    durations = analyze_clips(clips)
    
    # Build timeline
    timeline = build_timeline(clips, durations, target)
    print(f"🎬 Timeline: {len(timeline)} segments")
    
    # Concat
    concat_path = os.path.join(STOCK, f"concat_{num}.mp4")
    make_concat(timeline, concat_path)
    print(f"✅ Concat done: {concat_path}")
    
    # Add slowmo để kéo dài ~1.5x
    slow_path = os.path.join(STOCK, f"slow_{num}.mp4")
    add_slowmo(concat_path, slow_path, factor=1.5)
    print(f"✅ Slowmo done")
    
    # Ghép audio + video
    subprocess.run(["ffmpeg", "-y", "-i", slow_path, "-i", audio_path,
                   "-c:v", "libx264", "-c:a", "aac", "-shortest", out_path], check=True)
    print(f"🎉 DONE: {out_path}")
    
    # Cleanup
    os.remove(concat_path)
    os.remove(slow_path)

if __name__ == "__main__":
    main()
