"""HMT500(260313) 조립 시방서 (HMT500-A-001) — 단계별 3D 그림 + 절차서 PDF.

  python hardware/mech/assembly_procedure.py            → 그림 + PDF
  python hardware/mech/assembly_procedure.py --no-render → 그림은 그대로, PDF만 다시

출력: hardware/mech/out/assembly_procedure/step_XX.png, HMT500-A-001_assembly_procedure.pdf

형상은 hmt500_cad.py(기구 Rev I)와 KiCad 배치(placement.json) 그대로. 순서는 조립 시뮬레이션(assembly_sim.py, 명목 조립·공구·두께 공차 검사; 몰딩 유동은 확인 필요)과 같다.
그림 색: 회색 = 이미 조립된 부품, 주황 = 이번 단계에서 다는 부품, 빨간 화살표 = 움직이는 방향.
금속·수지 부품은 안이 보이도록 윗 절반(z > 0)을 잘라 그린 단계가 있다 (절단면 표시).
"""

import html
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cadquery as cq  # noqa: E402

import hmt500_cad as M  # noqa: E402
import hmt500_params as P  # noqa: E402

OUT = os.path.join(M.OUT, "assembly_procedure")
DOC_NO = "HMT500-A-001"
PDF = os.path.join(OUT, f"{DOC_NO}_assembly_procedure.pdf")

# ── 색 ──
METAL = (0.74, 0.76, 0.80)
METAL_CUT = (0.62, 0.64, 0.68)
RESIN = (0.86, 0.74, 0.50)
PCB_C = (0.12, 0.46, 0.22)
PART_C = (0.20, 0.20, 0.22)
PLUG_C = (0.94, 0.91, 0.82)
WIRE_C = (0.93, 0.93, 0.90)
CONN_C = (0.36, 0.36, 0.40)
EPOXY = (0.55, 0.42, 0.20)
NEW = (0.96, 0.52, 0.12)
ARROW = (0.85, 0.12, 0.12)
GREEN = (0.30, 0.65, 0.25)

# ── 기본 형상 (한 번만 만듦) ──
_C = {}


def S(name):
    if name not in _C:
        _C[name] = {
            "body": M.body, "cap": M.cap, "housing": M.housing, "endcap": M.endcap, "orings": M.orings,
            "seal": M.seal, "potting": M.potting, "potting2": M.potting2, "conn": M.sensor_connector,
            "conn_oring": M.conn_oring, "probe": M.sensor_probe, "elements": M.sensor_elements, "pcb": M.pcbs,
            "parts": M.pcb_parts, "cw": M.chassis_wire, "tool": M.push_tool, "w1": M.harness, "w1p": M.harness_plug,
            "w2": M.harness2, "w2p": M.harness2_plug, "holder": M.pcb_holder, "ring": M.pcb_ring, "m12": M.connector,
            "screws_ax": screws_axial, "screws_x": screws_cross, "setscrews": set_screws,
        }[name]()
    return _C[name]


def screws_axial():
    """홀더 축 나사 M2 ×2 (뒤에서 바디 탭으로): 머리 Ø3.8 × 1.3 + 몸통."""
    H = P.PCB_HOLDER
    x_face = H["x"][1]
    out = None
    for z, L in ((H["screw_pcd"] / 2, 8.0), (-H["screw_pcd"] / 2, 6.0)):
        head = M.axial_hole(x_face - H["cbore_depth"] + 0.8, x_face - H["cbore_depth"] + 2.1, 0, z, 3.8)
        shank = M.axial_hole(x_face - H["cbore_depth"] + 0.8 - L, x_face - H["cbore_depth"] + 0.8, 0, z, 2.0)
        s = head.union(shank)
        out = s if out is None else out.union(s)
    return out


def screws_cross():
    """PCB 가로 나사 M2×12 ×2 (홀더 → PCB 관통, z 방향)."""
    H = P.PCB_HOLDER
    r = H["d"] / 2
    out = None
    for y in H["cross"]["y"]:
        head = cq.Workplane("XY").workplane(offset=r - 1.3).center(H["cross"]["x"], y).circle(1.9).extrude(1.3)
        shank = cq.Workplane("XY").workplane(offset=r - 1.3 - 12).center(H["cross"]["x"], y).circle(1.0).extrude(12)
        s = head.union(shank)
        out = s if out is None else out.union(s)
    return out


def set_screws():
    E = P.ENDCAP
    Po = E["ports"]
    f1 = E["flange"]["x"][1]
    out = None
    for ang in Po["angles"]:
        a = math.radians(ang)
        s = M.axial_hole(f1 - 3.0, f1, Po["r"] * math.cos(a), Po["r"] * math.sin(a), 2.9)
        out = s if out is None else out.union(s)
    return out


def half(shape):
    """보는 쪽(z > 0) 절반 제거."""
    return shape.cut(cq.Workplane("XY").box(400, 120, 60).translate((20, 0, 30)))


def mv(shape, dx=0.0, dy=0.0, dz=0.0):
    return shape.translate((dx, dy, dz))


def arrow(p0, p1, d=1.4):
    """p0 → p1 화살표 (몸통 + 원뿔 머리)."""
    v = cq.Vector(*p1) - cq.Vector(*p0)
    L = v.Length
    u = v.normalized()
    head = min(4.5, L * 0.4)
    shaft = cq.Solid.makeCylinder(d / 2, L - head, cq.Vector(*p0), u)
    cone = cq.Solid.makeCone(d * 1.4, 0.0, head, cq.Vector(*p0) + u * (L - head), u)
    return cq.Workplane("XY").add(shaft.fuse(cone))


