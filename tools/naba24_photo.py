#!/usr/bin/env python3
"""Fetch a free stock photo from Pixabay for a Naba24 post.

Usage: PIXABAY_KEY=... python3 naba24_photo.py "english search words" OUT.jpg [--exclude id1,id2]
Prints the chosen Pixabay id and page URL. Exit code 2 if nothing suitable was found.

Rules baked in: photos only, safesearch, landscape, min 1600px wide; skips any image whose
tags suggest identifiable people, alcohol, smoking, weapons or other unsuitable content, so
designs show places and objects only (no real persons).
"""
import os, sys, json, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Naba24 bot; +https://instagram.com/naba24h)"}

def get(u, t):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t)

BLOCK = {
    "man", "men", "woman", "women", "girl", "boy", "people", "person", "child", "children",
    "kid", "kids", "baby", "face", "portrait", "model", "businessman", "businesswoman",
    "couple", "family", "selfie", "crowd", "lady", "guy", "student", "worker", "hands", "hand",
    "alcohol", "whiskey", "brandy", "liquor", "wine", "beer", "cocktail", "drinking", "drunk",
    "smoking", "tobacco", "cigarette", "cigar", "vape", "weapon", "gun", "rifle", "blood",
    "religion", "mosque", "church", "temple", "flag", "bikini", "sexy", "nude", "casino",
    "gambling", "pig", "pork", "logo", "brand", "text",
}

def main():
    key = os.environ.get("PIXABAY_KEY")
    if not key:
        sys.exit("PIXABAY_KEY not set")
    q, out = sys.argv[1], sys.argv[2]
    exclude = set()
    if "--exclude" in sys.argv:
        exclude = set(sys.argv[sys.argv.index("--exclude") + 1].split(","))
    params = dict(key=key, q=q, image_type="photo", orientation="horizontal", safesearch="true",
                  min_width=1600, per_page=40, order="popular")
    url = "https://pixabay.com/api/?" + urllib.parse.urlencode(params)
    data = json.load(get(url, 20))
    for h in data.get("hits", []):
        tags = {t.strip().lower() for t in h.get("tags", "").split(",")}
        words = set(w for t in tags for w in t.split())
        if str(h["id"]) in exclude or (tags | words) & BLOCK:
            continue
        img = get(h["largeImageURL"], 30).read()
        with open(out, "wb") as f:
            f.write(img)
        print(json.dumps({"id": h["id"], "page": h.get("pageURL"), "tags": h.get("tags")}, ensure_ascii=False))
        return
    print("no suitable photo for: " + q, file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    main()
