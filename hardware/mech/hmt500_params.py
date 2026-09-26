"""DOTECH HMT500 기구 설계 파라미터 (단위 mm).

좌표: 축 방향 x, 기준면 x = 0 은 육각 앞면(= 본디드 씰 접촉면, "씰면").
       x < 0 쪽이 오일(프로브), x > 0 쪽이 하우징·커넥터.
반경 방향 r (축에서 거리).

이 파일 하나로 3D CAD(hmt500_cad.py)와 2D 도면(hmt500_drawings.py)을 함께 만든다.
설치 치수(노출 프로브 34, G1/2 나사 14, AF27)는 기존 설치 위치 호환을 위해 고정.

Rev B (2026-09-26): 바디–하우징, 하우징–엔드캡을 용접 → 나사(M28×1) + 반경 O링 밀봉으로 변경.
  나사·O링 자리 벽 두께 확보를 위해 하우징 외경 Ø30 → Ø32.
  커넥터는 엔드캡 조립 후 바깥에서 체결하는 전면 장착형(리드선이 엔드캡 구멍을 통과 → 비틀림 없음).
"""

DRAWING_REV = "B"
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

# ── O링 (바디–하우징, 하우징–엔드캡 공통, 반경 방향 정적 밀봉) ──
ORING = dict(id=25.0, cs=2.0, groove_d=25.6, groove_w=2.7, bore=29.0,
             name="O-ring 25 x 2, FKM 75 (radial static seal in Ø29 H8 bore)")

# ── 프로세스 바디 M-101 (SUS316L 일체 선삭) ──
BODY = dict(
    x_front=-32.0,
    spigot=dict(x=(-32.0, -26.0), d=10.0, thread="M10x0.75-6g"),   # 보호캡 체결부
    tube=dict(x=(-26.0, -14.0), d=12.0),                            # 노출 프로브(캡 뒤)
    gthread=dict(x=(-14.0, -2.0), d=20.955, d_minor=18.631, thread="G1/2-A (ISO 228-1)"),
    relief=dict(x=(-2.0, 0.0), d=18.4),                              # 나사 언더컷
    hexa=dict(x=(0.0, 12.0), af=27.0, chamfer_angle=30),
    collar=dict(x=(12.0, 15.0), d=32.0),                            # 하우징 끝면이 닿는 칼라
    seal=dict(x=(15.0, 19.0), d=29.0, fit="f7", groove_x=(15.65, 18.35)),   # O링 자리
    mthread=dict(x=(19.0, 26.0), d=28.0, d_minor=26.917, thread="M28x1-6g"),  # 하우징 체결 수나사
    # 내부
    seat=dict(x=(-32.0, -27.0), d=8.0, fit="H7"),                    # GTMS 피드스루 안착
    wire=dict(x=(-27.0, 12.0), d=5.0),
    cbore=dict(x=(12.0, 26.0), d=22.0),
)

# ── 하우징 M-103 ── (양 끝: O링 자리 Ø29 H8 → 암나사 M28x1 → 본체 내경 Ø27)
HOUSING = dict(x=(15.0, 75.0), od=32.0, id=27.0,
               seal_bore=29.0, seal_len=4.0, thread="M28x1-6H", thread_d=28.0, thread_minor=26.917, thread_len=7.0)

# ── 엔드캡 M-104 ──
ENDCAP = dict(mthread=dict(x=(64.0, 71.0), d=28.0, d_minor=26.917, thread="M28x1-6g"),
              seal=dict(x=(71.0, 75.0), d=29.0, fit="f7", groove_x=(71.65, 74.35)),
              flange=dict(x=(75.0, 81.0), d=32.0, flats_af=28.0),
              cbore=dict(x=(64.0, 75.0), d=22.0),                   # 경량화·리드선 공간
              thread=dict(x=(75.0, 81.0), d=16.0, d_minor=14.376, thread="M16x1.5-6H"))

# ── 구매품 (단순 형상) ──
SEAL = dict(x=(-2.0, 0.0), id=21.5, od=28.7, name="Bonded seal G1/2 (USIT/DIN 3869 type), steel + FKM")
HEADER = dict(x=(-32.0, -27.0), d=8.0, pins=6, pin_d=0.46, pcd=4.5, pin_front=-40.0, pin_rear=27.5,
              name="Glass-to-metal feedthrough header, 6 pin, Ø8 (supplier TBD)")
CARRIER = dict(x=(-44.0, -34.5), w=4.5, t=0.635, name="Sensor carrier, alumina 0.635 (IST MK + Pt1000)")
PCB = dict(d=26.0, t=1.6, x=[28.0, 55.0], name="PCB Ø26 4-layer (measurement / power-output)")
CONNECTOR = dict(body=dict(x=(81.0, 85.0), d=20.0), thread=dict(x=(85.0, 96.0), d=12.0),
                 name="M Connect 8P male, front mount M16x1.5 (P/N TBD)")

TIP_X = CAP["x_tip"]
END_X = CONNECTOR["thread"]["x"][1]
OVERALL = END_X - TIP_X


def hex_corner_d(af):
    return af / 0.8660254


# 부품 목록 (조립도 부품표)
PARTS = [
    ("1", "HMT500-M-101", "Process body", "SUS316L (1.4404)", 1, "Machined"),
    ("2", "HMT500-M-102", "Protective cap", "SUS316L (1.4404)", 1, "Machined, 2 types (flow <1 / >1 m/s)"),
    ("3", "HMT500-M-103", "Housing tube Ø32", "SUS316L (1.4404)", 1, "Machined, M28x1 both ends, marking"),
    ("4", "HMT500-M-104", "End cap", "SUS316L (1.4404)", 1, "Machined, flats AF28"),
    ("5", "HMT500-P-201", "Feedthrough header 6P", "Kovar/316L + glass", 1, "Purchased, laser welded to 1"),
    ("6", "HMT500-P-202", "Sensor carrier + IST MK + Pt1000", "Alumina", 1, "Sub-assembly"),
    ("7", "HMT500-P-203", "Bonded seal G1/2", "Steel + FKM", 1, "Purchased"),
    ("8", "HMT500-E-301", "PCB assembly (2 boards)", "FR-4", 1, "See KiCad HMT500"),
    ("9", "HMT500-P-204", "M Connect 8P male, M16x1.5", "-", 1, "Purchased, front mount, P/N TBD"),
    ("10", "HMT500-P-205", "O-ring 25 x 2", "FKM 75", 2, "1-3 and 3-4 seal"),
    ("11", "HMT500-P-206", "O-ring for connector", "FKM", 1, "Per connector spec"),
]
