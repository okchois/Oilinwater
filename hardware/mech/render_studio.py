"""HMT500 제품 시안 — 스튜디오 사진풍 렌더 (VTK PBR + 환경광 + SSAO, 오프스크린).

  python hardware/mech/render_studio.py  →  hardware/mech/out/studio/HMT500_studio_*.png

- 형상은 hmt500_cad.py 를 그대로 쓰고, 사진용으로 나사산(톱니 회전체)·커넥터 핀·레이저 마킹만 덧붙인다.
- 치수 확인용이 아닌 외관 시안이다. 마킹 문안·커넥터 외형은 확정 전 가안.
"""

import math
import os
import sys

import numpy as np
import vtk
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from vtk.util import numpy_support as ns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq  # noqa: E402

import hmt500_cad as M  # noqa: E402
import hmt500_params as P  # noqa: E402

OUT = os.path.join(M.OUT, "studio")
TMP = os.path.join(OUT, "_tex")
BG = 0.965                       # 배경·바닥 밝기 (무한 흰 배경)
SS = 2                           # 슈퍼샘플링 배율
W, H = 1800, 1200
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MARK_DIR = math.radians(145)     # 마킹 중심 방향: atan2(z, y) — 카메라 쪽(−y) 약간 위


# ─────────────── 사진용 형상 보강 ───────────────
def saw_thread(x0, x1, d, d_minor, pitch):
    """나사산 모양 톱니 회전체 (나선 아님, 외관용)."""
    R, r = d / 2, d_minor / 2
    pts = [(x0, 0), (x0, r)]
    x = x0
    while x + pitch <= x1 + 1e-6:
        pts += [(x + pitch * 0.5, R), (x + pitch, r)]
        x += pitch
    pts += [(x1, r), (x1, 0)]
    out = []
    for q in pts:                       # 중복 점 제거 (길이 0 선분 방지)
        if not out or abs(out[-1][0] - q[0]) > 1e-6 or abs(out[-1][1] - q[1]) > 1e-6:
            out.append(q)
    return M.revolve(out)


def body_photo():
    B = P.BODY
    s = M.body()
    g = B["gthread"]
    s = s.cut(M.tube(*g["x"], g["d"] + 1, g["d_minor"] - 0.01)).union(
        saw_thread(*g["x"], g["d"], g["d_minor"], 25.4 / 14))
    return s.cut(M.cyl(*B["wire"]["x"], B["wire"]["d"]))


def connector_photo():
    Cn = P.CONNECTOR
    b0, b1 = Cn["body"]["x"]
    t0, t1 = Cn["thread"]["x"]
    nut = cq.Workplane("YZ").workplane(offset=b0).polygon(6, 18 / 0.8660254).extrude(b1 - b0)
    cham = M.revolve([(b0, 0), (b1, 0), (b1, 9.0), (b1 - 0.8, 10.4), (b0 + 0.8, 10.4), (b0, 9.0)])
    s = nut.intersect(cham)
    s = s.union(M.cyl(*Cn["inner"]["x"], Cn["inner"]["d"]))
    s = s.union(M.cyl(t0, t0 + 2, 11.0)).union(saw_thread(t0 + 2, t1, 12.0, 10.9, 1.0))
    return s.cut(M.cyl(t1 - 8, t1 + 0.1, 9.5))


def connector_insert():
    t1 = P.CONNECTOR["thread"]["x"][1]
    return M.cyl(t1 - 8, t1 - 3.2, 9.4)


def connector_pins():
    t1 = P.CONNECTOR["thread"]["x"][1]
    out = M.cyl(t1 - 3.3, t1 - 0.8, 1.0)                         # 가운데 핀
    for i in range(7):
        a = 2 * math.pi * i / 7 + math.pi / 2
        pin = cq.Workplane("YZ").workplane(offset=t1 - 3.3).center(2.9 * math.cos(a), 2.9 * math.sin(a)) \
            .circle(0.5).extrude(2.5)
        out = out.union(pin)
    key = cq.Workplane("XY").box(5, 1.2, 1.2).translate((t1 - 5.5, 0, -4.4))   # 코딩 키
    return out.union(key)


def seal_steel():
    S = P.SEAL
    return M.tube(*S["x"], S["od"], 24.2)


def seal_rubber():
    S = P.SEAL
    return M.tube(S["x"][0] - 0.15, S["x"][1] + 0.15, 24.2, S["id"])


