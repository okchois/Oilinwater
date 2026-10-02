"""HMT500(260313) 조립 시뮬레이션 — 조립도 주기 5의 순서(개선안 A–F 반영)를 한 단계씩 실제 형상으로 따라가며 검사.

  python hardware/mech/assembly_sim.py
    → hardware/mech/out/assembly_sim/report.json   (단계별 검사 결과)
    → hardware/mech/out/assembly_sim/*.png          (문제 장면 그림)

형상: hmt500_cad.py (기구) + PCB 실제 배치 (hardware/kicad/HMT500(ED260313A)/placement.json, 부품 = Fab 외형 × 높이).
방법: 움직이는 부품·공구를 경로를 따라 여러 위치에 놓고 정지 부품과의 겹침 부피·최소 거리를 계산한다.
      (나사산은 골지름 원통, 플러그·공구는 외형 상자·원통으로 단순화)
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cadquery as cq  # noqa: E402

import hmt500_cad as M  # noqa: E402
import hmt500_params as P  # noqa: E402

OUT = os.path.join(M.OUT, "assembly_sim")
PLACEMENT = os.path.join(HERE, "..", "kicad", "HMT500(ED260313A)", "placement.json")
T = P.PCB["t"]

# ── 가정 (구매품 치수 개략 — 데이터시트 확인 전) ──
PLUG1 = dict(lx=4.25, wy=5.0, hz=2.8)     # JST SHR-04V-S 꽂힌 상태 외형 (params HARNESS plug와 같은 크기)
PLUG2 = dict(lx=4.0, wy=11.8, hz=3.5)     # JST GHR-08V-S
DRIVER_D = 3.0                            # M2 나사용 드라이버 날 지름 (정밀 드라이버)
TWEEZER = dict(w=2.0, t=1.2)              # 핀셋 끝 단면
SCREW_HEAD = dict(d=3.8, k=1.3)           # M2 냄비머리 (ISO 14580 급)

results = []


def check(step, item, ok, value, note="", level=None):
    lv = level or ("OK" if ok else "NG")
    results.append(dict(step=step, item=item, verdict=lv, value=value, note=note))
    print(f"[{lv:4s}] {step} | {item}: {value}" + (f"  — {note}" if note else ""))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def zcyl(x, y, z0, z1, d):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def xcyl(y, z, x0, x1, d):
    return M.axial_hole(x0, x1, y, z, d)


def vol(a, b):
    try:
        return a.val().intersect(b.val()).Volume()
    except Exception:
        return float("nan")


def dist(a, b):
    return a.val().distance(b.val())


def union(items):
    s = None
    for it in items:
        s = it if s is None else s.union(it)
    return s


# ── PCB 실제 배치 ──
PL = json.load(open(PLACEMENT, encoding="utf-8"))
PARTS = {p["ref"]: p for p in PL["parts"]}


def part_solid(p):
    if p["h"] <= 0:
        return None
    x0, y0, x1, y1 = p["fab"]
    s = 1 if p["side"] == "T" else -1
    z0, z1 = sorted((s * T / 2, s * (T / 2 + p["h"])))
    return box(x0, x1, y0, y1, z0, z1)


def part_rmax(p):
    """부품 외형 상자의 축에서 최대 거리."""
    x0, y0, x1, y1 = p["fab"]
    return math.hypot(max(abs(y0), abs(y1)), T / 2 + p["h"])


def parts_in(xa, xb, refs=None):
    return [p for p in PL["parts"] if p["fab"][2] > xa and p["fab"][0] < xb and (refs is None or p["ref"] in refs)]


def polyline_len(pts):
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


def main():
    os.makedirs(OUT, exist_ok=True)
    body, holder, ring, housing, endcap, pcb = M.body(), M.pcb_holder(), M.pcb_ring(), M.housing(), M.endcap(), M.pcbs()
    solids = {r: part_solid(p) for r, p in PARTS.items()}
    board = pcb.union(union([s for s in solids.values() if s is not None]))
    cw = M.chassis_wire()
    Hh, Bd, Rg, Hs = P.PCB_HOLDER, P.BODY, P.PCB_RING, P.HOUSING

    # ════ 1. W-1 플러그를 바디 앞에서 Ø7 통로로 넣어 뒤로 뺌 ════
    diag = math.hypot(PLUG1["wy"], PLUG1["hz"]) / 2
    r_min = min(Bd["channel"]["d"], Bd["conn_thread"]["d"]) / 2
    moving = union([box(x - PLUG1["lx"] / 2, x + PLUG1["lx"] / 2, -PLUG1["wy"] / 2, PLUG1["wy"] / 2,
                        -PLUG1["hz"] / 2, PLUG1["hz"] / 2) for x in range(int(Bd["gthread"]["x"][0]), 13, 3)])
    v = vol(moving, body)
    check("1 W-1 플러그 → Ø7 통로", "플러그 대각 반경 vs 최소 통로 반경", v < 1e-3,
          f"{diag:.2f} / {r_min:.2f} mm (여유 {r_min - diag:.2f}), 겹침 {v:.3f} mm³",
          "어느 각도로 돌아도 통과. 커넥터 체결 때 플러그가 따라 돌아 꼬임 없음")

    # ════ 2. [벤치] PCB를 홀더 홈에 끼우고 가로 나사 M2×12 ════
    c = Hh["cross"]
    for y in c["y"]:
        zs = math.sqrt((Hh["d"] / 2) ** 2 - y ** 2)
        drv = zcyl(c["x"], y, zs + SCREW_HEAD["k"], 60, DRIVER_D)
        v = vol(drv, holder.union(board))
        check("2 [벤치] PCB 가로 나사 M2×12 (홀더가 바디 밖)", f"드라이버 z 방향 (y {y:+g})", v < 1e-3,
              f"홀더 바깥면 z {zs:.2f} 위로 막힘 없음", "나사 머리는 홀더 면에 묻음. 끝은 반대 면 안쪽 (홀더 두께 %.1f)" % (2 * zs))

    # ════ 3. W-1 플러그를 홀더 창으로 꿴 (PCB가 홈에 있는 상태) ════
    w = Hh["window"]
    zc = (w["z"][0] + w["z"][1]) / 2
    moving = union([box(x, x + PLUG1["lx"], -PLUG1["wy"] / 2, PLUG1["wy"] / 2, zc - PLUG1["hz"] / 2, zc + PLUG1["hz"] / 2)
                    for x in (Hh["x"][0] - 5, Hh["x"][0] - 1, (Hh["x"][0] + Hh["x"][1]) / 2 - 2, Hh["x"][1] - 2)])
    v = vol(moving, holder.union(pcb))
    d = dist(moving, holder.union(pcb))
    check("3 W-1 플러그 → 홀더 창 (PCB 장착 상태)", f"창 {w['wy']:g} × {w['z'][1] - w['z'][0]:g} vs 플러그", v < 1e-3,
          f"최소 거리 {d:.2f} mm (폭 여유 {(w['wy'] - PLUG1['wy']) / 2:.2f}, 높이 여유 {(w['z'][1] - w['z'][0] - PLUG1['hz']) / 2:.2f})",
          "제안 A: PCB를 먼저 끼워도 플러그가 지나감")

    # ════ 4. 홀더+PCB를 바디 카운터보어에 넣음 ════
    inside = [p for p in PL["parts"] if p["fab"][0] < Bd["cbore"]["x"][1]]
    worst = max((part_rmax(p), p["ref"]) for p in inside) if inside else (0, "-")
    v = vol(holder.union(board), body)
    check("4 홀더+PCB → 카운터보어 Ø22", f"앞쪽(x < {Bd['cbore']['x'][1]:g}) 부품 최대 반경 vs {Bd['cbore']['d'] / 2:g}, 형상 교차", v < 1e-3 and worst[0] < 10.8,
          f"{worst[0]:.2f} mm ({worst[1]}), 겹침 {v:.3f} mm³")

    # ════ 5. 홀더 축 나사 M2 (뒤에서) — 위쪽은 샤시 선 링 단자 함께 ════
    x_face = Hh["x"][1]
    for sgn in (1, -1):
        z = sgn * Hh["screw_pcd"] / 2
        drv = xcyl(0, z, x_face + SCREW_HEAD["k"] + 0.8, 120, DRIVER_D)
        obst = board.union(cw) if sgn > 0 else board
        vb = vol(drv, obst)
        d = dist(drv, obst)
        check("5 홀더 축 나사 (뒤에서, 드라이버 Ø%g)" % DRIVER_D, f"경로 z={z:+g} vs PCB·부품" + (" ·샤시 선" if sgn > 0 else ""),
              vb < 1e-3, f"최소 거리 {d:.2f} mm", "M2×8 + 링 단자 (카운터보어 Ø%g × %g)" % (Hh["cbore_d"], Hh["cbore_depth"])
              if sgn > 0 else "M2×6")
    C = P.CHASSIS_WIRE
    j5 = PARTS["J5"]
    xp, yp = j5["pads"][0]["xy"]
    path = [(xp, yp, T / 2), (xp, yp, 3.0), (x_face + 2.5, yp * 0.4, C["screw_z"] - 1.5), (x_face + 0.9, 0, C["screw_z"] - 2.2)]
    L = polyline_len(path) + 3.0
    check("5 샤시 선 (J5 → 링 단자)", "필요 길이 vs 선 길이", L < C["length"],
          f"{L:.1f} / {C['length']:g} mm (J5 x {xp:.1f}, y {yp:.1f})", "선은 W-1 창 위를 지남 (y 0, z 3–8)")
    vw = vol(cw, board.subtract(solids["J5"]) if solids.get("J5") else board)
    check("5 샤시 선", "선·링 단자 vs 부품", vw < 0.05, f"겹침 {vw:.3f} mm³")

    # ════ 6. W-1 플러그를 J3에 꽂음 (x 22.5 → 26.5) ════
    pl = P.HARNESS["plug"]
    stroke = 4.0
    moving = union([box(pl["x"][0] - s_, pl["x"][1] - s_, pl["y"][0], pl["y"][1], pl["z"][0], pl["z"][1])
                    for s_ in (stroke, stroke / 2, 0.0)])
    others = union([solids[r] for r in PARTS if r != "J3" and solids[r] is not None and PARTS[r]["side"] == "T"])
    v1, v2, v3, v4 = vol(moving, others), vol(moving, body), vol(moving, holder), vol(moving, cw)
    check("6 W-1 플러그 → J3 (꽂는 거리 4 mm)", "경로 vs 윗면 부품·바디·홀더·샤시 선", max(v1, v2, v3, v4) < 1e-3,
          f"겹침 {v1:.3f} / {v2:.3f} / {v3:.3f} / {v4:.3f} mm³", "카운터보어 입구에서 핀셋으로 (위쪽 공간 7.4 mm)")
    Lw1 = P.HARNESS["length"]
    xpin = P.SENSOR_CONN["x0"] - P.SENSOR_CONN["pin_y"]
    in_channel = Bd["channel"]["x"][1] - xpin
    span = pl["x"][0] - Bd["channel"]["x"][1]
    need = Bd["cbore"]["x"][1] + (Hh["x"][1] - Hh["x"][0]) + PLUG1["lx"] - Bd["channel"]["x"][1]
    check("6 W-1 길이", "통로 안 / 통로 끝~J3 / 남는 길이", in_channel + need <= Lw1,
          f"{in_channel:.0f} / {span:.1f} / {Lw1 - in_channel - span:.1f} mm (L {Lw1:g})",
          f"창에 꿸 때 통로 끝에서 {need:.0f} mm 필요 → 60 유지. 남는 선은 PCB 앞 윗면 고리 (아래는 높이 0 부품 J2)")

    # ════ 7. 지지링을 PCB 뒤에서 끼움 (PCB 뒤 끝 → 링 자리) ════
    r_in = Rg["id"] / 2
    rear = parts_in(Rg["x"][0], P.PCB["x"][1])
    worst = max((part_rmax(p), p["ref"]) for p in rear)
    check(f"7 지지링 끼움 (Ø{Rg['id']:g}이 x {P.PCB['x'][1]:g} → {Rg['x'][0]:g}로 지나감)", "뒤쪽 부품 최대 반경 vs 10 (외형 상자)", worst[0] < r_in - 0.3,
          f"{worst[0]:.2f} mm ({worst[1]})", "배치 규칙 C: 링 뒤 부품은 Ø20 기준")
    sweep = union([ring.translate((dx, 0, 0)) for dx in (8.0, 4.0, 0.0)])
    v = vol(sweep, board)
    check("7 지지링 끼움", "링 경로 vs PCB·부품 (형상 교차)", v < 1e-3, f"겹침 {v:.2f} mm³")

    # ════ 8. 하우징을 PCB 위로 씌움 (턴버클 시작 위치: 7 mm 뒤) ════
    tl = Hs["thread_len"]
    r_b = Hs["thread_minor"] / 2
    worst = max((part_rmax(p), p["ref"]) for p in PL["parts"] if p["fab"][2] > Hs["x"][0])
    check("8 하우징 씌움 (뒤에서 앞으로)", "부품 최대 반경 vs 하우징 최소 반경 %.2f" % r_b, worst[0] < r_b - 0.2,
          f"{worst[0]:.2f} mm ({worst[1]}), 링 바깥 {Rg['od'] / 2:.2f}", f"링 Ø{Rg['od']:g} vs 나사 골 Ø{Hs['thread_minor']:.2f}: 반경 여유 {(Hs['thread_minor'] - Rg['od']) / 2:.2f}")

    # ════ 9. W-2 플러그를 밀대 T-001로 하우징 뒤 입구에서 J1에 꽂음 ════
    h_pre = housing.translate((tl, 0, 0))
    x_rear = Hs["x"][1] + tl
    p2 = P.HARNESS2["plug"]
    depth = x_rear - p2["x"][1]
    tool = M.push_tool()
    moving = union([box(p2["x"][0] + s_, p2["x"][1] + s_, p2["y"][0], p2["y"][1], p2["z"][0], p2["z"][1])
                    for s_ in (20.0, 10.0, 4.0, 0.0)])
    others = union([ring, h_pre] + [solids[r] for r in PARTS if r != "J1" and solids[r] is not None])
    v = vol(moving, others)
    vt = vol(tool, others.union(pcb))
    dt = dist(tool, others.union(pcb))
    check("9 W-2 플러그 → J1 (하우징 안 %.1f mm)" % depth, "플러그 경로 vs 링·하우징·부품", v < 1e-3, f"겹침 {v:.3f} mm³")
    check("9 밀대 T-001 (J1에 다 밀어 넣은 순간)", "밀대 vs 링·하우징·PCB·부품", vt < 1e-3,
          f"최소 거리 {dt:.2f} mm, 겹침 {vt:.3f} mm³", "끝이 플러그 양쪽 턱을 밀고 가운데 홈(%.1f)으로 선이 지나감" % P.PUSH_TOOL["slot_w"])
    Lw2 = P.HARNESS2["length"]
    x_m12 = P.CONNECTOR["inner"]["x"][0]
    span_fin = math.hypot(x_m12 - p2["x"][1], (p2["z"][0] + p2["z"][1]) / 2)
    need2 = depth + 15.0
    check("9 W-2 길이", "꽂을 때 필요 / 체결 후 직선 / 남는 길이", Lw2 >= need2,
          f"{need2:.0f} / {span_fin:.1f} / {Lw2 - span_fin:.0f} mm (L {Lw2:g})",
          "남는 선은 턴버클 때 J1 뒤(윗면 부품 금지 구역)~엔드캡 안에서 한 번 접힘", level=None if Lw2 >= need2 else "NG")

    # ════ 10. 턴버클: 하우징만 7바퀴 → 바디 쪽 7 mm, 엔드캡 14 mm 접근 ════
    board_all = board.union(ring)
    for dx in (14.0, 7.0, 2.0, 0.0):
        e = endcap.translate((dx, 0, 0))
        v = vol(e, board_all)
        d = dist(e, board_all)
        check("10 턴버클 (엔드캡 이동)", f"엔드캡 {dx:>4g} mm 앞 → PCB·부품·링", v < 1e-3 and d >= 0.3,
              f"최소 거리 {d:.2f} mm, 겹침 {v:.2f} mm³", f"제안 B: PCB 계단 x {P.PCB['sections'][1][1]:g}" if dx == 0 else "")
    hv = vol(housing, board_all)
    hd = dist(housing, board_all)
    check("10 턴버클 (체결 후)", "하우징 vs PCB·부품·링", hv < 1e-3, f"최소 거리 {hd:.2f} mm")

    # ════ 11. 2차 몰딩 ════
    check("11 2차 몰딩 (M12 위, M3 구멍 주입)", "흐름 경로 (형상 설명, 유동 시험 아님)", True,
          f"엔드캡 Ø{P.ENDCAP['cbore']['d']:g} → 링 안(Ø{Rg['id']:g}) → 하우징 Ø{Hs['id']:g} → 홀더 뒤. "
          f"링 바깥 {(Hs['id'] - Rg['od']) / 2:.2f} mm 틈은 좁아 공기 빼기는 링 안쪽으로",
          "PCB가 세로로 서 있어 양면이 같이 참. J1·J3 플러그 몸체 안 오목한 곳은 진공 주입 권장", level="WARN")

    # Rev I: 원래 검사에서 빠진 구매품·공구·공차 조건을 명시적으로 검사.
    ec, cn = P.ENDCAP, P.CONNECTOR
    for angle in ec["ports"]["angles"]:
        a = math.radians(angle)
        y, z = ec["ports"]["r"] * math.cos(a), ec["ports"]["r"] * math.sin(a)
        access = M.endcap_port(angle, ec["flange"]["x"][1], cn["body"]["x"][1] + 10, ec["ports"]["access_d"])
        v = vol(access, M.connector())
        d = dist(access, M.connector())
        check("12 M3 주입·마감 공구 접근", f"경사 20° 공구 Ø{ec['ports']['access_d']:g}, 원주 {angle}°", v < 1e-3 and d >= ec["ports"]["access_clearance"],
              f"최소거리 {d:.3f} mm, 겹침 {v:.6f} mm³", "M12 어깨 Ø20 개략 형상 조건. 실제 품번 확인 필요")
    thick_max = P.PCB["t"] + P.PCB["t_tol"]
    for name, support in (("홀더", P.PCB_HOLDER), ("지지링", P.PCB_RING)):
        gap = support["slot_w"] - thick_max
        check("13 PCB 두께 최악 공차", name, gap >= P.PCB["slot_clearance"],
              f"최소 홈 {support['slot_w']:.2f} - 최대 PCB {thick_max:.2f} = {gap:.2f} mm")
    sp = P.SENSOR_PROBE
    needed = 0.3 + sp["mk33"]["l"] + 0.6 + sp["pt1000"]["l"]
    check("14 300pF 센서 캐리어", "소자 길이와 캐리어", needed <= sp["board"]["x"][1] - sp["board"]["x"][0],
          f"필요 {needed:.2f}, 캐리어 {sp['board']['x'][1] - sp['board']['x'][0]:.2f} mm", "IST Au/Cu 300pF 외형 기준; 공급 품번/접합 방식 확인 필요")
    vs = vol(M.sensor_elements(), M.cap())
    check("14 300pF 센서 외형", "보호캡과 교차", vs < 1e-3, f"겹침 {vs:.6f} mm³")
    slope = math.tan(math.radians(ec["ports"]["tilt_deg"]))
    r_inner = ec["ports"]["r"] + (ec["cbore"]["x"][1] - 0.5 - ec["flange"]["x"][1]) * slope
    exit_outer = r_inner + ec["ports"]["d_minor"] / 2 * math.sqrt(1+slope*slope)
    check("15 M3 내부 연결", "경사 구멍 끝이 Ø22 공간에 완전히 열림", exit_outer < ec["cbore"]["d"]/2,
          f"출구 최대 반경 {exit_outer:.3f} / 보어 반경 11 mm", "실제 점도/노즐/주입 시험 필요")
    # 나사 대경 Ø3을 전 길이에 적용해도 홈과 겹치지 않아야 함 (실제 탭 깊이는 입구 4 mm).
    rg = ec["ports"]["r"] + (ec["seal"]["groove_x"][1] - ec["flange"]["x"][1]) * slope
    web = P.ORING["groove_d"]/2 - (rg + 1.5 * math.sqrt(1+slope*slope))
    check("16 몰딩 구멍–O링 홈", "대경 Ø3 보수 외형 사이 살 두께", web >= 0.5,
          f"명목 최소 {web:.3f} mm", "가공 공차 포함 잔여 두께는 제작사 DFM 확인")

    json.dump(dict(placement=PL["meta"]["project"], results=results), open(os.path.join(OUT, "report.json"), "w"),
              ensure_ascii=False, indent=1)
    ng = sum(1 for r in results if r["verdict"] == "NG")
    wn = sum(1 for r in results if r["verdict"] == "WARN")
    print(f"\n{len(results)} checks: NG {ng}, WARN {wn}")
    if ng:
        raise RuntimeError(f"Assembly validation failed: {ng} NG")
    return dict(body=body, holder=holder, ring=ring, housing=housing, endcap=endcap, pcb=pcb, solids=solids, cw=cw)


# ════ 3D 절단 그림: 조립 완료 상태 (윗 절반 금속 제거, 실제 PCB 배치) ════
def render_cutaway(sh, out, side="T"):
    import vtk
    from render3d import actor_for
    s = 1 if side == "T" else -1
    cutter = box(-100, 200, -40, 40, *sorted((0.0, s * 40.0)))    # 보는 쪽 절반 제거 (금속·수지)
    scene = [(sh["body"].cut(cutter), (0.72, 0.74, 0.78), 1.0), (sh["housing"].cut(cutter), (0.82, 0.84, 0.88), 1.0),
             (sh["endcap"].cut(cutter), (0.72, 0.74, 0.78), 1.0), (sh["holder"].cut(cutter), (0.85, 0.72, 0.45), 1.0),
             (sh["ring"].cut(cutter), (0.85, 0.72, 0.45), 1.0), (M.connector().cut(cutter), (0.35, 0.35, 0.38), 1.0),
             (sh["pcb"], (0.10, 0.45, 0.20), 1.0)]
    for r, so in sh["solids"].items():
        if so is not None and PARTS[r]["side"] == side:
            col = (0.93, 0.90, 0.80) if r in ("J1", "J3") else (0.18, 0.18, 0.2)
            scene.append((so, col, 1.0))
    if side == "T":
        scene += [(sh["cw"], (0.30, 0.65, 0.25), 1.0),
                  (M.harness(), (0.92, 0.92, 0.90), 1.0), (M.harness_plug(), (0.93, 0.90, 0.80), 1.0),
                  (M.harness2(), (0.92, 0.92, 0.90), 1.0), (M.harness2_plug(), (0.93, 0.90, 0.80), 1.0)]
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    for so, col, op in scene:
        ren.AddActor(actor_for(so, col, op))
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(ren)
    win.SetSize(2000, 800)
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(45, 0, 0)
    cam.SetPosition(45, -60, s * 160)
    cam.SetViewUp(0, 1, 0)
    ren.ResetCamera()
    cam.Zoom(2.3)
    light = vtk.vtkLight()
    light.SetPosition(40, -100, s * 300)
    light.SetFocalPoint(40, 0, 0)
    ren.AddLight(light)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(out)
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()
    print(out)


if __name__ == "__main__":
    sh = main()
    if "--no-render" not in sys.argv:
        render_cutaway(sh, os.path.join(OUT, "assembled_top.png"), "T")
        render_cutaway(sh, os.path.join(OUT, "assembled_bottom.png"), "B")
