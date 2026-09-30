# HMT500(260313) JLC 주문 패키지

작성 2026-09-30 · 기구 Rev H · 회로·PCB HMT500(260313A)

| 서비스 | 대상 | 폴더 | 상태 |
|---|---|---|---|
| **JLCPCB** (PCB + PCBA) | PCB 1종(4층, 57 × 23)과 양면 부품 조립. 측정·MCU·전원·출력이 모두 한 보드 | `jlcpcb/` | BOM·CPL 준비 완료. LCSC 52/57줄 (나머지 5줄 글로벌 소싱, 결정 #34·#35). **배선 전**이라 거버 없음 |
| **JLCCNC** (CNC 가공) | 바디 M-101, 센서 보호캡 M-102(두텍 390000-001100과 같은 형상), 하우징 M-103, 엔드캡 M-104 (SUS316L, 시제품 SUS304); 홀더 M-105, 지지링 M-106 (PEEK) | `jlccnc/` | STEP + 도면 PDF + 주문표 준비 완료 |
| **JLC3D** (3D 프린트) | 조립 공구 T-001 밀대. 선택: 홀더·링 끼움 확인용 시제품 | `jlc3d/` | STL/STEP + 주문표 준비 완료 |
| **JLCMC** (표준 기계 부품) | M2 나사 3종, M3 무두나사, O링 2종, 본디드 씰 | `jlcmc/` | 사양·수량 준비 완료. JLCMC 품번은 검색 후 기입 |
| LCSC (JLC 계열 부품몰) | 하네스 W-1·W-2 JST 하우징·콘택트, PTFE 선, 샤시 선 링 단자 | `lcsc/` | JST 하우징·콘택트 LCSC 번호 기입 완료. PTFE 선·링 단자는 조회 후 기입 |

JLC 계열로 주문하지 않는 것은 다음과 같습니다.
- 두텍 사내품: HTX99R 센서 커넥터, M12 커넥터 P-204, 센서 프로브(MK33 + Pt1000).
- 에폭시(선정 미결), 나사 고정제·실런트.

수량은 시제품 **5세트**로 가정했습니다. 바꾸려면 `make_mech_package.py`의 `SETS` 값을 고칩니다.

## JLCPCB (PCB + 조립)

| 파일 | 내용 |
|---|---|
| `HMT500(260313A)_CPL_JLC.csv` | 부품 위치: Designator, Mid X/Y (mm), Layer, Rotation. KiCad 배치 그대로이고 거버와 같은 좌표계. 82개 |
| `HMT500(260313A)_BOM_JLC.csv` | Comment, Designator, Footprint, LCSC Part #. 50줄 |
| `jlc_parts_map.csv` | 값·풋프린트 → LCSC 번호·JLC 구분(Basic/Extended)·회전 보정. **여기만 채우면** BOM이 다시 생성됨 |

- 생성: `python3 manufacturing/jlc/make_jlcpcb_files.py`
- J2(Tag-Connect 패드)와 J5(샤시 선 구멍)는 부품이 없어서 BOM·CPL에서 뺐습니다.
- 주문 조건: 4층, 1.6 mm, ENIG, 최소 간격·선폭 0.15, 최소 드릴 0.2(TPS2660 방열 비아), **양면 조립**(Standard PCBA).
- 거버는 배선을 마친 뒤 `sh hardware/kicad/export_gerbers.sh`로 뽑습니다(`HMT500(260313A).zip`).
- 회전: JLC 미리보기에서 부품 방향을 확인합니다. 어긋난 패키지는 `jlc_parts_map.csv`의 `rot_offset`에 적습니다.

## JLCCNC (가공품)

`order_jlccnc.csv`에 부품별 재질, 대체 재질, 후처리, 나사, 공차가 있고, 부품마다 STEP과 도면 PDF가 한 쌍입니다. 주문할 때 아래를 **주문 메모에 꼭 적습니다.**

1. **왼나사:** 하우징 뒤 M26×1-LH 암나사, 엔드캡 M26×1-LH 수나사(턴버클). 앞쪽은 오른나사입니다.
2. **가는 나사·관용 나사:** 바디 G1/2-A(ISO 228-1), M26×1, M10×1.0 암나사(나사 길이 5.5), 엔드캡 M16×1.5 암나사. JLCCNC 표준 나사 목록에 없으면 도면 지시로 요청합니다.
3. **O링 자리:** Ø27 f7(바디·엔드캡) / Ø27 H8(하우징 양 끝), 표면 Ra 0.8.
4. **재질:** SUS316L이 없으면 316. 하우징·엔드캡은 304도 가능합니다(오일에 닿지 않음). PEEK가 없으면 시제품만 POM으로 하고, 양산은 PEEK로 합니다.
5. **후처리:** 스테인리스는 부동태화. 하우징 외면 레이저 마킹은 JLCCNC 옵션을 확인하고, 없으면 사내에서 합니다.

## JLC3D (3D 프린트)

- **T-001 밀대:** W-2 플러그를 하우징 안 19.5 mm 깊이의 J1에 밀어 넣는 공구입니다. SLA 레진 또는 MJF PA12로 2개.
- 홀더·링 끼움 확인용(선택): SLA 고정밀 레진. PEEK 가공품을 받기 전에 PCB, 플러그, 창 크기를 확인합니다.

## JLCMC · LCSC

- `jlcmc/order_jlcmc.csv`: 나사 A4-70(ISO 14580), O링 FKM 75, 본디드 씰. 품번 칸은 JLCMC에서 검색해 채웁니다.
- `lcsc/order_lcsc_harness.csv`: JST SH·GH 하우징·콘택트, PTFE 선, M2 링 단자. 하네스는 사내에서 만듭니다(압착 공구: JST 정품 또는 동등품).

## 부품 번호(LCSC) 매핑 — 결정 #34 (2026-09-30)

LCSC 품번은 `hardware/kicad/make_parts_list.py`의 `LCSC` 표가 기준입니다(웹 검색 결과의 LCSC 주소·제목으로 대조). 부품리스트 xlsx/csv의 "LCSC"·"JLC 구분" 열과 이 폴더 BOM에 같이 들어갑니다. 57줄 중 52줄에 LCSC 번호가 있습니다 (결정 #35 반영).

- **글로벌 소싱 5줄 (LCSC 번호 빈칸):** U4 STM32G0B1CCT3 (125 °C 등급 — LCSC엔 85 °C CCT6뿐), U2 LMR36006BRNXR, R19 PLTT0603Z4021 (0.02 %·5 ppm), R1·R30·R40 Vishay CRCW-HP 펄스 내성형. JLC 부품 매칭 화면에서 Global Sourcing으로 같은 품번을 고르거나 사급합니다.
- **LCSC에 맞춰 바꾼 풋프린트:** C6·C10 22 µF 25 V 1206 → 1210, C16·C17 220 nF 100 V 0603 → 0805, R1 MELF → 2512, L2 XAL4030 → XAL4040 (높이 4.0). C3는 Y2 1812 대신 2 kV X7R 1812 (DC 기기라 Y2 불필요).
- **주문 전 확인:** L1 Bourns SRF0905-102Y는 WE-SL2 풋프린트를 그대로 씀 — 랜드·권선 핀 배정을 Bourns 데이터시트로 대조 (이 작업 환경에서 bourns.com 접속 불가). TVS3301(약 88개)·SRF0905(약 810개) 재고가 적음. Basic 여부와 재고는 JLC 화면이 최종.
