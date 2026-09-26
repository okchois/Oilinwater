# 경쟁 제품·가격 조사 — 정전용량식 오일 내 수분 트랜스미터 (aw/%RS)

조사일: 2026-09-26

> **조사 방법과 한계:** 웹 검색 스니펫과 판매점 데이터시트 목록을 기반으로 했습니다. 제조사·판매점 사이트 상당수가 이 환경의 프록시에 막혀 원문을 직접 열지 못했습니다. **(미검증)** 표시 값과 가격은 반드시 다시 확인해야 합니다. 확인되지 않은 값은 n/a로 두었습니다.

## 1. 비교표

| 제조사/모델 | 측정량 | aw/%RS 정확도 | 오일 온도 | 압력 | 공정 연결 | 출력/인터페이스 | 전원 | 커넥터/IP | 용도 | 가격 |
|---|---|---|---|---|---|---|---|---|---|---|
| Vaisala MMT162 (단종 공지) | aw, T, ppm(변압기유) | ±0.02 (0–0.9), ±0.03 (0.9–1) | −40~80 °C | 200 bar | n/a | RS-485 비절연 Modbus RTU + 아날로그 2ch | 14–28 VDC(RS-485), 22–28 V(전류 출력) | M8 4핀, IP66 | OEM, 유압/윤활/변압기 | 약 €1,205 (미검증) |
| **Vaisala MMT143** (EE364와 가장 비슷한 형태, MMT162 후속으로 추정) | aw, %RS, T | ±2 %RS (0–90), ±3 %RS (90–100) | n/a | 200 bar(옵션, 미검증) | n/a | RS-485 Modbus RTU + 4–20 mA | n/a | n/a | OEM 소형, HUMICAP 180L2 | n/a |
| Vaisala Indigo MMP8 | aw, %RS, T, ppm | ±0.01 aw (±1 %RS) | 최대 180 °C | 0–40 bar abs | 프로브 262/448 mm | 단독 Modbus RTU / Indigo520 연결 시 아날로그 4ch + 릴레이 | n/a | n/a | 변압기, 고급 공정 | 약 $3,581 (미검증) |
| Vaisala MHT410 | 수분 + H₂ 0–5000 ppm + T | n/a | n/a | n/a | 변압기 밸브 | 아날로그 3ch, Modbus RTU, DNP3.0 | n/a | n/a | 변압기 | n/a |
| **E+E EE364** (구조 참고 제품, **원문 확인**) | aw, T, ppm | ±0.02 (0–0.9), ±0.03 (0.9–1), T ±0.2 °C | −40~80 °C (옵션 100 °C) | 20 bar | G½ ISO / ½" NPT | 4–20 mA 2ch(3선) + Modbus RTU | 10–28 VDC | **M12 8핀, IP65, 316L** | OEM, 유압/윤활/변압기/디젤 | 특정 구성 약 $1,762 (미검증) |
| E+E EE381 | aw, T, ppm | n/a | ≤120 °C | 20 bar (옵션 100) | G½ / ½" NPT | 아날로그 2ch(V/mA), 스위치, LCD 옵션 | n/a | 금속 하우징 | 산업 범용 | 약 $4,147부터 (미검증) |
| E+E EE360 | aw, T, ppm | n/a | ≤180 °C | 20 bar | n/a | 아날로그 2ch + RS-485 Modbus RTU 또는 Modbus TCP, TFT 디스플레이 | n/a | n/a | 고급형 | n/a |
| HYDAC AS1000 | 포화도 %, T | ≤±2 % FS | −25~100 °C | −0.5~50 bar | G3/8 (미검증) | 4–20 mA 2ch + 스위치 | n/a | M12 5핀, IP67 | 유압, 모바일 OEM | 약 $1,250 (eBay) |
| HYDAC AS3000 | 포화도 %, T | n/a | n/a | n/a | n/a | 4–20 mA/0–10 V, 스위치 2ch, 디스플레이, **IO-Link 버전** | n/a | n/a | 유압 | n/a |
| Pall WS10 | %Sat, T | ±2 % (0–90), ±3 % (90–100) | −40~125 °C | 20 bar (HP형 100 bar) | ½" NPT/BSPP | 4–20 mA 2ch | 21–28 VDC | M12 | 유압/윤활/절연유 | n/a |
| Parker Kittiwake | %RH, T | n/a | n/a | n/a | ½" BSP | 4–20 mA | n/a | n/a | 선박 | n/a |
| Argo-Hytos LubCos H2O+ II | %RH, aw, T, 유전율, 전도도 | n/a | n/a | n/a | n/a | RS232, CANopen, 4–20 mA 2ch | n/a | n/a | 윤활, 기어 | n/a |
| MP Filtri ICM-W | %Sat, T (+입자) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 오염 모니터 부가 기능 | n/a |
| Des-Case CMS | %RH, T (+입자) | ±3 %RH | n/a | n/a | n/a | RS-485 Modbus, CAN | n/a | n/a | 윤활 | n/a |
| ifm LDH100 | %RH, T | ±3 % FS | −20~120 °C | 50 bar | G¾ | 4–20 mA 2ch, **IO-Link 모델** | 9–33 VDC | M12 8핀, IP67 | 공장자동화, 유압 | **약 $732부터** |
| Bühler BCM-W | %RH, T | n/a | n/a | 50 bar | n/a | 4–20 mA, 스위치, **IO-Link**, 디스플레이 | n/a | n/a | 유압 탱크 | n/a |
| Kobold AFO | aw, T, ppm | ±0.02 (0–0.9) / ±0.03 | ≤125 °C | 300 bar | G½ 추정 | 4–20 mA 2ch + RS-485 Modbus RTU | 10–36 VDC | M12 8핀 A-code, IP66 | 범용 | n/a |
| CS Instruments FO 510 | aw, T, ppm | ±0.02/±0.03 | 0–100 °C | 300 bar | G½ / ½" NPT | 4–20 mA 2ch + Modbus RTU | n/a | IP66 | 범용 | n/a |
| Kongter KT-200/300 (중국) | aw, T, ppm | ppm ±10 % 또는 ±10 ppm | −40~120 °C | n/a | n/a | RS-485 Modbus, 4–20 mA | n/a | n/a | 변압기/윤활 | n/a |
| Shandong Fengtu (중국) | aw, T, ppm | ±0.02 (0–0.6) ~ ±0.04 (0.9–1) | −40~120 °C | n/a | n/a | RS-485 Modbus RTU, 4–20 mA 옵션 | n/a | n/a | 윤활 | n/a |
| 기타 중국 업체 (Sikoflow 등) | aw, ppm | n/a | n/a | n/a | n/a | RS-485 | n/a | n/a | 범용 | FOB $60–84부터 (미검증, 동급 아닐 수 있음) |

