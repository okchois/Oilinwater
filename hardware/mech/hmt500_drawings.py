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
        self.text(x0 + w - 3, y0 + 7, "HMT500 오일 수분 트랜스미터", 3.4, "end")
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
B, C, E, Hs = P.BODY, P.CAP, P.ENDCAP, P.HOUSING
HEX_R = P.hex_corner_d(B["hexa"]["af"]) / 2
BODY_OUT = [(*B["spigot"]["x"], 5.0), (*B["tube"]["x"], 6.0), (*B["gthread"]["x"], B["gthread"]["d"] / 2),
            (*B["relief"]["x"], B["relief"]["d"] / 2), (*B["hexa"]["x"], HEX_R), (*B["collar"]["x"], 15.0),
            (*B["wspigot"]["x"], 13.5)]
BODY_IN = [(*B["seat"]["x"], 4.0), (*B["wire"]["x"], 2.5), (*B["cbore"]["x"], 11.0)]
CAP_OUT = [(C["x_tip"], C["x_rear"], 6.0)]
CAP_IN = [(C["x_tip"], C["x_tip"] + C["tip_wall"], C["tip_hole"] / 2),
          (C["x_tip"] + C["tip_wall"], C["x_rear"] - C["thread_len"], C["bore"] / 2),
          (C["x_rear"] - C["thread_len"], C["x_rear"], 4.6)]      # M10x0.75 내경 약 Ø9.19
HOUS_OUT = [(*Hs["x"], 15.0)]
HOUS_IN = [(*Hs["x"], 13.5)]
END_OUT = [(*E["spigot"]["x"], 13.5), (*E["flange"]["x"], 15.0)]
END_IN = [(E["spigot"]["x"][0], E["flange"]["x"][1], E["thread"]["d_minor"] / 2)]


def draw_body(v, detail=True):
    v.section(BODY_OUT, BODY_IN)
    v.exterior(BODY_OUT)
    sh = v.sh
    # 외형: 육각 면 선, 나사 골지름(가는 선)
    x0, x1 = B["hexa"]["x"]
    sh.line(v.X(x0), v.Yl(HEX_R / 2), v.X(x1), v.Yl(HEX_R / 2))
    g0, g1 = B["gthread"]["x"]
    sh.line(v.X(g0), v.Yl(B["gthread"]["d_minor"] / 2), v.X(g1), v.Yl(B["gthread"]["d_minor"] / 2), "thin")
    sh.line(v.X(g0), v.Yu(B["gthread"]["d_minor"] / 2), v.X(g1), v.Yu(B["gthread"]["d_minor"] / 2), "thin")
    s0, s1 = B["spigot"]["x"]
    sh.line(v.X(s0), v.Yl(4.6), v.X(s1), v.Yl(4.6), "thin")
    sh.line(v.X(s0), v.Yu(4.6), v.X(s1), v.Yu(4.6), "thin")
    # 내부 외형(아래 반): 숨은선
    for x0_, x1_, r in BODY_IN:
        sh.line(v.X(x0_), v.Yl(r), v.X(x1_), v.Yl(r), "hidden")


def draw_cap(v):
    v.section(CAP_OUT, CAP_IN, "hatchfill2")
    v.exterior(CAP_OUT)
    sh = v.sh
    x0, x1 = C["x_rear"] - C["thread_len"], C["x_rear"]
    sh.line(v.X(x0), v.Yu(5.0), v.X(x1), v.Yu(5.0), "thin")      # 암나사 바깥지름(가는 선)
    for x, ang in C["holes"]:
        hr = C["hole_d"] / 2 * v.s
        if ang in (0, 180):          # 외형 반쪽에서 원으로 보이는 구멍 (정면)
            sh.circle(v.X(x), v.oy + (v.s * 3.0 if ang == 180 else -v.s * 3.0) if False else v.Yl(0) + v.s * 0.0, 0, "thin")
        if ang == 90:
            sh.circle(v.X(x), v.Yl(0) + 0.0, hr, "thin")
        if ang in (0, 180):
            # 단면 쪽(위): 벽을 관통하는 구멍 → 벽 해칭 끊김 표시
            sh.a(f'<rect x="{v.X(x) - hr:.3f}" y="{v.Yu(6.0):.3f}" width="{2 * hr:.3f}" height="{v.s * (6.0 - C["bore"] / 2):.3f}" fill="#fff" class="thin"/>')


