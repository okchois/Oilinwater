# HMT500(260313A) 회로도 검토 — 심볼 대조 · 최적화 계획 (승인 대기)

작성 2026-09-29 · 대상 회로도 v0.7 (82 부품, 70 넷)

## 1. 심볼 대조 결과

대조 자료: KiCad 공식 심볼 라이브러리(gitlab kicad-symbols, 제조사 데이터시트 기준으로 작성됨), VibrationSensor IVS320, 공개 하드웨어 PCAP04 보드(github NautyXie/pcap04-capacitance-readout), TI 데이터시트 검색 결과. ti.com·mouser 등 데이터시트 원문 사이트는 이 환경에서 막혀 있어, PDF 원문 대조는 못 했음.

| 부품 | 결과 | 근거 |
|---|---|---|
| U4 STM32G0B1CCT3 | ✅ 일치 (Tx 핀배치. TxN 변형은 PC6/PC7이 전원 → 해당 없음). SPI2 = PB13/14/15, USART2_DE = PA1 확인 | KiCad STM32G0B1C_B-C-E_Tx |
| U6 ADS1220 | ✅ 일치 | KiCad ADS1120-PW (같은 핀) |
| U3 TPS7A2033 | ✅ 일치 | KiCad TPS7A20xxxDBV |
| U12/U13 OPA197 | ✅ 일치 | KiCad OPA197xDBV |
| U7/U8 DAC8760 | ✅ 일치 (v0.7) | SBAS528D, IVS320 |
| U11 THVD2450 | ✅ 표준 SOIC-8 RS-485 배치 (1 R, 2 /RE, 3 DE, 4 D, 5 GND, 6 A, 7 B, 8 VCC) | KiCad THVD1450D·MAX481 동일 배치 |
| U1 TPS26600PWP | ⚠ 핀 번호 일치. **17번(EP)은 이름이 RTN** — 넷은 이미 EF_RTN(연결 맞음), 심볼 이름만 수정 | KiCad TPS26600PWP |
| U2 LMR36006 | ❌ **전부 틀림** (임시 핀). 실제 VQFN-HR 12핀 RNX: 1 PGND, 2 VIN, 3 NC, 4 BOOT, 5 VCC, 6 AGND, 7 FB, 8 PG, 9 EN, 10 VIN, 11 PGND, 12 SW | TI 데이터시트 검색 결과 |
| U9/U10 TPS26611 | ❌ **전부 틀림** (임시 핀, 핀 수도 다름). 실제 SOT-23-8 DDF: 1 GND, 2 MODE, 3 −Vs, 4 IN, 5 OUT, 6 +Vs, 7 EN, 8 SGOOD(Low = 정상) | TI 데이터시트 검색 결과 (출처 3개 중 2개 일치 → PDF 확인 필요) |
| U5 PCAP04 | ❌ **전부 틀림** (임시 핀). 실제 QFN24: 1 PC3, 2 GND, 3 VDD18(1개), 4 VDD33A, 5 PT1, 6 PT0REF, 7 PTOUT, 8 GND, 9 SSN, 10 MISO, 11 PG5/IRQ, 12 PG2, 13 IIC_EN, 14 VDD33B, 15 MOSI, 16 SCK, 17 PG3, 18 PG4, 19 PCAUX, 20 PC4, 21 PC5, 22 PC0, 23 PC1, 24 PC2, 25 EP=GND | 공개 PCAP04 보드 심볼 + 검색(24 = PC2, 1 = PC3 일치) |

## 2. 최적화 계획

| # | 항목 | 내용 | 부품 수 |
|---|---|---|---|
| A | 핀 수정 (필수) | LMR36006·TPS26611·PCAP04 실제 핀으로 교체, 풋프린트 확정(LMR36006 = VQFN-HR RNX, TPS26611 = SOT-23-8, PCAP04 = QFN-24 4×4), TPS2660 17번 RTN 이름 | 0 |
| B | TPS26611 연결 정리 | −Vs = GND, EN = 연결 안 함(내부 풀업), SGOOD → MCU (Low = 정상. 넷 이름 OUTn_FLT → OUTn_SGOOD, 펌웨어 논리 반전), MODE = 전류 제한 선택 | 0 |
| C | PCAP04 전원 정리 | VDD33A·VDD33B 두 핀 = +3V3A, VDD18 한 핀 → C25/C26 두 개를 한 개로. PG·PT·PCAUX 미사용 핀 처리 확정 | −1 (C26) |
| D | VIN_P 벌크 통합 | 채널별 4.7 µF/50 V(C43·C53) → 1개 공통 | −1 (C53) |
| E | TPS2660 IMON (R7) | MCU가 IMON을 읽지 않음 → 데이터시트에서 IMON 개방 허용 확인 후 R7 삭제 | −1 (확인 후) |
| F | 보류·유지 | 입력 2단 TVS(D2·R1) 유지(TPS2660 60 V 절대정격 여유), ADS1220 유지(PCAP04 내장 RDC로 Pt1000 측정 가능하나 F0.1급 정확도에 불리), 출력 보호 통일(#24 ⑤) 보류 유지 | 0 |

합계: 82 → 79개 (E 포함). 수정 후 넷리스트 대조·작도 규칙·겹침 검사·테스트 통과 확인.

미해결(데이터시트 원문 필요): TPS2660 RTN–GND 연결(R22), TPS26611 핀 PDF 재확인, TPS26611의 0–10 V 통과 여부.
