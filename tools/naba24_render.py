#!/usr/bin/env python3
"""Naba24 (نبأ 24) post renderer.

Usage:  python3 naba24_render.py spec.json OUT_PREFIX
Produces OUT_PREFIX_feed.jpg (1080x1350) and OUT_PREFIX_story.jpg (1080x1920).

spec.json fields:
  topic      : pill text, e.g. "اقتصاد"
  scene      : one of trade | finance | oil | world | gov | tech | health | aviation
  line1      : headline first line (black)
  line2      : headline second line (red)
  sub        : short Reuters-style sub-line
  stats      : list of 3 {"value": "...", "label": "..."}
  source     : e.g. "وام"
  date       : e.g. "28 أكتوبر 2026"
Env: NABA_WINDOWS=0 disables building windows; NABA_Q sets JPEG quality (default 78).
"""
import json, sys, html
from playwright.sync_api import sync_playwright

RED = "#D7141A"
import os
WINDOWS = os.environ.get("NABA_WINDOWS","1")=="1"
QUALITY = int(os.environ.get("NABA_Q","78"))
import base64
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
FONTS = {  # name -> (regular file, bold file or None for variable font)
    "cairo": ("Cairo[slnt,wght].ttf", None),
    "almarai": ("Almarai-Regular.ttf", "Almarai-ExtraBold.ttf"),
    "plex": ("IBMPlexSansArabic-Regular.ttf", "IBMPlexSansArabic-Bold.ttf"),
    "kufi": ("NotoKufiArabic[wght].ttf", None),
}
FONT = os.environ.get("NABA_FONT", "almarai")

def font_css():
    if FONT not in FONTS: return ""
    reg, bold = FONTS[FONT]
    def face(fn, weight):
        path = os.path.join(FONT_DIR, fn)
        if not os.path.exists(path): return ""
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        return "@font-face{font-family:'NabaAr';src:url(data:font/ttf;base64,%s);font-weight:%s}" % (b64, weight)
    return face(reg, "100 900" if bold is None else "400") + (face(bold, "700") if bold else "")
INK = "#111111"

# ---------- illustration scenes (flat vector, 1080 x 1000 viewBox) ----------
SKY = """
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/>
 </linearGradient>
</defs>
<rect width="1080" height="1000" fill="url(#sky)"/>
"""

def skyline(y=620, c="#1d2b45", c2="#2a3d5e"):
    b = []
    xs = [(0,110,260),(100,90,330),(185,130,220),(310,70,410),(375,120,300),
          (490,60,520),(545,110,360),(650,90,280),(735,140,390),(870,80,250),(945,135,320)]
    for i,(x,w,h) in enumerate(xs):
        col = c if i % 2 else c2
        b.append(f'<rect x="{x}" y="{y-h}" width="{w}" height="{h+10}" fill="{col}"/>')
        for wy in range(y-h+25, y-10, 38):
            for wx in range(x+14, x+w-14, 26):
                if WINDOWS and (wx*7+wy) % 5: b.append(f'<rect x="{wx}" y="{wy}" width="10" height="16" fill="#f6c96b" opacity=".55"/>')
    # needle tower
    b.append(f'<polygon points="515,{y-520} 528,{y-520} 540,{y} 503,{y}" fill="{c}"/>')
    b.append(f'<rect x="519" y="{y-600}" width="5" height="80" fill="{c}"/>')
    return "".join(b)

def scene_trade():
    s = SKY.format(a="#f7a65c", b="#ffd9a8")
    s += '<circle cx="820" cy="300" r="95" fill="#fff1d6" opacity=".9"/>'
    s += skyline(560, "#3b3f5c", "#4a4f70")
    s += '<rect y="560" width="1080" height="440" fill="#1f5f8b"/>'
    for y in range(600, 1000, 45):
        s += f'<path d="M0 {y} Q 135 {y-12} 270 {y} T 540 {y} T 810 {y} T 1080 {y}" stroke="#4d8fbf" stroke-width="4" fill="none" opacity=".5"/>'
    # cranes
    for x in (90, 260):
        s += f'<rect x="{x}" y="300" width="22" height="270" fill="{RED}"/>'
        s += f'<rect x="{x-70}" y="300" width="220" height="20" fill="{RED}"/>'
        s += f'<line x1="{x+11}" y1="250" x2="{x-60}" y2="300" stroke="{RED}" stroke-width="6"/>'
        s += f'<line x1="{x+11}" y1="250" x2="{x+140}" y2="300" stroke="{RED}" stroke-width="6"/>'
        s += f'<line x1="{x+120}" y1="320" x2="{x+120}" y2="430" stroke="#333" stroke-width="4"/>'
    # ship
    s += '<polygon points="330,700 1010,700 960,800 380,800" fill="#22252e"/>'
    s += '<rect x="330" y="690" width="680" height="16" fill="#c0392b"/>'
    cols = ["#e74c3c","#2e86c1","#f39c12","#27ae60","#8e44ad","#16a085","#d35400"]
    i = 0
    for row in range(3):
        for x in range(400, 900, 62):
            s += f'<rect x="{x}" y="{640-row*48}" width="58" height="46" fill="{cols[i%7]}" stroke="#1a1a1a" stroke-width="2"/>'
            i += 3
    s += '<rect x="900" y="560" width="80" height="130" fill="#ecf0f1"/><rect x="910" y="575" width="60" height="18" fill="#2c3e50"/>'
    s += '<rect x="930" y="520" width="20" height="40" fill="#c0392b"/>'
    return s

