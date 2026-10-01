"""HMT500(260313A) PCB(E-301) 보드 파일 생성: 외곽선, 고정 구멍, 금지 구역, 배치 구역.

치수는 기구 파라미터(hardware/mech/hmt500_params.py)를 그대로 읽는다.
  python3 hardware/kicad/gen_pcb_outline.py  →  hardware/kicad/HMT500(260313A)/HMT500(260313A).kicad_pcb

좌표: 보드 앞 끝(피드스루 쪽) 가운데 = (100, 100). KiCad x = 축 방향(뒤쪽 +), y = 폭 방향(아래 +).
부품 배치·배선은 아직 없음 — 회로도에서 "PCB 업데이트"로 부품을 불러와 배치 구역에 맞춰 놓는다.
"""

import math
import os
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
import sys  # noqa: E402

sys.path.insert(0, os.path.join(HERE, "..", "mech"))
import hmt500_params as P  # noqa: E402

PROJECT = "HMT500(260313A)"          # 회로·PCB·거버 공통 파일명 = 프로젝트 번호
OUT = os.path.join(HERE, PROJECT, PROJECT + ".kicad_pcb")
OX, OY = 100.0, 100.0
F0 = P.PCB["x"][0]


ZONES_EN = [("MEASUREMENT", "J3, PCAP04, ADS1220, Cref"),
            ("MCU + POWER", "STM32G0B1, eFuse, buck, LDO"),
            ("OUTPUT + PROTECTION", "J1, DAC8760x2, TPS26611, THVD2450")]


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "hmt500-pcb/" + key))


def K(x, y):
    """기구 좌표(x 축 방향, y 폭) → KiCad 좌표."""
    return (round(OX + (x - F0), 4), round(OY - y, 4))


def outline_pts():
    up = []
    for x0, x1, w in P.PCB["sections"]:
        up += [(x0, w / 2), (x1, w / 2)]
    pts = up + [(x, -y) for x, y in reversed(up)]
    out = []
    for p in pts:                      # 같은 점 중복 제거
        if not out or out[-1] != p:
            out.append(p)
    return out


def fillet_outline(pts, r):
    """모든 꼭짓점(직각)을 반경 r 로 둥글게 → [('line', a, b) | ('arc', s, m, e)]."""
    n = len(pts)
    corners = []
    for i in range(n):
        vx, vy = pts[i]
        px, py = pts[i - 1]
        nx, ny = pts[(i + 1) % n]
        l1 = math.hypot(px - vx, py - vy)
        l2 = math.hypot(nx - vx, ny - vy)
        u1 = ((px - vx) / l1, (py - vy) / l1)
        u2 = ((nx - vx) / l2, (ny - vy) / l2)
        rr = min(r, l1 / 2, l2 / 2)
        s = (vx + u1[0] * rr, vy + u1[1] * rr)
        e = (vx + u2[0] * rr, vy + u2[1] * rr)
        c = (vx + (u1[0] + u2[0]) * rr, vy + (u1[1] + u2[1]) * rr)
        b = math.hypot(u1[0] + u2[0], u1[1] + u2[1])
        m = (c[0] - (u1[0] + u2[0]) / b * rr, c[1] - (u1[1] + u2[1]) / b * rr)
        corners.append((s, m, e))
    segs = []
    for i in range(n):
        s, m, e = corners[i]
        segs.append(("arc", s, m, e))
        segs.append(("line", e, corners[(i + 1) % n][0]))
    return segs


def xy(p):
    x, y = K(*p)
    return f"(xy {x} {y})"


def gr_line(a, b, layer, w, key):
    (x1, y1), (x2, y2) = K(*a), K(*b)
    return f'  (gr_line (start {x1} {y1}) (end {x2} {y2}) (layer "{layer}") (width {w}) (tstamp {uid(key)}))'


def gr_arc(s, m, e, layer, w, key):
    (x1, y1), (xm, ym), (x2, y2) = K(*s), K(*m), K(*e)
    return f'  (gr_arc (start {x1} {y1}) (mid {xm} {ym}) (end {x2} {y2}) (layer "{layer}") (width {w}) (tstamp {uid(key)}))'


def gr_rect(x0, y0, x1, y1, layer, key, w=0.1):
    (a, b), (c, d) = K(x0, y0), K(x1, y1)
    return f'  (gr_rect (start {a} {b}) (end {c} {d}) (layer "{layer}") (width {w}) (fill none) (tstamp {uid(key)}))'


def gr_text(txt, x, y, layer, key, size=0.8):
    a, b = K(x, y)
    return (f'  (gr_text "{txt}" (at {a} {b}) (layer "{layer}") (tstamp {uid(key)})\n'
            f'    (effects (font (size {size} {size}) (thickness {size * 0.15:.3f}))))')


def keepout(name, x0, y0, x1, y1):
    pts = " ".join(xy(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)))
    return f"""  (zone (net 0) (net_name "") (layers "F.Cu" "B.Cu" "In1.Cu" "In2.Cu") (tstamp {uid(name)}) (name "{name}") (hatch edge 0.5)
    (connect_pads (clearance 0))
    (min_thickness 0.25) (filled_areas_thickness no)
    (keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed) (copperpour not_allowed) (footprints not_allowed))
    (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
    (polygon (pts {pts}))
  )"""


