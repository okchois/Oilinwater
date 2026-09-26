"""HMT500 구매용 부품리스트 생성 (회로도 BOM + 제조사 품번·단가 가정).

  python3 hardware/kicad/gen_hmt500.py        # 먼저 회로도·HMT500_BOM.csv 생성
  python3 hardware/kicad/make_parts_list.py   # → HMT500/HMT500_parts_list.xlsx, .csv

- 회로도 부품(참조번호·수량·값·풋프린트)은 HMT500_BOM.csv 에서 그대로 읽는다. 여기서는 품번과 단가만 붙인다.
- 수동소자 품번은 "제안" (동등품 대체 가능). 단가는 1k 기준 추정값이며 견적으로 확정한다.
- 회로도에 없지만 1대분에 필요한 전자 부품(PCB, 센서, 커넥터 등)은 EXTRA 로 덧붙인다.
"""

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(HERE, "HMT500")
FX = 1400  # 원/달러 가정

# (심볼, 값) → (분류, 제조사, 품번, 설명, 단가 USD 하한, 상한, 상태)
# 상태: 확정 / 제안(동등품 가능) / 확인 필요 / TBD
MAP = {
    ("C", "100n 100V"): ("수동", "Murata", "GRM21BR72A104KA35L", "MLCC 100 nF 100 V X7R 0805", 0.02, 0.05, "제안"),
    ("C", "10u 50V"): ("수동", "Murata", "GRM32ER71H106KA12L", "MLCC 10 uF 50 V X7R 1210", 0.15, 0.35, "제안"),
    ("C", "4.7n 2kV Y2"): ("보호", "Murata", "GA343QR7GF472KW01L", "Safety cap 4.7 nF Y2 (250 VAC) 1812", 0.15, 0.40, "제안"),
    ("C", "22n"): ("수동", "Murata", "GRM188R71H223KA01D", "MLCC 22 nF 50 V X7R 0603", 0.004, 0.01, "제안"),
    ("C", "2.2u 100V"): ("수동", "Murata", "GRM32ER72A225KA35L", "MLCC 2.2 uF 100 V X7R 1210", 0.15, 0.35, "제안"),
    ("C", "100n"): ("수동", "Murata", "GRM188R71H104KA93D", "MLCC 100 nF 50 V X7R 0603", 0.004, 0.01, "제안"),
    ("C", "1u"): ("수동", "Murata", "GRM188R61E105KA12D", "MLCC 1 uF 25 V X5R 0603", 0.005, 0.015, "제안"),
    ("C", "22u 10V"): ("수동", "Murata", "GRM21BR61A226ME44L", "MLCC 22 uF 10 V X5R 0805", 0.04, 0.10, "제안"),
    ("C", "10u"): ("수동", "Murata", "GRM21BR61E106KA73L", "MLCC 10 uF 25 V X5R 0805", 0.03, 0.08, "제안"),
    ("C", "4.7u"): ("수동", "Murata", "GRM21BR61E475KA12L", "MLCC 4.7 uF 25 V X5R 0805", 0.02, 0.06, "제안"),
    ("C", "220p C0G 1%"): ("측정", "Murata", "GRM1885C1H221FA01D", "MLCC 220 pF 50 V C0G ±1% 0603 (PCAP04 기준 C)", 0.01, 0.04, "제안"),
    ("C", "10n"): ("수동", "Murata", "GRM188R71H103KA01D", "MLCC 10 nF 50 V X7R 0603", 0.003, 0.01, "제안"),
    ("C", "1n 100V"): ("보호", "Murata", "GRM188R72A102KA01D", "MLCC 1 nF 100 V X7R 0603", 0.004, 0.01, "제안"),
    ("C", "100n 50V"): ("수동", "Murata", "GRM21BR71H104KA01L", "MLCC 100 nF 50 V X7R 0805", 0.01, 0.03, "제안"),
    ("C", "4.7u 50V"): ("수동", "Murata", "GRM32ER71H475KA88L", "MLCC 4.7 uF 50 V X7R 1210", 0.10, 0.25, "제안"),
    ("TVS_BI", "SMDJ36CA"): ("보호", "Littelfuse", "SMDJ36CA", "TVS 3000 W 36 V 양방향 SMC (입력 1단)", 0.25, 0.60, "제안"),
    ("TVS_BI", "SMBJ33CA"): ("보호", "Littelfuse", "SMBJ33CA", "TVS 600 W 33 V 양방향 SMB (입력 2단)", 0.08, 0.20, "제안"),
    ("TVS_BI", "SMAJ33CA"): ("보호", "Littelfuse", "SMAJ33CA", "TVS 400 W 33 V 양방향 SMA (아날로그 출력)", 0.06, 0.15, "제안"),
    ("TVS_BI", "SMAJ40CA (opt.)"): ("보호", "Littelfuse", "SMAJ40CA", "TVS 400 W 40 V 양방향 SMA (RS-485, 옵션)", 0.06, 0.15, "제안"),
    ("LED", "green"): ("표시", "Würth", "150060GS75000", "LED 녹색 0603", 0.03, 0.08, "제안"),
    ("FB", "600R@100MHz"): ("수동", "Murata", "BLM18KG601SN1D", "페라이트 비드 600 Ω@100 MHz 0603", 0.01, 0.03, "제안"),
    ("GDT", "GDT 230V"): ("보호", "Bourns", "2038-23-SM-RPLF", "GDT 230 V SMD (회로 GND–외함)", 0.40, 1.00, "확인 필요"),
    ("CONN_M8", "M Connect 8P male"): ("커넥터", "M Connect", "TBD (두텍 사용품)", "M12 8핀 수컷 전면 장착형, M16×1.5", 2.0, 10.0, "TBD"),
    ("CONN_SWD", "TC2030-IDC-NL"): ("생산", "Tag-Connect", "(PCB 패드만)", "SWD 기록용 패드 — 부품 실장 없음", 0.0, 0.0, "확정"),
    ("CONN_PROBE", "Feedthrough 6P"): ("기구", "TBD", "HMT500-P-201", "유리-금속 피드스루 6핀 (기구 부품, 바디에 용접)", 0.0, 0.0, "TBD"),
    ("CMC", "CMC 2x1mH 0.3A"): ("보호", "Würth", "WE-SL2 계열 (품번 확인)", "공통모드 초크 2×1 mH, ≥0.3 A", 0.30, 0.80, "확인 필요"),
    ("L", "22uH"): ("전원", "Coilcraft", "XGL4030-223ME (확인)", "파워 인덕터 22 uH, 4×4 mm, Isat ≥ 0.8 A", 0.25, 0.60, "확인 필요"),
    ("R", "4.7R 1W pulse"): ("보호", "Vishay", "MMB 0207 4.7 Ω (품번 확인)", "MELF 펄스 저항 4.7 Ω 1 W (입력 직렬)", 0.10, 0.30, "확인 필요"),
    ("R", "1M"): ("수동", "Yageo", "RC0603FR-071ML", "저항 1 MΩ 1% 0603", 0.002, 0.005, "제안"),
    ("R", "866k 1%"): ("전원", "Yageo", "RC0603FR-07866KL", "저항 866 kΩ 1% 0603 (UVLO)", 0.002, 0.005, "제안"),
    ("R", "97.6k 1%"): ("전원", "Yageo", "RC0603FR-0797K6L", "저항 97.6 kΩ 1% 0603 (UVLO/OVP)", 0.002, 0.005, "제안"),
    ("R", "36.5k 1%"): ("전원", "Yageo", "RC0603FR-0736K5L", "저항 36.5 kΩ 1% 0603 (OVP)", 0.002, 0.005, "제안"),
    ("R", "R_ILIM *"): ("전원", "Yageo", "RC0603FR-07 (값 TBD)", "저항 1% 0603 — TPS2660 전류제한 150 mA 값 계산 필요", 0.002, 0.005, "TBD"),
    ("R", "10k"): ("수동", "Yageo", "RC0603FR-0710KL", "저항 10 kΩ 1% 0603", 0.002, 0.005, "제안"),
    ("R", "100k 1%"): ("전원", "Yageo", "RC0603FR-07100KL", "저항 100 kΩ 1% 0603 (벅 FB)", 0.002, 0.005, "제안"),
    ("R", "24.9k 1%"): ("전원", "Yageo", "RC0603FR-0724K9L", "저항 24.9 kΩ 1% 0603 (벅 FB)", 0.002, 0.005, "제안"),
    ("R", "1k"): ("수동", "Yageo", "RC0603FR-071KL", "저항 1 kΩ 1% 0603", 0.002, 0.005, "제안"),
    ("R", "4.02k 0.01% 5ppm"): ("측정", "Vishay / Susumu", "0.01% 5 ppm 박막 (품번 확인)", "Pt1000 기준저항 4.02 kΩ 0.01% 5 ppm/K 0603", 1.00, 4.00, "확인 필요"),
    ("R", "10R pulse"): ("보호", "Vishay", "CRCW251210R0FKEGHP (확인)", "펄스 내성 저항 10 Ω 2512 (출력 직렬)", 0.05, 0.15, "확인 필요"),
    ("R", "2.2R (or 0R)"): ("보호", "Yageo", "RC0603FR-072R2L", "저항 2.2 Ω 1% 0603 (RS-485 직렬)", 0.002, 0.005, "제안"),
    ("R", "0R RTN link*"): ("전원", "Yageo", "RC0603JR-070RL", "0 Ω 링크 — TPS2660 RTN 연결 확인 후 실장 여부 결정", 0.002, 0.005, "확인 필요"),
    ("TPS2660", "TPS26600PWPR"): ("전원", "TI", "TPS26600PWPR", "eFuse 60 V 2 A, 역극성·OVP·UVLO, HTSSOP-16", 1.50, 3.00, "확정"),
    ("LMR36006", "LMR36006"): ("전원", "TI", "LMR36006 (가변판 주문코드 확인)", "벅 60 V 0.6 A → 5 V", 1.00, 1.60, "확인 필요"),
    ("TPS7A2033", "TPS7A2033PDBVR"): ("전원", "TI", "TPS7A2033PDBVR", "LDO 3.3 V 300 mA 저잡음 SOT-23-5", 0.07, 0.30, "확정"),
    ("STM32G0B1CxTx", "STM32G0B1CCT3"): ("MCU", "ST", "STM32G0B1CCT3", "MCU Cortex-M0+ 64 MHz 256 KB, LQFP48, −40~125 °C (사내 DP2000 G0B1CCT6 동일 다이)", 1.50, 2.50, "확정"),
    ("PCAP04", "PCAP04-AQFM-24"): ("측정", "ScioSense", "PCAP04-AQFM-24", "정전용량-디지털 변환기 QFN24", 6.50, 7.10, "확정"),
    ("ADS1220", "ADS1220IPWR"): ("측정", "TI", "ADS1220IPWR", "24-bit ADC, Pt1000 4선, TSSOP-16", 1.90, 3.50, "확정"),
    ("DAC8760", "DAC8760IPWP"): ("출력", "TI", "DAC8760IPWPR", "16-bit 전압/전류 출력 DAC, HTSSOP-24", 7.80, 12.40, "확정"),
    ("TPS26611", "TPS26611"): ("출력", "TI", "TPS26611 (패키지·주문코드 확인)", "4–20 mA 출력 오결선 보호", 1.20, 2.50, "확인 필요"),
    ("THVD2450", "THVD2450DR"): ("통신", "TI", "THVD2450DR", "RS-485 트랜시버, 버스 ±70 V 내성, SOIC-8", 1.50, 3.00, "확정"),
}

