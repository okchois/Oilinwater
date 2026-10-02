# DOTECH 실크 로고 원본

사용자 작업 폴더 `Claude/OILWATCH/docs/assets/dotech_logo_navy.png`에서 가져온 두텍 로고.
작은 기판에서 읽기 어려운 SENSING & CONTROL 부제는 제외하고 DOTECH 워드마크를 탑면 실크로 사용한다.
`generate_dotech_wordmark.py`는 알파 윤곽을 추출하고 제약 삼각분할한다(Pillow, numpy, shapely 2.1).
`dotech_wordmark.json`은 원본 비율을 유지한 정규화 벡터이며 `silk_layout.py`가 실제 PCB F.SilkS 다각형으로 만든다.
