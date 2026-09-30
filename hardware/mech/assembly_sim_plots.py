"""조립 시뮬레이션 그림: 개선안 A–F 장면 6개 (단면·평면, 치수 = hmt500_params + PCB 배치).

  python hardware/mech/assembly_sim_plots.py  →  out/assembly_sim/assembly_fixes.png
  (개선 전 문제 장면은 out/assembly_sim/assembly_issues.png — 1차 시뮬레이션 기록)
"""

import json
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle, FancyArrowPatch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hmt500_params as P  # noqa: E402

OUT = os.path.join(HERE, "out", "assembly_sim")
PL = json.load(open(os.path.join(HERE, "..", "kicad", "HMT500(260313A)", "placement.json"), encoding="utf-8"))
T = P.PCB["t"]
STEEL, PEEK, PCBC, BAD, GOOD, PART = "#9aa3ad", "#d9b36c", "#2e7d32", "#d62728", "#1f77b4", "#555555"
plt.rcParams["font.family"] = ["NanumGothic", "DejaVu Sans"]


def arrow(ax, a, b, c=BAD, lw=1.5):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=10, color=c, lw=lw))


def parts_z(side_filter=None, xa=-99, xb=999, ya=-99, yb=99):
    out = []
    for p in PL["parts"]:
        x0, y0, x1, y1 = p["fab"]
        if x1 < xa or x0 > xb or y1 < ya or y0 > yb or p["h"] <= 0:
            continue
        s = 1 if p["side"] == "T" else -1
        out.append((p, x0, x1, y0, y1, s * T / 2, s * (T / 2 + p["h"])))
    return out


def panel_a(ax):
    """① 홀더 뒷면 (x = 18): PCB를 먼저 끼운 상태에서 W-1 플러그가 창을 지나감."""
    H = P.PCB_HOLDER
    w = H["window"]
    ax.add_patch(Circle((0, 0), H["d"] / 2, color=PEEK))
    ax.add_patch(Circle((0, 0), H["hole_d"] / 2, color="white"))
    ax.add_patch(Rectangle((-w["wy"] / 2, w["z"][0]), w["wy"], w["z"][1] - w["z"][0], color="white"))
    ax.add_patch(Rectangle((-P.PCB["sections"][0][2] / 2, -T / 2), P.PCB["sections"][0][2], T, color=PCBC))
    pw, ph = 5.0, 2.8
    zc = (w["z"][0] + w["z"][1]) / 2
    ax.add_patch(Rectangle((-pw / 2, zc - ph / 2), pw, ph, fill=False, ec=GOOD, lw=2))
    ax.text(0, w["z"][1] + 0.5, "창 %g × %g — 플러그 5.0 × 2.8 통과 (여유 0.3 / 0.2)" % (w["wy"], w["z"][1] - w["z"][0]),
            ha="center", fontsize=7.5, color=GOOD)
    for sgn in (1, -1):
        ax.add_patch(Circle((0, sgn * H["screw_pcd"] / 2), H["cbore_d"] / 2, fill=False, ec="k", lw=0.8))
    ax.text(0, 10.8, "축 나사 M2×8 + 링 단자 (Ø%g 자리)" % H["cbore_d"], ha="center", fontsize=7)
    ax.text(0, -10.9, "축 나사 M2×6", ha="center", fontsize=7)
    for y in H["cross"]["y"]:
        ax.plot([y, y], [-9.5, 9.5], color="k", ls="--", lw=0.6)
    ax.text(5.3, -7.5, "가로 나사 M2×12\n(벤치에서)", fontsize=6.5)
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12.5, 12.5)
    ax.set_aspect("equal")
    ax.set_title("① A: 홀더 창 — PCB를 먼저 끼워도 W-1 플러그 통과 (x = 18 단면)", fontsize=9)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")


