"""외형 비교 도면: HMT500(260313) vs E+E EE364 vs Vaisala MMT162 — 같은 축척(1:1), 설치 기준면(씰면) 정렬.

  python docs/market/make_outline_comparison.py  →  docs/market/outline-comparison.png / .svg

- HMT500: hardware/mech/hmt500_params.py (기구 Rev G) 그대로.
- EE364: 원문 데이터시트 v1.13 치수(전장 140, 노출 34, 나사 14, 씰면~하우징 끝 77, 커넥터 15, Ø30, AF27).
  육각 길이는 도면에 없어 10으로 가정.
- MMT162: 웹 검색으로 본 데이터시트 치수(127.5, 119.5, 76, 43.5, 30.5, Ø33, AF30, M8)를
  "노출 30.5 + 나사 13 = 43.5, 몸통 76, 커넥터 8" 로 배치한 추정. 육각 길이 10 가정.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "hardware", "mech"))
import hmt500_params as P  # noqa: E402

plt.rcParams["font.family"] = ["NanumGothic", "DejaVu Sans"]
G_HALF = 20.955 / 2          # G½ 바깥지름


def hmt500():
    C, B, H, E, Cn = P.CAP, P.BODY, P.HOUSING, P.ENDCAP, P.CONNECTOR
    seg = [(C["x_tip"], B["gthread"]["x"][0], C["od"] / 2, "필터 캡 Ø12 (뿌리 3.5는 G½ 안)"),
           (*B["gthread"]["x"], G_HALF, "G½"),
           (*B["relief"]["x"], B["relief"]["d"] / 2, ""),
           (*B["hexa"]["x"], B["hexa"]["af"] / 2, "AF27"),
           (*B["collar"]["x"], B["collar"]["d"] / 2, ""),
           (B["collar"]["x"][1], H["x"][1], H["od"] / 2, "하우징 Ø32"),
           (*E["flange"]["x"], E["flange"]["flats_af"] / 2, "AF28"),
           (*Cn["body"]["x"], Cn["body"]["d"] / 2, ""),
           (*Cn["thread"]["x"], Cn["thread"]["d"] / 2, "M12")]
    return dict(name="HMT500(260313)  — 기구 Rev G", seg=seg, tip=C["x_tip"], end=Cn["thread"]["x"][1],
                thread=B["gthread"]["x"], od=H["od"], note="G½ ISO 228 + 본디드 씰, M12 8핀 (전면 장착, 품번 미정)",
                color="#1f77b4", conf="설계값")


def ee364():
    seg = [(-48, -14, 6, "Ø12"), (-14, 0, G_HALF, "G½"), (0, 10, 13.5, "AF27"), (10, 77, 15, "Ø30"),
           (77, 92, 6, "M12")]
    return dict(name="E+E EE364", seg=seg, tip=-48, end=92, thread=(-14, 0), od=30,
                note="G½ ISO / ½\" NPT, M12 8핀 — 원문 데이터시트 v1.13 (육각 길이 10은 가정)", color="#2ca02c",
                conf="원문")


def mmt162():
    seg = [(-43.5, -13, 6, "Ø12"), (-13, 0, G_HALF, "G½"), (0, 10, 15, "AF30"), (10, 76, 16.5, "Ø33"),
           (76, 84, 5, "M8")]
    return dict(name="Vaisala MMT162 (단종 공지)", seg=seg, tip=-43.5, end=84, thread=(-13, 0), od=33,
                note="G½ ISO / ½\" NPT, M8 4핀 — 검색 치수로 배치한 추정 (원문 도면 확인 필요)", color="#d62728",
                conf="추정")


def outline(seg):
    top = []
    for x0, x1, r, _ in seg:
        top += [(x0, r), (x1, r)]
    return [(seg[0][0], 0)] + top + [(seg[-1][1], 0)]


def dim(ax, x0, x1, y, txt, col="k"):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=0.8, color=col))
    ax.text((x0 + x1) / 2, y + 0.8, txt, ha="center", va="bottom", fontsize=8, color=col)


def main():
    prods = [hmt500(), ee364(), mmt162()]
    gap = 56
    fig, ax = plt.subplots(figsize=(15, 12.5))
    for i, p in enumerate(prods):
        yc = -i * gap
        top = outline(p["seg"])
        pts = [(x, yc + y) for x, y in top] + [(x, yc - y) for x, y in reversed(top)]
        ls = "--" if p["conf"] == "추정" else "-"
        ax.add_patch(Polygon(pts, closed=True, fc=p["color"], alpha=0.15, ec=p["color"], lw=1.4, ls=ls))
        for x0, x1, r, _ in p["seg"][1:]:
            ax.plot([x0, x0], [yc - r, yc + r], color=p["color"], lw=0.5, ls=ls)
        t0, t1 = p["thread"]
        for k in range(int((t1 - t0) / 1.3)):
            x = t0 + 0.65 + k * 1.3
            ax.plot([x, x + 0.6], [yc + G_HALF, yc + G_HALF - 0.9], color=p["color"], lw=0.5)
            ax.plot([x, x + 0.6], [yc - G_HALF, yc - G_HALF + 0.9], color=p["color"], lw=0.5)
        ax.plot([p["tip"] - 3, p["end"] + 3], [yc, yc], color="#999999", lw=0.5, ls="-.")
        for x0, x1, r, lab in p["seg"]:
            if lab:
                ax.text((x0 + x1) / 2, yc + r + 0.8, lab, ha="center", va="bottom", fontsize=7.5, color=p["color"])
        rmax = max(s[2] for s in p["seg"])
        dim(ax, p["tip"], p["end"], yc - rmax - 7, f"전장 {p['end'] - p['tip']:g}")
        dim(ax, p["tip"], t0, yc - rmax - 2.5, f"노출 {t0 - p['tip']:g}", p["color"])
        dim(ax, 0, p["end"], yc + rmax + 6.5, f"씰면 ~ 끝 {p['end']:g}", p["color"])
        ax.text(-78, yc + 3, p["name"], fontsize=11, weight="bold", color=p["color"], ha="left")
        ax.text(-78, yc - 2, f"몸통 Ø{p['od']:g}", fontsize=9, ha="left")
        ax.text(-78, yc - 6, p["note"], fontsize=7.5, ha="left", color="#444444", wrap=True)
    ax.axvline(0, color="k", lw=1.0, ls="--")
    ax.text(0.8, 28.5, "설치 기준면 (씰면)   <- 오일 쪽 | 하우징 쪽 ->", fontsize=9)
    ax.set_xlim(-80, 102)
    ax.set_ylim(-2 * gap - 28, 33)
    ax.set_aspect("equal")
    ax.set_xticks(range(-70, 101, 10))
    ax.grid(ls=":", lw=0.3)
    ax.set_yticks([])
    ax.set_xlabel("x (mm), 씰면 = 0 — 세 제품 같은 축척")
    ax.set_title("외형 비교 (반단면 아님, 바깥 윤곽) — HMT500(260313) vs E+E EE364 vs Vaisala MMT162\n"
                 "실선 = 설계값·원문 데이터시트, 점선 = 검색 치수로 배치한 추정", fontsize=11)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(HERE, f"outline-comparison.{ext}"), dpi=130)
    print(os.path.join(HERE, "outline-comparison.png"))


if __name__ == "__main__":
    main()
