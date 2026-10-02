# HMT500 LCSC–BOM 매칭 (2026-10-03)

실장 BOM **61행 / 108개 / LCSC 59종** 모두 번호를 기입하고 공식 LCSC 카탈로그의 제조사 품번·값·패키지와 대조했다. 하네스 하우징/단자 4종도 별도 시트에 포함했다. 회로 v0.10 / PCB A5-R1 / 기구 Rev I 기준이다.

## 바뀐 것

| 대상 | 반영 |
|---|---|
| C4 | 기존 C1532는 FH 0402B223K500NT로 삼성 품번과 불일치. 삼성 CL05B223KO5NNNC에 맞는 **C318579**로 정정. 22nF 16V X7R 0402. |
| C61 | 기존 CL21B225KBFNNNE의 등록을 찾지 못해, 기결정 #33/#38/#39의 같은 사양 대체 원칙으로 YAGEO **CC0805KKX7R9BB225 / C125847** 채택. 2.2µF 50V X7R ±10% 0805. 제조사 최대 높이 1.45 mm를 배치 검사에 반영(현재 위치 허용 높이 3.58 mm). |
| R9/R52 | UNI-ROYAL **0402WGF2212TCE / C43473**. 22.1kΩ ±1% 0402, 50V, 62.5mW. |
| C22 | 기존 결정 #34로 이미 선정된 Vishay C3898227의 실제 공차 **±2%**로 회로도/BOM 표시 정정. |
| R19 | 기존 결정 #38로 이미 선정된 Panasonic C491130의 **±0.1%·25ppm**으로 회로도/BOM 표시 정정. |
| 구매 목록 | PCB 6층/Rev I와 현재 하네스 40±2mm 설계값을 반영. 하네스 절단/완성 길이는 미확정으로 표시. |

Panasonic C491130/C473244는 LCSC에서 ERA3AEB4021V/ERA3AEB153V로 하이픈 없이 표시한다. PCAP04는 LCSC 제조사 표기가 ams이고 현재 BOM은 ScioSense다. 제조 라벨/로트는 구매 시 확인한다.

## 검증

- 생성기에서 수정 후 전체 재생성: 작도·넷리스트 81/81 일치, DRC 오류 0, 미연결 0, 테스트 33개 통과.
- 기존 C44/D1 풋프린트 라이브러리 경고 2개는 유지.
- 배선/비아 형상, 부품 위치·면·회전·풋프린트 동일 대조.
- BOM/CPL 참조번호 집합 108개 일치, 중복/누락 없음. XLSX 재열기 확인.
- 카탈로그 사실과 링크는 `manufacturing/jlc/bom_match_20261003/catalog_evidence.json` 및 엑셀에 저장. 모든 부품 데이터시트를 새로 검증한 결과는 아니다.

## 남은 위험 / 결정할 것

- **C61의 28V DC 바이어스 실효 용량** 및 입력 리플 적합성은 확인 필요. 명목값과 온도특성만으로 실효 용량을 보증하지 않는다.
- LCSC 등록과 JLC 실장 가능/재고 확보는 별개. 특히 C4와 TVS1401의 JLC 등급은 확인 필요. 다른 Basic/Extended 표기도 주문 시 확인.
- 기존 0.15mm 비아/POFV DFM, CPL 방향, 온도·EMC 시험 등 발주 조건은 유지.
- M12/센서/전선/링 단자/에폭시 등 미확정 별도 구매품은 LCSC 번호를 임의로 배정하지 않았다.
- 이번 매칭에 추가 사용자 결정은 없으며, 기존 제품 온도·실제 M12 등 미결 사항은 그대로다.

## 자료와 사용 방법

`manufacturing/jlc/bom_match_20261003/`의 엑셀/CSV 및 JLC BOM/CPL을 사용한다. **이전 A5-R1 ZIP에 들어 있는 BOM은 과거 판**이다. PCB 형상은 유지됐지만 이번 수정 BOM으로 교체해서 검토해야 한다. 주문 실행/제작 승인 아님.

근거:
- [C4 삼성 LCSC](https://www.lcsc.com/product-detail/C318579.html), [잘못 연결됐던 C1532](https://www.lcsc.com/product-detail/C1532.html)
- [C61 JLC](https://jlcpcb.com/partdetail/YAGEO-CC0805KKX7R9BB225/C125847), [YAGEO 개별 사양서](https://www.yageogroup.com/download/specsheet/CC0805KKX7R9BB225)
- [R9/R52 JLC](https://jlcpcb.com/partdetail/44464-0402WGF2212TCE/C43473)
- [C22](https://www.lcsc.com/product-detail/C3898227.html), [R19](https://www.lcsc.com/product-detail/C491130.html)
