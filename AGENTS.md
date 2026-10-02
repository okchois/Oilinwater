# AGENTS.md — HMT500(ED260313A) 오일 수분 트랜스미터 (두텍 DOTECH)

이 파일은 이 저장소를 맡는 AI 에이전트(Codex 등)용 인계 문서입니다. 작업 전에 끝까지 읽으세요.
마지막 인계: 2026-10-02 (PCB A5 배선 연결 완료, 제조 검토/발주 보류). 사람 담당자: 두텍 대표 (지시는 한국어).

## 1. 제품 한 줄

오일(윤활유·유압유) 속 수분(aw, ppm)과 온도를 재는 프로브형 트랜스미터. 전원 12–28 V DC, 4–20 mA/0–10 V × 2 + RS-485 Modbus RTU,
G½ 나사·M12 8핀 커넥터, 외형은 E+E EE364와 같은 치수(기구 Rev I). 프로젝트 번호 **HMT500(ED260313A)** = 회로·PCB·거버 파일명.

## 2. 저장소·폴더

- GitHub: `okchois/Oilinwater`, 작업 브랜치 **`claude/oil-moisture-transmitter-shji8x`** (main 아님. PR은 사람이 요청할 때만)

| 폴더 | 내용 |
|---|---|
| `hardware/kicad/` | **회로도·PCB 생성기** (`gen_hmt500.py` = 모든 부품·연결의 원본), 배치(`place_pcb.py`), 부품리스트(`make_parts_list.py` — 제조사 품번·**LCSC 표**), 넷리스트 검사(`check_netlist.py`), 풋프린트 `lib/HMT500_260313A.pretty/` |
| `hardware/kicad/HMT500(ED260313A)/` | 생성 결과: `.kicad_sch`(8시트) `.kicad_pcb` `.net` `_schematic.pdf` `_BOM.csv` `_parts_list.xlsx/.csv` `placement.json/.png` |
| `hardware/mech/` | 기구 (CadQuery): `hmt500_params.py`(모든 치수), `hmt500_cad.py`(STEP), `hmt500_drawings.py`+`make_pdf.sh`(도면), `assembly_sim.py`(조립 시뮬레이션 31항목), `assembly_procedure.py`(조립 시방서 PDF), `out/` |
| `manufacturing/jlc/` | 주문 패키지: `jlcpcb/`(BOM·CPL — `make_jlcpcb_files.py`), `jlccnc/` `jlc3d/` `jlcmc/` `lcsc/`(기구·하네스 — `make_mech_package.py`) |
| `firmware/` | 자체 RS-485 부트로더 코어(`bootloader/bl_core.*`, 호스트 시뮬레이터), 공용(`common/`). **앱 펌웨어는 아직 없음** |
| `tools/` | `fwupdate.py`(PC 업데이트 도구), `moisture_calc.py` |
| `tests/` | `test_kicad_gen.py`(작도 규칙·넷·배치), `test_mech_drawings.py`, `test_bootloader.py` |
| `docs/` | **`decision-log.md`(결정 #1–#58 + 미결 항목 — 가장 중요)**, `hw/`(회로 설계서·검토서·외부 검수 대응·배치), `market/`, `mech/`, `rs485-bootloader-design.md`, `prompts/` |

## 3. 현재 상태 (2026-10-02)

| 단계 | 상태 |
|---|---|
| 기구 Rev I, 도면, STEP, 조립 시방서 HMT500-A-001, JLCCNC 주문 패키지 | 형상 개선 완료, 실제 품번·가공성·압력·온도 확인 전 주문 보류 |
| 회로도 v0.10 (부품 110, 넷 81, 넷리스트 일치) | 완료 — 외부 검수 H01–H11 반영(결정 #35), DAC 확정(#37), JLC 부품(#38·#39) |
| PCB A5 (110개, 6층, 기구 Rev I 외형 유지) | **배선 연결 완료 — DRC 오류 0, 미연결 0**. `docs/hw/artwork-a5-261002.md` 참조. 제조 DFM/발주 보류. A1–A4 스냅샷 보존 |
| JLC BOM·CPL (61줄 모두 LCSC) | 2026-10-03 매칭: C61=C125847, R9/R52=C43473, C4=C318579 정정. 제조사/패키지 대조 완료; 재고/실장 가능 여부는 주문 시 확인 |
| **PCB 배선 → 거버 → JLCPCB 주문** | A5 거버·드릴·BOM/CPL 제조 검토 묶음 생성. JLC 업로드/주문은 하지 않음 |
| 앱 펌웨어 (Modbus, PCAP04, ADS1220, DAC8760, 부트로더 STM32 포팅) | 미착수 |
| 시제품 시험 (시험 계획 T1–T7) | 기판 수령 후 |

## 4. 확정 사항 (바꾸려면 두텍 승인 필요 — `docs/decision-log.md`)

- 전원 **12–28 V DC (최대 28 V)**, 입력 DC 절대 최대 33 V(TVS3301 한계). 전류 출력 부하 **RL ≤ 500 Ω** (전원 ≥ 18 V) — #36
- AO D30/D40 = **TVS1401DRBR (±14 V)** — #41. AO ±28/30 V 지속 오결선 무손상 보장 제외. 입력/RS-485 TVS3301 유지.
- 입력: SMDJ(1단) → R1 → TVS3301(2단) → **D3 직렬 쇼트키** → eFuse TPS2660 (RTN은 GND와 분리) — #35
- 5 V: **LMR51606** 벅(U2) → 3.3 V LDO TPS7A2033 — #38
- 아날로그 출력: DAC8760 ×2 + TPS26611 보호 + OPA197 +VSENSE 버퍼. **DAC 전원 VAO 16.1 V 벅(U15 LMR51606)**, CMP 4.7 nF + 100 pF, 출력 클램프 BAS70-04 — #37 (사내 VibrationSensor IVS320 AO rev 1.0과 같은 방식)
- RS-485: THVD2410DGKR + 버스 TVS3301 ×2, DE 10 k 풀다운 — #35
- MCU **STM32G0B1** (샘플 = CCT6 85 °C, 양산 = 온도 사양 확정 후 CCT3 검토) — #9, #39
- 펌웨어 업데이트 = **자체 RS-485 부트로더** (ST ROM 부트로더 사용 안 함) — #31, `docs/rs485-bootloader-design.md`
- 센서 IST **MK33-W 300 pF** (C22 330 pF C0G), 하네스 커넥터 JST SH/GH, 출력 보호 TPS26611 유지 — #33
- **샘플 단계 부품은 JLCPCB(LCSC) 품번 우선** — #38·#39

## 5. 작업 규칙 (꼭 지킬 것)

1. **KiCad 파일을 손으로 고치지 말 것.** 회로 변경은 `hardware/kicad/gen_hmt500.py`, 배치는 `place_pcb.py`, 품번은 `make_parts_list.py`(MAP·LCSC 표)에서. 그다음 재생성.
2. 재생성·검사 순서 (모두 통과해야 커밋):
   ```
   python3 hardware/kicad/gen_hmt500.py                      # 작도 규칙 검사 포함 (겹침·용지 밖이면 실패)
   kicad-cli sch export netlist -o "hardware/kicad/HMT500(ED260313A)/HMT500(ED260313A).net" "hardware/kicad/HMT500(ED260313A)/HMT500(ED260313A).kicad_sch"
   python3 hardware/kicad/check_netlist.py "hardware/kicad/HMT500(ED260313A)/HMT500(ED260313A).net"   # errors: 0
   kicad-cli sch export pdf -o "hardware/kicad/HMT500(ED260313A)/HMT500(ED260313A)_schematic.pdf" "hardware/kicad/HMT500(ED260313A)/HMT500(ED260313A).kicad_sch"
   python3 hardware/kicad/make_parts_list.py
   python3 hardware/kicad/place_pcb.py                       # 'ERROR ... no free place'가 없어야 함
   python3 manufacturing/jlc/make_jlcpcb_files.py
   python3 -m unittest discover -s tests
   ```
   DRC: 이 환경의 `kicad-cli 7.0.11`에는 `pcb drc`가 없음 → `pcbnew.WriteDRCReport(board, path, pcbnew.EDA_UNITS_MILLIMETRES, True)`로. 간격(clearance)·코트야드 오류 0이어야 함.
   기구를 바꾸면: `hmt500_cad.py`, `assembly_sim.py`(NG 0, 몰딩 유동은 WARN/실험 필요), `hmt500_drawings.py` + `make_pdf.sh`, `tests/test_mech_drawings.py`.
3. 기판이 꽉 차 있음 (윗면 657 / 아랫면 759 mm² 코트야드). 부품 추가 시 `place_pcb.py`의 PLAN 순서·`("pin", IC, 핀)` 기준이 결과를 크게 바꿈 → 핀 거리(디커플링·벅 루프)를 확인할 것.
4. 결정이 생기면 `docs/decision-log.md`에 번호를 이어서 기록 (#59부터). 관련 문서(`docs/hw/circuit-design.md` 맨 위 요약 등)도 함께.
5. 데이터시트 값은 원문으로 확인하고, 확인 못 한 값은 "확인 필요"로 표시. **저작권 있는 데이터시트 PDF는 커밋 금지.**
6. 문서는 한국어, 쉬운 말. 사람에게 보고할 때 바뀐 것·남은 위험·결정 필요한 것을 구분.
7. 커밋은 작업 브랜치에 푸시. main 직접 푸시·강제 푸시 금지.

## 6. 다음 할 일 (우선순위)

1. **A5 제조 검토**: `docs/hw/artwork-a5-261002.md`를 먼저 읽을 것. 미연결 0, 일반 DRC 오류 0, dangling 경고 0, C44/D1 실크→Fab 라이브러리 차이 경고 2개. In1 GND 전용이며 In4는 GND 동박과 제한된 7개 넷을 혼용한다. `artwork_a5.py`의 배선 범위를 지킬 것. 전원·서지 병목, 신호 에지·센서 잡음·발열·EMC는 실물/제조 검토 필요.
2. `manufacturing/jlc/artwork_A5_review/`로 DFM 준비. 0.15 mm 비아/POFV 공정 혼용, JLC 재고/실장 가능 여부, CPL 방향을 확인한 뒤 발주 판단.
3. 앱 펌웨어: 요구 F1–F6 (`docs/hw/external-review-response-260930.md` 6절), 부트로더 STM32G0B1 포팅.
4. 주문 전 확인: L1 Bourns SRF0905-102Y 랜드/핀은 원문 대조 완료. L2/L3는 SMNR4020 전용 랜드로 수정(#42); 포화 전류 정의는 확인 필요. LCSC 빈칸 0. 결정 #53 매칭표와 주문 시 재고/실장 가능 여부 확인.

## 7. 미결 (두텍 결정 필요)

- **제품 온도 사양** (주위 온도, 몰딩 안 전자부 최고 온도) → MCU CCT6/CCT3, GDT1(85 °C), JST(85 °C) 판단
- 에폭시 선정, JST −40 °C 확인, HSI 클럭 정확도, 압력 격벽 시험 — `docs/decision-log.md` 미결 표

## 8. 외부 검수 이력

- 1차 (코덱스, 2026-09-30): H01–H11 → 대응 `docs/hw/external-review-response-260930.md`
- 재검수 자료 목록: `docs/hw/rereview-package-260930.md`

## 9. 환경 메모

- KiCad 7.0.11 (`kicad-cli`, `pcbnew` 파이썬), Python 3 (openpyxl), 기구·렌더는 CadQuery 2.x + VTK 9 + matplotlib (가상환경 권장).
- 한글 글꼴 NanumGothic (회로도 한글 메모 출력용).

## 10. Rev I 인계

`docs/mech/rev-i-implementation-261001.md` 참조. M3 경사 구멍을 축 방향으로 바꾸면 O링 홈을 침범하므로 반드시 20° 유지. STEP 나사는 단순 원통: 도면의 나사/끼워맞춤 공차를 우선 적용. 제조사 DFM 확인 필요.

## 11. PCB 초안 재현

`hardware/kicad/rebuild_artwork.sh` 사용. 기본 A5(6층)이며 `HMT_ARTWORK=A1`~`A4`로 이전 판을 재현한다. `KICAD_PYTHON`, `KICAD_CLI`, `TEST_PYTHON`으로 환경을 지정한다. A5 배치·배선 스냅샷은 배치/층수가 다르면 복원을 거부한다. **A5는 DRC 오류 또는 미연결이 있으면 재생성 실패**다. 신호 비아 0.30/0.15 mm, 혼잡 신호 선폭/간격 0.10/0.10 mm. In1 GND 전용, In4 GND 동박/제한 배선 혼용, RTN 영역은 네 내층 모두 비운다. 전원·서지·방열 비아는 별도 치수를 유지한다. `audit_artwork.py`가 POFV 후보·면적을 기록하며 공정 혼용은 제조사 DFM 확인 필요. 검사는 KiCad 10.0.6 CLI로 수행한다. 제조 검토 파일 생성은 `manufacturing/jlc/export_artwork_review.py` 사용. 발주 승인이 아니다.

## A5-R1 실크 수정
2026-10-02: 실제 PCB/거버 실크는 A5-R1. `docs/hw/artwork-a5-r1-silk-261002.md` 참조. A5 배선 스냅샷 유지, finisher가 근접 레퍼런스·지시선을 재현한다. 제조 검토 패키지는 `manufacturing/jlc/artwork_A5_R1_review/`. 이전 PDF REF 덧글은 실제 실크와 다르므로 제작 근거로 사용하지 않는다.

## 하네스 도면 발행 인계 — 결정 #49

두텍 요청(2026-10-02): 다음 기구도면 발행 때 각각의 하네스 길이를 반드시 반영한다.
- W-1 센서–J3: 현재 40±2 mm. 홀더 창 통과와 플러그 삽입에 필요한 길이를 확인.
- W-2 M12–J1: 현재 40±2 mm. 실제 M12 내부 단자·납땜·수축튜브 형상, 조립 공구 접근과 턴버클 체결 후 여유선 수납을 확인.
- W-3 J5–샤시 링 단자: 현재 25 mm, 길이 공차 확인 필요. 단자 압착·납땜 및 고정 나사 접근을 확인.
- 위 값은 현재 설계값이며 최종 제조 길이 확정이 아니다. 전선 절단 길이/단자 조립 후 완성 길이를 구분하고 탈피·압착·납땜 길이, 공차, 선색·핀맵, 굽힘/고정/수납 경로를 도면에 표기.
- 최종 값은 hmt500_params.py의 HARNESS/HARNESS2/CHASSIS_WIRE에서 관리하고 조립도·하네스 제작도·조립 시방서·구매 목록에 동기화. assembly_procedure.py의 40 mm 및 make_mech_package.py의 W-3 25 mm 등 고정 문자열도 대조. assembly_sim.py의 과거 “60 유지” 설명과 현재 40 mm 값 불일치도 도면 발행 시 정리.
- 미확정 길이는 “확인 필요”로 표시하고, 실제 길이 변경 후 조립 경로 검사를 다시 수행한다.

하네스 검토도 Rev A(결정 #50): `hardware/mech/harness_drawings.py`로 생성, `hardware/mech/out/harness/`에 W-1/W-2/W-3 및 합본 PDF. ReportLab과 NanumGothic 폰트 사용. 현재 길이·논리 핀맵만 검증; 제조 승인 도면이 아니며 #49의 미확정 치수는 그대로 남는다.

M12 선정 사양서 Rev A(결정 #51): `hardware/mech/m12_specification.py`, 결과 `hardware/mech/out/m12/`. 프로젝트 모델 외형도와 제조사 참고품은 구분되어 있으며 실제 M Connect 구매품 품번 확정이 아니다.

M12 외형도 Rev B(결정 #52): `hardware/mech/m12_outline_drawing.py`로 흑백 제조사 도면 스타일 생성. `hardware/mech/out/m12/HMT500_M12_외형도_RevB.pdf`. 모델 치수 유지, 실제 공급품 확정 아님.

## LCSC–BOM 매칭 — 결정 #53 (2026-10-03)
`manufacturing/jlc/bom_match_20261003/`에 61행/108개 PCB 매칭표, 하네스 4종, 공식 카탈로그 대조 근거. C4 번호 오류 수정, C61 YAGEO 동일 명목 사양 대체(최대 높이 1.45 mm), R9/R52 번호 보완. C22/R19 공차 표시는 기존 결정 #34/#38에 맞춰 정정. 배선/위치 동일, 전체 재생성 검사 통과. 이전 A5-R1 ZIP의 BOM은 과거 판이므로 최신 jlcpcb/ 또는 매칭 묶음의 BOM/CPL을 사용. C61의 28 V DC 바이어스 실효 용량은 확인 필요.

## A5-R2 실크·로고 (2026-10-03)
두텍 요청으로 `silk_layout.py`에서 부품 옆의 레퍼런스를 재배치하고 탑면 DOTECH 원본 워드마크(폭 8 mm)를 추가했다. 기본 높이 0.8 mm, 혼잡 위치 0.6 mm, 선폭 0.1 mm. 0.6 mm는 제조사 고정밀 권장 최소보다 작으므로 인쇄성 확인 필요. 부품 아래/패드 위 배치는 금지하며 모든 번호가 인쇄되지는 않는다. 실제 표시/누락 목록은 `artwork_metrics.json`과 `docs/hw/artwork-a5-r2-silk-logo-261003.md` 참조. 최신 거버/현재 BOM은 `manufacturing/jlc/artwork_A5_R2_review/`. 배선·위치·패드 불변.

## 정식 명칭·전체 로고 A5-R3 — 결정 #55
2026-10-03 사용자 확인: PCB 정식 명칭 **HMT500(ED260313A)**. 최신 KiCad 폴더/프로젝트 파일과 제조용 파일은 이 명칭으로 통일. 기술용 라이브러리 별칭 HMT500_260313A는 유지. A5-R2까지의 과거 릴리스는 옛 이름 그대로 보존한다.
탑면 로고는 DOTECH + SENSING & CONTROL 전체(11.5×3.20 mm), KiCad 네이티브 다각형 그룹 `DOTECH full logo`. 레퍼런스는 각 부품의 Reference 필드, PCB 명칭은 PCB_TEXT로 편집 가능. 사용자 직접 KiCad 수정 요청을 존중하고 편집본을 새로 생성해 덮어쓰지 않도록 변경 전 상태를 확인할 것. 최신 제조 검토 묶음은 `manufacturing/jlc/artwork_A5_R3_review/`.

## BOM R1 조달 변경 — 결정 #56
2026-10-03: 구매 불가 C41/C51과 R5를 같은 값의 JLC 재고품 C153291/C23029로 변경. 생성기 MAP/LCSC가 원본. PCB A5-R3 유지. 최신 제조 검토 묶음은 `manufacturing/jlc/artwork_A5_R3_BOM_R1_review/`. 이전 A5-R3 BOM 대신 이 BOM을 사용. 나머지 부족 부품은 사전 구매 및 실제 PCBA 재고 배정 확인 필요.

## BOM R2 / 회로 v0.11 — 결정 #57
프리오더 회피를 위해 R1/R3/R4/R5/R6 변경. 최신 파일은 `manufacturing/jlc/artwork_A5_R3_BOM_R2_review/`. PCB A5-R3 동박 유지, R3=845k/R5=35.7k/R6=82k. R4 실제0.1%, R1 실제5%. 상세 계산·원문·미결은 `docs/hw/procurement-bom-r2-261003.md`. 전체 보드의 비저항 재고 문제는 아직 남는다.

## 기구 Rev J — 결정 #58
사용자 확정: 시제품1세트, 홀더/지지링도3D. 금속4종 SUS304 CNC 각1, 내부M-105/106 PA12-HP MJF 각1, 공구T-001 1. 형상은Rev I 유지; 재질/공정/수량/도면 주기 변경. 출력품의 지정 공차는 후가공 검사 기준이며 출력 그대로의 끼움 보장 아님. 최신CNC4품목/3D3품목, 과거POM/SUS316L 주문표 사용 금지. 과거 조립시방서PDF의POM 표기는 폐기하고 갱신한 생성기 기준으로 재발행해야 함.
