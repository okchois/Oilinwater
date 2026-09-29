"""DOTECH HMT500 3D CAD 모델 (CadQuery). 파라미터: hmt500_params.py

  pip install cadquery
  python hardware/mech/hmt500_cad.py   →  hardware/mech/out/*.step  (음영 렌더: render3d.py)

나사는 표현용(원통)이며 규격은 2D 도면에 표기한다.
"""

import math
import os

import cadquery as cq

import hmt500_params as P

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def revolve(profile):
    """profile: [(x, r), ...] 닫힌 단면(축 포함 또는 링). x축 기준 회전체."""
    return cq.Workplane("XY").polyline(profile).close().revolve(360, (0, 0, 0), (1, 0, 0))


def cyl(x0, x1, d):
    return revolve([(x0, 0), (x1, 0), (x1, d / 2), (x0, d / 2)])


def tube(x0, x1, d_out, d_in):
    return revolve([(x0, d_in / 2), (x1, d_in / 2), (x1, d_out / 2), (x0, d_out / 2)])


def body():
    B = P.BODY
    solid = cyl(*B["tube"]["x"], B["tube"]["d"])
    for k in ("gthread", "relief", "collar", "seal", "mthread"):
        solid = solid.union(cyl(*B[k]["x"], B[k]["d"]))
    g0, g1 = B["seal"]["groove_x"]
    solid = solid.cut(tube(g0, g1, B["seal"]["d"] + 1, P.ORING["groove_d"]))       # O링 홈
    # 육각 + 30° 모따기 (원추와 교차)
    h = B["hexa"]
    x0, x1 = h["x"]
    dc = P.hex_corner_d(h["af"])
    hexa = cq.Workplane("YZ").workplane(offset=x0).polygon(6, dc).extrude(x1 - x0)
    t = math.tan(math.radians(h["chamfer_angle"]))
    r_af = h["af"] / 2
    c = (dc / 2 - r_af) / t
    cham = revolve([(x0, 0), (x1, 0), (x1, r_af), (x1 - c, dc / 2 + 0.01), (x0 + c, dc / 2 + 0.01), (x0, r_af)])
    solid = solid.union(hexa.intersect(cham))
    # 내부
    for k in ("conn_cbore", "conn_land", "conn_thread", "channel", "cbore"):
        solid = solid.cut(cyl(*B[k]["x"], B[k]["d"]))
    # PCB 홀더 고정 M2 탭 (카운터보어 바닥, z = ±PCD/2 — PCB 평면에 수직 방향)
    T = B["holder_taps"]
    x_bot = B["cbore"]["x"][0]
    for sgn in (1, -1):
        solid = solid.cut(axial_hole(x_bot - T["depth"], x_bot + 0.01, 0, sgn * T["pcd"] / 2, T["d"] * 0.8))
    return solid


def axial_hole(x0, x1, y, z, d):
    return cq.Workplane("YZ").workplane(offset=x0).center(y, z).circle(d / 2).extrude(x1 - x0)


def cap():
    """보호캡 = 두텍 SUS 오일 필터 390000-001100 (반단면 윤곽 회전 + 측면 구멍 20개)."""
    C = P.CAP
    s = revolve(C["profile"])
    for x, ang in C["holes"]:
        a = math.radians(ang)
        d = (0, math.cos(a), math.sin(a))
        hole = cq.Workplane(cq.Plane(origin=(x, 0, 0), xDir=(1, 0, 0), normal=d)).circle(C["hole_d"] / 2).extrude(C["od"])
        s = s.cut(hole)
    return s


def housing():
    H = P.HOUSING
    x0, x1 = H["x"]
    s = tube(x0, x1, H["od"], H["id"])
    for a, b, sgn in ((x0, x0 + H["seal_len"], 1), (x1 - H["seal_len"], x1, -1)):
        s = s.cut(cyl(a - 0.01, b + 0.01, H["seal_bore"]))
    s = s.cut(cyl(x0 + H["seal_len"], x0 + H["seal_len"] + H["thread_len"], H["thread_minor"]))
    s = s.cut(cyl(x1 - H["seal_len"] - H["thread_len"], x1 - H["seal_len"], H["thread_minor"]))
    return s


