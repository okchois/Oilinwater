"""재생성·검사된 A5의 제조 검토 자료를 내보낸다. 발주 승인은 아니다."""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/kicad/HMT500(ED260313A)/HMT500(ED260313A)'
p = argparse.ArgumentParser()
p.add_argument('--kicad-cli', default='kicad-cli')
p.add_argument('--revision', default='A5-R3')
p.add_argument('--output', type=Path, default=ROOT / 'manufacturing/jlc/artwork_A5_R3_review')
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
gerbers = out / 'gerbers'
gerbers.mkdir(exist_ok=True)
board = Path(str(BASE) + '.kicad_pcb')
drc = out / 'DRC.json'
subprocess.run([a.kicad_cli, 'pcb', 'drc', '--refill-zones', '--save-board', '--format', 'json', '-o', str(drc), str(board)], check=True)
r = json.loads(drc.read_text())
if r['unconnected_items'] or any(v['severity'] == 'error' for v in r['violations']):
    raise SystemExit('제조 검토 자료 생성 중단: DRC 또는 미연결 오류')
check = json.loads((BASE.parent / 'artwork_check.json').read_text())
if check['copper_layers'] != 6 or check['pad_net_errors'] or check['critical_track_errors']:
    raise SystemExit('A5 생성기 검사를 먼저 통과해야 합니다.')
subprocess.run([a.kicad_cli, 'pcb', 'export', 'gerbers', '--layers', 'F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts', '--subtract-soldermask', '-o', str(gerbers), str(board)], check=True)
subprocess.run([a.kicad_cli, 'pcb', 'export', 'drill', '--format', 'excellon', '--excellon-units', 'mm', '--excellon-separate-th', '--generate-report', '--report-path', str(out / 'drill_report.txt'), '-o', str(gerbers), str(board)], check=True)
copper_files = [f for f in gerbers.iterdir() if f.is_file() and 'TF.FileFunction,Copper,' in f.read_text(errors='replace')]
if len(copper_files) != 6:
    raise SystemExit(f'동박 거버 수 불일치: {len(copper_files)}')
for suffix in ('BOM_JLC.csv', 'CPL_JLC.csv'):
    shutil.copy2(ROOT / 'manufacturing/jlc/jlcpcb' / (BASE.name + '_' + suffix), out)
with (out / (BASE.name + '_BOM_JLC.csv')).open(encoding='utf-8-sig', newline='') as f:
    bom = list(csv.DictReader(f))
with (out / (BASE.name + '_CPL_JLC.csv')).open(encoding='utf-8-sig', newline='') as f:
    cpl = list(csv.DictReader(f))
bom_refs = [s.strip() for row in bom for s in row['Designator'].split(',')]
cpl_refs = [row['Designator'] for row in cpl]
if set(bom_refs) != set(cpl_refs) or len(bom_refs) != len(set(bom_refs)) or len(cpl_refs) != len(set(cpl_refs)):
    raise SystemExit('BOM/CPL 참조번호 불일치 또는 중복')
missing = [row['Designator'] for row in bom if not row['LCSC Part #'].strip()]
archive = out / f'{BASE.name}_{a.revision}_Gerber_제조검토용.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for file in sorted(gerbers.iterdir()):
        if file.is_file(): z.write(file, file.name)
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None: raise SystemExit('ZIP 검사 실패')
manifest = dict(revision=a.revision, status='MANUFACTURING REVIEW ONLY — ORDER ON HOLD', pcb_sha256=hashlib.sha256(board.read_bytes()).hexdigest(), drc_errors=0, unconnected=0, drc_warnings=len(r['violations']), bom_rows=len(bom), placement_count=len(cpl), missing_lcsc_designators=missing, files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(gerbers.iterdir()) if f.is_file()})
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(out / '먼저_읽으세요.txt').write_text(f'''HMT500 PCB {a.revision} — 제조 검토용, 주문 보류
6층 / 명목 1.6 mm / 최소 일반 비아 패드 0.30, 드릴 0.15 mm
In1 GND 전용, In4 GND 동박과 제한된 신호·전원 혼용
Gerber·드릴·BOM·CPL은 동일 PCB에서 생성했습니다.

주문 전 확인:
- 0.15 mm 관통 비아와 0.20 mm 이상 패드 위 비아의 충전·동도금 혼용 DFM
- 실제 적층/동박 두께 및 CPL 부품 방향, DNP/수삽 부품 처리
- LCSC 번호 61행 모두 지정(2026-10-03); JLC 재고/실장 가능 여부와 CPL 방향 확인
- 일부 레퍼런스 높이 0.6 mm / 선폭 0.1 mm: 고정밀 실크 인쇄성 확인 필요
- 제품 온도 사양 및 몰딩 재료
전원·AO 발열, 센서 정밀도, EMC/서지 합격은 실물 시험으로 확인해야 합니다.
이 ZIP 생성 또는 DRC 통과는 제조사 승인이나 발주 승인을 뜻하지 않습니다.
''')
print(json.dumps(manifest, ensure_ascii=False, indent=2))
