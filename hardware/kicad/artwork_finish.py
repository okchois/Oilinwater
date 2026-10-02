"""배선 이후 라이브러리 ID·실크·검수 메타데이터 정리 (전기 연결 변경 없음)."""
import json,math,os
from pathlib import Path
import pcbnew as p

MM=p.FromMM

def bbox(obj, margin=0):
    q=obj.GetBoundingBox()
    return (p.ToMM(q.GetX())-margin,p.ToMM(q.GetY())-margin,p.ToMM(q.GetRight())+margin,p.ToMM(q.GetBottom())+margin)
def overlap(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]

def finish(b,report_path):
    for drawing in list(b.GetDrawings()):
        if isinstance(drawing,p.PCB_TEXT) and drawing.GetText() in ('HMT500 A1','HMT500 A2','HMT500 A3','HMT500 A4','HMT500 A5'):b.RemoveNative(drawing)
    fps=sorted(b.GetFootprints(),key=lambda f:(not f.GetReference().startswith(('J','U','D','L')),f.GetReference()))
    for fp in fps:
        fp.SetFPID(p.LIB_ID('HMT500_260313A',fp.GetFPID().GetLibItemName()))
        fp.Value().SetLayer(p.B_Fab if fp.IsFlipped() else p.F_Fab)
        fp.Value().SetVisible(False)
    # These dense adjacent outlines collide with DAC silk; retain on assembly Fab.
    for fp in fps:
        if fp.GetReference() in ('C44','D1'):
            for graphic in fp.GraphicalItems():
                if graphic.GetLayer()==p.B_SilkS:graphic.SetLayer(p.B_Fab)
    # Preserve all assembly labels on Fab; fit only unambiguous readable silk labels.
    pads={layer:[] for layer in (p.F_SilkS,p.B_SilkS)}
    for fp in fps:
        for pad in fp.Pads():
            for silk,mask in ((p.F_SilkS,p.F_Mask),(p.B_SilkS,p.B_Mask)):
                if pad.IsOnLayer(mask):pads[silk].append(bbox(pad,.18))
    shapes={layer:[] for layer in pads}
    for fp in fps:
        for g in fp.GraphicalItems():
            if g.GetLayer() in shapes:shapes[g.GetLayer()].append(bbox(g,.05))
    outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline,False)
    placed={layer:[] for layer in pads}; hidden=[]
    for fp in fps:
        ref=fp.Reference();layer=p.B_SilkS if fp.IsFlipped() else p.F_SilkS
        ref.SetLayer(layer);ref.SetTextSize(p.VECTOR2I(MM(.8),MM(.8)));ref.SetTextThickness(MM(.12))
        ref.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));ref.SetVisible(True)
        origin=fp.GetPosition();x,y=p.ToMM(origin.x),p.ToMM(origin.y)
        offsets=[(i*.4,j*.4) for i in range(-12,13) for j in range(-12,13)]
        offsets.sort(key=lambda q:math.hypot(*q))
        ok=False
        for dx,dy in offsets:
            ref.SetPosition(p.VECTOR2I(MM(x+dx),MM(y+dy)))
            box=bbox(ref,.08)
            # Conservative actual board polygon containment is checked by KiCad DRC afterwards.
            if not all(outline.Contains(p.VECTOR2I(MM(a),MM(c))) for a in (box[0]-.25,box[2]+.25) for c in (box[1]-.25,box[3]+.25)):continue
            if any(overlap(box,q) for q in pads[layer]+shapes[layer]+placed[layer]):continue
            placed[layer].append(box);ok=True;break
        if not ok:
            ref.SetPosition(origin);ref.SetVisible(False);hidden.append(fp.GetReference())
    # Board identification had historically used mechanical coordinates directly.
    for item in b.GetDrawings():
        if isinstance(item,p.PCB_TEXT) and item.GetLayer()==p.B_SilkS:
            item.SetLayer(p.Cmts_User) # artwork ID goes in free space below, original preserved in documentation
    mark=p.PCB_TEXT(b);mark.SetText('HMT500 '+os.environ.get('HMT_ARTWORK','A5'));mark.SetLayer(p.F_SilkS)
    mark.SetTextSize(p.VECTOR2I(MM(.8),MM(.8)));mark.SetTextThickness(MM(.12))
    mark.SetPosition(p.VECTOR2I(MM(152),MM(100)));b.Add(mark)
    tracks=list(b.GetTracks());lengths={};vias={}
    for t in tracks:
        if isinstance(t,p.PCB_VIA):vias[t.GetNetname()]=vias.get(t.GetNetname(),0)+1
        else:lengths[t.GetNetname()]=lengths.get(t.GetNetname(),0)+p.ToMM(t.GetLength())
    data={'status':'DRAFT - not released','silk_refs_hidden':hidden,'track_mm':{n:round(v,3) for n,v in lengths.items()},'vias':vias}
    Path(report_path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
