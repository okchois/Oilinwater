"""HMT500(ED260313A) 구매용 부품리스트 생성 (회로도 BOM + 제조사 품번·단가 가정).

  python3 hardware/kicad/gen_hmt500.py        # 먼저 회로도·HMT500(ED260313A)_BOM.csv 생성
  python3 hardware/kicad/make_parts_list.py   # → HMT500(ED260313A)/HMT500(ED260313A)_parts_list.xlsx, .csv

- 회로도 부품(참조번호·수량·값·풋프린트)은 HMT500(ED260313A)_BOM.csv 에서 그대로 읽는다. 여기서는 품번과 단가만 붙인다.
- 수동소자 품번은 "제안" (동등품 대체 가능). 단가는 1k 기준 추정값이며 견적으로 확정한다.
- 회로도에 없지만 1대분에 필요한 전자 부품(PCB, 센서, 커넥터 등)은 EXTRA 로 덧붙인다.
"""

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "HMT500(ED260313A)"   # 파일명 = 프로젝트 번호
OUTD = os.path.join(HERE, PROJECT)
FX = 1400  # 원/달러 가정

# (심볼, 값) → (분류, 제조사, 품번, 설명, 단가 USD 하한, 상한, 상태)
# 상태: 확정 / 제안(동등품 가능) / 확인 필요 / TBD
MAP = {
    ("C", "100n 100V"): ("수동", "Murata", "GRM21BR72A104KA35L", "MLCC 100 nF 100 V X7R 0805", 0.02, 0.05, "제안"),
    ("C", "10u 50V"): ("수동", "Samsung", "CL31B106KBHNNNE", "MLCC 10 uF 50 V X7R 1206 (벅 입력 C5, VAO 출력 C64·C65)", 0.10, 0.25, "LCSC"),
    ("C", "4.7n 2kV"): ("보호", "YAGEO", "CC1812KKX7RDBB472", "MLCC 4.7 nF 2 kV X7R 1812 (GND–외함. LCSC에 Y2 1812 없음 — DC 기기라 Y2 불필요)", 0.10, 0.20, "LCSC"),
    ("C", "22n"): ("수동", "Samsung", "CL05B223KO5NNNC", "MLCC 22 nF 16 V X7R 0402 (eFuse dV/dt, RTN 기준 저전압)", 0.002, 0.005, "LCSC"),
    ("C", "2.2u 100V"): ("수동", "Murata", "GRM32ER72A225KA35L", "MLCC 2.2 uF 100 V X7R 1210", 0.15, 0.35, "제안"),
    ("C", "100n"): ("수동", "Samsung", "CL05B104KO5NNNC", "MLCC 100 nF 16 V X7R 0402 (3.3·5 V 디커플링 — 결정 #35 0402로 자리 확보)", 0.002, 0.005, "LCSC"),
    ("C", "100n/50V"): ("출력", "YAGEO", "CC0603KRX7R9BB104", "MLCC 100 nF 50 V X7R 0603 (VS_CLAMP 약 24 V)", 0.004, 0.01, "LCSC"),
    ("C", "1u"): ("수동", "Murata", "GRM155Z71A105KE01D", "MLCC 1 uF 10 V X7R 0402 (5 V 이하 넷: 벅 VCC, LDO 입·출력. LCSC 표기 X7R — 데이터시트 확인)", 0.006, 0.02, "LCSC"),
    ("C", "22u 25V"): ("전원", "Murata", "GRM32ER71E226ME15L", "MLCC 22 uF 25 V X7R 1210 (벅 출력 2개, LMR36006 X7R 요구. LCSC에 1206 X7R 없음 → 1210)", 0.15, 0.40, "LCSC"),
    ("C", "20p C0G"): ("전원", "Samsung", "CL05C200JB5NNNC", "MLCC 20 pF 50 V C0G 0402 (벅 CFF)", 0.002, 0.005, "LCSC"),
    ("C", "10u"): ("수동", "Murata", "GRM31CR71E106KA12L", "MLCC 10 uF 25 V X7R 1206 (v0.9: 0805 X5R → 1206 X7R, DC 바이어스 여유)", 0.05, 0.12, "제안"),
    ("C", "4.7u"): ("수동", "Murata", "GRM21BR71E475KA73L", "MLCC 4.7 uF 25 V X7R 0805 (품번 확인 필요)", 0.03, 0.08, "확인 필요"),
    ("C", "22u 10V"): ("측정", "Murata", "GRM31CR71A226KE15L", "MLCC 22 uF 10 V X7R 1206 (PCAP04 VDD33 ≥ 10 µF 실효, 품번 확인 필요)", 0.08, 0.20, "확인 필요"),
    ("C", "220n 100V"): ("전원", "Samsung", "CL21B224KCFSFNE", "MLCC 220 nF 100 V X7R 0805 (LMR36006 VIN–PGND 핀마다. LCSC에 0603 없음 → 0805)", 0.02, 0.06, "LCSC"),
    ("C", "10n C0G"): ("측정", "Murata", "GRM1885C1H103JA01D", "MLCC 10 nF 50 V C0G 0603 (ADS1220 차동 필터)", 0.01, 0.03, "제안"),
    ("NPN_SOT23", "MMBTA06"): ("출력", "onsemi / Nexperia", "MMBTA06LT1G", "NPN 80 V 0.5 A SOT-23 — TPS26611 +Vs 이미터 폴로워 (1 B, 2 E, 3 C)", 0.02, 0.05, "제안"),
    ("ZENER", "BZX84C24"): ("출력", "onsemi", "BZX84C24LT1G", "제너 24 V (22.8–25.6) SOT-23 — +Vs 이미터 폴로워 기준 (1 A, 2 NC, 3 K). 외부 검수 H04: 27 → 24 V (+Vs 권장 30 V 여유)", 0.01, 0.03, "LCSC"),
    ("LMR51606", "LMR51606YFDBVR"): ("전원", "TI", "LMR51606YFDBVR", "벅 4–65 V 0.6 A 1.1 MHz FPWM SOT-23-6 — U2 5 V (결정 #38), U15 VAO 16.1 V (결정 #37)", 0.60, 1.20, "LCSC"),
    ("L", "10uH"): ("전원", "SXN", "SMNR4020-10UH", "파워 인덕터 10 µH ±20 %, 원문 정격 DC 1.60 A, DCR 0.165 Ω ±30 %, 4 × 4 × 2.2 mm max (전용 랜드; 포화 기준 확인 필요) — 5 V 벅 (부하 약 60 mA)", 0.05, 0.12, "확인 필요"),
    ("R", "118k 1%"): ("전원", "YAGEO", "AC0402FR-07118KL", "저항 118 kΩ 1% 0402 (5 V 벅 FB 상단)", 0.001, 0.003, "LCSC"),
    ("BAS70-04", "BAS70-04"): ("출력", "Nexperia", "BAS70-04,215", "쇼트키 2개 직렬 70 V SOT-23 — DAC 출력 클램프 (1 A, 2 K, 3 공통)", 0.02, 0.05, "LCSC"),
    ("L", "22uH"): ("출력", "SXN", "SMNR4020-22UH", "파워 인덕터 22 µH ±20 %, 원문 정격 DC 1.05 A, DCR 0.350 Ω ±30 %, 4 × 4 × 2.2 mm max (전용 랜드; 포화 기준 확인 필요) — VAO 벅", 0.05, 0.15, "확인 필요"),
    ("C", "2.2u 50V"): ("출력", "YAGEO", "CC0805KKX7R9BB225", "MLCC 2.2 uF 50 V X7R ±10% 0805, 최대 높이 1.45 mm (VAO 벅 입력)", 0.02, 0.15, "LCSC"),
    ("C", "4.7n"): ("출력", "Samsung", "CL05B472KB5NNNC", "MLCC 4.7 nF 50 V X7R 0402 (DAC VOUT–CMP 보상)", 0.002, 0.005, "LCSC"),
    ("C", "100p C0G"): ("출력", "Samsung", "CL05C101JB5NNNC", "MLCC 100 pF 50 V C0G 0402 (DAC CMP–GND)", 0.002, 0.005, "LCSC"),
    ("R", "422k 1%"): ("출력", "YAGEO", "RC0402FR-07422KL", "저항 422 kΩ 1% 0402 (VAO 분압 상단)", 0.001, 0.003, "LCSC"),
    ("R", "22.1k 1%"): ("출력", "UNI-ROYAL", "0402WGF2212TCE", "저항 22.1 kΩ 1% 0402 (VAO 분압 하단)", 0.001, 0.003, "확인 필요"),
    ("SCHOTTKY", "PMEG10010ELR"): ("보호", "Nexperia", "PMEG10010ELR-QX", "쇼트키 100 V 1 A 저누설 SOD-123W (SOD-123F 풋프린트) — eFuse 앞 직렬, 음(−) 서지·역극성 차단 (외부 검수 H01)", 0.05, 0.12, "LCSC"),
    ("C", "330p C0G 2%"): ("측정", "Vishay", "VJ0603A331GXACW1BC", "MLCC 330 pF 50 V C0G ±2% 0603 (결정 #34, PCAP04 기준 C)", 0.01, 0.04, "제안"),
    ("C", "10n"): ("수동", "Murata", "GRM188R71H103KA01D", "MLCC 10 nF 50 V X7R 0603", 0.003, 0.01, "제안"),
    ("C", "1n 100V"): ("보호", "Murata", "GRM188R72A102KA01D", "MLCC 1 nF 100 V X7R 0603", 0.004, 0.01, "제안"),
    ("C", "100n 50V"): ("수동", "Murata", "GRM21BR71H104KA01L", "MLCC 100 nF 50 V X7R 0805", 0.01, 0.03, "제안"),
    ("C", "4.7u 50V"): ("수동", "Murata", "GRM32ER71H475KA88L", "MLCC 4.7 uF 50 V X7R 1210 (소프트 터미네이션 권장 — 에폭시 응력)", 0.10, 0.25, "제안"),
    ("TVS_BI", "SMDJ36CA"): ("보호", "Littelfuse", "5.0SMDJ36CA", "TVS 5000 W 36 V 양방향 SMC (입력 1단. LCSC — 같은 36 V·SMC, 3 kW → 5 kW)", 0.30, 0.70, "LCSC"),
    ("TVS_BI", "SMBJ33CA"): ("보호", "Littelfuse", "SMBJ33CA", "TVS 600 W 33 V 양방향 SMB (입력 2단)", 0.08, 0.20, "제안"),
    ("TVS3301", "TVS3301DRBR"): ("보호", "TI", "TVS3301DRBR", "평탄 클램프 TVS 33 V 양방향, 40 V @ 27 A, SON-8 3×3 (아날로그 출력, TPS2661 데이터시트 권장)", 0.35, 0.60, "제안"),
    ("TVS1401", "TVS1401DRBR"): ("보호", "TI", "TVS1401DRBR", "평탄 클램프 TVS 14 V 양방향, 최대 23.55 V @ 30 A/125 C, SON-8 3×3 (AO 전용, 지속 ±28/30 V 오결선 보장 제외)", 0.35, 0.60, "제안"),
    ("TVS_BI", "SMAJ40CA (opt.)"): ("보호", "Littelfuse", "SMAJ40CA", "TVS 400 W 40 V 양방향 SMA (RS-485, 옵션)", 0.06, 0.15, "제안"),
    ("LED", "green"): ("표시", "Würth", "150060GS75000", "LED 녹색 0603", 0.03, 0.08, "제안"),
    ("FB", "600R@100MHz"): ("수동", "Murata", "BLM18KG601SN1D", "페라이트 비드 600 Ω@100 MHz 0603", 0.01, 0.03, "제안"),
    ("GDT", "2035-25-SM"): ("보호", "Bourns", "2035-25-SM-RPLF", "2전극 SMD GDT 250 V, Ø5 × 4.4 mm (회로 GND–외함. LCSC — 230 V형은 LCSC에 없음)", 0.40, 1.00, "LCSC"),
    ("CONN_GH8", "SM08B-GHS-TB"): ("커넥터", "JST", "SM08B-GHS-TB", "GH 1.25 mm 8핀 헤더, 옆 삽입(직각) SMD (M12 하네스 W-2, 정격 −25~+85 °C)", 0.35, 0.80, "제안"),
    ("CONN_CH", "CHASSIS wire"): ("커넥터", "-", "PCB 납땜 구멍 (부품 없음)", "샤시 선 AWG 28 PTFE 약 25 mm + M2 링 단자 → 홀더 축 나사. 선·단자는 기구 부품표(JLCMC)", 0.0, 0.0, "확정"),
    ("CONN_SWD", "TC2030-IDC-NL"): ("생산", "Tag-Connect", "(PCB 패드만)", "SWD 기록용 패드 — 부품 실장 없음", 0.0, 0.0, "확정"),
    ("CONN_SH4", "SM04B-SRSS-TB"): ("커넥터", "JST", "SM04B-SRSS-TB", "SH 1.0 mm 4핀 헤더, 옆 삽입(직각) SMD (센서 하네스 W-1, 정격 −25~+85 °C)", 0.30, 0.60, "제안"),
    ("CMC", "CMC 1mH 0.8A"): ("보호", "Bourns", "SRF0905-102Y", "공통모드 초크 2 × 1 mH, 0.8 A, 0.31 Ω, 9.2 × 6 × 5.3 mm (LCSC, Würth 744222 동등). WE-SL2 랜드 일치: 패드 2×1.2, 중심 ±3.75/±1.27 mm; SRF0905 원문 권선 1–4/2–3 대조 완료", 0.50, 1.20, "확인 필요"),
    ("L", "15uH"): ("전원", "Coilcraft", "XGL4040-153MEC", "파워 인덕터 15 µH 3.6 A, 4 × 4 × 4.0 mm (XAL4040 풋프린트. LCSC — 4030형은 LCSC에 없음)", 0.30, 0.70, "LCSC"),
    ("R", "4.7R 1W pulse"): ("보호", "Vishay", "CRCW25124R70FKEG", "CRCW 2512 4.7 Ω 1% 1 W (결정 #38: JLC 부품 — 펄스 내성 HP형 대신 일반형, 서지 시험 T1로 확인)", 0.05, 0.15, "LCSC"),
    ("R", "1M HV"): ("보호", "ROHM", "KTR18EZPF1004", "서지용 칩 저항 1 MΩ 1% 1206, 최고 사용 전압 500 V (GDT 방전 전 임펄스. LCSC — 1 kV 1206은 LCSC에 없음)", 0.02, 0.06, "LCSC"),
    ("R", "866k 1%"): ("전원", "Yageo", "RC0603FR-07866KL", "저항 866 kΩ 1% 0603 (UVLO)", 0.002, 0.005, "제안"),
    ("R", "97.6k 1%"): ("전원", "Yageo", "RC0603FR-0797K6L", "저항 97.6 kΩ 1% 0603 (UVLO/OVP)", 0.002, 0.005, "제안"),
    ("R", "36.5k 1%"): ("전원", "Yageo", "RC0603FR-0736K5L", "저항 36.5 kΩ 1% 0603 (OVP 32.6 V, 복귀 30.1 V — v0.9)", 0.002, 0.005, "제안"),
    ("R", "100k"): ("수동", "UNI-ROYAL", "0402WGF1003TCE", "저항 100 kΩ 1% 0402 (50 V)", 0.001, 0.003, "LCSC"),
    ("R", "10k 1%"): ("수동", "UNI-ROYAL", "0402WGF1002TCE", "저항 10 kΩ 1% 0402 (전원 감시 분압)", 0.001, 0.003, "LCSC"),
    ("R", "80.6k 1%"): ("전원", "Yageo", "RC0603FR-0780K6L", "저항 80.6 kΩ 1% 0603 (TPS2660 전류제한 149 mA = 12/R)", 0.002, 0.005, "제안"),
    ("R", "10k"): ("수동", "UNI-ROYAL", "0402WGF1002TCE", "저항 10 kΩ 1% 0402 (50 V)", 0.001, 0.003, "LCSC"),
    ("R", "100k 1%"): ("전원", "UNI-ROYAL", "0402WGF1003TCE", "저항 100 kΩ 1% 0402 (벅 FB, 전원 감시)", 0.001, 0.003, "LCSC"),
    ("R", "24.9k 1%"): ("전원", "Yageo", "RC0603FR-0724K9L", "저항 24.9 kΩ 1% 0603 (벅 FB)", 0.002, 0.005, "제안"),
    ("R", "1k"): ("수동", "UNI-ROYAL", "0402WGF1001TCE", "저항 1 kΩ 1% 0402", 0.001, 0.003, "LCSC"),
    ("R", "4.02k 0.1% 25ppm"): ("측정", "Panasonic", "ERA-3AEB4021V", "Pt1000 기준저항 4.02 kΩ 0.1 % 25 ppm/K 박막 0603 (결정 #38: JLC 부품 — 이전 PLTT 0.02 %·5 ppm. 초기 오차는 교정, 온도 드리프트는 ADS1220 내부 온도로 보정 검토)", 0.10, 0.30, "LCSC"),
    ("R", "15k 0.1% 25ppm"): ("출력", "Yageo", "RT0603BRD0715KL", "저항 15 kΩ 0.1% 25 ppm/K 0603 (DAC8760 외부 ISET-R)", 0.02, 0.06, "제안"),
    ("R", "10R"): ("출력", "UNI-ROYAL", "0402WGF100JTCE", "저항 10 Ω 1% 0402 (DAC8760 AVDD 직렬, 약 8 mW)", 0.001, 0.003, "LCSC"),
    ("R", "10R pulse"): ("보호", "Vishay", "CRCW251210R0FKEG", "CRCW 2512 10 Ω 1% 1 W (결정 #38: JLC 부품 — 일반형, 서지 시험 T3로 확인)", 0.03, 0.10, "LCSC"),
    ("R", "2.2R (or 0R)"): ("보호", "Yageo", "RC0603FR-072R2L", "저항 2.2 Ω 1% 0603 (RS-485 직렬)", 0.002, 0.005, "제안"),
    ("TPS2660", "TPS26600PWPR"): ("전원", "TI", "TPS26600PWPR", "eFuse 60 V 2 A, 역극성·OVP·UVLO, HTSSOP-16", 1.50, 3.00, "확정"),
    ("LMR36006", "LMR36006BRNXR"): ("전원", "TI", "LMR36006BRNXR", "벅 60 V 0.6 A → 5 V, 1 MHz 조정형, VQFN-HR 12핀 2×3 mm", 1.00, 1.60, "확정"),
    ("TPS7A2033", "TPS7A2033PDBVR"): ("전원", "TI", "TPS7A2033PDBVR", "LDO 3.3 V 300 mA 저잡음 SOT-23-5", 0.07, 0.30, "확정"),
    ("STM32G0B1CxTx", "STM32G0B1CCT6"): ("MCU", "ST", "STM32G0B1CCT6", "MCU Cortex-M0+ 64 MHz 256 KB, LQFP48, −40~85 °C — 사내 DP2000과 같은 품번. 샘플 단계 JLC 부품 (결정 #39), 양산은 전자부 온도 사양 확정 후 CCT3(125 °C) 검토", 1.50, 2.50, "LCSC"),
    ("PCAP04", "PCAP04-AQFM-24"): ("측정", "ScioSense", "PCAP04-AQFM-24", "정전용량-디지털 변환기 QFN24", 6.50, 7.10, "확정"),
    ("ADS1220", "ADS1220IPWR"): ("측정", "TI", "ADS1220IPWR", "24-bit ADC, Pt1000 2선 (J3 패드에서 켈빈 분기), TSSOP-16", 1.90, 3.50, "확정"),
    ("DAC8760", "DAC8760IPWP"): ("출력", "TI", "DAC8760IPWPR", "16-bit 전압/전류 출력 DAC, HTSSOP-24. 사양 확정 후 같은 핀 대체: DAC7760(12-bit V/I), DAC8750(16-bit 전류), DAC7750(12-bit 전류)", 7.80, 12.40, "확정"),
    ("OPA197", "OPA197IDBVR"): ("출력", "TI", "OPA197IDBVR", "36 V 레일투레일 연산증폭기 SOT-23-5 — DAC8760 +VSENSE 버퍼 (이득 1)", 0.60, 1.10, "제안"),
    ("TPS26611", "TPS26611DDFR"): ("출력", "TI", "TPS26611DDFR", "±50 V 아날로그 출력 오결선 보호, 32 mA 제한, SOT-23-8", 1.20, 2.50, "확정"),
    ("74LVC2G32", "SN74LVC2G32DCUR"): ("출력", "TI", "SN74LVC2G32DCUR", "OR 게이트 2회로 VSSOP-8 — DAC별 SCLK 게이트 (DAC8760 8.5.1.5)", 0.08, 0.20, "제안"),
    ("THVD2450", "THVD2410DGKR"): ("통신", "TI", "THVD2410DGKR", "RS-485 트랜시버 500 kbps (느린 에지), 버스 ±70 V 내성, VSSOP-8 (SOIC와 같은 핀, 외부 검수 H02 TVS 자리 확보) — THVD2450과 같은 핀 (v0.9)", 1.50, 3.00, "확정"),
}

