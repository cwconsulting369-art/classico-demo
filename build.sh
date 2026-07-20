#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

rm -rf dist
mkdir -p dist

cp src/index.html src/impressum.html src/datenschutz.html src/style.css src/app.js dist/
mkdir -p dist/assets/img
cp assets/img/*.webp assets/img/manifest.json dist/assets/img/

echo "dist/ gebaut:"
echo "  HTML/CSS/JS: $(du -ch dist/*.html dist/*.css dist/*.js | tail -1 | cut -f1)"
echo "  Bilder:      $(du -sh dist/assets/img | cut -f1)"
echo "  Gesamt:      $(du -sh dist | cut -f1)"
