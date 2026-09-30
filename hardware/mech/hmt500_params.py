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
  커넥터 뒤 핀 → 하네스 W-1 (Ø7 관통 통로, 케이블만) → 전자부 J3. (Rev F: 피드스루 없음)
  커넥터 플랜지 Ø11을 수용하려고 노출 프로브·보호캡 Ø12 → Ø16 (노출 길이 34, G1/2, 전장 144 유지).

Rev G (2026-09-30): 바디 앞 캡 보호 칼라 Ø12.3 × 3.5 (튜브 Ø16) — 보호캡이 꺾일 때 HTX99R 보호.
  HTX99R 위·아래 나사 모두 M10×1.0 (두텍 확인, 아래 Rev E의 M10×0.75 정정) → 바디 암나사 M10×1.0-6H.
  조립 시뮬레이션 반영(A–F): 홀더 창, PCB 계단 63.4, 샤시 선, W-2 40 mm, 밀대 T-001.

Rev H (2026-09-30): 외형을 E+E EE364와 부위별로 같게 — 노출 프로브 Ø12 × 34, G½ 14, 육각 AF27 × 10,
  몸통 Ø30, 씰면 ~ 하우징 끝 77, M12 15, 전장 140.
  보호캡 5.5 mm 연장(끝 쪽, 옆 구멍 1줄 추가). 육각 12 → 10 → 안쪽 전체(칼라·하우징·엔드캡·PCB·홀더·링) x −2.
  하우징 Ø32/Ø27 → Ø30/Ø25, 결합 나사 M28×1 → M26×1 (앞 오른나사, 뒤 왼나사), O링 자리 Ø29 → Ø27, O링 25×2 → 24×1.5.
  엔드캡 플랜지 6 → 4 (맞변 AF27), M16×1.5 커넥터 나사를 안쪽으로 2 mm (x 71–77). PCB 폭·길이·배치는 그대로.

Rev E (2026-09-29): HTX99R 커넥터의 두 Ø10 원통은 M10×0.75 나사 (두텍 확인 — Rev G에서 M10×1.0으로 정정).
  아래 나사 → 바디 앞 M10×0.75 암나사에 체결 (O링은 나사–플랜지 사이 홈, Ø10 H8 밀봉면). 맞변 7로 잡고 조임.
  위 나사 → 보호캡 체결 (캡 Ø12로 복귀, EE364와 같은 외경). 바디 앞 튜브는 플랜지 자리 때문에 Ø14.
  배선 꼬임 방지: 커넥터 핀에 선을 먼저 납땜 → 커넥터 체결(선 끝 자유) → 선을 뒤로 빼 피드스루에 납땜
  → 피드스루를 바디 뒤쪽(Ø22 카운터보어 바닥) Ø8 H7 자리에 뒤에서 넣고 뒤에서 레이저 용접.
