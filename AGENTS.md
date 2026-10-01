# AGENTS.md — HMT500(260313) 오일 수분 트랜스미터 (두텍 DOTECH)

이 파일은 이 저장소를 맡는 AI 에이전트(Codex 등)용 인계 문서입니다. 작업 전에 끝까지 읽으세요.
마지막 인계: 2026-10-01 (기구 Rev I 및 Mac 검사 호환 반영). 사람 담당자: 두텍 대표 (지시는 한국어).

## 1. 제품 한 줄

오일(윤활유·유압유) 속 수분(aw, ppm)과 온도를 재는 프로브형 트랜스미터. 전원 12–28 V DC, 4–20 mA/0–10 V × 2 + RS-485 Modbus RTU,
G½ 나사·M12 8핀 커넥터, 외형은 E+E EE364와 같은 치수(기구 Rev I). 프로젝트 번호 **HMT500(260313A)** = 회로·PCB·거버 파일명.

## 2. 저장소·폴더

- GitHub: `okchois/Oilinwater`, 작업 브랜치 **`claude/oil-moisture-transmitter-shji8x`** (main 아님. PR은 사람이 요청할 때만)

| 폴더 | 내용 |
|---|---|
| `hardware/kicad/` | **회로도·PCB 생성기** (`gen_hmt500.py` = 모든 부품·연결의 원본), 배치(`place_pcb.py`), 부품리스트(`make_parts_list.py` — 제조사 품번·**LCSC 표**), 넷리스트 검사(`check_netlist.py`), 풋프린트 `lib/HMT500_260313A.pretty/` |
| `hardware/kicad/HMT500(260313A)/` | 생성 결과: `.kicad_sch`(8시트) `.kicad_pcb` `.net` `_schematic.pdf` `_BOM.csv` `_parts_list.xlsx/.csv` `placement.json/.png` |
| `hardware/mech/` | 기구 (CadQuery): `hmt500_params.py`(모든 치수), `hmt500_cad.py`(STEP), `hmt500_drawings.py`+`make_pdf.sh`(도면), `assembly_sim.py`(조립 시뮬레이션 31항목), `assembly_procedure.py`(조립 시방서 PDF), `out/` |
| `manufacturing/jlc/` | 주문 패키지: `jlcpcb/`(BOM·CPL — `make_jlcpcb_files.py`), `jlccnc/` `jlc3d/` `jlcmc/` `lcsc/`(기구·하네스 — `make_mech_package.py`) |
| `firmware/` | 자체 RS-485 부트로더 코어(`bootloader/bl_core.*`, 호스트 시뮬레이터), 공용(`common/`). **앱 펌웨어는 아직 없음** |
| `tools/` | `fwupdate.py`(PC 업데이트 도구), `moisture_calc.py` |
| `tests/` | `test_kicad_gen.py`(작도 규칙·넷·배치), `test_mech_drawings.py`, `test_bootloader.py` |
| `docs/` | **`decision-log.md`(결정 #1–#41 + 미결 항목 — 가장 중요)**, `hw/`(회로 설계서·검토서·외부 검수 대응·배치), `market/`, `mech/`, `rs485-bootloader-design.md`, `prompts/` |

## 3. 현재 상태 (2026-10-01)

| 단계 | 상태 |
|---|---|
| 기구 Rev I, 도면, STEP, 조립 시방서 HMT500-A-001, JLCCNC 주문 패키지 | 형상 개선 완료, 실제 품번·가공성·압력·온도 확인 전 주문 보류 |
| 회로도 v0.10 (부품 110, 넷 81, 넷리스트 일치) | 완료 — 외부 검수 H01–H11 반영(결정 #35), DAC 확정(#37), JLC 부품(#38·#39) |
| PCB 배치 (110개 전부, 4층 57 × 23 mm, pcbnew DRC 간격 오류 0) | 완료 — **배선 전** |
| JLC BOM·CPL (61줄 중 59줄 LCSC) | 완료 — 남은 2줄: 2.2 µF 50 V X7R 0805(C61), 22.1k 1 % 0402(R9·R52) |
| **PCB 배선 → 거버 → JLCPCB 주문** | **다음 할 일** |
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
   kicad-cli sch export netlist -o "hardware/kicad/HMT500(260313A)/HMT500(260313A).net" "hardware/kicad/HMT500(260313A)/HMT500(260313A).kicad_sch"
   python3 hardware/kicad/check_netlist.py "hardware/kicad/HMT500(260313A)/HMT500(260313A).net"   # errors: 0
   kicad-cli sch export pdf -o "hardware/kicad/HMT500(260313A)/HMT500(260313A)_schematic.pdf" "hardware/kicad/HMT500(260313A)/HMT500(260313A).kicad_sch"
   python3 hardware/kicad/make_parts_list.py
   python3 hardware/kicad/place_pcb.py                       # 'ERROR ... no free place'가 없어야 함
   python3 manufacturing/jlc/make_jlcpcb_files.py
   python3 -m unittest discover -s tests
   ```
   DRC: 이 환경의 `kicad-cli 7.0.11`에는 `pcb drc`가 없음 → `pcbnew.WriteDRCReport(board, path, pcbnew.EDA_UNITS_MILLIMETRES, True)`로. 간격(clearance)·코트야드 오류 0이어야 함.
   기구를 바꾸면: `hmt500_cad.py`, `assembly_sim.py`(NG 0, 몰딩 유동은 WARN/실험 필요), `hmt500_drawings.py` + `make_pdf.sh`, `tests/test_mech_drawings.py`.
3. 기판이 꽉 차 있음 (윗면 657 / 아랫면 759 mm² 코트야드). 부품 추가 시 `place_pcb.py`의 PLAN 순서·`("pin", IC, 핀)` 기준이 결과를 크게 바꿈 → 핀 거리(디커플링·벅 루프)를 확인할 것.
4. 결정이 생기면 `docs/decision-log.md`에 번호를 이어서 기록 (#42부터). 관련 문서(`docs/hw/circuit-design.md` 맨 위 요약 등)도 함께.
5. 데이터시트 값은 원문으로 확인하고, 확인 못 한 값은 "확인 필요"로 표시. **저작권 있는 데이터시트 PDF는 커밋 금지.**
6. 문서는 한국어, 쉬운 말. 사람에게 보고할 때 바뀐 것·남은 위험·결정 필요한 것을 구분.
7. 커밋은 작업 브랜치에 푸시. main 직접 푸시·강제 푸시 금지.

## 6. 다음 할 일 (우선순위)

1. **PCB 배선** (4층): 전원·벅 루프(U2·U15 입력 C, 인덕터)·eFuse RTN 구리, DAC·TPS26611·R30/R40·TVS 짧게, 측정부(PCAP04·ADS1220) 가드, CHASSIS 넷클래스(간격 1.0, 선폭 0.5) J5까지 전용 선. 배치 메모: `docs/hw/pcb-placement-260313A.md`, `docs/hw/final-review-260313A.md` H절(남은 거리 문제: C54, R30/R40, D41, C47, GDT1–J5).
2. 거버·드릴 생성 → JLCPCB 주문 패키지 (BOM·CPL 회전 보정 확인).
3. 앱 펌웨어: 요구 F1–F6 (`docs/hw/external-review-response-260930.md` 6절), 부트로더 STM32G0B1 포팅.
4. 주문 전 확인: L1 Bourns SRF0905-102Y ↔ WE-SL2 풋프린트, L2/L3 SMNR4020 ↔ NR-40xx 랜드, LCSC 미확인 2줄.

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
