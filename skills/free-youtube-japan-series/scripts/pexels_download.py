#!/usr/bin/env python3
# pexels_download.py — Tải stock video free từ Pexels API
# Usage: python3 pexels_download.py

import os, json, urllib.request, subprocess, sys

API_KEY = "lotW8TmTEoCJJWfXlt95xjkKvVj5XTFzD6lji013D8mlohSaVkyhuT8h"
BASE = "https://api.pexels.com/videos/search"
OUT = os.path.dirname(os.path.abspath(__file__))

# Các query cho 3 video — mỗi query ~2 clips
QUERIES = {
    "v2_aokigahara": [
        "aokigahara forest",
        "japanese forest",
        "mount fuji forest",
        "japan nature",
    ],
    "v3_food": [
        "japanese food",
        "sushi preparation",
        "ramen bowl",
        "japan cuisine",
    ],
    "v4_zen": [
        "japanese garden",
        "zen garden",
        "kyoto temple",
        "zen meditation",
    ],
}

def search(query, per_page=5):
    url = f"{BASE}?query={urllib.parse.quote(query)}&per_page={per_page}"
    req = urllib.request.Request(url, headers={
        "Authorization": API_KEY,
        "User-Agent": "Mozilla/5.0 (compatible; PexelsDownloader/1.0)"
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def get_best_video(videos):
    """Pick video with HD (at least 1280x720) and longest duration."""
    best = None
    for v in videos:
        for f in v.get("video_files", []):
            if f.get("width", 0) >= 1280:
                if best is None or f.get("width", 0) > best.get("width", 0):
                    best = f
                    best["_id"] = v["id"]
                    best["_dur"] = v.get("duration", 0)
    return best

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        with open(path, "wb") as f:
            f.write(resp.read())

def main():
    import urllib.parse
    for vname, queries in QUERIES.items():
        out_dir = os.path.join(OUT, vname)
        os.makedirs(out_dir, exist_ok=True)
        print(f"\n📁 {vname}")
        count = 0
        for q in queries:
            try:
                data = search(q, per_page=4)
                videos = data.get("videos", [])
                if not videos:
                    print(f"  ⚠️ No results for: {q}")
                    continue
                best = get_best_video(videos)
                if not best:
                    print(f"  ⚠️ No HD for: {q}")
                    continue
                fname = f"{vname}_{count:02d}_{best['_id']}.mp4"
                fpath = os.path.join(out_dir, fname)
                download(best["link"], fpath)
                size = os.path.getsize(fpath)
                print(f"  ✅ {fname} ({best['width']}x{best['height']}, {best['_dur']}s, {size//1024}KB)")
                count += 1
            except Exception as e:
                print(f"  ⚠️ Error {q}: {e}")
        print(f"  → {count} clips downloaded")

if __name__ == "__main__":
    main()
