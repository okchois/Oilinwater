#!/bin/sh
# 거버·드릴 출력: 파일명 = 프로젝트 번호 HMT500(ED260313A)
#   sh hardware/kicad/export_gerbers.sh  →  hardware/kicad/HMT500(ED260313A)/gerber/HMT500(ED260313A)-*.g*, .drl
#                                           hardware/kicad/HMT500(ED260313A)/HMT500(ED260313A).zip (제작 의뢰용)
set -e
P="HMT500(ED260313A)"
D="$(dirname "$0")/$P"
rm -rf "$D/gerber" && mkdir -p "$D/gerber"
kicad-cli pcb export gerbers -l "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" \
    -o "$D/gerber/" "$D/$P.kicad_pcb"
kicad-cli pcb export drill -o "$D/gerber/" "$D/$P.kicad_pcb"
rm -f "$D/$P.zip"
(cd "$D/gerber" && python3 -c "import zipfile,glob,sys; z=zipfile.ZipFile(sys.argv[1],'w',zipfile.ZIP_DEFLATED); [z.write(f) for f in sorted(glob.glob('*'))]" "../$P.zip")
echo "$D/$P.zip"