def panel_b(ax):
    """② 앞쪽 옆 단면 (y = 0): 샤시 선 J5 → 링 단자 → 위 축 나사, 드라이버는 뒤에서 x 방향."""
    B, H, C = P.BODY, P.PCB_HOLDER, P.CHASSIS_WIRE
    zw = B["cbore"]["d"] / 2
    for s in (1, -1):
        ax.add_patch(Rectangle((B["cbore"]["x"][0] - 6, s * zw), B["cbore"]["x"][1] - B["cbore"]["x"][0] + 6, s * 4, color=STEEL))
    ax.add_patch(Rectangle((B["cbore"]["x"][0] - 6, -zw), 6, 2 * zw, color=STEEL))
    ax.add_patch(Rectangle((H["x"][0], -H["d"] / 2), H["x"][1] - H["x"][0], H["d"], color=PEEK, alpha=0.9))
    w = H["window"]
    ax.add_patch(Rectangle((H["x"][0], w["z"][0]), H["x"][1] - H["x"][0], w["z"][1] - w["z"][0], color="white"))
    ax.add_patch(Rectangle((P.PCB["x"][0], -T / 2), 30, T, color=PCBC))
    j5 = next(p for p in PL["parts"] if p["ref"] == "J5")
    xp = j5["pads"][0]["xy"][0]
    xf, zs = H["x"][1], C["screw_z"]
    ax.plot([xp, xp, xf + 2.5, xf + 0.9], [T / 2, 3.0, zs - 1.5, zs - 2.2], color="#2e7d32", lw=2.5)
    ax.add_patch(Rectangle((xf, zs - 2.25), 0.8, 4.5, color="#b08d57"))
    ax.add_patch(Rectangle((xf + 0.8, zs - 1.9), 1.3, 3.8, color="#666666"))
    ax.add_patch(Rectangle((xf + 2.1, zs - 1.5), 26, 3.0, color=GOOD, alpha=0.25))
    ax.text(xf + 5, zs + 2.2, "드라이버 Ø3 (뒤에서 x 방향) — 부품·선과 0.38 mm 이상", fontsize=7.5, color=GOOD)
    ax.text(xp + 0.6, 1.2, "J5", fontsize=7, color="#2e7d32")
    ax.text(xf - 0.2, zs + 3.1, "링 단자", fontsize=7, ha="right")
    ax.axvline(B["cbore"]["x"][1], color="k", ls=":", lw=0.8)
    ax.set_xlim(4, 44)
    ax.set_ylim(-14, 16)
    ax.set_aspect("equal")
    ax.set_title("② D: 샤시 선 J5 -> M2 링 단자 -> 금속 바디 (y = 0 단면)", fontsize=9)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("z (mm)")


def panel_c(ax):
    """③ 뒤쪽 평면 (z = 0): 턴버클 끝 엔드캡 앞면 x 64 와 PCB 계단 x 63.4 → 틈 0.6."""
    secs = P.PCB["sections"]
    up = []
    for x0, x1, w in secs:
        up += [(x0, w / 2), (x1, w / 2)]
    pts = up + [(x, -y) for x, y in reversed(up)]
    ax.add_patch(Polygon(pts, closed=True, fc=PCBC, alpha=0.25, ec=PCBC))
    E = P.ENDCAP
    for s in (1, -1):
        ax.add_patch(Rectangle((E["mthread"]["x"][0], s * E["cbore"]["d"] / 2), E["flange"]["x"][1] - E["mthread"]["x"][0],
                               s * (E["seal"]["d"] - E["cbore"]["d"]) / 2, color=STEEL))
    R = P.PCB_RING
    for s in (1, -1):
        ax.add_patch(Rectangle((R["x"][0], s * R["id"] / 2), R["x"][1] - R["x"][0], s * (R["od"] - R["id"]) / 2, color=PEEK))
    x_step = secs[1][1]
    xe = E["mthread"]["x"][0]
    arrow(ax, (x_step, 12.3), (xe, 12.3), GOOD, 1.2)
    arrow(ax, (xe, 12.3), (x_step, 12.3), GOOD, 1.2)
    ax.text(xe - 0.3, 13.0, "틈 %.1f" % (xe - x_step), color=GOOD, ha="center", fontsize=8)
    ax.text(xe - 11.5, -14.2, "B: PCB 폭 23 구간 끝 x %g (엔드캡 앞면 x %g)" % (x_step, xe), fontsize=8, color=GOOD)
    ax.set_xlim(xe - 12, xe + 12)
    ax.set_ylim(-15, 15)
    ax.set_aspect("equal")
    ax.set_title("③ B: 턴버클 끝 — 엔드캡과 PCB 틈 0.6 (z = 0 평면)", fontsize=9)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")


def panel_d(ax):
    """④ 지지링이 지나가는 단면 (x 59–71 부품을 y–z로 투영) vs 링 안지름 Ø20."""
    ax.add_patch(Circle((0, 0), P.PCB_RING["id"] / 2, fill=False, ec=PEEK, lw=2))
    ax.add_patch(Rectangle((-9, -T / 2), 18, T, color=PCBC))
    for p, x0, x1, y0, y1, z0, z1 in parts_z(xa=P.PCB_RING["x"][0], xb=P.PCB["x"][1]):
        ax.add_patch(Rectangle((y0, min(z0, z1)), y1 - y0, abs(z1 - z0), fill=False, ec=PART, lw=1.2))
        ax.text((y0 + y1) / 2, (z0 + z1) / 2, p["ref"], ha="center", va="center", fontsize=6.5)
    ax.text(0, 10.4, "링 안지름 Ø20 (x 71 -> 59로 지나감)", ha="center", fontsize=7, color="#8a6d1f")
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_aspect("equal")
    ax.set_title("④ C: 링 뒤 부품 높이 한계 Ø20 — 최대 반경 8.4 (R1)", fontsize=9)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")


