"""참고 이미지와 같은 흑백 외형·치수선 형식. 구매품 미확정 모델 검토도."""
import sys,argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
sys.path.insert(0,str(Path(__file__).resolve().parent))
import hmt500_params as P
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'hardware/mech/out/m12');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
for n,f in [('KR','NanumGothic-Regular.ttf'),('KRB','NanumGothic-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(Path.home()/'Library/Fonts'/f)))
c=canvas.Canvas(str(a.output/'HMT500_M12_외형도_RevB.pdf'),pagesize=(420*mm,297*mm));c.setTitle('HMT500 M12 외형도 Rev B — 선정 검토용')
def text(x,y,s,size=12,b=False):c.setFont('KRB'if b else'KR',size);c.drawString(x*mm,y*mm,s)
def line(x,y,xx,yy,w=.22):c.setLineWidth(w*mm);c.line(x*mm,y*mm,xx*mm,yy*mm)
def arrow(x,y,dx,dy):
 # filled arrow, pointing toward x,y
 norm=(dx*dx+dy*dy)**.5;dx/=norm;dy/=norm
 q=c.beginPath();q.moveTo(x*mm,y*mm);q.lineTo((x-dx*3-dy*.7)*mm,(y-dy*3+dx*.7)*mm);q.lineTo((x-dx*3+dy*.7)*mm,(y-dy*3-dx*.7)*mm);q.close();c.drawPath(q,fill=1,stroke=0)
def leader(points):
 for u,v in zip(points,points[1:]):line(*u,*v)
 u,v=points[-2:];arrow(*v,v[0]-u[0],v[1]-u[1])
def rect(x,y,w,h):c.setLineWidth(.4*mm);c.rect(x*mm,y*mm,w*mm,h*mm)
C=P.CONNECTOR;S=4;front=120;cy=155
l12=C['thread']['x'][1]-C['thread']['x'][0];shoulder=C['body']['x'][1]-C['body']['x'][0];inner=C['inner']['x'][1]-C['inner']['x'][0]
x1=front+l12*S;x2=x1+shoulder*S;x3=x2+inner*S
text(18,277,'HMT500  M12 8핀 커넥터 외형도',21,True);text(18,266,'HMT500-P-204 / Rev B / 2026-10-02 / 기구 Rev I 기준',10)
# Threads conventional simplified profile, not manufacturing thread detail.
def threaded(xa,xb,r,pitch):
 rect(xa,cy-r*S,xb-xa,2*r*S)
 line(xa,cy-(r-.5)*S,xb,cy-(r-.5)*S,.15);line(xa,cy+(r-.5)*S,xb,cy+(r-.5)*S,.15)
 xx=xa+.5
 while xx<xb-1:
  line(xx,cy-r*S,xx+1.6,cy-(r-.5)*S,.22);line(xx,cy+r*S,xx+1.6,cy+(r-.5)*S,.22);xx+=pitch*S
threaded(front,x1,6,1)
rect(x1,cy-C['body']['d']/2*S,x2-x1,C['body']['d']*S)
threaded(x2,x3,8,1.5)
# Mounting datum, no unconfirmed gasket thickness or locknut is dimensioned.
c.setDash(3*mm,1*mm);line(108,cy,x3+4,cy,.15);line(x2,107,x2,202,.15);c.setDash()
# Overall/shoulder/thread lengths with shared left datum like manufacturer drawing.
for end,y,label in [(x3,242,f'{l12+shoulder+inner:g} REF'),(x2,225,f'{l12+shoulder:g} REF'),(x1,208,f'{l12:g} REF')]:
 line(front,181,front,y+4,.15);line(end,cy+(10 if end==x1 or end==x2 else 8)*S+2,end,y+4,.15)
 line(front-10,y,end+10,y);arrow(front,y,1,0);arrow(end,y,-1,0);text(62,y-1.5,label,15)
# Wire fan, eight insulated lines, stripped-end lengths not yet specified.
for i in range(8):
 sy=cy+(i-3.5)*2.2;ey=cy+(i-3.5)*7.2
 for dd in (-.65,.65):
  q=c.beginPath();q.moveTo(x3*mm,(sy+dd)*mm);q.curveTo((x3+16)*mm,(sy+dd)*mm,246*mm,(ey+dd)*mm,264*mm,(ey+dd)*mm);q.lineTo(322*mm,(ey+dd)*mm);c.setLineWidth(.28*mm);c.drawPath(q)
 # stripped end shown symbolically, not dimensioned to source screenshot's 7 mm
 line(322,ey,333,ey,.4)
text(272,197,'8芯 / AWG28 PTFE'.replace('芯','심'),11)
line(322,185,322,213,.15);line(333,185,333,213,.15);line(314,208,341,208);arrow(322,208,1,0);arrow(333,208,-1,0)
text(300,219,'탈피 길이: 확인 필요',10)
line(x3,123,x3,100,.15);line(333,123,333,100,.15);line(x3,105,333,105);arrow(x3,105,-1,0);arrow(333,105,1,0)
text(246,109,'(L) — 측정 기준 확인 필요',11)
text(244,93,f"W-2 현재 설계 길이: {P.HARNESS2['length']:g} ±2 mm",11,True)
text(244,84,'최종 반대쪽 단말: JST GHR-08V-S',10)
text(244,76,'그림의 노출선은 끝단 표현이며 완성품 형상이 아님',9)
text(79,83,'M12×1',16);leader([(108,88),(139,135)])
text(159,69,'M16×1.5',16);leader([(190,76),(193,125)])
text(45,108,'Ø20 이하',15);leader([(82,112),(111,112),(x1+8,117)])
text(42,58,'A: 장착 기준면',11);leader([(93,62),(124,62),(x2,110)])
text(165,49,f'안쪽 나사부 {inner:g} 이하',12,True)
line(x2,115,x2,87,.15);line(x3,121,x3,87,.15);line(x2,90,x3,90);arrow(x2,90,-1,0);arrow(x3,90,1,0)
text(187,94,f'{inner:g} MAX',10)
# compact notes/title strip
line(15,39,405,39)
text(18,31,'주기: REF는 현 모델 참고치수. 실제 공급사 외형·가스켓·공구 맞변·핀 방향은 품번 확정 후 반영.',10)
text(18,23,'A-coded / 8핀 / Male. TURCK 참고 제품의 4핀 T코딩·25.8 mm·탈피 7 mm 치수는 적용하지 않음.',10)
text(18,13,'단위 mm / NTS / 선정 검토용 — 제조 승인 아님',10,True);text(316,13,'HMT500-P-204-OD / B',10,True)
c.showPage();c.save();print(a.output/'HMT500_M12_외형도_RevB.pdf')