def endcap():
    E = P.ENDCAP
    s = cyl(*E["mthread"]["x"], E["mthread"]["d"]).union(cyl(*E["seal"]["x"], E["seal"]["d"])).union(
        cyl(*E["flange"]["x"], E["flange"]["d"]))
    g0, g1 = E["seal"]["groove_x"]
    s = s.cut(tube(g0, g1, E["seal"]["d"] + 1, P.ORING["groove_d"]))
    f0, f1 = E["flange"]["x"]
    for sgn in (1, -1):   # 렌치 평면 AF28
        slab = cq.Workplane("XY").box(f1 - f0 + 0.2, 10, 40).translate(((f0 + f1) / 2, sgn * (E["flange"]["flats_af"] / 2 + 5), 0))
        s = s.cut(slab)
    s = s.cut(cyl(E["cbore"]["x"][0] - 0.1, E["cbore"]["x"][1], E["cbore"]["d"]))
    Po = E["ports"]                                  # 몰딩 주입·공기 빠짐 구멍 M3 ×2 (축 방향, 플랜지 관통)
    for ang in Po["angles"]:
        a = math.radians(ang)
        s = s.cut(axial_hole(E["cbore"]["x"][1] - 0.5, f1 + 0.1, Po["r"] * math.cos(a), Po["r"] * math.sin(a), Po["d_minor"]))
    return s.cut(cyl(E["thread"]["x"][0] - 0.1, f1 + 0.1, E["thread"]["d_minor"]))


def potting2():
    """하우징 안 전체 에폭시 몰딩 (PCB·부품·홀더·지지링·하네스·커넥터 뒤를 뺀 공간)."""
    z = P.POTTING2["zones"]
    s = cyl(*z[0][:2], z[0][2] - 0.02)
    for x0, x1, d in z[1:]:
        s = s.union(cyl(x0, x1, d - 0.02))
    for fn in (pcbs, pcb_parts, pcb_holder, pcb_ring, harness, harness_plug, harness2, harness2_plug, connector):
        s = s.cut(fn())
    return s


def orings():
    O = P.ORING
    out = None
    for g in (P.BODY["seal"]["groove_x"], P.ENDCAP["seal"]["groove_x"]):
        c = (g[0] + g[1]) / 2
        r0 = O["groove_d"] / 2 + O["cs"] / 2 - 0.15
        ring = cq.Workplane("XY").add(cq.Solid.makeTorus(r0, O["cs"] / 2, cq.Vector(c, 0, 0), cq.Vector(1, 0, 0)))
        out = ring if out is None else out.union(ring)
    return out


def seal():
    S = P.SEAL
    return tube(*S["x"], S["od"], S["id"])


def potting():
    """Ø7 관통 통로 전 길이 에폭시 몰딩 (W-1 전선 매립, 1차 격벽)."""
    Pt = P.POTTING
    return cyl(*Pt["x"], Pt["d"] - 0.02)


_CONN = {}


def sensor_connector():
    """두텍 HTX99R 센서 커넥터 STEP을 제품 좌표로 배치: 커넥터 y축 → 제품 −x, y=0 면이 x0."""
    if "s" not in _CONN:
        S = P.SENSOR_CONN
        s = cq.importers.importStep(os.path.join(os.path.dirname(os.path.abspath(__file__)), S["step"]))
        s = s.rotate((0, 0, 0), (0, 0, 1), 90).translate((S["x0"], 0, 0))
        _CONN["s"] = s
    return _CONN["s"]


def conn_oring():
    S, O = P.SENSOR_CONN, P.CONN_ORING
    y0, y1 = S["oring_groove"]["y"]
    c = S["x0"] - (y0 + y1) / 2
    r0 = S["oring_groove"]["d"] / 2 + O["cs"] / 2 - 0.15
    return cq.Workplane("XY").add(cq.Solid.makeTorus(r0, O["cs"] / 2, cq.Vector(c, 0, 0), cq.Vector(1, 0, 0)))


def sensor_probe():
    """교체형 센서 프로브: 수지 플러그 + 핀 4개 + 센서 기판 (기판 평면 = XY)."""
    SP = P.SENSOR_PROBE
    s = cyl(*SP["plug"]["x"], SP["plug"]["d"])
    h = SP["pins"]["pitch"] / 2
    for y in (-h, h):
        for z in (-h, h):
            s = s.union(cq.Workplane("YZ").workplane(offset=SP["pins"]["x"][0]).center(y, z)
                        .circle(SP["pins"]["d"] / 2).extrude(SP["pins"]["x"][1] - SP["pins"]["x"][0]))
    b = SP["board"]
    x0, x1 = b["x"]
    s = s.union(cq.Workplane("XY").box(x1 - x0 + 1.0, b["w"], b["t"]).translate(((x0 + x1) / 2 + 0.5, 0, 0)))
    return s


def sensor_elements():
    SP = P.SENSOR_PROBE
    b, mk, pt = SP["board"], SP["mk33"], SP["pt1000"]
    x0 = b["x"][0] + 0.3
    z = b["t"] / 2
    m = cq.Workplane("XY").box(mk["l"], mk["w"], mk["t"]).translate((x0 + mk["l"] / 2, -0.8, z + mk["t"] / 2))
    t = cq.Workplane("XY").box(pt["l"], pt["w"], pt["t"]).translate((x0 + mk["l"] + 0.6 + pt["l"] / 2, 1.6, z + pt["t"] / 2))
    return m.union(t)


