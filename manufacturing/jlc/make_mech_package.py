"""JLC 주문용 기구 패키지 생성: JLCCNC(가공) · JLC3D(3D 프린트) · JLCMC(표준 기계 부품) · LCSC(하네스 부품).

  python manufacturing/jlc/make_mech_package.py      (cadquery 필요)
    → manufacturing/jlc/jlccnc/  STEP + 도면 PDF + order_jlccnc.csv
    → manufacturing/jlc/jlc3d/   STL + STEP + order_jlc3d.csv
    → manufacturing/jlc/jlcmc/   order_jlcmc.csv
    → manufacturing/jlc/lcsc/    order_lcsc_harness.csv

형상·치수는 hardware/mech (hmt500_params.py, hmt500_cad.py, 도면 PDF)에서 그대로 가져온다.
수량 SETS 는 시제품 가정값 — 주문 전에 바꾼다.
"""

import csv
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MECH = os.path.join(HERE, "..", "..", "hardware", "mech")
sys.path.insert(0, MECH)
import cadquery as cq  # noqa: E402

import hmt500_cad as M  # noqa: E402
import hmt500_params as P  # noqa: E402

SETS = 5                       # 시제품 세트 수 (가정)
REV = P.DRAWING_REV
DWG_PDF = os.path.join(MECH, "out", "HMT500_mechanical_drawings.pdf")
DWG_PAGE = {"M-101": 2, "M-102": 3, "M-103": 3, "M-104": 3, "M-105": 4, "M-106": 4}   # 도면 PDF 쪽 번호

B, H, E, Hh, R, C = P.BODY, P.HOUSING, P.ENDCAP, P.PCB_HOLDER, P.PCB_RING, P.CAP

