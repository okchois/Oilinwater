"""PCB 실제 패드–넷을 생성기와 비교하고 라우팅 검수용 수치를 기록."""
import json,sys
from pathlib import Path
import pcbnew as p
import gen_hmt500 as g

BASE=Path(__file__).resolve().parent/g.PROJECT/g.PROJECT

def check(b):
    expected={(r,pin):n for n,ps in g.intended_nets().items() for r,pin in ps if not r.startswith('#')}
    actual={};errors=[]
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            key=(fp.GetReference(),pad.GetNumber()); net=pad.GetNetname()
            if key in actual and actual[key]!=net:errors.append(f'duplicate pad net {key}')
            actual[key]=net
            if net!=expected.get(key,''):errors.append(f'{key}: expected {expected.get(key,"")}, PCB {net}')
    for key in expected:
        if key not in actual:errors.append(f'missing pad {key}')
    layers={};nets={};vias=0
    for tr in b.GetTracks():
        if isinstance(tr,p.PCB_VIA):vias+=1;continue
        layer=b.GetLayerName(tr.GetLayer()); layers[layer]=layers.get(layer,0)+1
        net=tr.GetNetname();nets[net]=nets.get(net,0)+p.ToMM(tr.GetLength())
    if layers.get('In1.Cu',0):errors.append('signal tracks found on reserved In1.Cu ground plane')
    data={'pad_net_errors':errors,'layer_tracks':layers,'via_count':vias,'net_total_track_mm':{k:round(v,2) for k,v in nets.items()}}
    return data

if __name__=='__main__':
    b=p.LoadBoard(str(BASE)+'.kicad_pcb');data=check(b)
    Path(str(BASE.parent/'artwork_check.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(data,ensure_ascii=False));sys.exit(bool(data['pad_net_errors']))
