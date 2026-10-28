#!/usr/bin/env python3
"""Naba24 Reel renderer: animated 9:16 MP4 built from the same spec as naba24_render.py.

Usage: python3 naba24_reel.py spec.json OUT.mp4 [seconds=12]
Frames are captured deterministically (Web Animations currentTime) then encoded with ffmpeg.
"""
import os, sys, json, subprocess, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import naba24_render as R
from playwright.sync_api import sync_playwright

FPS = 30

ANIM_CSS = """
@keyframes zoom{from{transform:scale(1)}to{transform:scale(1.10)}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes up{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:none}}
@keyframes slideR{from{opacity:0;transform:translateX(120px) skewX(-14deg)}to{opacity:1;transform:skewX(-14deg)}}
@keyframes pop{0%{opacity:0;transform:scale(.6)}70%{opacity:1;transform:scale(1.06)}100%{opacity:1;transform:scale(1)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(215,20,26,.55)}50%{box-shadow:0 0 0 22px rgba(215,20,26,0)}}
.img svg{transform-origin:50% 40%;animation:zoom %(T)dms linear both}
.logo-img,.logo{animation:fade 500ms ease-out 0ms both}
.pill{animation:up 500ms ease-out 250ms both}
.badge{animation:slideR 450ms cubic-bezier(.2,.8,.2,1) 600ms both, pulse 1400ms ease-in-out 1200ms 6}
h1{animation:up 600ms ease-out 1000ms both}
h1 .r{animation:up 600ms ease-out 1600ms both}
.sub{animation:fade 600ms ease-out 2300ms both}
.stat:nth-child(1){animation:pop 500ms ease-out 3000ms both}
.stat:nth-child(2){animation:pop 500ms ease-out 3400ms both}
.stat:nth-child(3){animation:pop 500ms ease-out 3800ms both}
.foot{animation:fade 600ms ease-out 4500ms both}
"""

def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0
    T = int(secs * 1000)
    page_html = R.build(spec, 1080, 1920, True).replace("</style>", ANIM_CSS.replace("%(T)d", str(T)) + "</style>", 1)
    tmp = tempfile.mkdtemp(prefix="reel_")
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            pg = br.new_page(viewport={"width": 1080, "height": 1920})
            pg.set_content(page_html)
            pg.wait_for_timeout(300)
            pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
            n = int(secs * FPS)
            for i in range(n):
                t = i * 1000.0 / FPS
                pg.evaluate("t=>document.getAnimations().forEach(a=>{a.currentTime=t})", t)
                pg.screenshot(path=os.path.join(tmp, "f%04d.jpg" % i), type="jpeg", quality=90)
            br.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", os.path.join(tmp, "f%04d.jpg"),
                        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                        "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        "-c:a", "aac", "-b:a", "96k", out], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(out)

if __name__ == "__main__":
    main()
