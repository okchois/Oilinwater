"""HTX99R 센서 프로브용 센서 커넥터 — 2D 도면 (STEP → 은선 처리 투영 → A3 SVG/PDF).

  python hardware/mech/htx99r_connector_drawing.py
    입력: hardware/mech/ref/HTX99R_Sensor_Probe_Sensor_Connector.STEP (두텍 SolidWorks 모델)
    출력: hardware/mech/out/HTX99R-SC_sensor_connector.svg / .pdf

뷰는 3D 모델에서 은선 처리(HLR)로 투영한다. 치수는 모델에서 읽은 형상값(아래 FEAT)이며,
스크립트가 시작할 때 모델과 대조해 어긋나면 멈춘다.
좌표: 모델 y축 = 커넥터 축 (y=0 아랫면·PCB 쪽, y=15 윗면·센서 소켓 쪽).
"""

import math
import os
import subprocess
import sys

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hmt500_params as P  # noqa: E402

P.DRAWING_REV, P.DATE = "A", "2026-09-29"
import hmt500_drawings as D  # noqa: E402

STEP = os.path.join(HERE, "ref", "HTX99R_Sensor_Probe_Sensor_Connector.STEP")
OUT = os.path.join(HERE, "out")
NAME = "HTX99R-SC_sensor_connector"

# 모델에서 읽은 형상 (mm) — check_model()이 STEP과 대조
FEAT = dict(
    body_d=10.0, len=15.0, flange_d=11.0, flange_y=(7.0, 8.0),
    groove1=dict(d=8.2, y=(5.5, 7.0)), groove2=dict(d=8.1, y=(8.0, 9.5)),
    cham=0.5, flats_af=7.0, flats_y=(12.0, 15.0),
    sock_d=1.5, sock_bottom=7.1, sock_cs=0.2, pitch=2.54,
    recess_d=7.0, recess_depth=7.0,
    pin_sq=0.64, pin_y=(-3.0, 7.0), pin_tip=0.2,
    thread="M10×0.75", thread_lower=(0.5, 5.5), thread_upper=(9.5, 15.0), thread_minor=9.188,
)


def load():
    return cq.importers.importStep(STEP).val()


def check_model(s):
    bb = s.BoundingBox()
    assert abs(bb.ymin - FEAT["pin_y"][0]) < 1e-3 and abs(bb.ymax - FEAT["len"]) < 1e-3, (bb.ymin, bb.ymax)
    assert abs(bb.xmax - FEAT["flange_d"] / 2) < 1e-3
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    dia = set()
    for f in cq.Workplane().add(s).faces().vals():
        if f.geomType() == "CYLINDER":
            dia.add(round(BRepAdaptor_Surface(f.wrapped).Cylinder().Radius() * 2, 3))
    need = {FEAT["body_d"], FEAT["flange_d"], FEAT["groove1"]["d"], FEAT["groove2"]["d"], FEAT["sock_d"],
            FEAT["recess_d"]}
    assert need <= dia, (need, dia)


# ─────────────── 은선 처리 투영 ───────────────
def _polylines(compound, defl=0.004):
    out = []
    if compound is None or compound.IsNull():
        return out
    ex = TopExp_Explorer(compound, TopAbs_EDGE)
    while ex.More():
        e = TopoDS.Edge_s(ex.Current())
        c = BRepAdaptor_Curve(e)
        d = GCPnts_QuasiUniformDeflection(c, defl)
        if d.IsDone() and d.NbPoints() > 1:
            out.append([(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)])
        ex.Next()
    return out


def hlr(shape, vdir, xdir):
    a = HLRBRep_Algo()
    a.Add(shape.wrapped)
    a.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*vdir), gp_Dir(*xdir))))
    a.Update()
    a.Hide()
    h = HLRBRep_HLRToShape(a)
    vis = _polylines(h.VCompound()) + _polylines(h.OutLineVCompound()) + _polylines(h.Rg1LineVCompound())
    hid = _polylines(h.HCompound()) + _polylines(h.OutLineHCompound())
    return vis, hid


