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
DWG_PAGE = {"M-101": 2, "M-103": 3, "M-104": 3, "M-105": 4, "M-106": 4}   # 도면 PDF 쪽 번호

B, H, E, Hh, R = P.BODY, P.HOUSING, P.ENDCAP, P.PCB_HOLDER, P.PCB_RING

# ── JLCCNC: 가공품 ──
CNC = [
    dict(part="HMT500-M-101", name="Process body", fn=M.body, step="HMT500-M-101_body.step",
         material="SUS316L (1.4404)", alt="SUS316 — 접액부이므로 316 계열 유지", finish="As machined + 부동태화 (ASTM A967), 버 제거",
         threads=f"{B['gthread']['thread']} 수나사 (x −14~−2); {B['mthread']['thread']} 수나사; "
                 f"{B['conn_thread']['thread']} 암나사 깊이 {B['conn_thread']['x'][1] - B['conn_thread']['x'][0]:g}; "
                 f"2×{B['holder_taps']['thread']} 깊이 {B['holder_taps']['depth']:g} (카운터보어 바닥, PCD {B['holder_taps']['pcd']:g})",
         tol="O링 자리 Ø29 f7, 커넥터 밀봉면 Ø10 H8, 나머지 ISO 2768-mK, 밀봉면 Ra 0.8",
         note="Ø7 관통 통로 길이 34 (깊은 구멍). 육각 AF27. 1개/세트"),
    dict(part="HMT500-M-103", name="Housing tube", fn=M.housing, step="HMT500-M-103_housing.step",
         material="SUS316L (1.4404)", alt="SUS304 (비접액부) 가능", finish="As machined + 부동태화, 외면 레이저 마킹 (문안 별도)",
         threads=f"앞 {H['thread']} (오른나사) 암나사 길이 {H['thread_len']:g}; 뒤 {H['thread_rear']} (왼나사 LH) 암나사 길이 {H['thread_len']:g}",
         tol="O링 자리 Ø29 H8 양 끝 (길이 4), 나머지 ISO 2768-mK",
         note="턴버클: 앞 오른나사 / 뒤 왼나사 — 주문 메모에 반드시 표기. 1개/세트"),
    dict(part="HMT500-M-104", name="End cap", fn=M.endcap, step="HMT500-M-104_endcap.step",
         material="SUS316L (1.4404)", alt="SUS304 가능", finish="As machined + 부동태화",
         threads=f"{E['mthread']['thread']} (왼나사 LH) 수나사; {E['thread']['thread']} 암나사 (M12 커넥터); "
                 f"2×{E['ports']['thread']} 관통 (r {E['ports']['r']:g}, 90°·270°)",
         tol="O링 자리 Ø29 f7 + 홈, 맞변 AF28, 나머지 ISO 2768-mK",
         note="왼나사 표기 필수. 1개/세트"),
    dict(part="HMT500-M-105", name="PCB holder", fn=M.pcb_holder, step="HMT500-M-105_holder.step",
         material="PEEK (자연색)", alt="시제품: POM (연속 약 100 °C) — 양산은 PEEK", finish="As machined, 버 제거",
         threads=f"2×M2 가로 탭 (PCB 고정, 홈에 수직); 2×Ø{Hh['screw_d']} 관통 + 카운터보어 Ø{Hh['cbore_d']:g} 깊이 {Hh['cbore_depth']:g}",
         tol=f"Ø{Hh['d']:g} (0/−0.1), 홈 폭 {Hh['slot_w']} (+0.1/0) 깊이 3.5, 창 {Hh['window']['wy']:g} × "
             f"{Hh['window']['z'][1] - Hh['window']['z'][0]:g} (+0.1/0)",
         note="Rev G: W-1 플러그 창 추가. 1개/세트"),
    dict(part="HMT500-M-106", name="PCB rear support ring", fn=M.pcb_ring, step="HMT500-M-106_ring.step",
         material="PEEK (자연색)", alt="시제품: POM", finish="As machined",
         threads="-",
         tol=f"Ø{R['od']:g} (0/−0.1), Ø{R['id']:g}, 홈 폭 {R['slot_w']} (+0.1/0) ×2, 홈 바닥 사이 {2 * R['slot_y']:g} (+0.2/0)",
         note="1개/세트"),
]


