"""DOTECH HMT500 2D 기구 도면 생성 (A3, SVG → PDF). 파라미터: hmt500_params.py

  python3 hardware/mech/hmt500_drawings.py  →  hardware/mech/out/HMT500-M-0xx.svg
  (PDF 변환: make_pdf.sh)

도면 관례: 제1각법(ISO-E), 회전체는 위쪽 반 = 단면(해칭), 아래쪽 반 = 외형.
일반 공차 ISO 2768-mK, 단위 mm.
"""

import html
import math
import os

import hmt500_params as P

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
W, H = 420.0, 297.0
FONT = "'Noto Sans KR','NanumGothic','Malgun Gothic',Arial,sans-serif"


class Sheet:
    def __init__(self, dwg_no, title, scale_txt, material="-", sheet_txt="1/1"):
        self.o = []
        self.dwg_no, self.title, self.scale_txt, self.material, self.sheet_txt = dwg_no, title, scale_txt, material, sheet_txt
        self.a = self.o.append

    # 기본 요소
    def line(self, x1, y1, x2, y2, cls="thick"):
        self.a(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" class="{cls}"/>')

    def poly(self, pts, cls="thick", close=False, fill=None):
        d = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        tag = "polygon" if close else "polyline"
        f = f' fill="{fill}"' if fill else ""
        self.a(f'<{tag} points="{d}" class="{cls}"{f}/>')

    def text(self, x, y, s, size=3.5, anchor="start", rot=0, bold=False, cls=""):
        tr = f' transform="rotate({rot} {x:.3f} {y:.3f})"' if rot else ""
        b = ' font-weight="700"' if bold else ""
        self.a(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}"{b}{tr} class="t {cls}">{html.escape(str(s))}</text>')

    def circle(self, x, y, r, cls="thin", fill="none"):
        self.a(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" class="{cls}" fill="{fill}"/>')

    def arrow(self, x, y, ang):
        """화살촉: (x,y) 끝점, ang = 화살이 가리키는 방향(deg)."""
        L, Wd = 2.6, 0.9
        a = math.radians(ang)
        bx, by = x - L * math.cos(a), y - L * math.sin(a)
        px, py = -math.sin(a) * Wd, math.cos(a) * Wd
        self.a(f'<polygon points="{x:.3f},{y:.3f} {bx + px:.3f},{by + py:.3f} {bx - px:.3f},{by - py:.3f}" class="arrow"/>')

    # 치수
    def dim_h(self, xa, ya, xb, yb, yd, txt, above=True):
        """두 점(xa,ya),(xb,yb)의 수평 거리 치수를 높이 yd 에."""
        for x, y in ((xa, ya), (xb, yb)):
            s = 1 if yd > y else -1
            self.line(x, y + s * 1.0, x, yd + s * 1.5, "thin")
        self.line(xa, yd, xb, yd, "thin")
        if abs(xb - xa) > 7:
            self.arrow(xa, yd, 180)
            self.arrow(xb, yd, 0)
        else:
            self.arrow(xa, yd, 0)
            self.arrow(xb, yd, 180)
            self.line(xa - 5, yd, xa, yd, "thin")
            self.line(xb, yd, xb + 5, yd, "thin")
        self.text((xa + xb) / 2, yd - 1.0 if above else yd + 4.0, txt, 3.2, "middle")

    def dim_v(self, x, ya, yb, txt, side=1):
        """수직 치수(지름 등): x 위치, ya..yb."""
        self.line(x, ya, x, yb, "thin")
        self.arrow(x, min(ya, yb), -90)
        self.arrow(x, max(ya, yb), 90)
        self.text(x - 1.0 if side > 0 else x + 3.8, (ya + yb) / 2, txt, 3.2, "middle", rot=-90)

    def dim_v_ext(self, x_feat, x_dim, ya, yb, txt):
        for y in (ya, yb):
            self.line(x_feat + (1 if x_dim > x_feat else -1), y, x_dim + (1.5 if x_dim > x_feat else -1.5), y, "thin")
        self.dim_v(x_dim, ya, yb, txt)

    def leader(self, x, y, tx, ty, txt, size=3.2):
        self.line(x, y, tx, ty, "thin")
        self.arrow(x, y, math.degrees(math.atan2(y - ty, x - tx)))
        end = tx + (22 if tx >= x else -22)
        self.line(tx, ty, end, ty, "thin")
        self.text(tx + (1 if tx >= x else -1), ty - 1.0, txt, size, "start" if tx >= x else "end")

    def balloon(self, x, y, bx, by, n):
        self.line(x, y, bx, by, "thin")
        self.circle(x, y, 0.6, "thin", "#000")
        self.circle(bx, by, 4.2, "thick", "#fff")
        self.text(bx, by + 1.4, n, 4.0, "middle", bold=True)

    def finish(self, x, y, ra):
        """표면 거칠기 기호 (√ + Ra)."""
        self.poly([(x - 2, y - 3.4), (x, y), (x + 4.5, y - 7.5), (x + 10, y - 7.5)], "thin")
        self.text(x + 3.5, y - 8.3, f"Ra {ra}", 2.6)

    # 도면틀
    def frame(self):
        self.a(f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" class="thick" fill="none"/>')
        for i in range(8):
            x = 10 + (W - 20) * (i + 0.5) / 8
            self.text(x, 8.2, str(i + 1), 2.8, "middle")
        for i, ch in enumerate("ABCDEF"):
            y = 10 + (H - 20) * (i + 0.5) / 6
            self.text(6.5, y + 1, ch, 2.8, "middle")
        # 표제란
        x0, y0, w, h = W - 10 - 180, H - 10 - 42, 180, 42
        self.a(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" class="thick" fill="#fff"/>')
        rows = [y0 + 10, y0 + 18, y0 + 26, y0 + 34]
        for yy in rows:
            self.line(x0, yy, x0 + w, yy, "thin")
        self.line(x0 + 60, y0 + 10, x0 + 60, y0 + h, "thin")
        self.line(x0 + 120, y0 + 10, x0 + 120, y0 + h, "thin")
        self.text(x0 + 3, y0 + 7, "(주)두텍  DOTECH Co., Ltd.", 4.2, bold=True)
        self.text(x0 + w - 3, y0 + 7, "HMT500(260313) 오일 수분 트랜스미터", 3.4, "end")
        cells = [("품명", self.title, x0, rows[0]), ("도번", self.dwg_no, x0 + 60, rows[0]),
                 ("Rev / 일자", f"{P.DRAWING_REV} / {P.DATE}", x0 + 120, rows[0]),
                 ("재질", self.material, x0, rows[1]), ("척도", self.scale_txt, x0 + 60, rows[1]),
                 ("단위 / 투상", "mm / 제1각법", x0 + 120, rows[1]),
                 ("일반공차", "ISO 2768-mK", x0, rows[2]), ("표면(지정 외)", "Ra 1.6", x0 + 60, rows[2]),
                 ("쪽", self.sheet_txt, x0 + 120, rows[2]),
                 ("작성", "HMT500 설계", x0, rows[3]), ("검토", "", x0 + 60, rows[3]), ("승인", "", x0 + 120, rows[3])]
        for lab, val, cx, cy in cells:
            self.text(cx + 1.5, cy + 3.2, lab, 2.3, cls="muted")
            self.text(cx + 1.5, cy + 7.2, val, 3.3 if len(str(val)) < 22 else 2.7, bold=lab in ("도번", "품명"))
        # 제1각법 기호
        sx, sy = x0 + 150, rows[1] + 4
        self.a(f'<polygon points="{sx},{sy - 2} {sx + 7},{sy - 3.2} {sx + 7},{sy + 3.2} {sx},{sy + 2}" class="thin" fill="none"/>')
        self.circle(sx + 13, sy, 3.2)
        self.circle(sx + 13, sy, 1.6)

    def svg(self):
        style = f"""<style>
 .thick{{stroke:#000;stroke-width:0.5;fill:none;stroke-linecap:round;stroke-linejoin:round}}
 .thin{{stroke:#000;stroke-width:0.22;fill:none}}
 .center{{stroke:#000;stroke-width:0.2;stroke-dasharray:8 1.5 1.5 1.5;fill:none}}
 .hidden{{stroke:#000;stroke-width:0.25;stroke-dasharray:2 1.2;fill:none}}
 .hatchfill{{stroke:#000;stroke-width:0.5;fill:url(#hatch)}}
 .hatchfill2{{stroke:#000;stroke-width:0.5;fill:url(#hatch2)}}
 .part2{{stroke:#000;stroke-width:0.35;fill:url(#hatch2)}}
 .buy{{stroke:#000;stroke-width:0.35;fill:#e8e8e8}}
 .green{{stroke:#000;stroke-width:0.35;fill:#cfe8d0}}
 .arrow{{fill:#000;stroke:none}}
 .t{{font-family:{FONT};fill:#000}}
 .muted{{fill:#555}}
</style>
<defs>
 <pattern id="hatch" width="2.2" height="2.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="2.2" stroke="#000" stroke-width="0.18"/></pattern>
 <pattern id="hatch2" width="2.2" height="2.2" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="2.2" stroke="#000" stroke-width="0.18"/></pattern>
</defs>"""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
                f'<rect width="{W}" height="{H}" fill="#fff"/>{style}' + "\n".join(self.o) + "</svg>")


# ── 회전체 그리기 ──
class View:
    """부품 좌표 (x, r) → 도면 좌표. 위쪽 반 = 단면, 아래쪽 반 = 외형."""

    def __init__(self, sh, ox, oy, s):
        self.sh, self.ox, self.oy, self.s = sh, ox, oy, s

    def X(self, x):
        return self.ox + self.s * x

    def Yu(self, r):
        return self.oy - self.s * r

    def Yl(self, r):
        return self.oy + self.s * r

    def section(self, outer, inner, cls="hatchfill"):
        """outer/inner: [(x0, x1, r)] 구간별 반지름 (앞→뒤). inner r=0 은 속이 참."""
        pts = []
        for x0, x1, r in outer:
            pts += [(self.X(x0), self.Yu(r)), (self.X(x1), self.Yu(r))]
        for x0, x1, r in reversed(inner):
            pts += [(self.X(x1), self.Yu(r)), (self.X(x0), self.Yu(r))]
        self.sh.poly(pts, cls, close=True)

    def exterior(self, outer):
        prev = 0
        for i, (x0, x1, r) in enumerate(outer):
            self.sh.line(self.X(x0), self.Yl(r), self.X(x1), self.Yl(r))
            rmax = max(r, prev)
            self.sh.line(self.X(x0), self.oy, self.X(x0), self.Yl(rmax))
            prev = r
        self.sh.line(self.X(outer[-1][1]), self.oy, self.X(outer[-1][1]), self.Yl(outer[-1][2]))

    def axis(self, x0, x1):
        self.sh.line(self.X(x0) - 6, self.oy, self.X(x1) + 6, self.oy, "center")


def segs(*pairs):
    return list(pairs)


# ── 부품 형상(단면 구간) ──
B, C, E, Hs, O = P.BODY, P.CAP, P.ENDCAP, P.HOUSING, P.ORING
D = P.FRONT_SHIFT                        # Rev G: 커넥터·캡·프로브를 G½ 안쪽으로 옮긴 거리
HEX_R = P.hex_corner_d(B["hexa"]["af"]) / 2
R_OD = Hs["od"] / 2                     # 15.0 (Rev H Ø30)
R_SEAL = B["seal"]["d"] / 2             # 13.5
R_GRV = O["groove_d"] / 2               # 12.3
R_MT = B["mthread"]["d"] / 2            # 13.0 (M26 바깥지름)
R_MTm = B["mthread"]["d_minor"] / 2     # 12.4585 (M26x1 암나사 안지름)
MT = B["mthread"]["thread"].replace("x", "×")          # M26×1-6g
MTH = Hs["thread"].replace("x", "×")                    # M26×1-6H
MTL = E["mthread"]["thread"].replace("x", "×")          # M26×1-LH-6g
ORT = f"O링 {O['id']:g}×{O['cs']:g}"
DS, DSB = f"Ø{B['seal']['d']:g}", f"Ø{Hs['seal_bore']:g}"
AFE = f"AF{E['flange']['flats_af']:g}"
BODY_OUT = [(*B["gthread"]["x"], B["gthread"]["d"] / 2),
            (*B["relief"]["x"], B["relief"]["d"] / 2), (*B["hexa"]["x"], HEX_R), (*B["collar"]["x"], R_OD),
            (B["seal"]["x"][0], B["seal"]["groove_x"][0], R_SEAL), (*B["seal"]["groove_x"], R_GRV),
            (B["seal"]["groove_x"][1], B["seal"]["x"][1], R_SEAL), (*B["mthread"]["x"], R_MT)]
BODY_IN = [(*B[k]["x"], B[k]["d"] / 2) for k in ("cap_sleeve", "conn_cbore", "conn_land", "conn_thread", "channel", "cbore")]
R_CAP = C["od"] / 2
CAP_OUTLINE = C["profile"][:6] + [(C["x_rear"], 0.0)]      # 바깥 윤곽 (끝 → 열린 끝)
# 센서 커넥터 HTX99R-SC 단면 (제품 좌표, 모델 형상값)
SC = P.SENSOR_CONN
_x = lambda y: SC["x0"] - y       # noqa: E731
CONN_OUT = [(_x(15), _x(9.5), 5.0), (_x(9.5), _x(8), 4.05), (_x(8), _x(7), SC["flange_d"] / 2),
            (_x(7), _x(5.5), SC["oring_groove"]["d"] / 2), (_x(5.5), _x(0), 5.0)]
CONN_IN = [(_x(15), _x(7), 0.0), (_x(7), _x(0), 3.5)]
h0, h1 = Hs["x"]
_sl, _tl = Hs["seal_len"], Hs["thread_len"]
HOUS_OUT = [(h0, h1, R_OD)]
HOUS_IN = [(h0, h0 + _sl, Hs["seal_bore"] / 2), (h0 + _sl, h0 + _sl + _tl, R_MTm),
           (h0 + _sl + _tl, h1 - _sl - _tl, Hs["id"] / 2),
           (h1 - _sl - _tl, h1 - _sl, R_MTm), (h1 - _sl, h1, Hs["seal_bore"] / 2)]
END_OUT = [(*E["mthread"]["x"], R_MT), (E["seal"]["x"][0], E["seal"]["groove_x"][0], R_SEAL),
           (*E["seal"]["groove_x"], R_GRV), (E["seal"]["groove_x"][1], E["seal"]["x"][1], R_SEAL),
           (*E["flange"]["x"], R_OD)]
END_IN = [(*E["cbore"]["x"], E["cbore"]["d"] / 2), (*E["thread"]["x"], E["thread"]["d_minor"] / 2)]


def thread_lines(v, x0, x1, r, both=True):
    """나사 골/산 지름 가는 선 (위·아래)."""
    v.sh.line(v.X(x0), v.Yl(r), v.X(x1), v.Yl(r), "thin")
    if both:
        v.sh.line(v.X(x0), v.Yu(r), v.X(x1), v.Yu(r), "thin")


def draw_body(v, detail=True):
    v.section(BODY_OUT, BODY_IN)
    v.exterior(BODY_OUT)
    sh = v.sh
    # 외형: 육각 면 선, 나사 골지름(가는 선)
    x0, x1 = B["hexa"]["x"]
    sh.line(v.X(x0), v.Yl(HEX_R / 2), v.X(x1), v.Yl(HEX_R / 2))
    thread_lines(v, *B["gthread"]["x"], B["gthread"]["d_minor"] / 2)
    ct = B["conn_thread"]                                   # 커넥터 체결 암나사 (바깥지름 가는 선)
    sh.line(v.X(ct["x"][0]), v.Yu(ct["d_major"] / 2), v.X(ct["x"][1]), v.Yu(ct["d_major"] / 2), "thin")
    thread_lines(v, *B["mthread"]["x"], R_MTm - 0.08)
    # 내부 외형(아래 반): 숨은선
    for x0_, x1_, r in BODY_IN:
        sh.line(v.X(x0_), v.Yl(r), v.X(x1_), v.Yl(r), "hidden")
    T = B["holder_taps"]                          # PCB 홀더 고정 M2 탭 (숨은선)
    xb = B["cbore"]["x"][0]
    for r in (T["pcd"] / 2 - T["d"] / 2, T["pcd"] / 2 + T["d"] / 2):
        sh.line(v.X(xb - T["depth"]), v.Yl(r), v.X(xb), v.Yl(r), "hidden")
    sh.line(v.X(xb - T["depth"]), v.Yl(T["pcd"] / 2 - T["d"] / 2), v.X(xb - T["depth"]), v.Yl(T["pcd"] / 2 + T["d"] / 2), "hidden")


def draw_cap(v):
    """두텍 SUS 오일 필터 (390000-001100): 위 = 단면(윤곽 그대로), 아래 = 외형."""
    sh = v.sh
    sh.poly([(v.X(x), v.Yu(r)) for x, r in C["profile"]], "hatchfill2", close=True)
    pts = [(C["x_tip"], 0.0)] + CAP_OUTLINE
    sh.poly([(v.X(x), v.Yl(r)) for x, r in pts], "thick")
    for x in (C["x_tip"] + C["chamfer"], C["rear_relief"]["x"][0]):
        sh.line(v.X(x), v.oy, v.X(x), v.Yl(R_CAP), "thick")
    x0, x1 = C["thread_x"]
    sh.line(v.X(x0), v.Yu(5.0), v.X(x1), v.Yu(5.0), "thin")      # 암나사 바깥지름 (M10)
    hr = C["hole_d"] / 2 * v.s
    for x in sorted({x for x, _ in C["holes"]}):
        # 단면(위): 18° 기울어진 구멍이 벽을 관통 → 해칭 끊김 / 외형(아래): 정면 구멍
        sh.a(f'<rect x="{v.X(x) - hr:.3f}" y="{v.Yu(R_CAP):.3f}" width="{2 * hr:.3f}" height="{v.s * (R_CAP - C["bore"] / 2):.3f}" style="fill:#fff;stroke:#000;stroke-width:0.25"/>')
        sh.circle(v.X(x), v.Yl(0), hr, "thin")


def draw_housing(v):
    v.section(HOUS_OUT, HOUS_IN, "hatchfill2")
    v.exterior(HOUS_OUT)
    # 암나사 바깥지름(가는 선, 단면 쪽)
    for a, b in ((h0 + _sl, h0 + _sl + _tl), (h1 - _sl - _tl, h1 - _sl)):
        v.sh.line(v.X(a), v.Yu(R_MT), v.X(b), v.Yu(R_MT), "thin")
    for x0_, x1_, r in HOUS_IN:
        v.sh.line(v.X(x0_), v.Yl(r), v.X(x1_), v.Yl(r), "hidden")


def draw_endcap(v):
    v.section(END_OUT, END_IN)
    v.exterior(END_OUT)
    sh = v.sh
    thread_lines(v, *E["mthread"]["x"], R_MTm - 0.08)
    f0, f1 = E["thread"]["x"]
    sh.line(v.X(f0), v.Yu(E["thread"]["d"] / 2), v.X(f1), v.Yu(E["thread"]["d"] / 2), "thin")   # M16 암나사
    # 렌치 평면 AF28 (외형 쪽)
    sh.line(v.X(f0), v.Yl(E["flange"]["flats_af"] / 2), v.X(f1), v.Yl(E["flange"]["flats_af"] / 2))
    for x0_, x1_, r in END_IN:
        sh.line(v.X(x0_), v.Yl(r), v.X(x1_), v.Yl(r), "hidden")


def buy_rect(v, x0, x1, r0, r1, cls="buy", lower=True):
    sh = v.sh
    sh.a(f'<rect x="{v.X(x0):.3f}" y="{v.Yu(r1):.3f}" width="{v.s * (x1 - x0):.3f}" height="{v.s * (r1 - r0):.3f}" class="{cls}"/>')
    if lower:
        sh.a(f'<rect x="{v.X(x0):.3f}" y="{v.Yl(r0):.3f}" width="{v.s * (x1 - x0):.3f}" height="{v.s * (r1 - r0):.3f}" class="{cls}"/>')


# ═════════════════════ 시트 1: 조립도 ═════════════════════
def oring_xsec(v, gx):
    """O링 단면(검은 원) — 홈 중심, 위(단면) 쪽."""
    c = (gx[0] + gx[1]) / 2
    r0 = O["groove_d"] / 2 + O["cs"] / 2 - 0.15
    v.sh.a(f'<circle cx="{v.X(c):.3f}" cy="{v.Yu(r0):.3f}" r="{O["cs"] / 2 * v.s:.3f}" style="fill:#000;stroke:none"/>')


def draw_pcb_inside(v):
    """조립도: PCB(단면 평면에 놓임) 위쪽 반 + 홀더·지지링 단면."""
    sh = v.sh
    Pc, Hh, R = P.PCB, P.PCB_HOLDER, P.PCB_RING
    for x0_, x1_, d_ in P.POTTING2["zones"]:       # ⑤ 2차 몰딩 (하우징 안 전체)
        sh.a(f'<rect x="{v.X(x0_):.3f}" y="{v.Yu(d_ / 2):.3f}" width="{v.s * (x1_ - x0_):.3f}" height="{v.s * d_ / 2:.3f}" '
             f'style="fill:#f3e7c9;stroke:none"/>')
    # 홀더: 홈(단면 평면) 앞쪽만 재료가 보임
    v.section([(Hh["x"][0], Hh["slot_x"][0], Hh["d"] / 2)], [(Hh["x"][0], Hh["slot_x"][0], Hh["hole_d"] / 2)], "part2")
    # 지지링: 홈 바깥 띠만 재료
    v.section([(*R["x"], R["od"] / 2)], [(*R["x"], R["slot_y"])], "part2")
    # PCB 외곽 (위쪽 반)
    pts = [(v.X(Pc["x"][0]), v.oy)]
    for x0, x1, w in Pc["sections"]:
        pts += [(v.X(x0), v.Yu(w / 2)), (v.X(x1), v.Yu(w / 2))]
    pts += [(v.X(Pc["x"][1]), v.oy)]
    sh.poly(pts, "green", close=True)
    for x, y, a, b, h, side in P.pcb_part_boxes():
        if side > 0 and y + b / 2 > 0:
            y0 = max(0.0, y - b / 2)
            sh.a(f'<rect x="{v.X(x - a / 2):.3f}" y="{v.Yu(y + b / 2):.3f}" width="{v.s * a:.3f}" height="{v.s * (y + b / 2 - y0):.3f}" fill="#333" stroke="none"/>')
    for x, y in Pc["holes"]:
        if y > 0:
            sh.circle(v.X(x), v.Yu(y), Pc["hole_d"] / 2 * v.s, "thin", "#fff")
    # 센서 하네스 W-1: 피드스루 뒤 핀 → 홀더 구멍 → J3 플러그 (위에서 본 투영)
    Wh = P.HARNESS
    pl = Wh["plug"]
    sh.a(f'<rect x="{v.X(pl["x"][0]):.3f}" y="{v.Yu(pl["y"][1]):.3f}" width="{v.s * (pl["x"][1] - pl["x"][0]):.3f}" '
         f'height="{v.s * pl["y"][1]:.3f}" style="fill:#eee6cc;stroke:#000;stroke-width:0.18"/>')
    Pt = P.POTTING                                # ⑤ 에폭시 몰딩 (Ø7 통로 전 길이)
    sh.a(f'<rect x="{v.X(Pt["x"][0]):.3f}" y="{v.Yu(Pt["d"] / 2):.3f}" width="{v.s * (Pt["x"][1] - Pt["x"][0]):.3f}" '
         f'height="{v.s * Pt["d"] / 2:.3f}" style="fill:#d9c9a8;stroke:#000;stroke-width:0.25"/>')
    W2 = P.HARNESS2                               # ⑱ W-2: J1 → M12
    p2 = W2["plug"]
    sh.a(f'<rect x="{v.X(p2["x"][0]):.3f}" y="{v.Yu(p2["y"][1]):.3f}" width="{v.s * (p2["x"][1] - p2["x"][0]):.3f}" '
         f'height="{v.s * p2["y"][1]:.3f}" style="fill:#eee6cc;stroke:#000;stroke-width:0.18"/>')
    for yk in (4.375, 1.875):
        sh.poly([(v.X(p2["x"][1]), v.Yu(yk)), (v.X(66), v.Yu(yk * 0.8)), (v.X(Pc["x"][1] + 0.4), v.Yu(yk * 0.45)),
                 (v.X(P.CONNECTOR["inner"]["x"][0]), v.Yu(yk * 0.45))], "thin")
    xp = SC["x0"] - SC["pin_y"]                   # ⑮ 뒤 핀 끝 → Ø7 관통 통로 → J3
    g = Wh["conn_grid"] / 2
    for yp, yk in ((g, 1.5), (g * 0.4, 0.5)):
        sh.poly([(v.X(xp), v.Yu(yp)), (v.X(xp + 4), v.Yu(yp * 0.8)), (v.X(P.BODY["channel"]["x"][1] - 1), v.Yu(yk)),
                 (v.X(pl["x"][0]), v.Yu(yk))], "thin")


def sheet_assembly():
    sh = Sheet("HMT500-M-000", "HMT500 조립도 (Assembly)", "2 : 1", "부품표 참조", "1/4")
    s = 2.0
    v = View(sh, 150, 100, s)
    v.axis(P.TIP_X, P.END_X)
    # 구매품/내부 (먼저)
    Sd, Pc, Cn, SP = P.SEAL, P.PCB, P.CONNECTOR, P.SENSOR_PROBE
    buy_rect(v, *Sd["x"], Sd["id"] / 2, Sd["od"] / 2, "green")
    # 센서 커넥터 HTX99R-SC (단면) + 핀, 센서 프로브
    v.section(CONN_OUT, CONN_IN, "buy")
    hp = SP["pins"]["pitch"] / 2
    buy_rect(v, _x(7), _x(SC["pin_y"]), hp - 0.32, hp + 0.32, "buy", lower=False)
    buy_rect(v, *SP["pins"]["x"], hp - SP["pins"]["d"] / 2, hp + SP["pins"]["d"] / 2, "buy", lower=False)
    buy_rect(v, *SP["plug"]["x"], 0, SP["plug"]["d"] / 2, "buy", lower=False)
    buy_rect(v, SP["board"]["x"][0], SP["plug"]["x"][0], 0, SP["board"]["w"] / 2, "green", lower=False)
    mk = SP["mk33"]
    sh.a(f'<rect x="{v.X(SP["board"]["x"][0] + 0.3):.3f}" y="{v.Yu(2.7):.3f}" width="{s * mk["l"]:.3f}" height="{s * 1.9:.3f}" fill="#555" stroke="none"/>')
    sh.text(v.X(SP["board"]["x"][0] + 0.3 + mk["l"] / 2), v.Yu(0.3), "MK33", 1.6, "middle", cls="muted")
    f1 = E["flange"]["x"][1]
    buy_rect(v, *Cn["inner"]["x"], 0, 7.95, lower=False)      # 커넥터 M16 나사부 (엔드캡에 체결)
    buy_rect(v, *Cn["body"]["x"], 0, Cn["body"]["d"] / 2)
    buy_rect(v, *Cn["thread"]["x"], 0, Cn["thread"]["d"] / 2)
    # 가공품
    draw_body(v)
    draw_cap(v)
    draw_endcap(v)
    oy_ = P.SENSOR_CONN["oring_groove"]["y"]
    c_ = _x((oy_[0] + oy_[1]) / 2)
    v.sh.a(f'<circle cx="{v.X(c_):.3f}" cy="{v.Yu(SC["oring_groove"]["d"] / 2 + 0.45):.3f}" r="{P.CONN_ORING["cs"] / 2 * v.s:.3f}" style="fill:#000;stroke:none"/>')
    # 외형 반쪽: 하우징에 가려지는 바디·엔드캡 선 지우기 → 하우징 외형만
    sh.a(f'<rect x="{v.X(h0):.3f}" y="{v.oy + 0.3:.3f}" width="{s * (h1 - h0):.3f}" height="{s * R_OD:.3f}" fill="#fff" stroke="none"/>')
    draw_housing(v)
    for gx in (B["seal"]["groove_x"], E["seal"]["groove_x"]):
        oring_xsec(v, gx)
    draw_pcb_inside(v)
    # 풍선
    bl = [("2", v.X(-45 + D), v.Yu(R_CAP), v.X(-45 + D), 46), ("6", v.X(-43 + D), v.Yu(1.5), v.X(-24), 58),
          ("15", v.X(-34 + D), v.Yu(4.5), v.X(-15), 46), ("16", v.X(-8.75), v.Yu(4.6), v.X(-2), 58),
          ("1", v.X(-8), v.Yu(10.5), v.X(-15.5), 58), ("7", v.X(-1), v.Yu(13.5), v.X(-8.5), 58),
          ("5", v.X(-2), v.Yu(2.6), v.X(-4), 46), ("10", v.X(15), v.Yu((R_GRV + R_SEAL) / 2), v.X(18), 58),
          ("12", v.X(11.3), v.Yu(7), v.X(6), 58), ("17", v.X(19.5), v.Yu(2), v.X(23), 46),
          ("8", v.X(28), v.Yu(10), v.X(32), 46), ("3", v.X(43), v.Yu(R_OD), v.X(48), 58),
          ("13", v.X(59), v.Yu(11.8), v.X(58), 46),
          ("4", v.X(75), v.Yu(R_OD), v.X(68), 46), ("11", v.X(78), v.Yu(10), v.X(80), 58),
          ("9", v.X(86), v.Yu(6), v.X(91), 46), ("18", v.X(58.5), v.Yu(4), v.X(64), 58)]
    for n, x, y, bx, by in bl:
        sh.balloon(x, y, bx, by, n)
    # 치수 (아래쪽)
    yb = v.Yl(R_OD + 0.6)
    sh.dim_h(v.X(P.TIP_X), v.Yl(R_CAP), v.X(P.END_X), v.Yl(6), yb + 30, f"{P.OVERALL:.0f}")
    sh.dim_h(v.X(P.TIP_X), v.Yl(R_CAP), v.X(-14), v.Yl(7), yb + 10, f"{-14 - P.TIP_X:g}  (노출 프로브)")
    sh.dim_h(v.X(-14), v.Yl(10.5), v.X(0), v.Yl(HEX_R), yb + 10, "14")
    sh.dim_h(v.X(0), v.Yl(HEX_R), v.X(f1), v.Yl(R_OD), yb + 20, f"{f1:.0f}")
    sh.dim_h(v.X(0), v.Yl(HEX_R), v.X(P.END_X), v.Yl(6), yb + 10, f"{P.END_X:.0f}")
    sh.dim_v_ext(v.X(45), v.X(45), v.Yu(R_OD), v.Yl(R_OD), f"Ø{Hs['od']:g}")
    sh.dim_v_ext(v.X(-59.3 + D), v.X(-59.3 + D), v.Yu(R_CAP), v.Yl(R_CAP), "Ø12")
    sh.leader(v.X(-8), v.Yl(10.5), v.X(-24), v.Yl(10.5) + 14, "G1/2-A (ISO 228-1), 안쪽 Ø12.3 × 3.5 캡 칼라")
    sh.leader(v.X(4), v.Yl(HEX_R), v.X(16), v.Yl(HEX_R) + 12, "육각 AF27")
    sh.text(v.X(0) - 1, yb + 5, "A", 3.5, "middle", bold=True)
    sh.a(f'<rect x="{v.X(0) - 3:.2f}" y="{yb + 1.2:.2f}" width="4.6" height="5" class="thin" fill="none"/>')
    sh.text(v.X(0) - 4.5, yb + 5, "씰면 = 기준면", 2.8, "end")
    # 부품표
    tx, ty = W - 190, 165.5
    cols = [(0, 9, "No"), (9, 30, "도번"), (39, 45, "품명"), (84, 36, "재질"), (120, 8, "수량"), (128, 52, "비고")]
    rh = 3.8
    sh.a(f'<rect x="{tx}" y="{ty}" width="180" height="{rh * (len(P.PARTS) + 1)}" class="thick" fill="#fff"/>')
    for c0, cw, lab in cols:
        sh.text(tx + c0 + 1, ty + 3.4, lab, 2.5, bold=True)
        if c0:
            sh.line(tx + c0, ty, tx + c0, ty + rh * (len(P.PARTS) + 1), "thin")
    for i, row in enumerate(P.PARTS):
        y = ty + rh * (i + 1)
        sh.line(tx, y, tx + 180, y, "thin")
        for (c0, cw, _), val in zip(cols, row):
            sh.text(tx + c0 + 1, y + 3.4, str(val), 2.2 if len(str(val)) > 18 else 2.5)
    # 주기
    notes = [
        "주기 (NOTES)",
        "1. 피드스루 없음. 압력 격벽 = ⑯ O링 + ⑮ 몰드 핀 + ⑤ 몰딩. ⑤ 상온경화 에폭시 1종: 1차 = ① Ø7 통로(" + f"{B['channel']['x'][1] - B['channel']['x'][0]:g}" + "), 2차 = 하우징 안 전체 (양은 실측, ④ 안까지).",
        f"2. ①–③ {MTH[:-3]} 오른나사, ③–④ {MTH[:-3]} 왼나사 (턴버클) + O링 ⑩ ({DSB} H8/f7). ③만 돌려 체결 → ①·④·⑧·⑨·⑰·⑱은 돌지 않음 (하네스 꼬임 없음).",
        "3. 나사 고정제 중강도(Loctite 243 급), 체결 토크 5 N·m (TBD). ① 육각 AF27 / ④ 평면 " + AFE + " 을 고정하고 ③을 돌림.",
        "4. O링 FKM 75, 조립 전 실리콘 그리스 얇게 도포. 나사·모서리 통과 시 O링 손상 주의 (C0.5 도입부).",
        "5. 조립 (조립 시뮬레이션 반영): ⑰을 ⑮ 뒤 핀에 납땜 → ⑯ → ⑰ 플러그를 Ø7 통로로 뒤로 뺌 → ⑮를 ①에 체결 → 1차 몰딩 (프로브 아래, 뒤에서 주입·경화)",
        "    → [벤치] ⑧을 ⑫ 홈에 끼우고 가로 나사 M2×12 ×2, ⑳ 샤시 선을 ⑧ J5에 납땜, SWD 기록·기능 검사 → ⑰ 플러그를 ⑫ 창으로 꿰고 ⑫+⑧을 ①에 넣음",
        "    → ⑫ 축 나사 M2×6 (아래) + M2×8 (위, ⑳ 링 단자 함께)를 뒤에서 조임 → ⑰을 J3에 꽂음 → ⑬ → ⑨에 ⑱ 납땜 후 ⑨를 ④에 체결",
        "    → ③을 ⑧ 위로 씌움 (턴버클 시작 위치, 7 mm 뒤) → ④를 옆으로 비켜 들고 공구 T-001로 ⑱ 플러그를 ③ 뒤 입구로 밀어 J1에 꽂음",
        "    → ①·④를 잡고 ③만 7바퀴 돌려 양쪽 동시 체결 (④가 14 mm 다가오며 ⑱이 ④ 안에서 접힘) → 2차 몰딩: ⑨ 위, ④ M3 구멍으로 진공 주입 → ⑲로 막음",
        "    → ⑥ 센서 프로브를 ⑮에 꽂고 ② 보호캡을 ⑮ 위 나사(M10×1.0)에 체결 → ⑦. 상세 = 조립 시방서 HMT500-A-001. 몰딩 후 전자부 수리 불가.",
        "6. 내압 기준 확인 필요: 50 bar / 시험 75 bar는 제안값이며 승인 전 사용 금지 (접액부 = ①·②·⑥·⑦·⑮·⑯). ⑯ O링이 밀봉, ⑮ 몰드 핀 + ⑤ 몰딩이 전자부 격벽.",
        "7. ③ 외면 레이저 마킹: 모델명·출력·전원·핀맵·시리얼. 접액부 1.4404, EN 10204 3.1.",
        "8. ⑧ PCB는 ①에 고정(⑫)되어 ③·④ 체결 시 함께 돌지 않음. PCB 외곽·부품 높이: HMT500-M-105~106 / E-301.",
        "9. ⑰ 센서 하네스: JST SH 1.0 mm 4P (SHR-04V-S + SSH-003T-P0.2-H) ↔ ⑧ J3 SM04B-SRSS-TB (옆 삽입). 1·2 = MK33, 3·4 = Pt1000 (2선식).",
        f"    PTFE AWG30, {P.HARNESS['length']:g} mm (⑮ 핀 → J3). ② = 보호캡 M-102 (두텍 390000-001100 기반, 끝 5.5 연장, SUS304). JST SH 정격 −25~+85 °C → ⑧ 앞 끝 온도 시험으로 확인.",
        "10. ⑱ M12 하네스: JST GH 1.25 mm 8P (GHR-08V-S + SSHL-002T-P0.2) ↔ ⑧ J1 SM08B-GHS-TB (옆 삽입, 입구 뒤쪽). 핀 n = M12 핀 n, PTFE AWG28 40 mm.",
        "    샤시: ⑳ AWG28 선 25 mm (⑧ J5 → M2 링 단자 → ⑫ 위 축 나사 → ① 금속 탭). 몰딩 전 SWD 기록·기능 검사·1차 교정, 최종 교정은 2차 몰딩 경화 뒤.",
    ]
    for i, n in enumerate(notes):
        sh.text(18, 186 + i * 5.8, n, 2.9 if i else 3.6, bold=(i == 0))
    sh.text(18, 22, "HMT500 조립도  —  반단면 (위: 단면, 아래: 외형)", 5, bold=True)
    sh.text(18, 29, "오일 측(프로브)  ←                                                                                 →  하우징·커넥터", 3.0, cls="muted")
    sh.frame()
    return sh


# ═════════════════════ 시트 2: 바디 부품도 ═════════════════════
def sheet_body():
    sh = Sheet("HMT500-M-101", "프로세스 바디 (Process body)", "3 : 1", "SUS316L (1.4404)", "2/4")
    s = 3.0
    v = View(sh, 150, 120, s)
    v.axis(B["gthread"]["x"][0], B["mthread"]["x"][1])
    draw_body(v)
    X = v.X
    RM = max(HEX_R, R_OD)
    # 길이 치수 (아래 사슬)
    y1 = v.Yl(RM) + 12
    xg, xe = B["gthread"]["x"][0], B["mthread"]["x"][1]
    chain = [(xg, 0, 10.5, HEX_R), (*B["hexa"]["x"], HEX_R, HEX_R), (*B["collar"]["x"], R_OD, R_OD),
             (*B["seal"]["x"], R_SEAL, R_SEAL), (*B["mthread"]["x"], R_MT, R_MT)]
    for xa, xb, ra, rb in chain:
        sh.dim_h(X(xa), v.Yl(ra), X(xb), v.Yl(rb), y1, f"{xb - xa:g}")
    sh.dim_h(X(xg), v.Yl(10.5), X(xe), v.Yl(R_MT), y1 + 11, f"{xe - xg:g}")
    sh.dim_h(X(-2), v.Yl(9.2), X(0), v.Yl(HEX_R), v.Yl(HEX_R) + 5, "2", above=True)
    # 내부·홈 치수 (위)
    yt = v.Yu(RM) - 10
    g0, g1 = B["seal"]["groove_x"]
    s0_ = B["seal"]["x"][0]
    sh.dim_h(X(s0_), v.Yu(R_SEAL), X(g0), v.Yu(R_GRV), yt, f"{g0 - s0_:.2f}")
    sh.dim_h(X(g0), v.Yu(R_GRV), X(g1), v.Yu(R_GRV), yt - 8, f"{g1 - g0:.1f} (+0.1/0)")
    # 지름
    for x, r, t in ((-1, 9.2, "Ø18.4"), (sum(B["collar"]["x"]) / 2, B["collar"]["d"] / 2, f"Ø{B['collar']['d']:g}"),
                    (B["seal"]["x"][1] - 0.3, R_SEAL, f"{DS} f7"), (B["mthread"]["x"][1] - 3, R_MT, MT)):
        sh.dim_v(X(x), v.Yu(r), v.Yl(r), t)
    sl = B["cap_sleeve"]
    sh.leader(X(sl["x"][0] + 1), v.Yu(sl["d"] / 2), X(-12), 30,
              f"캡 칼라 Ø{sl['d']:g} (+0.1/0) 깊이 {sl['x'][1] - sl['x'][0]:g} — 보호캡 뿌리를 감쌈 (HTX99R 굽힘 보호)")
    sh.leader(X(B["conn_land"]["x"][0] + 0.5), v.Yu(5.0), X(-12), 37, "Ø11.2 깊이 1 / Ø10 H8 (+0.022/0) 깊이 1.5, Ra 0.8 (O링 면)")
    sh.leader(X(sum(B["conn_thread"]["x"]) / 2), v.Yu(4.8), X(-12), 44, f"{B['conn_thread']['thread'].replace('x', '×')} 나사 길이 {B['conn_thread']['x'][1] - B['conn_thread']['x'][0]:g} (커넥터 자리 면에서 {B['conn_thread']['x'][1] - B['x_front']:g}) — HTX99R 체결")
    sh.leader(X(6), v.Yu(3.5), X(-12), 51, f"Ø7 관통 {B['channel']['x'][1] - B['channel']['x'][0]:g} — 센서 하네스 W-1 통로 (피드스루 없음)")
    sh.leader(X(sum(B["seal"]["groove_x"]) / 2), v.Yl(R_GRV), X(28), v.Yl(RM) + 6, f"O링 홈 Ø{O['groove_d']:g} h9 (0/-0.052), R0.2 — {ORT}")
    cb = B["cbore"]
    sh.leader(X(cb["x"][1] - 1), v.Yu(11), X(30), v.Yu(RM) - 22, f"Ø{cb['d']:g} 깊이 {cb['x'][1] - cb['x'][0]:g}")
    # 기준면 A, 거칠기, 기하공차
    sh.a(f'<rect x="{X(0) - 2.3:.2f}" y="{v.Yu(HEX_R) - 12:.2f}" width="4.6" height="5" class="thin" fill="none"/>')
    sh.text(X(0), v.Yu(HEX_R) - 8.2, "A", 3.5, "middle", bold=True)
    sh.line(X(0), v.Yu(HEX_R) - 7, X(0), v.Yu(HEX_R), "thin")
    sh.finish(X(0) - 1, v.Yu(12), "0.8")
    fx, fy = X(0) + 4, v.Yu(HEX_R) - 22
    sh.a(f'<rect x="{fx}" y="{fy}" width="30" height="6" class="thin" fill="#fff"/>')
    sh.line(fx + 7, fy, fx + 7, fy + 6, "thin")
    sh.line(fx + 21, fy, fx + 21, fy + 6, "thin")
    sh.text(fx + 3.5, fy + 4.5, "⏥", 4, "middle")
    sh.text(fx + 14, fy + 4.4, "0.02", 3.2, "middle")
    sh.text(fx + 25.5, fy + 4.4, "", 3.2, "middle")
    sh.text(fx, fy - 1.5, "씰면 평면도 / 축 직각도 0.03", 2.6)
    # 육각 끝면도
    cx, cy, R = 352, 100, HEX_R * 2.2
    pts = [(cx + R * math.cos(math.radians(30 + 60 * i)), cy + R * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    sh.poly(pts, "thick", close=True)
    sh.circle(cx, cy, R_OD * 2.2, "hidden")          # 뒤쪽 칼라 Ø32
    sh.circle(cx, cy, 2.5 * 2.2, "thick")
    sh.line(cx - R - 4, cy, cx + R + 4, cy, "center")
    sh.line(cx, cy - R - 4, cx, cy + R + 4, "center")
    af = B["hexa"]["af"] / 2 * 2.2
    sh.dim_v_ext(cx + 10, cx + R + 10, cy - af, cy + af, "AF27 (0/-0.3)")
    sh.text(cx, cy + R + 12, "화살표 방향에서 본 육각 끝면 (2.2:1)", 3.0, "middle")
    sh.text(cx, cy + R + 17, f"모따기 30° 양쪽 / 숨은선 = 칼라 Ø{B['collar']['d']:g}", 3.0, "middle")
    T = B["holder_taps"]
    for sgn in (1, -1):
        sh.circle(cx, cy + sgn * T["pcd"] / 2 * 2.2, T["d"] / 2 * 2.2, "hidden")
    sh.text(cx, cy + R + 22, f"숨은선 원 2개: 2×{T['thread']} 깊이 {T['depth']:.0f}, PCD {T['pcd']:.0f}", 3.0, "middle")
    sh.text(cx, cy + R + 27, "(Ø22 카운터보어 바닥, PCB 홀더 M-105 고정)", 3.0, "middle")
    notes = ["주기 (NOTES)",
             "1. 재질 SUS316L (1.4404), 봉재 선삭. 재질성적서 EN 10204 3.1.",
             "2. 지정 없는 모서리 C0.3, 날카로운 모서리 제거. 지정 외 표면 Ra 1.6.",
             "3. 씰면(기준면 A) Ra 0.8, 평면도 0.02, 공구 자국 반경 방향 금지 (씰 누설 방지).",
             "4. Ø7 관통 통로 양끝 C0.3·버 완전 제거 (하네스 피복 보호). Ø10 H8 Ra 0.8 (O링 밀봉면), 입구 C0.3.",
             "5. 나사 G1/2-A: ISO 228-1, 불완전 나사부는 언더컷(2)에 포함.",
             f"6. {MT} 끝 C0.5×30° (O링 도입부), {DS} f7 (-0.020/-0.041) 밀봉면 Ra 0.8, 홈 바닥·측면 Ra 1.6, 버 금지.",
             "7. 전해 연마 또는 부동태 처리 (ASTM A967). 내압 설계 정격 50 bar (200 bar형 별도 검토)."]
    for i, n in enumerate(notes):
        sh.text(18, 205 + i * 6.2, n, 3.1 if i else 3.6, bold=(i == 0))
    sh.text(18, 22, "HMT500-M-101  프로세스 바디  —  반단면 (3:1)", 5, bold=True)
    sh.frame()
    return sh


# ═════════════════════ 시트 3: 캡 / 하우징 / 엔드캡 ═════════════════════
def sheet_small():
    sh = Sheet("HMT500-M-102~104", "필터 캡 · 하우징 · 엔드캡", "표기", "SUS316L (1.4404)", "3/4")
    # ── 보호캡 = 두텍 SUS 오일 필터 390000-001100 (3.5:1, 참고도), 왼쪽 위 ──
    s = 3.5
    v = View(sh, 0, 92, s)
    v.ox = 40 - C["x_tip"] * s
    v.axis(C["x_tip"], C["x_rear"])
    draw_cap(v)
    X = v.X
    xt, xr = C["x_tip"], C["x_rear"]
    rows = sorted({x for x, _ in C["holes"]})
    y1 = v.Yl(R_CAP) + 7
    sh.dim_h(X(xt), v.Yl(R_CAP), X(rows[0]), v.Yl(1.5), y1, f"{rows[0] - xt:g}")
    sh.dim_h(X(rows[0]), v.Yl(1.5), X(rows[-1]), v.Yl(1.5), y1, f"{len(rows) - 1}×{rows[1] - rows[0]:g}={rows[-1] - rows[0]:g}")
    sh.dim_h(X(C["rear_relief"]["x"][0]), v.Yl(R_CAP), X(xr), v.Yl(5.5), y1, "1")
    sh.dim_h(X(xt), v.Yl(R_CAP), X(xr), v.Yl(5.5), y1 + 9, f"{xr - xt:g}")
    sh.dim_h(X(C["thread_x"][0]), v.Yu(5), X(xr), v.Yu(5), v.Yu(R_CAP) - 7, f"{xr - C['thread_x'][0]:g}")
    sh.dim_h(X(xt), v.Yu(R_CAP), X(C["bore_x"][0]), v.Yu(4), v.Yu(R_CAP) - 7, f"{C['bore_x'][0] - xt:g}")
    sh.dim_v(X(xr) + 9, v.Yu(R_CAP), v.Yl(R_CAP), f"Ø{C['od']:g}")
    sh.leader(X(-45 + D), v.Yu(C["bore"] / 2), X(-44 + D), v.Yu(R_CAP) - 16, f"Ø{C['bore']:g} (센서실)")
    sh.leader(X(-34 + D), v.Yu(4.6), X(-32 + D), v.Yu(R_CAP) - 16, f"{C['thread'].replace('x', '×')} 깊이 8.5 — HTX99R 위 나사")
    sh.leader(X(-30.5 + D), v.Yl(5.5), X(-24 + D), v.Yl(R_CAP) + 20, f"Ø{C['rear_relief']['d']:g}")
    sh.leader(X(xt) + 0.3, v.oy - 1, X(xt) + 4, v.Yu(R_CAP) - 16, f"Ø{C['tip_hole']:g} 끝단 구멍")
    sh.leader(X(xt + 0.5), v.Yl(5.5), X(xt) - 2, v.Yl(R_CAP) + 20, f"C{C['chamfer']:g}")
    sh.leader(X(rows[1]), v.Yl(1.5), X(-40 + D), v.Yl(R_CAP) + 26, f"{len(C['holes'])}×Ø{C['hole_d']:g} 관통 ({len(rows)}줄 × 5개, 72°)")
    sh.text(40, 30, f"HMT500-M-102  센서 보호캡 (3.5:1) — 두텍 {C['part_no']} 기반", 4.4, bold=True)
    sh.text(40, 36, f"Rev H: 원 도면(2020-06-08, 소재 Ø12×32)에서 끝 쪽 {P.CAP_EXT:g} 연장 + 옆 구멍 1줄 추가. 재질 {C['material']}, 소재 Ø12×{xr - xt:g}", 2.8, cls="muted")
    # ── 엔드캡 (2.5:1), 오른쪽 위 ──
    s = 2.5
    e0, e1 = E["mthread"]["x"][0], E["flange"]["x"][1]
    v = View(sh, 0, 95, s)
    v.ox = 305 - e0 * s
    v.axis(e0, e1)
    draw_endcap(v)
    X = v.X
    yd = v.Yl(R_OD) + 8
    em, es, ef = E["mthread"]["x"], E["seal"]["x"], E["flange"]["x"]
    sh.dim_h(X(em[0]), v.Yl(R_MT), X(em[1]), v.Yl(R_SEAL), yd, f"{em[1] - em[0]:g}")
    sh.dim_h(X(es[0]), v.Yl(R_SEAL), X(es[1]), v.Yl(R_OD), yd, f"{es[1] - es[0]:g}")
    sh.dim_h(X(ef[0]), v.Yl(R_OD), X(ef[1]), v.Yl(R_OD), yd, f"{ef[1] - ef[0]:g}")
    sh.dim_h(X(em[0]), v.Yl(R_MT), X(ef[1]), v.Yl(R_OD), yd + 9, f"{ef[1] - em[0]:g}")
    g0, g1 = E["seal"]["groove_x"]
    sh.dim_h(X(g0), v.Yu(R_GRV), X(g1), v.Yu(R_GRV), v.Yu(R_OD) - 6, f"{g1 - g0:.1f} (+0.1/0)")
    sh.dim_v_ext(X(em[0]), X(em[0]) - 9, v.Yu(R_MT), v.Yl(R_MT), f"{MTL} (왼나사)")
    sh.dim_v(X(es[1] - 0.3), v.Yu(R_SEAL), v.Yl(R_SEAL), f"{DS} f7")
    sh.dim_v(X(ef[1]) + 9, v.Yu(R_OD), v.Yl(R_OD), f"Ø{E['flange']['d']:g}")
    et, ec = E["thread"]["x"], E["cbore"]["x"]
    sh.leader(X(et[1] - 2), v.Yu(E["thread"]["d"] / 2), X(ef[1] + 7), v.Yu(R_OD) - 16, f"M16×1.5-6H 관통 (길이 {et[1] - et[0]:g})")
    sh.leader(X(ec[0] + 3), v.Yu(11), X(ef[1] + 7), v.Yu(R_OD) - 24, f"Ø{E['cbore']['d']:g} 깊이 {ec[1] - ec[0]:g}")
    Po = E["ports"]                                  # 몰딩 주입·공기 빠짐 구멍 (외형 쪽 숨은선)
    for dr in (-Po["d_minor"] / 2, Po["d_minor"] / 2):
        ri = Po["r"] + (ec[1] - ef[1]) * math.tan(math.radians(Po["tilt_deg"]))
        sh.line(X(ec[1]), v.Yl(ri + dr), X(ef[1]), v.Yl(Po["r"] + dr), "hidden")
    sh.leader(X(ef[1] - 1.5), v.Yl(Po["r"]), X(ef[1] + 7), v.Yl(R_OD) + 13, f"2×M3 깊이 4 (주기 5)")
    sh.leader(X(sum(E["seal"]["groove_x"]) / 2), v.Yl(R_GRV), X(ef[1] + 7), v.Yl(R_OD) + 26, f"O링 홈 Ø{O['groove_d']:g} h9 ({ORT})")
    sh.leader(X(sum(ef) / 2), v.Yl(E["flange"]["flats_af"] / 2), X(ef[1] + 7), v.Yl(R_OD) + 3, f"평면 {AFE} (2면)")
    sh.text(250, 30, "HMT500-M-104  엔드캡 (2.5:1)", 4.6, bold=True)
    sh.text(250, 36, "커넥터 O링 면 Ra 0.8 / 커넥터 P/N 확정 후 M16 규격 재확인", 2.8, cls="muted")
    # ── 하우징 (1.5:1), 가운데 아래 ──
    s = 1.5
    v = View(sh, 0, 200, s)
    v.ox = 200 - h0 * s
    v.axis(h0, h1)
    draw_housing(v)
    X = v.X
    sh.dim_h(X(h0), v.Yl(R_OD), X(h1), v.Yl(R_OD), v.Yl(R_OD) + 9, f"{h1 - h0:.0f}")
    sh.dim_h(X(h0), v.Yu(R_OD), X(h0 + _sl), v.Yu(R_OD), v.Yu(R_OD) - 6, f"{_sl:.0f}")
    sh.dim_h(X(h0 + _sl), v.Yu(R_OD), X(h0 + _sl + _tl), v.Yu(R_OD), v.Yu(R_OD) - 6, f"{_tl:.0f}")
    sh.dim_v(X(h1) + 9, v.Yu(R_OD), v.Yl(R_OD), f"Ø{Hs['od']:g}")
    sh.dim_v(X(45), v.Yu(Hs["id"] / 2), v.Yl(Hs["id"] / 2), f"Ø{Hs['id']:g}")
    sh.dim_v_ext(X(h0), X(h0) - 10, v.Yu(Hs["seal_bore"] / 2), v.Yl(Hs["seal_bore"] / 2), f"{DSB} H8 (+0.033/0)")
    sh.leader(X(h1 - _sl - 3), v.Yu(R_MTm), X(h1) + 18, v.Yu(R_OD) - 4, f"앞 {MTH} / 뒤 {Hs['thread_rear'].replace('x', '×')} (왼나사), 유효 {_tl:g}")
    sh.leader(X(h1 - 2), v.Yu(Hs["seal_bore"] / 2), X(h1) + 18, v.oy - 4, f"{DSB} H8 깊이 {_sl:g} (양끝), Ra 0.8")
    sh.text(190, 152, "HMT500-M-103  하우징 (1.5:1)", 4.6, bold=True)
    sh.text(190, 158, "양 끝 C0.5×15° (O링 도입부) / 외면 Ra 0.8 헤어라인 또는 비드 / 레이저 마킹 영역 45×20", 2.8, cls="muted")
    notes = ["주기 (NOTES)",
             "1. 재질 SUS316L (1.4404), 재질성적서 EN 10204 3.1, 부동태 처리 (ASTM A967).",
             "2. 지정 없는 모서리 C0.3, 버 제거. 지정 외 표면 Ra 1.6. 일반공차 ISO 2768-mK.",
             f"3. ③–① {MTH[:-3]} 오른나사, ③–④ {MTH[:-3]} 왼나사 (턴버클: ③만 돌림) + {ORT} FKM, {DSB} H8/f7. 왼나사 끝에 'LH' 각인.",
             "4. ③ 나사·밀봉 보어는 한 번 척킹으로 가공 (동축도 Ø0.05). ② 보호캡은 SUS304 (두텍 필터 기반) — 접액부 316L 통일 여부 검토.",
             f"5. ④ M3 구멍 2개 (r{E['ports']['r']:g}, 90°·270°, 축에서 안쪽 20°, Ø2.5 관통): 하우징 안 몰딩 주입·공기 빠짐. 경화 후 M3×3 무두나사 + 실런트로 막음."]
    for i, n in enumerate(notes):
        sh.text(18, 247 + i * 6.2, n, 3.0 if i else 3.6, bold=(i == 0))
    sh.frame()
    return sh


# ═════════════════════ 시트 4: PCB 외곽 / 홀더 / 지지링 ═════════════════════
def pcb_limits():
    """구간별 (x0, x1, 폭, 보어 지름, 가장자리 높이 한계, 중심 높이 한계) — 여유 0.5 포함."""
    Pc = P.PCB
    out = []
    for x0, x1, w in Pc["sections"]:
        bore = min(Hs["id"], Hs["thread_minor"]) if w > 20 else B["cbore"]["d"]
        R = bore / 2
        edge = math.sqrt(R ** 2 - (w / 2) ** 2) - Pc["t"] / 2 - 0.5
        out.append((x0, x1, w, bore, edge, R - Pc["t"] / 2 - 0.5))
    return out


def sheet_pcb():
    sh = Sheet("HMT500-M-105~106", "PCB 홀더 · 지지링 · PCB 외곽", "표기", "PEEK / PA66-GF30", "4/4")
    Pc, Hh, R = P.PCB, P.PCB_HOLDER, P.PCB_RING
    f = Pc["x"][0]
    # ── PCB 외곽 (2:1) ──
    s, X0, cy = 2.5, 40.0, 92.0
    X = lambda x: X0 + s * (x - f)          # noqa: E731
    Y = lambda y: cy - s * y                # noqa: E731
    up = []
    for x0, x1, w in Pc["sections"]:
        up += [(X(x0), Y(w / 2)), (X(x1), Y(w / 2))]
    sh.poly(up + [(x, 2 * cy - y) for x, y in reversed(up)], "thick", close=True)
    sh.line(X(f) - 5, cy, X(Pc["x"][1]) + 5, cy, "center")
    # 금지 구역: 홀더 홈 물림, 지지링 홈
    s0, s1 = Hh["slot_x"]
    w0 = Pc["sections"][0][2] / 2
    sh.a(f'<rect x="{X(s0):.3f}" y="{Y(w0):.3f}" width="{s * (s1 - s0):.3f}" height="{s * 2 * w0:.3f}" class="hatchfill2"/>')
    wm = Pc["sections"][1][2] / 2
    for sgn in (1, -1):
        y0 = wm if sgn > 0 else -R["id"] / 2
        sh.a(f'<rect x="{X(R["x"][0]):.3f}" y="{Y(y0):.3f}" width="{s * (R["x"][1] - R["x"][0]):.3f}" height="{s * (wm - R["id"] / 2):.3f}" class="hatchfill2"/>')
    for x, y in Pc["holes"]:
        sh.circle(X(x), Y(y), Pc["hole_d"] / 2 * s, "thick")
    # 패드 구역
    for (xa, xb), (ya, yb) in ((Pc["jst"]["x"], Pc["jst"]["y"]), (Pc["gh"]["x"], Pc["gh"]["y"])):
        sh.a(f'<rect x="{X(xa):.3f}" y="{Y(yb):.3f}" width="{s * (xb - xa):.3f}" height="{s * (yb - ya):.3f}" style="fill:#f3d9a4;stroke:#000;stroke-width:0.18"/>')
    # 배치 구역 (점선) + 이름
    for i, (name, parts, xa, xb) in enumerate(Pc["zones"]):
        sh.a(f'<rect x="{X(xa) + 0.6:.3f}" y="{Y(8.2):.3f}" width="{s * (xb - xa) - 1.2:.3f}" height="{s * 16.4:.3f}" class="hidden"/>')
        sh.text((X(xa) + X(xb)) / 2, Y(-11.5) + 7 if i != 1 else Y(-11.5) + 7, name, 3.0, "middle", bold=True)
    sh.text((X(Pc["jst"]["x"][0]) + X(Pc["jst"]["x"][1])) / 2, Y(0) + 1, "J3", 2.6, "middle", bold=True)
    sh.text((X(Pc["jst"]["x"][0]) + X(Pc["jst"]["x"][1])) / 2, Y(-3.5) + 3.5, "JST SH 4P", 2.2, "middle")
    sh.dim_h(X(f), Y(-3.5), X(Pc["jst"]["x"][0]), Y(-3.5), Y(-11.5) + 9, f"{Pc['jst']['x'][0] - f:g}")
    gx = (X(Pc["gh"]["x"][0]) + X(Pc["gh"]["x"][1])) / 2
    sh.text(gx, Y(0) + 1, "J1", 2.6, "middle", bold=True)
    sh.text(gx, Y(Pc["gh"]["y"][0]) + 3.5, "JST GH 8P →", 2.2, "middle")
    # 치수
    yt = Y(11.5) - 8
    xs = [Pc["sections"][0][0]] + [sec[1] for sec in Pc["sections"]]
    for xa, xb in zip(xs, xs[1:]):
        sh.dim_h(X(xa), Y(9), X(xb), Y(9), yt, f"{xb - xa:g}")
    sh.dim_h(X(xs[0]), Y(9), X(xs[-1]), Y(9), yt - 9, f"{xs[-1] - xs[0]:g}  (PCB 전장)")
    sh.dim_h(X(f), Y(0), X(s1), Y(0), Y(-11.5) + 16, f"{s1 - s0:g}")
    sh.dim_h(X(f), Y(-5), X(Pc["holes"][0][0]), Y(-5), Y(-11.5) + 23, "")
    sh.text(X(Pc["holes"][0][0]) + 6, Y(-11.5) + 24, f"{Pc['holes'][0][0] - f:g}", 3.2)
    sh.dim_h(X(f), Y(-9), X(R["x"][0]), Y(-11.5), Y(-11.5) + 30, f"{R['x'][0] - f:g}")
    sh.dim_h(X(R["x"][0]), Y(-11.5), X(R["x"][1]), Y(-11.5), Y(-11.5) + 30, f"{R['x'][1] - R['x'][0]:g}")
    sh.dim_v_ext(X(f), X(f) - 8, Y(9), Y(-9), "18")
    sh.dim_v(X(45), Y(11.5), Y(-11.5), "23")
    sh.dim_v_ext(X(Pc["x"][1]), X(Pc["x"][1]) + 8, Y(9), Y(-9), "18")
    sh.leader(X(Pc["holes"][0][0]) - 1, Y(5) - 1, X(f) + 4, Y(11.5) - 24, f"2×Ø{Pc['hole_d']}, 간격 10 (홀더 가로 나사 M2)")
    sh.text(45, 26, "HMT500-E-301  PCB 외곽 — 기구 인터페이스 (2.5:1)", 4.6, bold=True)
    sh.text(45, 32, f"4층 FR-4 t{Pc['t']}, 모서리 R{Pc['corner_r']:g}. 빗금 = 부품·동박 금지 (양면): 홀더 홈 물림, 지지링 홈. 기준 = 앞 끝(피드스루 쪽)", 2.8, cls="muted")
    # 높이 한계 표
    tx, ty = 18.0, 160.0
    hdr = ["구간 (앞 끝 기준)", "폭", "둘러싼 보어", "부품 높이 한계 (한 면, 여유 0.5 포함)"]
    cw = [42, 16, 30, 90]
    sh.a(f'<rect x="{tx}" y="{ty}" width="{sum(cw)}" height="{5.4 * 4}" class="thick" fill="#fff"/>')
    xx = tx
    for c, h_ in zip(cw, hdr):
        sh.text(xx + 1.2, ty + 3.9, h_, 2.7, bold=True)
        xx += c
        sh.line(xx, ty, xx, ty + 5.4 * 4, "thin")
    for i, (x0, x1, w, bore, edge, ctr) in enumerate(pcb_limits()):
        y = ty + 5.4 * (i + 1)
        sh.line(tx, y, tx + sum(cw), y, "thin")
        where = "바디 카운터보어" if i == 0 else ("하우징" if i == 1 else "엔드캡 카운터보어")
        vals = [f"{x0 - f:g} ~ {x1 - f:g}", f"{w:g}", f"Ø{bore:.4g} ({where})", f"가장자리 {edge:.1f} / 중심 {ctr:.1f} mm"]
        xx = tx
        for c, val in zip(cw, vals):
            sh.text(xx + 1.2, y + 3.9, val, 2.7)
            xx += c
    # ── 홀더 M-105 (3:1) — 뒤에서 본 끝면 + 측면 ──
    s3, cx, cyh = 3.0, 250.0, 90.0
    rO, rH = Hh["d"] / 2 * s3, Hh["hole_d"] / 2 * s3
    sw = Hh["slot_w"] / 2 * s3
    sh.circle(cx, cyh, rO, "thick")
    sh.circle(cx, cyh, rH, "thick")
    sh.a(f'<rect x="{cx - rO:.3f}" y="{cyh - sw:.3f}" width="{2 * rO:.3f}" height="{2 * sw:.3f}" fill="#fff" class="thick"/>')
    sh.circle(cx, cyh, rO, "thick")
    for sgn in (1, -1):
        yy = cyh + sgn * Hh["screw_pcd"] / 2 * s3
        sh.circle(cx, yy, Hh["screw_d"] / 2 * s3, "thick")
        sh.circle(cx, yy, Hh["cbore_d"] / 2 * s3, "thin")
    w = Hh["window"]                    # W-1 플러그 창 (PCB 윗면 위, 앞뒤 관통)
    sh.a(f'<rect x="{cx - w["wy"] / 2 * s3:.3f}" y="{cyh - w["z"][1] * s3:.3f}" width="{w["wy"] * s3:.3f}" '
         f'height="{(w["z"][1] - w["z"][0]) * s3:.3f}" fill="#fff" class="thick"/>')
    sh.leader(cx - w["wy"] / 2 * s3, cyh - w["z"][1] * s3 + 2, cx + 6, cyh + rO + 32,
              f"창 {w['wy']:g} × {w['z'][1] - w['z'][0]:g} 관통 (홈 위 {w['z'][0]:g}–{w['z'][1]:g}) — PCB 끼운 뒤 W-1 플러그 통과")
    for y in Hh["cross"]["y"]:          # 가로 나사 (z 방향, 슬롯에 수직) — 숨은선
        xh = cx + y * s3
        for dx in (-1, 1):
            sh.line(xh + dx * Hh["cross"]["d"] / 2 * s3, cyh - rO + 3, xh + dx * Hh["cross"]["d"] / 2 * s3, cyh + rO - 3, "hidden")
    sh.line(cx - rO - 5, cyh, cx + rO + 5, cyh, "center")
    sh.line(cx, cyh - rO - 5, cx, cyh + rO + 5, "center")
    sh.dim_v_ext(cx + rO, cx + rO + 9, cyh - rO, cyh + rO, f"Ø{Hh['d']:g} (0/-0.1)")
    sh.dim_v_ext(cx, cx - rO - 9, cyh - Hh["screw_pcd"] / 2 * s3, cyh + Hh["screw_pcd"] / 2 * s3, f"PCD {Hh['screw_pcd']:g}")
    sh.dim_h(cx - Hh["cross"]["y"][0] * s3, cyh - rO + 6, cx + Hh["cross"]["y"][0] * s3, cyh - rO + 6, cyh - rO - 6, "10")
    sh.leader(cx + 5, cyh - Hh["screw_pcd"] / 2 * s3 - 3, cx + 22, cyh - rO - 14,
              f"2×Ø{Hh['screw_d']} 관통, 카운터보어 Ø{Hh['cbore_d']:g} 깊이 {Hh['cbore_depth']:g} (M2 → 바디, 위쪽은 링 단자 함께)")
    sh.leader(cx + rO - 3, cyh + sw, cx - 6, cyh + rO + 18, f"홈 폭 {Hh['slot_w']} (+0.1/0) 깊이 {s1 - s0:g}, 전폭")
    sh.leader(cx - rH * 0.7, cyh + rH * 0.7, cx - 18, cyh + rO + 10, f"Ø{Hh['hole_d']:g} 관통 (하네스 W-1 통과)")
    sh.text(cx - 50, cyh + rO + 26, "2×M2 가로 탭 (숨은선, 홈에 수직) — PCB 관통 고정 M2×12", 2.8)
    # 측면 (홈에 수직 방향에서 봄)
    L = (Hh["x"][1] - Hh["x"][0]) * s3
    sx0 = 302.0
    sh.a(f'<rect x="{sx0:.3f}" y="{cyh - rO:.3f}" width="{L:.3f}" height="{2 * rO:.3f}" class="thick" fill="none"/>')
    xs_slot = sx0 + (Hh["slot_x"][0] - Hh["x"][0]) * s3
    sh.line(xs_slot, cyh - rO, xs_slot, cyh + rO, "hidden")
    for y in Hh["cross"]["y"]:
        sh.circle(sx0 + (Hh["cross"]["x"] - Hh["x"][0]) * s3, cyh - y * s3, Hh["cross"]["d"] * 0.8 / 2 * s3, "thick")
    for dy in (-rH, rH):
        sh.line(sx0, cyh + dy, sx0 + L, cyh + dy, "hidden")
    sh.line(sx0 - 4, cyh, sx0 + L + 4, cyh, "center")
    sh.dim_h(sx0, cyh + rO, sx0 + L, cyh + rO, cyh + rO + 8, f"{Hh['x'][1] - Hh['x'][0]:g}", above=False)
    sh.dim_h(xs_slot, cyh - rO, sx0 + L, cyh - rO, cyh - rO - 6, f"{s1 - s0:g}")
    sh.text(sx0, cyh + rO + 5, "← 앞(바디 쪽)", 2.6, cls="muted")
    sh.text(215, 26, "HMT500-M-105  PCB 홀더 (3:1)", 4.6, bold=True)
    sh.text(215, 32, "왼쪽: 뒤(PCB 쪽)에서 본 끝면 / 오른쪽: 측면", 2.8, cls="muted")
    # ── 지지링 M-106 (3:1) ──
    s3 = 2.0
    cx2, cy2 = 370.0, 200.0
    ro, ri = R["od"] / 2 * s3, R["id"] / 2 * s3
    sh.circle(cx2, cy2, ro, "thick")
    sh.circle(cx2, cy2, ri, "thick")
    ns = R["slot_w"] / 2 * s3
    for sgn in (1, -1):
        x_in = cx2 + sgn * math.sqrt(ri ** 2 - ns ** 2)
        x_out = cx2 + sgn * R["slot_y"] * s3
        sh.a(f'<rect x="{min(x_in, x_out):.3f}" y="{cy2 - ns:.3f}" width="{abs(x_out - x_in):.3f}" height="{2 * ns:.3f}" fill="#fff" class="thick"/>')
    sh.line(cx2 - ro - 5, cy2, cx2 + ro + 5, cy2, "center")
    sh.line(cx2, cy2 - ro - 5, cx2, cy2 + ro + 5, "center")
    sh.dim_v_ext(cx2 + ro, cx2 + ro + 9, cy2 - ro, cy2 + ro, f"Ø{R['od']:g} (0/-0.1)")
    sh.dim_v(cx2 - 8, cy2 - ri, cy2 + ri, f"Ø{R['id']:g}")
    sh.dim_h(cx2 - R["slot_y"] * s3, cy2 + 2, cx2 + R["slot_y"] * s3, cy2 + 2, cy2 + ro + 8, f"{2 * R['slot_y']:g} (+0.2/0)  홈 바닥 사이", above=False)
    sh.leader(cx2 - R["slot_y"] * s3 + 1, cy2 + ns, cx2 - 34, cy2 + 10, f"홈 폭 {R['slot_w']} (+0.1/0) 2곳")
    sh.text(275, 160, f"HMT500-M-106  PCB 지지링 (2:1), 두께 {R['x'][1] - R['x'][0]:g}", 4.6, bold=True)
    sh.text(275, 166, "하우징 안에서 PCB 뒤쪽을 받침. 엔드캡과 연결 안 함 (체결 회전 전달 없음)", 2.8, cls="muted")
    notes = ["주기 (NOTES)",
             "1. M-105/106 재질 PEEK (연속 사용 ≥ 150 °C) 또는 PA66-GF30. 양산은 사출 검토.",
             "2. PCB는 ⑫ 홀더에만 고정. ⑬ 링은 흔들림 방지(축 방향 자유) — 열팽창 흡수.",
             f"3. J3 = {Pc['jst']['part']}, 높이 {Pc['jst']['h']:g}, 홀더 뒤 12.5 (꽂을 공간). W-1({P.HARNESS['length']:g} mm)로 HTX99R와 연결. 조립 후 하우징 안 전체 몰딩.",
             f"4. J1 = {Pc['gh']['part']}, 입구 뒤쪽(+x). 하네스 W-2({P.HARNESS2['length']:g} mm)로 M12 8P. J5 = 샤시 선 납땜 구멍 (→ 홀더 위 축 나사 링 단자).",
             f"   PCB 폭 23 구간은 x {Pc['sections'][1][1]:g}에서 끝 (턴버클 끝 엔드캡 앞면 x {E['mthread']['x'][0]:g}와 틈 {E['mthread']['x'][0] - Pc['sections'][1][1]:.1f}). "
             f"링 뒤(x ≥ {R['x'][0]:g}) 부품은 Ø{R['id']:g} 안 (링을 뒤에서 끼움).",
             "5. PCB 외곽·구역은 KiCad hardware/kicad/HMT500(ED260313A)/HMT500(ED260313A).kicad_pcb 와 같음."]
    for i, n in enumerate(notes):
        sh.text(18, 196 + i * 6.0, n, 2.9 if i else 3.6, bold=(i == 0))
    sh.frame()
    return sh


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("HMT500-M-000_assembly", sheet_assembly), ("HMT500-M-101_body", sheet_body),
                     ("HMT500-M-102-104_parts", sheet_small), ("HMT500-M-105-106_pcb", sheet_pcb)):
        open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8").write(fn().svg())
        print(name)


if __name__ == "__main__":
    main()
