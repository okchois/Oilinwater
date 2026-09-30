# HMT500(260313A) 프로젝트 풋프린트 라이브러리 `HMT500_260313A.pretty`

- 회로도에서 쓰는 풋프린트를 모두 이 폴더에 모아, 프로젝트만으로 PCB를 만들 수 있게 했습니다 (`fp-lib-table` 별칭 `HMT500_260313A`).
- 표준 풋프린트: KiCad 공식 라이브러리 **7.0.11 태그**에서 그대로 복사 (CC-BY-SA 4.0 + KiCad 라이브러리 예외 조항). KiCad 7로 읽을 수 있는 형식입니다.
- 직접 만든 3종 (`hardware/kicad/gen_footprints.py`):
  - `Texas_RNX0012A_VQFN-HR-12_2x3mm` — LMR36006, TI SNVSB48C RNX0012A Example Board Layout 치수
  - `GDT_Bourns_2035-xx-SM` — 2전극 SMD GDT (Bourns 2035-xx-SM 권장 패드 4.0 피치, 1.3 × 5.6)
  - `Texas_DRB0008A_PadFloat` — TVS3301: 방열 패드는 떠 있어야 해서(데이터시트 표 7-1) 비아·뒷면 패드를 뺀 판