# 회로도에는 없지만 1대분 전자부에 필요한 것
EXTRA = [
    ("기판", "PCB", "-", "HMT500-E-301", "PCB 4층 57×23 mm, FR-4 1.6 t, ENIG (기구 Rev C 외곽)", "-", 1, 0.80, 2.00, "추정"),
    ("센서", "센서 헤드", "IST", "MK 계열 (사내 공급품)", "정전용량 습도 소자 (캐리어에 실장)", "-", 1, 0.0, 0.0, "사내 단가"),
    ("센서", "센서 헤드", "TBD", "Pt1000 박막 Class A", "온도 소자 (캐리어에 실장)", "-", 1, 0.50, 3.00, "추정"),
    ("조립", "-", "-", "SMT 양면 실장", "1k 기준 조립비", "-", 1, 2.00, 4.00, "추정"),
]


def build_rows():
    rows = []
    with open(os.path.join(OUTD, "HMT500_BOM.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (r["Symbol"], r["Value"])
            if key not in MAP:
                raise KeyError(f"부품리스트 매핑 없음: {key}")
            cat, mfr, mpn, desc, lo, hi, st = MAP[key]
            fp = r["Footprint"].split(":")[-1]
            rows.append(dict(cat=cat, ref=r["References"], mfr=mfr, mpn=mpn, desc=desc, val=r["Value"], fp=fp,
                             qty=int(r["Qty"]), lo=lo, hi=hi, st=st, verify=r.get("Verify", "")))
    return rows


def write_csv(rows):
    p = os.path.join(OUTD, "HMT500_parts_list.csv")
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["No", "분류", "참조번호", "수량", "값", "풋프린트", "제조사", "품번", "설명", "단가USD_하한", "단가USD_상한", "상태"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["cat"], r["ref"], r["qty"], r["val"], r["fp"], r["mfr"], r["mpn"], r["desc"], r["lo"], r["hi"], r["st"]])
        for j, (cat, ref, mfr, mpn, desc, fp, qty, lo, hi, st) in enumerate(EXTRA, len(rows) + 1):
            w.writerow([j, cat, ref, qty, "-", fp, mfr, mpn, desc, lo, hi, st])
    return p


def write_xlsx(rows):
    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.table import Table, TableStyleInfo

    F = "Arial"
    thin = Side(style="thin", color="BFBFBF")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    head_fill = PatternFill("solid", fgColor="1F3864")
    blue = Font(name=F, size=10, color="0000FF")
    norm = Font(name=F, size=10)
    bold = Font(name=F, size=10, bold=True)
    st_fill = {"확인 필요": "FFF2CC", "TBD": "FCE4D6", "추정": "FFF2CC", "사내 단가": "FFF2CC"}

    wb = Workbook()
    # ── 요약 (가정 셀 포함) ──
    sm = wb.active
    sm.title = "요약"
    # ── 부품리스트 ──
    ws = wb.create_sheet("부품리스트")
    hdr = ["No", "분류", "참조번호", "수량/대", "값", "풋프린트", "제조사", "품번", "설명",
           "단가 하한 (USD)", "단가 상한 (USD)", "금액 하한 (USD)", "금액 상한 (USD)", "상태"]
    ws.append(hdr)
    for c in range(1, len(hdr) + 1):
        cell = ws.cell(1, c)
        cell.font = Font(name=F, size=10, bold=True, color="FFFFFF")
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = box
    allrows = [(r["cat"], r["ref"], r["qty"], r["val"], r["fp"], r["mfr"], r["mpn"], r["desc"], r["lo"], r["hi"], r["st"])
               for r in rows]
    allrows += [(cat, ref, qty, "-", fp, mfr, mpn, desc, lo, hi, st) for cat, ref, mfr, mpn, desc, fp, qty, lo, hi, st in EXTRA]
    for i, (cat, ref, qty, val, fp, mfr, mpn, desc, lo, hi, st) in enumerate(allrows, 1):
        rr = i + 1
        ws.append([i, cat, ref, qty, val, fp, mfr, mpn, desc, lo, hi, f"=D{rr}*J{rr}", f"=D{rr}*K{rr}", st])
        for c in range(1, len(hdr) + 1):
            cell = ws.cell(rr, c)
            cell.border = box
            cell.font = norm
            cell.alignment = Alignment(vertical="top", wrap_text=c in (3, 8, 9))
        for c in (4, 10, 11):
            ws.cell(rr, c).font = blue
        for c in (10, 11, 12, 13):
            ws.cell(rr, c).number_format = '$#,##0.000;($#,##0.000);"-"'
        if st in st_fill:
            ws.cell(rr, 14).fill = PatternFill("solid", fgColor=st_fill[st])
    last = len(allrows) + 1
    tot = last + 1
    ws.cell(tot, 9, "합계 (1대분)").font = bold
    ws.cell(tot, 12, f"=SUM(L2:L{last})").font = bold
    ws.cell(tot, 13, f"=SUM(M2:M{last})").font = bold
    for c in (12, 13):
        ws.cell(tot, c).number_format = '$#,##0.00'
        ws.cell(tot, c).border = box
    widths = [5, 8, 26, 8, 16, 26, 12, 30, 48, 12, 12, 12, 12, 10]
    for c, wdt in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(c)].width = wdt
    ws.freeze_panes = "D2"
    tab = Table(displayName="PartsList", ref=f"A1:N{last}")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(tab)
    ws.cell(1, 10).comment = Comment("1,000대 기준 추정 단가. 출처: docs/hw/bom-cost.md (유통사 검색가), "
                                     "MCU는 두텍 구매 이력(G0B1CCT6 2,060원/100개). 대리점 견적으로 확정.", "HMT500")

    # ── 요약 시트 ──
    sm["A1"] = "HMT500 전자부 부품리스트 — 요약"
    sm["A1"].font = Font(name=F, size=14, bold=True)
    sm["A2"] = "회로도 v0.3 (KiCad) 기준 · 1대분 · 단가는 1k 추정 (파란 글씨 = 입력값)"
    sm["A2"].font = Font(name=F, size=10, italic=True, color="595959")
    sm["A4"], sm["B4"] = "환율 (원/USD)", FX
    sm["A4"].font = bold
    sm["B4"].font = blue
    sm["B4"].fill = PatternFill("solid", fgColor="FFFF00")
    sm["B4"].number_format = "#,##0"
    sm["C4"] = "가정 — bom-cost.md 와 동일"
    sm["C4"].font = Font(name=F, size=9, color="595959")
    heads = ["분류", "품목 수", "금액 하한 (USD)", "금액 상한 (USD)", "금액 하한 (원)", "금액 상한 (원)"]
    for c, h in enumerate(heads, 1):
        cell = sm.cell(6, c, h)
        cell.font = Font(name=F, size=10, bold=True, color="FFFFFF")
        cell.fill = head_fill
        cell.border = box
        cell.alignment = Alignment(horizontal="center")
    cats = []
    for r in allrows:
        if r[0] not in cats:
            cats.append(r[0])
    rng = f"'부품리스트'!$B$2:$B${last}"
    for i, cat in enumerate(cats):
        rr = 7 + i
        sm.cell(rr, 1, cat)
        sm.cell(rr, 2, f"=COUNTIF({rng},A{rr})")
        sm.cell(rr, 3, f"=SUMIFS('부품리스트'!$L$2:$L${last},{rng},A{rr})")
        sm.cell(rr, 4, f"=SUMIFS('부품리스트'!$M$2:$M${last},{rng},A{rr})")
        sm.cell(rr, 5, f"=C{rr}*$B$4")
        sm.cell(rr, 6, f"=D{rr}*$B$4")
    end = 7 + len(cats) - 1
    tr = end + 1
    sm.cell(tr, 1, "합계")
    for c, col in ((2, "B"), (3, "C"), (4, "D"), (5, "E"), (6, "F")):
        sm.cell(tr, c, f"=SUM({col}7:{col}{end})")
    for rr in range(7, tr + 1):
        for c in range(1, 7):
            cell = sm.cell(rr, c)
            cell.border = box
            cell.font = bold if rr == tr else (Font(name=F, size=10, color="008000") if c in (2, 3, 4) else norm)
        for c in (3, 4):
            sm.cell(rr, c).number_format = '$#,##0.00;($#,##0.00);"-"'
        for c in (5, 6):
            sm.cell(rr, c).number_format = '#,##0;(#,##0);"-"'
    n = tr + 2
    notes = [
        "읽는 법",
        "· 부품리스트 시트의 참조번호·수량·값·풋프린트는 KiCad 회로도에서 자동 생성 (make_parts_list.py).",
        "· 상태: 확정 = 회로도·품번 확정 / 제안 = 동등품 대체 가능 / 확인 필요 = 데이터시트·견적 확인 후 확정 / TBD = 미정.",
        "· 제외: 기구 부품(바디·하우징·캡·엔드캡·홀더·O링·나사), 피드스루(HMT500-P-201)는 기구 부품표에 있음.",
        "· 핀 번호 확인 대상 IC: LMR36006, PCAP04, DAC8760, TPS26611 (회로도 VERIFY 표시). TPS2660은 R22 RTN 연결 확인.",
    ]
    for i, t in enumerate(notes):
        cell = sm.cell(n + i, 1, t)
        cell.font = bold if i == 0 else Font(name=F, size=10)
    for c, wdt in zip("ABCDEF", (16, 10, 16, 16, 16, 16)):
        sm.column_dimensions[c].width = wdt
    p = os.path.join(OUTD, "HMT500_parts_list.xlsx")
    wb.save(p)
    return p


def main():
    rows = build_rows()
    print(write_csv(rows))
    print(write_xlsx(rows))


if __name__ == "__main__":
    main()
