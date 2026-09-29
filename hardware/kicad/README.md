# HMT500 KiCad 회로도 v0.2

DOTECH HMT500 오일 수분 트랜스미터의 KiCad 회로도입니다. 설계 내용은 [회로 설계서](../../docs/hw/circuit-design.md)를 따릅니다.

| 파일 | 내용 |
|---|---|
| `HMT500/HMT500.kicad_pro` | 프로젝트 (KiCad 7 형식 — KiCad 8/9에서 열면 자동 변환) |
| `HMT500/HMT500.kicad_sch` | 최상위 시트 (하위 시트 6장) |
| `HMT500/connector.kicad_sch` | 커넥터, 입력 서지 보호(TVS 2단, CM 초크), 하우징 접지(1 MΩ, 4.7 nF, GDT) |
| `HMT500/power.kicad_sch` | eFuse TPS2660, 벅 LMR36006(5 V), LDO TPS7A2033(3.3 V) |
| `HMT500/mcu.kicad_sch` | STM32G0B1CCT3 (LQFP48, −40~125 °C), SWD(TC2030), 상태 LED, 풀업 |
| `HMT500/measurement.kicad_sch` | J3 센서 하네스 커넥터(JST SH 1.0 4핀), PCAP04(정전용량) + 기준 C, ADS1220(Pt1000 2선) |
| `HMT500/analog_out.kicad_sch` | DAC8760 ×2 + TPS26611 오결선 보호 + TVS |
| `HMT500/rs485.kicad_sch` | THVD2450 (±70 V) + 선택 TVS |
| `HMT500/HMT500.kicad_sym`, `sym-lib-table` | 프로젝트 심볼 라이브러리 |
| `HMT500/HMT500_BOM.csv` | 부품표 (값·풋프린트별 묶음) |
| `HMT500/HMT500_schematic.pdf` | 회로도 PDF (7쪽) |
| `HMT500/HMT500_parts_list.xlsx`, `.csv` | **구매용 부품리스트**: 회로도 부품 + 제조사·품번·1k 추정 단가·상태, 분류별 요약(환율 입력 시 원화 자동 계산). `make_parts_list.py`로 생성 |
| `HMT500/HMT500.kicad_pcb` | 보드 외곽(57 × 23, 기구 Rev C), 고정 구멍 2개, 금지 구역(홀더 홈·지지링 홈), 배치 구역·부품 높이 한계 표기. 부품 배치·배선 전 |
| `gen_pcb_outline.py` | 위 보드 파일 생성기. 치수는 `hardware/mech/hmt500_params.py`에서 읽습니다 |

## 도면 스타일 (v0.2)

- **흐름:** 신호는 왼쪽(입력) → 오른쪽(출력)으로 그리고, 전원은 위쪽 전원 심볼, GND는 아래쪽 GND 심볼로 표시합니다.
- **연결:** 시트 안은 실제 배선이고, 3선 이상 만나는 곳에는 접합점을 찍었습니다. 시트 사이 신호(SPI, 고장 신호, 커넥터 신호 등)만 전역 라벨로 잇습니다.
- **전원 심볼:** GND, +3V3, +3V3A(아날로그 3.3 V), +5V, VIN_P(보호된 입력), VDDA, CHASSIS
- **구획:** 기능 블록마다 점선 구획, 제목, 설계 메모(설정 공식, 확인 항목)를 넣었습니다.
- **용지:** 커넥터·RS-485 시트는 A4, 나머지는 A3입니다.

## 생성과 검증

회로도는 `gen_hmt500.py`가 생성합니다. 각 부품에 설계 의도 넷(`nets=`)을 적고 배선은 좌표로 그립니다.
- **생성 단계 검사:** 선 중간에 걸친 핀, 연결 안 된 핀, 용지 밖, 표제란 침범이 있으면 생성이 멈춥니다.
- **연결 검사:** `check_netlist.py`가 KiCad 넷리스트와 설계 의도를 핀 단위로 대조합니다. 현재 71넷, 오류 0입니다.
- **자동 테스트:** `tests/test_kicad_gen.py`에 포함되어 있고, kicad-cli가 있으면 넷리스트 대조까지 수행합니다.

```bash
python3 hardware/kicad/gen_hmt500.py                     # 회로도·라이브러리·BOM 생성
kicad-cli sch export netlist -o hmt500.net hardware/kicad/HMT500/HMT500.kicad_sch
python3 hardware/kicad/check_netlist.py hmt500.net       # 넷리스트 = 설계 의도 검사 (현재 71넷, 오류 0)
kicad-cli sch export pdf -o hardware/kicad/HMT500/HMT500_schematic.pdf hardware/kicad/HMT500/HMT500.kicad_sch
```

KiCad 8 이상에서는 `kicad-cli sch erc`로 ERC도 실행할 수 있습니다(KiCad 7 CLI에는 ERC가 없음).

## 현재 상태와 주의 사항

- **편집 원본:** 스크립트로 다시 생성하면 KiCad에서 손으로 고친 내용이 덮어써집니다. **KiCad에서 편집을 시작하면 그 뒤로는 KiCad 파일을 원본으로 삼으십시오.**
- **핀 번호 확인 필요 (VERIFY=YES):** TPS2660, LMR36006, PCAP04, DAC8760, TPS26611.
  - 이 환경에서 제조사 데이터시트 사이트가 막혀 있어 **핀 번호를 가번호로** 넣었습니다. 핀 이름과 연결(넷)은 설계서대로입니다.
  - 데이터시트를 보고 심볼 핀 번호만 고치면 됩니다.
  - 확인한 부품: STM32G0B1CCT3(LQFP48, KiCad 공식 심볼 STM32G0B1C_B-C-E_Tx 기준), ADS1220(TSSOP-16), THVD2450(SOIC-8), TPS7A2033(SOT-23-5). 이 넷도 데이터시트로 한 번 더 대조하십시오.
- **풋프린트 TBD:** 공통모드 초크, GDT, 벅 인덕터, 가번호 IC 5종. (J3 `Connector_JST:JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical`, J1 `Connector_JST:JST_GH_SM08B-GHS-TB_1x08-1MP_P1.25mm_Horizontal`은 KiCad 표준. J5 샤시 스프링 접점 TBD)
- **확인할 회로 사항:**
  - DAC8760 VOUT/IOUT 결합과 DVDD-EN 극성
  - TPS26611 전압 모드 통과 여부
  - TPS2660 분압 기준전압(1.2 V 가정: UVLO 약 9 V, OVP 약 33 V)과 ILIM 저항값
  - LMR36006 FB 기준전압(1.0 V 가정 → 5.0 V)
  - PCAP04 플로팅 측정 결선(PC0–PC1 기준 C, PC2–PC3 센서)