# JLCPCB 조립용 LCSC 품번 (결정 #33·#34, 2026-09-30 웹 검색 대조 — 주문 전 JLC 부품 페이지에서 재고·Basic 여부 확인)
# (심볼, 값) → (제조사, 품번, LCSC, 구분, 메모). 구분: Basic / Extended / 글로벌 소싱 (JLC가 Digikey·Mouser 등에서 대신 구매)
LCSC = {
    ("C", "100n 100V"): ("Samsung", "CL21B104KCFNNNE", "C28233", "Basic", ""),
    ("C", "2.2u 100V"): ("Murata", "GRM32ER72A225KA35L", "C86054", "Extended", ""),
    ("C", "4.7n 2kV"): ("YAGEO", "CC1812KKX7RDBB472", "C309511", "Extended", ""),
    ("C", "22n"): ("Samsung", "CL05B223KO5NNNC", "C318579", "확인 필요", "2026-10-03 LCSC 품번 대조: C1532는 FH 제품이므로 정정; JLC 등급/재고 확인 필요"),
    ("C", "10u 50V"): ("Samsung", "CL31B106KBHNNNE", "C89632", "Extended", ""),
    ("C", "22u 25V"): ("Murata", "GRM32ER71E226ME15L", "C424136", "Extended", ""),
    ("C", "100n"): ("Samsung", "CL05B104KO5NNNC", "C1525", "Basic", ""),
    ("C", "100n/50V"): ("YAGEO", "CC0603KRX7R9BB104", "C14663", "Basic", ""),
    ("C", "1u"): ("Murata", "GRM155Z71A105KE01D", "C528974", "Extended", "X7R 1 µF 0402 16 V는 LCSC에서 못 찾음 → 10 V (5 V 이하 넷)"),
    ("C", "20p C0G"): ("Samsung", "CL05C200JB5NNNC", "C32950", "Extended", ""),
    ("C", "10u"): ("Murata", "GRM31CR71E106KA12L", "C77093", "Extended", ""),
    ("C", "220n 100V"): ("Samsung", "CL21B224KCFSFNE", "C307542", "Extended", ""),
    ("C", "4.7u"): ("Murata", "GRM21BR71E475KA73L", "C162427", "Extended", ""),
    ("C", "330p C0G 2%"): ("Vishay", "VJ0603A331GXACW1BC", "C3898227", "Extended", "±2 % (LCSC에 ±1 % 없음) — 기준 C 절대값은 교정으로 제거, C0G라 온도 안정"),
    ("C", "22u 10V"): ("Murata", "GRM31CR71A226KE15L", "C91604", "Extended", ""),
    ("C", "10n C0G"): ("Murata", "GRM1885C1H103JA01D", "C85973", "Extended", ""),
    ("C", "1n 100V"): ("Murata", "GRM188R72A102KA01D", "C97897", "Extended", ""),
    ("C", "100n 50V"): ("YAGEO", "CC0805KRX7R9BB104", "C49678", "Basic", ""),
    ("C", "4.7u 50V"): ("Murata", "GRM32ER71H475KA88L", "C86052", "Extended", ""),
    ("TVS_BI", "SMDJ36CA"): ("Littelfuse", "5.0SMDJ36CA", "C141713", "Extended", ""),
    ("TVS1401", "TVS1401DRBR"): ("TI", "TVS1401DRBR", "C1849891", "", "D30/D40; LCSC 품번 확인, JLC 등급/재고 확인 필요"),
    ("TVS3301", "TVS3301DRBR"): ("TI", "TVS3301DRBR", "C2864392", "Extended", "D2/D60/D61 3개 유지; 재고 확인 필요"),
    ("ZENER", "BZX84C24"): ("onsemi", "BZX84C24LT1G", "C43728", "Extended", ""),
    ("SCHOTTKY", "PMEG10010ELR"): ("Nexperia", "PMEG10010ELR-QX", "C5361358", "Extended", ""),
    ("LMR51606", "LMR51606YFDBVR"): ("TI", "LMR51606YFDBVR", "C22439294", "Extended", ""),
    ("L", "10uH"): ("SXN", "SMNR4020-10UH", "C135263", "Extended", "SXN 원문 F=.95/G=2.1/H=3.3 mm 전용 랜드 반영; Isat 정의 확인 필요"),
    ("R", "118k 1%"): ("YAGEO", "AC0402FR-07118KL", "C144804", "Extended", ""),
    ("BAS70-04", "BAS70-04"): ("Nexperia", "BAS70-04,215", "C389351", "Extended", ""),
    ("L", "22uH"): ("SXN", "SMNR4020-22UH", "C135264", "Extended", "SXN 원문 F=.95/G=2.1/H=3.3 mm 전용 랜드 반영; Isat 정의 확인 필요"),
    ("C", "2.2u 50V"): ("YAGEO", "CC0805KKX7R9BB225", "C125847", "Extended", "결정 #53: 2.2 µF 50 V X7R ±10% 0805; 최대 높이 1.45 mm; DC 바이어스 실효 용량 확인 필요"),
    ("C", "4.7n"): ("Samsung", "CL05B472KB5NNNC", "C84705", "Extended", ""),
    ("C", "100p C0G"): ("Samsung", "CL05C101JB5NNNC", "C26409", "Extended", ""),
    ("R", "422k 1%"): ("YAGEO", "RC0402FR-07422KL", "C477738", "Extended", ""),
    ("R", "22.1k 1%"): ("UNI-ROYAL", "0402WGF2212TCE", "C43473", "Extended", "2026-10-03 LCSC/JLC 품번·22.1 kΩ ±1%·0402 대조"),
    ("FB", "600R@100MHz"): ("Murata", "BLM18KG601SN1D", "C85833", "Extended", "Basic 비드 C1002는 200 mA라 쓰지 않음"),
    ("GDT", "2035-25-SM"): ("Bourns", "2035-25-SM-RPLF", "C3660127", "Extended", ""),
    ("CONN_GH8", "SM08B-GHS-TB"): ("JST", "SM08B-GHS-TB(LF)(SN)", "C265111", "Extended", ""),
    ("CONN_SH4", "SM04B-SRSS-TB"): ("JST", "SM04B-SRSS-TB(LF)(SN)", "C160404", "Extended", ""),
    ("CMC", "CMC 1mH 0.8A"): ("Bourns", "SRF0905-102Y", "C2651138", "Extended", "SRF0905 권장 랜드와 WE-SL2 패드 치수·핀 배정 대조 완료 (2026-10-01); 주문 시 재고 확인"),
    ("L", "15uH"): ("Coilcraft", "XGL4040-153MEC", "C3911667", "Extended", ""),
    ("NPN_SOT23", "MMBTA06"): ("onsemi", "MMBTA06LT1G", "C77760", "Extended", ""),
    ("R", "4.7R 1W pulse"): ("Vishay", "CRCW25124R70FKEG", "C242563", "Extended", "결정 #38: 일반형 (HP 대신)"),
    ("R", "1M HV"): ("ROHM", "KTR18EZPF1004", "C253347", "Extended", "500 V (1 kV 1206은 LCSC에 없음)"),
    ("R", "866k 1%"): ("Vishay", "RCS0603866KFKEA", "C3954581", "Extended", ""),
    ("R", "97.6k 1%"): ("Panasonic", "ERA-3AEB9762V", "C2074558", "Extended", "0.1 % 25 ppm (1 %형 LCSC에 없음, 더 좋음)"),
    ("R", "36.5k 1%"): ("CAL-CHIP", "RM06F3652CT", "C4027587", "Extended", ""),
    ("R", "80.6k 1%"): ("UNI-ROYAL", "0603WAF8062T5E", "C23249", "Extended", ""),
    ("R", "100k 1%"): ("UNI-ROYAL", "0402WGF1003TCE", "C25741", "Basic", ""),
    ("R", "24.9k 1%"): ("UNI-ROYAL", "0603WAF2492T5E", "C25962", "Extended", ""),
    ("R", "10k"): ("UNI-ROYAL", "0402WGF1002TCE", "C25744", "Basic", ""),
    ("R", "100k"): ("UNI-ROYAL", "0402WGF1003TCE", "C25741", "Basic", ""),
    ("R", "10k 1%"): ("UNI-ROYAL", "0402WGF1002TCE", "C25744", "Basic", ""),
    ("R", "1k"): ("UNI-ROYAL", "0402WGF1001TCE", "C11702", "Basic", ""),
    ("R", "4.02k 0.1% 25ppm"): ("Panasonic", "ERA-3AEB4021V", "C491130", "Extended", "결정 #38: 0.1 %·25 ppm (PLTT 0.02 %·5 ppm 대신)"),
    ("R", "10R pulse"): ("Vishay", "CRCW251210R0FKEG", "C844885", "Extended", "결정 #38: 일반형 (HP 대신)"),
    ("R", "15k 0.1% 25ppm"): ("Panasonic", "ERA-3AEB153V", "C473244", "Extended", ""),
    ("R", "10R"): ("UNI-ROYAL", "0402WGF100JTCE", "C25077", "Basic", ""),
    ("TPS2660", "TPS26600PWPR"): ("TI", "TPS26600PWPR", "C544399", "Extended", ""),
    ("LMR36006", "LMR36006BRNXR"): ("TI", "LMR36006BRNXR", "", "글로벌 소싱", "LCSC에 없음 (차량용 LMR36006FSCQRNXRQ1 C2869760은 다른 품번·재고 16개)"),
    ("TPS7A2033", "TPS7A2033PDBVR"): ("TI", "TPS7A2033PDBVR", "C2862740", "Extended", "TECHPUBLIC 복제품 C49452001 아님"),
    ("STM32G0B1CxTx", "STM32G0B1CCT6"): ("ST", "STM32G0B1CCT6", "C5270241", "Extended", "샘플 단계 (결정 #39). 85 °C 등급 — 양산 전 온도 사양 확인"),
    ("PCAP04", "PCAP04-AQFM-24"): ("ScioSense", "PCAP04-AQFM-24", "C2829318", "Extended", ""),
    ("ADS1220", "ADS1220IPWR"): ("TI", "ADS1220IPWR", "C48263", "Extended", ""),
    ("DAC8760", "DAC8760IPWP"): ("TI", "DAC8760IPWPR", "C55047", "Extended", ""),
    ("TPS26611", "TPS26611DDFR"): ("TI", "TPS26611DDFR", "C3148140", "Extended", ""),
    ("THVD2450", "THVD2410DGKR"): ("TI", "THVD2410DGKR", "C1858306", "Extended", ""),
    ("OPA197", "OPA197IDBVR"): ("TI", "OPA197IDBVR", "C221351", "Extended", ""),
    ("74LVC2G32", "SN74LVC2G32DCUR"): ("TI", "SN74LVC2G32DCUR", "C91874", "Extended", ""),
}
# 하네스 부품 (LCSC 주문, 품번 → LCSC)
EXTRA_LCSC = {"GHR-08V-S": "C485357", "SSHL-002T-P0.2": "C189897", "SHR-04V-S": "C385125", "SSH-003T-P0.2-H": "C263995"}


