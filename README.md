# Oilinwater — 오일 내 수분 트랜스미터

오일(유압유·윤활유·절연유·연료) 속 수분을 온라인으로 측정하는 트랜스미터 개발 프로젝트.

- [결정 기록](docs/decision-log.md) — 확정 사항과 미결 사항 (MCU, DAC 대체 계획 등)
- [조사 보고서](docs/research-report.md) — 측정 원리, 경쟁 제품, 센서 소자, 회로/기구/펌웨어 설계, 교정, 인증, 로드맵
- [시장 조사 종합](docs/market/00-summary.md) — 세계 시장, 경쟁 제품·가격, 국내 시장, 포지셔닝 제안
- [E+E EE364 원문 요약](docs/reference/ee364-summary.md) — 구조 참고 제품의 치수, 사양, 핀맵, Modbus 맵
- [HMT500 기구 설계 Rev C](hardware/mech/README.md) — 제작 도면 PDF(조립도·부품도 4장), 3D STEP, 렌더 (나사 M28×1 + O링 결합, Ø32, 축 방향 PCB 1장)
- [HMT500 기구설계 견적 요청서 (PDF)](docs/mech/HMT500_RFQ.pdf) · [도면 HMT500-M-000](docs/mech/HMT500-M-000.pdf)
- [기구 설계안](docs/mech/mechanical-design.md) — EE364형 일체형 구조도, 압력 격벽, 밀봉, 열, 원가
- [KiCad 회로도 HMT500](hardware/kicad/README.md) — 계층 시트 6장, 심볼 라이브러리, BOM, PDF
- [회로 설계서 (서지·오결선 보호)](docs/hw/circuit-design.md) — 전원 eFuse, 출력 보호, RS-485 ±70 V, 접지, MCU 핀 할당
- [하드웨어 블록 설계](docs/hw/hardware-block-design.md) — 회로 블록도, 부품 선정, 아날로그 2ch + RS-485
- [MCU 선정 검토](docs/hw/mcu-selection.md) — STM32L431 재검토, 후보 비교, 교차 검토 질문지
- [사내 사용 부품 적용 검토](docs/hw/inhouse-parts.md) — MCU·DAC 구매 이력, DAC8760 → DAC7562 + 출력단 비교
- [RS-485 + 부트로더 설계](docs/rs485-bootloader-design.md) — 기본 출력 RS-485 Modbus RTU, 통신으로 펌웨어 업데이트
- [`firmware/`](firmware/) — MCU 비의존 부트로더 코어 + PC 시뮬레이터
- [`tools/fwupdate.py`](tools/fwupdate.py) — 펌웨어 이미지 생성 및 RS-485 업데이트 도구
- [`tools/moisture_calc.py`](tools/moisture_calc.py) — 수분 활동도(aw) ↔ ppm 환산 참조 구현

```bash
python3 tools/moisture_calc.py --temp 20 --aw 0.5     # aw -> ppm
python3 tools/moisture_calc.py --temp 60 --ppm 20     # ppm -> aw
```

```bash
make -C firmware                               # 부트로더 시뮬레이터 빌드
python3 -m unittest discover -s tests          # 통합 테스트
python3 tools/fwupdate.py mkimage app.bin app.oiw --hw-id 1 --version 1.0.0
python3 tools/fwupdate.py flash app.oiw --port /dev/ttyUSB0 --addr 1   # pyserial 필요
```
