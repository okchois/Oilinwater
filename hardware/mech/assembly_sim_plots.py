"""조립 시뮬레이션 그림: 문제 장면 6개 (단면·평면, 치수 = hmt500_params + PCB 배치).

  python hardware/mech/assembly_sim_plots.py  →  out/assembly_sim/assembly_issues.png
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
    """앞쪽 옆 단면 (y = +5 평면): PCB 가로 나사 드라이버가 바디 벽에 막힘."""
    B, H = P.BODY, P.PCB_HOLDER
    y = 5.0
    zw = math.sqrt((B["cbore"]["d"] / 2) ** 2 - y ** 2)
    zh = math.sqrt((H["d"] / 2) ** 2 - y ** 2)
    for s in (1, -1):
        ax.add_patch(Rectangle((B["cbore"]["x"][0] - 6, s * zw), B["cbore"]["x"][1] - B["cbore"]["x"][0] + 6, s * 4,
                               color=STEEL))
    ax.add_patch(Rectangle((B["cbore"]["x"][0] - 6, -zw), 6, 2 * zw, color=STEEL))
    ax.add_patch(Rectangle((H["x"][0], -zh), H["x"][1] - H["x"][0], 2 * zh, color=PEEK, alpha=0.9))
    ax.add_patch(Rectangle((P.PCB["x"][0], -T / 2), 30, T, color=PCBC))
    c = H["cross"]
    ax.add_patch(Rectangle((c["x"] - 1.5, T / 2 + 1.3), 3.0, 22, color=BAD, alpha=0.35))
    ax.plot([c["x"] - 1.5, c["x"] + 1.5], [zw, zw], color=BAD, lw=3)
    ax.text(c["x"] + 2, 12.5, "드라이버(z 방향)\n-> 바디 벽 z %.1f에서 막힘" % zw, color=BAD, fontsize=8)
    ax.axvline(B["cbore"]["x"][1], color="k", ls=":", lw=0.8)
    ax.text(B["cbore"]["x"][1] + 0.3, -13.5, "카운터보어 입구 x 26", fontsize=7)
    ax.plot(c["x"], 0, "kx")
    ax.text(c["x"] - 1, -3.5, "M2 가로 나사\nx 16.25", fontsize=7, ha="center")
    ax.set_xlim(4, 44)
    ax.set_ylim(-15, 25)
    ax.set_aspect("equal")
    ax.set_title("① PCB 가로 나사: 홀더가 바디 안이면 공구가 못 들어감 (y = +5 단면)", fontsize=9)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("z (mm)")


def panel_b(ax):
    """홀더 뒷면 (x = 18) 단면: PCB가 구멍을 가로막아 W-1 플러그가 못 지나감 + 제안 창."""
    H = P.PCB_HOLDER
    ax.add_patch(Circle((0, 0), H["d"] / 2, color=PEEK))
    ax.add_patch(Circle((0, 0), H["hole_d"] / 2, color="white"))
    ax.add_patch(Rectangle((-P.PCB["sections"][0][2] / 2, -T / 2), P.PCB["sections"][0][2], T, color=PCBC))
    pw, ph = 5.0, 2.8
    ax.add_patch(Rectangle((-pw / 2, T / 2), pw, ph, fill=False, ec=BAD, lw=2))
    ax.text(0, T / 2 + ph + 0.6, "W-1 플러그 5.0 × 2.8", color=BAD, ha="center", fontsize=8)
    ax.add_patch(Rectangle((-2.8, T / 2 + 0.05), 5.6, 3.2, fill=False, ec=GOOD, lw=1.5, ls="--"))
    ax.text(3.2, 3.2, "제안 창\n5.6 × 3.2", color=GOOD, fontsize=8)
    for s in (1, -1):
        ax.add_patch(Circle((0, s * H["screw_pcd"] / 2), H["cbore_d"] / 2, fill=False, ec="k", lw=0.8))
    ax.text(0, 9.2, "축 나사 M2 (z ±8)", ha="center", fontsize=7)
    ax.text(0, -1.9, "PCB (홈 1.7)", ha="center", fontsize=7, color="white")
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_aspect("equal")
    ax.set_title("② 홀더+PCB를 먼저 조립하면 Ø6 구멍 위 높이 0.9 mm < 플러그 2.8", fontsize=9)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")


def panel_c(ax):
    """뒤쪽 평면 (z = 0): 턴버클 끝에서 엔드캡 앞면이 PCB 넓은 구간 끝에 닿음."""
    secs = P.PCB["sections"]
    up = []
    for x0, x1, w in secs:
        up += [(x0, w / 2), (x1, w / 2)]
    pts = up + [(x, -y) for x, y in reversed(up)]
    ax.add_patch(Polygon(pts, closed=True, fc=PCBC, alpha=0.25, ec=PCBC))
    E = P.ENDCAP
    for s in (1, -1):
        ax.add_patch(Rectangle((E["mthread"]["x"][0], s * E["cbore"]["d"] / 2), 17, s * 3, color=STEEL))
        ax.plot(64, s * 11.5, "o", color=BAD, ms=8)
    R = P.PCB_RING
    for s in (1, -1):
        ax.add_patch(Rectangle((R["x"][0], s * R["id"] / 2), R["x"][1] - R["x"][0], s * (R["od"] - R["id"]) / 2,
                               color=PEEK))
    ax.plot([63.4, 63.4], [-11.5, 11.5], color=GOOD, ls="--")
    ax.text(63.3, 0.5, "제안: 폭 23 구간을\nx 63.4에서 끝냄 (틈 0.6)", color=GOOD, ha="right", fontsize=8)
    ax.text(66, 12.8, "엔드캡 앞면 x 64 = PCB 폭 23 끝 x 64: 틈 0", color=BAD, fontsize=8)
    ax.set_xlim(52, 76)
    ax.set_ylim(-15, 15)
    ax.set_aspect("equal")
    ax.set_title("③ 턴버클 끝: 엔드캡이 PCB 모서리에 닿음 (z = 0 평면)", fontsize=9)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")


def panel_d(ax):
    """지지링이 지나가는 단면 (x 59–71 부품을 y–z로 투영) vs 링 안지름 Ø20."""
    ax.add_patch(Circle((0, 0), P.PCB_RING["id"] / 2, fill=False, ec=PEEK, lw=2))
    ax.add_patch(Circle((0, 0), P.ENDCAP["cbore"]["d"] / 2, fill=False, ec=STEEL, lw=1, ls="--"))
    ax.add_patch(Rectangle((-9, -T / 2), 18, T, color=PCBC))
    for p, x0, x1, y0, y1, z0, z1 in parts_z(xa=P.PCB_RING["x"][0], xb=71):
        r = max(math.hypot(max(abs(y0), abs(y1)), max(abs(z0), abs(z1))), 0)
        c = BAD if r > 9.7 else PART
        ax.add_patch(Rectangle((y0, min(z0, z1)), y1 - y0, abs(z1 - z0), fill=False, ec=c, lw=1.2))
        ax.text((y0 + y1) / 2, (z0 + z1) / 2, p["ref"], ha="center", va="center", fontsize=6, color=c)
    ax.text(0, 10.4, "링 안지름 Ø20 (x 71 -> 59로 지나감)", ha="center", fontsize=7, color="#8a6d1f")
    ax.text(0, -12.6, "엔드캡 Ø22 (점선): 배치 규칙은 이것으로 검사했음", ha="center", fontsize=7)
    ax.set_xlim(-13, 13)
    ax.set_ylim(-13.5, 12)
    ax.set_aspect("equal")
    ax.set_title("④ 링을 끼울 때 뒤쪽 부품이 Ø20 안에 들어야 함 (GDT1 여유 0.16, 상자 기준)", fontsize=9)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")


def panel_e(ax):
    """J5 위치 단면: 하우징 내면까지 10.8 vs 접점 7.25."""
    j5 = next(p for p in PL["parts"] if p["ref"] == "J5")
    ax.add_patch(Circle((0, 0), P.HOUSING["id"] / 2, fill=False, ec=STEEL, lw=3))
    ax.add_patch(Rectangle((-11.5, -T / 2), 23, T, color=PCBC))
    x0, y0, x1, y1 = j5["fab"]
    ax.add_patch(Rectangle((y0, -T / 2 - j5["h"]), y1 - y0, j5["h"], fill=False, ec=BAD, lw=1.5))
    yp = j5["pads"][0]["xy"][1]
    zw = -math.sqrt((P.HOUSING["id"] / 2) ** 2 - yp ** 2)
    arrow(ax, (yp, -T / 2 - j5["h"]), (yp, zw), BAD)
    ax.text(yp + 0.5, (zw - T / 2 - j5["h"]) / 2, "%.1f mm 모자람" % (-zw - T / 2 - j5["h"]), color=BAD, fontsize=8)
    ax.text(yp, -T / 2 - j5["h"] / 2, "J5\n7.25", ha="center", fontsize=7, color=BAD)
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_aspect("equal")
    ax.set_title("⑤ J5 샤시 접점이 하우징 Ø27에 닿지 않음 (x %.1f 단면)" % j5["x"], fontsize=9)
    ax.set_xlabel("y (mm)")
    ax.set_ylabel("z (mm)")


def panel_f(ax):
    """하네스 길이: 꽂을 때와 체결 후."""
    rows = [("W-1 (센서)", 60, 31, 14.5, "통로 끝에서 창 꿰기에 24 mm 필요"),
            ("W-2 (M12)", 60, 0, 10.8, "꽂을 때 약 35 mm 필요 (하우징 안 20 + 옆으로 15)")]
    y = 0
    for name, L, fixed, span, note in rows:
        ax.barh(y, fixed, color="#999999")
        ax.barh(y, span, left=fixed, color=GOOD)
        ax.barh(y, L - fixed - span, left=fixed + span, color=BAD, alpha=0.5)
        ax.text(L + 1, y, f"남음 {L - fixed - span:.0f} mm", va="center", fontsize=8, color=BAD)
        ax.text(0, y + 0.42, f"{name}: {note}", fontsize=7.5)
        y += 1.3
    ax.set_yticks([])
    ax.set_xlim(0, 80)
    ax.set_ylim(-0.6, 2.4)
    ax.set_xlabel("mm (회색 = 통로 안 고정, 파랑 = 체결 후 필요한 직선 거리, 빨강 = 남는 길이)")
    ax.set_title("⑥ 하네스 남는 길이: W-2는 엔드캡 안에서 약 49 mm가 접힘", fontsize=9)


def main():
    os.makedirs(OUT, exist_ok=True)
    fig, axs = plt.subplots(3, 2, figsize=(14, 17))
    for fn, ax in zip((panel_a, panel_b, panel_c, panel_d, panel_e, panel_f), axs.flat):
        fn(ax)
        ax.grid(ls=":", lw=0.4)
    fig.suptitle("HMT500(260313) 조립 시뮬레이션 — 발견된 문제 (PCB 배치 rev 2 기준)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.975))
    out = os.path.join(OUT, "assembly_issues.png")
    fig.savefig(out, dpi=110)
    print(out)


if __name__ == "__main__":
    main()
