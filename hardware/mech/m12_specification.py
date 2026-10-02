"""HMT500 P-204 M12 선정 사양서. 공통 기구 치수로 검토 외형도 작성."""
import argparse,sys,json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
sys.path.insert(0,str(Path(__file__).resolve().parent))
import hmt500_params as P
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'hardware/mech/out/m12');p.add_argument('--font-dir',type=Path,default=Path.home()/'Library/Fonts');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
for n,f in [('KR','NanumGothic-Regular.ttf'),('KRB','NanumGothic-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(args.font_dir/f)))
out=args.output/'HMT500_M12_외형도포함_선정사양서_RevA.pdf';c=canvas.Canvas(str(out),pagesize=(420*mm,297*mm));c.setTitle('HMT500 M12 외형도 포함 선정 사양서 Rev A')
def t(x,y,s,z=10,b=False,color='#183247'):
 c.setFillColor(HexColor(color));c.setFont('KRB' if b else 'KR',z);c.drawString(x*mm,y*mm,s)
def line(x,y,xx,yy,color='#294557'):
 c.setStrokeColor(HexColor(color));c.setLineWidth(.25*mm);c.line(x*mm,y*mm,xx*mm,yy*mm)
def rect(x,y,w,h,color='#edf3f6'):
 c.setFillColor(HexColor(color));c.setStrokeColor(HexColor('#294557'));c.rect(x*mm,y*mm,w*mm,h*mm,fill=1,stroke=1)
def dim(x1,x2,y,label):
 line(x1,y,x2,y)
 for x in [x1,x2]:line(x-1,y-1,x+1,y+1)
 t((x1+x2)/2-pdfmetrics.stringWidth(label,'KR',9)/mm/2,y+2,label,9)
def page(n,title):
 c.setStrokeColor(HexColor('#294557'));c.rect(10*mm,10*mm,400*mm,277*mm)
 t(18,274,title,19,True);t(18,263,'HMT500-P-204  |  Rev A  |  2026-10-02  |  기구 Rev I / PCB A5-R1',10)
 line(10,26,410,26);t(18,16,'선정·견적 검토용 / 구매품 품번 미확정 / 단위 mm / 축척 없음 (NTS)',9);t(371,16,f'{n} / 2',10)
page(1,'M12 8핀 커넥터 — 외형·장착 조건')
t(18,251,'접속부 M12×1과 장착부 M16×1.5는 서로 다른 나사입니다.',12,True)
# Dimensioned project envelope, x=77 mounting face at drawing X=160.
s=6;face=160;cy=191
X=lambda v:face+(v-77)*s
rect(X(71),cy-8*s,6*s,16*s,'#e5edf1')
rect(X(77),cy-10*s,4*s,20*s,'#d7e6ee')
rect(X(81),cy-6*s,11*s,12*s,'#e5edf1')
# Diagram is positioned below title (top at 251); upper labels go beside it.
for xx in [72,73,74,75,76]:line(X(xx),cy-8*s,X(xx),cy+8*s,'#b1bec7')
for xx in range(82,92):line(X(xx),cy-6*s,X(xx),cy+6*s,'#b1bec7')
c.setDash(2*mm,1*mm);line(85,cy,248,cy);line(face,124,face,254);c.setDash()
t(26,224,'장치 내부',12,True);t(254,224,'장치 외부 / 상대 케이블 접속',12,True)
t(22,210,'장착 수나사: M16×1.5',10,True);line(95,208,X(73),202)
t(257,207,'접속 수나사: M12×1',11,True);line(250,205,X(86),200)
t(257,191,'형식: A-coded / 8핀 / Male',11,True)
t(257,176,'어깨 외경: Ø20 이하',11,True);line(249,176,X(79),cy-50)
t(257,164,'표현된 외형은 현 기구 모델입니다.',9)
t(257,156,'표준이 커넥터 몸체 전체 치수를',9);t(257,150,'정하는 것은 아닙니다.',9)
dim(X(71),X(77),121,'6 이하');dim(X(77),X(81),121,'4*');dim(X(81),X(92),121,'11*')
dim(X(77),X(92),109,'외부 돌출 15*')
t(21,133,'기준면 A: 엔드캡 뒤 끝면 x=77',9);line(104,135,face,145)
t(21,101,'* 4 / 11 / 15는 현재 모델 치수이며 선정품 실측값·표준 치수가 아닙니다.',10,True,'#ad491c')
line(18,94,402,94)
for i,(a,b) in enumerate([('장착 암나사','엔드캡 M16×1.5-6H, 모델 x71–77 (길이 6). 구매품 체결·씰 형상 대조 필요.'),('내부 여유','PCB 뒤끝 x69 → 모델 커넥터 안쪽 끝 x71: 축 방향 2 mm. 납땜 핀·수축튜브 돌출은 별도.'),('공구 공간','어깨 Ø20 조건에서 M3 경사 주입 공구 여유 0.625 mm. 어깨 확대 시 재검사.'),('밀봉·고정','O링/가스켓 형상, 장착 토크, 회전 방지, 체결 유효 길이: 선정품 도면으로 확인 필요.'),('선정 자료','공급사 2D 치수도·STEP·단자 방향도 요청. 안쪽 단자 전체 형상과 외부 돌출 길이를 포함할 것.')]):
 t(20,84-i*11,a,10,True);t(63,84-i*11,b,10)
c.showPage()
page(2,'M12 8핀 커넥터 — 전기·하네스·구매 사양')
t(18,249,'HMT500 핀 배정 (표준 공통 기능 배정이 아닌 본 제품 배정)',12,True)
pins=[('1','예비 / PCB NC'),('2','RS485_B_EXT'),('3','RS485_A_EXT'),('4','OUT1_EXT'),('5','OUT2_EXT'),('6','GND_IN / 전원 −'),('7','예비 / PCB NC'),('8','VIN_EXT / 전원 +')]
pl=json.loads((ROOT/'hardware/kicad/HMT500(ED260313A)/placement.json').read_text());j=next(q for q in pl['parts'] if q['ref']=='J1');nets={p['n']:p['net'] for p in j['pads']}
for k,v in [('2','RS485_B_EXT'),('3','RS485_A_EXT'),('4','OUT1_EXT'),('5','OUT2_EXT'),('6','GND_IN'),('8','VIN_EXT')]:assert nets[k]==v
for i,(num,net) in enumerate(pins):
 y=237-i*10;t(22,y,num,10,True);t(38,y,net,10);t(125,y,'→ J1.'+num,10);line(20,y-3,167,y-3,'#ced9df')
t(181,249,'선정 조건 및 현재 상태',12,True)
rows=[('접속 형식','M12 A-coded, 8핀 수형, 직선, 전면 장착'),('장착 나사','M16×1.5 (PG9·M16×1 등과 혼용 불가)'),('제품 사용 전압','12–28 V DC / 최대 28 V'),('커넥터 정격','30 V DC 이상 적용 여부 확인; 아래 참고품은 30 V'),('허용 전류','선정품·접점별·배선 규격으로 확인 필요'),('방수·온도','제품 요구와 체결 조건 확정 후 검증; 현재 보증 등급 미확정'),('하네스 W-2',f"8심 AWG28 PTFE, 현재 {P.HARNESS2['length']:g}±2 mm, JST GHR-08V-S"),('단자·배선','납땜형 또는 지정 리드선형. 실제 길이·피복·핀별 선색 확인'),('공통 주의','1·7번은 8심에 포함, PCB NC. 샤시는 별도 W-3 연결')]
for i,(a,b) in enumerate(rows):t(181,237-i*9,a,9,True);t(220,237-i*9,b,9)
t(20,142,'핀 배열의 정면/배선면 방향·키 위치는 선정품 제조사 도면을 따릅니다. 본 표를 물리적 핀 위치도로 사용하지 마십시오.',10,True,'#ad491c')
line(18,134,402,134);t(18,124,'제조사 공식 참고품 — 채택품 또는 무수정 호환품으로 승인한 것은 아닙니다.',12,True)
t(20,112,'[1] Phoenix Contact 1436424 · SACC-E-M12MS-8CON-M16/0,5 P',11,True)
t(20,103,'8핀 Male / A-coded / M16×1.5 전면 장착 / 30 V AC·DC / 2 A / 0.25 mm² 리드선 0.5 m.',10)
t(20,94,'현재 W-2의 AWG28·40 mm와 다릅니다. 외형·씰·내부 돌출·JST 압착 적합성을 별도로 확인해야 합니다.',10)
u1='https://www.phoenixcontact.com/en-fr/products/device-connector-front-mounting-sacc-e-m12ms-8con-m16-05-p-1436424'
t(20,85,'제조사 제품 페이지 및 외형도 열기 [1]',9,color='#1665a4');c.linkURL(u1,(20*mm,83*mm,170*mm,90*mm),relative=0)
t(20,72,'[2] binder 76 0831 0011 00008-0200 · M12-A series 763',11,True)
t(20,63,'8핀 Male / M16×1.5 / 30 V / 2 A (UL 1.5 A) / 리드선 AWG24·0.2 m. 현재 W-2와 배선 규격이 다름.',10)
u2='https://www.binder-usa.com/us-en/products/automation-technology/m12-a/76-0831-0011-00008-0200-m12-a-male-panel-mount-connector-8-unshielded-single-wires-ip68-ul-m16x15'
t(20,54,'제조사 제품 페이지·외형도·접속면 핀 배열 열기 [2]',9,color='#1665a4');c.linkURL(u2,(20*mm,52*mm,200*mm,59*mm),relative=0)
t(20,39,'발행 근거: hmt500_params.py / PCB J1 연결 정보 / 제조사 공식 페이지(2026-10-02 확인). 실제 M Connect 품번: 확인 필요.',9)
c.showPage();c.save();print(out)
