"""TPS2660 divider corners. TI SLVSDG2G electrical limits; values in ohms."""
import itertools,json
from pathlib import Path
r=[845000,97600,35700]
tolerance=[.01,.001,.01];tcr=[100e-6,25e-6,100e-6]
result={}
for delta in [0,100]:
    errors=[t+c*delta for t,c in zip(tolerance,tcr)]
    row={}
    for name,lo,hi,kind in [('UVLO_rise',1.175,1.225,'UV'),('OVP_rise',1.17,1.225,'OV'),('OVP_fall',1.085,1.125,'OV')]:
        vals=[]
        for signs in itertools.product([-1,1],repeat=3):
            a,b,c=[v*(1+s*e) for v,s,e in zip(r,signs,errors)]
            for ref,iu,io in itertools.product([lo,hi],[-100e-9,100e-9],[-100e-9,100e-9]):
                v=ref*(a+b+c)/(b+c)+iu*a+io*a*c/(b+c) if kind=='UV' else ref*(a+b+c)/c+iu*a+io*(a+b)
                vals.append(v)
        row[name]=[min(vals),max(vals)]
    result[f'deltaT_{delta}C']=row
result['nominal']={'UVLO_rise':1.19*sum(r)/sum(r[1:]),'OVP_rise':1.19*sum(r)/r[2],'OVP_fall':1.1*sum(r)/r[2],'ILIM_mA':12000/82000*1000}
result['notes']='Divider voltage referenced to EF_RTN at VIN_D, not connector; IC threshold limits, independent resistor initial tolerance/TCR and both +/-100nA leakage included. deltaT100 covers -40..125C relative to25C, not product temperature qualification. 82k exact current-limit min/max not tabulated: bench check required.'
assert result['deltaT_100C']['OVP_fall'][0]>28
assert result['deltaT_100C']['OVP_rise'][0]>28
assert result['deltaT_100C']['UVLO_rise'][1]<10
Path(__file__).with_name('calculations.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
