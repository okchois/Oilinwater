# 국내 시장 조사 — 국산 오일 내 수분 트랜스미터

조사일: 2026-09-26

> **출처 주의:** 대부분의 원문 페이지(한전, 언론사, 업체 사이트)가 이 환경의 네트워크 정책으로 열리지 않았습니다. 아래 내용은 거의 전부 **검색 결과 요약·스니펫 기반**이며, 수치·날짜는 원문 재확인이 필요합니다.

## 1. 수요 산업과 잠재 고객

### 1.1 전력 변압기 — 가장 확실한 수요처

- **한전 변전소 종합 예방진단시스템**
  - 154 kV 금천 변전소에 시범 적용했고, 국가산단과 수도권 부하밀집지역부터 확대해 2030년까지 전사 구축이 목표입니다.
  - 사업비는 변전소 1곳당 약 2억 원, 총 약 2,594억 원으로 추정됩니다(아시아투데이 2026-06 기사 스니펫).
  - 변압기에 붙는 센서로 부싱, 부분방전, OLTC, 유중가스(DGA)가 소개되어 있습니다. **수분 센서가 포함되는지는 확인하지 못했습니다.**
- **한전 전력연구원:** 2019~2022년에 유중 삽입형 가스센서 3종(H₂, C₂H₂, CO)을 국산화했습니다. 반면 **수분 센서를 국산화한 사례는 찾지 못했습니다** → 빈자리이자, 가스센서를 보완하는 제품이 될 가능성이 있습니다(추정).
- **변압기 제조사:** 효성중공업(ARMOUR/ARMOUR+), HD현대일렉트릭(INTEGRICT), LS일렉트릭, 일진전기. 모두 AI 데이터센터용 전력기기를 공략하고 있습니다.
- **변압기 진단 시스템 업체 (OEM 공급 대상):**
  - 피닉스테크: 변압기 감시 시스템(TMS), DGA, 온라인 수분 감시·건조 장치(TRANSEC CL). TMS는 "타사 센서 연동 가능"으로 소개됩니다.
  - KJ다이나
  - 라인하우젠코리아

### 1.2 기타 산업

| 산업 | 현황 | 수분 센서 채택 확인 여부 |
|---|---|---|
| 조선·해양 | HD한국조선해양(HiCBM), 한화오션, 삼성중공업(SVESSEL)의 선박 상태진단 솔루션 | 미확인 |
| 풍력 | 유니슨 원격 모니터링. 국내 상태감시(CMS) 업체로 렉터슨, 우리기술 | 기어오일 수분을 감시 항목으로 언급한 자료만 있음 |
| 건설기계 | HD건설기계(2026-01 합병 출범, 스니펫), DEVELON 원격관리 | 미확인. 기준 경쟁품은 HYDAC AS1000 |
| 발전 터빈유 | 터빈유 KS M 2120, 절연유 KS C 2301 | 발전사의 온라인 감시 기준은 미확인 |
| 윤활관리 업체 (채널 후보) | 솔지(대구, Tan Delta 센서 취급), 비투솔루션(오일 모니터링, 여과장치) | – |

## 2. 국내 유통 제품 (외산)

| 브랜드 | 제품 | 국내 채널 |
|---|---|---|
| Vaisala | MMT162, MMP8, MHT410 | Vaisala Korea, 엠지코리아, 플루토테크 |
| E+E Elektronik | EE381, EE360, EE364 | 이플러스이일렉트로닉코리아, 엠지코리아 |
| HYDAC | AS1000 | 하이닥코리아 |
| ifm | LDH100/112/122 (M12, IO-Link, 4–20 mA) | ifm 한국 (2024년 신제품 소개) |
| Kobold | AFO | 한국어 페이지 있음, 대리점 미확인 |
| Parker | 수분 오염 관련 콘텐츠 | 파카하니핀 코리아 (센서 판매 여부 미확인) |

- **소형 aw 방식 제품은 국내에서 사실상 외산이 차지하고 있습니다.**
- 조사된 국산 전용 제품은 (주)두텍 HMX350뿐입니다(아래 3절).

## 3. (주)두텍 공개 정보 현황

검색에 잡힌 공개 정보를 정리했습니다. 사내 정보와 다르면 사내 정보가 우선합니다.

- 영문 표기는 **DOTECH**(dotech21.com)입니다. 이름이 비슷한 "(주)두시텍"은 다른 회사입니다.
- 온습도 센서, 디지털 컨트롤러, 압력센서, 냉동공조 제어기기, 클린룸 FFU/BFU용 LCU를 다룹니다. 미스미, 코머신, 다아라에 입점해 있습니다.
- 제품 카테고리에 **"오일수분 트랜스미터"** 가 있습니다.
  - **HMX350 멀티 트랜스미터**가 "수분활성도, 오일수분측정"을 한다고 소개됩니다.
  - 형태는 벽면형·분리형·고압 프로브(최대 20 bar)이고, 통신은 Ethernet과 RS485입니다.
- 방폭형 온습도 트랜스미터 HTX500도 있습니다.

→ **이번 신제품의 의미:** 이미 오일 수분 제품군과 RS-485 통신 경험이 있으므로, 이번 제품은 **EE364급 소형 일체형(M 커넥터, G½, aw/ppm, 부트로더)으로 라인업을 넓히는 것**으로 볼 수 있습니다.

## 4. 정부 지원 프로그램