**변압기용 복합 모니터 (수분은 부가 기능):** GE Vernova Hydran M2-X, Qualitrol QHS393, Megger/Weidmann InsuLogix, Camlin TOTUS G9, Morgan Schaffer Calisto(Doble). 모두 시스템 단위로 팔리는 고가 제품이며 가격은 공개되지 않았습니다.

**해당 제품이 없거나 다른 시장인 곳**
- Omega, Setra: 오일 수분 전용 제품 없음
- Rotronic: 식품용 aw 제품만 있음
- Michell: 세라믹 센서 기반 ppmW 분석기로 다른 시장
- Gill Sensors: CAN 기반 오일 상태 센서만 있음
- Bosch Rexroth: HYDAC 제품 재판매
- 한국 업체: tradekorea에 "Oil Moisture Transmitter" 등록이 1건 있으나 페이지가 차단되어 제조사를 확인하지 못했습니다. 이 외에 국산 전용 제품은 찾지 못했습니다.

## 2. 가격대

| 가격대 | 제품 | 특징 |
|---|---|---|
| 저가 (<$300) | 중국 업체 (Kongter, Fengtu, Sikoflow 등) | RS-485 Modbus와 aw/ppm 제공. 교정 추적성과 인증이 불명확 |
| **중가 ($700–1,800)** | ifm LDH100 (~$732), HYDAC AS1000 (~$1,250), Vaisala MMT162 (~€1,205), E+E EE364 (~$1,760) | OEM·유압 시장의 주류. **우리 제품이 직접 겨냥할 구간** |
| 고가 ($3,500+) | Vaisala MMP8 + Indigo520, E+E EE381, EE360, 변압기 복합 모니터 | 변압기, 고급 공정 |

## 3. 신규 진입자를 위한 시사점

