"""DOTECH HMT500 기구 설계 파라미터 (단위 mm).

좌표: 축 방향 x, 기준면 x = 0 은 육각 앞면(= 본디드 씰 접촉면, "씰면").
       x < 0 쪽이 오일(프로브), x > 0 쪽이 하우징·커넥터.
반경 방향 r (축에서 거리).

이 파일 하나로 3D CAD(hmt500_cad.py)와 2D 도면(hmt500_drawings.py)을 함께 만든다.
설치 치수(노출 프로브 34, G1/2 나사 14, AF27)는 기존 설치 위치 호환을 위해 고정.

Rev B (2026-09-26): 바디–하우징, 하우징–엔드캡을 용접 → 나사(M28×1) + 반경 O링 밀봉으로 변경.
  나사·O링 자리 벽 두께 확보를 위해 하우징 외경 Ø30 → Ø32.
  커넥터는 엔드캡 조립 후 바깥에서 체결하는 전면 장착형(리드선이 엔드캡 구멍을 통과).

Rev C (2026-09-26): 원형 PCB 2장 → 축 방향 긴 PCB 1장 (축을 지나는 평면, 가운데가 넓은 모양).
  앞쪽은 바디 카운터보어에 나사 고정한 수지 홀더(M-105)의 홈에, 뒤쪽은 수지 지지링(M-106)의 홈에 끼운다.
  하우징·엔드캡을 돌려 체결해도 PCB는 바디에 고정되어 함께 돌지 않는다.

Rev D (2026-09-29): 센서 접속을 두텍 HTX99R 센서 커넥터(ref/ STEP)로 변경.
  교체형 센서 프로브(MK33-W mini + Pt1000, 4핀)를 커넥터 소켓에 꽂는다.
  커넥터는 바디 앞 Ø10 H8 구멍에 O링(홈 Ø8.2)으로 밀봉, 플랜지 Ø11은 바디 턱이 압력을 받고 보호캡 턱이 빠짐을 막는다.
  커넥터 뒤 핀 → 납땜·포팅 공간 → GTMS 피드스루(압력 격벽 유지) → 전자부.
  커넥터 플랜지 Ø11을 수용하려고 노출 프로브·보호캡 Ø12 → Ø16 (노출 길이 34, G1/2, 전장 144 유지).

Rev E (2026-09-29): HTX99R 커넥터의 두 Ø10 원통은 M10×0.75 나사 (두텍 확인).
  아래 나사 → 바디 앞 M10×0.75 암나사에 체결 (O링은 나사–플랜지 사이 홈, Ø10 H8 밀봉면). 맞변 7로 잡고 조임.
  위 나사 → 보호캡 체결 (캡 Ø12로 복귀, EE364와 같은 외경). 바디 앞 튜브는 플랜지 자리 때문에 Ø14.
  배선 꼬임 방지: 커넥터 핀에 선을 먼저 납땜 → 커넥터 체결(선 끝 자유) → 선을 뒤로 빼 피드스루에 납땜
  → 피드스루를 바디 뒤쪽(Ø22 카운터보어 바닥) Ø8 H7 자리에 뒤에서 넣고 뒤에서 레이저 용접.
"""

DRAWING_REV = "E"
DATE = "2026-09-29"

# ── 보호캡 M-102 ──
CAP = dict(
    x_tip=-48.0,          # 프로브 끝
    x_rear=-30.0,         # 바디 앞면(커넥터 플랜지)에 닿는 면
    od=12.0,
    bore=9.0,             # 센서실 내경 (센서 프로브 수용)
    tip_wall=1.2,
    tip_hole=3.0,
    thread="M10x0.75-6H",                 # HTX99R 커넥터 위 나사에 체결
    thread_x=(-37.0, -31.5),
    thread_minor=9.188,
    relief=dict(x=(-31.5, -30.0), d=10.2),   # 커넥터 나사 언더컷(홈 Ø8.1) 위 여유
    hole_d=2.4,
    # (x 위치, 각도°) 측면 유통 구멍 8개: 2줄씩 90° 엇갈림 (센서 프로브 둘레)
    holes=[(-45.2, 0), (-45.2, 180), (-43.0, 90), (-43.0, 270),
           (-40.8, 0), (-40.8, 180), (-38.6, 90), (-38.6, 270)],
    chamfer=0.5,
)

