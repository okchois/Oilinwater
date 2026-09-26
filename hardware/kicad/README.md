# HMT500 KiCad 회로도 v0.1

DOTECH HMT500 오일 수분 트랜스미터의 KiCad 회로도입니다. 설계 내용은 [회로 설계서](../../docs/hw/circuit-design.md)를 따릅니다.

| 파일 | 내용 |
|---|---|
| `HMT500/HMT500.kicad_pro` | 프로젝트 (KiCad 7 형식 — KiCad 8/9에서 열면 자동 변환) |
| `HMT500/HMT500.kicad_sch` | 최상위 시트 (하위 시트 6장) |
| `HMT500/connector.kicad_sch` | 커넥터, 입력 서지 보호(TVS 2단, CM 초크), 하우징 접지(1 MΩ, 4.7 nF, GDT) |
| `HMT500/power.kicad_sch` | eFuse TPS2660, 벅 LMR36006(5 V), LDO TPS7A2033(3.3 V) |
| `HMT500/mcu.kicad_sch` | STM32L431RC, SWD(TC2030), 상태 LED, 풀업 |
| `HMT500/measurement.kicad_sch` | PCAP04(정전용량) + 기준 C, ADS1220(Pt1000 4선) |
| `HMT500/analog_out.kicad_sch` | DAC8760 ×2 + TPS26611 오결선 보호 + TVS |
| `HMT500/rs485.kicad_sch` | THVD2450 (±70 V) + 선택 TVS |
| `HMT500/HMT500.kicad_sym`, `sym-lib-table` | 프로젝트 심볼 라이브러리 |
| `HMT500/HMT500_BOM.csv` | 부품표 (값·풋프린트별 묶음) |
| `HMT500/HMT500_schematic.pdf` | 회로도 PDF (7쪽) |

## 생성과 검증

회로도는 `gen_hmt500.py`가 생성합니다. 부품·넷을 스크립트에서 고친 뒤 다시 생성할 수 있습니다.

```bash
python3 hardware/kicad/gen_hmt500.py                     # 회로도·라이브러리·BOM 생성
kicad-cli sch export netlist -o hmt500.net hardware/kicad/HMT500/HMT500.kicad_sch
python3 hardware/kicad/check_netlist.py hmt500.net       # 넷리스트 = 설계 의도 검사 (현재 71넷, 오류 0)
kicad-cli sch export pdf -o hardware/kicad/HMT500/HMT500_schematic.pdf hardware/kicad/HMT500/HMT500.kicad_sch
```

KiCad 8 이상에서는 `kicad-cli sch erc`로 ERC도 실행할 수 있습니다(KiCad 7 CLI에는 ERC가 없음).

## 현재 상태와 주의 사항

- **연결 방식:** 모든 연결은 **전역 넷 라벨**로 되어 있습니다(핀마다 짧은 선 + 라벨). 전기적으로는 완결된 회로도이며, 보기 좋게 배치하고 배선하는 일은 KiCad에서 이어서 합니다.
  - 스크립트로 다시 생성하면 KiCad에서 손으로 고친 배치가 덮어써집니다. **KiCad에서 편집을 시작하면 그 뒤로는 KiCad 파일을 원본으로 삼으십시오.**
- **핀 번호 확인 필요 (VERIFY=YES):** TPS2660, LMR36006, PCAP04, DAC8760, TPS26611.
  - 이 환경에서 제조사 데이터시트 사이트가 막혀 있어 **핀 번호를 가번호로** 넣었습니다. 핀 이름과 연결(넷)은 설계서대로입니다.
  - 데이터시트를 보고 심볼 핀 번호만 고치면 됩니다.
  - 확인한 부품: STM32L431RC(LQFP64), ADS1220(TSSOP-16), THVD2450(SOIC-8), TPS7A2033(SOT-23-5). 이 넷도 데이터시트로 한 번 더 대조하십시오.
- **풋프린트 TBD:** M Connect 8핀, 공통모드 초크, GDT, 피드스루, 벅 인덕터, 가번호 IC 5종.
- **확인할 회로 사항:**
  - DAC8760 VOUT/IOUT 결합과 DVDD-EN 극성
  - TPS26611 전압 모드 통과 여부
  - TPS2660 분압 기준전압(1.2 V 가정: UVLO 약 9 V, OVP 약 33 V)과 ILIM 저항값
  - LMR36006 FB 기준전압(1.0 V 가정 → 5.0 V)
  - PCAP04 플로팅 측정 결선(PC0–PC1 기준 C, PC2–PC3 센서)
