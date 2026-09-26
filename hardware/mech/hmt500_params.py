"""DOTECH HMT500 기구 설계 파라미터 (단위 mm).

좌표: 축 방향 x, 기준면 x = 0 은 육각 앞면(= 본디드 씰 접촉면, "씰면").
       x < 0 쪽이 오일(프로브), x > 0 쪽이 하우징·커넥터.
반경 방향 r (축에서 거리).

이 파일 하나로 3D CAD(hmt500_cad.py)와 2D 도면(hmt500_drawings.py)을 함께 만든다.
설치 치수(노출 프로브 34, G1/2 나사 14, AF27, Ø30)는 기존 설치 위치 호환을 위해 고정.
"""

DRAWING_REV = "A"
DATE = "2026-09-26"

# ── 보호캡 M-102 ──
CAP = dict(
    x_tip=-48.0,          # 프로브 끝
    x_rear=-26.0,         # 프로브 튜브 어깨에 맞닿는 면
    od=12.0,
    bore=9.0,             # 센서실 내경
    tip_wall=1.2,
    tip_hole=3.0,
    thread="M10x0.75-6H",
    thread_len=6.0,       # 뒤쪽 내부 나사 길이 (x -32 ~ -26)
    hole_d=2.6,
    # (x 위치, 각도°) 측면 유통 구멍 8개: 2줄씩 90° 엇갈림
    holes=[(-44.5, 0), (-44.5, 180), (-41.0, 90), (-41.0, 270),
           (-37.5, 0), (-37.5, 180), (-34.0, 90), (-34.0, 270)],
    chamfer=0.5,
)

# ── 프로세스 바디 M-101 (SUS316L 일체 선삭) ──
BODY = dict(
    x_front=-32.0,
    spigot=dict(x=(-32.0, -26.0), d=10.0, thread="M10x0.75-6g"),   # 보호캡 체결부
    tube=dict(x=(-26.0, -14.0), d=12.0),                            # 노출 프로브(캡 뒤)
    gthread=dict(x=(-14.0, -2.0), d=20.955, d_minor=18.631, thread="G1/2-A (ISO 228-1)"),
    relief=dict(x=(-2.0, 0.0), d=18.4),                              # 나사 언더컷
    hexa=dict(x=(0.0, 12.0), af=27.0, chamfer_angle=30),
    collar=dict(x=(12.0, 15.0), d=30.0),                            # 하우징 용접 칼라
    wspigot=dict(x=(15.0, 20.0), d=27.0, fit="h7"),                  # 하우징 삽입부
    # 내부
    seat=dict(x=(-32.0, -27.0), d=8.0, fit="H7"),                    # GTMS 피드스루 안착
    wire=dict(x=(-27.0, 12.0), d=5.0),
    cbore=dict(x=(12.0, 20.0), d=22.0),
)

# ── 하우징 M-103 ──
HOUSING = dict(x=(15.0, 75.0), od=30.0, id=27.0)

# ── 엔드캡 M-104 ──
ENDCAP = dict(spigot=dict(x=(70.0, 75.0), d=27.0, fit="h7"),
              flange=dict(x=(75.0, 79.0), d=30.0),
              thread=dict(d=16.0, d_minor=14.376, thread="M16x1.5-6H"))

# ── 구매품 (단순 형상) ──
SEAL = dict(x=(-2.0, 0.0), id=21.5, od=28.7, name="Bonded seal G1/2 (USIT/DIN 3869 type), steel + FKM")
HEADER = dict(x=(-32.0, -27.0), d=8.0, pins=6, pin_d=0.46, pcd=4.5, pin_front=-40.0, pin_rear=21.5,
              name="Glass-to-metal feedthrough header, 6 pin, Ø8 (supplier TBD)")
CARRIER = dict(x=(-44.0, -34.5), w=4.5, t=0.635, name="Sensor carrier, alumina 0.635 (IST MK + Pt1000)")
PCB = dict(d=26.0, t=1.6, x=[22.0, 48.0], name="PCB Ø26 4-layer (measurement / power-output)")
CONNECTOR = dict(body=dict(x=(79.0, 83.0), d=20.0), thread=dict(x=(83.0, 94.0), d=12.0),
                 name="M Connect 8P male, rear mount M16x1.5 (P/N TBD)")

TIP_X = CAP["x_tip"]
END_X = CONNECTOR["thread"]["x"][1]
OVERALL = END_X - TIP_X


def hex_corner_d(af):
    return af / 0.8660254


# 부품 목록 (조립도 부품표)
PARTS = [
    ("1", "HMT500-M-101", "Process body", "SUS316L (1.4404)", 1, "Machined"),
    ("2", "HMT500-M-102", "Protective cap", "SUS316L (1.4404)", 1, "Machined, 2 types (flow <1 / >1 m/s)"),
    ("3", "HMT500-M-103", "Housing tube", "SUS316L (1.4404)", 1, "Machined / tube, laser marking"),
    ("4", "HMT500-M-104", "End cap", "SUS316L (1.4404)", 1, "Machined"),
    ("5", "HMT500-P-201", "Feedthrough header 6P", "Kovar/316L + glass", 1, "Purchased, laser welded to 1"),
    ("6", "HMT500-P-202", "Sensor carrier + IST MK + Pt1000", "Alumina", 1, "Sub-assembly"),
    ("7", "HMT500-P-203", "Bonded seal G1/2", "Steel + FKM", 1, "Purchased"),
    ("8", "HMT500-E-301", "PCB assembly (2 boards)", "FR-4", 1, "See KiCad HMT500"),
    ("9", "HMT500-P-204", "M Connect 8P male, M16x1.5", "-", 1, "Purchased, P/N TBD"),
    ("10", "HMT500-P-205", "O-ring for connector", "FKM", 1, "Per connector spec"),
]