def draw_housing(v):
    v.section(HOUS_OUT, HOUS_IN, "hatchfill2")
    v.exterior(HOUS_OUT)


def draw_endcap(v):
    v.section(END_OUT, END_IN)
    v.exterior(END_OUT)
    x0, x1 = E["spigot"]["x"][0], E["flange"]["x"][1]
    v.sh.line(v.X(x0), v.Yu(8.0), v.X(x1), v.Yu(8.0), "thin")
    v.sh.line(v.X(x0), v.Yl(E["thread"]["d_minor"] / 2), v.X(x1), v.Yl(E["thread"]["d_minor"] / 2), "hidden")


def buy_rect(v, x0, x1, r0, r1, cls="buy", lower=True):
    sh = v.sh
    sh.a(f'<rect x="{v.X(x0):.3f}" y="{v.Yu(r1):.3f}" width="{v.s * (x1 - x0):.3f}" height="{v.s * (r1 - r0):.3f}" class="{cls}"/>')
    if lower:
        sh.a(f'<rect x="{v.X(x0):.3f}" y="{v.Yl(r0):.3f}" width="{v.s * (x1 - x0):.3f}" height="{v.s * (r1 - r0):.3f}" class="{cls}"/>')


# ═════════════════════ 시트 1: 조립도 ═════════════════════
def sheet_assembly():
    sh = Sheet("HMT500-M-000", "HMT500 조립도 (Assembly)", "2 : 1", "부품표 참조", "1/3")
    s = 2.0
    v = View(sh, 150, 100, s)
    v.axis(P.TIP_X, P.END_X)
    # 구매품/내부 (먼저)
    Sd, Hd, Cr, Pc, Cn = P.SEAL, P.HEADER, P.CARRIER, P.PCB, P.CONNECTOR
    buy_rect(v, *Sd["x"], Sd["id"] / 2, Sd["od"] / 2, "green")
    buy_rect(v, *Hd["x"], 0, Hd["d"] / 2, "buy")
    for x in Pc["x"]:
        buy_rect(v, x, x + Pc["t"], 0, Pc["d"] / 2, "green")
    sh.a(f'<rect x="{v.X(Cr["x"][0]):.3f}" y="{v.Yu(Cr["t"] / 2 + 0.6):.3f}" width="{s * (Cr["x"][1] - Cr["x"][0]):.3f}" height="{s * (Cr["t"] + 1.2):.3f}" class="buy"/>')
    for yy in (1.2, -1.2):
        sh.line(v.X(Hd["pin_front"]), v.oy - s * yy, v.X(Hd["x"][0]), v.oy - s * yy, "thin")
        sh.line(v.X(Hd["x"][1]), v.oy - s * yy, v.X(Hd["pin_rear"]), v.oy - s * yy, "thin")
    buy_rect(v, *Cn["body"]["x"], 0, Cn["body"]["d"] / 2)
    buy_rect(v, *Cn["thread"]["x"], 0, Cn["thread"]["d"] / 2)
    buy_rect(v, P.ENDCAP["spigot"]["x"][0] + 1, P.ENDCAP["flange"]["x"][1], 0, 7.95)
    # 가공품
    draw_body(v)
    draw_cap(v)
    draw_housing(v)
    draw_endcap(v)
    # 용접 표시
    for x in (Hs["x"][0], Hs["x"][1]):
        sh.a(f'<path d="M{v.X(x) - 1.5:.2f},{v.Yu(15) - 0.2:.2f} l1.5,-2 l1.5,2" class="thick" fill="#000"/>')
    # 풍선
    bl = [("2", v.X(-40), v.Yu(6), v.X(-40), 46), ("6", v.X(-38), v.oy, v.X(-30), 58),
          ("5", v.X(-29.5), v.Yu(3.5), v.X(-20), 46), ("7", v.X(-1), v.Yu(13.5), v.X(-6), 58),
          ("1", v.X(6), v.Yu(HEX_R), v.X(8), 46), ("8", v.X(49), v.Yu(10), v.X(40), 58),
          ("3", v.X(60), v.Yu(15), v.X(60), 46), ("4", v.X(77), v.Yu(15), v.X(77), 58),
          ("9", v.X(90), v.Yu(6), v.X(92), 46)]
    for n, x, y, bx, by in bl:
        sh.balloon(x, y, bx, by, n)
    # 치수 (아래쪽)
    yb = v.Yl(15.6)
    sh.dim_h(v.X(P.TIP_X), v.Yl(6), v.X(P.END_X), v.Yl(6), yb + 30, f"{P.OVERALL:.0f}")
    sh.dim_h(v.X(P.TIP_X), v.Yl(6), v.X(-14), v.Yl(6), yb + 10, "34  (노출 프로브)")
    sh.dim_h(v.X(-14), v.Yl(10.5), v.X(0), v.Yl(HEX_R), yb + 10, "14")
    sh.dim_h(v.X(0), v.Yl(HEX_R), v.X(P.ENDCAP["flange"]["x"][1]), v.Yl(15), yb + 20, "79")
    sh.dim_h(v.X(0), v.Yl(HEX_R), v.X(P.END_X), v.Yl(6), yb + 10, "94")
    sh.dim_v_ext(v.X(70), v.X(70), v.Yu(15), v.Yl(15), "Ø30")
    sh.dim_v_ext(v.X(-20), v.X(-20), v.Yu(6), v.Yl(6), "Ø12")
    sh.leader(v.X(-8), v.Yl(10.5), v.X(-24), v.Yl(10.5) + 14, "G1/2-A (ISO 228-1)")
    sh.leader(v.X(4), v.Yl(HEX_R), v.X(16), v.Yl(HEX_R) + 12, "육각 AF27")
    sh.text(v.X(0) - 1, v.Yl(15.6) + 5, "A", 3.5, "middle", bold=True)
    sh.a(f'<rect x="{v.X(0) - 3:.2f}" y="{v.Yl(15.6) + 1.2:.2f}" width="4.6" height="5" class="thin" fill="none"/>')
    sh.text(v.X(0) + 3, v.Yl(15.6) + 5, "기준면 A = 씰면", 2.8)
    # 부품표
    tx, ty = W - 190, 180
    cols = [(0, 9, "No"), (9, 30, "도번"), (39, 45, "품명"), (84, 36, "재질"), (120, 8, "수량"), (128, 52, "비고")]
    rh = 5.4
    sh.a(f'<rect x="{tx}" y="{ty}" width="180" height="{rh * (len(P.PARTS) + 1)}" class="thick" fill="#fff"/>')
    for c0, cw, lab in cols:
        sh.text(tx + c0 + 1, ty + 3.9, lab, 2.8, bold=True)
        if c0:
            sh.line(tx + c0, ty, tx + c0, ty + rh * (len(P.PARTS) + 1), "thin")
    for i, row in enumerate(P.PARTS):
        y = ty + rh * (i + 1)
        sh.line(tx, y, tx + 180, y, "thin")
        for (c0, cw, _), val in zip(cols, row):
            sh.text(tx + c0 + 1, y + 3.9, str(val), 2.5 if len(str(val)) > 18 else 2.8)
    # 주기
    notes = [
        "주기 (NOTES)",
        "1. ⑤ 피드스루는 ① 앞면에 전둘레 레이저 용접. 용접 후 헬륨 리크 ≤ 1×10⁻⁸ mbar·l/s (협력사 사양 확인).",
        "2. ①–③, ③–④ 전둘레 레이저 용접(양산). 시제품은 나사+O링 결합 가능 (분해용).",
        "3. 내압 시험: 정격 50 bar → 75 bar 유지, 누설 없음. (200 bar형: 300 bar)",
        "4. ② 보호캡 체결 시 나사 고정제 사용, 토크 TBD. G1/2 설치 토크는 본디드 씰 규격에 따름.",
        "5. 보호 등급 IP67 (커넥터 체결 상태). 접액부 재질 1.4404, 재질성적서 EN 10204 3.1.",
        "6. ③ 외면 레이저 마킹: 모델명, 출력, 전원, 핀맵, 시리얼 (문안 별도).",
        "7. 나사는 도면 표시만(회전체 모델). 규격 치수는 부품도(HMT500-M-101~104) 따름.",
    ]
    for i, n in enumerate(notes):
        sh.text(18, 196 + i * 6.2, n, 3.0 if i else 3.6, bold=(i == 0))
    sh.text(18, 22, "HMT500 조립도  —  반단면 (위: 단면, 아래: 외형)", 5, bold=True)
    sh.text(18, 29, "오일 측(프로브)  ←                                                                                 →  하우징·커넥터", 3.0, cls="muted")
    sh.frame()
    return sh