1. **"aw + ppm + Modbus + M12 + G½"를 모두 갖춘 제품이 적습니다.** 이 조합은 EE364, Kobold AFO, CS FO 510 정도입니다(뒤의 둘은 같은 OEM 제품으로 추정). HYDAC, Pall, ifm, Bühler는 %RS 아날로그 출력 중심이고 ppm이나 Modbus가 없습니다. → 우리 기본 구성(RS-485 Modbus + aw/ppm)이 이 틈에 맞습니다.
2. **IO-Link는 뚜렷한 빈자리입니다.** 현재 IO-Link 제품(ifm, HYDAC AS3000, Bühler)은 모두 %RH만 측정하고 정확도가 ±2~3 % FS입니다. ±0.02 aw 정확도에 ppm까지 주는 IO-Link 제품은 확인되지 않았습니다. → RS-485 기본 모델 다음 파생 모델로 IO-Link를 권장합니다.
3. **CAN/J1939는 모바일 유압(건설기계)의 빈자리입니다.** CAN 지원 제품은 Argo-Hytos(CANopen)와 Des-Case 정도입니다.
4. **$400–800 가격대가 비어 있습니다.** 유럽 브랜드는 $1,200 이상이고, 중국 제품은 신뢰성과 교정 문서가 불투명합니다. **교정 성적서가 포함된 ±0.02 aw 제품을 $500 전후**로 내놓으면 이 사이를 공략할 수 있습니다. 소형 OEM 제품인 Vaisala MMT162의 단종 공지로 대체 수요도 생깁니다.
5. **압력·온도 기준선:** EE364의 20 bar/80 °C는 약한 편입니다. 경쟁 수준은 50 bar(HYDAC, ifm), 200 bar(Vaisala), 300 bar(AFO, FO 510)이고 온도는 120 °C 이상입니다. → 유압 시장에 들어가려면 **최소 50 bar, 목표 200 bar, 120 °C**가 필요합니다.
6. **센서 공급사와 경쟁할 위험이 있습니다.** IST AG도 자체 "moisture in oil probe" 모듈을 팔고 있어, MK 센서를 쓰는 다른 경쟁사가 나올 수 있습니다. 차별화는 센서 칩이 아니라 **오일별 포화곡선 DB(ppm 환산), 교정 추적성, 진단 기능, 펌웨어**에서 만들어야 합니다.
7. **변압기 시장:** 대형 DGA 모니터는 수분을 부가 기능으로 넣습니다. 중소형·배전 변압기용 저가 aw/ppm 센서(Modbus/DNP3) 구간은 비어 있고, 이 구간에는 Vaisala MHT410과 Qualitrol QHS393 정도만 있습니다. 광유와 에스테르의 ppm 환산 계수 지원은 필수입니다.
8. **교체 호환성:**
   - 스위치 출력(60/80 % 기본값), 상태 LED, 선택형 디스플레이 같은 부가 기능이 있습니다.
   - **EE364 호환 모드**로 기존 제품을 그대로 대체할 수 있게 하면 유리합니다. EE364와 같은 M12 8핀 핀맵과 같은 Modbus 레지스터 맵을 쓰는 방식입니다.
   - EE364 레지스터 번호(aw=52, ppm=54, T=26, 1부터 셈)는 Quick Guide 원문으로 확인했습니다. FLOAT32는 CDAB 워드 순서입니다([요약](../reference/ee364-summary.md)).

## 출처

- https://www.vaisala.com/en/products/instruments-sensors-and-other-measurement-devices/instruments-industrial-measurements/mmt162
- https://www.enr.com/ext/resources/custom-content/Infocenter/2017/Vaisala/CEN-G-MMT162-Datasheet-B210755EN-1.pdf
- https://www.vaisala.com/en/products/mmt143-moisture-and-temperature-transmitter-oil
- https://www.vaisala.com/en/products/instruments-sensors-and-other-measurement-devices/instruments-industrial-measurements/mmp8
- https://www.instrumentation2000.com/vaisala-mmp8-probe.html
- https://www.vaisala.com/en/products/instruments-sensors-and-other-measurement-devices/instruments-industrial-measurements/mht410
- https://www.epluse.com/products/moisture-in-oil-instrumentation/oil-measurement-transmitter/ee364/
- https://www.instrumart.com/assets/datasheet_EE364.pdf
- https://www.instrumart.com/configuration/42983
- https://www.epluse.com/products/moisture-in-oil-instrumentation/oil-measurement-transmitter/ee381/
- https://sensorpros.com/products/ee381-compact-moisture-in-oil-transmitter
- https://www.epluse.com/products/moisture-in-oil-instrumentation/oil-measurement-transmitter/ee360/
- https://www.hydac.com.au/aqua-sensor-as-1000.html
- https://www.ebay.de/itm/205020368934
- https://www.hydac.com/media/local_resources_usa/downloads/catalog/electronics/pdfs/as-3000-aquasensor-with-display-io-link.pdf
- https://www.pall.com/content/dam/pall/power-&-utilities/literature-library/non-gated/IMWS10EN.pdf
- https://www.insatechmarine.com/products/condition-monitoring/lube-oil/moisture-sensor/
- https://www.argo-hytos.com/products/sensors-measurement/lubrication-condition-sensors/lubcos-h2o-ii.html
- https://www.pe-energy.com/product/des-case-cmswm0rg1-2-contamination-monitoring-sensor/
- https://www.ifm.com/us/en/product/LDH100
- https://www.buehler-technologies.com/en/fluidcontrol/oil-condition-sensors/oil-moisture-sensor-bcm-w
- https://www.kobold.com/Industrial-Oil-Moisture-Sensor-AFO
- https://www.cs-instruments.com/FO-510-Industrial-oil-moisture-sensor/
- https://kongter.com/products/kt-200-moisture-in-oil-transmitter/
- https://www.fengtutec.com/technical/1920.html
- https://www.made-in-china.com/products-search/hot-china-products/Oil_Moisture_Sensor.html
- https://www.tradekorea.com/product/detail/P271458/Oil-Moisture-Transmitter---Water-in-Oil-Switch-Detector--.html
- https://www.ist-ag.com/en/products/rht-sensor-module-moisture-oil-monitoring
- https://www.gevernova.com/grid-solutions/automation/transformer-monitoring/hydran-m2-x
- https://www.qualitrolcorp.com/products/OM-Sensor
- https://www.megger.com/en-us/products/insulogixr-g2-acetylene-hydrogen-and-moisture-monitor
- https://camlingroup.com/product/totus-transformer-monitor/