def scene_finance():
    s = SKY.format(a="#0f1c3a", b="#28477a")
    s += skyline(760, "#0b1530", "#13234a")
    s += '<rect y="760" width="1080" height="240" fill="#0b1530"/>'
    pts = "60,640 200,560 320,600 450,450 580,500 720,330 860,380 1020,200"
    s += f'<polyline points="{pts}" fill="none" stroke="#2ecc71" stroke-width="14" stroke-linejoin="round" stroke-linecap="round"/>'
    s += '<polygon points="1020,200 975,215 1005,250" fill="#2ecc71"/>'
    for x,h in ((120,90),(240,140),(360,120),(480,200),(600,170),(720,260),(840,230),(960,320)):
        s += f'<rect x="{x}" y="{900-h}" width="70" height="{h}" fill="#f1c40f" opacity=".85"/>'
    return s

def scene_oil():
    s = SKY.format(a="#e9692c", b="#f8c471")
    s += '<circle cx="250" cy="330" r="110" fill="#fdebd0" opacity=".9"/>'
    s += '<rect y="640" width="1080" height="360" fill="#c27c3b"/>'
    s += '<path d="M0 640 Q 300 600 600 650 T 1080 630 L1080 1000 L0 1000Z" fill="#a8652c"/>'
    # pumpjack
    s += '<polygon points="560,640 640,420 720,640" fill="none" stroke="#222" stroke-width="16"/>'
    s += '<rect x="430" y="400" width="420" height="34" rx="8" fill="#222" transform="rotate(-10 640 417)"/>'
    s += '<path d="M420 360 q-40 60 0 140 l30 0 q-20-70 0-140z" fill="#222"/>'
    s += '<line x1="440" y1="480" x2="440" y2="640" stroke="#222" stroke-width="8"/>'
    # barrels
    for x in (780, 870, 825):
        y = 560 if x == 825 else 640
        s += f'<rect x="{x}" y="{y-90}" width="80" height="90" rx="8" fill="{RED}"/><rect x="{x}" y="{y-60}" width="80" height="8" fill="#8b0d11"/><rect x="{x}" y="{y-30}" width="80" height="8" fill="#8b0d11"/>'
    return s

def scene_world():
    s = SKY.format(a="#0d2a4a", b="#1d5a8c")
    s += '<circle cx="540" cy="520" r="330" fill="#2e86c1"/>'
    s += '<path d="M360 330 q80-60 160 -10 q40 60 -20 90 q-60 10 -60 70 q-40 40 -90 0 q-30 -80 10 -150z" fill="#27ae60"/>'
    s += '<path d="M600 420 q90 -30 150 40 q20 90 -60 120 q-60 50 -40 120 q-60 20 -80 -60 q-30 -110 30 -220z" fill="#27ae60"/>'
    s += '<path d="M420 640 q60 -10 90 40 q-10 60 -80 50 q-40 -40 -10 -90z" fill="#27ae60"/>'
    for r in (330, 250, 160):
        s += f'<ellipse cx="540" cy="520" rx="{r}" ry="330" fill="none" stroke="#fff" stroke-width="2" opacity=".25"/>'
    for y in (300, 420, 520, 620, 740):
        s += f'<line x1="210" y1="{y}" x2="870" y2="{y}" stroke="#fff" stroke-width="2" opacity=".2"/>'
    return s

