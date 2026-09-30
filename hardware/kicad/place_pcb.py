"""HMT500(260313A) PCB 부품 배치 (배선 전 승인용).

  python3 hardware/kicad/place_pcb.py
    → HMT500(260313A)/HMT500(260313A).kicad_pcb   (외곽선·금지 구역 + 부품 84개, 넷 지정, 배선 없음)
    → HMT500(260313A)/placement.json               (배치 결과: 기구 좌표 — 조립 시뮬레이션·그림용)

좌표는 기구 좌표(x 축 방향 뒤쪽 +, y 폭 방향, z 윗면 +)로 계산하고 KiCad 좌표로 바꿔 넣는다 (gen_pcb_outline.K).
윗면 = F (z+), 아랫면 = B.

배치 방법: 고정 부품(J3·J1·U4)을 먼저 놓고, 나머지는 표 PLAN 순서대로
"기준점(부모 부품의 같은 넷 패드) 가까운 빈 자리"를 0.25 mm 격자에서 찾는다.
자리 조건 = 보드 안(가장자리 0.3 mm), 홀더 홈·지지링 홈 금지 구역, 하네스 플러그·전선 통로(윗면),
높이 한계(보어 − 판 두께/2 − 0.5 mm), 같은 면 코트야드 겹침 없음(J2 Tag-Connect는 구멍 때문에 양면).
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("HMT_DRAFT", "1")

import pcbnew  # noqa: E402

import gen_hmt500 as G  # noqa: E402
import gen_pcb_outline as O  # noqa: E402

P = O.P
LIB = os.path.join(HERE, "lib", "HMT500_260313A.pretty")
OUT = O.OUT
JSON_OUT = os.path.join(os.path.dirname(OUT), "placement.json")
MM, TOMM = pcbnew.FromMM, pcbnew.ToMM

EDGE = 0.25          # 코트야드 ~ 보드 가장자리
GAP = 0.1            # 코트야드 사이
STEP = 0.25          # 탐색 격자
SLACK = 1.5          # 기준점 거리 여유 (이 안에서 붙는 자리 우선)
TOUCH = 0.6          # 붙은 면 하나당 가점 (mm)

# ── 부품 높이 (mm, 데이터시트 최대값) — 풋프린트 이름으로 ──
HEIGHT = {
    "JST_GH_SM08B": 4.25, "JST_SH_SM04B": 2.95, "SpringContact_Harwin_S1941-46R": 7.25,
    "L_CommonMode_Wuerth_WE-SL2": 5.3, "GDT_Bourns_2035": 5.0, "L_Coilcraft_XAL4030": 3.1,
    "L_Coilcraft_XAL4040": 4.0,   # v0.9 LCSC: L1 SRF0905 5.3, L2 XGL4040 4.0
    "C_1210": 2.5, "D_SMC": 2.62, "D_SMB": 2.3, "R_MELF_MMB-0207": 2.2, "C_1812": 2.0,
    "C_1206": 1.8, "SOIC-8": 1.75, "LQFP-48": 1.6, "SOT-23": 1.45, "HTSSOP": 1.2, "TSSOP": 1.2,
    "C_0805": 1.35, "VSSOP": 1.0, "Texas_DRB": 1.0, "Texas_RNX": 1.0, "QFN-24": 0.9,
    "R_2512": 0.7, "_0603_": 0.95, "Tag-Connect": 0.0, "SolderWire": 0.0,
    "R_1206": 0.7,
}


def height(fp):
    for k, h in HEIGHT.items():
        if k in fp:
            return h
    raise KeyError(fp)


# ── 기구 조건 ──
X0, X1 = P.PCB["x"]
# 아래 배치 계획·하네스 통로의 x 값은 Rev G 기구 좌표(PCB 앞 끝 x 14.5) 기준. Rev H(육각 10)에서 PCB가 x −2 → DX로 옮김.
# KiCad 좌표는 PCB 앞 끝 기준이라 변하지 않는다.
DX = X0 - 14.5
SLOT_X1 = P.PCB_HOLDER["slot_x"][1]                  # 18.0
RING = P.PCB_RING
RING_KO = (RING["x"][0] - 0.3, RING["x"][1] + 0.3, RING["id"] / 2 - 0.3)   # x0, x1, |y| 한계
# 윗면 하네스 통로 (x0, x1, |y| 한계, 허용 부품 높이 — None = 부품 금지)
#  - 플러그 몸체 + 꽂는 거리·잡는 공간(약 4 mm)은 완전히 비움
#  - 전선만 지나가는 곳은 낮은 부품 허용: W-1 선 중심 z 2.2, 굵기 0.6 → 선 아래 1.9 → 부품 ≤ 1.0 (여유 0.9)
#    W-2는 턴버클로 엔드캡이 14 mm 다가오며 남는 선(약 29 mm)이 플러그 뒤에서 접히므로 J1 뒤는 전부 비움
HARNESS_BANDS = [
    (X0, 22.5 + DX, 3.5, 1.0),             # W-1 선 (홀더 구멍 → 플러그)
    (22.5 + DX, 30.5 + DX, 3.5, None),     # W-1 플러그(Rev G x 26.5–30.5) + 꽂는 거리·잡는 공간
    (58.5 + DX, X1, 6.4, None),         # W-2 플러그(x 58.5–62.5) + 잡는 공간 + 남는 선이 접히는 곳 (조립 시뮬레이션 ⑥)
]


def half_width(xa, xb):
    """x 구간 전체에서 보드 반폭."""
    return min(w / 2 for (s0, s1, w) in P.PCB["sections"] if xb > s0 and xa < s1)


def corners_convex():
    """볼록 모서리(필렛 R) 중심들: 앞·뒤 끝 4개 + 넓은 구간의 계단 4개."""
    r = P.PCB["corner_r"]
    out = []
    secs = P.PCB["sections"]
    for i, (s0, s1, w) in enumerate(secs):
        h = w / 2
        wl = secs[i - 1][2] / 2 if i > 0 else 0.0
        wr = secs[i + 1][2] / 2 if i + 1 < len(secs) else 0.0
        if h > wl:
            out += [(s0 + r, h - r), (s0 + r, -(h - r))]
        if h > wr:
            out += [(s1 - r, h - r), (s1 - r, -(h - r))]
    return out


CORNERS = corners_convex()


def corners_concave():
    """오목 모서리(계단 안쪽) 필렛 중심: 필렛이 보드 재료를 더하므로 가장자리가 부품 쪽으로 나온다."""
    r = P.PCB["corner_r"]
    out = []
    secs = P.PCB["sections"]
    for i in range(len(secs) - 1):
        (a0, a1, wa), (b0, b1, wb) = secs[i], secs[i + 1]
        x = a1
        if wa < wb:          # 좁음 → 넓음: 안쪽 모서리 (x, wa/2), 필렛 중심은 좁은 쪽 바깥
            out += [(x - r, wa / 2 + r), (x - r, -(wa / 2 + r))]
        elif wa > wb:
            out += [(x + r, wb / 2 + r), (x + r, -(wb / 2 + r))]
    return out


CONCAVE = corners_concave()


def corner_ok(box):
    r = P.PCB["corner_r"] - EDGE
    xa, ya, xb, yb = box
    for (cx, cy) in CORNERS:
        for (px, py) in ((xa, ya), (xa, yb), (xb, ya), (xb, yb)):
            # 필렛 중심 바깥쪽 사분면에 있는 꼭짓점만 검사
            if (px - cx) * (1 if cx > 40 else -1) > 0 and (py - cy) * (1 if cy > 0 else -1) > 0:
                if math.hypot(px - cx, py - cy) > r:
                    return False
    rr = P.PCB["corner_r"] + EDGE
    for (cx, cy) in CONCAVE:
        dx = max(xa - cx, 0.0, cx - xb)
        dy = max(ya - cy, 0.0, cy - yb)
        if math.hypot(dx, dy) < rr:
            return False
    return True


def bore(x):
    """부품이 지나가거나 놓이는 가장 좁은 안지름.
    링(안지름 Ø20)은 PCB 뒤 끝(x 71)부터 끼워 x 59–63까지 가므로 x ≥ 59 부품은 모두 Ø20 안 (조립 시뮬레이션 ④)."""
    if x < P.BODY["cbore"]["x"][1]:
        return P.BODY["cbore"]["d"]            # 22
    if x >= RING["x"][0]:
        return RING["id"]                      # 20
    return min(P.HOUSING["id"], P.HOUSING["thread_minor"])   # Rev H: 25 / 나사 골지름 24.917 (하우징이 PCB 위로 지나감)


def h_allow(xa, xb, ymax):
    b = min(bore(x) for x in (xa, (xa + xb) / 2, xb, *[x for x in (P.BODY["cbore"]["x"][1], RING["x"][0], RING["x"][1], P.ENDCAP["mthread"]["x"][0])
                                               if xa <= x <= xb]))
    r = b / 2
    return -1.0 if ymax >= r else math.sqrt(r * r - ymax * ymax) - P.PCB["t"] / 2 - 0.5


def region_ok(side, box, h, check_h=True):
    xa, ya, xb, yb = box
    if xa < SLOT_X1 + EDGE or xb > X1 - EDGE:
        return False
    hw = half_width(xa, xb) - EDGE
    if ya < -hw or yb > hw or not corner_ok(box):
        return False
    if xb > RING_KO[0] and xa < RING_KO[1] and (ya < -RING_KO[2] or yb > RING_KO[2]):
        return False
    if side == "T":
        for (a, b, w, hmax) in HARNESS_BANDS:
            if xb > a and xa < b and yb > -w and ya < w and (hmax is None or h > hmax):
                return False
    if check_h and h > h_allow(xa, xb, max(abs(ya), abs(yb))):
        return False
    return True


OFFSETS = sorted((math.hypot(i * STEP, j * STEP), i * STEP, j * STEP)
                 for i in range(-160, 161) for j in range(-100, 101))


def overlap(a, b, gap=GAP):
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


# ── KiCad ↔ 기구 좌표 ──
def to_k(x, y):
    return pcbnew.VECTOR2I(MM(O.OX + (x - O.F0)), MM(O.OY - y))


def from_k(v):
    return (TOMM(v.x) - O.OX + O.F0, O.OY - TOMM(v.y))


def layer_box(fp, layers):
    xs, ys = [], []
    for it in fp.GraphicalItems():
        if it.GetLayer() in layers and not isinstance(it, pcbnew.FP_TEXT):
            b = it.GetBoundingBox()
            (x0, y0), (x1, y1) = from_k(pcbnew.VECTOR2I(b.GetLeft(), b.GetBottom())), \
                from_k(pcbnew.VECTOR2I(b.GetRight(), b.GetTop()))
            xs += [x0, x1]
            ys += [y0, y1]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def set_pose(fp, side, x, y, rot):
    if fp.IsFlipped():
        fp.Flip(fp.GetPosition(), False)
    fp.SetOrientationDegrees(0)
    fp.SetPosition(to_k(x, y))
    fp.SetOrientationDegrees(rot)
    if side == "B":
        fp.Flip(fp.GetPosition(), False)      # 위아래 뒤집기 (KiCad 기본)


# ── 부품·넷 ──
PARTS = {}          # ref -> dict(fp, val, nets)
for S in G.SHEETS:
    for ref in S.order:
        if ref.startswith("#"):
            continue
        p = S.parts[ref]
        PARTS[ref] = dict(fp=p["fp"], val=p["val"], nets=dict(S.nets.get(ref, {})))


# ── 배치 계획 ──
# (ref, 면, 기준) — 기준: (x, y) 고정 좌표 | ("near", 부모, 넷) | ("pin", 부모, 핀번호) | ("at", x, y) 탐색 시작점
# 면 "T"/"B", "TB" = 윗면 우선·안 되면 아랫면, "BT" 반대. rots: 허용 회전.
PLAN = [
    # ── 고정: 하네스 헤더 두 개, MCU ──
    ("J3", "T", ("fix", None, None), dict(rot=-90)),
    ("J1", "T", ("fix", None, None), dict(rot=90)),
    ("U4", "T", ("fix", 42.8, 0.0), dict(rot=0)),
    # ════ 윗면: 큰 부품 자리 (코트야드 크기로 계산한 칸) ════
    ("J5", "T", ("at", 18.8, 7.4), {}),                      # 샤시 선 구멍: 홀더 위 축 나사(y 0, z 8) 바로 뒤 (조립 시뮬레이션 ⑤ → D안)
    ("J2", "T", ("at", 20.4, 0.0), dict(rots=(90,))),       # SWD Tag-Connect: 높이 0 → W-1 선 아래 (프로그래밍은 하네스 꽂기 전). 구멍 3개는 아랫면도 막음
    ("D40", "T", ("at", 50.15, 2.08), dict(rots=(0,))),     # 출력 TVS: J1 OUT 핀 바로 앞 (서지 경로 최단)
    ("D30", "T", ("at", 50.15, -2.08), dict(rots=(0,))),
    ("R40", "T", ("at", 54.75, 9.3), dict(rots=(0,))),      # 10R 2512: J1 옆구리
    ("R30", "T", ("at", 54.75, -9.3), dict(rots=(0,))),
    ("U11", "T", ("at", 46.75, -8.4), dict(rots=(0, 180))), # RS-485: J1 A/B 핀·MCU USART 핀 사이
    ("U14", "T", ("at", 49.6, 8.6), {}),                    # DAC SCLK 게이트: MCU SPI2 핀 옆 윗면
    ("C36", "T", ("near", "U14", "+3V3"), {}),
    # LDO + 페라이트 (앞쪽 윗면 — +3V3A 를 측정부에 바로)
    ("U3", "T", ("at", 23.0, 6.0), {}),
    ("C26", "T", ("near", "U3", "+5V"), {}),
    ("C12", "T", ("near", "U3", "+3V3"), {}),
    ("FB1", "T", ("near", "U3", "+3V3"), {}),
    ("C13", "T", ("near", "FB1", "+3V3A"), {}),
    # 측정 (J3 옆 — 센서선 최단)
    ("U5", "T", ("near", "J3", "SENS_C1"), {}),
    ("U6", "T", ("near", "J3", "PT_P"), {}),
    ("C22", "T", ("near", "U5", "CREF_A"), {}),
    ("C25", "T", ("near", "U5", "CDC_V18"), {}),
    ("C29", "T", ("near", "U5", "+3V3A"), {}),
    ("R17", "T", ("near", "U6", "PT_SP_F"), {}),
    ("R18", "T", ("near", "U6", "PT_SN_F"), {}),
    ("C27", "T", ("near", "U6", "PT_SP_F"), {}),
    ("R19", "T", ("near", "U6", "REF_N"), {}),
    ("R20", "T", ("near", "R19", "REF_N"), {}),
    ("C23", "T", ("near", "U6", "+3V3A"), {}),
    ("C28", "T", ("near", "U6", "+3V3"), {}),
    ("C24", "T", ("near", "U5", "+3V3A"), {}),
    # 출력 TVS 옆 C, MCU 주변, RS-485 C
    ("C41", "T", ("near", "D30", "OUT1_EXT"), {}),
    ("C51", "T", ("near", "D40", "OUT2_EXT"), {}),
    ("C18", "T", ("near", "U4", "+3V3"), {}),
    ("C21", "T", ("near", "U4", "NRST"), {}),
    ("C60", "T", ("near", "U11", "+3V3"), {}),
    ("R33", "T", ("near", "U4", "DAC_ALARM"), {}),
    # ════ 아랫면: 큰 부품 자리 ════
    # 입력 보호·샤시 (뒤쪽: J1 VIN/GND 아래 → 링·엔드캡 구역)
    ("L1", "B", ("at", 61.07, 0.0), dict(rots=(90,))),      # 링 구역 가운데 (높이 5 → |y| ≤ 7.7)
    ("D1", "B", ("at", 54.28, 6.28), dict(rots=(90,))),
    ("R1", "B", ("at", 66.01, 4.93), dict(rots=(90, 0))),  # 엔드캡 구역 (v0.9 LCSC: MELF → 2512)

    # 전류 출력 DAC 2개 (가운데 — 발열을 센서 쪽에서 멀리)
    # v0.9: DAC(최악 0.73 W씩)를 측정부(PCAP04·ADS1220 윗면 x 29–37) 밑에서 뒤쪽으로
    ("U7", "B", ("at", 46.5, -6.6), dict(rots=(0, 180))),
    ("U8", "B", ("at", 46.5, 6.6), dict(rots=(180,))),      # U7과 대칭: ISET·REF 핀(13·14)이 안쪽 → R42·C50 핀 옆
    # v0.9: DAC 핀에 붙어야 하는 부품 (ISET-R, REF C, AVDD R·C, +3V3 C) — DAC 다음 바로
    ("R32", "B", ("pin", "U7", "13"), {}),
    ("C40", "B", ("pin", "U7", "14"), {}),
    ("R42", "B", ("pin", "U8", "13"), {}),
    ("C50", "B", ("pin", "U8", "14"), {}),
    ("C44", "B", ("pin", "U7", "2"), {}),
    ("C54", "B", ("pin", "U8", "2"), {}),
    ("R34", "B", ("near", "U7", "DAC1_AVDD"), {}),
    ("C42", "B", ("near", "U7", "DAC1_AVDD"), {}),
    ("R44", "B", ("near", "U8", "DAC2_AVDD"), {}),
    ("C52", "B", ("near", "U8", "DAC2_AVDD"), {}),
    ("C43", "B", ("near", "U7", "DAC1_AVDD"), {}),
    # v0.9: MCU 전원 핀 4–7 디커플링 — 윗면은 J3 하네스 통로라 바로 아래 아랫면 (비아 1개 거리)
    ("C14", "BT", ("pin", "U4", "4"), {}),
    ("C20", "BT", ("pin", "U4", "5"), {}),
    ("C15", "BT", ("pin", "U4", "6"), {}),
    # eFuse: 방열 비아 → 윗면에도 RTN 동박 패드가 생김 → 윗면 부품이 없는 J3 플러그 통로 바로 아래
    ("U1", "B", ("at", 26.6, 0.0), dict(rots=(0, 180))),
    # v0.9: 입력 2단 TVS·입력 C는 eFuse IN 옆 (SLVSDG2G 11.1·12.1)
    ("D2", "B", ("near", "U1", "VIN_F"), dict(rots=(0, 90, 180, 270))),
    ("C2", "B", ("near", "U1", "VIN_F"), {}),
    ("C1", "B", ("near", "U1", "VIN_F"), {}),
    # 벅·LDO (앞쪽 — +3V3A 를 측정부 가까이, 발열 적음)
    ("U2", "B", ("at", 21.5, 4.5), dict(rots=(180,))),   # BOOT·VCC 핀(4·5)이 J5 금지 구역 반대쪽 → C8·C9 핀 옆
    # v0.9: 벅 입력 220 nF·BOOT·VCC 콘덴서를 U2 핀에 먼저 (SNVSB48C 11.1)
    ("C16", "B", ("pin", "U2", "10"), {}),
    ("C17", "B", ("pin", "U2", "2"), {}),
    ("C5", "B", ("near", "U2", "VIN_P"), {}),              # 벌크 CIN (eFuse 출력 겸용)
    ("C8", "B", ("pin", "U2", "4"), {}),
    ("C9", "B", ("pin", "U2", "5"), {}),
    # v0.9 재검토: 샤시 부품은 벅 핀 콘덴서 직후에 J5 옆 자리를 먼저 차지 (MCU·측정부에서 떨어뜨림)
    ("GDT1", "TB", ("near", "J5", "CHASSIS"), {}),
    ("C3", "TB", ("near", "J5", "CHASSIS"), {}),
    ("R2", "TB", ("near", "J5", "CHASSIS"), {}),
    ("L2", "B", ("near", "U2", "BUCK_SW"), {}),
    ("C10", "B", ("near", "L2", "+5V"), {}),
    ("C6", "B", ("near", "L2", "+5V"), {}),
    ("R8", "B", ("near", "U2", "BUCK_FB"), {}),
    ("R9", "B", ("near", "U2", "BUCK_FB"), {}),
    ("C11", "B", ("near", "R8", "BUCK_FB"), {}),
    # eFuse 분압·설정 부품
    ("C7", "B", ("near", "U1", "VIN_P"), {}),
    ("R3", "B", ("near", "U1", "UV_DIV"), {}),
    ("R4", "B", ("near", "U1", "OV_DIV"), {}),
    ("R5", "B", ("near", "U1", "OV_DIV"), {}),
    ("R6", "B", ("near", "U1", "EF_ILIM"), {}),
    ("C4", "B", ("near", "U1", "EF_DVDT"), {}),
    # 샤시 부품: 접지선 구멍 J5 옆 (서지가 GDT → 샤시로 바로). 앞쪽 전원부 다음에 남는 자리
    # v0.9: 샤시 부품은 J5 바로 옆 (선–대지 서지가 측정부를 지나지 않게, 검토 D2)
    # 벅 입력 C: VIN–PGND 핀 바로 옆 (SNVSB48C 9.2.1.2.6), LDO 입력 C
    # 출력 스위치·센스 앰프 (DAC 뒤 → R30/R40 쪽)
    ("U9", "B", ("near", "U7", "DAC1_OUT"), {}),
    ("U10", "B", ("near", "U8", "DAC2_OUT"), {}),
    ("U12", "B", ("near", "U7", "DAC1_SENSE"), {}),
    ("U13", "B", ("near", "U8", "DAC2_SENSE"), {}),
    ("C45", "B", ("near", "U12", "DAC1_AVDD"), {}),
    ("C55", "B", ("near", "U13", "DAC2_AVDD"), {}),
    # v0.9: TPS26611 +Vs 클램프 (+Vs 핀 옆 100n)
    ("C46", "B", ("near", "U9", "VS_CLAMP"), {}),
    ("C56", "B", ("near", "U10", "VS_CLAMP"), {}),
    ("Q1", "B", ("near", "C46", "VS_CLAMP"), {}),        # 이미터 폴로워 (VS_CLAMP = 이미터)
    ("C53", "B", ("near", "Q1", "VS_CLAMP"), {}),
    ("R50", "B", ("near", "Q1", "VS_BASE"), {}),
    ("D50", "B", ("near", "Q1", "VS_BASE"), {}),
    ("R31", "B", ("near", "U12", "OUT1_SNS"), {}),
    ("R41", "B", ("near", "U13", "OUT2_SNS"), {}),
    # v0.9: 풀업·감시·RS-485 DE 풀다운
    ("R60", "TB", ("near", "U11", "RS485_DE"), {}),
    ("R10", "TB", ("near", "U14", "DAC1_LATCH"), {}),
    ("R11", "TB", ("near", "U14", "DAC2_LATCH"), {}),
    ("R12", "TB", ("near", "U6", "CS_ADC"), {}),
    ("R13", "TB", ("near", "U5", "CS_CDC"), {}),
    ("R14", "TB", ("near", "U4", "VIN_SENSE"), {}),
    ("R15", "TB", ("near", "R14", "VIN_SENSE"), {}),
    ("C30", "TB", ("near", "R14", "VIN_SENSE"), {}),
]

# 하네스 헤더 고정: 몸체 앞면(J3) / 뒷면(J1)을 기구 도면 값에 맞춘다
J3_FRONT = P.PCB["jst"]["x"][0]         # 30.5 — 플러그가 앞(-x)에서 꽂힘
J1_REAR = P.HARNESS2["plug"]["x"][0]     # 58.5 — 플러그가 뒤(+x)에서 꽂힘


UNPLACED = []
CHASSIS_PARTS = {"GDT1", "C3", "R2"}     # v0.9: 샤시 부품 ~ 회로 부품 코트야드 0.5 mm (+ 넷클래스 CHASSIS 동박 간격 1.0 — 에폭시 몰딩 안, 검토 D2)
CH_GAP = 0.5
J5_KO = 3.3          # J5 구멍 중심 ~ 다른 부품 코트야드 (양면). 패드 Ø1.6 + 코트야드 여유 → 코트야드 간격 ≥ 2 mm (재검토)

# 4층 기판 설계 규칙 (일반 4층 공정: 선폭·간격 0.1 mm 급, 최소 드릴 0.2 mm 가능 — 여유 두고 설정)
#  - 간격 0.15: SOT-23-8(0.65 피치) 패드 사이 0.15, TPS2660 방열 비아 드릴 0.2
RULES = dict(min_through_hole_diameter=0.2, min_via_diameter=0.4, min_hole_clearance=0.2,
             min_copper_edge_clearance=0.3)
NETCLASS = dict(clearance=0.15, track_width=0.15, via_diameter=0.45, via_drill=0.2)
CHASSIS_CLASS = dict(clearance=1.0, track_width=0.5, via_diameter=0.8, via_drill=0.4)


def set_rules(pro_path, keep):
    """pcbnew 저장이 .kicad_pro 를 기본값으로 다시 쓰므로: 회로도 시트 목록을 되살리고 설계 규칙을 넣는다."""
    pro = json.load(open(pro_path))
    pro["sheets"] = keep.get("sheets", pro.get("sheets", []))
    pro["board"]["design_settings"]["rules"].update(RULES)
    ns = pro["net_settings"]
    for c in ns["classes"]:
        if c["name"] == "Default":
            c.update(NETCLASS)
    # v0.9: 샤시 넷은 다른 넷과 1.0 mm (몰딩 안), 선폭 0.5 (서지 전류, 검토 D2)
    base = next(c for c in ns["classes"] if c["name"] == "Default")
    ns["classes"] = [c for c in ns["classes"] if c["name"] != "CHASSIS"] + [dict(base, name="CHASSIS", **CHASSIS_CLASS)]
    ns["netclass_patterns"] = [p_ for p_ in ns.get("netclass_patterns") or [] if p_.get("netclass") != "CHASSIS"] + \
        [{"netclass": "CHASSIS", "pattern": "CHASSIS"}]
    open(pro_path, "w").write(json.dumps(pro, indent=2) + "\n")


def build():
    open(OUT, "w", encoding="utf-8").write(O.build())
    board = pcbnew.LoadBoard(OUT)
    nets = {}
    for ref, p in PARTS.items():
        for n in p["nets"].values():
            if n and n not in nets:
                ni = pcbnew.NETINFO_ITEM(board, n)
                board.Add(ni)
                nets[n] = ni

    placed = {}     # ref -> dict(side, x, y, rot, crt, fab, fp)

    scratch = pcbnew.BOARD()          # 뒤집기(Flip)는 보드에 올린 풋프린트만 가능

    def make(ref, tmp=False):
        p = PARTS[ref]
        fp = pcbnew.FootprintLoad(LIB, p["fp"].split(":")[1])
        (scratch if tmp else board).Add(fp)
        if tmp:
            return fp
        fp.SetFPID(pcbnew.LIB_ID(*p["fp"].split(":")))
        fp.SetReference(ref)
        fp.SetValue(p["val"])
        for pad in fp.Pads():
            n = p["nets"].get(pad.GetNumber())
            if n:
                pad.SetNet(nets[n])
        return fp

    def crt(fp):
        return layer_box(fp, (pcbnew.F_CrtYd, pcbnew.B_CrtYd))

    def pad_xy(ref, net):
        fp = placed[ref]["fp"]
        pts = [from_k(pd.GetPosition()) for pd in fp.Pads() if PARTS[ref]["nets"].get(pd.GetNumber()) == net]
        return (sum(a for a, _ in pts) / len(pts), sum(b for _, b in pts) / len(pts))

    def pin_xy(ref, num):
        pts = [from_k(pd.GetPosition()) for pd in placed[ref]["fp"].Pads() if pd.GetNumber() == num]
        return pts[0]

    def holes(fp):
        """관통 구멍(NPTH/PTH) → 반대 면도 막는 사각형들 (구멍 + 0.3)."""
        out = []
        for pd in fp.Pads():
            if pd.GetAttribute() in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_PTH):
                (x, y), r = from_k(pd.GetPosition()), TOMM(max(pd.GetSize().x, pd.GetSize().y)) / 2 + 0.3
                out.append((x - r, y - r, x + r, y + r))
        return out

    def free(side, box, ref, own_holes=()):
        if "J5" in placed and ref != "J5":            # v0.9: 샤시 선 납땜 구멍 둘레 양면 금지 (손납땜 브리지 방지)
            j = placed["J5"]
            dx_ = max(box[0] - j["x"], 0.0, j["x"] - box[2])
            dy_ = max(box[1] - j["y"], 0.0, j["y"] - box[3])
            if math.hypot(dx_, dy_) < J5_KO:
                return False
        for r, q in placed.items():
            g_ = CH_GAP if (r in CHASSIS_PARTS) != (ref in CHASSIS_PARTS) else GAP
            if q["side"] == side and overlap(box, q["crt"], g_):
                return False
            if q["side"] != side and any(overlap(box, hb, 0.0) for hb in q["holes"]):
                return False
            if q["side"] != side and any(overlap(hb, q["crt"], 0.0) for hb in own_holes):
                return False
        return True

    def commit(ref, fp, side, x, y, rot):
        placed[ref] = dict(side=side, x=x, y=y, rot=rot, crt=crt(fp), holes=holes(fp),
                           fab=layer_box(fp, (pcbnew.F_Fab, pcbnew.B_Fab)), fp=fp)

    # 부품 중심 → 코트야드 (면·회전별) 캐시
    shape = {}

    def local_box(ref, side, rot):
        k = (PARTS[ref]["fp"], side, rot)
        if k not in shape:
            fp = make(ref, tmp=True)
            set_pose(fp, side, 0.0, 0.0, rot)
            shape[k] = (crt(fp), holes(fp))
        return shape[k]

    for ref, sides, how, opt in PLAN:
        fp = make(ref)
        h = height(PARTS[ref]["fp"])
        if how[0] == "fix":
            side, rot = sides, opt["rot"]
            if ref in ("J3", "J1"):
                set_pose(fp, side, 0.0, 0.0, rot)
                fab = layer_box(fp, (pcbnew.F_Fab,))
                x = J3_FRONT - fab[0] if ref == "J3" else J1_REAR - fab[2]
                y = 0.0
            else:
                x, y = how[1] + DX, how[2]
            set_pose(fp, side, x, y, rot)
            assert free(side, crt(fp), ref), ref
            if ref == "U4":                       # J3·J1 은 플러그 통로를 정의하는 쪽
                assert region_ok(side, crt(fp), h, check_h=False), ref
            commit(ref, fp, side, x, y, rot)
            continue
        if how[0] in ("near", "pin") and how[1] not in placed:
            UNPLACED.append(ref)
            board.Remove(fp)
            continue
        if how[0] == "at":
            ax, ay = how[1] + DX, how[2]
        elif how[0] == "pin":                     # v0.9: 특정 핀 바로 옆 (디커플링 C → 해당 전원 핀)
            ax, ay = pin_xy(how[1], how[2])
        else:
            ax, ay = pad_xy(how[1], how[2])
        rots = opt.get("rots", (0, 90, 180, 270))
        # 1) 기준점에서 가장 가까운 빈 자리 거리 dmin, 2) dmin + SLACK 안의 후보 중
        #    사방이 막힌(다른 부품·가장자리에 붙은) 자리를 우선 → 틈이 덜 생김
        cands, dmin = [], None
        for si, side in enumerate(sides):
            pen = 3.0 * si                          # 두 번째 면은 3 mm 벌점
            for rot in rots:
                bx, hl = local_box(ref, side, rot)
                for d0, dx, dy in OFFSETS:
                    d = d0 + pen
                    if dmin is not None and d > dmin + SLACK:
                        break
                    x, y = round(ax + dx, 3), round(ay + dy, 3)
                    box = (x + bx[0], y + bx[1], x + bx[2], y + bx[3])
                    own = [(x + a, y + b, x + c, y + d) for (a, b, c, d) in hl]
                    if region_ok(side, box, h) and free(side, box, ref, own):
                        dmin = d if dmin is None else min(dmin, d)
                        touch = 0
                        for (ex, ey) in ((-0.3, 0), (0.3, 0), (0, -0.3), (0, 0.3)):
                            b2 = (box[0] + ex, box[1] + ey, box[2] + ex, box[3] + ey)
                            if not (region_ok(side, b2, h) and free(side, b2, ref)):
                                touch += 1
                        cands.append((d - TOUCH * touch, d, side, x, y, rot))
        best = min((c for c in cands if c[1] <= dmin + SLACK), default=None)
        if not best:
            UNPLACED.append(ref)
            board.Remove(fp)
            continue
        _, _, side, x, y, rot = best
        set_pose(fp, side, x, y, rot)
        commit(ref, fp, side, x, y, rot)

    board.BuildConnectivity()
    pro_path = OUT[:-len(".kicad_pcb")] + ".kicad_pro"
    keep = json.load(open(pro_path))
    pcbnew.SaveBoard(OUT, board)
    set_rules(pro_path, keep)
    prl = OUT[:-len(".kicad_pcb")] + ".kicad_prl"
    if os.path.exists(prl):
        os.remove(prl)                          # 사용자 로컬 설정 파일 — 저장소에 넣지 않음
    return board, placed


def report(placed):
    rows, err = [], []
    for ref, q in sorted(placed.items(), key=lambda kv: (kv[1]["side"], kv[1]["x"])):
        fp = PARTS[ref]["fp"]
        h = height(fp)
        c = q["crt"]
        ymax = max(abs(c[1]), abs(c[3]))
        ha = h_allow(c[0], c[2], ymax)
        pads = [dict(n=pd.GetNumber(), xy=[round(v, 3) for v in from_k(pd.GetPosition())],
                     net=PARTS[ref]["nets"].get(pd.GetNumber(), ""))
                for pd in q["fp"].Pads() if pd.GetNumber()]
        rows.append(dict(ref=ref, val=PARTS[ref]["val"], fp=fp.split(":")[1], side=q["side"],
                         x=round(q["x"], 3), y=round(q["y"], 3), rot=q["rot"], h=h,
                         crt=[round(v, 3) for v in c], fab=[round(v, 3) for v in (q["fab"] or c)],
                         h_allow=round(ha, 2), pads=pads))
        if h > ha:
            err.append(f"{ref}: height {h} > allowed {ha:.2f}")
    return rows, err


def main():
    board, placed = build()
    rows, err = report(placed)
    area = {s: sum((r["crt"][2] - r["crt"][0]) * (r["crt"][3] - r["crt"][1]) for r in rows if r["side"] == s)
            for s in "TB"}
    meta = dict(project=O.PROJECT, coords="mech: x axial (rear +), y lateral, z top +; KiCad = (100 + x - " + f"{X0:g}, 100 - y)",
                side={"T": "F.Cu (z+)", "B": "B.Cu (z-)"}, courtyard_area=area,
                harness_bands_top=[list(b) for b in HARNESS_BANDS],   # x0, x1, |y|, 허용 높이(None = 금지)
                counts={s: sum(1 for r in rows if r["side"] == s) for s in "TB"},
                unplaced=UNPLACED)
    json.dump(dict(meta=meta, parts=rows), open(JSON_OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(OUT)
    print("parts", len(rows), meta["counts"], "courtyard mm2", {k: round(v) for k, v in area.items()})
    err += [f"{r}: no free place" for r in UNPLACED]
    for e in err:
        print("ERROR", e)
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
