# HMT500(260313A) KiCad 회로도 v0.8

DOTECH HMT500(260313) 오일 수분 트랜스미터의 KiCad 회로도입니다.

**파일명·프로젝트 번호 = HMT500(260313A)** (결정 #25): 회로도·심볼·BOM·부품리스트·PDF, PCB 파일, 거버(`HMT500(260313A)-F_Cu.gtl` 등, 묶음 `HMT500(260313A).zip`), PCB 실크 마킹(아랫면 가운데) 모두 같은 이름을 씁니다. 거버 출력: `sh hardware/kicad/export_gerbers.sh`.

**v0.8 (결정 #26):** 모든 IC 핀을 제조사 데이터시트 원문으로 대조하고 반영했습니다 — [검토 문서](../../docs/hw/schematic-review-260313A.md).

설계 내용은 [회로 설계서](../../docs/hw/circuit-design.md)를 따릅니다.

| 파일 | 내용 |
|---|---|
| `HMT500(260313A)/HMT500(260313A).kicad_pro` | 프로젝트 (KiCad 7 형식 — KiCad 8/9에서 열면 자동 변환) |
| `HMT500(260313A)/HMT500(260313A).kicad_sch` | 최상위 시트 (하위 시트 6장) |
| `HMT500(260313A)/HMT500(260313A)_connector.kicad_sch` | 커넥터, 입력 서지 보호(TVS 2단, CM 초크), 하우징 접지(1 MΩ, 4.7 nF, GDT) |
| `HMT500(260313A)/HMT500(260313A)_power.kicad_sch` | eFuse TPS2660 (RTN은 GND와 분리, OVP 29 V → 전원 12–28 V), 벅 LMR36006BRNXR(5 V, L 15 µH·CFF 20 pF), LDO TPS7A2033(3.3 V) (v0.8) |
| `HMT500(260313A)/HMT500(260313A)_mcu.kicad_sch` | STM32G0B1CCT3 (LQFP48, −40~125 °C), SWD(TC2030), 리셋, 내부 온도센서. SPI1 = ADS1220, SPI2 = DAC(모드 3), SPI3 = PCAP04 (v0.8) |
| `HMT500(260313A)/HMT500(260313A)_measurement.kicad_sch` | J3 센서 하네스 커넥터(JST SH 1.0 4핀), PCAP04(QFN24 실제 핀, DC 없는 플로팅 모드) + 기준 C, ADS1220(Pt1000 2선) |
| `HMT500(260313A)/HMT500(260313A)_analog_out.kicad_sch` | DAC8760 ×2 (SCLK 게이트 U14, AVDD 10 Ω, ALARM wired-OR) + OPA197 +VSENSE 버퍼 + 외부 ISET-R + TPS26611DDFR 오결선 보호 + TVS3301 (v0.8) |
| `HMT500(260313A)/HMT500(260313A)_rs485.kicad_sch` | THVD2450 (±70 V) + 선택 TVS |
| `HMT500(260313A)/HMT500(260313A).kicad_sym`, `sym-lib-table` | 프로젝트 심볼 라이브러리 |
| `HMT500(260313A)/HMT500(260313A)_BOM.csv` | 부품표 (값·풋프린트별 묶음) |
| `HMT500(260313A)/HMT500(260313A)_schematic.pdf` | 회로도 PDF (7쪽) |
| `HMT500(260313A)/HMT500(260313A)_parts_list.xlsx`, `.csv` | **구매용 부품리스트**: 회로도 부품 + 제조사·품번·1k 추정 단가·상태, 분류별 요약(환율 입력 시 원화 자동 계산). `make_parts_list.py`로 생성 |
| `HMT500(260313A)/HMT500(260313A).kicad_pcb` | 보드 외곽(57 × 23, 4층), 고정 구멍 2개, 금지 구역(홀더 홈·지지링 홈), **부품 84개 배치·넷 지정 완료 (배선 전, 승인 대기)**. 설계 규칙: 간격·선폭 0.15, 비아 0.45/0.2, 가장자리 0.3 |
| `HMT500(260313A)/placement.png`, `placement.json` | 배치 그림(윗면/아랫면, 색 = 기능 블록, 숫자 = 부품 높이)과 배치 표(기구 좌표) — 조립 시뮬레이션 입력 |
| `gen_pcb_outline.py` | 외곽·금지 구역 생성기. 치수는 `hardware/mech/hmt500_params.py`에서 읽습니다 |
| `place_pcb.py` | 부품 배치 (pcbnew). 고정 부품 + 큰 부품 자리표 + 작은 부품은 부모 패드 옆 빈 자리 탐색. 보드·금지 구역·하네스 플러그 통로·높이(보어) 조건 검사. `python3 place_pcb.py` |
| `plot_placement.py` | 배치 그림 (matplotlib) |
| `gen_footprints.py`, `lib/HMT500_260313A.pretty` | 프로젝트 풋프린트 (KiCad 7.0.11 복사본 + 자체 3종) |

## 도면 스타일 (v0.2)

- **흐름:** 신호는 왼쪽(입력) → 오른쪽(출력)으로 그리고, 전원은 위쪽 전원 심볼, GND는 아래쪽 GND 심볼로 표시합니다.
- **연결:** 시트 안은 실제 배선이고, 3선 이상 만나는 곳에는 접합점을 찍었습니다. 시트 사이 신호(SPI, 고장 신호, 커넥터 신호 등)만 전역 라벨로 잇습니다.
- **전원 심볼:** GND, +3V3, +3V3A(아날로그 3.3 V), +5V, VIN_P(보호된 입력), CHASSIS
- **구획:** 기능 블록마다 점선 구획, 제목, 설계 메모(설정 공식, 확인 항목)를 넣었습니다.
- **용지:** 커넥터·RS-485 시트는 A4, 나머지는 A3입니다.

## 생성과 검증

회로도는 `gen_hmt500.py`가 생성합니다. 각 부품에 설계 의도 넷(`nets=`)을 적고 배선은 좌표로 그립니다.
- **생성 단계 검사:** 선 중간에 걸친 핀, 연결 안 된 핀, 용지 밖, 표제란 침범이 있으면 생성이 멈춥니다.
- **연결 검사:** `check_netlist.py`가 KiCad 넷리스트와 설계 의도를 핀 단위로 대조합니다. 현재 74넷, 오류 0입니다.
- **자동 테스트:** `tests/test_kicad_gen.py`에 포함되어 있고, kicad-cli가 있으면 넷리스트 대조까지 수행합니다.

```bash
python3 hardware/kicad/gen_hmt500.py                     # 회로도·라이브러리·BOM 생성
kicad-cli sch export netlist -o hmt500.net hardware/kicad/HMT500(260313A)/HMT500(260313A).kicad_sch
python3 hardware/kicad/check_netlist.py hmt500.net       # 넷리스트 = 설계 의도 검사 (현재 74넷, 오류 0)
kicad-cli sch export pdf -o hardware/kicad/HMT500(260313A)/HMT500(260313A)_schematic.pdf hardware/kicad/HMT500(260313A)/HMT500(260313A).kicad_sch
```

KiCad 8 이상에서는 `kicad-cli sch erc`로 ERC도 실행할 수 있습니다(KiCad 7 CLI에는 ERC가 없음).

## 현재 상태와 주의 사항

- **편집 원본:** 스크립트로 다시 생성하면 KiCad에서 손으로 고친 내용이 덮어써집니다. **KiCad에서 편집을 시작하면 그 뒤로는 KiCad 파일을 원본으로 삼으십시오.**
- **핀 번호 확인 필요 (VERIFY=YES):** TPS2660, LMR36006, PCAP04, DAC8760, TPS26611.
  - 이 환경에서 제조사 데이터시트 사이트가 막혀 있어 **핀 번호를 가번호로** 넣었습니다. 핀 이름과 연결(넷)은 설계서대로입니다.
  - 데이터시트를 보고 심볼 핀 번호만 고치면 됩니다.
  - 확인한 부품: STM32G0B1CCT3(LQFP48, KiCad 공식 심볼 STM32G0B1C_B-C-E_Tx 기준), ADS1220(TSSOP-16), THVD2450(SOIC-8), TPS7A2033(SOT-23-5). 이 넷도 데이터시트로 한 번 더 대조하십시오.
- **풋프린트 TBD:** 공통모드 초크, GDT, 벅 인덕터, 가번호 IC 5종. (J3 `Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal`, J1 `Connector_JST:JST_GH_SM08B-GHS-TB_1x08-1MP_P1.25mm_Horizontal`은 KiCad 표준. J5 샤시 스프링 접점 TBD)
- **확인할 회로 사항:**
  - DAC8760 VOUT/IOUT 결합과 DVDD-EN 극성
  - TPS26611 전압 모드 통과 여부
  - TPS2660 분압 기준전압(1.2 V 가정: UVLO 약 9 V, OVP 약 33 V)과 ILIM 저항값
  - LMR36006 FB 기준전압(1.0 V 가정 → 5.0 V)
  - PCAP04 플로팅 측정 결선(PC0–PC1 기준 C, PC2–PC3 센서)