def pcb_outline_pts():
    """PCB 외곽 (x, y) — 앞→뒤 위쪽 가장자리, 뒤→앞 아래쪽 가장자리."""
    up = []
    for x0, x1, w in P.PCB["sections"]:
        up += [(x0, w / 2), (x1, w / 2)]
    return up + [(x, -y) for x, y in reversed(up)]


def pcbs():
    Pc = P.PCB
    t = Pc["t"]
    b = cq.Workplane("XY").polyline(pcb_outline_pts()).close().extrude(t).translate((0, 0, -t / 2))
    try:
        b = b.edges("|Z").fillet(Pc["corner_r"] * 0.5)
    except Exception:
        pass
    for x, y in Pc["holes"]:
        b = b.cut(cq.Workplane("XY").center(x, y).circle(Pc["hole_d"] / 2).extrude(4).translate((0, 0, -2)))
    return b


def pcb_parts():
    out = None
    t = P.PCB["t"]
    for x, y, a, b, h, side in P.PCB_PARTS:
        z = side * (t / 2 + h / 2)
        bx = cq.Workplane("XY").box(a, b, h).translate((x, y, z))
        out = bx if out is None else out.union(bx)
    return out


def harness_paths():
    """W-1 전선 경로: HTX99R 뒤 핀 → Ø7 관통 통로 → 홀더 Ø6 구멍 (PCB 위) → 곧게 J3 플러그 뒤(-x 면)."""
    W, S = P.HARNESS, P.SENSOR_CONN
    xp = S["x0"] - S["pin_y"]                     # 커넥터 뒤 핀 끝
    g = W["conn_grid"] / 2
    pins = sorted([(-g, -g), (-g, g), (g, -g), (g, g)], key=lambda p: (p[0], p[1]))   # y 순서 = 플러그 1→4
    n = len(pins)
    out = []
    for k, (yp, zp) in enumerate(pins):
        yk = (k - (n - 1) / 2) * W["pitch"]
        gz = W["gap_z"]
        out.append([(xp, yp, zp), (xp + 4.0, yp * 0.8, zp * 0.5 + 1.0), (P.BODY["channel"]["x"][1] - 1.0, yk, gz),
                    (W["plug"]["x"][0], yk, gz)])        # 옆 삽입 J3: 홀더 구멍에서 곧게 플러그로
    return out


def harness2_paths():
    """W-2 전선 경로: J1 GH 플러그 뒤(+x) → 엔드캡 카운터보어 → M12 커넥터 뒤면 핀 (1–7 원주, 8 가운데)."""
    W = P.HARNESS2
    pl = W["plug"]
    zc = (pl["z"][0] + pl["z"][1]) / 2
    x_face = P.CONNECTOR["inner"]["x"][0]
    out = []
    for n in range(1, 9):
        yk = (n - 4.5) * W["pitch"]
        if n == 8:
            py, pz = 0.0, 0.0
        else:
            a = math.radians(90 + (n - 1) * 360 / 7)
            py, pz = W["conn_pcd"] / 2 * math.cos(a), W["conn_pcd"] / 2 * math.sin(a)
        x_pcb = P.PCB["x"][1]
        out.append([(pl["x"][1], yk, zc), (66.0, yk * 0.8, W["wire_z"]), (x_pcb + 0.4, py * 0.8, W["wire_z"]),
                    (x_face - 0.7, py, pz), (x_face, py, pz)])     # PCB 끝을 지난 뒤 핀 높이로 내려감
    return out


def _wires(paths, d):
    r = d / 2
    out = None
    for path in paths:
        for p0, p1 in zip(path, path[1:]):
            v0, v1 = cq.Vector(*p0), cq.Vector(*p1)
            seg = cq.Solid.makeCylinder(r, (v1 - v0).Length, v0, v1 - v0)
            out = seg if out is None else out.fuse(seg)
        for p_ in path[1:-1]:
            out = out.fuse(cq.Solid.makeSphere(r, cq.Vector(*p_), angleDegrees1=-90, angleDegrees2=90))
    return cq.Workplane("XY").newObject([out.clean()])


def harness():
    return _wires(harness_paths(), P.HARNESS["wire_d"])


def harness2():
    return _wires(harness2_paths(), P.HARNESS2["wire_d"])


