# 전자부 부품 가격 (BOM 원가) v0.1

조사일: 2026-09-26 · 기준: 블록도 v0.2 (RS-485 + 아날로그 2채널 전압/전류 선택형) · 수량 1,000대 기준 · 기구(하우징, 프로브, 보호캡) 제외

> **가격 출처와 한계**
> - 유통사 사이트(DigiKey, Mouser, LCSC 등)가 이 환경에서 직접 열리지 않았습니다. 그래서 **검색 결과에 노출된 가격**을 썼습니다.
> - 수량 구간(1개 / 1,000개)이 명확하지 않은 값이 섞여 있습니다.
> - **(추정)** 표시 값은 검색 가격이 없어 유사 부품을 기준으로 추정한 것입니다.
> - 실제 원가는 공식 대리점 견적(1k, 5k)으로 확정해야 합니다.
> - 원화는 **1 USD = 1,400원 가정**으로 환산했습니다.

## 1. 부품별 단가 (1대분)

| # | 블록 | 부품 | 수량 | 단가 USD (저가 ~ 정규 유통) | 1대분 USD | 가격 근거 |
|---|---|---|---|---|---|---|
| 1 | MCU | STM32L431RCT6 | 1 | 1.7 ~ 3.1 | 1.7 ~ 3.1 | LCSC $1.71부터, TME $3.13 (160개 이상) |
| 2 | 정전용량 측정 | ScioSense PCAP04-AQFM-24 | 1 | 6.5 ~ 7.1 | 6.5 ~ 7.1 | DigiKey $6.47~7.11 |
| 3 | 온도 측정 | TI ADS1220IPWR | 1 | 1.9 ~ 3.5 | 1.9 ~ 3.5 | LCSC $1.91~1.95, 정규 유통 1k (추정) |
| 4 | **아날로그 출력** | **TI DAC8760IPWP** (기준안) | **2** | 7.8 ~ 12.4 | **15.7 ~ 24.7** | DigiKey/Mouser 1k $12.09~12.37, 1ku $7.84 |
| 4' | (대안) | ADI AD5422BREZ | 2 | 5.8 ~ 19.3 | 11.6 ~ 38.5 | LCSC $5.78, DigiKey $19.25. 편차가 커서 견적 필요 |
| 5 | RS-485 | TI THVD1450DR | 1 | 0.6 ~ 1.2 | 0.6 ~ 1.2 | LCSC $0.58, 정규 유통 (추정) |
| 6 | 전원 | TI LMR36006 + 인덕터 | 1 | 1.1 ~ 1.8 | 1.1 ~ 1.8 | LCSC $1.02 (Q1판), 인덕터 (추정) |
| 7 | 전원 | TI TPS7A2033PDBVR (LDO) | 1 | 0.07 ~ 0.3 | 0.1 ~ 0.3 | LCSC $0.07~0.14 |
| 8 | 보호 | SMBJ33A, SM712, 출력 TVS ×2, PTC ×4, 역극성 FET, CM 초크 | 1식 | – | 0.5 ~ 2.5 | SMBJ33A $0.02~0.07, SM712 $0.02~0.30 (LCSC), 나머지 (추정) |
| 9 | 온도센서 | Pt1000 박막 Class A | 1 | 0.5 ~ 3 | 0.5 ~ 3 | 대량 단가 (추정). 참고로 RS 소량가는 Heraeus $31/개 |
| 10 | 정밀 기준소자 | C0G 기준 커패시터 1%, 정밀 저항 0.01% 5 ppm/K | 1식 | – | 0.6 ~ 2 | (추정) |
| 11 | 수동소자 | 저항, 커패시터 약 80~120개, 크리스털 | 1식 | – | 0.5 ~ 1.5 | (추정) |
| 12 | PCB | 원형 4층 2장 | 1세트 | – | 0.8 ~ 2 | (추정) |
| 13 | 표시 | 상태 LED (옵션) | 1 | – | 0.05 | (추정) |
| | | **전자부 합계 (기준안: DAC8760)** | | | **약 $31 ~ 53** | **약 43,000 ~ 74,000원** |

## 2. 별도 항목

