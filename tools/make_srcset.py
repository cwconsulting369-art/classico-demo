#!/usr/bin/env python3
"""
Erzeugt aus den Mastern (raw/masters/) die responsiven Auslieferungsgrößen.

Kontext: ComfyUI/Tower waren beim Bau nicht erreichbar, deshalb kommen die
Master hier aus lizenzfreien Stock-Quellen (Pexels License, s. HTML-Kommentare
in src/index.html) statt aus eigener Generierung. Alle Master liegen bereits
deutlich über 3000px auf der langen Kante -> kein Hochrechnen nötig, wir
skalieren nur nach unten.

Mobile-first: Das Handy lädt die 500er-Datei, nicht den Master.
Kein serverseitiger Zuschnitt auf ein festes Seitenverhältnis -- das Bild
wird proportional verkleinert und der Browser croppt via object-fit:cover
passend zum jeweiligen Layout-Slot (sizes/srcset regeln nur die Breite).
"""
import os, json
from PIL import Image, ImageOps

SRC = "/home/carlos/projects/classico-friseursalon/raw/masters"
OUT = "/home/carlos/projects/classico-friseursalon/assets/img"
os.makedirs(OUT, exist_ok=True)

STEPS = [500, 900, 1800]
QUALITY = {500: 74, 900: 78, 1800: 82}

SLUGS = ["hero-atmosphaere", "story-handwerk", "atmo-bart", "atmo-kind", "atmo-tools"]

manifest = {}
total = 0
for slug in SLUGS:
    p = f"{SRC}/{slug}.jpg"
    if not os.path.exists(p):
        print(f"!! Master fehlt: {slug}")
        continue
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    mw, mh = im.size
    made = []
    for w in STEPS:
        if w > mw:
            continue  # Master gibt diese Stufe nicht her -> nicht hochrechnen
        h = round(mh * (w / mw))
        out = im.resize((w, h), Image.LANCZOS)
        f = f"{OUT}/{slug}-{w}.webp"
        out.save(f, "WEBP", quality=QUALITY.get(w, 78), method=6)
        kb = os.path.getsize(f) / 1024
        total += kb
        made.append({"w": w, "h": h, "kb": round(kb, 1)})
    if not made:
        print(f"!! keine Stufe erzeugt: {slug} (Master {mw}x{mh})")
        continue
    manifest[slug] = {"master": [mw, mh], "sizes": made}
    print(f"{slug:20s} Master {mw}x{mh} -> " + ", ".join(f"{m['w']}({m['kb']:.0f}K)" for m in made))

json.dump(manifest, open(f"{OUT}/manifest.json", "w"), indent=1)
print(f"\n{len(manifest)} Bilder, {sum(len(v['sizes']) for v in manifest.values())} Dateien, {total/1024:.1f} MB")
