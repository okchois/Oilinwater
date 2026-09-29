"""HMT500 3D 모델 음영 렌더(오프스크린 VTK) → out/HMT500_render.png, out/HMT500_render_section.png"""
import os
import sys

import cadquery as cq
import vtk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hmt500_cad as M  # noqa: E402


def actor_for(shape, color, opacity=1.0):
    v = shape.val() if hasattr(shape, "val") else shape
    data = v.toVtkPolyData(0.02, 0.2)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(data)
    normals.SetFeatureAngle(35)
    m = vtk.vtkPolyDataMapper()
    m.SetInputConnection(normals.GetOutputPort())
    a = vtk.vtkActor()
    a.SetMapper(m)
    p = a.GetProperty()
    p.SetColor(*color)
    p.SetSpecular(0.5)
    p.SetSpecularPower(40)
    p.SetDiffuse(0.8)
    p.SetAmbient(0.25)
    p.SetOpacity(opacity)
    return a


def render(parts, out, cut=False):
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    cutter = cq.Workplane("XY").box(400, 100, 100).translate((0, -50, 0))
    for name, fn, col in parts:
        s = fn()
        if cut and not name.startswith(("E-301", "W-")):   # PCB는 자르지 않고 전체를 보여 줌
            s = s.cut(cutter)
        ren.AddActor(actor_for(s, col))
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(ren)
    win.SetSize(1800, 800)
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(23, 0, 0)
    cam.SetPosition(23 + 110, -230, 120)
    cam.SetViewUp(0, 0, 1)
    ren.ResetCamera()
    cam.Zoom(1.55)
    light = vtk.vtkLight()
    light.SetPosition(200, -300, 300)
    light.SetFocalPoint(0, 0, 0)
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
    o = M.OUT
    render(M.PARTS, os.path.join(o, "HMT500_render.png"))
    render(M.PARTS, os.path.join(o, "HMT500_render_section.png"), cut=True)