def harness2_plug():
    pl = P.HARNESS2["plug"]
    (x0, x1), (y0, y1), (z0, z1) = pl["x"], pl["y"], pl["z"]
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def harness_plug():
    Pl = P.HARNESS["plug"]
    (x0, x1), (y0, y1), (z0, z1) = Pl["x"], Pl["y"], Pl["z"]
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def pcb_holder():
    Hh = P.PCB_HOLDER
    x0, x1 = Hh["x"]
    s = cyl(x0, x1, Hh["d"]).cut(cyl(x0 - 0.1, x1 + 0.1, Hh["hole_d"]))
    s0, s1 = Hh["slot_x"]
    s = s.cut(cq.Workplane("XY").box(s1 - s0 + 0.1, Hh["d"] + 1, Hh["slot_w"]).translate(((s0 + s1) / 2 + 0.05, 0, 0)))
    for sgn in (1, -1):   # 바디 고정 나사 구멍 + 머리 자리
        s = s.cut(axial_hole(x0 - 0.1, x1 + 0.1, 0, sgn * Hh["screw_pcd"] / 2, Hh["screw_d"]))
        s = s.cut(axial_hole(x1 - Hh["cbore_depth"], x1 + 0.1, 0, sgn * Hh["screw_pcd"] / 2, Hh["cbore_d"]))
    c = Hh["cross"]
    for y in c["y"]:      # PCB 가로 고정 나사 (z 방향)
        s = s.cut(cq.Workplane("XY").center(c["x"], y).circle(c["d"] * 0.8 / 2).extrude(30).translate((0, 0, -15)))
    return s


def pcb_ring():
    R = P.PCB_RING
    s = tube(*R["x"], R["od"], R["id"])
    x0, x1 = R["x"]
    return s.cut(cq.Workplane("XY").box(x1 - x0 + 1, 2 * R["slot_y"], R["slot_w"]).translate(((x0 + x1) / 2, 0, 0)))


def connector():
    Cn = P.CONNECTOR
    s = cyl(*Cn["body"]["x"], Cn["body"]["d"]).union(cyl(*Cn["thread"]["x"], Cn["thread"]["d"]))
    s = s.union(cyl(*Cn["inner"]["x"], Cn["inner"]["d"]))   # M16 나사부 (엔드캡 안)
    return s.cut(cyl(Cn["thread"]["x"][1] - 8, Cn["thread"]["x"][1] + 0.1, 9.5))


PARTS = [
    ("M-101_body", body, (0.72, 0.74, 0.78)),
    ("M-102_cap", cap, (0.80, 0.82, 0.86)),
    ("M-103_housing", housing, (0.82, 0.84, 0.88)),
    ("M-104_endcap", endcap, (0.72, 0.74, 0.78)),
    ("P-209_epoxy", potting, (0.55, 0.45, 0.25)),
    ("P-209_potting", potting2, (0.62, 0.50, 0.28)),
    ("P-202_sensor_probe", sensor_probe, (0.78, 0.66, 0.46)),
    ("P-202_elements", sensor_elements, (0.95, 0.93, 0.85)),
    ("HTX99R-SC_connector", sensor_connector, (0.15, 0.15, 0.17)),
    ("P-208_conn_oring", conn_oring, (0.10, 0.10, 0.10)),
    ("P-203_seal", seal, (0.20, 0.65, 0.30)),
    ("P-205_orings", orings, (0.10, 0.10, 0.10)),
    ("E-301_pcb", pcbs, (0.10, 0.45, 0.20)),
    ("E-301_parts", pcb_parts, (0.15, 0.15, 0.17)),
    ("W-1_harness", harness, (0.92, 0.92, 0.90)),
    ("W-1_plug", harness_plug, (0.93, 0.90, 0.80)),
    ("W-2_harness", harness2, (0.92, 0.92, 0.90)),
    ("W-2_plug", harness2_plug, (0.93, 0.90, 0.80)),
    ("M-105_holder", pcb_holder, (0.85, 0.72, 0.45)),
    ("M-106_ring", pcb_ring, (0.85, 0.72, 0.45)),
    ("P-204_connector", connector, (0.35, 0.35, 0.38)),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    asm = cq.Assembly(name="HMT500")
    shapes = {}
    for name, fn, col in PARTS:
        s = fn()
        shapes[name] = s
        if name.startswith("M-"):
            cq.exporters.export(s, os.path.join(OUT, f"HMT500-{name}.step"))
        asm.add(s, name=name, color=cq.Color(*col))
    asm.save(os.path.join(OUT, "HMT500_assembly.step"))
    comp = cq.Workplane("XY").newObject([cq.Compound.makeCompound([s.val() for s in shapes.values()])])
    bb = comp.val().BoundingBox()
    print(f"assembly bbox x {bb.xmin:.1f}..{bb.xmax:.1f} (length {bb.xlen:.1f}), dia {bb.ylen:.1f}")
    for name, s in shapes.items():
        v = s.val().Volume()
        rho, mat = (1.32e-3, "PEEK") if name in ("M-105_holder", "M-106_ring") else (7.98e-3, "316L")
        print(f"  {name:18s} volume {v / 1000:7.2f} cm3" + (f"  mass({mat}) {v * rho:6.1f} g" if name.startswith("M-") else ""))


if __name__ == "__main__":
    main()