# English order data for JLCCNC (the drawings are in Korean — this sheet and QUOTE_REQUEST.txt carry the key specs)
CNC_EN = {
    "HMT500-M-101": dict(
        material="Stainless steel 316L (1.4404); 316 acceptable (wetted part)",
        finish="As machined, deburr, passivation (ASTM A967)",
        threads="G1/2-A (ISO 228-1) external; M28x1-6g external (right hand); M10x0.75-6H internal, depth 5.5; "
                "2x M2-6H tapped, depth 5, on counterbore bottom, PCD 16",
        tol="O-ring seat dia 29 f7; connector seal bore dia 10 H8; sealing faces Ra 0.8; others ISO 2768-mK",
        note="Through channel dia 7 x 34 long (deep hole). Hex AF27 with 30 deg chamfer."),
    "HMT500-M-103": dict(
        material="Stainless steel 316L (1.4404); 304 acceptable (not wetted)",
        finish="As machined, deburr, passivation; outer laser marking if available (text supplied later)",
        threads="Front: M28x1-6H internal, RIGHT hand, length 7; Rear: M28x1-LH-6H internal, LEFT hand, length 7",
        tol="O-ring bores dia 29 H8 at both ends (length 4), Ra 0.8, C0.5 lead-in chamfers; others ISO 2768-mK",
        note="Turnbuckle tube: front thread RIGHT hand, rear thread LEFT hand. Please confirm."),
    "HMT500-M-104": dict(
        material="Stainless steel 316L (1.4404); 304 acceptable",
        finish="As machined, deburr, passivation",
        threads="M28x1-LH-6g external, LEFT hand; M16x1.5-6H internal (connector); 2x M3 through (fill/vent ports, r10 at 90/270 deg)",
        tol="O-ring seat dia 29 f7 with groove, Ra 0.8; wrench flats AF28; others ISO 2768-mK",
        note="LEFT hand external thread. Please confirm."),
    "HMT500-M-105": dict(
        material="PEEK natural; POM acceptable for this prototype lot",
        finish="As machined, deburr",
        threads="2x M2 tapped cross holes (perpendicular to slot); 2x dia 2.2 through with counterbore dia 5.2 depth 2.2",
        tol="OD 21.6 (0/-0.1); slot width 1.7 (+0.1/0) depth 3.5; window 5.6 x 3.2 (+0.1/0); others ISO 2768-mK",
        note="Drawing sheet M-105~106 (holder at top right)."),
    "HMT500-M-106": dict(
        material="PEEK natural; POM acceptable for this prototype lot",
        finish="As machined, deburr",
        threads="-",
        tol="OD 26.4 (0/-0.1); ID 20; 2 slots width 1.7 (+0.1/0); slot bottoms 23.2 (+0.2/0) apart; thickness 4",
        note="Drawing sheet M-105~106 (ring at right)."),
}
NAME_EN = {"HMT500-M-101": "Process body", "HMT500-M-103": "Housing tube", "HMT500-M-104": "End cap",
           "HMT500-M-105": "PCB holder", "HMT500-M-106": "PCB rear support ring"}

