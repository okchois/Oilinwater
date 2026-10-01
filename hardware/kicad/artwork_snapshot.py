"""검토 중 배선의 재현 가능한 스냅샷. 다른 배치에는 적용하지 않는다.

capture OUTPUT.json / restore INPUT.json — KiCad pcbnew Python으로 실행.
스냅샷은 제작 승인 또는 DRC 통과를 의미하지 않는다.
"""
import argparse, json
from pathlib import Path
import pcbnew as p
import wx
from route_pcb import BASE

def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def vec(a):return p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1]))
def placement(b):
    return {f.GetReference():dict(pos=[round(v,4) for v in xy(f.GetPosition())],angle=round(f.GetOrientationDegrees(),4),flipped=f.IsFlipped(),footprint=str(f.GetFPID().GetLibItemName())) for f in b.GetFootprints()}
def capture(b):
    tracks=[]
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):
            tracks.append(dict(kind='via',net=t.GetNetname(),pos=xy(t.GetPosition()),width=p.ToMM(t.GetWidth(p.F_Cu)),drill=p.ToMM(t.GetDrillValue())))
        else:tracks.append(dict(kind='track',net=t.GetNetname(),start=xy(t.GetStart()),end=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=b.GetLayerName(t.GetLayer())))
    zones=[]
    for z in b.Zones():
        poly=z.Outline()
        if any(poly.HoleCount(i) for i in range(poly.OutlineCount())):raise ValueError('Zone holes unsupported; extend serializer before capture')
        zones.append(dict(name=z.GetZoneName(),layers=[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],net=z.GetNetname(),rule=z.GetIsRuleArea(),tracks=z.GetDoNotAllowTracks(),vias=z.GetDoNotAllowVias(),fills=z.GetDoNotAllowZoneFills(),priority=z.GetAssignedPriority(),clearance=p.ToMM(z.GetLocalClearance()),minimum=p.ToMM(z.GetMinThickness()),points=[[xy(poly.COutline(i).CPoint(j)) for j in range(poly.COutline(i).PointCount())] for i in range(poly.OutlineCount())]))
    return dict(status='DRAFT — NOT FOR FABRICATION',placement=placement(b),tracks=tracks,zones=zones)
def restore(b,d):
    if placement(b)!=d['placement']:raise ValueError('Placement differs from routing snapshot: reroute required')
    for t in list(b.GetTracks()):b.RemoveNative(t)
    for z in list(b.Zones()):b.RemoveNative(z)
    for q in d['tracks']:
        if q['kind']=='via':
            t=p.PCB_VIA(b);t.SetPosition(vec(q['pos']));t.SetWidth(p.FromMM(q['width']));t.SetDrill(p.FromMM(q['drill']));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
        else:
            t=p.PCB_TRACK(b);t.SetStart(vec(q['start']));t.SetEnd(vec(q['end']));t.SetWidth(p.FromMM(q['width']));t.SetLayer(b.GetLayerID(q['layer']))
        t.SetNet(b.FindNet(q['net']));b.Add(t)
    for q in d['zones']:
        z=p.ZONE(b);layers=p.LSET()
        for layer in q['layers']:
            lid=b.GetLayerID(layer)
            if lid<0:raise ValueError('Unknown layer '+layer)
            layers.AddLayer(lid)
        z.SetLayerSet(layers);z.SetZoneName(q['name']);z.SetIsRuleArea(q['rule'])
        z.SetDoNotAllowTracks(q['tracks']);z.SetDoNotAllowVias(q['vias']);z.SetDoNotAllowZoneFills(q['fills']);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
        if not q['rule']:z.SetNet(b.FindNet(q['net']))
        z.SetAssignedPriority(q['priority']);z.SetLocalClearance(p.FromMM(q['clearance']));z.SetMinThickness(p.FromMM(q['minimum']));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
        for pts in q['points']:
            z.Outline().NewOutline()
            for pt in pts:z.Outline().Append(vec(pt))
        b.Add(z)
    from artwork_finish import finish
    finish(b,BASE.parent/'artwork_metrics.json')
    b.BuildConnectivity();p.SaveBoard(str(BASE)+'.kicad_pcb',b,True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['capture','restore']);ap.add_argument('file',type=Path);a=ap.parse_args()
    app=wx.App(False);b=p.LoadBoard(str(BASE)+'.kicad_pcb')
    if a.mode=='capture':a.file.parent.mkdir(parents=True,exist_ok=True);a.file.write_text(json.dumps(capture(b),ensure_ascii=False,indent=2)+'\n')
    else:restore(b,json.loads(a.file.read_text()))