# 회로도에는 없지만 1대분 전자부에 필요한 것
EXTRA = [
    ("기판", "PCB", "-", "HMT500(ED260313A) (E-301)", "PCB 6층 57×23 mm, FR-4 nominal 1.6 t, ENIG (A5-R1, 기구 Rev I 외곽)", "-", 1, 0.80, 2.00, "추정"),
    ("센서", "센서 헤드", "IST", "MK33-W (300 pF, 품번 확인 필요)", "정전용량 습도 소자 300 pF (센서 프로브 P-202에 실장, 결정 #33)", "-", 1, 0.0, 0.0, "사내 단가"),
    ("센서", "센서 헤드", "IST", "MiniSens Pt1000 F0.1", "온도 소자 1.6×1.2 mm (센서 프로브 P-202에 실장)", "-", 1, 0.50, 3.00, "추정"),
    ("커넥터", "P-204", "M Connect", "TBD (두텍 사용품)", "M12 8핀 수컷 전면 장착형 M16×1.5, 리드선형 (W-2 납땜)", "-", 1, 2.0, 10.0, "TBD"),
    ("하네스", "W-2", "JST", "GHR-08V-S", "GH 1.25 mm 8핀 소켓 하우징 (M12 하네스 W-2)", "-", 1, 0.06, 0.15, "제안"),
    ("하네스", "W-2", "JST", "SSHL-002T-P0.2", "GH 크림프 단자 AWG 30–26", "-", 8, 0.03, 0.06, "제안"),
    ("하네스", "W-2", "TBD", "PTFE AWG28 전선", "UL1213 계열 200 °C, 8심 × 40±2 mm 설계값(절단/완성 길이 확인 필요) + 수축튜브 (M12 핀 납땜)", "-", 1, 0.15, 0.40, "추정"),
    ("하네스", "W-1", "JST", "SHR-04V-S", "SH 1.0 mm 4핀 소켓 하우징 (센서 하네스 W-1)", "-", 1, 0.04, 0.10, "제안"),
    ("하네스", "W-1", "JST", "SSH-003T-P0.2-H", "SH 크림프 단자 AWG 32–28", "-", 4, 0.03, 0.06, "제안"),
    ("하네스", "W-1", "TBD", "PTFE AWG30 전선", "UL1213 계열 200 °C, 4심 × 40±2 mm 설계값(절단/완성 길이 확인 필요) (HTX99R 뒤 핀 납땜 + 수축튜브)", "-", 1, 0.10, 0.30, "추정"),
    ("조립", "-", "-", "SMT 양면 실장", "1k 기준 조립비", "-", 1, 2.00, 4.00, "추정"),
]


