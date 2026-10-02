"""A5: In1은 GND 전용, In4는 GND 동박 + 검토된 7개 넷만 허용.

층수/기구/전기 간격은 A4와 같으며 In4 배선은 스냅샷과 별도 DRC로 검증한다.
아래 길이는 회로별 레이아웃 회귀 한도이며 전기적 보증값이 아니다.
"""
IN4_MAX_TRACK_MM = {
    '+3V3': 6, 'VIN_P': 14, 'SWCLK': 7, 'OUT1_SGOOD': 19,
    'RS485_A_EXT': 12, 'DAC2_LATCH': 9, 'DAC_MOSI': 33,
}