# ─────────────── 재질 ───────────────
STEEL = dict(color=(0.80, 0.81, 0.83), metal=1.0, rough=0.28)
STEEL_BLAST = dict(color=(0.74, 0.75, 0.77), metal=1.0, rough=0.48)
STEEL_TURN = dict(color=(0.82, 0.83, 0.85), metal=1.0, rough=0.20)
NICKEL = dict(color=(0.83, 0.82, 0.79), metal=1.0, rough=0.22)
BLACK = dict(color=(0.04, 0.04, 0.045), metal=0.0, rough=0.45)
RUBBER = dict(color=(0.03, 0.03, 0.03), metal=0.0, rough=0.75)
GOLD = dict(color=(1.0, 0.80, 0.42), metal=1.0, rough=0.25)
FR4 = dict(color=(0.05, 0.32, 0.14), metal=0.0, rough=0.35)
IC = dict(color=(0.06, 0.06, 0.07), metal=0.0, rough=0.5)
PEEK = dict(color=(0.78, 0.66, 0.46), metal=0.0, rough=0.55)
KOVAR = dict(color=(0.72, 0.62, 0.40), metal=1.0, rough=0.35)
ALUMINA = dict(color=(0.93, 0.92, 0.88), metal=0.0, rough=0.5)
CUT = dict(color=(0.70, 0.71, 0.73), metal=1.0, rough=0.55)


EXTERIOR = [
    ("cap", M.cap, STEEL_BLAST),
    ("body", body_photo, STEEL_TURN),
    ("housing", M.housing, STEEL),
    ("endcap", M.endcap, STEEL_TURN),
    ("seal_steel", seal_steel, dict(color=(0.70, 0.71, 0.72), metal=1.0, rough=0.35)),
    ("seal_rubber", seal_rubber, RUBBER),
    ("connector", connector_photo, NICKEL),
    ("insert", connector_insert, BLACK),
    ("pins", connector_pins, GOLD),
]
INTERIOR = [
    ("header", M.header, KOVAR),
    ("sensor_probe", M.sensor_probe, PEEK),
    ("elements", M.sensor_elements, ALUMINA),
    ("sensor_conn", M.sensor_connector, BLACK),
    ("conn_oring", M.conn_oring, RUBBER),
    ("orings", M.orings, RUBBER),
    ("pcb", M.pcbs, FR4),
    ("pcb_parts", M.pcb_parts, IC),
    ("holder", M.pcb_holder, PEEK),
    ("ring", M.pcb_ring, PEEK),
]