HEADER = """(kicad_pcb (version 20221018) (generator pcbnew)
  (general (thickness 1.6))
  (paper "A4")
  (title_block
    (title "HMT500(260313A) PCB E-301 (outline & keepouts)")
    (date "{date}")
    (rev "{rev}")
    (company "DOTECH Co., Ltd.")
    (comment 1 "Board outline from hardware/mech/hmt500_params.py (gen_pcb_outline.py)")
  )
  (layers
    (0 "F.Cu" signal)
    (1 "In1.Cu" power)
    (2 "In2.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive")
    (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user "B.Silkscreen")
    (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user "User.Drawings")
    (41 "Cmts.User" user "User.Comments")
    (42 "Eco1.User" user "User.Eco1")
    (43 "Eco2.User" user "User.Eco2")
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user "B.Courtyard")
    (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Paste" (type "Top Solder Paste"))
      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 1" (type "prepreg") (thickness 0.2) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "In1.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 2" (type "core") (thickness 1.065) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "In2.Cu" (type "copper") (thickness 0.035))
      (layer "dielectric 3" (type "prepreg") (thickness 0.2) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.035))
      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
      (layer "B.Paste" (type "Bottom Solder Paste"))
      (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "ENIG")
      (dielectric_constraints no)
    )
    (pad_to_mask_clearance 0)
    (aux_axis_origin {ox} {oy})
    (grid_origin {ox} {oy})
  )
  (net 0 "")
"""


def build():
    Pc, Hh, R = P.PCB, P.PCB_HOLDER, P.PCB_RING
    o = [HEADER.format(date=P.DATE, rev="A1", ox=OX, oy=OY)]
    # 외곽선
    for i, sg in enumerate(fillet_outline(outline_pts(), Pc["corner_r"])):
        if sg[0] == "line":
            if math.dist(sg[1], sg[2]) > 1e-6:
                o.append(gr_line(sg[1], sg[2], "Edge.Cuts", 0.1, f"edge-l{i}"))
        else:
            o.append(gr_arc(*sg[1:], "Edge.Cuts", 0.1, f"edge-a{i}"))
    # 홀더 가로 나사 구멍 (비도금, Edge.Cuts 원)
    for i, (x, y) in enumerate(Pc["holes"]):
        cx, cy = K(x, y)
        o.append(f'  (gr_circle (center {cx} {cy}) (end {round(cx + Pc["hole_d"] / 2, 4)} {cy}) (layer "Edge.Cuts") '
                 f'(width 0.1) (fill none) (tstamp {uid(f"hole{i}")}))')
    # 금지 구역: 홀더 홈 물림(앞 끝 전폭), 지지링 홈(가장자리 띠)
    w0 = Pc["sections"][0][2] / 2
    s0, s1 = Hh["slot_x"]
    o.append(keepout("KO_holder_slot", s0 - 0.5, w0 + 0.5, s1, -w0 - 0.5))
    wm = Pc["sections"][1][2] / 2
    for sgn, nm in ((1, "KO_ring_top"), (-1, "KO_ring_bottom")):
        o.append(keepout(nm, R["x"][0] - 0.3, sgn * (wm + 0.5), R["x"][1] + 0.3, sgn * (R["id"] / 2 - 0.3)))
    # 배치 구역 (Dwgs.User) + 이름
    for i, (name, parts, xa, xb) in enumerate(Pc["zones"]):   # KiCad 기본 글꼴에 한글이 없어 영문 표기
        en, en_parts = ZONES_EN[i]
        o.append(gr_rect(xa + 0.2, 8.0, xb - 0.2, -8.0, "Dwgs.User", f"zone{i}"))
        o.append(gr_text(en, (xa + xb) / 2, 6.8, "Dwgs.User", f"zone{i}t", 1.0))
        o.append(gr_text(en_parts, (xa + xb) / 2, -6.8, "Dwgs.User", f"zone{i}p", 0.5))
    # 패드 구역
    J = Pc["jst"]
    for key, (xa, xb), (yb, yt), lab in (("wp", J["x"], J["y"], "J3 JST SH 4P SM04B-SRSS-TB (side entry <- front)"),
                                         ("cp", Pc["gh"]["x"], Pc["gh"]["y"], "J1 JST GH 8P SM08B-GHS-TB (side entry -> rear)")):
        o.append(gr_rect(xa, yt, xb, yb, "Dwgs.User", key))
        o.append(gr_text(lab, (xa + xb) / 2, yb - 0.8, "Dwgs.User", key + "t", 0.5))
    # PCB 마킹 (실크): 프로젝트 번호 = 파일명. 아랫면(B.SilkS, 거울 글자), 보드 가운데
    xm = (Pc["zones"][0][2] + Pc["zones"][-1][3]) / 2
    a, b = K(xm, 0)
    o.append(f'  (gr_text "{PROJECT}" (at {a} {b}) (layer "B.SilkS") (tstamp {uid("mark")})\n'
             f'    (effects (font (size 1.2 1.2) (thickness 0.18)) (justify mirror)))')
    # 부품 높이 한계 (Cmts.User)
    y = -14.0
    o.append(gr_text("Component height limit per side (incl. 0.5 margin):", F0 + 20, y, "Cmts.User", "hl0", 0.8))
    for i, (x0, x1, w) in enumerate(Pc["sections"]):
        bore = P.HOUSING["id"] if w > 20 else P.BODY["cbore"]["d"]
        edge = math.sqrt((bore / 2) ** 2 - (w / 2) ** 2) - Pc["t"] / 2 - 0.5
        ctr = bore / 2 - Pc["t"] / 2 - 0.5
        o.append(gr_text(f"{x0 - F0:g}-{x1 - F0:g} mm: width {w:g}, bore {bore:g} -> edge {edge:.1f} / center {ctr:.1f} mm",
                         F0 + 20, y - 1.4 * (i + 1), "Cmts.User", f"hl{i + 1}", 0.7))
    o.append(")")
    return "\n".join(o) + "\n"


def main():
    open(OUT, "w", encoding="utf-8").write(build())
    print(OUT)


if __name__ == "__main__":
    main()
