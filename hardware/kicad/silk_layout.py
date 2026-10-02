"""A5-R3: 부품 몸체 밖의 가까운 레퍼런스와 원본 DOTECH 벡터 로고."""
import json,math,random,uuid
from pathlib import Path
import pcbnew as p
MM=p.FromMM

def box(q,m=0):
 b=q.GetBoundingBox();return (p.ToMM(b.GetX())-m,p.ToMM(b.GetY())-m,p.ToMM(b.GetRight())+m,p.ToMM(b.GetBottom())+m)
def hit(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def union(bs):return min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs)
def dist(x,y,b):return math.hypot(max(b[0]-x,0,x-b[2]),max(b[1]-y,0,y-b[3]))
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'hmt500/r2/'+s))
def layout(b,fps):
 logo=json.loads((Path(__file__).parent/'assets/dotech_wordmark.json').read_text())
 ids={uid('logo'+str(i)) for i in range(max(logo.get('legacy_triangle_count',0),len(logo['polygons'])))}
 ids|={uid('leader'+f.GetReference()+suffix) for f in fps for suffix in ('','0','1')}
 for group in list(b.Groups()):
  if group.GetName()=="DOTECH full logo":
   for member in list(group.GetItems()):group.RemoveItem(member)
   b.RemoveNative(group)
 for q in list(b.GetDrawings()):
  if q.m_Uuid.AsString() in ids or (isinstance(q,p.PCB_TEXT) and q.GetLayer()==p.F_SilkS and q.GetText().startswith('HMT500')):b.RemoveNative(q)
 layers=(p.F_SilkS,p.B_SilkS);obs={l:[] for l in layers};bodies={};hulls={};sides={}
 for fp in fps:
  name=fp.GetReference();layer=p.B_SilkS if fp.IsFlipped() else p.F_SilkS;sides[name]=layer
  fab=[box(q,.04) for q in fp.GraphicalItems() if isinstance(q,p.PCB_SHAPE) and q.GetLayer()==(p.B_Fab if fp.IsFlipped() else p.F_Fab)]
  pads=[box(q) for q in fp.Pads()]
  bodies[name]=union(fab or pads);hulls[name]=union(pads+[bodies[name]])
  obs[layer].append(bodies[name])
  for pad in fp.Pads():
   for l,mask in ((p.F_SilkS,p.F_Mask),(p.B_SilkS,p.B_Mask)):
    if pad.IsOnLayer(mask):obs[l].append(box(pad,.17))
  for q in fp.GraphicalItems():
   if q.GetLayer() not in obs:continue
   if isinstance(q,p.PCB_SHAPE) and q.GetShape()==p.S_RECT:
    x0,y0,x1,y1=box(q);m=.025
    obs[q.GetLayer()].extend([(x0-m,y0-m,x1+m,y0+m),(x0-m,y1-m,x1+m,y1+m),(x0-m,y0-m,x0+m,y1+m),(x1-m,y0-m,x1+m,y1+m)])
   else:obs[q.GetLayer()].append(box(q,.025))
 outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline,False)
 def inside(q):return all(outline.Contains(p.VECTOR2I(MM(x),MM(y))) for x in (q[0]-.2,q[2]+.2) for y in (q[1]-.2,q[3]+.2))
 # Wordmark occupies the clear top-side area behind J1; reserve before references.
 lx,ly,lw=144.6,96.8,11.5;lh=lw*logo['aspect'];lb=(lx-.15,ly-.15,lx+lw+.15,ly+lh+.15)
 assert inside(lb) and not any(hit(lb,q) for q in obs[p.F_SilkS]),'logo clearance'
 obs[p.F_SilkS].append(lb)
 logo_group=p.PCB_GROUP(b);logo_group.SetName('DOTECH full logo');b.Add(logo_group)
 for i,glyph in enumerate(logo['polygons']):
  poly=p.SHAPE_POLY_SET();poly.NewOutline()
  for x,y in glyph['outer']:poly.Append(int(MM(lx+x*lw)),int(MM(ly+y*lw)),0,-1)
  for hole in glyph['holes']:
   h=poly.NewHole(0)
   for x,y in hole:poly.Append(int(MM(lx+x*lw)),int(MM(ly+y*lw)),0,h)
  poly.Fracture()
  q=p.PCB_SHAPE(b);q.SetUuid(p.KIID(uid('logo'+str(i))));q.SetShape(p.S_POLYGON);q.SetPolyShape(poly);q.SetFilled(True);q.SetWidth(0);q.SetLayer(p.F_SilkS);b.Add(q);logo_group.AddItem(q)
 mark=p.PCB_TEXT(b);mark.SetText('HMT500(ED260313A)\nA5-R3');mark.SetLayer(p.F_SilkS);mark.SetTextSize(p.VECTOR2I(MM(.4),MM(.8)));mark.SetTextThickness(MM(.1));mark.SetPosition(p.VECTOR2I(MM(150.35),MM(102.5)))
 assert inside(box(mark,.1)) and not any(hit(box(mark,.1),q) for q in obs[p.F_SilkS]),'ID clearance'
 obs[p.F_SilkS].append(box(mark,.1));b.Add(mark)
 options={}
 for fp in fps:
  name=fp.GetReference();r=fp.Reference();layer=sides[name];own=hulls[name]
  r.SetLayer(layer);r.SetTextSize(p.VECTOR2I(MM(.5),MM(.8)));r.SetTextThickness(MM(.1));r.SetVisible(True)
  ox,oy=p.ToMM(fp.GetPosition().x),p.ToMM(fp.GetPosition().y)
  near=[q for q in obs[layer] if hit((own[0]-4,own[1]-4,own[2]+4,own[3]+4),q)]
  opts=[]
  for tw,th in ((.5,.8),(.4,.6)):
   r.SetTextSize(p.VECTOR2I(MM(tw),MM(th)))
   for angle in (0,90):
    r.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));r.SetPosition(p.VECTOR2I(0,0));z=box(r,.04);hw=(z[2]-z[0])/2;hh=(z[3]-z[1])/2
    # search beside the actual pad/body hull, including long ICs beyond +/-4mm
    coords=set()
    for k in range(23):
     gap=.20+k*.1
     for j in range(int((own[3]-own[1]+2)*10)+1):
      y=own[1]-1+j*.1
      coords.add((own[0]-hw-gap,y));coords.add((own[2]+hw+gap,y))
     for j in range(int((own[2]-own[0]+2)*10)+1):
      x=own[0]-1+j*.1
      coords.add((x,own[1]-hh-gap));coords.add((x,own[3]+hh+gap))
    for x,y in sorted(coords):
     r.SetPosition(p.VECTOR2I(MM(x),MM(y)));bb=box(r,.04)
     if not inside(bb) or any(hit(bb,q) for q in near):continue
     gap=dist(x,y,own)
     closest=min((dist(x,y,hulls[n]) for n in hulls if n!=name and sides[n]==layer),default=100)
     # Ownership by hull distance. Ambiguous candidates get a short explicit leader.
     line=None;lineboxes=[]
     if closest<gap+.05:
      tx=min(max(x,own[0]-.30),own[2]+.30);ty=min(max(y,own[1]-.30),own[3]+.30)
      dx,dy=tx-x,ty-y
      t=min(hw/abs(dx) if dx else 1e6,hh/abs(dy) if dy else 1e6)
      if t>=1:continue
      sx,sy=x+dx*t,y+dy*t;length=math.hypot(tx-sx,ty-sy)
      if length<.12 or length>2.5:continue
      count=max(2,int(length/.04)+1)
      lineboxes=[(sx+(tx-sx)*k/count-.06,sy+(ty-sy)*k/count-.06,sx+(tx-sx)*k/count+.06,sy+(ty-sy)*k/count+.06) for k in range(count+1)]
      if any(hit(v,q) for v in lineboxes for q in near):
       found=None
       # One elbow can route a short ownership leader around a neighbouring pad.
       for ex,ey in [(own[0]-.30,own[1]-.30),(own[2]+.30,own[1]-.30),(own[0]-.30,own[3]+.30),(own[2]+.30,own[3]+.30)]:
        for bx,by in ((x,ey),(ex,y)):
         dx,dy=bx-x,by-y
         tt=min(hw/abs(dx) if dx else 1e6,hh/abs(dy) if dy else 1e6)
         if tt>=1:continue
         ax,ay=x+dx*tt,y+dy*tt
         points=[(ax,ay),(bx,by),(ex,ey)]
         if sum(math.dist(a,c) for a,c in zip(points,points[1:]))>2.5:continue
         boxes=[]
         for (a,c),(d,e) in zip(points,points[1:]):
          count=max(2,int(math.hypot(d-a,e-c)/.04)+1)
          boxes.extend((a+(d-a)*k/count-.06,c+(e-c)*k/count-.06,a+(d-a)*k/count+.06,c+(e-c)*k/count+.06) for k in range(count+1))
         if any(hit(v,q) for v in boxes for q in near) or any(hit(v,bb) for v in boxes[2:]):continue
         found=(points,boxes);break
        if found:break
       if not found:continue
       line,lineboxes=found
      else:line=[(sx,sy),(tx,ty)]
     score=(.6 if th<.8 else 0)+gap+.04*math.hypot(x-ox,y-oy)+(.4 if line else 0)+angle*.0001
     opts.append((score,x,y,angle,bb,line,lineboxes,(tw,th)))
  options[name]=sorted(opts)
 print('No candidates:',[n for n,o in options.items() if not o],flush=True)
 # Repeated constrained packing: deterministic trials improve crowded groups.
 best={};bestscore=1e9
 for trial in range(45):
  rng=random.Random(5300+trial);chosen={};occupied={l:[] for l in layers}
  order=sorted(options,key=lambda n:(len(options[n])*(1 if not trial else rng.uniform(.55,1.8)),n))
  for name in order:
   for opt in options[name]:
    if any(hit(v,q) for v in [opt[4]]+opt[6] for q in occupied[sides[name]]):continue
    chosen[name]=opt;occupied[sides[name]].extend([opt[4]]+opt[6]);break
  score=sum(v[0] for v in chosen.values())
  if len(chosen)>len(best) or (len(chosen)==len(best) and score<bestscore):best,bestscore=chosen,score
 # Repair greedy dead ends by relocating up to two blocking references.
 compact={}
 for name,opts in options.items():
  seen=set();compact[name]=[]
  for opt in opts:
   key=(round(opt[1]*2),round(opt[2]*2),opt[3],opt[7])
   if key in seen:continue
   seen.add(key);compact[name].append(opt)
 def collides(a,c):return any(hit(v,q) for v in [a[4]]+a[6] for q in [c[4]]+c[6])
 def insert(name,state,depth,locked,budget):
  if budget[0]<=0:return None
  budget[0]-=1
  attempts=[]
  for opt in compact[name]:
   conflicts=[n for n,c in state.items() if sides[n]==sides[name] and collides(opt,c)]
   if any(n in locked for n in conflicts) or len(conflicts)>2:continue
   if not conflicts:return {**state,name:opt}
   if depth:attempts.append((len(conflicts),opt[0],opt,conflicts))
  for _,_,opt,conflicts in sorted(attempts,key=lambda x:x[:2])[:25]:
   trial={n:c for n,c in state.items() if n not in conflicts};trial[name]=opt
   for displaced in conflicts:
    trial=insert(displaced,trial,depth-1,locked|{name},budget)
    if trial is None:break
   if trial is not None:return trial
  return None
 for name in sorted(set(options)-set(best),key=lambda n:len(options[n])):
  if not options[name]:continue
  improved=insert(name,best,2,set(),[300])
  if improved is not None:best=improved
 placements={};hidden=[];leaders=[]
 for fp in fps:
  name=fp.GetReference();r=fp.Reference()
  if name not in best:r.SetVisible(False);r.SetPosition(fp.GetPosition());hidden.append(name);continue
  _,x,y,angle,bb,line,_,size=best[name]
  r.SetTextSize(p.VECTOR2I(MM(size[0]),MM(size[1])))
  r.SetPosition(p.VECTOR2I(MM(x),MM(y)));r.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));r.SetVisible(True)
  placements[name]={'x':x,'y':y,'angle':angle,'body_distance_mm':round(dist(x,y,hulls[name]),3),'text_mm':[size[0],size[1],.1],'leader':bool(line)}
  if line:
   for i,(start,end) in enumerate(zip(line,line[1:])):
    q=p.PCB_SHAPE(b);q.SetUuid(p.KIID(uid('leader'+name+str(i))));q.SetShape(p.S_SEGMENT);q.SetLayer(sides[name]);q.SetWidth(MM(.1));q.SetStart(p.VECTOR2I(MM(start[0]),MM(start[1])));q.SetEnd(p.VECTOR2I(MM(end[0]),MM(end[1])));b.Add(q)
   leaders.append(name)
 print('R2 silk visible',len(placements),'hidden',hidden,flush=True)
 return placements,hidden,leaders,{'position_mm':[lx,ly],'size_mm':[lw,lh],'source':'assets/dotech_logo_source.png','tagline_omitted':False}
