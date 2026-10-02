"""배선 이후 라이브러리 ID·실크·검수 메타데이터 정리 (전기 연결 변경 없음)."""
import json,math,os,uuid
from pathlib import Path
import pcbnew as p

MM=p.FromMM

def bbox(obj, margin=0):
    q=obj.GetBoundingBox()
    return (p.ToMM(q.GetX())-margin,p.ToMM(q.GetY())-margin,p.ToMM(q.GetRight())+margin,p.ToMM(q.GetBottom())+margin)
def overlap(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]

def finish(b,report_path):
    b.GetTitleBlock().SetRevision(os.environ.get("HMT_ARTWORK","A5")+"-R3")
    leader_ids={str(uuid.uuid5(uuid.NAMESPACE_URL,"hmt500/silk-leader/"+f.GetReference())) for f in b.GetFootprints()}
    for drawing in list(b.GetDrawings()):
        if isinstance(drawing,p.PCB_SHAPE) and drawing.m_Uuid.AsString() in leader_ids:b.RemoveNative(drawing);continue
        if isinstance(drawing,p.PCB_TEXT) and drawing.GetText().startswith('HMT500 A'):b.RemoveNative(drawing)
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
    for item in b.GetDrawings():
        if isinstance(item,p.PCB_TEXT) and item.GetLayer()==p.B_SilkS:
            item.SetLayer(p.Cmts_User)
    from silk_layout import layout
    placements,hidden,leaders,logo=layout(b,fps)
    tracks=list(b.GetTracks());lengths={};vias={}
    for t in tracks:
        if isinstance(t,p.PCB_VIA):vias[t.GetNetname()]=vias.get(t.GetNetname(),0)+1
        else:lengths[t.GetNetname()]=lengths.get(t.GetNetname(),0)+p.ToMM(t.GetLength())
    data={'status':'DRAFT - not released','silk_leaders':leaders,'silk_revision':'A5-R3','silk_text_sizes_mm':[[.5,.8,.1],[.4,.6,.1]],'logo':logo,'silk_refs_visible':placements,'silk_refs_hidden':hidden,'track_mm':{n:round(v,3) for n,v in lengths.items()},'vias':vias}
    Path(report_path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