def scene_gov():
    s = SKY.format(a="#5dade2", b="#d6eaf8")
    s += '<rect y="760" width="1080" height="240" fill="#d5c4a1"/>'
    s += '<polygon points="240,360 840,360 540,220" fill="#f4ecd8" stroke="#b9a37a" stroke-width="6"/>'
    s += '<rect x="250" y="360" width="580" height="30" fill="#e6d8b8"/>'
    for x in range(280, 820, 90):
        s += f'<rect x="{x}" y="390" width="44" height="330" fill="#f4ecd8" stroke="#c9b48a" stroke-width="3"/>'
    s += '<rect x="220" y="720" width="640" height="40" fill="#e6d8b8"/>'
    s += '<rect x="534" y="120" width="6" height="110" fill="#555"/>'
    s += '<rect x="540" y="120" width="40" height="80" fill="#00732f"/><rect x="540" y="146" width="40" height="27" fill="#fff"/><rect x="540" y="173" width="40" height="27" fill="#000"/><rect x="520" y="120" width="20" height="80" fill="#ff0000" transform="translate(20,0)"/>'
    return s

def scene_tech():
    s = SKY.format(a="#120b2e", b="#2b1b6b")
    for i in range(14):
        x, y = 80 + (i*73) % 920, 150 + (i*131) % 600
        s += f'<circle cx="{x}" cy="{y}" r="10" fill="#7fdbff"/>'
        x2, y2 = 80 + ((i+3)*73) % 920, 150 + ((i+3)*131) % 600
        s += f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="#7fdbff" stroke-width="3" opacity=".4"/>'
    s += '<rect x="390" y="370" width="300" height="300" rx="30" fill="#1b2a49" stroke="#7fdbff" stroke-width="8"/>'
    s += '<rect x="450" y="430" width="180" height="180" rx="14" fill="#7fdbff" opacity=".3"/>'
    for k in range(5):
        o = 400 + k*60
        s += f'<line x1="{o}" y1="330" x2="{o}" y2="370" stroke="#7fdbff" stroke-width="8"/><line x1="{o}" y1="670" x2="{o}" y2="710" stroke="#7fdbff" stroke-width="8"/>'
        s += f'<line x1="350" y1="{o-20}" x2="390" y2="{o-20}" stroke="#7fdbff" stroke-width="8"/><line x1="690" y1="{o-20}" x2="730" y2="{o-20}" stroke="#7fdbff" stroke-width="8"/>'
    return s

def scene_health():
    s = SKY.format(a="#a3e4d7", b="#e8f8f5")
    s += '<rect x="440" y="250" width="200" height="500" rx="20" fill="#fff" stroke="#16a085" stroke-width="8"/>'
    s += f'<rect x="290" y="400" width="500" height="200" rx="20" fill="#fff" stroke="#16a085" stroke-width="8"/>'
    s += f'<rect x="460" y="270" width="160" height="460" rx="12" fill="{RED}"/><rect x="310" y="420" width="460" height="160" rx="12" fill="{RED}"/>'
    s += '<path d="M60 860 L300 860 L340 790 L390 930 L440 820 L470 860 L1020 860" stroke="#16a085" stroke-width="10" fill="none"/>'
    return s

def scene_aviation():
    s = SKY.format(a="#2e86c1", b="#aed6f1")
    for cx, cy in ((200,250),(820,180),(650,420)):
        s += f'<ellipse cx="{cx}" cy="{cy}" rx="120" ry="40" fill="#fff" opacity=".8"/>'
    s += skyline(860, "#2c3e50", "#34495e")
    s += '<g transform="rotate(-12 540 480)">'
    s += '<rect x="250" y="450" width="600" height="70" rx="35" fill="#f8f9f9"/>'
    s += '<polygon points="480,480 640,480 760,330 700,330" fill="#d0d3d4"/>'
    s += '<polygon points="480,500 640,500 760,660 700,660" fill="#b3b6b7"/>'
    s += f'<polygon points="270,470 330,470 300,360 250,360" fill="{RED}"/>'
    s += '<rect x="560" y="470" width="260" height="14" fill="#2e86c1" opacity=".6"/>'
    s += '</g>'
    return s

SCENES = dict(trade=scene_trade, finance=scene_finance, oil=scene_oil, world=scene_world,
              gov=scene_gov, tech=scene_tech, health=scene_health, aviation=scene_aviation)

LOGO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo.png")
if os.path.exists(LOGO_FILE):
    LOGO = '<img class="logo-img" src="data:image/png;base64,%s">' % base64.b64encode(open(LOGO_FILE, "rb").read()).decode()