def section_face(shape, z0):
    """평면 z=z0 단면 → 외곽·구멍 폴리라인 목록 (x, y). 와이어 탐색기로 선분 순서를 맞춘다."""
    from OCP.BRepTools import BRepTools_WireExplorer
    plate = cq.Workplane("XY").box(40, 40, 0.002).translate((0, 6, z0)).val()
    com = shape.intersect(plate)
    loops = []
    for f in cq.Workplane().add(com).faces().vals():
        if f.normalAt().z < 0.99:
            continue
        for w in [f.outerWire()] + f.innerWires():
            pts = []
            we = BRepTools_WireExplorer(w.wrapped, f.wrapped)
            while we.More():
                e = we.Current()
                c = BRepAdaptor_Curve(e)
                d = GCPnts_QuasiUniformDeflection(c, 0.003)
                seg = [(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)]
                if we.Orientation() == 1:          # TopAbs_REVERSED
                    seg = seg[::-1]
                pts += seg
                we.Next()
            loops.append(pts)
    return loops


# ─────────────── 도면 ───────────────
class V:
    """모델 2D 좌표 → 도면 좌표 (배율 s, 원점 ox, oy; 모델 y 위쪽이 도면 위쪽)."""

    def __init__(self, sh, ox, oy, s):
        self.sh, self.ox, self.oy, self.s = sh, ox, oy, s

    def P(self, x, y):
        return self.ox + self.s * x, self.oy - self.s * y

    def draw(self, vis, hid):
        for pl in hid:
            self.sh.poly([self.P(*p) for p in pl], "hidden")
        for pl in vis:
            self.sh.poly([self.P(*p) for p in pl], "thick")

    def center_v(self, y0, y1, x=0.0):
        a, b = self.P(x, y0 - 1.2), self.P(x, y1 + 1.2)
        self.sh.line(*a, *b, "center")

    def center_h(self, x0, x1, y=0.0):
        a, b = self.P(x0 - 1.2, y), self.P(x1 + 1.2, y)
        self.sh.line(*a, *b, "center")


def dim_y(sh, v, x_feat, x_dim, y0, y1, txt):
    """축 방향(세로) 길이 치수: 모델 y0..y1, 치수선은 도면 x=x_dim."""
    (xa, ya), (_, yb) = v.P(x_feat, y0), v.P(x_feat, y1)
    for yy in (ya, yb):
        sh.line(xa + (1 if x_dim > xa else -1), yy, x_dim + (1.5 if x_dim > xa else -1.5), yy, "thin")
    sh.line(x_dim, ya, x_dim, yb, "thin")
    big = abs(yb - ya) > 7
    sh.arrow(x_dim, min(ya, yb), -90 if big else 90)
    sh.arrow(x_dim, max(ya, yb), 90 if big else -90)
    sh.text(x_dim - 1.0, (ya + yb) / 2, txt, 3.0, "middle", rot=-90)


def dim_x(sh, v, x0, x1, y_feat0, y_feat1, y_dim, txt):
    (xa, ya), (xb, yb) = v.P(x0, y_feat0), v.P(x1, y_feat1)
    sh.dim_h(xa, ya, xb, yb, y_dim, txt)


