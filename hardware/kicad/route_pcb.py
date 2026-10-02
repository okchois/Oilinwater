"""재현 가능한 아트워크 준비/SES 반영. KiCad pcbnew Python으로 실행.

prepare: 배치 PCB에 GND/RTN 동박과 내층 금지 영역을 생성하고 DSN 내보내기.
import: 동일 배치에 해당하는 로컬 라우터 SES를 반영하고 동박 재채움.
"""
import argparse
import json
import os
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
        z.SetNet(b.FindNet(net)); z.SetLocalClearance(MM(.15 if net=='GND' else .3))
        z.SetPadConnection(p.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(MM(.25)); z.SetThermalReliefSpokeWidth(MM(.25))
        z.SetMinThickness(MM(.15))
        if net=='GND':z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
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
    if b.GetCopperLayerCount()==6:
        b.SetLayerType(p.In3_Cu,p.LT_SIGNAL);b.SetLayerType(p.In4_Cu,p.LT_SIGNAL if os.environ.get("HMT_ARTWORK","A5")=="A5" else p.LT_POWER)
    fps={f.GetReference():f for f in b.GetFootprints()}
    ep=max((pd for pd in fps['U1'].Pads() if pd.GetNumber()=='17'),key=lambda pd:pd.GetSize().x*pd.GetSize().y)
    x,y=p.ToMM(ep.GetPosition().x),p.ToMM(ep.GetPosition().y)
    # A2: DAC PowerPAD -> GND reference plane. Opposite-side pads were checked
    # before choosing these sites; F.Mask tenting limits solder wicking.
    if os.environ.get('HMT_ARTWORK','A5')in ('A2','A3','A4','A5'):
        sites=json.loads((HERE/'placement'/'thermal_vias_A2.json').read_text())
        expected={'U7':(127.8,107.1),'U8':(134.7,92.9)}
        for ref,pos in expected.items():
            actual=fps[ref].GetPosition()
            if abs(p.ToMM(actual.x)-pos[0])>.001 or abs(p.ToMM(actual.y)-pos[1])>.001:
                raise ValueError('Re-evaluate A2 thermal vias after moving '+ref)
        for site in sites:
            pt=p.VECTOR2I(MM(site['xy'][0]),MM(site['xy'][1]))
            existing=next((v for v in b.GetTracks() if isinstance(v,p.PCB_VIA) and v.GetNetname()=='GND' and (v.GetPosition()-pt).EuclideanNorm()<1000),None)
            v=existing or p.PCB_VIA(b)
            if existing is None:
                v.SetPosition(pt);v.SetWidth(MM(.45));v.SetDrill(MM(.2))
                v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet('GND'));b.Add(v)
            v.SetFrontTentingMode(p.TENTING_MODE_TENTED)
    # A local return island around the exposed pad. Isolation verified by DRC.
    rt=(x-2.2,y-3.0,x+2.2,y+3.0)
    for layer in (p.F_Cu,p.B_Cu):
        z=rect(b,layer,rt,'EF_RTN',name='RTN dedicated island'); z.SetAssignedPriority(5)
    for layer in ([p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu] if b.GetCopperLayerCount()==6 else [p.In1_Cu,p.In2_Cu]):
        rect(b,layer,(rt[0]-.3,rt[1]-.3,rt[2]+.3,rt[3]+.3),keepout=True,name='RTN isolation under U1')
    for layer in ([p.F_Cu,p.In1_Cu,p.In4_Cu,p.B_Cu] if b.GetCopperLayerCount()==6 else [p.F_Cu,p.In1_Cu,p.B_Cu]):
        rect(b,layer,(99,88,157.5,112),'GND',name='GND')
    p.ZONE_FILLER(b).Fill(b.Zones())
    p.SaveBoard(str(BASE)+'.kicad_pcb',b,True)
    # Outer GND fills must be rebuilt around tracks after routing, not imported as fixed obstacles.
    for z in list(b.Zones()):
        if not z.GetIsRuleArea() and z.GetLayer() not in (p.In1_Cu,p.In4_Cu): b.RemoveNative(z)
    b.SetLayerType(p.In1_Cu,p.LT_POWER)
    if not p.ExportSpecctraDSN(b,str(dsn)):raise RuntimeError('DSN export failed')
    # Pad pitch constrains RTN-to-adjacent control pins to .25; GND isolation stays .30.
    Path(str(BASE)+'.kicad_dru').write_text("""(version 1)
(rule "RTN to system GND isolation"
 (condition "(A.NetName == 'EF_RTN' && B.NetName == 'GND') || (A.NetName == 'GND' && B.NetName == 'EF_RTN')")
 (constraint clearance (min 0.3mm)))
""")
    data=dsn.read_text()
    ground_rules='(layer_rule In1.Cu (active off))'
    if b.GetCopperLayerCount()==6 and os.environ.get('HMT_ARTWORK','A5')!='A5':ground_rules+=' (layer_rule In4.Cu (active off))'
    data=data.replace('(boundary', '(autoroute_settings (fanout off) (autoroute on) (postroute off) '+ground_rules+')\n    (boundary',1)
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
