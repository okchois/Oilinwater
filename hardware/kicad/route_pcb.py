"""재현 가능한 아트워크 준비/SES 반영. KiCad pcbnew Python으로 실행.

prepare: 배치 PCB에 GND/RTN 동박과 내층 금지 영역을 생성하고 DSN 내보내기.
import: 동일 배치에 해당하는 로컬 라우터 SES를 반영하고 동박 재채움.
"""
import argparse
import json
from pathlib import Path
import pcbnew as p
import wx

HERE=Path(__file__).resolve().parent
BASE=HERE/'HMT500(260313A)'/'HMT500(260313A)'
MM=p.FromMM

def rect(b, layer, xy, net=None, keepout=False, name=''):
    z=p.ZONE(b); z.SetLayer(layer); z.SetZoneName(name)
    if keepout:
        z.SetIsRuleArea(True)
        z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(False) # RTN through-vias retain antipads on plane layers
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
    else:
        z.SetNet(b.FindNet(net)); z.SetLocalClearance(MM(.3))
        z.SetPadConnection(p.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(MM(.25)); z.SetThermalReliefSpokeWidth(MM(.25))
        z.SetMinThickness(MM(.15))
    outline=z.Outline(); outline.NewOutline()
    x0,y0,x1,y1=xy
    for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:outline.Append(MM(x),MM(y))
    b.Add(z)
    return z

def prepare(b,dsn):
    for z in list(b.Zones()):
        if z.GetZoneName() in ('RTN dedicated island','RTN isolation under U1','GND'):b.RemoveNative(z)
    # In1 = continuous ground reference; In2 = power/slow signals.
    b.SetLayerType(p.In1_Cu,p.LT_POWER); b.SetLayerType(p.In2_Cu,p.LT_SIGNAL)
    fps={f.GetReference():f for f in b.GetFootprints()}
    ep=max((pd for pd in fps['U1'].Pads() if pd.GetNumber()=='17'),key=lambda pd:pd.GetSize().x*pd.GetSize().y)
    x,y=p.ToMM(ep.GetPosition().x),p.ToMM(ep.GetPosition().y)
    # A local return island around the exposed pad. Isolation verified by DRC.
    rt=(x-2.2,y-3.0,x+2.2,y+3.0)
    for layer in (p.F_Cu,p.B_Cu):
        z=rect(b,layer,rt,'EF_RTN',name='RTN dedicated island'); z.SetAssignedPriority(5)
    for layer in (p.In1_Cu,p.In2_Cu):
        rect(b,layer,(rt[0]-.3,rt[1]-.3,rt[2]+.3,rt[3]+.3),keepout=True,name='RTN isolation under U1')
    for layer in (p.F_Cu,p.In1_Cu,p.B_Cu):
        rect(b,layer,(99,88,157.5,112),'GND',name='GND')
    p.ZONE_FILLER(b).Fill(b.Zones())
    p.SaveBoard(str(BASE)+'.kicad_pcb',b,True)
    # Outer GND fills must be rebuilt around tracks after routing, not imported as fixed obstacles.
    for z in list(b.Zones()):
        if not z.GetIsRuleArea() and z.GetLayer()!=p.In1_Cu: b.RemoveNative(z)
    b.SetLayerType(p.In1_Cu,p.LT_POWER)
    if not p.ExportSpecctraDSN(b,str(dsn)):raise RuntimeError('DSN export failed')
    # Pad pitch constrains RTN-to-adjacent control pins to .25; GND isolation stays .30.
    Path(str(BASE)+'.kicad_dru').write_text("""(version 1)
(rule "RTN to system GND isolation"
 (condition "(A.NetName == 'EF_RTN' && B.NetName == 'GND') || (A.NetName == 'GND' && B.NetName == 'EF_RTN')")
 (constraint clearance (min 0.3mm)))
""")
    data=dsn.read_text()
    data=data.replace('(boundary', '(autoroute_settings (fanout off) (autoroute on) (postroute off) (layer_rule In1.Cu (active off)))\n    (boundary',1)
    dsn.write_text(data)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['prepare','import']);ap.add_argument('file',type=Path)
    a=ap.parse_args(); app=wx.GetApp() or wx.App(False)
    if a.mode=='prepare':
        pro_path=Path(str(BASE)+'.kicad_pro'); pro=json.loads(pro_path.read_text())
        ns=pro['net_settings']; default=next(c for c in ns['classes'] if c['name']=='Default')
        groups={
          'GROUND': (.20,.15,['GND']),
          'POWER': (.35,.15,['VIN_EXT','VIN_L','VIN_F','VIN_D','VIN_P','GND_IN','VAO','+5V']),
          'SWITCH': (.35,.15,['BUCK_SW','VAO_SW']),
          'ANALOG': (.20,.15,['DAC1_OUT','DAC2_OUT','OUT1_P','OUT2_P','OUT1_EXT','OUT2_EXT','SENS_C1','SENS_C2','CREF_A','CREF_B','PT_P','PT_N','PT_SP_F','PT_SN_F']),
          'RTN': (.25,.25,['EF_RTN']),
        }
        ns['classes']=[c for c in ns['classes'] if c['name'] not in groups]
        ns['netclass_patterns']=[q for q in ns.get('netclass_patterns',[]) if q['netclass'] not in groups]
        for name,(width,clearance,nets) in groups.items():
            ns['classes'].append(dict(default,name=name,track_width=width,clearance=clearance))
            ns['netclass_patterns'] += [dict(netclass=name,pattern=n) for n in nets]
        pro_path.write_text(json.dumps(pro,indent=2)+'\n')
    b=p.LoadBoard(str(BASE)+'.kicad_pcb')
    if a.mode=='prepare':prepare(b,a.file)
    else:
        if not p.ImportSpecctraSES(b,str(a.file)):raise RuntimeError('SES import failed')
        from artwork_finish import finish
        finish(b,BASE.parent/'artwork_metrics.json')
        p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(BASE)+'.kicad_pcb',b,True)
if __name__=='__main__':main()