# ── JLCCNC: 가공품 ──
CNC = [
    dict(part="HMT500-M-101", name="Process body", fn=M.body, step="HMT500-M-101_body.step",
         material="SUS304 (이번 시제품, JLCCNC 온라인 선택지)", alt="양산: SUS316L (1.4404) — 접액부", finish="As machined + 부동태화 (ASTM A967), 버 제거",
         threads=f"{B['gthread']['thread']} 수나사 (x −14~−2); {B['mthread']['thread']} 수나사; "
                 f"{B['conn_thread']['thread']} 암나사 깊이 {B['conn_thread']['x'][1] - B['conn_thread']['x'][0]:g}; "
                 f"2×{B['holder_taps']['thread']} 깊이 {B['holder_taps']['depth']:g} (카운터보어 바닥, PCD {B['holder_taps']['pcd']:g})",
         tol=f"O링 자리 Ø{B['seal']['d']:g} f7, 커넥터 밀봉면 Ø10 H8, 캡 칼라 Ø{B['cap_sleeve']['d']:g} (+0.1/0), 나머지 ISO 2768-mK, 밀봉면 Ra 0.8",
         note=f"Rev H: 칼라 Ø{B['collar']['d']:g}, 육각 AF27 × {B['hexa']['x'][1] - B['hexa']['x'][0]:g}. "
              f"G½ 앞면에 캡 칼라 Ø{B['cap_sleeve']['d']:g} × {B['cap_sleeve']['x'][1] - B['cap_sleeve']['x'][0]:g}. "
              f"Ø7 관통 통로 길이 {B['channel']['x'][1] - B['channel']['x'][0]:g}. 1개/세트"),
    dict(part="HMT500-M-102", name="Sensor protection cap (oil filter)", fn=M.cap, step="HMT500-M-102_cap.step",
         material="SUS304 (두텍 원도면 390000-001100 재질)", alt="SUS316L (접액부 통일 시)", finish="As machined + 부동태화, 버 제거 (구멍 안쪽 포함)",
         threads=f"{C['thread']} 암나사 깊이 {C['thread_x'][1] - C['thread_x'][0]:g} (HTX99R 위 나사, 두텍 확인)",
         tol=f"외경 Ø{C['od']:g}, 센서실 Ø{C['bore']:g}, 측면 {len(C['holes'])}×Ø{C['hole_d']:g} (5줄 × 5개, 72°), 끝 Ø{C['tip_hole']:g}, "
             f"끝 C{C['chamfer']:g}, 열린 끝 Ø{C['rear_relief']['d']:g} × 1, 나머지 ISO 2768-mK",
         note=f"두텍 390000-001100 (도면 2020-06-08) 기반, Rev H: 끝 쪽 {P.CAP_EXT:g} 연장 (전장 {C['x_rear'] - C['x_tip']:g}) + 옆 구멍 1줄. 1개/세트"),
    dict(part="HMT500-M-103", name="Housing tube", fn=M.housing, step="HMT500-M-103_housing.step",
         material="SUS304 (이번 시제품)", alt="양산: SUS316L 또는 SUS304 (비접액부)", finish="As machined + 부동태화, 외면 레이저 마킹 (문안 별도)",
         threads=f"앞 {H['thread']} (오른나사) 암나사 길이 {H['thread_len']:g}; 뒤 {H['thread_rear']} (왼나사 LH) 암나사 길이 {H['thread_len']:g}",
         tol=f"Ø{H['od']:g} / 안 Ø{H['id']:g}, O링 자리 Ø{H['seal_bore']:g} H8 양 끝 (길이 {H['seal_len']:g}), 나머지 ISO 2768-mK",
         note="턴버클: 앞 오른나사 / 뒤 왼나사 — 주문 메모에 반드시 표기. 1개/세트"),
    dict(part="HMT500-M-104", name="End cap", fn=M.endcap, step="HMT500-M-104_endcap.step",
         material="SUS304 (이번 시제품)", alt="양산: SUS316L 또는 SUS304", finish="As machined + 부동태화",
         threads=f"{E['mthread']['thread']} (왼나사 LH) 수나사; {E['thread']['thread']} 암나사 (M12 커넥터); "
                 f"2×{E['ports']['thread']} 깊이 4 / Ø2.5 관통 (입구 r {E['ports']['r']:g}, 90°·270°, 안쪽 경사 20°)",
         tol=f"O링 자리 Ø{E['seal']['d']:g} f7 + 홈, 플랜지 Ø{E['flange']['d']:g} 맞변 AF{E['flange']['flats_af']:g}, 나머지 ISO 2768-mK",
         note="왼나사 표기 필수. 1개/세트"),
    dict(part="HMT500-M-105", name="PCB holder", fn=M.pcb_holder, step="HMT500-M-105_holder.step",
         material="POM White (이번 시제품, JLCCNC 온라인)", alt="양산: PEEK", finish="As machined, 버 제거",
         threads=f"2×M2 가로 탭 (PCB 고정, 홈에 수직); 2×Ø{Hh['screw_d']} 관통 + 카운터보어 Ø{Hh['cbore_d']:g} 깊이 {Hh['cbore_depth']:g}",
         tol=f"Ø{Hh['d']:g} (0/−0.1), 홈 폭 {Hh['slot_w']} (+0.1/0) 깊이 3.5, 창 {Hh['window']['wy']:g} × "
             f"{Hh['window']['z'][1] - Hh['window']['z'][0]:g} (+0.1/0)",
         note="Rev G: W-1 플러그 창 추가. 1개/세트"),
    dict(part="HMT500-M-106", name="PCB rear support ring", fn=M.pcb_ring, step="HMT500-M-106_ring.step",
         material="POM White (이번 시제품)", alt="양산: PEEK", finish="As machined",
         threads="-",
         tol=f"Ø{R['od']:g} (0/−0.1), Ø{R['id']:g}, 홈 폭 {R['slot_w']} (+0.1/0) ×2, 홈 바닥 사이 {2 * R['slot_y']:g} (+0.2/0)",
         note="1개/세트"),
]