| 항목 | 1대분 | 비고 |
|---|---|---|
| M Connect 8핀 커넥터 | 약 $2 ~ 10 (추정) | 유럽 브랜드 M12 8핀 패널형 $5~10, 중국산 $1.5~3 수준. 사용 중인 M Connect 품번 단가로 대체 필요 |
| IST MK 센서 | 공급가 | 사내 구매 단가로 대체 |
| SMT 조립 | 약 $2 ~ 4 (추정) | 양면 실장, 1k 기준 |
| 절연형 RS-485 옵션 | +$3 ~ 5 (추정) | ISO1410(LCSC 표기 $0.66은 이상치 가능, 정규 유통 수 달러 추정) + 절연 DC/DC |

## 3. 원가 구조 해석

- **아날로그 출력 DAC 2개가 전자부 원가의 약 절반(50%)** 입니다. 그다음은 PCAP04(약 15~20%)입니다.
- 원가 절감안(출력부 비교):

| 출력 방식 | 출력부 원가 (2채널) | 전압/전류 선택 | 비고 |
|---|---|---|---|
| DAC8760 ×2 (기준안) | $15.7 ~ 24.7 | O | 16-bit, 진단·교정 레지스터 내장 |
| AD5422 ×2 | $11.6 ~ 38.5 | O | 단일 핀 결합 앱노트 있음. 견적 편차가 큼 |
| DAC7760 ×2 (12-bit판) | DAC8760보다 저렴 (추정) | O | 가격 확인 필요 |
| MCU 내장 DAC + XTR300 ×2 | 약 $6 ~ 10 (추정) | O | 외장 정밀저항과 교정 부담 증가 |
| MCU 내장 DAC + XTR111 ×2 | 약 $6 ~ 7 (추정) | **X (전류만)** | v0.1 구성 |

- 목표 판매가 약 $500(시장 조사 기준)에 비하면 전자부 원가 $31~53은 **판매가의 약 6~11%** 입니다. 원가를 가장 크게 좌우하는 것은 기구(SUS 가공), 센서, 교정 공수일 가능성이 큽니다.

## 4. 다음 단계

1. 국내 공식 대리점(TI·ADI·ST 대리점, 디바이스마트 등)에 1k/5k 견적을 요청합니다. 대상은 DAC8760, AD5422, PCAP04, ADS1220, STM32L431, M Connect입니다.
2. 출력부 방식을 결정합니다: DAC8760 / AD5422 / XTR300.
3. 회로도 작성 후 전체 BOM(수동소자 포함)을 확정하고 [bom.csv](bom.csv)를 갱신합니다.

## 출처

- AD5422BREZ: https://www.lcsc.com/product-detail/Others_Analog-Devices_AD5422BREZ-REEL_Analog-Devices-ADI-AD5422BREZ-REEL_C192062.html , https://www.digikey.com/en/products/detail/analog-devices-inc/AD5422BREZ/2077063
- DAC8760IPWP: https://octopart.com/dac8760ipwp-texas+instruments-29661991 , https://www.digikey.com/en/products/detail/texas-instruments/DAC8760IPWP/5176207
- PCAP04: https://www.digikey.com/en/products/detail/sciosense/PCAP04-AQFM-24/10324311
- ADS1220IPWR: https://www.lcsc.com/product-detail/C48263.html
- STM32L431RCT6: https://www.lcsc.com/product-detail/ST-Microelectronics_STMicroelectronics_STM32L431RCT6_STM32L431RCT6_C92468.html , https://www.tme.com/us/en-us/details/stm32l431rct6/st-microcontrollers/stmicroelectronics/
- THVD1450DR: https://www.lcsc.com/product-detail/C2671361.html
- LMR36006: https://www.lcsc.com/product-detail/C2869760.html
- TPS7A2033PDBVR: https://www.lcsc.com/product-detail/C2862740.html
- ISO1410BDWR: https://lcsc.com/product-detail/Isolated-RS-485-422-Transceivers_Texas-Instruments-ISO1410BDWR_C2671027.html
- SM712 / SMBJ33A: https://www.lcsc.com/product-detail/C12067.html , https://www.lcsc.com/product-detail/C499719.html
- Pt1000 (Heraeus): https://nz.rs-online.com/web/p/rtd-sensors/4538105
- M12 8핀 패널 커넥터: https://www.binder-usa.com/us-en/products/automation-technology/m12-a/99-3481-458-08-m12-a-male-panel-mount-connector-8-shieldable-thr-ip68-ul-for-pcb-assembly
