# -*- coding: utf-8 -*-
import json,csv,shutil,zipfile,hashlib
from pathlib import Path
from openpyxl import Workbook,load_workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
root=Path(__file__).resolve().parents[2]; out=root/'manufacturing/jlc/bom_match_20261003'; out.mkdir(exist_ok=True)
cat=json.loads((out/'catalog_evidence.json').read_text())
rows=list(csv.DictReader(open(root/'manufacturing/jlc/jlcpcb/jlc_parts_map.csv',encoding='utf-8-sig')))
ids={r['lcsc'] for r in rows}|{'C485357','C189897','C385125','C263995'}
ev={c:{'url':f'https://www.lcsc.com/product-detail/{c}.html','checked_date':'2026-10-03',**cat[c]} for c in sorted(ids)}
(out/'catalog_evidence.json').write_text(json.dumps(ev,ensure_ascii=False,indent=2))
wb=Workbook(); sm=wb.active;sm.title='요약'
for row in [ ['HMT500 LCSC–BOM 매칭','2026-10-03'],['기준','회로 v0.10 / PCB A5-R1 / 기구 Rev I'],['실장 BOM','61행 / 108개 / 고유 LCSC 59종'],['검증 범위','LCSC 공식 카탈로그 품번·사양·패키지 대조. 모든 부품 데이터시트를 재검증한 것은 아님.'],['C4 정정','C1532 → C318579. 기존 삼성 CL05B223KO5NNNC에 번호를 맞춤.'],['C61 대체','YAGEO CC0805KKX7R9BB225 / C125847. 2.2µF 50V X7R ±10% 0805.'],['C61 높이','최대 1.45 mm 반영; 배치 모델 허용 높이 3.58 mm. DC 바이어스 실효 용량 확인 필요.'],['R9/R52 보완','0402WGF2212TCE / C43473'],['C22/R19 표시','기채택 부품에 맞춰 C22 ±2%, R19 ±0.1%·25ppm으로 회로도/BOM 정정.'],['하네스','별도 시트 4종 매칭. 센서·M12·전선·링 단자 등은 실제 구매품 확정 필요.'],['재고·조립','LCSC 등록은 JLC 실장 가능/재고 확보를 보증하지 않음. JLC 등급은 기존 기록이며 주문 시 확인.'],['검사','재생성: 81/81 넷 일치, DRC 오류 0, 미연결 0, 33 tests OK. 기존 라이브러리 경고 2개.'],['발주 상태','DFM·CPL 방향·온도/EMC 시험 등 기존 미결 유지. 주문 실행 없음.'] ]:sm.append(row)
headers=['참조번호','수량/대','회로 값','제조사','구매 품번','LCSC 번호','PCB 풋프린트','카탈로그 패키지','카탈로그 사양','대조 결과','메모','LCSC 링크','JLC 구분(주문시 재확인)']
ws=wb.create_sheet('PCB 매칭');ws.append(headers);export=[]
for r in rows:
 d=cat[r['lcsc']];props={p['name']:p['value'] for p in d['additionalProperty']}
 exact=r['mpn']==d['mpn']; assert exact or (r['mpn'] in ['ERA-3AEB4021V','ERA-3AEB153V'] and r['mpn'].replace('-','')==d['mpn'])
 note=r['note']
 if not exact:note+='; LCSC 표기는 '+d['mpn']+' (하이픈 차이)'
 if r['refs']=='U5':note+='; 카탈로그 제조사 ams, 현재 BOM ScioSense. 동일 품번; 제조 라벨/로트 확인 필요.'
 if r['refs']=='D3':note+='; SOD-123W 구매품 / SOD-123F 랜드: 기존 설계 유지, 실장 미리보기 확인.'
 if r['refs']=='L1':note+='; 전용 권선 핀/랜드 대조는 결정 #42 이전 검토 참조.'
 vals=[r['refs'],int(r['qty']),r['value'],r['mfr'],r['mpn'],r['lcsc'],r['footprint'],props.get('Package',''),d['description'],'품번·카탈로그 패키지 대조',note,ev[r['lcsc']]['url'],r['jlc_type'] or '확인 필요']
 ws.append(vals);export.append(vals)
for i in range(2,ws.max_row+1):ws.cell(i,12).hyperlink=ws.cell(i,12).value;ws.cell(i,12).style='Hyperlink'
h=wb.create_sheet('하네스 별도구매');h.append(['하네스','수량/대','품번','LCSC','카탈로그 사양','링크'])
for ref,qty,c in [('W-2 housing',1,'C485357'),('W-2 contact',8,'C189897'),('W-1 housing',1,'C385125'),('W-1 contact',4,'C263995')]:
 d=cat[c];h.append([ref,qty,d['mpn'],c,d['description'],ev[c]['url']]);h.cell(h.max_row,6).hyperlink=ev[c]['url']
for sh in wb:
 sh.freeze_panes='A2';sh.auto_filter.ref=sh.dimensions
 for c in sh[1]:c.font=Font(color='FFFFFF',bold=True);c.fill=PatternFill('solid',fgColor='17365D')
 for row in sh.iter_rows(min_row=2):
  for c in row:c.alignment=Alignment(vertical='top',wrap_text=True)
  sh.row_dimensions[row[0].row].height=58 if sh==ws else 44
 widths=([22,115] if sh==sm else [30,10,25,20,31,18,43,30,65,29,72,65,27] if sh==ws else [23,12,28,16,70,65])
 for n,w in enumerate(widths,1):sh.column_dimensions[get_column_letter(n)].width=w
 sh.sheet_properties.pageSetUpPr.fitToPage=True;sh.page_setup.orientation='landscape';sh.page_setup.paperSize=sh.PAPERSIZE_A3;sh.page_setup.fitToWidth=1;sh.page_setup.fitToHeight=0
wb.save(out/'HMT500_LCSC_BOM_매칭.xlsx')
with open(out/'HMT500_LCSC_BOM_매칭.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(headers);w.writerows(export)
for name in ['HMT500(260313A)_BOM_JLC.csv','HMT500(260313A)_CPL_JLC.csv','jlc_parts_map.csv']:shutil.copy2(root/'manufacturing/jlc/jlcpcb'/name,out/name)
with open(out/'HMT500(260313A)_CPL_JLC.csv',encoding='utf-8-sig') as f:cp=list(csv.DictReader(f))
refs=[x for r in rows for x in r['refs'].split()];assert len(refs)==len(set(refs))==len(cp)==108;assert set(refs)=={r['Designator'] for r in cp}
assert len(rows)==61 and all(r['lcsc'] for r in rows)
book=load_workbook(out/'HMT500_LCSC_BOM_매칭.xlsx');assert book['PCB 매칭'].max_row==62
print('Verified 61 rows, 108 unique references/CPL, 59 unique LCSC + 4 harness codes; XLSX re-open OK')
