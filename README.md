# Oilinwater — 오일 내 수분 트랜스미터

오일(유압유·윤활유·절연유·연료) 속 수분을 온라인으로 측정하는 트랜스미터 개발 프로젝트.

- [조사 보고서](docs/research-report.md) — 측정 원리, 경쟁 제품, 센서 소자, 회로/기구/펌웨어 설계, 교정, 인증, 로드맵
- [`tools/moisture_calc.py`](tools/moisture_calc.py) — 수분 활동도(aw) ↔ ppm 환산 참조 구현

```bash
python3 tools/moisture_calc.py --temp 20 --aw 0.5     # aw -> ppm
python3 tools/moisture_calc.py --temp 60 --ppm 20     # ppm -> aw
```