else:
    LOGO = f"""<div class="logo"><div class="logo-in"><span class="l1">نبأ</span><span class="l2">24</span></div></div>"""

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:%(W)dpx;height:%(H)dpx;background:#fff;font-family:'NabaAr','DejaVu Sans',sans-serif;direction:rtl;overflow:hidden;position:relative}
.img{position:absolute;top:0;left:0;width:%(W)dpx;height:%(IH)dpx;overflow:hidden}
.img svg{width:100%%;height:100%%}
.img:after{content:'';position:absolute;left:0;right:0;bottom:0;height:120px;background:linear-gradient(to bottom,rgba(255,255,255,0),#fff)}
.logo{position:absolute;top:40px;left:40px;width:150px;height:150px;border-radius:50%%;background:#fff;box-shadow:0 6px 20px rgba(0,0,0,.25);display:flex;align-items:center;justify-content:center}
.logo-in{width:132px;height:132px;border-radius:50%%;background:%(RED)s;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;line-height:1}
.l1{font-size:50px;font-weight:bold}.l2{font-size:34px;font-weight:bold;margin-top:4px;direction:ltr}
.logo-img{position:absolute;top:34px;left:34px;width:180px;height:180px;border-radius:50%%;box-shadow:0 6px 22px rgba(0,0,0,.35)}
.pill{position:absolute;top:66px;right:40px;background:rgba(17,17,17,.85);color:#fff;font-size:34px;font-weight:bold;padding:14px 36px;border-radius:60px}
.content{position:absolute;top:%(CT)dpx;right:60px;left:60px}
.badge{display:inline-block;background:%(RED)s;color:#fff;font-weight:bold;font-size:%(BF)dpx;padding:12px 40px;transform:skewX(-14deg);margin-bottom:%(GAP)dpx}
.badge span{display:inline-block;transform:skewX(14deg)}
h1{font-size:%(HF)dpx;line-height:1.3;font-weight:800;color:%(INK)s;font-weight:bold}
h1 .r{color:%(RED)s;display:block}
.sub{font-size:%(SF)dpx;color:#555;margin-top:%(GAP2)dpx;line-height:1.5}
.stats{display:flex;gap:22px;margin-top:%(GAP)dpx}
.stat{flex:1;border:3px solid #eee;border-top:8px solid %(RED)s;border-radius:14px;padding:%(SP)dpx 10px;text-align:center;background:#fafafa}
.stat .v{unicode-bidi:plaintext;font-size:%(VF)dpx;font-weight:bold;color:%(INK)s;line-height:1.2}
.stat .lb{font-size:%(LF)dpx;color:#666;margin-top:8px;line-height:1.35}
.foot{position:absolute;bottom:%(FB)dpx;right:60px;left:60px;display:flex;justify-content:space-between;align-items:center;border-top:3px solid #eee;padding-top:22px;font-size:28px;color:#444}
.foot b{color:%(RED)s}
"""

def build(spec, W, H, story):
    IH = 900 if story else 640
    p = dict(W=W, H=H, IH=IH, RED=RED, INK=INK,
             CT=(830 if story else 560), BF=(46 if story else 38), GAP=(48 if story else 36),
             GAP2=(24 if story else 14), HF=(84 if story else 74), SF=(44 if story else 36),
             SP=(48 if story else 34), VF=(62 if story else 54), LF=(31 if story else 29),
             FB=(90 if story else 40))
    import re
    def e(t):
        t = html.escape(t)
        return re.sub(r'([+\-\u2212]?\d[\d.,]*%?)', r'<span dir="ltr" style="unicode-bidi:isolate">\1</span>', t)
    stats = "".join(f'<div class="stat"><div class="v">{e(s["value"])}</div><div class="lb">{e(s["label"])}</div></div>' for s in spec["stats"][:3])
    svg = f'<svg viewBox="0 {250 if not story else 60} 1080 {640 if not story else 900}" preserveAspectRatio="xMidYMid slice">{SCENES.get(spec.get("scene","world"), scene_world)()}</svg>'
    return f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>{font_css()}{CSS % p}</style></head><body>
<div class="img">{svg}</div>{LOGO}<div class="pill">{e(spec['topic'])}</div>
<div class="content"><div class="badge"><span>خبر عاجل</span></div>
<h1>{e(spec['line1'])}<span class="r">{e(spec['line2'])}</span></h1>
<div class="sub">{e(spec['sub'])}</div><div class="stats">{stats}</div></div>
<div class="foot"><span>المصدر: <b>{e(spec['source'])}</b></span><span>{e(spec['date'])}</span></div>
</body></html>"""

def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for name, W, H, story in (("feed", 1080, 1350, False), ("story", 1080, 1920, True)):
            pg = br.new_page(viewport={"width": W, "height": H})
            pg.set_content(build(spec, W, H, story))
            pg.wait_for_timeout(200)
            pg.screenshot(path=f"{out}_{name}.jpg", type="jpeg", quality=QUALITY, full_page=False)
            pg.close()
        br.close()
    print(f"{out}_feed.jpg {out}_story.jpg")

if __name__ == "__main__":
    main()
