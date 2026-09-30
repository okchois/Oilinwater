# HMT500(260313A) 회로도 검토 — 데이터시트 대조 · 최적화 계획

**상태: A–O 전부 실시 완료 (2026-09-30, 회로도 v0.8, 결정 #26).** 전원 범위 12–28 V 승인.

작성 2026-09-30 · 대상 회로도 v0.7 (82 부품, 70 넷)

## 1. 대조 자료

제조사 데이터시트 원문 (다운로드해 대조, 저장소에는 넣지 않음):

| 부품 | 문서 |
|---|---|
| LMR36006 | TI SNVSB48C (2019-10) |
| TPS2660 | TI SLVSDG2G (2019-12) |
| TPS2661x | TI SLVSFE3C (2021-12) |
| DAC8760 | TI SBAS528D (2021-12) |
| ADS1220 | TI SBAS501D |
| THVD2450 | TI SLLSF20B |
| TPS7A20 | TI 데이터시트 |
| OPA197 | TI SBOS737C |
| PCAP04 | ScioSense SC-001050-DS-6 (2023-09) |
| STM32G0B1 | st.com 접속 불가 → KiCad 공식 심볼 STM32G0B1C_B-C-E_Tx로 대조 |

## 2. 핀 대조 결과

| 부품 | 결과 |
|---|---|
| STM32G0B1CCT3, ADS1220, TPS7A2033, OPA197, THVD2450, DAC8760 | ✅ 일치 |
| TPS2660 | ⚠ 핀 번호 일치. 17번 = PowerPAD → **RTN 면에 연결** (이름 EP → RTN) |
| LMR36006 | ❌ 임시 핀 → 실제 VQFN-HR 12핀: 1 PGND, 2 VIN, 3 NC, 4 BOOT, 5 VCC, 6 AGND, 7 FB, 8 PG, 9 EN, 10 VIN, 11 PGND, 12 SW |
| TPS26611 | ❌ 임시 핀 → 실제 SOT-23-8: 1 GND, 2 MODE, 3 −Vs, 4 IN, 5 OUT, 6 +Vs, 7 EN, 8 SGOOD |
| PCAP04 | ❌ 임시 핀 → 실제 QFN24: 1 PC3, 2 GND, 3 VDD18, 4 VDD33, 5 PT1, 6 PT0REF, 7 PTOUT, 8 GND, 9 SSN, 10 MISO, 11 PG5, 12 PG2, 13 IIC_EN, 14 VDD33, 15 MOSI, 16 SCK, 17 PG3, 18 PG4, 19 PCAUX, 20 PC4, 21 PC5, 22 PC0, 23 PC1, 24 PC2 |

## 3. 데이터시트로 새로 드러난 문제

| # | 부품 | 데이터시트 내용 | 현재 회로 | 판정 |
|---|---|---|---|---|
| 1 | **TPS2660** | "RTN을 GND에 연결하면 역극성 보호가 꺼지고, 역극성 때 **영구 손상**" (9.3.5.5). R3–R5·ILIM·dVdT·IMON·MODE는 **RTN 기준** | R22 0 Ω으로 RTN–GND 연결. R5·R6·R7·C4·MODE를 GND에 연결 | **치명** |
| 2 | **TPS26611** | +Vs 권장 **최대 30 V**, 절대최대 32 V | +Vs = VIN_P. OVP 32.6 V(기준 1.19 V로 재계산)까지 올라감 | **정격 초과** |
| 3 | **DAC8760** | Rev D에서 **데이지 체인 기능 삭제**. 여러 개를 한 버스에 쓰려면 **SCLK 게이트** 필요 (8.5.1.5, Fig. 8-9) | v0.7 데이지 체인 | **지원 안 됨** |
| 4 | DAC8760 | AVDD 상승 속도 1 V/ns 이하 → **AVDD에 10 Ω 직렬** 권장 (10장 CAUTION) | 없음 | 추가 |
| 5 | DAC8760 | ALARM은 오픈 드레인, **외부 10 kΩ 풀업 필요** | MCU 내부 풀업 | 추가 |
| 6 | PCAP04 | VDD18 **≥ 4.7 µF**, VDD33 **≥ 10 µF**. VDD18은 1핀 | 1 µF 두 개 (VDD18_D/A 가정) | 수정 |
| 7 | LMR36006 | 5 V·1 MHz 권장값: L = **15 µH**, COUT = 2 × 15 µF, CFF = **20 pF** | L2 22 µH, C10 22 µF 0805 1개, CFF 없음 | 수정 |
| 8 | TPS2660 | I_OL = 12 / R_ILIM(kΩ) → 150 mA = **80.6 kΩ**. IMON은 쓰지 않으면 개방 가능 | R6 값 미정, R7 10 k | 확정·삭제 |
| 9 | PCAP04 | 단일 플로팅·접지 모드는 **DC 없음** ("other modes are DC free") | — | MK33 DC 없는 구동 **미결 해소** |

## 4. 최적화 계획

| # | 내용 | 부품 수 |
|---|---|---|
| A | LMR36006·TPS26611·PCAP04 실제 핀·풋프린트로 교체. LMR36006 = **LMR36006BRNXR** (1 MHz, 조정형 — 고정 출력형 없음). TPS2660 17번 = RTN | 0 |
| B | **TPS2660 RTN 정정:** R22 삭제, R5·R6·C4·MODE → RTN, R7 삭제(IMON 개방), R6 = 80.6 k 1 % (150 mA) | −2 |
| C | **전원 범위 12–28 V로 조정:** R5 36.5 k → 41.2 k → OVP 29.0 V (28.5–29.9 V), UVLO 8.6 V. TPS26611 +Vs 30 V 이내, EE364 전원(10–28 V)과도 맞음 | 0 |
| D | **DAC SPI를 SCLK 게이트 방식으로** (TI Fig. 8-9, IVS320과 같음): 74LVC2G32 1개 + 100 nF, LATCH1 = PB10, LATCH2 = PB11, DIN·SDO 공유(SDO는 LATCH 뒤 3-state). R33·DCEN 삭제 | +1 |
| E | DAC AVDD 10 Ω 직렬 ×2 | +2 |
| F | ALARM 두 개를 한 선으로 묶고 10 kΩ 풀업 1개 → PB3. 어느 채널인지는 상태 레지스터로 확인 | +1 |
| G | TPS26611: −Vs = GND, EN 개방(내부 풀업), MODE = GND (32 mA 제한, 100 ms 후 차단, 800 ms 재시도), SGOOD(0–3 V 출력, **Low = 정상**) → MCU. 넷 이름 OUTn_SGOOD | 0 |
| H | PCAP04: VDD18 4.7 µF 1개 (C26 삭제), VDD33 10 µF, IIC_EN = GND, INTN → PG5(11번, 레지스터로 설정), PTOUT·PT·PCAUX 미사용 개방. 중앙 패드는 GND 외 연결 금지 | −1 |
| I | 벅: L2 15 µH, C10 → 22 µF ×2 (1206 25 V), CFF 20 pF 추가 | +2 |
| J | VIN_P 벌크 4.7 µF 두 개(C43·C53) → 하나 | −1 |
| K | 문서: 전압 모드 오차 예산에 채널 간 GND 공유분 추가, 발열 대책(최소 부하 250 Ω 권장, 미사용 채널 출력 끔, DAC 간격·방열) | 0 |
| L | **출력 TVS 교체:** D30·D40 SMAJ33CA → **TI TVS3301** (TPS2661 데이터시트 Fig. 9-14 권장품). 클램프 40 V(27 A) vs SMAJ33CA 약 53 V — TPS2661 IN/OUT 절대최대 ±55 V에 여유. 누설 450 nA(85 °C)로 4–20 mA 오차도 작음, SON-8 3×3 | 0 |
| M | **PCAP04 전용 SPI3 (PB3/PB4/PB5):** PCAP04 MISO는 PG1 겸용 핀이고, SSN High일 때 Hi-Z라는 기재가 데이터시트에 없음 → ADS1220과 SPI1 공유 시 충돌 위험. ALARM → PB6, PWR_FLT → PB7로 이동. (두 칩 모두 SPI 모드 1이라 공유 자체는 가능하나, 확인 전에는 분리가 안전) | 0 |
| N | 문서: ADS1220 설정 한계 — IDAC ≤ 250 µA (IDAC 여유 AVDD − 0.9 V), R19 4.02 k로 기준 1.005 V (최소 0.75 V 이상), PGA 이득 ≤ 2 (120 °C Pt1000 0.365 V) | 0 |
| O | 문서: 전류 출력 최대 부하 = (전원 − 3 V) / 24 mA − 25 Ω (DAC 여유 AVDD − 2 V, TPS2661 RON 최대 12.5 Ω, R30 10 Ω) → 12 V: 약 350 Ω, 24 V: 약 850 Ω | 0 |

합계 (L–O 포함): 82 → 84개 (안전·정격 문제 수정으로 부품이 약간 늘어남).

유지: 입력 2단 TVS, ADS1220 (Pt1000 정확도), TPS26611 보호 방식 (#24 ⑤ 보류).

데이터시트로 문제없음을 확인한 것: TPS2660 SHDN 개방 가능(내부 2.7 V), dVdT 22 nF → 상승 4.2 ms, OVP 기준 1.19 V; LMR36006 EN–VIN 직결·PG 개방 허용, VCC 1 µF·BOOT 100 nF; TPS7A20 EN–IN 직결(내부 500 k 풀다운이라 필수); THVD2450 DE·/RE 묶음; DAC8760 방열 패드 GND, AVDD 10–36 V, REXT 비트로 외부 ISET 선택; OPA197 36 V·입력 레일투레일; ADS1220·PCAP04 모두 SPI 모드 1.

남은 확인:
- HART-IN 미사용 처리: 데이터시트에 지시 없음. 내부 35 kΩ이고 AC 결합 입력이라 개방 유지 (IVS320과 같음).
- STM32 데이터시트 원문 대조 (st.com 허용 필요. KiCad 심볼로는 확인됨).