# ── 센서 커넥터 HTX99R-SC (두텍 기존 부품, ref/ STEP) ──
# 커넥터 좌표 y(축) → 제품 x = CONN_X0 - y (소켓 면 y=15 이 프로브 끝 쪽)
SENSOR_CONN = dict(step="ref/HTX99R_Sensor_Probe_Sensor_Connector.STEP", x0=-22.0,
                   body_d=10.0, flange_d=11.0, flange_y=(7.0, 8.0), len=15.0, pin_y=-3.0,
                   oring_groove=dict(d=8.2, y=(5.5, 7.0)), socket_face_y=15.0, sock_depth=7.9,
                   thread_lower=dict(y=(0.5, 5.5), spec="M10x0.75"),   # → 바디 암나사
                   thread_upper=dict(y=(9.5, 15.0), spec="M10x0.75"),  # → 보호캡
                   name="HTX99R sensor connector 4P (DOTECH)")
CONN_ORING = dict(id=8.0, cs=1.2, name="O-ring 8 x 1.2 FKM (connector seal in Ø10 H8)")

# ── 교체형 센서 프로브 (MK33-W mini + Pt1000 MiniSens) ──
SENSOR_PROBE = dict(plug=dict(x=(-39.5, -37.0), d=8.5),          # 수지 플러그 (PEEK)
                    pins=dict(x=(-37.0, -32.0), d=1.0, pitch=2.54),  # 소켓에 꽂히는 핀 4개 (규격 확인)
                    board=dict(x=(-46.3, -39.5), w=6.0, t=0.8),    # 센서 기판 (세라믹 또는 FR-4)
                    mk33=dict(l=5.0, w=3.81, t=0.4),              # IST MK33-W mini (150138)
                    pt1000=dict(l=1.6, w=1.2, t=0.5),             # IST MiniSens Pt1000 F0.1
                    name="Sensor probe insert: MK33-W mini + Pt1000, 4 pins")

# ── O링 (바디–하우징, 하우징–엔드캡 공통, 반경 방향 정적 밀봉) ──
ORING = dict(id=25.0, cs=2.0, groove_d=25.6, groove_w=2.7, bore=29.0,
             name="O-ring 25 x 2, FKM 75 (radial static seal in Ø29 H8 bore)")

