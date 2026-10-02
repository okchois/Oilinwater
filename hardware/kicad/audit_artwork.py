"""실제 PCB의 비아 치수, 보수적 POFV 후보, 접지/RTN 동박 면적 기록.

POFV 후보는 SMD 패드 바운딩 박스 겹침 기준이며 제조사 판정이 아니다.
폴리곤 개수는 면 내부의 연결 형상이며 신호 무결성/방열 시험을 대체하지 않는다.
"""
import csv
import json
from pathlib import Path
import pcbnew as p
import wx
from route_pcb import BASE

app = wx.App(False)
b = p.LoadBoard(str(BASE) + '.kicad_pcb')
rows, dims, areas, ground = [], {}, {}, {}
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA): continue
    x, y = p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)
    width, drill = p.ToMM(t.GetWidth(p.F_Cu)), p.ToMM(t.GetDrillValue())
    key = f'{width:.2f}/{drill:.2f}'
    dims[key] = dims.get(key, 0) + 1
    refs = []
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetAttribute() != p.PAD_ATTRIB_SMD or pad.GetNetname() != t.GetNetname(): continue
            bb = pad.GetBoundingBox()
            dx = max(p.ToMM(bb.GetX()) - x, 0, x - p.ToMM(bb.GetRight()))
            dy = max(p.ToMM(bb.GetY()) - y, 0, y - p.ToMM(bb.GetBottom()))
            if dx * dx + dy * dy < (width / 2) ** 2:
                refs.append(f.GetReference() + '.' + pad.GetNumber())
    if refs: rows.append([t.GetNetname(), x, y, width, drill, ';'.join(sorted(set(refs)))])
for z in b.Zones():
    if z.GetIsRuleArea(): continue
    layer = b.GetLayerName(z.GetLayer())
    poly = z.GetFilledPolysList(z.GetLayer())
    if z.GetNetname() == 'EF_RTN': areas[layer] = round(poly.Area() / 1e12, 3)
    if z.GetNetname() == 'GND' and layer in ('In1.Cu', 'In4.Cu'):
        ground[layer] = dict(filled_mm2=round(poly.Area() / 1e12, 3), polygon_count=poly.OutlineCount())
data = dict(via_dimensions=dims, via_count=sum(dims.values()), rtn_filled_mm2=areas, ground_planes=ground, possible_pofv=len(rows), possible_pofv_below_02=sum(row[4] < .2 for row in rows))
(BASE.parent / 'manufacturing_audit.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
with (BASE.parent / 'POFV_candidates.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['net', 'x_mm', 'y_mm', 'pad_mm', 'drill_mm', 'overlapping_SMD_pad'])
    writer.writerows(rows)
print(json.dumps(data, ensure_ascii=False))
