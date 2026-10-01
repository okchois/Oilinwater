# 재검수 자료 — HMT500(260313A) 회로도 v0.9 (외부 검수 H01–H11 반영판)

- 저장소: https://github.com/okchois/Oilinwater
- 브랜치: `claude/oil-moisture-transmitter-shji8x`
- 회로도 PDF SHA-256: `f4b4e7481a12a026eaa5aba49e8b245e8aa3d1d5f3d205bcc02c9f5e2032d8f0` (1차 검수 원본은 `814608…edca`)

## 먼저 볼 것

| 자료 | 경로 |
|---|---|
| 1차 검수 대응 (항목별 판단·조치, 출력 부하 표, 전류 예산, 펌웨어 F1–F6, 시험 T1–T7) | `docs/hw/external-review-response-260930.md` |
| 회로도 PDF (A3 8장) | `hardware/kicad/HMT500(260313A)/HMT500(260313A)_schematic.pdf` |
| 넷리스트 (KiCad 내보내기, 81넷) | `hardware/kicad/HMT500(260313A)/HMT500(260313A).net` |
| 결정 기록 (#31 부트로더, #33–#35 이번 변경) | `docs/decision-log.md` |

## 원본·보조 자료

| 자료 | 경로 |
|---|---|
| KiCad 원본 (회로도 8시트, PCB, 심볼) | `hardware/kicad/HMT500(260313A)/` |
| 회로도 생성기 (모든 부품값·연결의 원본) | `hardware/kicad/gen_hmt500.py` |
| 넷리스트 대조 검사 (그린 회로 = 설계 의도) | `hardware/kicad/check_netlist.py` |
| 부품리스트 (제조사 품번·LCSC·JLC 구분) | `hardware/kicad/HMT500(260313A)/HMT500(260313A)_parts_list.xlsx`, `.csv` |
| JLC 조립 BOM·CPL | `manufacturing/jlc/jlcpcb/` |
| PCB 배치 그림·데이터 (110개, 배선 전) | `hardware/kicad/HMT500(260313A)/placement.png`, `placement.json` |
| 회로 설계서 | `docs/hw/circuit-design.md` |
| 3중 검토서 (내부) | `docs/hw/final-review-260313A.md` |
| 자체 RS-485 부트로더 설계 | `docs/rs485-bootloader-design.md` |

## 1차 검수 이후 바뀐 회로 (결정 #33–#39)

- D3 PMEG10010ELR 직렬 쇼트키 (D2 뒤·U1 앞, U1 입력 넷 VIN_D) — H01
- D60/D61 TVS3301 (RS485_A_EXT, RS485_B_EXT – GND), U11 THVD2410DGKR (VSSOP-8) — H02
- D50 BZX84C24LT1G (27 → 24 V) — H04 → 결정 #37에서 VAO 16.1 V로 대체 (D50 삭제)
- ADS1220 IDAC = 250 µA 고정 문구 — H08
- **결정 #37 (DAC 확정, IVS320 AO rev 1.0 방식):** VAO 16.1 V 벅 U15 LMR51606 (DAC AVDD·TPS26611 +Vs·OPA197 V+), 제너 폴로워·C43 삭제, CMP 보상 4.7 nF + 100 pF, DAC 출력 클램프 BAS70-04 (D41/D51)
- **결정 #38·#39 (샘플 단계 JLC 부품 우선):** U2 5 V 벅 LMR51606 (LMR36006 대체), R19 0.1 %·25 ppm, R1·R30·R40 일반 2512, MCU STM32G0B1CCT6 (85 °C)
- C7 삭제, 저전압 R·C 37개 0402, C22 330 pF C0G (센서 MK33-W 300 pF), L2 XGL4040-153MEC, LCSC 대체품 (결정 #34)

## 재검수 요청 범위 (제안)

1. H01·H02·H03·H04 수정(결정 #35·#37)이 지적을 해소하는지, VAO 16.1 V 벅 설계(LMR51606) 적합성, 새 부품이 다른 문제(누설, 정격, 신호 품질)를 만들지 않는지
2. 결정 #34의 LCSC 대체품(정격·패키지·핀 배정) 적합성, 특히 L1 SRF0905-102Y의 WE-SL2 풋프린트 호환
3. 대응 문서의 계산(출력 부하 표, 전류 예산)과 펌웨어·시험 요구의 누락
4. 아직 없는 것: PCB 배선(거버), 펌웨어 앱, 시험 성적서