# English order data for JLCCNC (the drawings are in Korean — this sheet and QUOTE_REQUEST.txt carry the key specs)
CNC_EN = {
    "HMT500-M-101": dict(
        material="Stainless steel SUS304 for this prototype lot (316L for production)",
        finish="As machined, deburr, passivation (ASTM A967)",
        threads=f"G1/2-A (ISO 228-1) external; {B['mthread']['thread']} external (right hand); M10x1.0-6H internal, thread length 5.5 "
                "(ends 8.0 behind the connector seat face, after dia 11.2 x 1 counterbore and dia 10 H8 x 1.5 seal bore); "
                "2x M2-6H tapped, depth 5, on counterbore bottom, PCD 16",
        tol=f"O-ring seat dia {B['seal']['d']:g} f7; connector seal bore dia 10 H8; sealing faces Ra 0.8; others ISO 2768-mK",
        note="No front tube: the part starts with the G1/2 thread. Front sleeve bore dia 12.3 (+0.1/0) x 3.5 deep, "
             "machined into the G1/2 front face (holds the cap root against side load; connector seat face at its bottom). "
             f"Through channel dia 7 x {B['channel']['x'][1] - B['channel']['x'][0]:g} long. Hex AF27 x 10 long with 30 deg chamfer; "
             f"collar dia {B['collar']['d']:g}."),
    "HMT500-M-102": dict(
        material="Stainless steel SUS304 (wetted, oil)",
        finish="As machined, deburr inside and outside of all holes, passivation",
        threads=f"{C['thread']}-6H internal (fine pitch 1.0), depth {C['thread_x'][1] - C['thread_x'][0]:g} from the open end",
        tol=f"OD {C['od']:g}; bore dia {C['bore']:g}; {len(C['holes'])}x dia {C['hole_d']:g} radial holes "
            "(5 rows at 6.5/11.5/16.5/21.5/26.5 mm from the tip x 5 holes at 72 deg, same angles each row); tip hole dia 3; "
            "tip chamfer C1; open-end relief dia 11 x 1; others ISO 2768-mK",
        note=f"Filter cap screwed onto the sensor connector, overall length {C['x_rear'] - C['x_tip']:g}. "
             "Drawing sheet M-102~104 (cap at top)."),
    "HMT500-M-103": dict(
        material="Stainless steel SUS304",
        finish="As machined, deburr, passivation; outer laser marking if available (text supplied later)",
        threads=f"Front: {H['thread']} internal, RIGHT hand, length 7; Rear: {H['thread_rear']} internal, LEFT hand, length 7",
        tol=f"OD {H['od']:g}, ID {H['id']:g}, length {H['x'][1] - H['x'][0]:g}; O-ring bores dia {H['seal_bore']:g} H8 at both ends "
            "(length 4), Ra 0.8, C0.5 lead-in chamfers; others ISO 2768-mK",
        note="Turnbuckle tube: front thread RIGHT hand, rear thread LEFT hand. Please confirm."),
    "HMT500-M-104": dict(
        material="Stainless steel SUS304",
        finish="As machined, deburr, passivation",
        threads=f"{E['mthread']['thread']} external, LEFT hand; M16x1.5-6H internal, length 6 (connector, TENTATIVE - will be "
                "confirmed with the connector part number; please quote as M16x1.5); 2x M3 depth 4 mm, pilot dia 2.5 through, inclined 20 deg inward from axial direction (fill/vent ports, entry r11.8 at 90/270 deg)",
        tol=f"O-ring seat dia {E['seal']['d']:g} f7 with groove, Ra 0.8; flange dia {E['flange']['d']:g} x 4 with wrench flats "
            f"AF{E['flange']['flats_af']:g}; others ISO 2768-mK",
        note="LEFT hand external thread. Fill/vent access assumes connector shoulder OD <=20 and axial tool/nozzle OD <=2.5. Actual connector P/N must be confirmed before manufacture."),
    "HMT500-M-105": dict(
        material="POM (White) for this prototype lot (PEEK for production)",
        finish="As machined, deburr",
        threads="2x M2 tapped cross holes (perpendicular to slot); 2x dia 2.2 through with counterbore dia 5.2 depth 2.2",
        tol="OD 21.6 (0/-0.1); slot width 1.9 (+0.1/0) depth 3.5; window 5.6 x 3.3 (+0.1/0); others ISO 2768-mK",
        note="Drawing sheet M-105~106 (holder at top right)."),
    "HMT500-M-106": dict(
        material="POM (White) for this prototype lot (PEEK for production)",
        finish="As machined, deburr",
        threads="-",
        tol=f"OD {R['od']:g} (0/-0.1); ID 20; 2 slots width 1.9 (+0.1/0); slot bottoms 23.2 (+0.2/0) apart; thickness 4",
        note="Drawing sheet M-105~106 (ring at right)."),
}
TAG = {"HMT500-M-101": "SUS304", "HMT500-M-102": "SUS304", "HMT500-M-103": "SUS304", "HMT500-M-104": "SUS304",      # 이번 시제품: JLCCNC 온라인 선택지
       "HMT500-M-105": "POM-White", "HMT500-M-106": "POM-White"}