RFQ = """Request for quotation - CNC machining (JLCCNC)
Project: HMT500(260313) oil moisture transmitter, prototype lot
Company: DOTECH Co., Ltd.
Drawing revision: {rev}   Date: {date}
Quantity: {sets} sets (1 of each part per set) - please also quote 10 and 50 sets if possible.

Files: one STEP (3D) and one PDF (2D) per part. The PDFs are in Korean; the key specs are listed below
and in order_jlccnc_EN.csv. Sheet M-102~104 also shows the filter cap M-102, which is NOT ordered.
Sheet M-105~106 also shows the PCB outline, which is NOT a machined part.

{parts}

General:
- Unspecified tolerances ISO 2768-mK. Break sharp edges 0.2-0.5 unless noted.
- Threads are modelled as plain cylinders in the STEP files; please cut threads per the callouts above.
- IMPORTANT: M-103 rear thread and M-104 thread are LEFT hand (M28x1-LH). M-103 front and M-101 are RIGHT hand.
- Fine / pipe threads: G1/2-A, M28x1, M10x0.75, M16x1.5. If a thread is not in your standard list, please advise.
- O-ring sealing surfaces (dia 29 f7 / H8, dia 10 H8): Ra 0.8, no tool marks across the seal.
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
    ("P-205", "O링 25 × 2, FKM 75", 2, "바디–하우징, 하우징–엔드캡 (반경 방향)"),
    ("P-208", "O링 8 × 1.2, FKM 75", 1, "HTX99R 커넥터"),
    ("P-203", "본디드 씰 G1/2 (21.5 × 28.7 × 2, 강 + FKM)", 1, "설치 나사 밀봉 — JLCMC에 없으면 유압 부품상"),
]

# ── LCSC: 하네스·샤시 선 부품 (LCSC 번호는 부품 조회 후 기입) ──
LC = [
    ("W-1", "JST SHR-04V-S (SH 1.0 mm 4P 하우징)", 1),
    ("W-1", "JST SSH-003T-P0.2-H (SH 콘택트, AWG 32–28)", 4),
    ("W-2", "JST GHR-08V-S (GH 1.25 mm 8P 하우징)", 1),
    ("W-2", "JST SSHL-002T-P0.2 (GH 콘택트, AWG 30–26)", 8),
    ("W-1", "PTFE 절연선 AWG 30 (UL1213 계열, 200 °C)", "4 × 60 mm"),
    ("W-2", "PTFE 절연선 AWG 28 (UL1213 계열)", "8 × 40 mm"),
    ("W-3", "PTFE 절연선 AWG 28 녹/황 또는 녹색", "1 × 25 mm"),
    ("W-3", "M2 링 단자, 비절연, AWG 28–22, 바깥 Ø4.5 이하, 두께 0.8 이하", 1),
]


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
    rows = []
    for c in CNC:
        shutil.copy(os.path.join(MECH, "out", c["step"]), os.path.join(d_cnc, c["step"]))
        pdf = f"{c['part']}_drawing_rev{REV}.pdf"
        pdf_page(DWG_PAGE[c["part"].replace("HMT500-", "")], os.path.join(d_cnc, pdf))
        rows.append([c["part"], c["name"], c["step"], pdf, c["material"], c["alt"], c["finish"], c["threads"], c["tol"],
                     SETS, c["note"]])
    rows_en, parts_txt = [], []
    for c in CNC:
        e = CNC_EN[c["part"]]
        rows_en.append([c["part"], NAME_EN[c["part"]], c["step"], f"{c['part']}_drawing_rev{REV}.pdf", e["material"],
                        e["finish"], e["threads"], e["tol"], SETS, e["note"]])
        parts_txt.append(f"{c['part']}  {NAME_EN[c['part']]}  x{SETS}\n  3D: {c['step']}   2D: {c['part']}_drawing_rev{REV}.pdf\n"
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
    write_csv(os.path.join(d_lc, "order_lcsc_harness.csv"), ["Harness", "Description", "Qty/set", "LCSC P/N"],
              [[h, dsc, q, "(조회 후 기입)"] for h, dsc, q in LC])
    print("jlccnc", len(CNC), "jlc3d", len(PRINT), "jlcmc", len(MC), "lcsc", len(LC))


if __name__ == "__main__":
    main()