# ═════════════════════ 시트 2: 바디 부품도 ═════════════════════
def sheet_body():
    sh = Sheet("HMT500-M-101", "프로세스 바디 (Process body)", "3 : 1", "SUS316L (1.4404)", "2/3")
    s = 3.0
    v = View(sh, 150, 120, s)
    v.axis(-32, 20)
    draw_body(v)
    X = v.X
    # 길이 치수 (아래 사슬)
    y1 = v.Yl(HEX_R) + 12
    chain = [(-32, -26, 5.0, 6.0, "6"), (-26, -14, 6.0, 10.5, "12"), (-14, 0, 10.5, HEX_R, "14"),
             (0, 12, HEX_R, HEX_R, "12"), (12, 15, 15, 15, "3"), (15, 20, 15, 13.5, "5")]
    for xa, xb, ra, rb, t in chain:
        sh.dim_h(X(xa), v.Yl(ra), X(xb), v.Yl(rb), y1, t)
    sh.dim_h(X(-32), v.Yl(5), X(20), v.Yl(13.5), y1 + 11, "52")
    sh.dim_h(X(-2), v.Yl(9.2), X(0), v.Yl(HEX_R), v.Yl(HEX_R) + 5, "2", above=True)
    # 내부 치수 (위)
    yt = v.Yu(HEX_R) - 10
    sh.dim_h(X(-32), v.Yu(4), X(-27), v.Yu(4), yt, "5")
    sh.dim_h(X(12), v.Yu(11), X(20), v.Yu(11), yt, "8")
    # 지름
    for x, r, t in ((-29, 5.0, "M10×0.75-6g"), (-20, 6.0, "Ø12"), (-1, 9.2, "Ø18.4"), (13.5, 15.0, "Ø30"),
                    (17.5, 13.5, "Ø27 h7 (0/-0.021)")):
        sh.dim_v(X(x), v.Yu(r), v.Yl(r), t)
    sh.leader(X(-30.5), v.Yu(4.0), X(-27), v.Yu(HEX_R) - 34, "Ø8 H7 (+0.015/0) 깊이 5 — 피드스루 안착")
    sh.leader(X(-5), v.Yu(2.5), X(-12), v.Yu(HEX_R) - 18, "Ø5 관통")
    sh.leader(X(18), v.Yu(11), X(30), v.Yu(HEX_R) - 20, "Ø22 깊이 8")
    sh.leader(X(-8), v.Yl(10.48), X(-20), v.Yl(HEX_R) + 30, "G1/2-A  ISO 228-1  (유효 나사 12)")
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
    cx, cy, R = 330, 95, HEX_R * 2.2
    pts = [(cx + R * math.cos(math.radians(30 + 60 * i)), cy + R * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    sh.poly(pts, "thick", close=True)
    sh.circle(cx, cy, 15 * 2.2 - 0.1, "thin")
    sh.circle(cx, cy, 2.5 * 2.2, "thick")
    sh.line(cx - R - 4, cy, cx + R + 4, cy, "center")
    sh.line(cx, cy - R - 4, cx, cy + R + 4, "center")
    af = B["hexa"]["af"] / 2 * 2.2
    sh.dim_v_ext(cx + 10, cx + R + 10, cy - af, cy + af, "AF27 (0/-0.3)")
    sh.text(cx, cy + R + 12, "화살표 방향에서 본 육각 끝면 (2.2:1)", 3.0, "middle")
    sh.text(cx, cy + R + 17, "모따기 30° 양쪽", 3.0, "middle")
    notes = ["주기 (NOTES)",
             "1. 재질 SUS316L (1.4404), 봉재 선삭. 재질성적서 EN 10204 3.1.",
             "2. 지정 없는 모서리 C0.3, 날카로운 모서리 제거. 지정 외 표면 Ra 1.6.",
             "3. 씰면(기준면 A) Ra 0.8, 평면도 0.02, 공구 자국 반경 방향 금지 (씰 누설 방지).",
             "4. Ø8 H7 안착부에 피드스루 레이저 용접: 용접 전 세척(오일·이물 제거).",
             "5. 나사 G1/2-A: ISO 228-1, 불완전 나사부는 언더컷(2)에 포함.",
             "6. 전해 연마 또는 부동태 처리 (ASTM A967).",
             "7. 내압 설계: 정격 50 bar (200 bar형 동일 형상 검토 — 피드스루 사양에 따름)."]
    for i, n in enumerate(notes):
        sh.text(18, 205 + i * 6.2, n, 3.1 if i else 3.6, bold=(i == 0))
    sh.text(18, 22, "HMT500-M-101  프로세스 바디  —  반단면 (3:1)", 5, bold=True)
    sh.frame()
    return sh


# ═════════════════════ 시트 3: 캡 / 하우징 / 엔드캡 ═════════════════════
def sheet_small():
    sh = Sheet("HMT500-M-102~104", "보호캡 · 하우징 · 엔드캡", "표기", "SUS316L (1.4404)", "3/3")
    # ── 보호캡 (4:1), 왼쪽 위 ──
    s = 4.0
    v = View(sh, 0, 92, s)
    v.ox = 45 - C["x_tip"] * s
    v.axis(C["x_tip"], C["x_rear"])
    draw_cap(v)
    X = v.X
    y1 = v.Yl(6) + 8
    sh.dim_h(X(C["x_tip"]), v.Yl(6), X(C["x_tip"] + C["tip_wall"]), v.Yl(1.5), y1, "1.2")
    for k, (x, _) in enumerate(C["holes"][::2]):
        sh.dim_h(X(C["x_tip"]), v.Yl(6), X(x), v.Yl(0.5), y1 + 7 * (k + 1), f"{x - C['x_tip']:.1f}")
    sh.dim_h(X(C["x_tip"]), v.Yl(6), X(C["x_rear"]), v.Yl(6), y1 + 35, "22")
    sh.dim_h(X(C["x_rear"] - C["thread_len"]), v.Yu(5), X(C["x_rear"]), v.Yu(5), v.Yu(6) - 7, "6")
    sh.dim_v(X(C["x_rear"]) + 8, v.Yu(6), v.Yl(6), "Ø12")
    sh.leader(X(-35), v.Yu(4.5), X(-33), v.Yu(6) - 18, "Ø9 (센서실)")
    sh.leader(X(-28), v.Yu(4.8), X(-22), v.Yu(6) - 10, "M10×0.75-6H 깊이 6")
    sh.leader(X(C["x_tip"]) + 0.3, v.oy - 1, X(C["x_tip"]) + 6, v.Yu(6) - 18, "Ø3 끝단 구멍")
    sh.leader(X(-41), v.Yl(1.3), X(-20), v.Yl(6) + 14, "8×Ø2.6 관통")
    sh.text(X(-20) + 1, v.Yl(6) + 18, "줄마다 180° 2개, 이웃 줄 90° 엇갈림", 2.8)
    sh.text(45, 30, "HMT500-M-102  보호캡 (4:1)", 4.6, bold=True)
    sh.text(45, 36, "유속 < 1 m/s: 본 도면 / > 1 m/s: Ø1.8 구멍 + 소결 필터 삽입형 (별도 도면)", 2.8, cls="muted")
    # ── 엔드캡 (2.5:1), 오른쪽 위 ──
    s = 2.5
    v = View(sh, 0, 90, s)
    v.ox = 300 - E["spigot"]["x"][0] * s
    v.axis(E["spigot"]["x"][0], E["flange"]["x"][1])
    draw_endcap(v)
    X = v.X
    sh.dim_h(X(70), v.Yl(13.5), X(75), v.Yl(15), v.Yl(15) + 8, "5")
    sh.dim_h(X(75), v.Yl(15), X(79), v.Yl(15), v.Yl(15) + 8, "4")
    sh.dim_h(X(70), v.Yl(13.5), X(79), v.Yl(15), v.Yl(15) + 16, "9")
    sh.dim_v_ext(X(70), X(70) - 10, v.Yu(13.5), v.Yl(13.5), "Ø27 h7 (0/-0.021)")
    sh.dim_v(X(79) + 10, v.Yu(15), v.Yl(15), "Ø30")
    sh.leader(X(77), v.Yu(7.5), X(86), v.Yu(15) - 10, "M16×1.5-6H 관통")
    sh.text(285, 30, "HMT500-M-104  엔드캡 (2.5:1)", 4.6, bold=True)
    sh.text(285, 36, "커넥터 O링 면 Ra 0.8 / 커넥터 P/N 확정 후 나사 규격 재확인", 2.8, cls="muted")
    # ── 하우징 (2:1), 가운데 아래 ──
    s = 1.5
    v = View(sh, 0, 206, s)
    v.ox = 60 - Hs["x"][0] * s
    v.axis(*Hs["x"])
    draw_housing(v)
    X = v.X
    sh.dim_h(X(Hs["x"][0]), v.Yl(15), X(Hs["x"][1]), v.Yl(15), v.Yl(15) + 9, "60")
    sh.dim_v(X(Hs["x"][1]) + 9, v.Yu(15), v.Yl(15), "Ø30")
    sh.dim_v_ext(X(Hs["x"][0]), X(Hs["x"][0]) - 10, v.Yu(13.5), v.Yl(13.5), "Ø27 H7 (+0.021/0)")
    sh.text(60, 170, "HMT500-M-103  하우징 (1.5:1)", 4.6, bold=True)
    sh.text(60, 176, "양 끝 C0.3 / 외면 Ra 0.8 헤어라인 또는 비드 / 레이저 마킹 영역 45×20 (문안 별도)", 2.8, cls="muted")
    notes = ["주기 (NOTES)",
             "1. 재질 SUS316L (1.4404), 재질성적서 EN 10204 3.1, 부동태 처리 (ASTM A967).",
             "2. 지정 없는 모서리 C0.3, 버 제거. 지정 외 표면 Ra 1.6. 일반공차 ISO 2768-mK.",
             "3. ③–① (Ø27 H7/h7), ③–④ 끼워맞춤 후 전둘레 레이저 용접 (시제품: 나사+O링 대안).",
             "4. ② 보호캡 구멍 가공 후 내부 버 완전 제거 (센서 손상 방지)."]
    for i, n in enumerate(notes):
        sh.text(18, 247 + i * 6.2, n, 3.0 if i else 3.6, bold=(i == 0))
    sh.frame()
    return sh


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("HMT500-M-000_assembly", sheet_assembly), ("HMT500-M-101_body", sheet_body),
                     ("HMT500-M-102-104_parts", sheet_small)):
        open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8").write(fn().svg())
        print(name)


if __name__ == "__main__":
    main()
