#!/bin/sh
# 저장소 루트에서 실행. PCB 배치와 스냅샷이 다르면 복원을 중단한다.
# 이 파일의 성공은 제작 승인이 아니다. DRC 미연결/오류를 별도로 확인한다.
set -eu
export HMT_ARTWORK=${HMT_ARTWORK:-A5}
PY=${KICAD_PYTHON:-python3}
CLI=${KICAD_CLI:-kicad-cli}
TEST_PY=${TEST_PYTHON:-python3}
BASE='hardware/kicad/HMT500(260313A)/HMT500(260313A)'
python3 hardware/kicad/gen_hmt500.py
"$CLI" sch export netlist -o "$BASE.net" "$BASE.kicad_sch"
python3 hardware/kicad/check_netlist.py "$BASE.net"
"$CLI" sch export pdf -o "${BASE}_schematic.pdf" "$BASE.kicad_sch"
"$PY" hardware/kicad/make_parts_list.py
"$PY" hardware/kicad/place_pcb.py
"$PY" hardware/kicad/route_pcb.py prepare "${TMPDIR:-/tmp}/hmt500_artwork.dsn"
"$PY" hardware/kicad/artwork_snapshot.py restore "hardware/kicad/routing/artwork_${HMT_ARTWORK}_draft.json"
"$CLI" pcb drc --refill-zones --save-board --format json -o "${BASE}_artwork_drc.json" "$BASE.kicad_pcb"
"$PY" hardware/kicad/check_artwork.py
"$PY" hardware/kicad/audit_artwork.py
"$PY" manufacturing/jlc/make_jlcpcb_files.py
"$TEST_PY" hardware/kicad/plot_placement.py
"$TEST_PY" -m unittest discover -s tests
python3 - "$BASE" <<'PY'
import json,sys,os
from pathlib import Path
report=json.loads(Path(sys.argv[1]+'_artwork_drc.json').read_text())
errors=sum(q['severity']=='error' for q in report['violations'])
unconnected=len(report['unconnected_items'])
print(f'DRAFT: DRC errors={errors}, unconnected={unconnected}; NO FABRICATION RELEASE')
if errors or (os.environ.get('HMT_ARTWORK')=='A5' and unconnected):sys.exit(1)
PY
