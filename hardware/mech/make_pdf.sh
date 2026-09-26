#!/bin/bash
# SVG 도면 → 한 개의 PDF (A3 가로 4쪽) + 미리보기 PNG
set -e
cd "$(dirname "$0")/out"
CHROME=${CHROME:-/opt/pw-browsers/chromium-1194/chrome-linux/chrome}
cat > _dwg.html <<HTML
<html><head><meta charset="utf-8"><style>@page{size:420mm 297mm;margin:0}body{margin:0}
img{width:420mm;height:297mm;display:block;page-break-after:always}</style></head><body>
<img src="HMT500-M-000_assembly.svg"><img src="HMT500-M-101_body.svg"><img src="HMT500-M-102-104_parts.svg"><img src="HMT500-M-105-106_pcb.svg">
</body></html>
HTML
"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=HMT500_mechanical_drawings.pdf "file://$PWD/_dwg.html" 2>/dev/null
rm -f _dwg.html
echo "HMT500_mechanical_drawings.pdf"
