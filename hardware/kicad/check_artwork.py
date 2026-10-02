"""PCB 실제 패드–넷을 생성기와 비교하고 라우팅 검수용 수치를 기록."""
import json,sys,os
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
    expected_layers=6 if os.environ.get('HMT_ARTWORK','A3')=='A3' else 4
    if b.GetCopperLayerCount()!=expected_layers:errors.append(f'expected {expected_layers} copper layers')
    layers={};nets={};vias=0
    for tr in b.GetTracks():
        if isinstance(tr,p.PCB_VIA):vias+=1;continue
        layer=b.GetLayerName(tr.GetLayer()); layers[layer]=layers.get(layer,0)+1
        net=tr.GetNetname();nets[net]=nets.get(net,0)+p.ToMM(tr.GetLength())
    for ground_layer in (('In1.Cu','In4.Cu') if b.GetCopperLayerCount()==6 else ('In1.Cu',)):
        if layers.get(ground_layer,0):errors.append('signal tracks found on reserved '+ground_layer+' ground plane')
    critical_limits = {} if os.environ.get('HMT_ARTWORK','A3') not in ('A2','A3') else {
        'CREF_A':3.0, 'CREF_B':3.0, 'BUCK_SW':6.0, 'BUCK_FB':4.0,
        'VAO_SW':6.0, 'VAO_FB':4.0, 'DAC1_CMP':6.0, 'DAC2_CMP':6.0,
    }
    # Board-specific layout acceptance limits, not IC electrical ratings.
    # Connectivity and clearance still require the independent KiCad DRC.
    critical_errors=[f'{n}: {nets.get(n,0):.2f} mm exceeds {limit:.2f} mm'
                     for n,limit in critical_limits.items() if nets.get(n,0)>limit]
    data={'copper_layers':b.GetCopperLayerCount(),'critical_track_limit_mm':critical_limits,'critical_track_errors':critical_errors,'pad_net_errors':errors,'layer_tracks':layers,'via_count':vias,'net_total_track_mm':{k:round(v,2) for k,v in nets.items()}}
    return data

if __name__=='__main__':
    import wx
    app=wx.GetApp() or wx.App(False)
    b=p.LoadBoard(str(BASE)+'.kicad_pcb');data=check(b)
    Path(str(BASE.parent/'artwork_check.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(data,ensure_ascii=False));sys.exit(bool(data['pad_net_errors'] or data['critical_track_errors']))