# ── 프로세스 바디 M-101 (SUS316L 일체 선삭) ──
BODY = dict(
    x_front=-30.0,
    tube=dict(x=(-30.0, -14.0), d=14.0),                            # 노출 프로브 (캡 뒤, 커넥터 수용)
    gthread=dict(x=(-14.0, -2.0), d=20.955, d_minor=18.631, thread="G1/2-A (ISO 228-1)"),
    relief=dict(x=(-2.0, 0.0), d=18.4),                              # 나사 언더컷
    hexa=dict(x=(0.0, 12.0), af=27.0, chamfer_angle=30),
    collar=dict(x=(12.0, 15.0), d=32.0),                            # 하우징 끝면이 닿는 칼라
    seal=dict(x=(15.0, 19.0), d=29.0, fit="f7", groove_x=(15.65, 18.35)),   # O링 자리
    mthread=dict(x=(19.0, 26.0), d=28.0, d_minor=26.917, thread="M28x1-6g"),  # 하우징 체결 수나사
    # 내부
    conn_cbore=dict(x=(-30.0, -29.0), d=11.2),                      # 커넥터 플랜지 자리
    conn_land=dict(x=(-29.0, -27.5), d=10.0, fit="H8"),              # O링 밀봉면 (커넥터 홈 Ø8.2)
    conn_thread=dict(x=(-27.5, -22.0), d=9.188, d_major=10.0, thread="M10x0.75-6H"),   # 커넥터 아래 나사
    channel=dict(x=(-22.0, 7.0), d=7.0),                             # 배선 통로 (커넥터 핀 → 피드스루)
    seat=dict(x=(7.0, 12.0), d=8.0, fit="H7"),                       # GTMS 피드스루 (뒤에서 삽입·용접, 압력 격벽)
    cbore=dict(x=(12.0, 26.0), d=22.0),
    holder_taps=dict(n=2, d=2.0, depth=5.0, pcd=16.0, thread="M2-6H"),   # 홀더 고정 나사 (카운터보어 바닥 x=12)
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
HEADER = dict(x=(7.0, 12.0), d=8.0, pins=6, pin_d=0.46, pcd=4.5, pin_front=3.0, pin_rear=13.5,
              name="Glass-to-metal feedthrough header, 6 pin, Ø8 (supplier TBD)")
# ── PCB E-301: 축 방향 1장, 축을 지나는 평면(z=0)에 세움. 폭은 y 방향 ──
PCB = dict(t=1.6, x=(14.5, 71.0),
           sections=[(14.5, 26.0, 18.0),    # 바디 카운터보어 Ø22 안
                     (26.0, 64.0, 23.0),    # 하우징 Ø27 안
                     (64.0, 71.0, 18.0)],   # 엔드캡 카운터보어 Ø22 안
           corner_r=1.0,
           holes=[(16.25, 5.0), (16.25, -5.0)], hole_d=2.2,   # 홀더 가로 나사 M2 (x, y)
           # J3 센서 하네스 헤더: JST SH 1.0 mm 4P 윗면 삽입 (BM04B-SRSS-TB), 윗면(+z), 외형 포함 MP 패드
           jst=dict(x=(19.5, 23.5), y=(-3.5, 3.5), h=4.25, side=1,
                    part="JST BM04B-SRSS-TB (SH 1.0 mm 4P, top entry, SMD)"),
           conn_pads_x=(66.0, 70.0),                           # 커넥터 리드선 패드
           zones=[("측정", "J3 · PCAP04 · ADS1220 · 기준 C", 18.0, 34.0),
                  ("MCU·전원", "STM32G0B1 · eFuse · 벅 · LDO", 34.0, 50.0),
                  ("출력·보호", "DAC8760×2 · TPS26611 · THVD2450 · TVS", 50.0, 71.0)],
           name="PCB 57×23 4-layer, 1 board (E-301)")
# 표현용 주요 부품 (x, y, 가로, 세로, 높이, 면 +1/-1)
PCB_PARTS = [
    (21.5, 0.0, 4.0, 7.0, 4.25, 1),    # J3 JST SH 4P 헤더 (윗면 삽입)
    (27.0, 0.0, 4.0, 4.0, 0.9, 1),     # PCAP04 QFN24 — J3 바로 뒤 (센서선 최단)
    (31.5, 0.0, 5.0, 6.4, 1.2, 1),     # ADS1220 TSSOP16
    (27.0, 4.5, 2.0, 1.25, 1.0, -1),   # 기준 C (C0G)
    (41.0, 0.0, 7.0, 7.0, 1.4, 1),     # STM32G0B1CCT3 LQFP48
    (38.0, 0.0, 5.0, 4.0, 1.0, -1),    # TPS2660 eFuse
    (45.0, 0.0, 4.0, 4.0, 3.0, -1),    # 벅 인덕터
    (41.0, 7.0, 3.0, 3.0, 1.0, -1),    # LMR36006
    (55.0, 0.0, 6.0, 6.0, 1.0, 1),     # DAC8760 #1 VQFN40
    (55.0, 0.0, 6.0, 6.0, 1.0, -1),    # DAC8760 #2
    (61.5, 0.0, 3.0, 3.0, 1.0, 1),     # TPS26611
    (61.5, 5.5, 5.0, 6.0, 1.7, -1),    # THVD2450 SOIC8
    (67.5, 0.0, 7.0, 6.0, 2.4, 1),     # SMCJ TVS
    (67.5, 0.0, 5.0, 4.0, 2.0, -1),    # CM 초크
]

PCB_HOLDER = dict(x=(12.2, 18.0), d=21.6, hole_d=6.0, slot_w=1.7, slot_x=(14.5, 18.0),   # Ø6: 하네스 W-1 전선 통과
                  screw_pcd=16.0, screw_d=2.2, cbore_d=4.0, cbore_depth=1.8,
                  cross=dict(x=16.25, y=(5.0, -5.0), d=2.2, tap="M2"),
                  name="PCB holder (PEEK or PA66-GF30)")
PCB_RING = dict(x=(59.0, 63.0), od=26.4, id=20.0, slot_w=1.7, slot_y=11.6,
                name="PCB rear support ring (PEEK or PA66-GF30)")
# 센서 하네스 W-1: 피드스루 뒤 핀 1~4 (납땜 + 수축튜브) → JST SH 플러그 → PCB J3
HARNESS = dict(plug=dict(x=(20.0, 23.0), y=(-2.5, 2.5), z_top=5.6),   # SHR-04V-S 꽂힌 상태 외형
               wire_d=0.6, pitch=1.0, bend_z=6.6, gap_z=2.2, length=22.0,
               pins=[("1", "SENS_C1", "MK33 전극 1"), ("2", "SENS_C2", "MK33 전극 2"),
                     ("3", "PT_P", "Pt1000 +"), ("4", "PT_N", "Pt1000 −")],
               ft_pins=(0, 1, 2, 3),        # 피드스루 핀 번호(0부터). 4·5 예비
               housing="JST SHR-04V-S", contact="JST SSH-003T-P0.2-H ×4 (AWG 32–28)",
               wire="AWG 30 PTFE 절연 (UL1213 계열, 200 °C), 4심, 길이 22 ±2",
               name="Sensor harness W-1, JST SH 1.0 mm 4P")
CONNECTOR = dict(body=dict(x=(81.0, 85.0), d=20.0), thread=dict(x=(85.0, 96.0), d=12.0),
                 inner=dict(x=(73.0, 81.0), d=15.9),
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
    ("5", "HMT500-P-201", "Feedthrough header 6P", "Kovar/316L + glass", 1, "Purchased, welded to 1 from rear"),
    ("6", "HMT500-P-202", "Sensor probe: MK33-W mini + Pt1000", "PEEK + ceramic", 1, "Plug-in, replaceable"),
    ("7", "HMT500-P-203", "Bonded seal G1/2", "Steel + FKM", 1, "Purchased"),
    ("8", "HMT500-E-301", "PCB assembly 57x23 (1 board)", "FR-4", 1, "See KiCad HMT500"),
    ("9", "HMT500-P-204", "M Connect 8P male, M16x1.5", "-", 1, "Purchased, front mount, P/N TBD"),
    ("10", "HMT500-P-205", "O-ring 25 x 2", "FKM 75", 2, "1-3 and 3-4 seal"),
    ("11", "HMT500-P-206", "O-ring for connector", "FKM", 1, "Per connector spec"),
    ("12", "HMT500-M-105", "PCB holder", "PEEK / PA66-GF30", 1, "Machined or molded"),
    ("13", "HMT500-M-106", "PCB rear support ring", "PEEK / PA66-GF30", 1, "Machined or molded"),
    ("14", "HMT500-P-207", "Screw M2x6 (2) + M2x12 (2)", "A4 stainless", 4, "ISO 14580 / 7380"),
    ("15", "HTX99R-SC", "Sensor connector 4P, M10x0.75 x2", "per DOTECH dwg", 1, "In-house, screwed into 1"),
    ("16", "HMT500-P-208", "O-ring 8 x 1.2", "FKM 75", 1, "Connector seal"),
    ("17", "HMT500-W-1", "Sensor harness, JST SH 1.0 4P", "PTFE AWG30", 1, "5 → J3 on 8, L22"),
]
