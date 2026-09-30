"""HMT500(260313A) 프로젝트 풋프린트 라이브러리 — 직접 만드는 풋프린트 3개 (KiCad 7 pcbnew API).

  python3 hardware/kicad/gen_footprints.py  →  hardware/kicad/lib/HMT500_260313A.pretty/

같은 폴더의 나머지 풋프린트는 KiCad 공식 라이브러리 7.0.11 태그에서 그대로 복사한 것 (CC-BY-SA 4.0 + 예외 조항).
여기서 만드는 것:
  - Texas_RNX0012A_VQFN-HR-12_2x3mm : LMR36006 (TI SNVSB48C, RNX0012A Example Board Layout)
  - GDT_Bourns_2035-xx-SM           : 2전극 SMD GDT Ø5 × 4.4 (Bourns 2035-xx-SM 권장 패드 4.0 피치, 1.3 × 5.6)
  - Texas_DRB0008A_PadFloat          : TVS3301 — 방열 패드는 떠 있어야 함 (데이터시트 표 7-1) → 비아·뒷면 패드 제거 (9번 패드는 심볼 핀이 없어 넷 없음)
"""

import os

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "lib", "HMT500_260313A.pretty")
MM = pcbnew.FromMM


def vec(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def new_fp(name, descr):
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID("HMT500_260313A", name))
    fp.SetDescription(descr)
    fp.SetAttributes(pcbnew.FP_SMD)
    fp.Reference().SetText("REF**")
    fp.Reference().SetPosition(vec(0, -2.6))
    fp.Value().SetText(name)
    fp.Value().SetPosition(vec(0, 2.6))
    return fp


def pad(fp, num, x, y, w, h, shape=pcbnew.PAD_SHAPE_ROUNDRECT, rr=0.2, layers=("F.Cu", "F.Paste", "F.Mask")):
    p = pcbnew.PAD(fp)
    p.SetNumber(num)
    p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(shape)
    if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
        p.SetRoundRectRadiusRatio(rr)
    p.SetSize(vec(w, h))
    p.SetPosition(vec(x, y))
    p.SetPos0(vec(x, y))                     # KiCad 7: 저장은 로컬 좌표(pos0)
    ls = pcbnew.LSET()
    for n in layers:
        ls.AddLayer({"F.Cu": pcbnew.F_Cu, "F.Paste": pcbnew.F_Paste, "F.Mask": pcbnew.F_Mask}[n])
    p.SetLayerSet(ls)
    fp.Add(p)


def rect(fp, layer, x0, y0, x1, y1, width):
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        s = pcbnew.FP_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart0(vec(*a))
        s.SetEnd0(vec(*b))
        s.SetDrawCoord()
        s.SetLayer(layer)
        s.SetWidth(MM(width))
        fp.Add(s)


def line(fp, layer, a, b, width):
    s = pcbnew.FP_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart0(vec(*a))
    s.SetEnd0(vec(*b))
    s.SetDrawCoord()
    s.SetLayer(layer)
    s.SetWidth(MM(width))
    fp.Add(s)


def rnx0012a():
    """TI RNX0012A land pattern (도면 좌표: 위 +y → KiCad y 반전). 패드 0.6 × 0.25, 반경 0.05."""
    fp = new_fp("Texas_RNX0012A_VQFN-HR-12_2x3mm",
                "TI RNX0012A VQFN-HR 12 pin 2x3 mm (LMR36006), land pattern per SNVSB48C Example Board Layout")
    left = {"1": 1.125, "2": 0.475, "3": -0.175, "4": -0.675}
    right = {"11": 1.125, "10": 0.475, "9": -0.175, "8": -0.675}
    for n, y in left.items():
        pad(fp, n, -0.9, -y, 0.6, 0.25)
    for n, y in right.items():
        pad(fp, n, 0.9, -y, 0.6, 0.25)
    for n, x in (("5", -0.5), ("6", 0.0), ("7", 0.5)):
        pad(fp, n, x, 1.4, 0.25, 0.6)
    pad(fp, "12", 0.0, -0.788, 0.25, 1.825, rr=0.2)          # SW: 가운데 긴 패드
    rect(fp, pcbnew.F_Fab, -1.0, -1.5, 1.0, 1.5, 0.1)
    rect(fp, pcbnew.F_CrtYd, -1.45, -1.95, 1.45, 1.95, 0.05)
    line(fp, pcbnew.F_SilkS, (-1.35, -1.65), (-0.95, -1.65), 0.12)   # 1번 핀 표시
    return fp


def gdt_2035():
    fp = new_fp("GDT_Bourns_2035-xx-SM",
                "Bourns 2035-xx-SM 2-electrode SMD GDT, 5 mm dia x 4.4 mm; pads 1.3 x 5.6 at 4.0 mm pitch "
                "(datasheet recommended pad layout)")
    pad(fp, "1", -2.0, 0, 1.3, 5.6, shape=pcbnew.PAD_SHAPE_RECT)
    pad(fp, "2", 2.0, 0, 1.3, 5.6, shape=pcbnew.PAD_SHAPE_RECT)
    rect(fp, pcbnew.F_Fab, -2.2, -2.5, 2.2, 2.5, 0.1)
    rect(fp, pcbnew.F_CrtYd, -2.9, -3.05, 2.9, 3.05, 0.05)
    fp.Reference().SetPosition(vec(0, -3.6))
    fp.Value().SetPosition(vec(0, 3.6))
    return fp


def drb_padfloat():
    src = pcbnew.FootprintLoad(LIB, "Texas_DRB0008A")
    fp = pcbnew.FOOTPRINT(src)
    fp.SetFPID(pcbnew.LIB_ID("HMT500_260313A", "Texas_DRB0008A_PadFloat"))
    fp.SetDescription("TI DRB0008A for TVS3301: exposed pad must float (no vias, no B.Cu pad; pad 9 has no symbol pin)")
    for p in list(fp.Pads()):
        if p.GetNumber() == "9":
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH or p.IsOnLayer(pcbnew.B_Cu):
                fp.Remove(p)
            # 남은 앞면 패드 조각은 번호 9 유지: 심볼에 9번 핀이 없으므로 어떤 넷에도 연결되지 않음
    return fp


if __name__ == "__main__":
    for f in (rnx0012a(), gdt_2035(), drb_padfloat()):
        pcbnew.FootprintSave(LIB, f)
        print(f.GetFPID().GetLibItemName(), len(f.Pads()), "pads")