def turn_arrow(x, r, a0=200.0, a1=340.0, d=1.2):
    """축(x) 둘레 회전 화살표 (호 + 원뿔)."""
    pts = [cq.Vector(x, r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
           for a in (a0, (a0 + a1) / 2, a1)]
    arc = cq.Edge.makeThreePointArc(*pts)
    path = cq.Wire.assembleEdges([arc])
    t0 = arc.tangentAt(0)
    prof = cq.Wire.makeCircle(d / 2, pts[0], t0)
    tube = cq.Solid.sweep(prof, [], path)
    t1 = arc.tangentAt(1)
    cone = cq.Solid.makeCone(d * 1.5, 0.0, 4.0, pts[2], t1)
    return cq.Workplane("XY").add(tube.fuse(cone))


# ── 공통 조합 ──
def done_body(cut=True):
    b = S("body")
    return [(half(b) if cut else b, METAL_CUT if cut else METAL)]


def sensor_side(potted=True):
    sc = [(S("conn"), CONN_C), (S("conn_oring"), PART_C), (S("w1"), WIRE_C)]
    if potted:
        sc.append((S("potting"), EPOXY))
    return sc


def pcb_asm(dx=0.0, cut_holder=True, with_cw=True, new=False):
    h = S("holder")
    sc = [(mv(half(h) if cut_holder else h, dx), NEW if new else RESIN), (mv(S("pcb"), dx), PCB_C),
          (mv(S("parts"), dx), PART_C)]
    if with_cw:
        sc.append((mv(S("cw"), dx), GREEN))
    return sc


def endcap_asm(dx=0.0, cut=True, new=False):
    e = S("endcap")
    return [(mv(half(e) if cut else e, dx), NEW if new else METAL_CUT if cut else METAL),
            (mv(S("m12"), dx), CONN_C), (mv(S("w2"), dx), WIRE_C)]


# ── 단계 정의 ──
# cam: (초점 x, y, z), 방향 (카메라 위치 − 초점, 정규화 전), 확대
ISO = (-0.35, -0.75, 0.85)
TOPV = (-0.15, -0.35, 1.0)
FRONT = (-0.8, -0.9, 0.5)
REAR = (1.0, -0.6, 0.55)

SPARE = P.HARNESS["length"]
TL = P.HOUSING["thread_len"]


def steps():
    H, E, Hs, B = P.PCB_HOLDER, P.ENDCAP, P.HOUSING, P.BODY
    xw = P.HARNESS["plug"]["x"]
    st = []

    def add(**k):
        st.append(k)

    add(key="w1_solder", title="센서 하네스 W-1 → HTX99R 뒤 핀 납땜", group="A. 센서부 (바디 앞쪽)",
        parts="⑮ HTX99R-SC 센서 커넥터, ⑰ W-1 센서 하네스 (JST SH 4P, PTFE AWG30, 40 mm)",
        tools="온도 조절 인두 (330 °C 이하), 핀셋, 열풍기, 확대경", mat="무연 땜납 (Sn96.5Ag3Cu0.5), 수축튜브 Ø1.2 (4개)",
        spec="핀 1·2 = MK33 전극 (SENS_C1/C2), 핀 3·4 = Pt1000 (PT_P/PT_N). 핀마다 수축튜브.",
        check="핀 배정 (도통 시험기), 땜납 브리지 없음, 수축튜브가 핀 뿌리까지 덮음, 선 끝 플러그 방향",
        caution="HTX99R 몰드(수지)를 인두로 3초 넘게 가열하지 않음. 선 끝(플러그)은 자유로운 상태 유지.",
        scene=lambda: [(S("conn"), CONN_C), (S("w1"), NEW), (S("w1p"), NEW)],
        cam=((-25, 30), ISO, 1.7))
    add(key="conn_oring", title="HTX99R에 O링 ⑯ 끼움", group="A. 센서부 (바디 앞쪽)",
        parts="⑯ O링 8 × 1.2 FKM 75", tools="O링 피크 (수지), 장갑", mat="실리콘 그리스 (O링용, 얇게)",
        spec="O링을 나사와 플랜지 사이 홈(Ø8.2)에 끼움. 꼬임 없이.",
        check="O링 꼬임·흠 없음, 홈에 완전히 앉음",
        caution="나사산 위로 넘길 때 O링이 긁히지 않게 천천히 늘림.",
        scene=lambda: [(S("conn"), CONN_C), (S("w1"), WIRE_C), (S("w1p"), PLUG_C),
                       (mv(S("conn_oring"), -9), NEW), (arrow((P.SENSOR_CONN["x0"] - 16, 0, 7), (P.SENSOR_CONN["x0"] - 8, 0, 7)), ARROW)],
        cam=((-24, 2), ISO, 1.6))
    add(key="w1_through", title="W-1 플러그를 바디 앞에서 Ø7 통로로 넣어 뒤로 뺌", group="A. 센서부 (바디 앞쪽)",
        parts="① 프로세스 바디 M-101", tools="핀셋",
        mat="-", spec=f"플러그(5.0 × 2.8)가 Ø7 통로 (길이 {B['channel']['x'][1] - B['channel']['x'][0]:g})를 어느 각도로도 지나감 (여유 0.63).",
        check="선 4가닥이 통로 안에서 꼬이지 않음, 피복 손상 없음",
        caution="통로 입구·출구 C0.3 버가 없는지 먼저 확인 (피복 보호).",
        scene=lambda: done_body() + [(mv(S("conn"), -22), CONN_C), (mv(S("conn_oring"), -22), PART_C),
                                     (mv(S("w1"), -22), WIRE_C), (mv(S("w1p"), -22), NEW),
                                     (arrow((xw[0] - 22 + 6, 0, 6), (xw[0] - 22 + 20, 0, 6)), ARROW)],
        cam=((-38, 16), TOPV, 1.0))
    add(key="conn_screw", title="HTX99R를 바디 앞 M10×1.0 암나사에 체결", group="A. 센서부 (바디 앞쪽)",
        parts="⑮ + ⑯ (+ ⑰)", tools="스패너 맞변 7 (HTX99R), 토크 드라이버, 바디 고정 지그 (AF27)",
        mat="-", spec="토크 1.0 N·m (TBD — 두텍 HTX99R 사양 확인). 플랜지가 Ø11.2 자리에 닿을 때까지.",
        check="플랜지 틈 없음, 선이 통로 뒤로 자유롭게 나옴 (선 끝을 잡지 않아 꼬임 없음)",
        caution="뒤로 나온 W-1 선 끝을 잡지 말 것 — 커넥터와 함께 돌아야 꼬이지 않음.",
        scene=lambda: done_body() + [(S("conn"), NEW), (S("conn_oring"), PART_C), (S("w1"), WIRE_C),
                                     (mv(S("w1p"), 0), PLUG_C),
                                     (turn_arrow(B["x_front"] - 6, 8.5), ARROW)],
        cam=((-22, 14), ISO, 1.0))
    add(key="potting1", title="1차 몰딩: Ø7 통로에 에폭시 주입·경화", group="A. 센서부 (바디 앞쪽)",
        parts="⑤ 상온경화 에폭시 (1종)", tools="디스펜서 (니들 18G), 진공 탈포기, 세움 지그 (프로브 아래)",
        mat="에폭시 약 0.5 cm³ (품목 선정 중)", spec="프로브를 아래로 세우고 뒤(카운터보어 쪽)에서 통로를 채움. 경화 조건은 에폭시 사양.",
        check="통로 뒤 끝까지 가득, 기포 없음, 선이 통로 가운데",
        caution="에폭시가 카운터보어 바닥 M2 탭 2개에 들어가지 않게 (테이프·핀으로 막음). 경화 전 움직이지 않음.",
        scene=lambda: done_body() + sensor_side(potted=False) + [(S("potting"), NEW), (S("w1p"), PLUG_C),
                                                                 (arrow((B["cbore"]["x"][0] + 14, 0, 4), (B["cbore"]["x"][0] + 1.5, 0, 4)), ARROW)],
        cam=((-20, 14), TOPV, 1.0))
    add(key="bench_pcb", title="[벤치] PCB ⑧을 홀더 ⑫ 홈에 끼우고 가로 나사 2개", group="B. 전자부 (벤치)",
        parts="⑧ PCB E-301, ⑫ PCB 홀더 M-105, ⑭ M2×12 ×2", tools="정밀 드라이버 (날 Ø3 이하), ESD 매트·손목띠",
        mat="-", spec="PCB 앞 끝을 홀더 홈(폭 1.9, 깊이 3.5) 끝까지. 가로 나사 M2×12 손 조임 (약 0.1 N·m, 수지 탭).",
        check="PCB가 홈에 꽉 끼고 흔들림 없음, 나사 머리가 홀더 면에 묻힘",
        caution="ESD 주의. 나사 과조임 금지 (POM 탭 손상).",
        scene=lambda: pcb_asm(cut_holder=False, with_cw=False) + [(mv(S("screws_x"), 0, 0, 9), NEW),
                                                                   (arrow((H["cross"]["x"], 12, 26), (H["cross"]["x"], 5.5, 16)), ARROW)],
        cam=((6, 72), ISO, 1.0))
    add(key="bench_cw", title="[벤치] 샤시 선 ⑳을 J5에 납땜, 펌웨어 기록·기능 검사", group="B. 전자부 (벤치)",
        parts="⑳ W-3 샤시 선 (AWG28 25 mm + M2 링 단자)", tools="인두, SWD 프로그래머 (Tag-Connect J2), 검사 지그",
        mat="땜납", spec="J5 (PCB 윗면)에 납땜. 링 단자 쪽은 자유. SWD 펌웨어 기록 → 전원·출력·RS-485 기능 검사 → 1차 교정.",
        check="펌웨어 버전, 4–20 mA 두 채널, Modbus 응답, 소비 전류 (검사 기록지)",
        caution="검사는 하네스 꽂기 전 (J2는 W-1 선 아래가 됨).",
        scene=lambda: pcb_asm(cut_holder=False, with_cw=False) + [(S("screws_x"), METAL), (S("cw"), NEW)],
        cam=((8, 34), ISO, 1.0))
    add(key="holder_in", title="W-1 플러그를 홀더 창으로 꿰고, 홀더+PCB를 바디에 넣음", group="C. 바디에 전자부 장착",
        parts="B 단계 조립품", tools="핀셋",
        mat="-", spec=f"창 {H['window']['wy']:g} × {H['window']['z'][1] - H['window']['z'][0]:g}로 플러그를 뒤로 꿴 뒤, "
                      f"홀더를 Ø{B['cbore']['d']:g} 카운터보어 바닥까지 밀어 넣음. 나사 구멍 PCD {H['screw_pcd']:g}을 탭에 맞춤.",
        check="홀더가 카운터보어 바닥에 닿음, 선이 창에서 눌리지 않음",
        caution="W-1 선을 당기지 말 것 (1차 몰딩 뿌리 보호).",
        scene=lambda: done_body() + sensor_side() + pcb_asm(dx=16, new=True) + [(S("screws_x"), METAL) if False else (mv(S("screws_x"), 16), METAL),
                                                                             (S("w1p"), PLUG_C),
                                                                             (arrow((40, 0, 14), (26, 0, 14)), ARROW)],
        cam=((-22, 62), TOPV, 1.0))
    add(key="holder_screw", title="홀더 축 나사: 아래 M2×6, 위 M2×8 + 샤시 링 단자", group="C. 바디에 전자부 장착",
        parts="⑭ M2×6, M2×8", tools="정밀 드라이버 (날 Ø3), 토크 드라이버",
        mat="나사 고정제 저강도 (Loctite 222 급, 1방울)", spec="토크 0.2 N·m. 위쪽 나사는 ⑳ 링 단자를 머리 밑에 끼움 → 금속 바디와 샤시 연결.",
        check="샤시 도통: J5 ~ 바디 < 1 Ω",
        caution="드라이버는 PCB 뒤쪽에서 축과 나란히 (부품과 최소 0.38 mm).",
        scene=lambda: done_body() + sensor_side() + pcb_asm() + [(S("screws_x"), METAL), (S("w1p"), PLUG_C),
                                                                 (mv(S("screws_ax"), 10), NEW),
                                                                 (arrow((H["x"][1] + 22, 0, 8), (H["x"][1] + 12, 0, 8)), ARROW)],
        cam=((-6, 42), ISO, 1.0))
    add(key="w1_plug", title="W-1 플러그를 J3에 꽂음", group="C. 바디에 전자부 장착",
        parts="⑰ 플러그 → ⑧ J3", tools="핀셋 (끝 2.0 × 1.2)",
        mat="-", spec="카운터보어 입구 위쪽 공간(7.4 mm)으로 핀셋을 넣어 플러그를 뒤(+x)로 4 mm 밀어 끝까지.",
        check="플러그 걸림 턱 확인, 남는 선은 PCB 앞 윗면에서 느슨한 고리",
        caution="선을 잡고 밀지 말 것 (플러그 몸체를 밈).",
        scene=lambda: done_body() + sensor_side() + pcb_asm() + [(S("screws_x"), METAL), (S("screws_ax"), METAL),
                                                                 (S("w1p"), NEW),
                                                                 (arrow((xw[0] - 9, 0, 6.5), (xw[0] + 1, 0, 6.5)), ARROW)],
        cam=((6, 36), TOPV, 1.0))
    add(key="ring", title="지지링 ⑬을 PCB 뒤에서 끼움", group="C. 바디에 전자부 장착",
        parts="⑬ PCB 지지링 M-106", tools="-",
        mat="-", spec=f"링 홈 2곳에 PCB 가장자리를 맞춰 뒤에서 x {P.PCB_RING['x'][0]:g}까지 밀어 넣음 (링 안 Ø20 안에 부품이 모두 들어감).",
        check="링이 PCB 넓은 구간 끝에 닿음, 부품 닿음 없음",
        caution="링은 축 방향으로 고정하지 않음 (열팽창 흡수).",
        scene=lambda: done_body() + sensor_side() + pcb_asm() + [(S("screws_x"), METAL), (S("screws_ax"), METAL),
                                                                 (S("w1p"), PLUG_C), (mv(S("ring"), 16), NEW),
                                                                 (arrow((P.PCB["x"][1] + 26, 0, 13), (P.PCB["x"][1] + 12, 0, 13)), ARROW)],
        cam=((-22, 100), ISO, 1.35))
    add(key="m12", title="[벤치] W-2를 M12 뒤 핀에 납땜하고 M12를 엔드캡에 체결", group="D. 엔드캡",
        parts="⑨ M12 8P 커넥터, ④ 엔드캡 M-104, ⑪ 커넥터 O링, ⑱ W-2 (JST GH 8P, 40 mm)",
        tools="인두, 열풍기, M12 커넥터 스패너, 엔드캡 고정 지그 (AF27)", mat="땜납, 수축튜브 Ø1.2 ×8",
        spec="핀 n = M12 핀 n. W-2 선을 엔드캡 안쪽으로 넣고 M12를 바깥(뒤)에서 M16×1.5에 체결. 토크: 커넥터 사양 (TBD).",
        check="M12 핀 1–8 ↔ GH 플러그 1–8 도통·절연, O링 자리",
        caution="커넥터 품번 확정 전 (나사부 ≤ 6 mm 조건). M12 체결 시 선 끝은 자유 (꼬임 없음).",
        scene=lambda: [(half(S("endcap")), METAL_CUT), (mv(S("m12"), 14), NEW), (mv(S("w2"), 14), WIRE_C), (mv(S("w2p"), 14), PLUG_C),
                                               (arrow((E["flange"]["x"][1] + 30, 0, 12), (E["flange"]["x"][1] + 18, 0, 12)), ARROW)],
        cam=((58, 115), ISO, 1.0))
    add(key="orings", title="O링 ⑩ 2개를 바디·엔드캡 홈에 끼움", group="E. 하우징 턴버클 체결",
        parts="⑩ O링 24 × 1.5 FKM 75 ×2", tools="O링 피크 (수지)", mat="실리콘 그리스 (얇게)",
        spec=f"바디 홈 Ø{P.ORING['groove_d']:g} (x {B['seal']['groove_x'][0]:g}–{B['seal']['groove_x'][1]:g}), "
             f"엔드캡 홈 (x {E['seal']['groove_x'][0]:g}–{E['seal']['groove_x'][1]:g}).",
        check="꼬임·흠 없음", caution="M26 나사산을 넘길 때 O링 긁힘 주의.",
        scene=lambda: done_body(cut=False) + pcb_asm(cut_holder=False) + [(S("ring"), RESIN), (S("orings"), NEW)] + endcap_asm(cut=False),
        cam=((-22, 95), ISO, 1.0))
    add(key="housing_on", title=f"하우징 ③을 PCB 위로 씌움 (턴버클 시작 위치, {TL:g} mm 뒤)", group="E. 하우징 턴버클 체결",
        parts="③ 하우징 M-103", tools="-", mat="-",
        spec=f"앞(오른나사) 쪽을 바디로 향하게. 바디 M26×1 나사 입구에 닿는 위치 (체결 전, 최종보다 {TL:g} mm 뒤).",
        check="방향 확인: 뒤 끝 'LH' 각인이 엔드캡 쪽",
        caution="하우징 안쪽 나사 골(Ø24.9)과 부품 틈 1.27 mm — 비스듬히 넣지 말 것.",
        scene=lambda: done_body() + sensor_side() + pcb_asm() + [(S("screws_ax"), METAL), (S("w1p"), PLUG_C), (S("ring"), RESIN),
                                                                 (mv(half(S("housing")), TL + 14), NEW),
                                                                 (arrow((Hs["x"][1] + 30, 0, 18), (Hs["x"][1] + 16, 0, 18)), ARROW)],
        cam=((-22, 112), ISO, 1.25))
    add(key="w2_push", title="공구 T-001로 W-2 플러그를 하우징 뒤 입구에서 J1에 꽂음", group="E. 하우징 턴버클 체결",
        parts="⑱ W-2 플러그 → ⑧ J1", tools="T-001 밀대 (3D 프린트, 끝 두께 3.0, 가운데 홈 10.4)",
        mat="-", spec="엔드캡(M12 달린 상태)을 옆으로 비켜 들고, 밀대 끝으로 플러그 양쪽 턱을 밀어 하우징 안 19.5 mm 깊이의 J1에 끝까지.",
        check="플러그 걸림 확인 (가볍게 당겨 빠지지 않음)",
        caution="선을 밀대 가운데 홈으로 빼서 누르지 않게.",
        scene=lambda: done_body() + sensor_side() + pcb_asm() + [(S("screws_ax"), METAL), (S("w1p"), PLUG_C), (S("ring"), RESIN),
                                                                 (mv(half(S("housing")), TL), METAL_CUT),
                                                                 (S("w2p"), PLUG_C), (S("tool"), NEW),
                                                                 (arrow((P.HARNESS2["plug"]["x"][1] + 50, 0, 10), (P.HARNESS2["plug"]["x"][1] + 36, 0, 10)), ARROW)],
        cam=((-22, 145), ISO, 1.4))
    add(key="turnbuckle", title=f"턴버클 체결: 바디·엔드캡을 잡고 하우징만 {TL:g}바퀴", group="E. 하우징 턴버클 체결",
        parts="① ③ ④", tools="AF27 스패너 2개 (바디 육각, 엔드캡 맞변) + 하우징 벨트 렌치, 토크 렌치",
        mat="나사 고정제 중강도 (Loctite 243 급) — 양쪽 수나사 앞쪽 2산",
        spec=f"하우징을 돌리면 앞(오른나사)·뒤(왼나사)가 동시에 당겨짐 → 엔드캡이 {2 * TL:g} mm 다가옴. 토크 5 N·m (TBD). "
             "바디·엔드캡·PCB·M12·하네스는 돌지 않음.",
        check="하우징 양 끝이 칼라·플랜지에 닿음 (틈 0), 엔드캡과 PCB 틈 0.6 (계산값), W-2 여유 선은 J1 뒤에서 한 번 접힘",
        caution="엔드캡을 돌리지 말 것 (W-2 꼬임). 처음 1바퀴는 손으로 양쪽 나사 물림 확인.",
        scene=lambda: done_body() + sensor_side() + pcb_asm() + [(S("screws_ax"), METAL), (S("w1p"), PLUG_C), (S("ring"), RESIN),
                                                                 (S("w2p"), PLUG_C), (half(S("housing")), NEW)] + endcap_asm(cut=True)
                      + [(turn_arrow(43, Hs["od"] / 2 + 3, 30, 150, d=1.6), ARROW),
                         (arrow((E["flange"]["x"][1] + 18, 0, -18), (E["flange"]["x"][1] + 4, 0, -18)), ARROW)],
        cam=((-22, 98), ISO, 1.2))
    add(key="potting2", title="2차 몰딩: 엔드캡 M3 구멍으로 하우징 안 전체 주입", group="F. 몰딩·마감",
        parts="⑤ 에폭시, ⑲ M3×3 무두나사 ×2", tools="진공 주입 장치, 디스펜서, 육각 렌치 1.5",
        mat="에폭시 주입량 확인 필요 (현재 CAD·실측 기준), 나사 실런트", spec="M12를 위로 세우고 한쪽 M3 구멍으로 진공 주입, 다른 구멍으로 공기 빠짐. Rev I: 포트 r11.8, 안쪽 경사 20°, M12 어깨 Ø20 이하·노즐 외경 Ø2.5 이하 조건. 실제 품번·수지 점도에 따른 주입 시험 필요. "
                                               "경화 후 ⑲ + 실런트로 막음 (0.3 N·m).",
        check="공기 빠짐 구멍으로 에폭시가 나옴, 경화 후 2차 교정",
        caution="몰딩 후 전자부 분해·수리 불가 — 몰딩 전 검사 기록 확인. 최종 교정은 경화 뒤.",
        scene=lambda: done_body() + sensor_side() + pcb_asm() + [(S("ring"), RESIN), (S("w2p"), PLUG_C), (half(S("housing")), METAL_CUT)]
                      + endcap_asm(cut=True) + [(S("potting2"), (0.95, 0.60, 0.20), 0.45), (mv(S("setscrews"), 6), NEW),
                         (arrow((P.ENDCAP["flange"]["x"][1] + 20, 0, 12), (P.ENDCAP["flange"]["x"][1] + 8, 0, 11)), ARROW)],
        cam=((-22, 95), ISO, 1.0))
    add(key="probe_cap", title="센서 프로브 ⑥을 꽂고 보호캡 ②를 체결", group="F. 몰딩·마감",
        parts="⑥ 센서 프로브 (MK33-W + Pt1000), ② 보호캡 M-102", tools="장갑 (센서면 만지지 않음), 스패너 (캡 평면 없으면 손 조임)",
        mat="-", spec="프로브 핀 4개를 HTX99R 소켓에 곧게 꽂음 → 보호캡을 HTX99R 위 나사 M10×1.0에 체결. "
                      f"캡 뿌리 {B['cap_sleeve']['x'][1] - B['cap_sleeve']['x'][0]:g} mm가 G½ 앞면 칼라에 들어감. 손 조임 + 0.5 N·m (TBD).",
        check="캡이 칼라 바닥에 닿음, 옆 구멍 막힘 없음",
        caution="센서 표면·구멍에 기름·지문 금지. 프로브는 현장 교체품 (캡만 풀면 교체).",
        scene=lambda: [(S("body"), METAL), (mv(S("probe"), -12), NEW), (mv(S("elements"), -12), (0.2, 0.2, 0.6)),
                       (mv(S("cap"), -42), NEW), (S("conn"), CONN_C),
                       (arrow((P.CAP["x_tip"] - 46, 0, 10), (P.CAP["x_tip"] - 36, 0, 10)), ARROW)],
        cam=((-100, 20), FRONT, 1.5))
    add(key="seal", title="본디드 씰 ⑦ 끼움, 최종 검사", group="F. 몰딩·마감",
        parts="⑦ 본디드 씰 G½ (강 + FKM)", tools="내압 시험기, 절연 저항계, 교정 장치",
        mat="-", spec="씰을 보호캡 쪽에서 G½ 나사 뒤 씰면까지. 내압 조건 확인 필요 (75 bar 제안값), 절연, 출력·온도 교정, 레이저 마킹 확인.",
        check="최종 검사 기록 (부록 체크시트)",
        caution="씰 고무면 손상 주의. 설치 토크는 현장 설치 설명서.",
        scene=lambda: [(S("body"), METAL), (S("cap"), METAL), (S("housing"), METAL), (S("endcap"), METAL), (S("m12"), CONN_C),
                       (mv(S("seal"), -38), NEW), (arrow((-60, 0, 17), (-46, 0, 17)), ARROW)],
        cam=((-75, 95), FRONT, 1.4))
    return st


# ── 그리기 ──
def render(scene, out, cam, opac=None, size=(1500, 900)):
    import vtk
    from render3d import actor_for
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    for item in scene:
        shape, col = item[0], item[1]
        op = item[2] if len(item) > 2 else 1.0
        ren.AddActor(actor_for(shape, col, op))
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(ren)
    win.SetSize(*size)
    xr, d, zoom = cam                                  # xr: 보여줄 x 구간 (None = 전체)
    n = math.sqrt(sum(c * c for c in d))
    fx = 0.0 if xr is None else (xr[0] + xr[1]) / 2
    c = ren.GetActiveCamera()
    c.SetFocalPoint(fx, 0, 0)
    c.SetPosition(fx + 300 * d[0] / n, 300 * d[1] / n, 300 * d[2] / n)
    c.SetViewUp(0, 0, 1)
    c.SetViewAngle(20)
    if xr is None:
        ren.ResetCamera()
    else:
        ren.ResetCamera(xr[0], xr[1], -17, 17, -17, 17)
    c.Zoom(zoom)
    ren.ResetCameraClippingRange()
    for pos in ((-100, -200, 300), (200, -100, 200)):
        L = vtk.vtkLight()
        L.SetPosition(*pos)
        L.SetFocalPoint(fx, 0, 0)
        L.SetIntensity(0.55)
        ren.AddLight(L)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(out)
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()


def render_all(only=None):
    os.makedirs(OUT, exist_ok=True)
    for i, s in enumerate(steps(), 1):
        if only and s["key"] not in only:
            continue
        scene = s["scene"]()
        out = os.path.join(OUT, f"step_{i:02d}.png")
        render(scene, out, s["cam"])
        print(out)
    render([(S("body"), METAL), (S("cap"), METAL), (S("housing"), METAL), (S("endcap"), METAL), (S("m12"), CONN_C),
            (S("seal"), PART_C)], os.path.join(OUT, "overview.png"), (None, ISO, 1.05))
    # 분해도 (표지)
    ex = [(mv(S("cap"), -60), METAL), (mv(S("probe"), -45), NEW), (mv(S("seal"), -30), PART_C),
          (mv(S("conn"), -20), CONN_C), (S("body"), METAL), (mv(S("holder"), 18), RESIN), (mv(S("pcb"), 30), PCB_C),
          (mv(S("parts"), 30), PART_C), (mv(S("ring"), 48), RESIN), (mv(S("housing"), 58), METAL),
          (mv(S("endcap"), 110), METAL), (mv(S("m12"), 122), CONN_C)]
    render(ex, os.path.join(OUT, "exploded.png"), (None, ISO, 2.2), size=(2000, 700))


# ── 문서 ──
CSS = """
@page { size: 297mm 210mm; margin: 0 }
body { margin: 0; font-family: 'NanumGothic', 'Noto Sans CJK KR', sans-serif; color: #111; font-size: 10.5pt }
.page { width: 297mm; height: 210mm; box-sizing: border-box; padding: 11mm 13mm 9mm; page-break-after: always; position: relative }
.hdr { display: flex; justify-content: space-between; border-bottom: 1.2px solid #111; padding-bottom: 2mm; font-size: 9pt }
.hdr b { font-size: 10pt }
.ftr { position: absolute; bottom: 5mm; left: 13mm; right: 13mm; font-size: 8pt; color: #555; display: flex; justify-content: space-between }
h1 { font-size: 22pt; margin: 14mm 0 3mm } h2 { font-size: 14pt; margin: 4mm 0 2mm } h3 { font-size: 11pt; margin: 3mm 0 1.5mm }
table { border-collapse: collapse; width: 100% } td, th { border: 0.6px solid #555; padding: 1.1mm 1.8mm; vertical-align: top; font-size: 9pt }
th { background: #eee; text-align: left; white-space: nowrap }
.step { display: grid; grid-template-columns: 158mm 1fr; gap: 6mm; margin-top: 3mm }
.step img { width: 158mm; border: 0.6px solid #bbb }
.step td, .step th { font-size: 10pt; padding: 1.6mm 2mm }
.no { display: inline-block; background: #111; color: #fff; border-radius: 2mm; padding: 0.6mm 2.5mm; margin-right: 2mm }
.grp { color: #666; font-size: 9pt }
.warn { border-left: 3px solid #d9480f; padding-left: 2mm; background: #fff4e6 }
.legend span { display: inline-block; width: 3.2mm; height: 3.2mm; vertical-align: -0.4mm; margin: 0 1mm 0 3mm; border: 0.5px solid #555 }
.small { font-size: 8.5pt; color: #333 }
.sign td { height: 6.5mm }
"""


def page(inner, no, total, title):
    return (f'<div class="page"><div class="hdr"><span><b>(주)두텍 DOTECH</b> · HMT500(260313) 오일 수분 트랜스미터</span>'
            f'<span><b>{DOC_NO} 조립 시방서</b> · 기구 Rev {P.DRAWING_REV} · {P.DATE}</span></div>{inner}'
            f'<div class="ftr"><span>{html.escape(title)}</span><span>{no} / {total}</span></div></div>')


def e(t):
    return html.escape(str(t))


def build_pdf():
    st = steps()
    img = lambda n: "file://" + os.path.join(OUT, n)      # noqa: E731
    pages = []
    # 1. 표지
    flow = "".join(f"<tr><td>{i}</td><td>{e(s['group'])}</td><td>{e(s['title'])}</td></tr>" for i, s in enumerate(st, 1))
    pages.append(("표지·적용 범위", f"""
<h1>HMT500(260313) 조립 시방서</h1>
<div class="grp">문서 {DOC_NO} · 기구 Rev {P.DRAWING_REV} (외형 = E+E EE364와 같은 치수) · PCB HMT500(260313A) · 작성 {P.DATE}</div>
<img src="{img('exploded.png')}" style="width:100%;margin:5mm 0 2mm;border:0.6px solid #bbb">
<table><tr><th>적용 범위</th><td>HMT500(260313) 시제품 조립 (기계부 · 하네스 · 몰딩 · 최종 검사). 회로 조립(SMT)은 JLCPCB PCBA로 완료된 PCB를 받는 것으로 함.</td></tr>
<tr><th>관련 도면</th><td>HMT500-M-000 조립도, M-101 바디, M-102~104 캡·하우징·엔드캡, M-105~106 홀더·지지링 (HMT500_mechanical_drawings.pdf) · KiCad HMT500(260313A)</td></tr>
<tr><th>근거</th><td>조립 순서는 조립 시뮬레이션 (hardware/mech/assembly_sim.py, 명목 조립·공구·두께 공차 검사; 몰딩 유동은 확인 필요)으로 공구·부품 간섭을 확인한 순서. 그림은 3D 모델(hmt500_cad.py)을 그대로 그림.</td></tr>
<tr><th>그림 읽는 법</th><td class="legend">회색<span style="background:#bcc2cc"></span> 이미 조립됨 · 주황<span style="background:#f5851f"></span> 이번 단계 부품 · 빨강<span style="background:#d91f1f"></span> 움직이는 방향 · 금속·수지 부품 일부는 안이 보이게 절반을 잘라 그림</td></tr>
<tr><th>(TBD)</th><td>토크·에폭시·M12 품번 등 표시된 값은 시제품 시험 후 확정. 확정 전에는 생산 작업 기준으로 사용하지 말 것. 시제품 시험 계획에서 별도 승인·기록.</td></tr></table>
"""))
    # 2. 흐름 + 외관
    pages.append(("조립 흐름", f"""
<h2>조립 흐름 ({len(st)}단계)</h2>
<div style="display:grid;grid-template-columns:1fr 118mm;gap:6mm">
<table><tr><th>No</th><th>구분</th><th>작업</th></tr>{flow}</table>
<div><img src="{img('overview.png')}" style="width:118mm;border:0.6px solid #bbb">
<p class="small">완성품 외형 (Rev I): 전장 {P.OVERALL:g} · 노출 프로브 Ø12 × {P.BODY['gthread']['x'][0] - P.CAP['x_tip']:g} · G½ 14 · 육각 AF27 × 10 ·
몸통 Ø{P.HOUSING['od']:g} · 씰면 ~ 엔드캡 끝 {P.ENDCAP['flange']['x'][1]:g} · M12 15.</p>
<p class="small warn"><b>순서를 바꾸지 말 것.</b> 특히 ① HTX99R 체결은 W-1 선 끝이 자유로운 상태에서, ② 홀더 축 나사는 W-1 플러그를 창으로 꿴 뒤,
③ 하우징은 턴버클로 하우징만 돌림 — 모두 하네스 꼬임·간섭을 피하려는 순서.</p></div></div>
"""))
    # 3. 부품표
    rows = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td><td>{e(q)}</td><td>{e(n)}</td></tr>"
                   for a, b, c, d, q, n in P.PARTS)
    pages.append(("부품표", f"""<h2>부품표 (1대분)</h2>
<table><tr><th>No</th><th>도번·품번</th><th>품명</th><th>재질</th><th>수량</th><th>비고</th></tr>{rows}</table>
<p class="small">시제품: M-101~104는 SUS304 (JLCCNC), M-105·106은 POM 백색. 양산 재질은 도면 표기 (SUS316L / PEEK).</p>"""))
    # 4. 공구·소모품·토크
    pages.append(("공구·소모품·조임", f"""<h2>공구 · 소모품 · 조임 기준</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:6mm">
<div><h3>공구</h3><table>
<tr><th>공구</th><th>용도</th></tr>
<tr><td>AF27 스패너 ×2 / 바디 고정 지그</td><td>바디 육각, 엔드캡 맞변 (둘 다 AF27)</td></tr>
<tr><td>하우징 벨트 렌치 (Ø30)</td><td>턴버클: 하우징만 돌림</td></tr>
<tr><td>토크 렌치 1–10 N·m, 토크 드라이버 0.1–1 N·m</td><td>턴버클, HTX99R, M2 나사</td></tr>
<tr><td>스패너 맞변 7</td><td>HTX99R 체결</td></tr>
<tr><td>정밀 드라이버 (날 Ø3 이하)</td><td>M2 나사 (가로·축)</td></tr>
<tr><td>핀셋 (끝 2.0 × 1.2), O링 피크 (수지)</td><td>W-1 플러그, O링</td></tr>
<tr><td>T-001 W-2 플러그 밀대 (3D 프린트)</td><td>J1 꽂기 (하우징 안 19.5 mm)</td></tr>
<tr><td>인두·열풍기, SWD 프로그래머 (Tag-Connect), 검사 지그</td><td>하네스 납땜, 펌웨어·기능 검사</td></tr>
<tr><td>디스펜서·진공 주입 장치·탈포기</td><td>1차·2차 몰딩</td></tr>
<tr><td>내압 시험기 (≥ 75 bar), 절연 저항계, 교정 장치</td><td>최종 검사</td></tr></table></div>
<div><h3>소모품</h3><table>
<tr><th>품목</th><th>용도</th></tr>
<tr><td>상온경화 에폭시 1종 (TBD: ≥ 120 °C, 내유성, SUS·PEEK·FR-4 접착)</td><td>1차 Ø7 통로 약 0.5 cm³, 2차 하우징 안 실제 주입량 확인 필요</td></tr>
<tr><td>실리콘 그리스 (O링용)</td><td>O링 ⑩ ×2, ⑯</td></tr>
<tr><td>나사 고정제 중강도 (Loctite 243 급) / 저강도 (222 급)</td><td>턴버클 나사 / M2 축 나사</td></tr>
<tr><td>나사 실런트</td><td>M3 무두나사 ⑲</td></tr>
<tr><td>무연 땜납, 수축튜브 Ø1.2</td><td>W-1 (4), W-2 (8), W-3</td></tr></table>
<h3>조임 기준 (TBD = 시험 후 확정)</h3><table>
<tr><th>부위</th><th>토크</th></tr>
<tr><td>HTX99R → 바디 M10×1.0</td><td>1.0 N·m (TBD, 두텍 사양)</td></tr>
<tr><td>PCB 가로 나사 M2×12 → 홀더 (POM)</td><td>약 0.1 N·m (확인 필요)</td></tr>
<tr><td>홀더 축 나사 M2 → 바디 (SUS)</td><td>0.2 N·m (확인 필요)</td></tr>
<tr><td>M12 → 엔드캡 M16×1.5</td><td>커넥터 사양 (TBD)</td></tr>
<tr><td>하우징 턴버클 M26×1 (R/LH)</td><td>5 N·m (TBD)</td></tr>
<tr><td>M3×3 무두나사</td><td>0.3 N·m (확인 필요) + 실런트</td></tr>
<tr><td>보호캡 → HTX99R 위 나사</td><td>손 조임 + 0.5 N·m (TBD)</td></tr></table></div></div>
<p class="small warn">ESD: B 단계부터 PCB를 다룰 때 손목띠·ESD 매트 사용. 청결: 접액부·O링 면에 먼지·금속 칩 없음. 에폭시 작업은 환기·보호장갑.</p>"""))
    # 5. 단계
    for i, s in enumerate(st, 1):
        inner = f"""<div style="margin-top:3mm"><span class="no">{i}</span><b style="font-size:14pt">{e(s['title'])}</b>
<span class="grp"> &nbsp; {e(s['group'])}</span></div>
<div class="step"><img src="{img(f'step_{i:02d}.png')}">
<div><table>
<tr><th>부품</th><td>{e(s['parts'])}</td></tr>
<tr><th>공구</th><td>{e(s['tools'])}</td></tr>
<tr><th>소모품</th><td>{e(s['mat'])}</td></tr>
<tr><th>작업·기준</th><td>{e(s['spec'])}</td></tr>
<tr><th>검사</th><td>{e(s['check'])}</td></tr>
<tr><th>주의</th><td class="warn">{e(s['caution'])}</td></tr></table>
<table class="sign" style="margin-top:3mm"><tr><th>작업자</th><td></td><th>일자</th><td></td></tr>
<tr><th>검사</th><td colspan="3">□ 합격 &nbsp; □ 불합격 &nbsp; 비고:</td></tr></table></div></div>"""
        pages.append((f"{i}. {s['title']}", inner))
    # 6. 최종 검사 기록지
    items = [("외관", "흠·찍힘·버 없음, 레이저 마킹 (모델·출력·전원·핀맵·시리얼)"),
             ("치수", f"전장 {P.OVERALL:g} ±0.5, 노출 프로브 34, 몸통 Ø30"),
             ("샤시 도통", "M12 하우징(샤시) ~ 바디 < 1 Ω"), ("절연", "전원·신호 ~ 샤시 ≥ 100 MΩ (시험전압 확인 필요 — 샤시 보호소자와 협의)"),
             ("내압", "확인 필요: 75 bar·5분은 제안값, 정격·시험 계획 승인 후 수행"), ("전원", "12 / 24 / 28 V 소비 전류"),
             ("출력", "4–20 mA 2채널 4·12·20 mA 점검, RS-485 Modbus 응답"),
             ("교정", "aw 2점 이상, 온도 2점 (2차 몰딩 경화 후)"), ("기록", "펌웨어 버전, 교정 계수, 시리얼")]
    rows = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td></td><td>□ 합 □ 불</td></tr>" for a, b in items)
    pages.append(("최종 검사 기록지", f"""<h2>최종 검사 기록지</h2>
<table style="margin-bottom:3mm"><tr><th>시리얼</th><td style="width:60mm"></td><th>작업자</th><td></td><th>일자</th><td></td></tr></table>
<table><tr><th style="width:28mm">항목</th><th>기준</th><th style="width:60mm">측정값</th><th style="width:26mm">판정</th></tr>{rows}</table>
<p class="small">몰딩 후에는 전자부 분해·수리가 불가하므로, 2차 몰딩 전 단계 7(기능 검사) 기록이 있어야 몰딩을 진행한다.</p>"""))
    total = len(pages)
    body = "".join(page(inner, n, total, title) for n, (title, inner) in enumerate(pages, 1))
    src = os.path.join(OUT, "_procedure.html")
    open(src, "w", encoding="utf-8").write(f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>')
    chrome = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", f"--print-to-pdf={PDF}", "file://" + src],
                   check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    os.remove(src)
    print(PDF)


if __name__ == "__main__":
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--no-render" not in sys.argv:
        render_all(only or None)
    build_pdf()