def main():
    s = load()
    check_model(s)
    F = FEAT
    sh = D.Sheet("HTX99R-SC", "센서 커넥터 (HTX99R 센서 프로브)", "5 : 1", "STEP에 재질 정보 없음 (확인)", "1/1")
    sc = 5.0

    # ── 정면도 (z 방향에서 봄) ──
    vf = V(sh, 95, 125, sc)
    vis, hid = hlr(s, (0, 0, 1), (1, 0, 0))
    vf.draw(vis, hid)
    vf.center_v(F["pin_y"][0], F["len"])
    sh.text(vf.P(0, 0)[0], 28, "정면도", 4.0, "middle", bold=True)

    # 정면도 치수 — 왼쪽: 축 방향 사슬, 오른쪽: 전장
    R = F["body_d"] / 2
    xl = vf.P(-F["flange_d"] / 2, 0)[0] - 8
    dim_y(sh, vf, -R, xl, F["pin_y"][0], 0, "3")
    dim_y(sh, vf, -R, xl, 0, F["groove1"]["y"][0], "5.5")
    dim_y(sh, vf, -R, xl, F["groove1"]["y"][0], F["flange_y"][0], "1.5")
    dim_y(sh, vf, -F["flange_d"] / 2, xl, F["flange_y"][0], F["flange_y"][1], "1")
    dim_y(sh, vf, -R, xl, F["flange_y"][1], F["groove2"]["y"][1], "1.5")
    dim_y(sh, vf, -R, xl, F["groove2"]["y"][1], F["len"], "5.5")
    dim_y(sh, vf, -R, xl - 9, 0, F["flange_y"][0], "7")
    xr = vf.P(F["flange_d"] / 2, 0)[0] + 8
    dim_y(sh, vf, R, xr, 0, F["len"], "15")
    dim_y(sh, vf, R, xr + 9, F["pin_y"][0], F["len"], "18")
    dim_y(sh, vf, F["flats_af"] / 2, xr - 4, F["flats_y"][0], F["flats_y"][1], "3")
    # 지름
    yb = vf.P(0, F["pin_y"][0])[1] + 8
    dim_x(sh, vf, -R, R, 2.5, 2.5, yb, f"{F['thread']} (하우징 체결)")
    for (y0, y1) in (F["thread_lower"], F["thread_upper"]):                  # 나사 골지름 (가는 선)
        for xs in (-F["thread_minor"] / 2, F["thread_minor"] / 2):
            a_, b_ = vf.P(xs, y0), vf.P(xs, y1)
            sh.line(*a_, *b_, "thin")
    sh.leader(*vf.P(R, 11.0), xr + 14, vf.P(0, 12.5)[1] + 2, "M10×1.0 (필터 캡)")
    dim_x(sh, vf, -F["flange_d"] / 2, F["flange_d"] / 2, 7.5, 7.5, vf.P(0, F["len"])[1] - 14, "Ø11")
    dim_x(sh, vf, -F["flats_af"] / 2, F["flats_af"] / 2, 13.5, 13.5, vf.P(0, F["len"])[1] - 6, "7 (맞변)")
    tx = xl - 12
    sh.leader(*vf.P(-F["groove1"]["d"] / 2, 6.25), tx, vf.P(0, 4.0)[1],
              f"홈 Ø{F['groove1']['d']} × {F['groove1']['y'][1] - F['groove1']['y'][0]:g}")
    sh.leader(*vf.P(-F["groove2"]["d"] / 2, 8.75), tx, vf.P(0, 11.0)[1],
              f"홈 Ø{F['groove2']['d']} × {F['groove2']['y'][1] - F['groove2']['y'][0]:g}")
    sh.leader(*vf.P(-R + 0.25, F["len"] - 0.25), tx, vf.P(0, 17.0)[1], "C0.5 (양 끝)")

    # ── 단면 A–A (z = +1.27 평면: 핀·소켓 중심) ──
    zc = F["pitch"] / 2
    va = V(sh, 200, 125, sc)
    cut_keep = cq.Workplane("XY").box(40, 40, 20).translate((0, 6, zc - 10)).val()
    half = s.intersect(cut_keep)
    vis, hid = hlr(half, (0, 0, 1), (1, 0, 0))
    va.draw(vis, [])
    for loop in section_face(s, zc):
        pts = [va.P(*p) for p in loop]
        d = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        sh.a(f'<polygon points="{d}" class="hatchfill" style="fill-rule:evenodd"/>')
    va.center_v(F["pin_y"][0], F["len"])
    for x in (-F["pitch"] / 2, F["pitch"] / 2):
        va.center_v(F["pin_y"][0], F["len"], x)
    sh.text(va.P(0, 0)[0], 28, "단면 A–A", 4.0, "middle", bold=True)
    # 단면 치수
    xr2 = va.P(F["flange_d"] / 2, 0)[0] + 8
    dim_y(sh, va, F["pitch"] / 2, xr2, F["sock_bottom"], F["len"], "7.9")
    dim_y(sh, va, F["recess_d"] / 2, xr2 + 9, 0, F["recess_depth"], "7")
    dim_x(sh, va, -F["pitch"] / 2, F["pitch"] / 2, F["len"], F["len"], va.P(0, F["len"])[1] - 8, "2.54")
    dim_x(sh, va, -F["recess_d"] / 2, F["recess_d"] / 2, 0, 0, va.P(0, F["pin_y"][0])[1] + 8, "Ø7")
    tx2 = xr2 + 22
    sh.leader(*va.P(F["pitch"] / 2 + F["sock_d"] / 2, 12.5), tx2, va.P(0, 16.5)[1],
              f"4× Ø{F['sock_d']} 깊이 {F['len'] - F['sock_bottom']:.1f}, 입구 C{F['sock_cs']}")
    sh.leader(*va.P(F["pitch"] / 2 + F["pin_sq"] / 2, -1.5), tx2, va.P(0, -3.5)[1],
              f"4× □{F['pin_sq']} 핀, 끝 C{F['pin_tip']}")
    sh.leader(*va.P(-F["recess_d"] / 2, 4.0), va.P(-8, 0)[0] - 6, va.P(0, -3.5)[1] + 6,
              f"오목부 Ø{F['recess_d']:g} 깊이 {F['recess_depth']:g}")

    # ── 윗면도 (센서 쪽, +y에서 봄) — 제1각법: 정면도 아래 ──
    vt = V(sh, 95, 218, sc)
    vis, hid = hlr(s, (0, 1, 0), (1, 0, 0))
    vt.draw(vis, [])
    vt.center_h(-F["flange_d"] / 2, F["flange_d"] / 2)
    vt.center_v(-F["flange_d"] / 2, F["flange_d"] / 2)
    sh.text(vt.P(0, 0)[0], vt.P(0, -F["flange_d"] / 2)[1] + 12, "윗면도 (센서 소켓 쪽)", 3.6, "middle", bold=True)
    dim_x(sh, vt, -F["pitch"] / 2, F["pitch"] / 2, F["pitch"] / 2, F["pitch"] / 2, vt.P(0, 5.5)[1] - 5, "2.54")
    dim_y(sh, vt, F["pitch"] / 2, vt.P(F["flange_d"] / 2, 0)[0] + 6, -F["pitch"] / 2, F["pitch"] / 2, "2.54")
    # 단면 표시선 A–A (윗면도에서 z=+1.27 → 이 뷰의 모델 y = -z)
    ya_ = vt.P(0, -zc)[1]
    x0_, x1_ = vt.P(-F["flange_d"] / 2 - 3, 0)[0], vt.P(F["flange_d"] / 2 + 3, 0)[0]
    sh.line(x0_, ya_, x0_ + 5, ya_, "thick")
    sh.line(x1_ - 5, ya_, x1_, ya_, "thick")
    sh.line(x0_ + 5, ya_, x1_ - 5, ya_, "center")
    for xx in (x0_, x1_):
        sh.arrow(xx, ya_ - 5, -90)
        sh.line(xx, ya_, xx, ya_ - 5, "thin")
        sh.text(xx, ya_ - 7, "A", 4.0, "middle", bold=True)

    # ── 아랫면도 (PCB 쪽, −y에서 봄) ──
    vb = V(sh, 200, 218, sc)
    vis, hid = hlr(s, (0, -1, 0), (1, 0, 0))
    vb.draw(vis, [])
    vb.center_h(-F["flange_d"] / 2, F["flange_d"] / 2)
    vb.center_v(-F["flange_d"] / 2, F["flange_d"] / 2)
    sh.text(vb.P(0, 0)[0], vb.P(0, -F["flange_d"] / 2)[1] + 12, "아랫면도 (PCB 핀 쪽)", 3.6, "middle", bold=True)
    dim_x(sh, vb, -F["pitch"] / 2, F["pitch"] / 2, F["pitch"] / 2, F["pitch"] / 2, vb.P(0, 5.5)[1] - 5, "2.54")

    # ── 등각도 (참고, 2.5:1) ──
    vi = V(sh, 365, 88, 2.5)
    d = (1, 0.8, 1.2)
    n = math.sqrt(sum(c * c for c in d))
    d = tuple(c / n for c in d)
    up = (0, 1, 0)
    x = (up[1] * d[2] - up[2] * d[1], up[2] * d[0] - up[0] * d[2], up[0] * d[1] - up[1] * d[0])
    nx = math.sqrt(sum(c * c for c in x))
    x = tuple(c / nx for c in x)
    vis, hid = hlr(s, d, x)
    vi.draw(vis, [])
    sh.text(365, 130, "등각도 (참고, 2.5:1)", 3.6, "middle", bold=True)

    # ── PCB 풋프린트 참고 (아랫면 핀) ──
    notes = [
        "주기 (NOTES)",
        "1. 형상·치수는 두텍 SolidWorks 모델 (HTX99R) Sensor Probe_Sensor Connector.STEP 에서 추출. 단위 mm.",
        "2. 재질·공차·표면처리는 STEP에 없음 — 원 도면 또는 공급사 사양 확인. 일반공차 ISO 2768-mK 가정.",
        "3. Ø10 두 곳은 나사: 아래 M10×0.75 = 하우징 체결, 위 M10×1.0 = 필터 캡 체결 (두텍 390000-001100 도면 기준, 확인 필요). 윗면 소켓 4× Ø1.5.",
        "4. PCB 풋프린트 제안: 2×2, 피치 2.54, 도금 구멍 Ø1.0, 패드 Ø1.7. 핀 돌출 3.0 → PCB 1.6 t 관통 후 1.4.",
        "5. 홈 Ø8.2 (플랜지 아래): O링 자리 (HMT500은 O링 8×1.2, Ø10 H8 밀봉면). 홈 Ø8.1 (플랜지 위): 위 나사 언더컷.",
        "6. HMT500 Rev F 적용: 바디 앞 M10×0.75-6H 암나사에 체결, 필터 캡을 위 나사에 체결. 아랫면 핀 4× □0.64: 하네스 W-1 납땜 + 수축튜브 (포팅 없음).",
    ]
    for i, t in enumerate(notes):
        sh.text(252, 168 + i * 6.0, t, 2.6 if i else 3.6, bold=(i == 0))
    sh.text(18, 22, "HTX99R-SC  센서 커넥터  —  정면도 · 단면 A–A · 윗면도 · 아랫면도 (5:1, 제1각법)", 5, bold=True)
    sh.frame()

    os.makedirs(OUT, exist_ok=True)
    svg = os.path.join(OUT, NAME + ".svg")
    open(svg, "w", encoding="utf-8").write(sh.svg())
    html = os.path.join(OUT, "_htx.html")
    open(html, "w").write('<html><head><meta charset="utf-8"><style>@page{size:420mm 297mm;margin:0}body{margin:0}'
                          f'img{{width:420mm;height:297mm;display:block}}</style></head><body><img src="{NAME}.svg"></body></html>')
    chrome = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pdf = os.path.join(OUT, NAME + ".pdf")
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", "file://" + html], stderr=subprocess.DEVNULL, check=True)
    os.remove(html)
    print(svg)
    print(pdf)


if __name__ == "__main__":
    main()
