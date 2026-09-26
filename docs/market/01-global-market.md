# 세계 시장 규모와 동향 — 온라인 오일 상태 모니터링 / 오일 내 수분 센서

조사일: 2026-09-26

> **주의:** 시장 수치는 모두 조사기관의 공개 요약, 보도자료, 검색 스니펫에서 가져온 것이며 유료 원문으로 검증하지 않았습니다. 기관마다 시장 범위(분석 서비스 포함 여부, 하드웨어만 집계하는지 등)가 달라 편차가 큽니다.

## 1. 시장 규모와 CAGR

### 1.1 오일 상태 모니터링(OCM) 전체

| 기관 (발표) | 기준값 | 전망값 | CAGR |
|---|---|---|---|
| MarketsandMarkets (2025) | 2025년 12.7억 달러 | 2030년 17.8억 달러 | 7.0% |
| Research&Markets (2025) | 2025년 26.1억 달러 | 2030년 35.1억 달러 | 5.9% |
| Knowledge Sourcing (2025) | 2025년 19.76억 달러 | 2030년 28.07억 달러 | 7.27% |
| Mordor Intelligence (2026) | 2026년 19.9억 달러 | 2031년 26.4억 달러 | 5.78% |
| Precedence Research | 2025년 14.6억 달러 | 2034년 27.1억 달러 | 7.12% |
| GM Insights | 2025년 15억 달러 | 2035년 34억 달러 | 8.8% |

- 2025년 기준 약 13억~26억 달러, CAGR 약 6~9%가 합의 범위입니다.
- 하드웨어(센서·분석기) 비중이 가장 크고(한 요약은 약 60%, 출처 불명확), 소프트웨어·서비스가 가장 빠르게 성장합니다.
- 북미가 최대 시장이고, 아시아태평양이 가장 빠르게 성장합니다(GM Insights).

### 1.2 오일 품질 센서 / 수분 센서 (신뢰도 낮음)

| 자료 | 수치 | 비고 |
|---|---|---|
| Marketintelo, Dataintelo (오일 품질 센서) | 2024년 12억 달러 → 2033년 25억~28.5억 달러, CAGR 8.7~10.2% | 자동차 엔진오일 센서 포함 가능성 높음 |
| IndexBox (오일 품질 센서) | 2026~2035년 CAGR 7.2% | |
| Dataintelo (오일 수분 센서) | 2023년 18억 달러 → 2032년 32억 달러, CAGR 6.5% | 과대 추정 가능성 |
| Verified Market Reports (소형 오일 수분 센서) | 2024년 2.48억 달러 → 2033년 3.5억 달러, CAGR 4.5% | **산업용 수분 트랜스미터로는 이 수준(수억 달러)이 현실적(추정)** |
| openPR (OWD 수분계) | 2025년 1.07억 달러 → 2035년 2.78억 달러, CAGR 10% | 보도자료 |

### 1.3 변압기 모니터링

| 기관 | 수치 | CAGR |
|---|---|---|
| MarketsandMarkets (2026) | 2026년 31.1억 달러 → 2031년 49.8억 달러 | 9.9% |
| 360iResearch | 2025년 30.3억 달러 → 2032년 58.6억 달러 | 9.86% |
| DataHorizzon | 2024년 21억 달러 → 2033년 42억 달러 | 8.1% |
| Global Growth Insights | 2026년 32.5억 달러 → 2035년 70.3억 달러 | 8.94% |

## 2. 수요 동인과 트렌드

- **예지보전 / Industry 4.0:** 모든 보고서가 첫 번째 동인으로 꼽습니다. 정기 오일 교환이 상태 기반 교환으로 바뀌는 흐름입니다.
- **변압기 수요와 디지털화:**
  - AI와 데이터센터 부하로 변압기 수요가 급증했습니다. Wood Mackenzie는 2025년 미국 전력용 변압기 공급 부족을 약 30%로 추정합니다.
  - 새로 구하기 어려우니 기존 변압기의 수명을 늘려야 하고, 그래서 DGA(유중가스)와 수분을 함께 보는 모니터 수요가 커집니다(예: Vaisala MHT410).
  - 신규 변압기에 모니터를 공장에서 미리 장착하는 사례도 늘고 있습니다.
- **에스테르 절연유:**
  - 20°C 포화 수분량이 천연 에스테르 약 1,100 ppm, 합성 에스테르 약 2,200~2,700 ppm으로 광유(약 50~55 ppm)보다 훨씬 높습니다.
  - 그래서 ppm 값만으로는 판정할 수 없고, %RS(aw)를 직접 재는 정전용량식 센서가 구조적으로 유리합니다.
- **풍력 기어박스 상태감시(CMS):** 입자 센서와 수분 센서가 표준 구성이 되고 있습니다. 인증 기준은 DNV-SE-0439이고, 해상풍력은 현장 접근 비용이 커서 연속 모니터링 도입이 빨라지고 있습니다.
- **유압(산업·모바일):** OCM에서 가장 빠르게 크는 용도로 평가됩니다(Polaris, 한 요약은 CAGR 8.72%). 장비 제조사가 소형 센서를 기본 탑재하는 사례가 늘고 있습니다.
- **IO-Link 확산:** ifm LDH, Bühler BCM-W, HYDAC가 IO-Link 수분 센서를 내놓고 있습니다. 유압 파워유닛과 공작기계에서는 사실상 기본 인터페이스가 되어 가는 추세입니다(정성적 판단).
- **선박:**
  - 미국 VGP/VIDA 규정으로 선미관(stern tube)에 친환경 윤활유(에스테르 등)를 써야 합니다.
  - 이 윤활유는 가수분해에 약하고 물을 많이 흡수해 수분 모니터링 수요가 생깁니다. 다만 센서 설치를 의무로 정한 규정은 확인하지 못했습니다.
  - 제품 예: Rivertrace SMART WiO.