# ─────────────── 텍스처 ───────────────
def marking_textures():
    """하우징 레이저 마킹: base color + ORM(오클루전·거칠기·금속도). 가로 = 축(60 mm), 세로 = 둘레."""
    L = P.HOUSING["x"][1] - P.HOUSING["x"][0]
    C = math.pi * P.HOUSING["od"]
    ppm = 24
    w, h = int(L * ppm), int(C * ppm)
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    cx, cy = w // 2, h // 2

    def txt(s, y, size, font=FONT_R, anchor="mm", x=None):
        d.text((cx if x is None else x, cy + y * ppm), s, fill=255, font=ImageFont.truetype(font, int(size * ppm)),
               anchor=anchor)

    txt("DOTECH", -6.8, 4.2, FONT_B)
    d.line([(cx - 20 * ppm, cy - 3.6 * ppm), (cx + 20 * ppm, cy - 3.6 * ppm)], fill=255, width=int(0.18 * ppm))
    txt("HMT500", -0.6, 3.3, FONT_B)
    txt("Moisture-in-Oil Transmitter", 3.3, 1.45)
    txt("aw  ·  T  ·  ppm      RS-485 Modbus RTU  ·  2× V/I", 6.0, 1.05)
    txt("12–30 V DC   ·   IP67   ·   20 bar", 8.2, 1.05)
    txt("S/N  HMT5-26-00017", 10.6, 0.95)
    # 핀맵 (뒤쪽, 작은 글씨)
    y0 = 15.0
    for i, s in enumerate(["8  V+", "6  GND", "4  OUT1", "5  OUT2", "3  RS485 A", "2  RS485 B"]):
        d.text((cx - 18 * ppm + (i % 3) * 13 * ppm, cy + (y0 + (i // 3) * 2.0) * ppm), s, fill=200,
               font=ImageFont.truetype(FONT_R, int(0.9 * ppm)), anchor="lm")
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))
    m = np.asarray(mask, dtype=np.float32) / 255.0
    # 헤어라인(축 방향 가는 결)
    rng = np.random.default_rng(3)
    grain = rng.normal(0, 1, (h, 1)).astype(np.float32)
    grain = np.repeat(grain, w, axis=1)
    grain = np.asarray(Image.fromarray(((grain * 18) + 128).clip(0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.8)), dtype=np.float32) / 255.0 - 0.5
    base_metal = np.array([204, 206, 210], np.float32)
    mark = np.array([58, 60, 64], np.float32)
    base = base_metal[None, None, :] * (1 + 0.05 * grain[..., None])
    rgb = base * (1 - m[..., None]) + mark[None, None, :] * m[..., None]
    orm = np.zeros((h, w, 3), np.float32)
    orm[..., 0] = 255
    orm[..., 1] = (0.26 + 0.05 * grain + 0.40 * m) * 255
    orm[..., 2] = (1.0 - 0.55 * m) * 255
    os.makedirs(TMP, exist_ok=True)
    pb, po = os.path.join(TMP, "housing_base.png"), os.path.join(TMP, "housing_orm.png")
    # VTK PNG 리더는 아래 행부터 읽으므로 위아래를 뒤집어 저장 (글자가 바로 보이게)
    Image.fromarray(np.flipud(rgb).clip(0, 255).astype(np.uint8)).save(pb)
    Image.fromarray(np.flipud(orm).clip(0, 255).astype(np.uint8)).save(po)
    return pb, po


def env_texture():
    os.makedirs(TMP, exist_ok=True)
    """스튜디오 환경(등장방형): 어두운 회색 + 위쪽 큰 소프트박스 + 좌우 스트립 + 밝은 바닥."""
    w, h = 2048, 1024
    lon = (np.arange(w) + 0.5) / w * 2 * math.pi - math.pi
    lat = math.pi / 2 - (np.arange(h) + 0.5) / h * math.pi
    LON, LAT = np.meshgrid(lon, lat)
    img = np.full((h, w), 0.52, np.float32)
    img += 0.12 * np.clip(LAT / (math.pi / 2), 0, 1)
    img[LAT < -0.05] = 0.92                                           # 흰 바닥 반사

    def box(lon0, lat0, dlon, dlat, v):
        m = (np.abs(((LON - lon0 + math.pi) % (2 * math.pi)) - math.pi) < dlon) & (np.abs(LAT - lat0) < dlat)
        img[m] = v

    box(0.0, 1.15, 0.9, 0.30, 1.0)                                   # 위 소프트박스
    box(-1.9, 0.30, 0.18, 0.45, 1.0)                                 # 왼쪽 스트립
    box(1.7, 0.35, 0.14, 0.40, 0.85)                                 # 오른쪽 스트립
    box(math.pi, 0.25, 0.5, 0.25, 0.55)                              # 뒤 반사판
    im = Image.fromarray((img * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)).convert("RGB")
    p = os.path.join(TMP, "env.png")
    im.save(p)
    return p


def profile_r(x):
    """바깥 반경 r(x) — 바닥 그림자용."""
    best = 0.0
    for fn_parts in (P.BODY, P.ENDCAP):
        for k, v in fn_parts.items():
            if isinstance(v, dict) and "x" in v and "d" in v and k not in ("seat", "wire", "cbore", "thread"):
                if v["x"][0] <= x <= v["x"][1]:
                    best = max(best, v["d"] / 2)
    if P.BODY["hexa"]["x"][0] <= x <= P.BODY["hexa"]["x"][1]:
        best = max(best, P.hex_corner_d(P.BODY["hexa"]["af"]) / 2)
    if P.CAP["x_tip"] <= x <= P.CAP["x_rear"]:
        best = max(best, P.CAP["od"] / 2)
    if P.HOUSING["x"][0] <= x <= P.HOUSING["x"][1]:
        best = max(best, P.HOUSING["od"] / 2)
    Cn = P.CONNECTOR
    if Cn["body"]["x"][0] <= x <= Cn["body"]["x"][1]:
        best = max(best, 10.4)
    if Cn["thread"]["x"][0] <= x <= Cn["thread"]["x"][1]:
        best = max(best, 6.0)
    return best


FLOOR = dict(x=(-160.0, 220.0), y=(-150.0, 150.0))


def floor_texture(rotz_deg):
    os.makedirs(TMP, exist_ok=True)
    """바닥 접촉 그림자 텍스처 (제품 z축 회전 반영)."""
    ppm = 4
    (x0, x1), (y0, y1) = FLOOR["x"], FLOOR["y"]
    w, h = int((x1 - x0) * ppm), int((y1 - y0) * ppm)
    xs = x0 + (np.arange(w) + 0.5) / ppm
    ys = y1 - (np.arange(h) + 0.5) / ppm
    X, Y = np.meshgrid(xs, ys)
    a = math.radians(-rotz_deg)
    Xp = X * math.cos(a) - Y * math.sin(a)                            # 제품 좌표로 되돌림
    Yp = X * math.sin(a) + Y * math.cos(a)
    xr = np.linspace(P.TIP_X - 1, P.END_X + 1, 800)
    rr = np.array([profile_r(x) for x in xr])
    R = np.interp(Xp, xr, rr, left=0, right=0)
    R16 = R / 16.0
    sig = 2.5 + 7.0 * (1 - R16) + 3.0
    dark = (0.10 + 0.42 * R16 ** 4) * np.exp(-(Yp ** 2) / (2 * (0.55 * R + sig) ** 2)) * (R > 0)
    dark += 0.25 * np.exp(-(Yp ** 2) / (2 * (0.25 * R + 0.8) ** 2)) * (R16 > 0.97)
    im = Image.fromarray((dark * 255).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2 * ppm))
    dk = np.asarray(im, np.float32) / 255.0
    v = (BG * (1 - dk)) * 255
    p = os.path.join(TMP, f"floor_{int(rotz_deg)}.png")
    Image.fromarray(np.dstack([v, v, v]).clip(0, 255).astype(np.uint8)).save(p)
    return p