def build_rows():
    rows = []
    with open(os.path.join(OUTD, PROJECT + "_BOM.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (r["Symbol"], r["Value"])
            if key not in MAP:
                raise KeyError(f"부품리스트 매핑 없음: {key}")
            cat, mfr, mpn, desc, lo, hi, st = MAP[key]
            lc = LCSC.get(key)
            lcsc, jt, lnote = ("", "", "")
            if lc:
                mfr, mpn, lcsc, jt, lnote = lc
                if lnote:
                    desc = f"{desc} [LCSC: {lnote}]"
            fp = r["Footprint"].split(":")[-1]
            rows.append(dict(cat=cat, ref=r["References"], mfr=mfr, mpn=mpn, desc=desc, val=r["Value"], fp=fp,
                             qty=int(r["Qty"]), lo=lo, hi=hi, st=st, verify=r.get("Verify", ""), lcsc=lcsc, jt=jt))
    return rows


def write_csv(rows):
    p = os.path.join(OUTD, PROJECT + "_parts_list.csv")
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["No", "분류", "참조번호", "수량", "값", "풋프린트", "제조사", "품번", "설명", "단가USD_하한", "단가USD_상한", "상태", "LCSC", "JLC구분"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["cat"], r["ref"], r["qty"], r["val"], r["fp"], r["mfr"], r["mpn"], r["desc"], r["lo"], r["hi"], r["st"], r["lcsc"], r["jt"]])
        for j, (cat, ref, mfr, mpn, desc, fp, qty, lo, hi, st) in enumerate(EXTRA, len(rows) + 1):
            w.writerow([j, cat, ref, qty, "-", fp, mfr, mpn, desc, lo, hi, st, EXTRA_LCSC.get(mpn, ""), "LCSC 주문" if mpn in EXTRA_LCSC else ""])
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
           "단가 하한 (USD)", "단가 상한 (USD)", "금액 하한 (USD)", "금액 상한 (USD)", "상태", "LCSC", "JLC 구분"]
    ws.append(hdr)
    for c in range(1, len(hdr) + 1):
        cell = ws.cell(1, c)
        cell.font = Font(name=F, size=10, bold=True, color="FFFFFF")
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = box
    allrows = [(r["cat"], r["ref"], r["qty"], r["val"], r["fp"], r["mfr"], r["mpn"], r["desc"], r["lo"], r["hi"], r["st"], r["lcsc"], r["jt"])
               for r in rows]
    allrows += [(cat, ref, qty, "-", fp, mfr, mpn, desc, lo, hi, st, EXTRA_LCSC.get(mpn, ""), "LCSC 주문" if mpn in EXTRA_LCSC else "")
                for cat, ref, mfr, mpn, desc, fp, qty, lo, hi, st in EXTRA]
    for i, (cat, ref, qty, val, fp, mfr, mpn, desc, lo, hi, st, lcsc, jt) in enumerate(allrows, 1):
        rr = i + 1
        ws.append([i, cat, ref, qty, val, fp, mfr, mpn, desc, lo, hi, f"=D{rr}*J{rr}", f"=D{rr}*K{rr}", st, lcsc, jt])
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
    widths = [5, 8, 26, 8, 16, 26, 12, 30, 48, 12, 12, 12, 12, 10, 11, 11]
    for c, wdt in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(c)].width = wdt
    ws.freeze_panes = "D2"
    tab = Table(displayName="PartsList", ref=f"A1:P{last}")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(tab)
    ws.cell(1, 10).comment = Comment("1,000대 기준 추정 단가. 출처: docs/hw/bom-cost.md (유통사 검색가), "
                                     "MCU는 두텍 구매 이력(G0B1CCT6 2,060원/100개). 대리점 견적으로 확정.", "HMT500")

    # ── 요약 시트 ──
    sm["A1"] = PROJECT + " 전자부 부품리스트 — 요약"
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
        "· 핀 번호 확인 대상 IC: 없음 — 전 IC 제조사 데이터시트로 핀 대조 완료 (회로도 v0.8, STM32는 KiCad 공식 심볼). TPS2660 RTN은 GND와 분리 (R22 삭제).",
    ]
    for i, t in enumerate(notes):
        cell = sm.cell(n + i, 1, t)
        cell.font = bold if i == 0 else Font(name=F, size=10)
    for c, wdt in zip("ABCDEF", (16, 10, 16, 16, 16, 16)):
        sm.column_dimensions[c].width = wdt
    p = os.path.join(OUTD, PROJECT + "_parts_list.xlsx")
    wb.save(p)
    return p


def main():
    rows = build_rows()
    print(write_csv(rows))
    print(write_xlsx(rows))


if __name__ == "__main__":
    main()
