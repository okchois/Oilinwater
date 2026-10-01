"""제조사 원문 기준 SMNR4020 랜드. PDF는 저장소에 포함하지 않음.
SXN SMNR series p4: F=.95 G=2.1 H=3.3, C=2.0±.2 mm.
https://datasheet.lcsc.com/datasheet/pdf/c30b0f031d0070e2292eba9306a4bf8b.pdf
"""
from pathlib import Path

def generate():
    lib=Path(__file__).resolve().parent/'lib'/'HMT500_260313A.pretty'
    s=(lib/'L_Taiyo-Yuden_NR-40xx.kicad_mod').read_text()
    s=s.replace('L_Taiyo-Yuden_NR-40xx','L_SXN_SMNR4020')
    import re
    s=re.sub(r'\(descr "[^"]*"\)', '(descr "SXN SMNR4020, manufacturer land F0.95 G2.1 H3.3 mm, body max 4.3x4.3x2.2 mm")', s)
    s=re.sub(r'\(tags "[^"]*"\)', '(tags "SXN SMNR4020 inductor")', s)
    s=s.replace('(at -1.4 0) (size 1.2 3.7)','(at -1.525 0) (size 0.95 3.3)')
    s=s.replace('(at 1.4 0) (size 1.2 3.7)','(at 1.525 0) (size 0.95 3.3)')
    # No inaccurate 3D model inherited from the former Taiyo-Yuden package.
    i=s.find('  (model ')
    if i>=0:s=s[:i]+')\n'
    # Keep existing 4.5 mm courtyard: max body 4.3 mm, inter-courtyard margin is additional .1 mm.
    (lib/'L_SXN_SMNR4020.kicad_mod').write_text(s)
if __name__=='__main__':generate()