# ─────────────── VTK 도우미 ───────────────
def polydata(shape, tol=0.01, ang=0.08):
    v = shape.val() if hasattr(shape, "val") else shape
    pd = v.toVtkPolyData(tol, ang)
    n = vtk.vtkPolyDataNormals()
    n.SetInputData(pd)
    n.SetFeatureAngle(32)
    n.SplittingOn()
    n.ConsistencyOn()
    n.Update()
    return n.GetOutput()


def transformed(pd, rotz):
    t = vtk.vtkTransform()
    t.RotateZ(rotz)
    f = vtk.vtkTransformPolyDataFilter()
    f.SetTransform(t)
    f.SetInputData(pd)
    f.Update()
    return f.GetOutput()


def housing_tcoords(pd):
    pts = ns.vtk_to_numpy(pd.GetPoints().GetData())
    x0, x1 = P.HOUSING["x"]
    s = (pts[:, 0] - x0) / (x1 - x0)
    th = np.arctan2(pts[:, 2], pts[:, 1])
    t = ((th - MARK_DIR) / (2 * math.pi) + 0.5) % 1.0
    tc = ns.numpy_to_vtk(np.column_stack([s, t]).astype(np.float32), deep=True)
    tc.SetName("TCoords")
    pd.GetPointData().SetTCoords(tc)
    return pd


def texture(path, srgb=True):
    r = vtk.vtkPNGReader()
    r.SetFileName(path)
    t = vtk.vtkTexture()
    t.SetInputConnection(r.GetOutputPort())
    t.InterpolateOn()
    t.MipmapOn()
    t.RepeatOff()
    t.EdgeClampOn()
    if srgb:
        t.UseSRGBColorSpaceOn()
    return t


def pbr_actor(pd, mat, base_tex=None, orm_tex=None):
    m = vtk.vtkPolyDataMapper()
    m.SetInputData(pd)
    a = vtk.vtkActor()
    a.SetMapper(m)
    p = a.GetProperty()
    p.SetInterpolationToPBR()
    p.SetColor(*mat["color"])
    p.SetMetallic(mat["metal"])
    p.SetRoughness(mat["rough"])
    if base_tex is not None:
        p.SetColor(1, 1, 1)
        p.SetBaseColorTexture(base_tex)
    if orm_tex is not None:
        p.SetORMTexture(orm_tex)
        p.SetMetallic(1.0)
        p.SetRoughness(1.0)
        p.SetOcclusionStrength(1.0)
    return a