def panel_e(ax):
    """⑤ 밀대 T-001로 W-2 플러그를 J1에 밀어 넣음 (평면, 하우징 턴버클 시작 위치)."""
    Hs, T_ = P.HOUSING, P.PUSH_TOOL
    tl = Hs["thread_len"]
    for s in (1, -1):
        ax.add_patch(Rectangle((Hs["x"][0] + tl, s * Hs["id"] / 2), Hs["x"][1] - Hs["x"][0], s * 2.5, color=STEEL))
    R = P.PCB_RING
    for s in (1, -1):
        ax.add_patch(Rectangle((R["x"][0], s * R["id"] / 2), R["x"][1] - R["x"][0], s * (R["od"] - R["id"]) / 2, color=PEEK))
    secs = P.PCB["sections"]
    up = []
    for x0, x1, w in secs:
        up += [(x0, w / 2), (x1, w / 2)]
    ax.add_patch(Polygon(up + [(x, -y) for x, y in reversed(up)], closed=True, fc=PCBC, alpha=0.2, ec=PCBC))
    j1 = next(p for p in PL["parts"] if p["ref"] == "J1")
    x0, y0, x1, y1 = j1["fab"]
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="k"))
    ax.text((x0 + x1) / 2, 0, "J1", ha="center", fontsize=8)
    p2 = P.HARNESS2["plug"]
    ax.add_patch(Rectangle((p2["x"][0], p2["y"][0]), p2["x"][1] - p2["x"][0], p2["y"][1] - p2["y"][0], color="#e8dcc0", ec="k"))
    xt = p2["x"][1]
    tool = [(xt, -T_["tip_w"] / 2), (xt + T_["tip_len"], -T_["tip_w"] / 2), (xt + T_["tip_len"], -T_["width"] / 2),
            (xt + T_["tip_len"] + T_["length"], -T_["width"] / 2), (xt + T_["tip_len"] + T_["length"], T_["width"] / 2),
            (xt + T_["tip_len"], T_["width"] / 2), (xt + T_["tip_len"], T_["tip_w"] / 2), (xt, T_["tip_w"] / 2)]
    ax.add_patch(Polygon(tool, closed=True, fc=GOOD, alpha=0.25, ec=GOOD))
    ax.add_patch(Rectangle((xt, -T_["slot_w"] / 2), T_["slot_len"] + T_["tip_len"], T_["slot_w"], fc="white", ec=GOOD, ls="--"))
    for k in range(8):
        yk = (k - 3.5) * 1.25
        ax.plot([xt, xt + 60], [yk, yk * 0.3], color="#999999", lw=0.8)
    ax.text(xt + 35, 9.5, "T-001 밀대 (3D 프린트): 끝이 플러그 양쪽 턱을 밂, 홈 %.1f로 선 8가닥 통과" % T_["slot_w"],
            fontsize=7, color=GOOD, ha="center")
    ax.text(Hs["x"][1] + tl + 1, -15.5, "하우징 뒤 끝 (턴버클 시작 위치)", fontsize=7)
    ax.axvline(Hs["x"][1] + tl, color="k", ls=":", lw=0.8)
    ax.set_xlim(48, 110)
    ax.set_ylim(-17, 17)
    ax.set_aspect("equal")
    ax.set_title("⑤ F: 밀대로 W-2 플러그를 하우징 안 19.5 mm 깊이의 J1에 꽂음 (평면)", fontsize=9)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")


def panel_f(ax):
    """⑥ 하네스 길이: 꽂을 때와 체결 후."""
    rows = [("W-1 (센서) 60 mm", 60, 31, P.BODY["channel"]["x"][1] - P.BODY["channel"]["x"][0], "통로 끝에서 창 꿰기에 24 mm 필요 -> 유지"),
            ("W-2 (M12) 40 mm", P.HARNESS2["length"], 0, 10.8, "꽂을 때 약 34 mm 필요 (하우징 안 20 + 옆 15)")]
    y = 0
    for name, L, fixed, span, note in rows:
        ax.barh(y, fixed, color="#999999")
        ax.barh(y, span, left=fixed, color=GOOD)
        ax.barh(y, L - fixed - span, left=fixed + span, color="#f0b27a")
        ax.text(L + 1, y, f"남음 {L - fixed - span:.0f} mm", va="center", fontsize=8)
        ax.text(0, y + 0.42, f"{name}: {note}", fontsize=7.5)
        y += 1.3
    ax.set_yticks([])
    ax.set_xlim(0, 80)
    ax.set_ylim(-0.6, 2.4)
    ax.set_xlabel("mm (회색 = 통로 안 고정, 파랑 = 체결 후 직선 거리, 주황 = 남는 길이)")
    ax.set_title("⑥ E: W-2 60 -> 40 mm (남는 선 49 -> 29 mm)", fontsize=9)


def main():
    os.makedirs(OUT, exist_ok=True)
    fig, axs = plt.subplots(3, 2, figsize=(14, 17))
    for fn, ax in zip((panel_a, panel_b, panel_c, panel_d, panel_e, panel_f), axs.flat):
        fn(ax)
        ax.grid(ls=":", lw=0.4)
    fig.suptitle("HMT500(260313) 조립 시뮬레이션 — 개선안 A–F 반영 후 (NG 0)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    out = os.path.join(OUT, "assembly_fixes.png")
    fig.savefig(out, dpi=110)
    print(out)


if __name__ == "__main__":
    main()