NAME_EN = {"HMT500-M-101": "Process body", "HMT500-M-102": "Sensor protection cap", "HMT500-M-103": "Housing tube", "HMT500-M-104": "End cap",
           "HMT500-M-105": "PCB holder", "HMT500-M-106": "PCB rear support ring"}

RFQ = """Request for quotation - CNC machining (JLCCNC)
Project: HMT500(260313) oil moisture transmitter, prototype lot
Company: DOTECH Co., Ltd.
Drawing revision: {rev}   Date: {date}
STATUS: DFM / prototype preparation only. Connector P/N, resin, pressure and temperature qualification remain open.
Quantity: {sets} sets (1 of each part per set) - please also quote 10 and 50 sets if possible.

TOLERANCE: STEP and PDF use the SAME nominal geometry (Rev I). The explicit drawing tolerances control.
  Seal spigots dia 27 f7, seal bores dia 27 H8, connector seal bore dia 10 H8, O-ring groove dia 24.6 h9.
  Holder/ring PCB slots: 1.9 (+0.1/0), for finished PCB thickness 1.6 +/-0.16.
  Do NOT substitute general +/-0.05 for these fits. Please confirm achievable tolerances and quote accordingly.
  If these tolerances cannot be met, request approval for a revised design before machining.

MATERIAL: NOT aluminium. The file names carry the material (SUS304 / POM-White). Please set it per part:
  M-101, M-102, M-103, M-104 = stainless steel (online option SUS304 accepted for this prototype lot; 316L preferred later);
  M-105, M-106 = POM (White) for this prototype lot (PEEK not offered online).

Files: one STEP (3D) and one PDF (2D) per part. The PDFs are in Korean; the key specs are listed below
and in order_jlccnc_EN.csv. Sheet M-102~104 carries three parts: cap M-102 (top), housing M-103, end cap M-104.
Sheet M-105~106 also shows the PCB outline, which is NOT a machined part.

{parts}

General:
- Unspecified tolerances ISO 2768-mK. Break sharp edges 0.2-0.5 unless noted.
- Threads are NOT modelled in the STEP files (cosmetic): internal threads are modelled at the minor diameter,
  external threads at the major diameter. Please cut threads per the callouts above and on the drawings.
- IMPORTANT: M-103 rear thread and M-104 thread are LEFT hand (M26x1-LH). M-103 front and M-101 are RIGHT hand.
- Fine / pipe threads: G1/2-A, M26x1, M10x1.0, M16x1.5. If a thread is not in your standard list, please advise.
- O-ring sealing surfaces (dia 27 f7 / H8, dia 10 H8): Ra 0.8, no tool marks across the seal.
- Material certificate EN 10204 3.1 for 316L (M-101 wetted part) if available.
- Please send DFM questions before machining.
"""