"""

DRAWING_REV = "H"
DATE = "2026-09-30"

# ── 보호캡 = 두텍 SUS PROBE OIL FILTER (품번 390000-001100, 도면 2020-06-08, SUS304) ──
# 원 도면 좌표(끝 0 → 열린 끝 32)를 제품 x로: x = x_tip + xf. 열린 끝이 커넥터 플랜지 앞면(x=-30)에 닿음
# Rev G: Ø14 튜브를 없애고 HTX99R·보호캡·센서 프로브를 G½ 나사부 안쪽으로 19.5 mm 넣음 (캡 뿌리 3.5 mm를 나사부가 감쌈)
FRONT_SHIFT = 19.5
CAP_EXT = 5.5                     # Rev H: 캡을 끝 쪽으로 5.5 연장 → 노출 34 (EE364와 같음)
_CO = -62.0 + FRONT_SHIFT         # 원 도면(32 mm) 캡의 끝 위치 — 나사·센서실 뒤쪽은 이 기준
_CT = _CO - CAP_EXT
CAP = dict(
    part_no="390000-001100", src="DOTECH SUS PROBE / OIL FILTER dwg 2020-06-08 (A3 2:1)", material="SUS304",
    x_tip=_CT,            # 프로브 끝
    x_rear=-30.0 + FRONT_SHIFT,   # 열린 끝 = 커넥터 플랜지 앞면 (바디 칼라 바닥)
    od=12.0,
    chamfer=1.0,          # 끝 C1
    rear_relief=dict(x=(_CO + 31, _CO + 32), d=11.0),     # 열린 끝 1 mm Ø11
    tip_hole=3.0, tip_hole_depth=0.5,                     # 끝단 Ø3 (드릴 끝 원뿔로 Ø8 보어와 이어짐)
    bore=8.0, bore_x=(_CT + 3.0, _CO + 23.2),             # 센서실 Ø8
    thread="M10x1.0", thread_x=(_CO + 23.5, -30.0 + FRONT_SHIFT),       # 암나사 8.5 (도면 M10x1.0)
    thread_minor=8.917,
    hole_d=3.0,
    # 측면 구멍 Ø3: 5줄(원 끝 기준 1, 6, 11, 16, 21 — Rev H 연장부에 1줄 추가) × 5개(72° 간격)
    holes=[(_CO + xf, (270 + 72 * k) % 360) for xf in (1.0, 6.0, 11.0, 16.0, 21.0) for k in range(5)],
)
# 반단면 윤곽 (x, r): 바깥 끝 → 뒤 → 안쪽 → 끝 (닫힌 다각형)
CAP["profile"] = [
    (_CT, CAP["tip_hole"] / 2), (_CT, CAP["od"] / 2 - CAP["chamfer"]), (_CT + CAP["chamfer"], CAP["od"] / 2),
    (CAP["rear_relief"]["x"][0], CAP["od"] / 2), (CAP["rear_relief"]["x"][0], CAP["rear_relief"]["d"] / 2),
    (CAP["x_rear"], CAP["rear_relief"]["d"] / 2), (CAP["x_rear"], CAP["thread_minor"] / 2),
    (CAP["thread_x"][0], CAP["thread_minor"] / 2), (CAP["bore_x"][1], CAP["bore"] / 2),
    (CAP["bore_x"][0], CAP["bore"] / 2), (_CT + CAP["tip_hole_depth"], CAP["tip_hole"] / 2)]

# ── 센서 커넥터 HTX99R-SC (두텍 기존 부품, ref/ STEP) ──
# 커넥터 좌표 y(축) → 제품 x = CONN_X0 - y (소켓 면 y=15 이 프로브 끝 쪽)
SENSOR_CONN = dict(step="ref/HTX99R_Sensor_Probe_Sensor_Connector.STEP", x0=-22.0 + FRONT_SHIFT,
                   body_d=10.0, flange_d=11.0, flange_y=(7.0, 8.0), len=15.0, pin_y=-3.0,
                   oring_groove=dict(d=8.2, y=(5.5, 7.0)), socket_face_y=15.0, sock_depth=7.9,
                   thread_lower=dict(y=(0.5, 5.5), spec="M10x1.0"),    # → 바디 암나사 (두텍 확인 2026-09-30: 위·아래 모두 M10×1.0)
                   thread_upper=dict(y=(9.5, 15.0), spec="M10x1.0"),   # → 필터 캡 (390000-001100 도면 M10x1.0)
                   name="HTX99R sensor connector 4P (DOTECH)")
CONN_ORING = dict(id=8.0, cs=1.2, name="O-ring 8 x 1.2 FKM (connector seal in Ø10 H8)")

# ── 교체형 센서 프로브 (MK33-W mini + Pt1000 MiniSens) ──
SENSOR_PROBE = dict(plug=dict(x=(-39.5 + FRONT_SHIFT, -37.0 + FRONT_SHIFT), d=7.6),   # 필터 Ø8 센서실 안          # 수지 플러그 (PEEK)
                    pins=dict(x=(-37.0 + FRONT_SHIFT, -32.0 + FRONT_SHIFT), d=1.0, pitch=2.54),  # 소켓에 꽂히는 핀 4개 (규격 확인)
                    board=dict(x=(-46.3 + FRONT_SHIFT, -39.5 + FRONT_SHIFT), w=6.0, t=0.8),    # 센서 기판 (세라믹 또는 FR-4)
                    mk33=dict(l=5.0, w=3.81, t=0.4),              # IST MK33-W mini (150138)
                    pt1000=dict(l=1.6, w=1.2, t=0.5),             # IST MiniSens Pt1000 F0.1
                    name="Sensor probe insert: MK33-W mini + Pt1000, 4 pins")

# ── O링 (바디–하우징, 하우징–엔드캡 공통, 반경 방향 정적 밀봉) ──
# Rev H: Ø27 자리, 단면 1.5 (홈 바닥과 카운터보어 Ø22 사이 벽 1.3). 압축 20 %, 늘림 2.5 %
ORING = dict(id=24.0, cs=1.5, groove_d=24.6, groove_w=2.1, bore=27.0,
             name="O-ring 24 x 1.5, FKM 75 (radial static seal in Ø27 H8 bore)")

# ── 프로세스 바디 M-101 (SUS316L 일체 선삭) ──
BODY = dict(
    x_front=-30.0 + FRONT_SHIFT,   # 커넥터 자리 면 (= 캡 칼라 바닥). 바디 맨 앞면은 G½ 나사 시작 x −14
    # 캡 보호 칼라 (Rev G): Ø14 튜브 없음. G½ 나사부 안쪽을 Ø12.3 × 3.5 파서 보호캡 뿌리를 감쌈
    # → 캡이 상하좌우로 힘을 받으면 금속 바디가 받고 HTX99R(수지)에 굽힘이 안 감.
    # 깊이 3.5 = 캡 Ø11 릴리프 1 + Ø12 부분 2.5. HTX99R 맞변 7 평면과 0.5 떨어짐 (스패너 들어감)
    cap_sleeve=dict(x=(-14.0, -10.5), d=12.3),
    gthread=dict(x=(-14.0, -2.0), d=20.955, d_minor=18.631, thread="G1/2-A (ISO 228-1)"),
    relief=dict(x=(-2.0, 0.0), d=18.4),                              # 나사 언더컷
    hexa=dict(x=(0.0, 10.0), af=27.0, chamfer_angle=30),            # Rev H: 길이 10 (EE364)
    collar=dict(x=(10.0, 13.0), d=30.0),                            # 하우징 끝면이 닿는 칼라
    seal=dict(x=(13.0, 17.0), d=27.0, fit="f7", groove_x=(13.95, 16.05)),   # O링 자리
    mthread=dict(x=(17.0, 24.0), d=26.0, d_minor=24.917, thread="M26x1-6g"),  # 하우징 체결 수나사
    # 내부
    conn_cbore=dict(x=(-10.5, -9.5), d=11.2),                      # 커넥터 플랜지 자리
    conn_land=dict(x=(-9.5, -8.0), d=10.0, fit="H8"),              # O링 밀봉면 (커넥터 홈 Ø8.2)
    conn_thread=dict(x=(-8.0, -2.5), d=8.917, d_major=10.0, thread="M10x1.0-6H"),    # 커넥터 아래 나사 (M10×1.0, 골지름 8.917)
    channel=dict(x=(-2.5, 10.0), d=7.0),                             # 관통 — 센서 하네스 W-1만 지나감 (Rev H: 12.5 길이)
    cbore=dict(x=(10.0, 24.0), d=22.0),
    holder_taps=dict(n=2, d=2.0, depth=5.0, pcd=16.0, thread="M2-6H"),   # 홀더 고정 나사 (카운터보어 바닥 x=10)
)

# ── 하우징 M-103 ── (양 끝: O링 자리 Ø27 H8 → 암나사 M26x1 → 본체 내경 Ø25)
# 턴버클 체결: 앞(바디) M26x1 오른나사, 뒤(엔드캡) M26x1 왼나사 → 하우징만 돌리면 바디·엔드캡이 돌지 않고 당겨짐
# Rev H: Ø30 (EE364). 벽: 가운데 2.5, 나사 바깥 2.0, O링 자리 1.5. 하우징은 오일 압력을 받지 않음 (격벽 = 바디 통로 몰딩)
HOUSING = dict(x=(13.0, 73.0), od=30.0, id=25.0,
               seal_bore=27.0, seal_len=4.0, thread="M26x1-6H", thread_rear="M26x1-LH-6H",
               thread_d=26.0, thread_minor=24.917, thread_len=7.0)

# ── 엔드캡 M-104 ──
ENDCAP = dict(mthread=dict(x=(62.0, 69.0), d=26.0, d_minor=24.917, thread="M26x1-LH-6g"),   # 왼나사 (턴버클)
              seal=dict(x=(69.0, 73.0), d=27.0, fit="f7", groove_x=(69.95, 72.05)),
              flange=dict(x=(73.0, 77.0), d=30.0, flats_af=27.0),   # Rev H: 길이 4, 맞변 AF27 (육각과 같은 스패너)
              cbore=dict(x=(62.0, 71.0), d=22.0),                   # 경량화·리드선 공간
              thread=dict(x=(71.0, 77.0), d=16.0, d_minor=14.376, thread="M16x1.5-6H"),   # Rev H: 안쪽으로 2 (플랜지 4 + 2)
              ports=dict(r=10.0, angles=(90, 270), thread="M3", d_minor=2.5, plug="M3x3 set screw + sealant"))  # 몰딩 주입·공기 빠짐

# ── 구매품 (단순 형상) ──
SEAL = dict(x=(-2.0, 0.0), id=21.5, od=28.7, name="Bonded seal G1/2 (USIT/DIN 3869 type), steel + FKM")
# Ø7 관통 통로(pass-through)는 케이블을 넣은 뒤 전 길이를 에폭시로 몰딩 (1차 격벽, 두텍 지시)
# 압력 격벽: HTX99R O링 + 몰드 핀 → Ø7 × 34 에폭시 몰딩 (전선 매립). 피드스루 없음
POTTING = dict(x=(-2.5, 10.0), d=7.0, name="Epoxy molding, Ø7 x 12.5 channel (W-1 embedded)")
# 하우징 안 전체 몰딩 (2차, 같은 상온경화 에폭시): 바디 Ø22 카운터보어 + 하우징 Ø25 + 엔드캡 Ø22 (M12 뒤면까지)
POTTING2 = dict(zones=[(10.0, 24.0, 22.0), (24.0, 62.0, 25.0), (62.0, 69.0, 22.0)],
                material="상온경화 에폭시 1종 (통로·전자부 공통)", name="Epoxy potting, housing interior (electronics)")
# ── PCB E-301: 축 방향 1장, 축을 지나는 평면(z=0)에 세움. 폭은 y 방향 ──
# Rev H: 모양·배치 그대로, 위치만 x −2 (육각 10). KiCad 좌표 = (100 + x − PCB x0, 100 − y) 라 KiCad 파일은 변하지 않음
PCB = dict(t=1.6, x=(12.5, 69.0),
           sections=[(12.5, 24.0, 18.0),    # 바디 카운터보어 Ø22 안
                     (24.0, 61.4, 23.0),    # 하우징 Ø25 안 (끝 61.4: 턴버클 끝 엔드캡 앞면 x 62와 틈 0.6 — 조립 시뮬레이션 ③)
                     (61.4, 69.0, 18.0)],   # 엔드캡 카운터보어 Ø22 안
           corner_r=1.0,
           holes=[(14.25, 5.0), (14.25, -5.0)], hole_d=2.2,   # 홀더 가로 나사 M2 (x, y)
           # J3 센서 하네스 헤더: JST SH 1.0 mm 4P 옆 삽입(직각, SM04B-SRSS-TB), 윗면, 입구 = 앞(-x, 센서 쪽)
           jst=dict(x=(28.5, 32.5), y=(-3.5, 3.5), h=2.95, side=1,   # 홀더 뒤 12.5 mm: 꽂을 공간·여유 선
                    part="JST SM04B-SRSS-TB (SH 1.0 mm 4P, side entry, SMD)"),
           # J1 M12 하네스 헤더: JST GH 1.25 mm 8P 옆 삽입(직각, SM08B-GHS-TB), 윗면, 입구 = 뒤(+x, 커넥터 쪽)
           gh=dict(x=(50.5, 56.5), y=(-6.4, 6.4), h=4.25, side=1,
                   part="JST SM08B-GHS-TB (GH 1.25 mm 8P, side entry, SMD)"),
           zones=[("측정", "J3 · PCAP04 · ADS1220 · 기준 C", 16.0, 33.0),
                  ("MCU·전원", "STM32G0B1 · eFuse · 벅 · LDO", 33.0, 48.0),
                  ("출력·보호", "J1 · DAC8760×2 · TPS26611 · THVD2450", 48.0, 69.0)],
           name="PCB 57×23 4-layer, 1 board (E-301)")
# 표현용 주요 부품 (x, y, 가로, 세로, 높이, 면 +1/-1)
PCB_PARTS = [
    (32.5, 0.0, 4.0, 7.0, 2.95, 1),    # J3 JST SH 4P 헤더 (옆 삽입, 입구 -x) — 외형 개략
    (26.5, -5.5, 4.0, 4.0, 0.9, 1),    # PCAP04 QFN24 — J3 옆 (센서선 최단)
    (27.2, 5.5, 6.4, 5.0, 1.2, 1),     # ADS1220 TSSOP16 (가로 배치)
    (26.5, -5.5, 2.0, 1.25, 1.0, -1),  # 기준 C (C0G)
    (41.0, 0.0, 7.0, 7.0, 1.4, 1),     # STM32G0B1CCT3 LQFP48
    (38.0, 0.0, 5.0, 4.0, 1.0, -1),    # TPS2660 eFuse
    (45.0, 0.0, 4.0, 4.0, 3.0, -1),    # 벅 인덕터
    (41.0, 7.0, 3.0, 3.0, 1.0, -1),    # LMR36006
    (55.5, 0.0, 6.0, 12.8, 4.25, 1),   # J1 JST GH 8P 헤더 (옆 삽입, 입구 +x) — 외형 개략
    (48.5, 6.5, 7.0, 6.0, 2.4, 1),     # SMCJ TVS (입력 1단)
    (67.5, 0.0, 6.0, 6.0, 1.0, 1),     # DAC8760 #1 VQFN40
    (55.0, 0.0, 6.0, 6.0, 1.0, -1),    # DAC8760 #2
    (61.5, -4.5, 3.0, 3.0, 1.0, -1),   # TPS26611
    (61.5, 5.5, 5.0, 6.0, 1.7, -1),    # THVD2450 SOIC8
    (67.5, 0.0, 5.0, 4.0, 2.0, -1),    # CM 초크
]
PLACEMENT = __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)),
                                       "..", "kicad", "HMT500(260313A)", "placement.json")


def pcb_part_boxes():
    """PCB 부품 외형 (x, y, 가로, 세로, 높이, 면): KiCad 실제 배치(placement.json)가 있으면 그것, 없으면 PCB_PARTS 개략."""
    import json
    import os
    if not os.path.exists(PLACEMENT):
        return PCB_PARTS
    out = []
    with open(PLACEMENT, encoding="utf-8") as f:
        parts = json.load(f)["parts"]
    for p in parts:
        if p["h"] > 0:
            x0, y0, x1, y1 = p["fab"]
            out.append(((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, p["h"], 1 if p["side"] == "T" else -1))
    return out

PCB_HOLDER = dict(x=(10.2, 16.0), d=21.6, hole_d=6.0, slot_w=1.7, slot_x=(12.5, 16.0),   # Ø6: 하네스 W-1 전선 통과
                  # 창: PCB를 먼저 끼운 상태에서 W-1 플러그(5.0 × 2.8)가 지나가는 통로 (PCB 윗면 위, 조립 시뮬레이션 ①②)
                  window=dict(wy=5.6, z=(0.85, 4.05)),
                  # 축 나사 자리: Ø5.2 × 2.2 — 위쪽 나사는 샤시 선 M2 링 단자(바깥 Ø4.5, 두께 0.8)를 함께 조임
                  screw_pcd=16.0, screw_d=2.2, cbore_d=5.2, cbore_depth=2.2,
                  cross=dict(x=14.25, y=(5.0, -5.0), d=2.2, tap="M2"),
                  name="PCB holder (PEEK or PA66-GF30)")
# 샤시 접지 선: PCB J5 납땜 구멍 → AWG 28 PTFE → M2 링 단자 → 홀더 위쪽 축 나사 (금속 바디 탭). 스프링 접점 J5 대체
CHASSIS_WIRE = dict(pad=(17.5, 0.0), screw_z=8.0, length=25.0, wire="AWG 28 PTFE (UL1213 계열), 녹/황 또는 녹색",
                    terminal="M2 링 단자 (절연 없음, AWG 28–22, 바깥 Ø4.5 이하, 두께 0.8 이하)", screw="M2×8 (링 단자 쪽)")
# 조립 공구: W-2 플러그 밀대 (하우징 뒤 입구 → J1, 깊이 약 20 mm). 3D 프린트
PUSH_TOOL = dict(length=70.0, width=14.0, t=2.4, slot_w=10.4, slot_len=55.0, tip_w=12.4, tip_t=3.0, tip_len=4.0,
                 name="Assembly tool T-001: W-2 plug push bar (3D print, PA12 or resin)")
# Rev H: 바깥 Ø24.5 (하우징 Ø25, 나사 골지름 Ø24.917 통과). 홈 바닥 바깥 벽 0.65
PCB_RING = dict(x=(57.0, 61.0), od=24.5, id=20.0, slot_w=1.7, slot_y=11.6,
                name="PCB rear support ring (PEEK or PA66-GF30)")
# M12 하네스 W-2: J1 GH 플러그 (입구 +x) → 엔드캡 카운터보어 → M12 커넥터 뒤 핀 8개 (납땜 + 수축튜브)
HARNESS2 = dict(plug=dict(x=(56.5, 60.5), y=(-5.9, 5.9), z=(0.8, 4.3)),   # GHR-08V-S 꽂힌 상태 외형 (개략)
                wire_d=0.6, pitch=1.25, wire_z=3.3, conn_pcd=5.0, length=40.0,   # 40: 꽂을 때 약 35 필요 (조립 시뮬레이션 ⑥)
                housing="JST GHR-08V-S", contact="JST SSHL-002T-P0.2 ×8 (AWG 30–26)",
                wire="AWG 28 PTFE 절연 (UL1213 계열), 8심, 길이 40 ±2",
                name="Field harness W-2, JST GH 1.25 mm 8P → M12 8P (pin n = pin n)")
# 센서 하네스 W-1: HTX99R 뒤 핀 4개 (납땜) → Ø7 관통 통로 (에폭시 몰딩) → JST SH 플러그 → PCB J3
HARNESS = dict(plug=dict(x=(24.5, 28.5), y=(-2.5, 2.5), z=(0.8, 3.6)),   # SHR-04V-S 꽂힌 상태 외형 (개략), J3 앞
               wire_d=0.6, pitch=1.0, gap_z=2.2, length=40.0,   # Rev G: 통로 34 → 14.5로 줄어 60 → 40 (Rev H 통로 12.5) (창에 꿸 때 36 필요)         # 홀더 구멍에서 곧게 플러그 뒤로
               pins=[("1", "SENS_C1", "MK33 전극 1"), ("2", "SENS_C2", "MK33 전극 2"),
                     ("3", "PT_P", "Pt1000 +"), ("4", "PT_N", "Pt1000 −")],
               conn_grid=2.54,              # HTX99R 뒤 핀 4개 (2.54 격자, 핀 끝 x = x0 - pin_y)
               housing="JST SHR-04V-S", contact="JST SSH-003T-P0.2-H ×4 (AWG 32–28)",
               wire="AWG 30 PTFE 절연 (UL1213 계열, 200 °C), 4심, 길이 40 ±2",
               name="Sensor harness W-1, JST SH 1.0 mm 4P")
CONNECTOR = dict(body=dict(x=(77.0, 81.0), d=20.0), thread=dict(x=(81.0, 92.0), d=12.0),
                 inner=dict(x=(71.0, 77.0), d=15.9),   # Rev H: 나사부 ≤ 6 (엔드캡 M16 길이) — 품번 선정 조건. PCB 뒤 끝 x 69와 틈 2
                 name="M12 8P male (M Connect), front mount M16x1.5 (P/N TBD)")

TIP_X = CAP["x_tip"]
END_X = CONNECTOR["thread"]["x"][1]
OVERALL = END_X - TIP_X


def hex_corner_d(af):
    return af / 0.8660254


# 부품 목록 (조립도 부품표)
PARTS = [
    ("1", "HMT500-M-101", "Process body", "SUS316L (1.4404)", 1, "Machined"),
    ("2", "HMT500-M-102", "Sensor cap (ex 390000-001100)", "SUS304", 1, "Machined, M10x1.0, 25 holes"),
    ("3", "HMT500-M-103", "Housing tube Ø30", "SUS316L (1.4404)", 1, "Machined, M26x1 R/LH ends, marking"),
    ("4", "HMT500-M-104", "End cap", "SUS316L (1.4404)", 1, "Machined, flats AF27"),
    ("5", "HMT500-P-209", "Epoxy, RT cure (1 type)", "Epoxy (TBD)", 1, "Pour 1: Ø7 channel / 2: interior"),
    ("6", "HMT500-P-202", "Sensor probe: MK33-W mini + Pt1000", "PEEK + ceramic", 1, "Plug-in, replaceable"),
    ("7", "HMT500-P-203", "Bonded seal G1/2", "Steel + FKM", 1, "Purchased"),
    ("8", "HMT500-E-301", "PCB assembly 57x23 (1 board)", "FR-4", 1, "See KiCad HMT500(260313A)"),
    ("9", "HMT500-P-204", "M12 8P male (M Connect), M16x1.5", "-", 1, "Front mount, leads → W-2, P/N TBD"),
    ("10", "HMT500-P-205", "O-ring 24 x 1.5", "FKM 75", 2, "1-3 and 3-4 seal"),
    ("11", "HMT500-P-206", "O-ring for connector", "FKM", 1, "Per connector spec"),
    ("12", "HMT500-M-105", "PCB holder", "PEEK / PA66-GF30", 1, "Machined or molded"),
    ("13", "HMT500-M-106", "PCB rear support ring", "PEEK / PA66-GF30", 1, "Machined or molded"),
    ("14", "HMT500-P-207", "Screw M2x6 + M2x8 + M2x12 (2)", "A4 stainless", 4, "ISO 14580 / 7380"),
    ("15", "HTX99R-SC", "Sensor connector 4P, M10x1.0 x2", "per DOTECH dwg", 1, "In-house, screwed into 1"),
    ("16", "HMT500-P-208", "O-ring 8 x 1.2", "FKM 75", 1, "Connector seal"),
    ("17", "HMT500-W-1", "Sensor harness, JST SH 1.0 4P", "PTFE AWG30", 1, "15 → J3 on 8, L40"),
    ("18", "HMT500-W-2", "Field harness, JST GH 1.25 8P", "PTFE AWG28", 1, "9 → J1 on 8, L40"),
    ("19", "HMT500-P-210", "Set screw M3x3 + sealant", "A4 stainless", 2, "Fill / vent ports in 4"),
    ("20", "HMT500-W-3", "Chassis wire + M2 ring terminal", "PTFE AWG28", 1, "8 J5 → 12 top screw, L25"),
]