def floor_actor(rotz):
    (x0, x1), (y0, y1) = FLOOR["x"], FLOOR["y"]
    z = -P.HOUSING["od"] / 2 - 0.02
    ps = vtk.vtkPlaneSource()
    ps.SetOrigin(x0, y0, z)
    ps.SetPoint1(x1, y0, z)
    ps.SetPoint2(x0, y1, z)
    m = vtk.vtkPolyDataMapper()
    m.SetInputConnection(ps.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(m)
    a.SetTexture(texture(floor_texture(rotz), srgb=False))
    p = a.GetProperty()
    p.LightingOff()
    return a


# ─────────────── 장면 ───────────────
def build_scene(rotz, cutaway=False, cache={}):
    key = ("pd", cutaway)
    if key not in cache:
        cutter = cq.Workplane("XY").box(400, 100, 100).translate((0, -50, 0))
        parts = []
        for name, fn, mat in EXTERIOR + (INTERIOR if cutaway else []):
            s = fn()
            if cutaway and name not in ("pcb", "pcb_parts", "pins", "sensor_probe", "elements"):
                s = s.cut(cutter)
            parts.append((name, polydata(s), mat))
        cache[key] = parts
    return cache[key]


def render(name, cam_pos, focal, rotz=0.0, cutaway=False, view_angle=24.0, up=(0, 0, 1)):
    ren = vtk.vtkRenderer()
    ren.SetBackground(BG, BG, BG)
    env = texture(env_texture(), srgb=True)
    env.SetColorModeToDirectScalars()
    ren.SetEnvironmentTexture(env, True)
    ren.UseImageBasedLightingOn()
    ren.SetEnvironmentUp(0, 0, 1)
    ren.SetEnvironmentRight(1, 0, 0)
    base_p, orm_p = marking_textures()
    for pname, pd, mat in build_scene(rotz, cutaway):
        pdt = transformed(pd, rotz)
        if pname == "housing" and not cutaway:
            housing_tcoords(pd)
            pdt = transformed(pd, rotz)
            ren.AddActor(pbr_actor(pdt, mat, texture(base_p), texture(orm_p, srgb=False)))
        else:
            ren.AddActor(pbr_actor(pdt, mat))
    ren.AddActor(floor_actor(rotz))
    for pos, inten in (((-150, -220, 320), 1.5), ((260, -120, 140), 0.6), ((0, 250, 200), 0.4)):
        lt = vtk.vtkLight()
        lt.SetLightTypeToSceneLight()
        lt.SetPosition(*pos)
        lt.SetFocalPoint(20, 0, 0)
        lt.SetIntensity(inten)
        ren.AddLight(lt)
    ren.UseSSAOOn()
    ren.SetSSAORadius(4.0)
    ren.SetSSAOBias(0.05)
    ren.SetSSAOKernelSize(128)
    ren.SetSSAOBlur(True)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(ren)
    win.SetSize(W * SS, H * SS)
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(*focal)
    cam.SetPosition(*cam_pos)
    cam.SetViewUp(*up)
    cam.SetViewAngle(view_angle)
    ren.ResetCameraClippingRange()
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.ReadFrontBufferOff()
    w2i.Update()
    arr = ns.vtk_to_numpy(w2i.GetOutput().GetPointData().GetScalars())
    img = arr.reshape(H * SS, W * SS, -1)[::-1, :, :3]
    im = Image.fromarray(img.astype(np.uint8)).resize((W, H), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"HMT500_studio_{name}.png")
    im.save(p)
    print(p)
    return p


SHOTS = [
    # 이름, 카메라 위치, 초점, 제품 회전(z), 절개, 화각
    ("01_hero", (-95, -250, 120), (26, 0, -2), 0, False, 26),
    ("02_rear", (250, -190, 95), (30, 0, -2), 0, False, 27),
    ("03_side", (24, -330, 38), (24, 0, -1), 0, False, 25),
    ("04_probe_closeup", (-120, -95, 45), (-22, 0, -2), 0, False, 22),
    ("05_top", (-40, -150, 260), (24, 0, -4), -25, False, 28),
    ("06_cutaway", (40, -260, 150), (24, 0, -2), 0, True, 26),
]


def main():
    only = set(sys.argv[1:])
    for name, pos, foc, rz, cut, va in SHOTS:
        if only and not any(name.startswith(o) for o in only):
            continue
        render(name, pos, foc, rz, cut, va)


if __name__ == "__main__":
    main()