# ── JLC3D: 3D 프린트 ──
PRINT = [
    dict(part="HMT500-T-001", name="W-2 plug push bar (assembly tool)", fn=M.push_tool, qty=2,
         material="SLA 레진 (예: 8001) 또는 MJF PA12", note="조립 공구 (제품 아님). 끝 두께 3.0, 가운데 홈 10.4"),
    dict(part="HMT500-M-105", name="PCB holder — fit check", fn=M.pcb_holder, qty=2,
         material="SLA 레진 (고정밀)", note="선택: PEEK 가공 전 PCB·플러그 끼움 확인용"),
    dict(part="HMT500-M-106", name="Support ring — fit check", fn=M.pcb_ring, qty=2,
         material="SLA 레진 (고정밀)", note="선택: 가공 전 끼움 확인용"),
]

# ── JLCMC: 표준 기계 부품 (품번은 JLCMC 검색 후 기입) ──
MC = [
    ("P-207a", "M2×6 나사, A4-70, ISO 14580 (치즈머리 Torx) 또는 ISO 7380", 1, "홀더 → 바디 (아래)"),
    ("P-207b", "M2×8 나사, A4-70, ISO 14580", 1, "홀더 → 바디 (위, 샤시 링 단자 함께)"),
    ("P-207c", "M2×12 나사, A4-70, ISO 14580", 2, "PCB → 홀더 가로 고정 (벤치)"),
    ("P-210", "M3×3 무두나사 (ISO 4026 평끝), A4", 2, "엔드캡 몰딩 구멍 막음 (+ 실런트)"),
    ("P-205", "O링 24 × 1.5, FKM 75 (Rev H)", 2, "바디–하우징, 하우징–엔드캡 (반경 방향)"),
    ("P-208", "O링 8 × 1.2, FKM 75", 1, "HTX99R 커넥터"),
    ("P-203", "본디드 씰 G1/2 (21.5 × 28.7 × 2, 강 + FKM)", 1, "설치 나사 밀봉 — JLCMC에 없으면 유압 부품상"),
]

# ── LCSC: 하네스·샤시 선 부품 (LCSC 번호는 부품 조회 후 기입) ──
LC = [
    ("W-1", "JST SHR-04V-S (SH 1.0 mm 4P 하우징)", 1),
    ("W-1", "JST SSH-003T-P0.2-H (SH 콘택트, AWG 32–28)", 4),
    ("W-2", "JST GHR-08V-S (GH 1.25 mm 8P 하우징)", 1),
    ("W-2", "JST SSHL-002T-P0.2 (GH 콘택트, AWG 30–26)", 8),
    ("W-1", "PTFE 절연선 AWG 30 (UL1213 계열, 200 °C)", f"4 × {P.HARNESS['length']:g} mm"),
    ("W-2", "PTFE 절연선 AWG 28 (UL1213 계열)", f"8 × {P.HARNESS2['length']:g} mm"),
    ("W-3", "PTFE 절연선 AWG 28 녹/황 또는 녹색", "1 × 25 mm"),
    ("W-3", "M2 링 단자, 비절연, AWG 28–22, 바깥 Ø4.5 이하, 두께 0.8 이하", 1),
]


# Rev I: JLC 전용 치수 변환을 없앰. STEP/PDF/견적서가 같은 파라미터와 공차를 사용.

def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def pdf_page(page, out):
    tmp = out + ".tmp.pdf"
    subprocess.run(["pdfseparate", "-f", str(page), "-l", str(page), DWG_PDF, tmp], check=True)
    os.replace(tmp, out)