- **무선 / IIoT:** 수분 센서에 특화된 무선 제품은 드물어 아직 초기 단계로 봅니다. **선점 기회가 있는 영역**입니다.

## 3. 응용 부문, 구매자, 채널

**성장 순위 (정성적 종합, 불확실)**

1. 변압기(전력회사, 데이터센터, 재생에너지 연계): 모니터링 시장 CAGR 약 9~10%
2. 유압(산업·모바일)
3. 풍력 기어박스
4. 선박, 터빈·압축기(성숙 시장)

**구매자와 판매 채널**

| 구매자 | 특징 |
|---|---|
| 장비 제조사(OEM): 유압 파워유닛, 공작기계, 풍력, 변압기 | 대량 구매. 가격에 민감하고 인터페이스(IO-Link, CAN/J1939, 4–20 mA, Modbus)를 중시 |
| 필터·유체 관리 업체: HYDAC, Parker, Pall, Bühler, CJC | 오프라인 필터와 탈수 장비에 센서를 묶어 판매하는 핵심 채널 |
| 최종사용자: 전력회사, 발전사, 제철·제지, 선주 | 기존 설비 개조용 구매. 변압기는 입찰이나 모니터링 시스템 통합사를 거쳐 구매 |

## 4. 알람 기준 (고객이 쓰는 한계값)

- **유압·윤활유:**
  - 권고: 포화도 50% 미만 또는 300 ppm 미만. 서보 밸브와 고압 시스템은 200 ppm 미만, 장비 제조사 다수는 100 ppm 미만을 요구합니다(업계 자료).
  - 제조사 기본 알람 예: HYDAC AS1000 경고 60%RS·알람 80%RS, Rivertrace 사전 알람 0.5 aw·주 알람 0.9 aw.
  - 광유계 유압유의 20°C 포화 수분량은 약 200~300 ppm입니다.
- **터빈유 (ASTM D4378):** 경고 200 ppm이고, 보수적인 사용자는 100 ppm을 씁니다.
- **IEEE C57.106 (운전 중 광유):** 69 kV 이하 35 ppm, 69~230 kV 25 ppm, 230 kV 초과 20 ppm입니다.
- **IEC 60422:** 전압 등급별로 양호/보통/불량 한계가 따로 있습니다. 구체적인 수치는 **원문 확인 전이라 싣지 않았습니다.**
- **천연 에스테르유:** IEC 62975를 적용하며 %RS 기반으로 판정하는 경향이 있습니다.

→ **제품 반영:** 알람 기본값은 60/80%RS로 하고, 용도별 프리셋(유압, 터빈, 변압기-광유, 변압기-에스테르)을 두는 것을 권장합니다.

## 5. 기술 트렌드

- **복합 센서:** 수분(%RS)에 유전율, 전도도, 점도·밀도, 입자를 더하는 방향입니다(예: HYDACLab, TE OPS3, 중국 저가 복합 센서).
- **정전용량 박막 센서:** 사실상 업계 표준이고, 소형화 덕분에 장비 제조사 기본 탑재가 늘고 있습니다.
- **AI 예지:** 오일 잔존수명(RUL) 예측 연구가 활발합니다. 상용 제품은 아직 추세 감시와 이상 탐지 수준입니다.
- **디지털 인터페이스:** IO-Link, Modbus RTU/TCP, CANopen/J1939로 옮겨 가고 있습니다.

## 출처

- https://www.marketsandmarkets.com/Market-Reports/oil-condition-monitoring-market-62105661.html
- https://www.researchandmarkets.com/reports/5532694/oil-condition-monitoring-market-global
- https://www.knowledge-sourcing.com/report/oil-conditioning-monitoring-market
- https://www.mordorintelligence.com/industry-reports/oil-condition-monitoring-market
- https://www.precedenceresearch.com/oil-condition-monitoring-market
- https://www.gminsights.com/industry-analysis/oil-condition-monitoring-market
- https://www.polarismarketresearch.com/industry-analysis/oil-condition-monitoring-market
- https://marketintelo.com/report/oil-quality-sensor-market
- https://dataintelo.com/report/global-oil-moisture-sensor-market
- https://www.verifiedmarketreports.com/product/compact-moisture-in-oil-sensor-market/
- https://www.marketsandmarkets.com/PressReleases/transformer-monitoring-system.asp
- https://www.360iresearch.com/library/intelligence/transformer-monitoring-system
- https://transformers-magazine.com/tm-news/us-faces-30-transformer-shortfall-in-2025/
- https://www.vaisala.com/en/products/instruments-sensors-and-other-measurement-devices/instruments-industrial-measurements/mht410
- https://www.mdpi.com/1996-1073/13/23/6429
- https://www.dnv.com/energy/standards-guidelines/dnv-se-0439-certification-of-condition-monitoring/
- https://www.machinerylubrication.com/Read/32286/monitoring-wind-turbine-gear-oils-with-online-sensors
- https://www.lubesngreases.com/magazine/23_6/meeting-stern-regulations/
- https://rivertrace.com/products/smart-wio-sensor/
- https://www.hydac.com/en-us/hydraulics-goes-io-link/
- https://www.ifm.com/us/en/us/learn-more/analytical/oil-humidity-sensor/ldh-oil-humidity-sensor
- https://www.buehler-technologies.com/en/fluidcontrol/oil-condition-sensors/oil-moisture-sensor-bcm-w
- https://www.machinerylubrication.com/Read/30440/water-in-oil
- https://ieeexplore.ieee.org/document/1049145
