from PIL import Image
import numpy as np,json
from shapely.geometry import box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
from pathlib import Path
HERE=Path(__file__).resolve().parent
im=Image.open(HERE/'dotech_logo_source.png');a=np.array(im)[:104,:,3]>128
runs=[]
for y,row in enumerate(a):
 edges=np.diff(np.r_[False,row,False].astype(int));starts=np.where(edges==1)[0];ends=np.where(edges==-1)[0]
 runs.extend(box(int(x),y,int(e),y+1) for x,e in zip(starts,ends))
g=unary_union(runs).simplify(.65,preserve_topology=True);x0,y0,x1,y1=g.bounds
tri=[]
for poly in g.geoms:
 for t in constrained_delaunay_triangles(poly).geoms:
  if t.area>0:tri.append([[(x-x0)/(x1-x0),(y-y0)/(x1-x0)] for x,y in list(t.exterior.coords)[:-1]])
open(HERE/'dotech_wordmark.json','w').write(json.dumps({'source':'dotech_logo_source.png alpha channel, wordmark only (tagline omitted for silk legibility)','aspect':(y1-y0)/(x1-x0),'polygons':[{'outer':[[(x-x0)/(x1-x0),(y-y0)/(x1-x0)] for x,y in list(poly.exterior.coords)[:-1]],'holes':[[[(x-x0)/(x1-x0),(y-y0)/(x1-x0)] for x,y in list(h.coords)[:-1]] for h in poly.interiors]} for poly in g.geoms],'legacy_triangle_count':len(tri)}))
print(len(tri),g.bounds)
