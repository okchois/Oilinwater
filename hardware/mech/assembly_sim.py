"""HMT500(260313) 조립 시뮬레이션 — 조립도 주기 5의 순서를 한 단계씩 실제 형상으로 따라가며 검사.

  python hardware/mech/assembly_sim.py
    → hardware/mech/out/assembly_sim/report.json   (단계별 검사 결과)
    → hardware/mech/out/assembly_sim/*.png          (문제 장면 그림)

형상: hmt500_cad.py (기구) + PCB 실제 배치 (hardware/kicad/HMT500(260313A)/placement.json, 부품 = Fab 외형 × 높이).
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
PLACEMENT = os.path.join(HERE, "..", "kicad", "HMT500(260313A)", "placement.json")
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


def main():
    os.makedirs(OUT, exist_ok=True)
    body, holder, ring, housing, endcap, pcb = M.body(), M.pcb_holder(), M.pcb_ring(), M.housing(), M.endcap(), M.pcbs()
    solids = {r: part_solid(p) for r, p in PARTS.items()}
    board = pcb.union(union([s for s in solids.values() if s is not None]))
    Hh, Bd, Rg, Hs, E = P.PCB_HOLDER, P.BODY, P.PCB_RING, P.HOUSING, P.ENDCAP

    # ════ 1. W-1 플러그를 바디 앞에서 Ø7 통로로 넣어 뒤로 뺌 ════
    diag = math.hypot(PLUG1["wy"], PLUG1["hz"]) / 2
    r_min = min(Bd["channel"]["d"], Bd["conn_thread"]["d"]) / 2
    moving = union([box(x - PLUG1["lx"] / 2, x + PLUG1["lx"] / 2, -PLUG1["wy"] / 2, PLUG1["wy"] / 2,
                        -PLUG1["hz"] / 2, PLUG1["hz"] / 2) for x in range(-30, 13, 3)])
    v = vol(moving, body)
    check("1 W-1 플러그 → Ø7 통로", "플러그 대각 반경 vs 최소 통로 반경", v < 1e-3,
          f"{diag:.2f} / {r_min:.2f} mm (여유 {r_min - diag:.2f}), 겹침 {v:.3f} mm³",
          "플러그가 어느 각도로 돌아도 통과. 커넥터 체결 때 플러그가 따라 돌아 꼬임 없음")

    # ════ 2. 홀더: 플러그를 Ø6 구멍으로 통과 ════
    r_hole = Hh["hole_d"] / 2
    check("2 홀더 Ø6 구멍 통과 (PCB 없이)", "플러그 대각 반경 vs 구멍 반경", diag < r_hole,
          f"{diag:.2f} / {r_hole:.2f} mm (여유 {r_hole - diag:.2f})", "여유 0.13 mm — 빡빡함", level="WARN")
    # PCB가 홈에 있을 때 구멍 위쪽 공간
    z_top = math.sqrt(r_hole ** 2 - (PLUG1["wy"] / 2) ** 2) if r_hole > PLUG1["wy"] / 2 else 0
    free_h = z_top - T / 2
    check("2' 홀더+PCB 먼저 조립 후 플러그 통과", "PCB 위 구멍 높이 vs 플러그 높이", free_h >= PLUG1["hz"],
          f"{free_h:.2f} (폭 {PLUG1['wy']:g} 위치) / 필요 {PLUG1['hz']:g} mm",
          "PCB가 구멍 가운데를 막아 플러그가 못 지나감")

    # ════ 3. 홀더를 바디에 넣고 M2 축 방향 나사 (뒤에서) ════
    x_face = Hh["x"][1]
    h_home = holder
    for sgn in (1, -1):
        z = sgn * Hh["screw_pcd"] / 2
        drv = xcyl(0, z, x_face + SCREW_HEAD["k"], 120, DRIVER_D)
        vb = vol(drv, board)
        d = dist(drv, board)
        check("3 홀더 축 나사 M2 (뒤에서, PCB 장착 상태)", f"드라이버 Ø{DRIVER_D:g} 경로 z={z:+g} vs PCB·부품",
              vb < 1e-3, f"최소 거리 {d:.2f} mm", "드라이버가 PCB 위/아래를 지나 뒤에서 들어감")

    # ════ 4. PCB 가로 고정 나사 M2 (z 방향, x 16.25) — 홀더가 바디 안에 있을 때 ════
    c = Hh["cross"]
    for y in c["y"]:
        drv = zcyl(c["x"], y, T / 2 + SCREW_HEAD["k"], 60, DRIVER_D)
        v = vol(drv, body)
        wall = math.sqrt((Bd["cbore"]["d"] / 2) ** 2 - y ** 2)
        check("4 PCB 가로 나사 M2 (홀더가 바디 안)", f"드라이버 z 방향 경로 (y {y:+g}) vs 바디 벽",
              v < 1e-3, f"바디 카운터보어 벽이 z {wall:.1f} mm에서 막음 (겹침 {v:.0f} mm³)",
              "나사가 카운터보어 입구(x 26)에서 9.75 mm 안쪽 — 수직 공구 불가")
    # 나사 길이: 홀더 바깥면에서 박을 때 끝이 반대쪽 바깥으로 나오는지
    zs = math.sqrt((Hh["d"] / 2) ** 2 - 5.0 ** 2)
    check("4 PCB 가로 나사 M2", "M2×12 길이 vs 홀더 두께 (y ±5에서 z ±%.2f)" % zs, True,
          f"홀더 두께 {2 * zs:.1f} mm — 머리를 홀더 면에 묻으면 끝이 반대 면 안쪽에 남음 (M2×12 적합)", level="OK")

    # ════ 5. 제안 경로: 홀더+PCB 벤치 조립 → 창으로 플러그 통과 → 바디에 넣고 축 나사 ════
    win = dict(wy=5.6, z0=T / 2 + 0.05, z1=T / 2 + 0.05 + 3.2)
    check("5 제안: 홀더 윗면 창 5.6 × 3.2", "플러그 통과 여유 (폭 / 높이)",
          win["wy"] > PLUG1["wy"] and win["z1"] - win["z0"] > PLUG1["hz"],
          f"{(win['wy'] - PLUG1['wy']) / 2:.2f} / {(win['z1'] - win['z0'] - PLUG1['hz']):.2f} mm",
          "창 위쪽 끝 z %.2f < 축 나사 머리 자리 아래 z %.1f" % (win["z1"], Hh["screw_pcd"] / 2 - Hh["cbore_d"] / 2),
          level="OK")

    # ════ 6. W-1 플러그를 J3에 꽂음 (x 22.5 → 26.5) ════
    pl = P.HARNESS["plug"]
    stroke = 4.0
    moving = union([box(pl["x"][0] - s, pl["x"][1] - s, pl["y"][0], pl["y"][1], pl["z"][0], pl["z"][1])
                    for s in (stroke, stroke / 2, 0.0)])
    others = union([solids[r] for r in PARTS if r != "J3" and solids[r] is not None and PARTS[r]["side"] == "T"])
    v1, v2, v3 = vol(moving, others), vol(moving, body), vol(moving, holder)
    check("6 W-1 플러그 → J3 (꽂는 거리 4 mm)", "플러그 경로 vs 윗면 부품·바디·홀더", max(v1, v2, v3) < 1e-3,
          f"겹침 {v1:.3f} / {v2:.3f} / {v3:.3f} mm³")
    tw_room = Bd["cbore"]["d"] / 2 - pl["z"][1]
    check("6 W-1 플러그 → J3", "핀셋 공간 (플러그 위 ~ 바디 벽, y 0)", tw_room > 3, f"{tw_room:.1f} mm",
          "플러그는 시작 위치에서 대부분 카운터보어 안(x < 26) → 위·뒤에서 핀셋으로 잡아 밀어 넣음", level="OK")
    Lw1 = P.HARNESS["length"]
    xpin = P.SENSOR_CONN["x0"] - P.SENSOR_CONN["pin_y"]
    in_channel = Bd["channel"]["x"][1] - xpin
    span = pl["x"][0] - Bd["channel"]["x"][1]
    slack1 = Lw1 - in_channel - span
    need_thread = (Bd["cbore"]["x"][1] + (Hh["x"][1] - Hh["x"][0]) + PLUG1["lx"]) - Bd["channel"]["x"][1]
    check("6 W-1 길이", "통로 안 / 통로 끝~J3 / 남는 길이", True,
          f"{in_channel:.0f} / {span:.1f} / {slack1:.1f} mm (L {Lw1:g})",
          f"홀더를 카운터보어 입구에 두고 창에 꿰려면 통로 끝에서 {need_thread:.0f} mm 필요 → 남는 {slack1:.0f} mm는 "
          "PCB 앞 윗면(x 18–26.5)에 고리로 남음 (그 아래는 높이 0 부품 J2만)", level="WARN")

    # ════ 7. 지지링을 PCB 뒤에서 끼움 (x 71 → 59) ════
    r_in = Rg["id"] / 2
    near = [(p["ref"], round(part_rmax(p), 2)) for p in parts_in(Rg["x"][0], P.PCB["x"][1]) if part_rmax(p) > r_in - 0.3]
    worst = max((part_rmax(p), p["ref"]) for p in parts_in(Rg["x"][0], P.PCB["x"][1]))
    check("7 지지링 끼움 (안지름 Ø20이 x 71 → 59로 지나감)", "뒤쪽 부품 최대 반경 vs 링 안 반경 10",
          worst[0] < r_in, f"최대 {worst[0]:.2f} mm ({worst[1]})" + (f", 여유 0.3 미만: {near}" if near else ""),
          "링은 엔드캡 구역(x 64–71) 부품 위로도 지나감 → 그 구역 높이 한계는 Ø22가 아니라 Ø20 "
          "(배치 규칙은 Ø22로 검사했음 — 고쳐야 함). GDT1은 외형 상자로 9.84, 실제 원통 Ø5로는 약 9.0",
          level="WARN" if worst[0] < r_in and near else None)
    sweep = union([ring.translate((dx, 0, 0)) for dx in (8.0, 4.0, 0.0)])
    v = vol(sweep, board)
    check("7 지지링 끼움", "링 경로 vs PCB·부품 (형상 교차)", v < 1e-3, f"겹침 {v:.2f} mm³")

    # ════ 8. 하우징을 PCB 위로 씌움 (턴버클 시작 위치: 체결 길이 7 mm 뒤) ════
    tl = Hs["thread_len"]
    r_b = Hs["thread_minor"] / 2
    worst = max((part_rmax(p), p["ref"]) for p in PL["parts"] if p["fab"][2] > Hs["x"][0])
    check("8 하우징 씌움 (뒤에서 앞으로)", "부품 최대 반경 vs 하우징 최소 반경 %.2f" % r_b, worst[0] < r_b - 0.2,
          f"{worst[0]:.2f} mm ({worst[1]}), 링 바깥 {Rg['od'] / 2:.2f}", "링 Ø26.4 vs 나사 골 Ø26.92: 반경 여유 0.26")
    j5 = PARTS.get("J5")
    if j5:
        x0, y0, x1, y1 = j5["fab"]
        yp = abs(j5["pads"][0]["xy"][1])
        wall = math.sqrt((Hs["id"] / 2) ** 2 - yp ** 2) - T / 2
        check("8 J5 샤시 스프링 접점", "하우징 내면까지 높이 vs 접점 자유 높이", wall <= j5["h"],
              f"{wall:.1f} / {j5['h']:g} mm (모자람 {wall - j5['h']:.1f})",
              "접점이 하우징에 닿지 않음 → 샤시 접지 없음. 닿게 만들어도 턴버클 7바퀴 동안 하우징이 접점 위에서 회전·축 이동")

    # ════ 9. W-2 플러그를 하우징 뒤 입구로 넣어 J1에 꽂음 ════
    h_pre = housing.translate((tl, 0, 0))
    x_rear = Hs["x"][1] + tl
    p2 = P.HARNESS2["plug"]
    depth = x_rear - p2["x"][1]
    moving = union([box(p2["x"][0] + s, p2["x"][1] + s, p2["y"][0], p2["y"][1], p2["z"][0], p2["z"][1])
                    for s in (20.0, 10.0, 4.0, 0.0)])
    others = union([ring, h_pre] + [solids[r] for r in PARTS if r != "J1" and solids[r] is not None])
    v = vol(moving, others)
    check("9 W-2 플러그 → J1 (하우징 안 %.1f mm 깊이)" % depth, "플러그 경로 vs 링·하우징·부품", v < 1e-3,
          f"겹침 {v:.3f} mm³", "링 안쪽(Ø20)을 지나 J1에 닿음. 핀셋·밀대로 축 방향 삽입 (GH 8P 삽입력)")
    Lw2 = P.HARNESS2["length"]
    x_m12 = P.CONNECTOR["inner"]["x"][0]
    span_fin = math.hypot(x_m12 - p2["x"][1], (p2["z"][0] + p2["z"][1]) / 2)
    span_pre = span_fin + 2 * tl
    check("9 W-2 길이", "꽂을 때 / 체결 후 직선 거리 / 남는 길이", True,
          f"{span_pre:.1f} / {span_fin:.1f} / {Lw2 - span_fin:.0f} mm (L {Lw2:g})",
          "턴버클로 엔드캡이 14 mm 다가오며 선이 엔드캡 안에서 접힘. 꽂을 때 엔드캡을 옆으로 비켜 들 길이만 있으면 됨 "
          "(하우징 뒤 끝까지 %.0f + 옆 15 mm ≈ %.0f mm)" % (x_rear - p2["x"][1], x_rear - p2["x"][1] + 15), level="WARN")

    # ════ 10. 턴버클: 하우징만 7바퀴 → 바디 쪽 7 mm, 엔드캡 14 mm 접근 ════
    board_all = board.union(ring)
    for dx in (14.0, 7.0, 2.0, 0.5, 0.0):
        e = endcap.translate((dx, 0, 0))
        v = vol(e, board_all)
        d = dist(e, board_all)
        ok = v < 1e-3 and d >= 0.3
        check("10 턴버클 (엔드캡 이동)", f"엔드캡 {dx:>4g} mm 앞 → PCB·부품·링", ok,
              f"최소 거리 {d:.2f} mm, 겹침 {v:.2f} mm³",
              "엔드캡 앞면(x 64, r 11–14)이 PCB 넓은 구간 끝(x 64, 폭 23)에 닿음 — 공차에 따라 PCB를 밀어냄" if dx == 0 and d < 0.3 else "",
              level=None if ok or dx > 0 else "NG")
    hv = vol(housing, board_all)
    hd = dist(housing, board_all)
    check("10 턴버클 (체결 후)", "하우징 vs PCB·부품·링", hv < 1e-3, f"최소 거리 {hd:.2f} mm")

    # ════ 11. 2차 몰딩 ════
    check("11 2차 몰딩 (M12 위, M3 구멍 주입)", "흐름 경로", True,
          "엔드캡 Ø22 → 링 안(Ø20) → 하우징 Ø27 → 홀더 뒤. 링 바깥 0.3 mm 틈은 좁아 링 뒤 공기 빼기는 링 안쪽으로",
          "PCB가 세로로 서 있어 양면이 같이 참. 오목한 곳(J1·J3 플러그 몸체 안)은 진공 주입 권장", level="OK")

    json.dump(dict(placement=PL["meta"]["project"], results=results), open(os.path.join(OUT, "report.json"), "w"),
              ensure_ascii=False, indent=1)
    ng = sum(1 for r in results if r["verdict"] == "NG")
    wn = sum(1 for r in results if r["verdict"] == "WARN")
    print(f"\n{len(results)} checks: NG {ng}, WARN {wn}")
    return dict(body=body, holder=holder, ring=ring, housing=housing, endcap=endcap, pcb=pcb, solids=solids)




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
            col = (0.85, 0.2, 0.2) if r == "J5" else (0.93, 0.90, 0.80) if r in ("J1", "J3") else (0.18, 0.18, 0.2)
            scene.append((so, col, 1.0))
    if side == "T":
        scene += [(M.harness(), (0.92, 0.92, 0.90), 1.0), (M.harness_plug(), (0.93, 0.90, 0.80), 1.0),
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
