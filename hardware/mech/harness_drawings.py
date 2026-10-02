"""W-1/W-2/W-3 하네스 검토도. 전기/기구 사양 변경 없이 공통 길이를 사용한다."""
import argparse, sys, json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
sys.path.insert(0,str(Path(__file__).resolve().parent))
import hmt500_params as P
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'hardware/mech/out/harness');parser.add_argument('--font-dir',type=Path,default=Path.home()/'Library/Fonts');a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True)
for name,file in [('KR','NanumGothic-Regular.ttf'),('KRB','NanumGothic-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,str(a.font_dir/file)))
DATA=[dict(id='W-1',title='센서 하네스',length=f"{P.HARNESS['length']:g} ±2 mm",left='HTX99R-SC 뒤 납땜 핀',right='JST SHR-04V-S → PCB J3',pins=['SENS_C1 / MK33 전극 1','SENS_C2 / MK33 전극 2','PT_P / Pt1000','PT_N / Pt1000'],wire='4심 · AWG30 · PTFE (현 설계: UL1213 계열)',bom=[('전선','PTFE AWG30','4가닥; 선색 확인 필요'),('플러그 하우징','JST SHR-04V-S','1개'),('압착 콘택트','JST SSH-003T-P0.2-H','4개'),('맞물리는 PCB 헤더','JST SM04B-SRSS-TB (J3)','PCB 장착품; 하네스 BOM 제외'),('납땜부 절연','개별 수축튜브','4개; 규격·절단 길이 확인 필요')],notes=['HTX99R 뒤 핀 납땜 → 바디 통로·홀더 창 통과 → J3에 삽입.', '커넥터 체결 중 플러그 끝은 자유롭게 두어 전선 꼬임을 방지.', '실제 HTX99R 핀 번호·보는 방향과 대조 후 핀맵 승인.']),dict(id='W-2',title='M12 전원·통신·출력 하네스',length=f"{P.HARNESS2['length']:g} ±2 mm",left='M12 8P 뒤 납땜 단자',right='JST GHR-08V-S → PCB J1',pins=['예비 / PCB NC','RS485_B_EXT','RS485_A_EXT','OUT1_EXT','OUT2_EXT','GND_IN','예비 / PCB NC','VIN_EXT / 전원 +'],wire='8심 · AWG28 · PTFE (현 설계: UL1213 계열)',bom=[('전선','PTFE AWG28','8가닥; 선색 확인 필요'),('플러그 하우징','JST GHR-08V-S','1개'),('압착 콘택트','JST SSHL-002T-P0.2','8개'),('맞물리는 PCB 헤더','JST SM08B-GHS-TB (J1)','PCB 장착품; 하네스 BOM 제외'),('M12·납땜부 절연','M12 품번 및 수축튜브','품번·치수·절단 길이 확인 필요')],notes=['핀 n ↔ 핀 n 직결. 1·7번도 현 8심 하네스에 포함되며 PCB에서는 NC.', '밀대로 J1에 삽입할 길이와 턴버클 체결 후 여유선 수납 공간을 함께 확보.', '실제 M12 단자·수축튜브 확인 전 길이 축소 금지. 단자 정면/배선면 혼동 주의.']),dict(id='W-3',title='샤시 접지 하네스',length=f"{P.CHASSIS_WIRE['length']:g} mm / 공차 확인 필요",left='PCB J5.1 납땜',right='M2 비절연 링 단자 → 바디',pins=['CHASSIS'],wire='1심 · AWG28 · PTFE · 녹/황 또는 녹색 (최종 색 확인)',bom=[('전선','PTFE AWG28','1가닥'),('링 단자','M2 비절연, AWG28 대응','1개; 제조사 품번 확인 필요'),('링 단자 외형 조건','바깥 Ø4.5 이하 / 두께 0.8 이하','현 기구 설계 조건'),('체결 위치','홀더 위쪽 축 나사 M2×8','금속 바디 탭과 전기 접촉'),('PCB 접속','J5.1 납땜','신호 GND_IN과 혼동 금지')],notes=['J5 납땜 → 홀더 위쪽 축 나사의 링 단자 → 금속 바디.', '드라이버 접근 경로와 센서 하네스 창을 침범하지 않도록 수납.', '링 중심 기준 완성 길이와 전선 절단 길이는 서로 다름. 단자 확정 후 치수화.'])]
# Verify logical connector nets against generated placement, including intentionally NC pins.
pl=json.loads((ROOT/'hardware/kicad/HMT500(260313A)/placement.json').read_text());parts={p['ref']:p for p in pl['parts']}
for ref,expected in [('J3',{'1':'SENS_C1','2':'SENS_C2','3':'PT_P','4':'PT_N'}),('J1',{'2':'RS485_B_EXT','3':'RS485_A_EXT','4':'OUT1_EXT','5':'OUT2_EXT','6':'GND_IN','8':'VIN_EXT'}),('J5',{'1':'CHASSIS'})]:
 actual={p['n']:p['net'] for p in parts[ref]['pads']}
 assert all(actual[k]==v for k,v in expected.items()),(ref,actual)
def draw(c,d,page):
 def text(x,y,s,size=10,bold=False,color='#182c3d'):
  c.setFillColor(HexColor(color));c.setFont('KRB' if bold else 'KR',size);c.drawString(x*mm,y*mm,s)
 def line(x,y,xx,yy):c.setStrokeColor(HexColor('#294557'));c.setLineWidth(.25*mm);c.line(x*mm,y*mm,xx*mm,yy*mm)
 c.setStrokeColor(HexColor('#294557'));c.rect(10*mm,10*mm,400*mm,277*mm)
 text(18,274,f"HMT500  |  {d['id']} {d['title']}",20,True)
 text(18,263,'제작 검토용 · Rev A · 기구 Rev I / PCB A5-R1 기준 · 2026-10-02',10)
 text(18,253,'길이 기준·탈피·압착 조건 미확정 — 양산 제작 승인 도면 아님',11,True,'#b34816')
 text(18,239,'① 전기 연결 개략도 (핀 배열도 아님 / 축척 없음)',12,True)
 text(25,226,d['left'],11,True);text(238,226,d['right'],11,True)
 n=len(d['pins']);step=7 if n>4 else 12;top=211;bottom=top-(n-1)*step
 for i,pin in enumerate(d['pins'],1):
  y=top-(i-1)*step
  c.setStrokeColor(HexColor('#294557'));c.rect(35*mm,(y-2)*mm,8*mm,4*mm);c.rect(271*mm,(y-2)*mm,8*mm,4*mm)
  line(43,y,271,y);text(27,y-1,str(i),9);text(282,y-1,str(i) if n>1 else 'M2',9)
  c.setFillColor(HexColor('#ffffff'));c.rect(100*mm,(y-2.2)*mm,pdfmetrics.stringWidth(pin,'KR',9)+6*mm,5*mm,stroke=0,fill=1);text(103,y-1,pin,9)
 text(304,211,'배선 사양',11,True)
 # Fixed wrapping to avoid overly long text.
 for j,s in enumerate(d['wire'].split(' · ')):text(304,202-j*7,s,9)
 text(304,171,'기준 설계 길이 Lref',10,True);text(304,162,d['length'],10,True)
 text(304,153,'절단/완성 길이 기준: 확인 필요',9)
 text(25,148,'양단 숫자는 전기적 핀 번호입니다. 실제 커넥터 핀 위치·래치·키 방향을 나타내지 않습니다.',9)
 line(18,142,402,142)
 text(18,132,'② 구성품',12,True)
 yy=123
 for label,part,qty in d['bom']:
  text(20,yy,label,9);text(66,yy,part,9);text(163,yy,qty,9);yy-=8
 text(286,132,'③ 제작 치수 확정 항목',12,True)
 for j,s in enumerate(['Lcut: 전선 절단 길이 — 확인 필요','Lassy: 완성 길이 및 측정 기준점 — 확인 필요','양단 탈피·납땜 길이 — 확인 필요','압착 높이·폭·인장 기준 — 확인 필요','선색·수축튜브 규격 — 확인 필요']):text(287,123-j*8,s,9)
 line(18,78,402,78);text(18,68,'④ 조립·검사 주기',12,True)
 for j,s in enumerate(d['notes']):text(20,59-j*8,s,10)
 text(20,34,'전수 핀맵 도통·인접선 단락·단자 잠금·납땜부 절연을 확인. 시험 수치와 공구 조건은 해당 단자 사양 확정 후 기입.',9)
 line(10,27,410,27);text(18,17,f"도면번호 HMT500-W-{page:03d}  |  Rev A  |  단위 mm  |  A3 / NTS",10,True);text(315,17,f"{page}/3  ·  작성: 설계 검토",9)
 c.showPage()
combined=canvas.Canvas(str(a.output/'HMT500_하네스도면_RevA.pdf'),pagesize=(420*mm,297*mm));combined.setTitle('HMT500 하네스 W-1 W-2 W-3 제작 검토도 Rev A')
for i,d in enumerate(DATA,1):
 single=canvas.Canvas(str(a.output/f"HMT500_{d['id']}_RevA.pdf"),pagesize=(420*mm,297*mm));draw(single,d,i);single.save();draw(combined,d,i)
combined.save();(a.output/'하네스_사양.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2))
print(a.output)