def main():
    d_cnc, d_3d, d_mc, d_lc = (os.path.join(HERE, x) for x in ("jlccnc", "jlc3d", "jlcmc", "lcsc"))
    for d in (d_cnc, d_3d, d_mc, d_lc):
        os.makedirs(d, exist_ok=True)
    for f in os.listdir(d_cnc):                      # 이전 이름 파일 정리
        if f.endswith((".step", ".pdf")):
            os.remove(os.path.join(d_cnc, f))
    rows = []
    for c in CNC:
        c["step"] = c["step"].replace(".step", f"_{TAG[c['part']]}.step")    # 파일 이름에 재질 (JLCCNC 기본값 알루미늄 방지)
        cq.exporters.export(c["fn"](), os.path.join(d_cnc, c["step"]))
        pdf = f"{c['part']}_drawing_rev{REV}_{TAG[c['part']]}.pdf"
        pdf_page(DWG_PAGE[c["part"].replace("HMT500-", "")], os.path.join(d_cnc, pdf))
        rows.append([c["part"], c["name"], c["step"], pdf, c["material"], c["alt"], c["finish"], c["threads"], c["tol"],
                     SETS, c["note"]])
    rows_en, parts_txt = [], []
    for c in CNC:
        e = CNC_EN[c["part"]]
        rows_en.append([c["part"], NAME_EN[c["part"]], c["step"], f"{c['part']}_drawing_rev{REV}_{TAG[c['part']]}.pdf", e["material"],
                        e["finish"], e["threads"], e["tol"], SETS, e["note"]])
        parts_txt.append(f"{c['part']}  {NAME_EN[c['part']]}  x{SETS}\n  3D: {c['step']}   2D: {c['part']}_drawing_rev{REV}_{TAG[c['part']]}.pdf\n"
                         f"  Material: {e['material']}\n  Finish: {e['finish']}\n  Threads: {e['threads']}\n"
                         f"  Tolerances: {e['tol']}\n  Note: {e['note']}")
    write_csv(os.path.join(d_cnc, "order_jlccnc_EN.csv"),
              ["Part", "Name", "3D (STEP)", "2D (PDF)", "Material", "Finish", "Threads", "Tolerance", "Qty", "Note"], rows_en)
    with open(os.path.join(d_cnc, "QUOTE_REQUEST.txt"), "w", encoding="utf-8") as f:
        f.write(RFQ.format(rev=REV, date=P.DATE, sets=SETS, parts="\n\n".join(parts_txt)))
    write_csv(os.path.join(d_cnc, "order_jlccnc.csv"),
              ["Part", "Name", "3D (STEP)", "2D (PDF)", "Material", "Alternative", "Finish", "Threads", "Tolerance",
               "Qty", "Note"], rows)
    rows = []
    for p in PRINT:
        base = f"{p['part']}_{p['name'].split(' —')[0].replace(' ', '_').replace('(', '').replace(')', '')}"
        s = p["fn"]()
        cq.exporters.export(s, os.path.join(d_3d, base + ".stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(s, os.path.join(d_3d, base + ".step"))
        rows.append([p["part"], p["name"], base + ".stl", p["material"], p["qty"], p["note"]])
    write_csv(os.path.join(d_3d, "order_jlc3d.csv"), ["Part", "Name", "File", "Material", "Qty", "Note"], rows)
    write_csv(os.path.join(d_mc, "order_jlcmc.csv"), ["Item", "Description", "Qty/set", "Qty total", "Use", "JLCMC P/N"],
              [[i, dsc, q, q * SETS, use, "(검색 후 기입)"] for i, dsc, q, use in MC])
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hardware", "kicad"))
    from make_parts_list import EXTRA_LCSC as PL_LCSC   # JST 하네스 부품 LCSC 번호 (결정 #34)
    write_csv(os.path.join(d_lc, "order_lcsc_harness.csv"), ["Harness", "Description", "Qty/set", "LCSC P/N"],
              [[h, dsc, q, next((v for k, v in PL_LCSC.items() if k in dsc), "(조회 후 기입)")] for h, dsc, q in LC])
    print("jlccnc", len(CNC), "jlc3d", len(PRINT), "jlcmc", len(MC), "lcsc", len(LC))


if __name__ == "__main__":
    main()
