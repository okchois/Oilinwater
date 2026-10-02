"""A2 배치 원본: 회로/기구 제약을 검증한 110개 부품 좌표.

placement/artwork_A2.json은 생성기의 입력이며 KiCad 결과 파일이 아니다.
J1/J3/J5/J2/U4 위치는 A1과 같다. DAC 보상 C의 순서/방향과 U15
피드백 저항은 실제 단면 배선 경로를 확인하여 조정했다.
"""
from pathlib import Path

LAYOUT_PATH = Path(__file__).resolve().parent / 'placement' / 'artwork_A2.json'
# 기구 좌표. MCU 안쪽 비아와 우측 모서리 SPI 비아의 반대면 부품 금지 영역.
BACK_ESCAPE = (37.5, -1.9, 44.1, 1.9)
BACK_ESCAPES = (BACK_ESCAPE, (45.7, -3.35, 46.8, 3.15))
# A4: R42를 기구 좌표 x +0.55/y −0.20 mm 이동하면서 실제 반대면 패드·비아
# 간격을 KiCad로 재검증했다. A2/A3의 넓은 탐색용 창에서 R42가 사용하는
# 왼쪽 부분을 제외한 통로를 예약한다. 전기적 keepout/DRC 간격은 유지한다.
BACK_ESCAPES_A4 = (BACK_ESCAPE, (46.25, -3.35, 46.8, 3.15))

def plan(original):
    # 고정 좌표 배치에서도 기존 순서/부품 목록으로 생성기 검사를 수행한다.
    return original
