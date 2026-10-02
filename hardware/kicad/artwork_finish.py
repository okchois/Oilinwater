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
    b.GetTitleBlock().SetRevision(os.environ.get("HMT_ARTWORK","A5")+"-R1")
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
    # Preserve all assembly labels on Fab; fit only unambiguous readable silk labels.
    pads={layer:[] for layer in (p.F_SilkS,p.B_SilkS)}
    for fp in fps:
        for pad in fp.Pads():
            for silk,mask in ((p.F_SilkS,p.F_Mask),(p.B_SilkS,p.B_Mask)):
                if pad.IsOnLayer(mask):pads[silk].append(bbox(pad,.18))
    shapes={layer:[] for layer in pads}
    for fp in fps:
        for g in fp.GraphicalItems():
            if g.GetLayer() in shapes:
                if isinstance(g,p.PCB_SHAPE) and g.GetShape()==p.S_RECT:
                    x0,y0,x1,y1=bbox(g)
                    m=.05
                    shapes[g.GetLayer()].extend([(x0-m,y0-m,x1+m,y0+m),(x0-m,y1-m,x1+m,y1+m),(x0-m,y0-m,x0+m,y1+m),(x1-m,y0-m,x1+m,y1+m)])
                else:shapes[g.GetLayer()].append(bbox(g,.05))
    outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline,False)
    # R1: local, ownership-aware silk. Never use distant whitespace for a ref.
    def body(fp):
        items=list(fp.Pads())
        boxes=[bbox(q) for q in items]
        if not boxes:return bbox(fp)
        return (min(q[0] for q in boxes),min(q[1] for q in boxes),max(q[2] for q in boxes),max(q[3] for q in boxes))
    bodies={fp.GetReference():body(fp) for fp in fps}
    def distance(x,y,q):return math.hypot(max(q[0]-x,0,x-q[2]),max(q[1]-y,0,y-q[3]))
    options={};placements={};hidden=[]
    for fp in fps:
        name=fp.GetReference();ref=fp.Reference();layer=p.B_SilkS if fp.IsFlipped() else p.F_SilkS
        ref.SetLayer(layer);ref.SetTextSize(p.VECTOR2I(MM(.6),MM(.8)));ref.SetTextThickness(MM(.12))
        ref.SetVisible(True)
        origin=fp.GetPosition();x,y=p.ToMM(origin.x),p.ToMM(origin.y);own=bodies[name]
        candidates=[]
        for angle in (0,90):
            ref.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T))
            for i in range(-20,21):
                for j in range(-20,21):
                    px,py=x+i*.2,y+j*.2
                    gap=distance(px,py,own)
                    if gap>1.35:continue
                    # The intended component must be uniquely closest to the label.
                    if any(distance(px,py,bodies[f.GetReference()])<gap+.12 for f in fps if f!=fp and f.IsFlipped()==fp.IsFlipped()):continue
                    ref.SetPosition(p.VECTOR2I(MM(px),MM(py)));box=bbox(ref,.08)
                    if not all(outline.Contains(p.VECTOR2I(MM(a),MM(c))) for a in (box[0]-.25,box[2]+.25) for c in (box[1]-.25,box[3]+.25)):continue
                    if any(overlap(box,q) for q in pads[layer]+shapes[layer]):continue
                    candidates.append((gap+math.hypot(px-x,py-y)*.05+angle*.0001,px,py,angle,box))
        options[name]=sorted(candidates)
    placed={layer:[] for layer in pads}
    # Most constrained first so large packages do not consume small-component space.
    for fp in sorted(fps,key=lambda f:(len(options[f.GetReference()]),f.GetReference())):
        name=fp.GetReference();ref=fp.Reference();layer=ref.GetLayer()
        for score,x,y,angle,box in options[name]:
            if any(overlap(box,q) for q in placed[layer]):continue
            ref.SetPosition(p.VECTOR2I(MM(x),MM(y)));ref.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));ref.SetVisible(True)
            placed[layer].append(box);placements[name]={'x':x,'y':y,'angle':angle,'body_distance_mm':round(distance(x,y,bodies[name]),3)}
            break
        else:
            ref.SetPosition(fp.GetPosition());ref.SetVisible(False);hidden.append(name)
    # Remaining refs: an explicit short leader identifies the intended body.
    leaders=[]
    for fp in fps:
        name=fp.GetReference()
        if name not in hidden:continue
        ref=fp.Reference();layer=ref.GetLayer();own=bodies[name]
        ox,oy=p.ToMM(fp.GetPosition().x),p.ToMM(fp.GetPosition().y)
        offsets=sorted(((i*.2,j*.2) for i in range(-20,21) for j in range(-20,21)),key=lambda q:math.hypot(*q))
        found=False
        for dx,dy in offsets:
            x,y=ox+dx,oy+dy
            if distance(x,y,own)>2.8:continue
            for angle in (0,90):
                ref.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));ref.SetPosition(p.VECTOR2I(MM(x),MM(y)));ref.SetVisible(True)
                box=bbox(ref,.08)
                if not all(outline.Contains(p.VECTOR2I(MM(a),MM(c))) for a in (box[0]-.25,box[2]+.25) for c in (box[1]-.25,box[3]+.25)):continue
                obstacles=pads[layer]+shapes[layer]+placed[layer]
                if any(overlap(box,q) for q in obstacles):continue
                # Nearest hull point; stop outside the target's mask opening.
                tx=min(max(x,own[0]-.28),own[2]+.28);ty=min(max(y,own[1]-.28),own[3]+.28)
                if math.hypot(tx-x,ty-y)<.1:continue
                ux,uy=tx-x,ty-y
                t=min((abs((box[2]-box[0])/2/ux) if ux else 1e6),(abs((box[3]-box[1])/2/uy) if uy else 1e6))
                if t>=1:continue
                sx,sy=x+ux*t,y+uy*t
                length=math.hypot(tx-sx,ty-sy)
                if length<.15:continue
                samples=max(2,int(length/.04)+1)
                lineboxes=[(sx+(tx-sx)*k/samples-.07,sy+(ty-sy)*k/samples-.07,sx+(tx-sx)*k/samples+.07,sy+(ty-sy)*k/samples+.07) for k in range(samples+1)]
                if any(overlap(q,r) for q in lineboxes for r in obstacles):continue
                line=p.PCB_SHAPE(b);line.SetUuid(p.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,"hmt500/silk-leader/"+name))));line.SetShape(p.S_SEGMENT);line.SetLayer(layer);line.SetWidth(MM(.12));line.SetStart(p.VECTOR2I(MM(sx),MM(sy)));line.SetEnd(p.VECTOR2I(MM(tx),MM(ty)));b.Add(line)
                placed[layer].extend([box]+lineboxes);hidden.remove(name)
                placements[name]={'x':x,'y':y,'angle':angle,'body_distance_mm':round(distance(x,y,own),3),'leader':True}
                leaders.append(name);found=True;break
            if found:break
        if not found:ref.SetVisible(False);ref.SetPosition(fp.GetPosition())
    # Board identification had historically used mechanical coordinates directly.
    for item in b.GetDrawings():
        if isinstance(item,p.PCB_TEXT) and item.GetLayer()==p.B_SilkS:
            item.SetLayer(p.Cmts_User) # artwork ID goes in free space below, original preserved in documentation
    mark=p.PCB_TEXT(b);mark.SetText('HMT500 '+(os.environ.get('HMT_ARTWORK','A5')+'-R1'));mark.SetLayer(p.F_SilkS)
    mark.SetTextSize(p.VECTOR2I(MM(.6),MM(.8)));mark.SetTextThickness(MM(.12))
    mark.SetPosition(p.VECTOR2I(MM(151),MM(100)));b.Add(mark)
    tracks=list(b.GetTracks());lengths={};vias={}
    for t in tracks:
        if isinstance(t,p.PCB_VIA):vias[t.GetNetname()]=vias.get(t.GetNetname(),0)+1
        else:lengths[t.GetNetname()]=lengths.get(t.GetNetname(),0)+p.ToMM(t.GetLength())
    data={'status':'DRAFT - not released','silk_leaders':leaders,'silk_revision':'A5-R1','silk_text_mm':[.6,.8,.12],'silk_refs_visible':placements,'silk_refs_hidden':hidden,'track_mm':{n:round(v,3) for n,v in lengths.items()},'vias':vias}
    Path(report_path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