| 프로그램 | 내용 | 적합도 |
|---|---|---|
| **한전 중소벤처 협력연구개발** | 배전·송변전 기자재와 핵심부품(국산화 포함). 융복합 과제 최대 20억 원, 정부 공동투자형 최대 75%(2년 이하 12억 원). 기업 부담 15% 이상. 기업이 과제를 직접 제안 가능 | **변압기용 수분 센서에 가장 적합** |
| 구매조건부 신제품개발사업 (중기부/TIPA) | 수요처(공공기관·대기업)가 구매를 약속하는 과제. 동서발전, 석유공사 등이 공동투자형으로 운영 | 높음 (수요처 확보가 관건) |
| 중기부 2026 소부장 분야 | 신규 140개 과제, 168억 원, 지원 품목 137개로 확대 | 센서 품목 해당 여부는 공고문 확인 필요 |
| 산업부 R&D | 2026년 5.5조 원, 그중 소부장 공급망 1조 4,914억 원 | 중간 |
| 조달청 혁신제품 시범구매 | 2026년 3차 74개 제품·127억 원. 2027년 수요조사 10월 시작 | 제품 출시 후 |
| NEP(신제품 인증) / EPC(성능인증) | NEP는 공공기관 20% 의무구매, EPC는 우선구매·수의계약 가능 | 제품 출시 후 |

## 5. 인증과 조달 장벽

- **KC 전자파 적합성:** 산업용 트랜스미터는 보통 "적합등록" 대상입니다. 신청은 전파관리소(emsit.go.kr), 시험은 KTL 등에서 합니다. → **기본으로 필요합니다.**
- **KCs 방폭:** 폭발 위험 장소에서 쓰는 전기기기는 의무입니다(산업안전보건법 제84조). 인증기관은 산업안전보건인증원, 가스안전공사, KTL입니다. 정유·화학, 선박 일부 구역에 필요하며, 두텍의 방폭 제품(HTX500) 경험을 활용할 수 있습니다.
- **한국선급(KR) 형식승인:** 선박용 기자재가 대상입니다.
- **한전 기자재 공급자 등록(유자격):**
  - 중요 기자재는 등록 업체만 입찰할 수 있습니다(한전SRM).
  - 2026년 3월에 전면 개편이 추진됐다는 기사 스니펫이 있습니다.
  - 센서 단품이 등록 대상인지는 확인하지 못했습니다. → 현실적으로는 **변압기 제조사나 TMS 업체를 거쳐 부품으로 납품**하는 경로가 유력합니다(추정).
- **발전 5사:** 별도의 기자재 공급자 유자격 인증 제도가 있습니다.

## 6. 진입 경로 제안 (추정 포함)

1. **변압기 쪽:**
   - 한전 협력 R&D나 구매조건부 과제로 국산화 실적을 확보합니다.
   - 변압기 3사와 TMS 업체(피닉스테크 등)에 OEM으로 공급합니다. 이미 국산화된 가스센서를 보완하는 제품으로 제안할 수 있습니다.
2. **유압·윤활 쪽:**
   - 윤활관리 업체(솔지, 비투솔루션)와 필터·정제기 업체를 판매 채널로 씁니다.
   - 건설기계 OEM은 IO-Link나 CAN 파생 모델이 있어야 대응할 수 있습니다.
3. **인증:** KC 적합등록을 기본으로 하고, 시장에 따라 KR과 KCs를 추가합니다.

## 출처

- https://www.epluse.com/ko/products/moisture-in-oil-instrumentation/oil-measurement-transmitter/ee381/
- https://www.mg-korea.co.kr/shop/list.php?ca_id=201206
- https://www.vaisala.com/ko/products/instruments-sensors-and-other-measurement-devices/instruments-industrial-measurements/mmp8
- https://blog.plutotech.co.kr/89
- https://www.ifm.com/kr/ko/shared/productnews/2024/hmi/oil-humidity-sensor-keeps-an-eye-on-quality
- https://m.hydac.com/kr-ko/company.html
- https://www.hitouch.co.kr/product/product_list.htm?product_category=06050300
- https://dotech21.com/layout/kor/home.php?go=item.view&mid=11&s_mode=A&s_subj=002006000&num=122&s_key1=&s_que=&start=0
- https://www.komachine.com/ko/companies/dotech/products/series/16394
- https://www.epj.co.kr/news/articleView.html?idxno=30902
- http://www.epnews.co.kr/news/articleView.html?idxno=46335
- https://www.asiatoday.co.kr/kn/view.php?key=20260628010009806
- https://www.hyosungheavyindustries.com/kr/business/digital-solutions/P010302
- https://www.hd-hyundaielectric.com/elect/m/ko/integrict/integrict.jsp
- https://phoenixtech.kr/bbs/board.php?bo_table=product&sca=1&wr_id=40
- https://reinhausen.co.kr/
- https://www.solge.com/html/sub02_1.html?cate=1
- https://www.kepco.co.kr/eum/program/technology/collaboration/conts.do
- https://www.mt.co.kr/policy/2026/03/24/2026032409440480166
- https://m.gov.kr/portal/service/serviceInfo/B55207000038
- https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000116943
- https://www.korea.kr/news/policyNewsView.do?newsId=148956908
- https://www.etnews.com/20260818000083
- https://www.nepmark.or.kr/sub1/sub3.asp?smenu=sub1&stitle=subtitle1_3
- https://customer.ktl.re.kr/web/contents/K101010600.do
- https://miis.kosha.or.kr/oshci/busi/viewExplosionInfo.do
- https://www.krs.co.kr/kor/Content/CF_View.aspx?MRID=124&URID=71
