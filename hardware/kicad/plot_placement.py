"""배치 그림: placement.json → PNG (윗면 / 아랫면, 기구 좌표).

  python plot_placement.py [out.png]      (matplotlib 필요 — KiCad python 과 별개로 실행 가능)

아랫면은 윗면에서 투시한 방향(좌표 그대로)으로 그린다. 색 = 부품 높이.
"""

import json
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Circle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mech"))
import hmt500_params as P  # noqa: E402

PROJECT = "HMT500(260313A)"
JSON_IN = os.path.join(HERE, PROJECT, "placement.json")

GROUP = [("J3", "U5", "U6", "C22", "C25", "C29", "R17", "R18", "C27", "R19", "R20", "C23", "C28", "C24"),
         ("U4", "C14", "C15", "C20", "C18", "C21", "J2", "U14", "C36", "R33"),
         ("U1", "C5", "C7", "R3", "R4", "R5", "R6", "C4", "U2", "L2", "C8", "C9", "R8", "R9", "C11", "C10", "C6",
          "U3", "C12", "FB1", "C13"),
         ("J1", "L1", "D1", "R1", "D2", "C1", "GDT1", "C3", "R2", "J5"),
         ("U7", "U8", "R32", "C40", "R34", "C42", "C44", "R42", "C50", "R44", "C52", "C54", "U9", "U10", "R30", "R40",
          "D30", "D40", "C41", "C51", "U12", "U13", "R31", "R41", "C43", "C45", "C55"),
         ("U11", "C60")]
GCOL = ["#1f77b4", "#9467bd", "#d62728", "#8c564b", "#2ca02c", "#ff7f0e"]
GNAME = ["measurement", "MCU", "power", "input/chassis", "4-20 mA out", "RS-485"]


def gcol(ref):
    for i, g in enumerate(GROUP):
        if ref in g:
            return GCOL[i]
    return "#777777"


def outline(ax):
    pts = []
    for x0, x1, w in P.PCB["sections"]:
        pts += [(x0, w / 2), (x1, w / 2)]
    pts = pts + [(x, -y) for x, y in reversed(pts)] + [pts[0]]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color="k", lw=1.2)
    for (x, y) in P.PCB["holes"]:
        ax.add_patch(Circle((x, y), P.PCB["hole_d"] / 2, fill=False, color="k", lw=0.8))


def zones(ax, side, bands):
    s0, s1 = P.PCB_HOLDER["slot_x"]
    ax.add_patch(Rectangle((s0, -9), s1 - s0, 18, color="#bbbbbb", alpha=0.5, lw=0))
    ax.text((s0 + s1) / 2, 0, "holder\nslot", ha="center", va="center", fontsize=6)
    r0, r1 = P.PCB_RING["x"]
    for sg in (1, -1):
        ax.add_patch(Rectangle((r0 - 0.3, sg * 9.7), r1 - r0 + 0.6, sg * 1.8, color="#bbbbbb", alpha=0.5, lw=0))
    ax.add_patch(Rectangle((r0, -11.5), r1 - r0, 23, fill=False, ls=":", color="#666666", lw=0.6))
    ax.text((r0 + r1) / 2, 11.9, "ring", ha="center", fontsize=6)
    if side == "T":
        for (xa, xb, w, hmax) in bands:
            ax.add_patch(Rectangle((xa, -w), xb - xa, 2 * w, color="#ffd27f" if hmax is None else "#fff0c8",
                                   alpha=0.45, lw=0, hatch=None if hmax is None else "..."))
            ax.text((xa + xb) / 2, -w + 0.4, "no parts" if hmax is None else f"h<={hmax:g}", ha="center",
                    fontsize=5, color="#a06000")
        ax.text(22.0, 3.9, "W-1 wires z~2.2", fontsize=5.5, color="#a06000", ha="center")
        ax.text(64.5, 6.8, "W-2 plug / wires", fontsize=5.5, color="#a06000", ha="center")


def draw(ax, parts, side, title, bands):
    outline(ax)
    zones(ax, side, bands)
    for r in parts:
        if r["side"] != side:
            continue
        x0, y0, x1, y1 = r["crt"]
        c = gcol(r["ref"])
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=True, fc=c, alpha=0.12, ec=c, lw=0.6))
        fx0, fy0, fx1, fy1 = r["fab"]
        ax.add_patch(Rectangle((fx0, fy0), fx1 - fx0, fy1 - fy0, fill=False, ec=c, lw=1.0))
        for p in r["pads"]:
            ax.plot(*p["xy"], ".", ms=1.5, color=c)
        big = (x1 - x0) * (y1 - y0) > 12
        ax.text(r["x"], r["y"], r["ref"] + (f"\n{r['h']:g}" if big else ""), ha="center", va="center",
                fontsize=6.5 if big else 5, color="k", weight="bold" if big else "normal")
    ax.set_title(title, fontsize=10)
    ax.set_xlim(12, 73)
    ax.set_ylim(-13, 13)
    ax.set_aspect("equal")
    ax.set_xticks(range(15, 75, 5))
    ax.tick_params(labelsize=7)
    ax.grid(ls=":", lw=0.3)


def main():
    d = json.load(open(JSON_IN, encoding="utf-8"))
    parts = d["parts"]
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, PROJECT, "placement.png")
    fig, axs = plt.subplots(2, 1, figsize=(12, 11))
    m = d["meta"]
    draw(axs[0], parts, "T", f"TOP (F, z+) — {m['counts']['T']} parts   front = sensor (x {P.PCB['x'][0]:g}) ... rear = M12 (x {P.PCB['x'][1]:g})",
         m["harness_bands_top"])
    draw(axs[1], parts, "B", f"BOTTOM (B, z-), seen through from top — {m['counts']['B']} parts", [])
    hs = [plt.Line2D([], [], color=c, lw=3) for c in GCOL]
    axs[0].legend(hs, GNAME, fontsize=7, loc="lower left", ncol=6, bbox_to_anchor=(0, 1.06))
    un = m.get("unplaced") or []
    fig.suptitle(f"{PROJECT} placement (mech coords, mm; label = ref / height)"
                 + (f"   UNPLACED: {' '.join(un)}" if un else ""), fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(out)


if __name__ == "__main__":
    main()
