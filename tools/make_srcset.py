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

# Service-Thumbnails (Leistungen-Sektion, ~84px Anzeigegröße) -> deutlich kleinere Stufen,
# kein Grund das Handy 500px+ für ein 84px-Thumbnail laden zu lassen (Playbook Regel 3).
THUMB_STEPS = [160, 320]
THUMB_QUALITY = {160: 72, 320: 76}
# slug -> Quelldatei (svc-rasur/svc-kinderschnitt nutzen bewusst dieselben, bereits verifizierten
# Master wie die Atmosphäre-Sektion -- exakt dasselbe Motiv passt inhaltlich zur Leistung).
THUMB_SLUGS = {
    "svc-herrenschnitt": "svc-herrenschnitt",
    "svc-bartpflege": "svc-bartpflege",
    "svc-waschen": "svc-waschen",
    "svc-rasur": "atmo-bart",
    "svc-damenschnitt": "svc-damenschnitt",
    "svc-coloration": "svc-coloration",
    "svc-kinderschnitt": "atmo-kind",
}

# Bestehendes manifest.json laden statt zu überschreiben -- mehrere Slug-Gruppen leben darin.
manifest_path = f"{OUT}/manifest.json"
manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
total = 0


def process(slug, src_name, steps, quality):
    global total
    p = f"{SRC}/{src_name}.jpg"
    if not os.path.exists(p):
        print(f"!! Master fehlt: {slug} ({src_name}.jpg)")
        return
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    mw, mh = im.size
    made = []
    for w in steps:
        if w > mw:
            continue  # Master gibt diese Stufe nicht her -> nicht hochrechnen
        h = round(mh * (w / mw))
        out = im.resize((w, h), Image.LANCZOS)
        f = f"{OUT}/{slug}-{w}.webp"
        out.save(f, "WEBP", quality=quality.get(w, 76), method=6)
        kb = os.path.getsize(f) / 1024
        total += kb
        made.append({"w": w, "h": h, "kb": round(kb, 1)})
    if not made:
        print(f"!! keine Stufe erzeugt: {slug} (Master {mw}x{mh})")
        return
    manifest[slug] = {"master": [mw, mh], "sizes": made}
    print(f"{slug:20s} Master {mw}x{mh} -> " + ", ".join(f"{m['w']}({m['kb']:.0f}K)" for m in made))


for slug in SLUGS:
    process(slug, slug, STEPS, QUALITY)
for slug, src_name in THUMB_SLUGS.items():
    process(slug, src_name, THUMB_STEPS, THUMB_QUALITY)

json.dump(manifest, open(manifest_path, "w"), indent=1)
print(f"\n{len(manifest)} Bilder, {sum(len(v['sizes']) for v in manifest.values())} Dateien, {total/1024:.1f} MB (dieser Lauf)")
