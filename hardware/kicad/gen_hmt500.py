"""DOTECH HMT500(260313) KiCad 회로도 생성기 (파일명·프로젝트 번호 HMT500(260313A)) v0.3 — 배치·배선된 정식 회로도.

python3 hardware/kicad/gen_hmt500.py  →  hardware/kicad/HMT500(260313A)/

- 좌표 단위 u = 2.54 mm(100 mil). 모든 핀·선은 1.27 mm 격자 위.
- 신호는 왼쪽→오른쪽, 전원은 위(전원 심볼), GND는 아래(GND 심볼).
- 시트 사이 신호만 전역 라벨, 전원은 전원 심볼(GND, +3V3, +3V3A, +5V, VIN_P, VDDA, CHASSIS).
- 각 부품의 nets=... 는 설계 의도(정답)이며, 그린 배선이 이와 같은지 check_netlist.py로 검증한다.
- 그리기 규칙 위반(선 중간에 걸친 핀, 연결 안 된 핀)은 생성 단계에서 오류로 멈춘다.
"""

import csv
import json
import os
import uuid

PROJECT = "HMT500(260313A)"      # 회로·PCB·거버 파일명 = 프로젝트 번호
PRODUCT = "HMT500(260313)"       # 제품(프로젝트) 이름
LIB = "HMT500_260313A"           # 심볼 라이브러리 별칭 (lib_id에 괄호를 넣지 않음)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), PROJECT)
NS = uuid.UUID("6f1c0a52-8d7e-4c1a-9a53-4d2f0b7e1a10")
U = 2.54


def uid(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def mm(v):
    return f"{round(v * U, 4):g}"


def fnum(v):
    return f"{round(v, 4):g}"


REF_SZ, VAL_SZ = 1.27, 1.27
HANGUL_FACE = "NanumGothic"          # KiCad 기본(스트로크) 글꼴에는 한글이 없어 한글 글자는 트루타입으로


def has_hangul(t):
    return any("가" <= ch <= "힣" or "ㄱ" <= ch <= "ㆎ" for ch in str(t))


KO_SAFE = {"\u2212": "-", "\u00b5": "u"}      # NanumGothic에 없는 글자 → 대체


def ko_safe(t):
    return "".join(KO_SAFE.get(ch, ch) for ch in t) if has_hangul(t) else t


def text_w(t, size, bold=False):
    w = sum((1.0 if has_hangul(ch) else 1.05) for ch in str(t)) * size / U
    return w * (1.08 if bold else 1.0)


FONT = "(effects (font (size 1.27 1.27)))"
HIDE = "(effects (font (size 1.27 1.27)) hide)"
ST = "(stroke (width 0.254) (type default))"

# ════════════════════════════ 심볼 정의 ════════════════════════════
SYM = {}


def ic(name, left=(), right=(), top=(), bottom=(), w=8, prefix="U", verify=False, desc="", ts=2, toff=0, bs=2, rows=1):
    SYM[name] = dict(kind="ic", left=list(left), right=list(right), top=list(top), bottom=list(bottom),
                     w=w, prefix=prefix, verify=verify, desc=desc, ts=ts, toff=toff, bs=bs, rows=rows)


def two(name, prefix, draw, desc, pnum=("1", "2"), stack=None):
    """2단자 심볼. pnum = (위/왼쪽, 아래/오른쪽) 핀 번호, stack = {핀: [같은 자리에 겹친 핀들]} (다핀 패키지용)."""
    SYM[name] = dict(kind="two", prefix=prefix, draw=draw, desc=desc, pnum=pnum, stack=stack or {})


def pwr(name, style, desc):
    SYM[name] = dict(kind="pwr", prefix="#PWR", style=style, desc=desc)


two("R", "R", "rect", "Resistor")
two("C", "C", "cap", "Capacitor")
two("L", "L", "ind", "Inductor")
two("FB", "FB", "ferrite", "Ferrite bead")
two("TVS_BI", "D", "tvs", "Bidirectional TVS diode")
two("GDT", "GDT", "gdt", "Gas discharge tube")
two("TVS3301", "D", "tvs", "TI TVS3301 33 V bidirectional flat-clamp TVS, SON-8 DRB (IN = 1-4, GND = 5-8, pad floating)",
    pnum=("1", "5"), stack={"1": ["2", "3", "4"], "5": ["6", "7", "8"]})
two("TVS1401", "D", "tvs", "TI TVS1401 14 V bidirectional flat-clamp TVS, SON-8 DRB (IN = 1-4, GND = 5-8, pad floating)",
    pnum=("1", "5"), stack={"1": ["2", "3", "4"], "5": ["6", "7", "8"]})
two("LED", "D", "led", "LED (pin1 = K, pin2 = A)")
two("ZENER", "D", "zener", "Zener diode SOT-23 (pin 3 = K, pin 1 = A, pin 2 NC)", pnum=("3", "1"))
two("SCHOTTKY", "D", "schottky", "Schottky diode SOD-123F/W (pin 1 = K, pin 2 = A)", pnum=("2", "1"))
SYM["PWR_FLAG"] = dict(kind="flag", prefix="#FLG", desc="Power flag")
for n in ("+3V3", "+3V3A", "+5V", "VIN_P", "VDDA", "VAO"):
    pwr(n, "up", f"Power symbol {n}")
pwr("GND", "gnd", "Ground")
pwr("EF_RTN", "rtn", "TPS2660 RTN reference (local, NOT connected to GND)")
pwr("CHASSIS", "chassis", "Chassis / housing (earth via process pipe)")

B, I, O, P, PI, PO, OC, T, NC = ("bidirectional", "input", "output", "passive", "power_in", "power_out",
                                 "open_collector", "tri_state", "no_connect")

ic("CONN_GH8", right=[("8", "V+", P), ("6", "GND", P), ("4", "OUT1", P), ("5", "OUT2", P), ("3", "RS485_A", P),
                      ("2", "RS485_B", P), ("1", "NC", P), ("7", "NC", P)],
   w=6, prefix="J", desc="JST GH 1.25 mm 8-pin side-entry header. Harness W-2 to M12 8P field connector (pin n = M12 pin n)")
ic("CONN_CH", right=[("1", "CHASSIS", P)], w=6, prefix="J",
   desc="Chassis wire solder hole: AWG 28 wire to an M2 ring terminal under a PCB-holder screw (metal body)")
ic("CMC", left=[("1", "", P), ("2", "", P)], right=[("4", "", P), ("3", "", P)], w=4, prefix="L",
   desc="2-line common mode choke")
ic("TPS2660", left=[("1", "IN", PI), ("2", "IN", P), ("7", "~{SHDN}", I), ("3", "UVLO", I), ("4", "NC", NC),
                   ("6", "MODE", I), ("5", "OVP", I)],
   right=[("15", "OUT", PO), ("16", "OUT", P), ("14", "~{FLT}", OC), ("11", "ILIM", P), ("10", "IMON", P),
          ("12", "dVdT", P), ("13", "NC", NC)],
   bottom=[("9", "GND", PI), ("8", "RTN", P), ("17", "RTN", P)], w=12,
   desc="TI TPS26600PWP 60V eFuse, HTSSOP-16 (datasheet SLVSDG2G). RTN = device reference, never tied to GND (reverse-polarity block between RTN and GND); PowerPAD = RTN")
ic("LMR36006", left=[("2", "VIN", PI), ("10", "VIN", P), ("9", "EN", I), ("8", "PG", OC)], top=[("4", "BOOT", P)],
   right=[("12", "SW", PO), ("7", "FB", I), ("5", "VCC", P), ("3", "NC(SW)", P)],
   bottom=[("6", "AGND", PI), ("1", "PGND", PI), ("11", "PGND", P)],
   w=8, rows=6, desc="TI LMR36006 60V 0.6A sync buck, VQFN-HR-12 RNX 2x3 mm (datasheet SNVSB48C). VFB = 1.0 V")
ic("LMR51606", left=[("5", "VIN", PI), ("4", "EN", I)], right=[("1", "CB", P), ("6", "SW", PO), ("3", "FB", I)],
   bottom=[("2", "GND", PI)], w=6, desc="TI LMR51606YFDBVR 4-65 V 0.6 A buck, 1.1 MHz FPWM, SOT-23-6 (SLUSEY1B: 1 CB, 2 GND, 3 FB, 4 EN, 5 VIN, 6 SW)")
ic("BAS70-04", left=[("3", "COM", P)], right=[("2", "K", P), ("1", "A", P)], w=4, prefix="D",
   desc="Dual series Schottky 70 V SOT-23 (1 = A of D1, 2 = K of D2, 3 = common)")
ic("NPN_SOT23", left=[("1", "B", I)], top=[("3", "C", P)], bottom=[("2", "E", P)], w=4, prefix="Q",
   desc="NPN transistor SOT-23 (1 = B, 2 = E, 3 = C)")
ic("TPS7A2033", left=[("1", "IN", PI), ("3", "EN", I)], right=[("5", "OUT", PO), ("4", "NC", NC)],
   bottom=[("2", "GND", PI)], w=6, desc="TI TPS7A2033 3.3V LDO, SOT-23-5")
ic("STM32G0B1CxTx",
   left=[("10", "PF2-NRST", B), ("1", "PC13", B), ("2", "PC14", B), ("3", "PC15", B), ("8", "PF0", B), ("9", "PF1", B),
         ("30", "PC6", B), ("31", "PC7", B), ("38", "PD0", B), ("39", "PD1", B), ("40", "PD2", B), ("41", "PD3", B)],
   right=[(n, nm, B) for n, nm in (("11", "PA0"), ("12", "PA1"), ("13", "PA2"), ("14", "PA3"), ("15", "PA4"),
                                   ("16", "PA5"), ("17", "PA6"), ("18", "PA7"), ("28", "PA8"), ("29", "PA9"),
                                   ("32", "PA10"), ("33", "PA11"), ("34", "PA12"), ("35", "PA13"),
                                   ("36", "PA14-BOOT0"), ("37", "PA15"))] +
         [(n, f"PB{i}", B) for i, n in enumerate(["19", "20", "21", "42", "43", "44", "45", "46", "47", "48", "22",
                                                  "23", "24", "25", "26", "27"])],
   top=[("4", "VBAT", PI), ("6", "VDD", PI), ("5", "VREF+", PI)],
   bottom=[("7", "VSS", PI)], ts=4,
   w=20, toff=1, desc="STM32G0B1CCT3 LQFP48, -40..125C (pinout from KiCad library STM32G0B1C_B-C-E_Tx)")
ic("CONN_SWD", left=[("2", "SWDIO", P), ("4", "SWCLK", P), ("3", "NRST", P), ("6", "SWO", P)],
   top=[("1", "VCC", P)], bottom=[("5", "GND", P)], w=12, prefix="J", desc="Tag-Connect TC2030 SWD")
ic("CONN_SH4", right=[("1", "SENS_1", P), ("2", "SENS_2", P), ("3", "PT+", P), ("4", "PT-", P)], w=6, prefix="J",
   desc="JST SH 1.0 mm 4-pin side-entry (right angle) header. Sensor harness W-1 direct from HTX99R connector (MK sensor + Pt1000 2-wire)")
ic("PCAP04", left=[("24", "PC2", P), ("1", "PC3", P), ("22", "PC0", P), ("20", "PC4", P), ("21", "PC5", P),
                   ("23", "PC1", P), ("19", "PCAUX", P), ("6", "PT0REF", P), ("5", "PT1", P), ("7", "PTOUT", P)],
   right=[("9", "SSN", I), ("16", "SCK", I), ("15", "MOSI", I), ("10", "MISO", T), ("11", "PG5", O),
          ("12", "PG2", B), ("17", "PG3", B), ("18", "PG4", B), ("3", "VDD18", P), ("13", "IIC_EN", I)],
   top=[("4", "VDD33", PI), ("14", "VDD33", PI)], ts=3, bottom=[("2", "GND", PI), ("8", "GND", PI), ("25", "EP", P)],
   w=10, rows=12, desc="ScioSense PCAP04 capacitance-to-digital, QFN24 4x4 (datasheet SC-001050-DS-6). VDD18 >= 4.7 uF, VDD33 >= 10 uF; INTN on PG5")
ic("ADS1220", left=[("10", "AIN1", P), ("11", "AIN0/REFP1", P), ("6", "AIN3/REFN1", P), ("7", "AIN2", P)],
   right=[("1", "SCLK", I), ("2", "~{CS}", I), ("16", "DIN", I), ("15", "DOUT/~{DRDY}", T), ("14", "~{DRDY}", O),
          ("3", "CLK", I)],
   top=[("12", "AVDD", PI), ("13", "DVDD", PI)], ts=4, bs=3,
   bottom=[("9", "REFP0", P), ("8", "REFN0", P), ("5", "AVSS", PI), ("4", "DGND", PI)],
   w=16, desc="TI ADS1220 24-bit ADC, TSSOP-16")
ic("DAC8760", left=[("9", "DIN", I), ("8", "SCLK", I), ("7", "LATCH", I), ("10", "SDO", O), ("3", "~{ALARM}", OC),
                    ("18", "HART-IN", I)],
   right=[("21", "VOUT", P), ("19", "IOUT", P), ("22", "+VSENSE", I), ("14", "REFOUT", O), ("15", "REFIN", I),
          ("20", "BOOST", O), ("17", "CMP", P)],
   top=[("24", "AVDD", PI), ("2", "DVDD", PI)], ts=4,
   bottom=[("1", "AVSS", PI), ("4", "GND", PI), ("11", "GND", PI), ("12", "GND", PI), ("25", "EP", PI),
           ("23", "-VSENSE", I), ("6", "CLR", I), ("5", "CLR-SEL", I), ("16", "DVDD-EN", I), ("13", "ISET-R", P)],
   w=20, rows=10, desc="TI DAC8760 16-bit V/I output DAC, HTSSOP-24 PWP (pinout: datasheet SBAS528D, as VibrationSensor IVS320)")
ic("OPA197", left=[("1", "OUT", O), ("4", "-IN", I)], right=[("3", "+IN", I)], top=[("5", "V+", PI)],
   bottom=[("2", "V-", PI)], w=6,
   desc="TI OPA197 36 V rail-to-rail op amp, SOT-23-5 DBV (1 OUT, 2 V-, 3 +IN, 4 -IN, 5 V+). +VSENSE unity-gain buffer")
ic("TPS26611", left=[("4", "IN", P)], right=[("5", "OUT", P), ("7", "EN", I)],
   top=[("6", "+Vs", PI)], bottom=[("1", "GND", PI), ("3", "-Vs", PI), ("2", "MODE", I), ("8", "SGOOD", O)],
   w=10, rows=4, desc="TI TPS26611 +/-50 V current-loop / analog output protector, SOT-23-8 DDF (datasheet SLVSFE3C). +Vs <= 30 V")
ic("74LVC2G32", left=[("1", "1A", I), ("5", "2A", I), ("2", "1B", I), ("6", "2B", I)], right=[("7", "1Y", O), ("3", "2Y", O)],
   top=[("8", "VCC", PI)], bottom=[("4", "GND", PI)], w=6, desc="Dual 2-input OR gate (SCLK gating per DAC8760 datasheet 8.5.1.5)")
ic("THVD2450", left=[("4", "D", I), ("1", "R", O), ("2", "~{RE}", I), ("3", "DE", I)],
   right=[("6", "A", B), ("7", "B", B)], top=[("8", "VCC", PI)], bottom=[("5", "GND", PI)], w=8,
   desc="TI THVD2450 +/-70V fault-protected RS-485, SOIC-8")


# ── 심볼 기하 (라이브러리 좌표, u 단위, y 위쪽 +) ──
def ic_geom(s):
    n = max(len(s["left"]), len(s["right"]), s.get("rows", 1))
    tr = (n - 1) // 2
    hw = s["w"] / 2
    pins = []
    for i, (num, nm, t) in enumerate(s["left"]):
        pins.append((num, nm, t, -hw - 1, tr - i, 0))
    for i, (num, nm, t) in enumerate(s["right"]):
        pins.append((num, nm, t, hw + 1, tr - i, 180))
    btop, bbot = tr + 1, tr - (n - 1) - 1
    for side, lst, y, ang in (("t", s["top"], btop + 1, 270), ("b", s["bottom"], bbot - 1, 90)):
        k = len(lst)
        for i, (num, nm, t) in enumerate(lst):
            pins.append((num, nm, t, (s.get("ts", 2) if side == "t" else s.get("bs", 2)) * (i - (k - 1) / 2) + (s.get("toff", 0) if side == "t" else 0), y, ang))
    return pins, (-hw, btop, hw, bbot)


def pins_of(name):
    s = SYM[name]
    if s["kind"] == "ic":
        return ic_geom(s)[0]
    if s["kind"] in ("pwr", "flag"):
        return [("1", name if s["kind"] == "pwr" else "pwr", "power_in" if s["kind"] == "pwr" else "power_out", 0, 0,
                 90 if s.get("style") == "up" or s["kind"] == "flag" else 270)]
    a, b = s.get("pnum", ("1", "2"))
    out = [(a, "~", P, 0, 1.5, 270), (b, "~", P, 0, -1.5, 90)]
    for base, extra in s.get("stack", {}).items():
        bx = [o for o in out if o[0] == base][0]
        out += [(n, "~", P, bx[3], bx[4], bx[5]) for n in extra]
    return out


def graphics(name):
    s = SYM[name]
    k = s["kind"]
    if k == "ic":
        x1, y1, x2, y2 = ic_geom(s)[1]
        g = [f"(rectangle (start {mm(x1)} {mm(y1)}) (end {mm(x2)} {mm(y2)}) {ST} (fill (type background)))"]
        if name == "CMC":
            for yy in (0, -1):
                g.append(f"(polyline (pts (xy {mm(x1)} {mm(yy)}) (xy {mm(x2)} {mm(yy)})) {ST} (fill (type none)))")
                g.append(f"(circle (center {mm(x1 + 0.6)} {mm(yy + 0.35)}) (radius 0.25) {ST} (fill (type outline)))")
            g.append(f"(polyline (pts (xy {mm(x1)} {mm(-0.5)}) (xy {mm(x2)} {mm(-0.5)})) (stroke (width 0.508) (type default)) (fill (type none)))")
        return g
    if k == "flag":
        return [f"(polyline (pts (xy 0 0) (xy 0 1.27) (xy -1.016 1.905) (xy 0 2.54) (xy 1.016 1.905) (xy 0 1.27)) {ST} (fill (type none)))"]
    if k == "pwr":
        if s["style"] == "up":
            return [f"(polyline (pts (xy 0 0) (xy 0 1.27)) {ST} (fill (type none)))",
                    f"(polyline (pts (xy -0.762 0.762) (xy 0 1.27) (xy 0.762 0.762)) {ST} (fill (type none)))"]
        if s["style"] in ("gnd", "rtn"):
            return [f"(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) {ST} (fill (type none)))"]
        return [f"(polyline (pts (xy 0 0) (xy 0 -1.27)) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.905 -1.27) (xy 1.905 -1.27)) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.905 -1.27) (xy -2.54 -2.54)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 -1.27) (xy -0.635 -2.54)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 1.905 -1.27) (xy 1.27 -2.54)) {ST} (fill (type none)))"]
    d = s["draw"]
    if d == "rect":
        return [f"(rectangle (start -1.016 2.54) (end 1.016 -2.54) {ST} (fill (type none)))"]
    if d == "cap":
        return [f"(polyline (pts (xy -2.032 0.508) (xy 2.032 0.508)) (stroke (width 0.3048) (type default)) (fill (type none)))",
                f"(polyline (pts (xy -2.032 -0.508) (xy 2.032 -0.508)) (stroke (width 0.3048) (type default)) (fill (type none)))",
                f"(polyline (pts (xy 0 2.54) (xy 0 0.508)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 -2.54) (xy 0 -0.508)) {ST} (fill (type none)))"]
    if d == "ind":
        arcs = []
        for c in (1.905, 0.635, -0.635, -1.905):
            arcs.append(f"(arc (start 0 {fnum(c + 0.635)}) (mid 0.635 {fnum(c)}) (end 0 {fnum(c - 0.635)}) {ST} (fill (type none)))")
        return arcs
    if d == "ferrite":
        return [f"(rectangle (start -1.016 2.032) (end 1.016 -2.032) {ST} (fill (type outline)))",
                f"(polyline (pts (xy 0 2.54) (xy 0 2.032)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 -2.54) (xy 0 -2.032)) {ST} (fill (type none)))"]
    if d == "tvs":
        return [f"(polyline (pts (xy -1.27 2.54) (xy 1.27 2.54) (xy 0 0) (xy -1.27 2.54)) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.27 -2.54) (xy 1.27 -2.54) (xy 0 0) (xy -1.27 -2.54)) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.778 -0.508) (xy -1.27 0) (xy 1.27 0) (xy 1.778 0.508)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 3.81) (xy 0 2.54)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 -3.81) (xy 0 -2.54)) {ST} (fill (type none)))"]
    if d == "gdt":
        return [f"(circle (center 0 0) (radius 2.032) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.016 0.508) (xy 1.016 0.508)) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.016 -0.508) (xy 1.016 -0.508)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 2.032) (xy 0 0.508)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 -2.032) (xy 0 -0.508)) {ST} (fill (type none)))"]
    if d == "zener":
        return [f"(polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27) (xy 0 1.27) (xy -1.27 -1.27)) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.778 1.778) (xy -1.27 1.27) (xy 1.27 1.27) (xy 1.778 0.762)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 2.54) (xy 0 1.27)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 -2.54) (xy 0 -1.27)) {ST} (fill (type none)))"]
    if d == "schottky":                  # 위 = A, 아래 = K (가로 배치 시 왼쪽 A → 오른쪽 K)
        return [f"(polyline (pts (xy -1.27 1.27) (xy 1.27 1.27) (xy 0 -1.27) (xy -1.27 1.27)) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.778 -0.762) (xy -1.778 -1.27) (xy 1.778 -1.27) (xy 1.778 -1.778)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 2.54) (xy 0 1.27)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 0 -2.54) (xy 0 -1.27)) {ST} (fill (type none)))"]
    if d == "led":
        return [f"(polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27) (xy 0 1.27) (xy -1.27 -1.27)) {ST} (fill (type none)))",
                f"(polyline (pts (xy -1.27 1.27) (xy 1.27 1.27)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 1.524 0) (xy 2.54 1.016)) {ST} (fill (type none)))",
                f"(polyline (pts (xy 1.524 -1.016) (xy 2.54 0)) {ST} (fill (type none)))"]
    raise ValueError(d)


def lib_symbol(name, prefixed):
    s = SYM[name]
    k = s["kind"]
    full = f"{LIB}:{name}" if prefixed else name
    power = " (power)" if k in ("pwr", "flag") else ""
    pn = " (pin_numbers hide)" if k != "ic" else ""
    pnames = " (pin_names (offset 0) hide)" if k != "ic" else " (pin_names (offset 0.508))"
    bom = "no" if k in ("pwr", "flag") else "yes"
    o = [f"(symbol {q(full)}{power}{pn}{pnames} (in_bom {bom}) (on_board {bom})"]
    o.append(f'(property "Reference" {q(s["prefix"])} (at 0 0 0) {HIDE if k in ("pwr", "flag") else FONT})')
    o.append(f'(property "Value" {q(name)} (at 0 0 0) {FONT})')
    o.append(f'(property "Footprint" "" (at 0 0 0) {HIDE})')
    o.append(f'(property "Datasheet" "~" (at 0 0 0) {HIDE})')
    o.append(f'(property "ki_description" {q(s.get("desc", ""))} (at 0 0 0) {HIDE})')
    if s.get("verify"):
        o.append(f'(property "VERIFY" "YES - pin numbers are placeholders" (at 0 0 0) {HIDE})')
    o.append(f"(symbol {q(name + '_0_1')} " + " ".join(graphics(name)) + ")")
    ps = []
    for num, nm, t, x, y, ang in pins_of(name):
        ln = 2.54 if k == "ic" else (0 if k in ("pwr", "flag") else 1.27)
        hide = " hide" if k in ("pwr", "flag") else ""
        ps.append(f"(pin {t} line (at {mm(x)} {mm(y)} {ang}) (length {fnum(ln)}){hide} (name {q(nm)} {FONT}) (number {q(num)} {FONT}))")
    o.append(f"(symbol {q(name + '_1_1')} " + " ".join(ps) + ")")
    o.append(")")
    return " ".join(o)


def rot(px, py, r):
    return {0: (px, py), 90: (-py, px), 180: (-px, -py), 270: (py, -px)}[r]


# ════════════════════════════ 시트 편집기 ════════════════════════════
PWR_COUNT = [0]


def two_nets(sym, n1, n2):
    """2단자 부품의 핀→넷 (핀 번호·겹친 핀 포함)."""
    s = SYM[sym]
    a, b = s.get("pnum", ("1", "2"))
    m = {a: n1, b: n2}
    for base, extra in s.get("stack", {}).items():
        m.update({n: m[base] for n in extra})
    return m


class Sheet:
    def __init__(self, file, title, desc, dx=0, dy=0, paper="A3"):
        self.file, self.title, self.desc, self.dx, self.dy, self.paper = f"{PROJECT}_{file}", title, desc, dx, dy, paper
        self.parts = {}      # ref -> dict
        self.order = []
        self.wires = []      # ((x1,y1),(x2,y2))
        self.labels = []     # (net, (x,y), ang, kind)
        self.label_src = []  # 라벨을 그은 시작점 (보통 핀 끝) — 라벨 방향 판정용
        self.ncs = []
        self.texts = []
        self.boxes = []
        self.nets = {}       # 의도: ref -> {pin: net}

    # 좌표
    def o(self, pt):
        return (pt[0] + self.dx, pt[1] + self.dy)

    def place(self, ref, sym, val, fp, x, y, r=0, nets=None, **kw):
        x, y = x + self.dx, y + self.dy
        self.parts[ref] = dict(sym=sym, val=val, fp=fp, x=x, y=y, r=r, kw=kw)
        self.order.append(ref)
        if nets is not None:
            self.nets[ref] = nets
        return ref

    def P(self, ref, num):
        p = self.parts[ref]
        for pn, nm, t, px, py, ang in pins_of(p["sym"]):
            if pn == num:
                rx, ry = rot(px, py, p["r"])
                return (p["x"] + rx, p["y"] - ry)
        raise KeyError(f"{ref}.{num}")

    # 2핀 부품: 세로(pin1 위, pin2 아래) / 가로(pin1 왼쪽, pin2 오른쪽)
    def v2(self, ref, sym, val, fp, x, ytop, n1, n2, flip=False, **kw):
        # flip=True: pin2 위, pin1 아래 (LED 애노드 위)
        r = 180 if flip else 0
        self.parts[ref] = dict(sym=sym, val=val, fp=fp, x=x + self.dx, y=ytop + 1.5 + self.dy, r=r, kw=kw)
        self.order.append(ref)
        self.nets[ref] = two_nets(sym, n1, n2)
        return ref

    def h2(self, ref, sym, val, fp, xleft, y, n1, n2, **kw):
        self.parts[ref] = dict(sym=sym, val=val, fp=fp, x=xleft + 1.5 + self.dx, y=y + self.dy, r=90, kw=kw)
        self.order.append(ref)
        self.nets[ref] = two_nets(sym, n1, n2)
        return ref

    # 배선
    def w(self, *pts):
        pts = [self.o(p) for p in pts]
        for a, b in zip(pts, pts[1:]):
            if a[0] != b[0] and a[1] != b[1]:
                raise ValueError(f"{self.file}: diagonal wire {a}->{b}")
            if a != b:
                self.wires.append((a, b))

    def wa(self, *pts):  # 절대 좌표(이미 오프셋 적용된 핀 좌표 등)
        for a, b in zip(pts, pts[1:]):
            if a[0] != b[0] and a[1] != b[1]:
                raise ValueError(f"{self.file}: diagonal wire {a}->{b}")
            if a != b:
                self.wires.append((a, b))

    def pw(self, sym, pt, absolute=False):
        PWR_COUNT[0] += 1
        ref = f"#PWR{PWR_COUNT[0]:03d}"
        x, y = pt if absolute else self.o(pt)
        self.parts[ref] = dict(sym=sym, val=sym, fp="", x=x, y=y, r=0, kw={})
        self.order.append(ref)
        return ref

    def flag(self, pt, absolute=False):
        PWR_COUNT[0] += 1
        ref = f"#FLG{PWR_COUNT[0]:03d}"
        x, y = pt if absolute else self.o(pt)
        self.parts[ref] = dict(sym="PWR_FLAG", val="PWR_FLAG", fp="", x=x, y=y, r=0, kw={})
        self.order.append(ref)

    def gnd_stub(self, pt, d=1):  # pt 절대좌표(핀) → 아래로 d, GND
        e = (pt[0], pt[1] + d)
        self.wa(pt, e)
        self.pw("GND", e, absolute=True)

    def rtn_stub(self, pt, d=1):  # TPS2660 RTN 기준 (GND 아님)
        e = (pt[0], pt[1] + d)
        self.wa(pt, e)
        self.pw("EF_RTN", e, absolute=True)

    def sup_stub(self, net, pt, d=1):
        e = (pt[0], pt[1] - d)
        self.wa(pt, e)
        self.pw(net, e, absolute=True)

    def gl(self, net, pt, d="R", absolute=True, length=2):
        """pt(절대)에서 d 방향으로 length만큼 선을 긋고 전역 라벨."""
        vx, vy = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}[d]
        e = (pt[0] + vx * length, pt[1] + vy * length) if length else pt
        if length:
            self.wa(pt, e)
        self.labels.append((net, e, {"R": 0, "L": 180, "U": 90, "D": 270}[d], "global"))
        self.label_src.append(pt)

    def nc(self, pt):
        self.ncs.append(pt)

    def text(self, s, pt, size=1.5, bold=False):
        self.texts.append((s, self.o(pt), size, bold))

    def box(self, x1, y1, x2, y2, title, tdx=0.5, ko_next=False):
        self.boxes.append((self.o((x1, y1)), self.o((x2, y2))))
        self.texts.append((title, self.o((x1 + tdx, y1 + 1.2)), 1.6, True))
        ko = next((v for k, v in BOX_KO if title.startswith(k)), None)
        if ko:                                   # 한글 부제목: 같은 줄에 들어가면 옆, 아니면 다음 줄
            ko = ko.format(ch=title[len("ANALOG OUTPUT CH"):].split()[0] if title.startswith("ANALOG") else
                           title[2:].split()[0] if title.startswith("CH") else "")
            xe = x1 + tdx + text_w(title, 1.6, True) + 1.5
            if not ko_next and xe + text_w(ko, 1.4) < x2 - 0.5:
                self.texts.append((ko, self.o((xe, y1 + 1.2)), 1.4, False))
            else:
                self.texts.append((ko, self.o((x1 + tdx, y1 + 2.3)), 1.3, False))


SHEETS = []
# 박스 제목 한글 부제목 (영문 제목 시작 문자열 → 한글). 한글은 NanumGothic 트루타입으로 출력
BOX_KO = [("FIELD CONNECTOR", "현장 커넥터"), ("INPUT SURGE", "입력 서지·역극성 보호"),
          ("CIRCUIT GND", "회로 GND–외함 분리"), ("eFuse", "전자 퓨즈"), ("BUCK", "5 V 강압 전원"),
          ("LDO", "3.3 V 레귤레이터"), ("MCU DECOUPLING", "MCU 바이패스"), ("VDDA FILTER", "아날로그 기준 전원 필터"),
          ("FAULT PULL-UPS", "고장 신호 풀업·리셋"), ("SWD", "생산 프로그래밍"), ("MCU NOTES", "MCU 설정 메모"),
          ("CAPACITIVE HUMIDITY", "습도 센서 측정"), ("Pt1000", "온도 측정 (2선식)"), ("DECOUPLING", "바이패스"),
          ("ANALOG OUTPUT CH", "아날로그 출력 {ch}"), ("CH", "채널 {ch} 바이패스"), ("DAC SELECTION", "DAC 선정"), ("DAC SPI", "DAC 전용 SPI"),
          ("RS-485", "RS-485 통신"), ("RESET", "리셋"), ("LOCAL INPUT CAPS", "국부 입력 콘덴서"), ("PULL-UPS", "풀업"),
          ("OUTPUT PROTECTOR SUPPLY", "출력 보호기 전원 클램프"), ("SUPPLY MONITOR", "전원 전압 감시"),
          ("OPTIONS NOT FITTED", "PCB에 넣지 않은 선택 사항")]

FP = {
    "R0603": "Resistor_SMD:R_0603_1608Metric", "R2512": "Resistor_SMD:R_2512_6332Metric",
    "RMELF": "Resistor_SMD:R_MELF_MMB-0207", "C0603": "Capacitor_SMD:C_0603_1608Metric",
    "C0805": "Capacitor_SMD:C_0805_2012Metric", "C1206": "Capacitor_SMD:C_1206_3216Metric",
    "C1210": "Capacitor_SMD:C_1210_3225Metric", "C1812": "Capacitor_SMD:C_1812_4532Metric",
    "SMA": "Diode_SMD:D_SMA", "SMB": "Diode_SMD:D_SMB", "SMC": "Diode_SMD:D_SMC",
    "FB0603": "Inductor_SMD:L_0603_1608Metric", "LED": "LED_SMD:LED_0603_1608Metric",
    "R1206": "Resistor_SMD:R_1206_3216Metric", "SOT23": "Package_TO_SOT_SMD:SOT-23",
    "SOD123F": "Diode_SMD:D_SOD-123F", "SOT236": "Package_TO_SOT_SMD:SOT-23-6",
    "C0402": "Capacitor_SMD:C_0402_1005Metric", "R0402": "Resistor_SMD:R_0402_1005Metric",   # 외부 검수 반영: 자리 확보 (결정 #35)
}


def decap(S, ref, val, fp, x, ytop, net):
    """전원 심볼(위) — 커패시터 — GND(아래) 한 벌."""
    S.v2(ref, "C", val, FP[fp], x, ytop, net, "GND")
    S.sup_stub(net, S.P(ref, "1"))
    S.gnd_stub(S.P(ref, "2"))


def part_table(S, x, y, rows, title="주요 부품  —  역할 · 특징 · 사양"):
    """주요 부품 표: 부품번호 | 부품 | 역할 | 특징·사양 (열 정렬). * = 데이터시트로 확인할 값."""
    head = ("부품번호", "부품", "역할", "특징 · 사양")
    widths = [max(text_w(r[c], 1.27, c == 0) for r in list(rows) + [head]) + 1.4 for c in range(4)]
    y0 = y + 3.4
    for i, r in enumerate([head] + list(rows)):
        xx = x + 0.5
        for c, t in enumerate(r):
            S.texts.append((t, S.o((xx, y0 + 1.7 * i)), 1.27, i == 0 or c == 0))
            xx += widths[c]
    yb = y0 + 1.7 * len(rows) + 0.9
    S.boxes.append((S.o((x, y)), S.o((x + sum(widths) + 0.6, yb + 1.1))))
    S.texts.append((title, S.o((x + 0.5, y + 1.2)), 1.6, True))
    S.texts.append(("* 표시 값은 데이터시트로 확인", S.o((x + 0.5, yb + 0.7)), 1.1, False))


# ════════════════════════════ 1. 커넥터·입력 보호 ════════════════════════════
S = Sheet("connector.kicad_sch", "Connector & input protection",
          "Field connector, 2-stage bidirectional TVS surge protection, chassis isolation", dx=2, dy=2)
SHEETS.append(S)
S.place("J1", "CONN_GH8", "SM08B-GHS-TB", "Connector_JST:JST_GH_SM08B-GHS-TB_1x08-1MP_P1.25mm_Horizontal",
        16, 29, nets={"8": "VIN_EXT", "6": "GND_IN", "4": "OUT1_EXT", "5": "OUT2_EXT", "3": "RS485_A_EXT",
                      "2": "RS485_B_EXT"})
S.place("L1", "CMC", "CMC 1mH 0.8A", "Inductor_SMD:L_CommonMode_Wuerth_WE-SL2", 32.5, 26,
        nets={"1": "VIN_EXT", "4": "VIN_L", "2": "GND_IN", "3": "GND"})     # WE-SL2: 권선 1–4, 2–3
S.wa(S.P("J1", "8"), S.P("L1", "1"))
S.wa(S.P("J1", "6"), S.P("L1", "2"))
b = S.P("L1", "3")                          # GND 출력: 핀에서 바로 아래로 GND, PWR_FLAG는 옆 짧은 선 끝
g = (b[0], b[1] + 2)
S.wa(b, g, (g[0] + 1, g[1]))
S.pw("GND", g, absolute=True)
S.flag((g[0] + 1, g[1]), absolute=True)
a = S.P("L1", "4")
S.v2("D1", "TVS_BI", "SMDJ36CA", FP["SMC"], 40, 26, "VIN_L", "GND")
S.h2("R1", "R", "4.7R 1W pulse", FP["R2512"], 45, 26, "VIN_L", "VIN_F")
S.wa(a, S.P("D1", "1"), S.P("R1", "1"))
S.gnd_stub(S.P("D1", "2"))
S.v2("D2", "TVS3301", "TVS3301DRBR", "HMT500_260313A:Texas_DRB0008A_PadFloat", 52, 26, "VIN_F", "GND")
S.v2("C1", "C", "100n 100V", FP["C0805"], 58, 26, "VIN_F", "GND")
S.gnd_stub(S.P("D2", "5"))
S.gnd_stub(S.P("C1", "2"))
S.w((48, 26), (52, 26), (58, 26), (62, 26))
# v0.9 (외부 검수 H01): 직렬 100 V 쇼트키 — 음(−) 서지·역극성을 다이오드가 막아 eFuse IN–OUT 역전압 제거
S.h2("D3", "SCHOTTKY", "PMEG10010ELR", FP["SOD123F"], 62, 26, "VIN_F", "VIN_D")
S.w((65, 26), (68, 26))
S.flag((68, 26))
S.gl("VIN_D", S.o((68, 26)), "R")
for num, net in (("4", "OUT1_EXT"), ("5", "OUT2_EXT"), ("3", "RS485_A_EXT"), ("2", "RS485_B_EXT")):
    S.gl(net, S.P("J1", num), "R", length=1)
S.nc(S.P("J1", "1"))
S.nc(S.P("J1", "7"))
S.place("J5", "CONN_CH", "CHASSIS wire", "HMT500_260313A:SolderWire_Chassis_D0.6mm", 16, 43, nets={"1": "CHASSIS"})
sh = S.P("J5", "1")
S.v2("R2", "R", "1M HV", FP["R1206"], 36, 44, "CHASSIS", "GND")
S.v2("C3", "C", "4.7n 2kV", FP["C1812"], 42, 44, "CHASSIS", "GND")
S.place("GDT1", "GDT", "2035-25-SM", "HMT500_260313A:GDT_Bourns_2035-xx-SM", 52, 45.5, nets={"1": "CHASSIS", "2": "GND"})
S.wa(sh, S.o((24, 43)))                          # J5 핀 = 샤시 선 높이 → 곧게
S.w((24, 43), (36, 43), (42, 43), (52, 43), (60, 43))
for r_ in ("R2", "C3", "GDT1"):
    S.wa((S.P(r_, "1")[0], 43 + S.dy), S.P(r_, "1"))
    S.gnd_stub(S.P(r_, "2"))
S.pw("CHASSIS", (60, 43))
S.box(8, 17, 28.5, 38, "FIELD CONNECTOR")
S.text("J1 JST GH 8P -> W-2 -> M12 8P", (8.5, 19.5), 1.27)
S.text("EE364 pinout, pin n = pin n", (8.5, 21.0), 1.27)
S.text("GH mounting pads (MP): PCB only", (8.5, 37.0), 1.27)
S.text("Pins 1, 7: not connected", (8.5, 35.4), 1.27)
S.box(29, 17, 75, 35, "INPUT SURGE / REVERSE-POLARITY PROTECTION")
S.text("TVS bidirectional: -30 V miswiring must not conduct", (29.5, 19.5), 1.27)
S.text("SMDJ (1st) -> R1 -> TVS3301 (2nd) -> D3 100 V Schottky -> eFuse (sheet Power)", (29.5, 34), 1.27)
S.box(32, 39.5, 75, 54, "CIRCUIT GND <-> CHASSIS  (floating)")
S.text("GDT conducts only on line-to-ground surge", (56, 52.5), 1.27)
S.text("PCB-housing creepage >= 2 mm", (56, 50), 1.27)

part_table(S, 6, 58, [
    ("J1", "SM08B-GHS-TB", "현장 커넥터 연결", "JST GH 1.25 mm 8P 옆 삽입, 하네스 W-2 → M12 8P, 핀 n = M12 핀 n"),
    ("L1", "CMC 1mH 0.8A", "전원선 공통모드 노이즈 차단", "Bourns SRF0905-102Y (LCSC, 744222 동등), 2 × 1 mH, 0.8 A, 9.2 × 6 × 5.3 mm — 전도 방출·내성 대책"),
    ("D1", "SMDJ36CA", "입력 서지 1단 흡수", "TVS 양방향 3000 W, 36 V — −30 V 오결선에 도통 안 함"),
    ("R1", "4.7R 1W pulse", "1단·2단 서지 분담", "2512 1 W (Vishay CRCW2512, JLC 부품 — 결정 #38, 펄스 에너지 시험 T1)"),
    ("D2", "TVS3301DRBR", "입력 서지 2단 클램프", "TI 평탄 클램프 ±33 V, 최대 42.5 V @ 27 A. DC 입력 33 V 초과 금지 (v0.9, 이전 SMBJ33CA)"),
    ("D3", "PMEG10010ELR", "음(−) 서지·역극성 차단", "Nexperia 100 V 1 A 쇼트키 (저누설). D2가 −42.5 V로 잡는 동안 출력 쪽 +28 V → 역전압 약 71 V를 D3가 받음 → eFuse IN–OUT 역전압 없음 (외부 검수 H01). 손실 약 0.45 V × 0.1 A"),
    ("GDT1", "2035-25-SM", "회로 GND–외함 서지 방전", "Bourns 2전극 SMD GDT 250 V (LCSC), Ø5 × 4.4 mm — 선–대지 서지 때만 도통"),
    ("C3, R2", "4.7n 2kV / 1M HV", "GND–외함 고주파 결합", "4.7 nF 2 kV X7R 1812 + 1 MΩ 서지용 칩 저항 1206 (500 V, GDT 방전 전 임펄스, 몰딩 안)"),
    ("J5", "CHASSIS wire", "PCB–바디 접지 선", "AWG 28 선 약 25 mm → M2 링 단자 → PCB 홀더 축 나사(금속 바디 탭). 조립 시뮬레이션 결과 스프링 접점 대체"),
])

# ════════════════════════════ 2. 전원 ════════════════════════════
S = Sheet("power.kicad_sch", "Power", "eFuse (reverse/OV/UV), 60V buck to 5V, LDO 3.3V", dx=4, dy=14)
SHEETS.append(S)
S.place("U1", "TPS2660", "TPS26600PWPR",
        "Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm_ThermalVias", 30, 23, nets={
    "1": "VIN_D", "2": "VIN_D", "3": "UV_DIV", "5": "OV_DIV", "6": "EF_RTN", "9": "GND", "8": "EF_RTN", "17": "EF_RTN",
    "15": "VIN_P", "16": "VIN_P", "14": "PWR_FLT", "11": "EF_ILIM", "12": "EF_DVDT"})
# 입력: VIN_F 라벨을 핀마다, 분압 R3–R5는 한 줄 세로, 탭은 UVLO·OVP 핀과 같은 높이 → 직선
# 분압 R3–R5: 위 끝 = IN 줄, 탭 = UVLO·OVP 줄 → 모두 곧은 선
p1, p2 = S.P("U1", "1"), S.P("U1", "2")
S.v2("R3", "R", "866k 1%", FP["R0603"], 14, p1[1] - S.dy, "VIN_D", "UV_DIV")
S.v2("R4", "R", "97.6k 1%", FP["R0603"], 14, p1[1] - S.dy + 3, "UV_DIV", "OV_DIV")
S.v2("R5", "R", "36.5k 1%", FP["R0603"], 14, p1[1] - S.dy + 6, "OV_DIV", "EF_RTN")
S.wa(S.P("R3", "1"), p1)
S.wa(p2, p1)                               # IN 두 핀은 핀 끝끼리
S.gl("VIN_D", S.P("R3", "1"), "U", length=0)
S.v2("C2", "C", "2.2u 100V", FP["C1210"], 8, p1[1] - S.dy + 3, "VIN_D", "GND")   # v0.9: TVS 사용 시 IN ≥ 1 µF (SLVSDG2G 11.1)
c2t = S.P("C2", "1")
S.wa(c2t, (c2t[0], p1[1]), S.P("R3", "1"))
S.gnd_stub(S.P("C2", "2"))
S.wa(S.P("R3", "2"), S.P("U1", "3"))
S.wa(S.P("R5", "1"), S.P("U1", "5"))
S.rtn_stub(S.P("R5", "2"))
S.nc(S.P("U1", "7"))                      # SHDN 개방 = 켜짐 (내부 2.7 V)
S.nc(S.P("U1", "4"))
S.nc(S.P("U1", "13"))
S.nc(S.P("U1", "10"))                     # IMON 미사용 → 개방 (데이터시트 허용)
S.gl("EF_RTN", S.P("U1", "6"), "L", length=2)     # MODE = RTN: 전류 제한 + 자동 재시도
S.gnd_stub(S.P("U1", "9"))
r8, r17 = S.P("U1", "8"), S.P("U1", "17")
S.wa(r17, r8)
S.rtn_stub(r8)
# 출력 쪽: OUT 두 핀은 핀 끝끼리, 나머지 설정 부품은 계단식으로 직선 (모두 RTN 기준)
o15, o16 = S.P("U1", "15"), S.P("U1", "16")
S.wa(o16, o15)
S.sup_stub("VIN_P", o15)
S.gl("PWR_FLT", S.P("U1", "14"), "R", length=2)
S.v2("C4", "C", "22n", FP["C0402"], 42, 25, "EF_DVDT", "EF_RTN")
S.v2("R6", "R", "80.6k 1%", FP["R0603"], 46, 23, "EF_ILIM", "EF_RTN")
S.wa(S.P("U1", "12"), S.P("C4", "1"))
S.wa(S.P("U1", "11"), S.P("R6", "1"))
for r_ in ("R6", "C4"):
    S.rtn_stub(S.P(r_, "2"))
decap(S, "C5", "10u 50V", "C1206", 53, 22, "VIN_P")
# 벅: 전원 핀마다 전원 심볼, BOOT 콘덴서는 위로, FB·SW는 라벨
# 결정 #38: 5 V 벅 = LMR51606YFDBVR (JLC 부품, VAO 벅 U15와 같은 IC). SLUSEY1B 표 8-1 (1.1 MHz, 5 V): L 10 µH,
#   COUT ≥ 10 µF / 25 V, RFBT 118k / RFBB 22.1k → 0.8 V × (1 + 118/22.1) = 5.07 V
S.place("U2", "LMR51606", "LMR51606YFDBVR", FP["SOT236"], 72, 23, nets={
    "5": "VIN_P", "4": "VIN_P", "1": "BUCK_BOOT", "6": "BUCK_SW", "3": "BUCK_FB", "2": "GND"})
vi, en = S.P("U2", "5"), S.P("U2", "4")
S.sup_stub("VIN_P", vi)
S.wa(en, vi)                               # EN = VIN (데이터시트 허용)
S.gnd_stub(S.P("U2", "2"))
bt, sw = S.P("U2", "1"), S.P("U2", "6")
xc_ = sw[0] + 3
S.v2("C8", "C", "100n", FP["C0402"], xc_ - S.dx, sw[1] - 3 - S.dy, "BUCK_BOOT", "BUCK_SW")
S.wa(bt, (xc_ - 1, bt[1]), (xc_ - 1, sw[1] - 3), S.P("C8", "1"))
S.h2("L2", "L", "10uH", "HMT500_260313A:L_SXN_SMNR4020", xc_ + 2 - S.dx, sw[1] - S.dy, "BUCK_SW", "+5V")
S.wa(sw, S.P("C8", "2"), S.P("L2", "1"))
l2o = S.P("L2", "2")
S.wa(l2o, (l2o[0] + 1, l2o[1]))
S.flag((l2o[0] + 1, l2o[1]), absolute=True)
S.sup_stub("+5V", (l2o[0] + 1, l2o[1]))
S.gl("BUCK_FB", S.P("U2", "3"), "R", length=1)
decap(S, "C6", "22u 25V", "C1210", 95, 22, "+5V")
S.v2("R8", "R", "118k 1%", FP["R0402"], 105, 22, "+5V", "BUCK_FB")
S.v2("R9", "R", "22.1k 1%", FP["R0402"], 105, 26, "BUCK_FB", "GND")
S.sup_stub("+5V", S.P("R8", "1"))
S.wa(S.P("R8", "2"), S.P("R9", "1"))
S.gl("BUCK_FB", S.P("R9", "1"), "R", length=1)
S.gnd_stub(S.P("R9", "2"))
# LDO + 아날로그 레일
S.place("U3", "TPS7A2033", "TPS7A2033PDBVR", "Package_TO_SOT_SMD:SOT-23-5", 122, 21,
        nets={"1": "+5V", "3": "+5V", "5": "+3V3", "2": "GND"})
ui, ue = S.P("U3", "1"), S.P("U3", "3")
S.wa(ue, ui)                               # EN = IN (내부 500k 풀다운이라 필수)
S.sup_stub("+5V", ui)
S.gnd_stub(S.P("U3", "2"))
S.nc(S.P("U3", "4"))
S.sup_stub("+3V3", S.P("U3", "5"))
decap(S, "C12", "1u", "C0402", 130, 22, "+3V3")
S.h2("FB1", "FB", "600R@100MHz", FP["FB0603"], 136, 21, "+3V3", "+3V3A")
S.sup_stub("+3V3", S.P("FB1", "1"))
fo = S.P("FB1", "2")
S.wa(fo, (fo[0] + 1, fo[1]))
S.flag((fo[0] + 1, fo[1]), absolute=True)
S.sup_stub("+3V3A", (fo[0] + 1, fo[1]))
decap(S, "C13", "10u", "C1206", 146, 22, "+3V3A")
# v0.9: 벅 입력 220 nF × 2 (U2 핀 옆) + 벌크 = C5 10 µF를 U2 옆에 배치, LDO 입력 1 µF (U3 옆) — SNVSB48C 9.2.1.2.6, SBVS338H 5.3
decap(S, "C16", "220n 100V", "C0805", 121, 38.5, "VIN_P")
decap(S, "C26", "1u", "C0402", 147, 38.5, "+5V")
S.box(6, 12, 63.5, 34.5, "eFuse  TPS2660   reverse -60 V  /  OVP 32.6 V  /  UVLO 8.9 V")
S.text("UVLO = 1.19 V x (R3+R4+R5)/(R4+R5) = 8.9 V   OVP rise 1.19 V x (R3+R4+R5)/R5 = 32.6 V (31.5-34.2), fall 30.1 V", (6.5, 35.5), 1.27)
S.text("I_OL = 12 / R6 = 149 mA.  Supply 12-28 V recovers after OVP trip (fall > 29.2 V).  TPS26611 +Vs clamped (sheet Aux).", (6.5, 37), 1.27)
S.text("EF_RTN = TPS2660 RTN reference: R5, R6, C4, MODE, PowerPAD. NEVER connect to GND (datasheet 9.3.5.5).", (6.5, 38.5), 1.27)
S.box(64, 12, 111.5, 33, "BUCK 5 V   LMR51606  (4-65 V in, 0.6 A, 1.1 MHz)")
S.text("Vout = 0.8 V x (1 + R8/R9) = 5.07 V.  1.1 MHz: L 10 uH, COUT 22 uF (SLUSEY1B Table 8-1). Same IC as U15.", (64, 35.5 + 3), 1.27)
S.box(112.5, 12, 155, 33, "LDO 3.3 V   TPS7A2033   +   analog rail +3V3A")
S.box(118, 33.5, 156, 45.5, "LOCAL INPUT CAPS")
S.text("C16 at U2 VIN-GND, C5 (bulk) next to U2; C26 at U3 IN", (118.5, 44.8), 1.27)

part_table(S, 6, 46, [
    ("U1", "TPS26600PWPR", "전자 퓨즈 (입력 보호)", "역극성 −60 V 차단, 과전압 32.6 V (복귀 30.1 V)·저전압 8.9 V (R3–R5), 전류 제한 149 mA (R6), 돌입 제한 (C4), 고장 출력 FLT"),
    ("C2", "2.2u 100V", "eFuse 입력 콘덴서", "TVS와 함께 IN ≥ 1 µF (데이터시트 11.1), U1 핀 옆 — 핫플러그 링잉 억제"),
    ("EF_RTN", "(기준 접지)", "TPS2660 내부 기준", "R5·R6·C4·MODE·방열 패드는 RTN에 연결. GND와 연결 금지 — 역극성 보호 무효·손상"),
    ("U2", "LMR51606YFDBVR", "5 V 강압 전원 (벅)", "입력 4–65 V, 0.6 A 동기식, 1.1 MHz FPWM, SOT-23-6, 출력 = 0.8 V × (1 + R8/R9) = 5.07 V (결정 #38, JLC 부품, U15와 같은 IC)"),
    ("L2, C6", "10uH / 22u 25V", "벅 출력 필터", "SLUSEY1B 표 8-1 (5 V, 1.1 MHz: 10 µH, ≥ 10 µF). L2 SMNR4020-10UH 4 × 4 × 2 mm"),
    ("C16 (+C5)", "220n (+10u)", "벅 입력 콘덴서", "VIN–GND 핀 옆 220 nF, 벌크 C5 10 µF를 U2 옆에"),
    ("U3", "TPS7A2033PDBVR", "3.3 V 저잡음 레귤레이터", "300 mA, 저잡음·높은 PSRR → 벅 리플 제거, SOT-23-5"),
    ("FB1", "600R@100MHz", "아날로그 전원 +3V3A 분리", "페라이트 비드 + C13 10 µF → PCAP04·ADS1220 전원"),
])

# ════════════════════════════ 3. MCU ════════════════════════════
S = Sheet("mcu.kicad_sch", "MCU", "STM32G0B1CCT6, SWD, reset, internal temperature sensor", dx=6, dy=6)
SHEETS.append(S)
mnet = {"4": "+3V3", "6": "+3V3", "5": "+3V3", "7": "GND", "10": "NRST",
        "12": "RS485_DE", "13": "RS485_TX", "14": "RS485_RX", "16": "SPI_SCK", "17": "SPI_MISO", "18": "SPI_MOSI",
        "35": "SWDIO", "36": "SWCLK", "37": "CS_CDC", "19": "VIN_SENSE", "20": "CS_ADC", "21": "ADC_DRDY",
        "42": "CDC_SCK", "43": "CDC_MISO", "44": "CDC_MOSI", "45": "DAC_ALARM", "46": "PWR_FLT",
        "22": "DAC1_LATCH", "23": "DAC2_LATCH", "24": "CDC_INT", "11": "OUT1_SGOOD", "15": "OUT2_SGOOD",

        "25": "DAC_SCK", "26": "DAC_MISO", "27": "DAC_MOSI"}
S.place("U4", "STM32G0B1CxTx", "STM32G0B1CCT6", "Package_QFP:LQFP-48_7x7mm_P0.5mm", 62, 52, nets=mnet)
for n in ("4", "6", "5"):                        # VBAT, VDD, VREF+(= VDD) 각각 +3V3 심볼
    S.sup_stub("+3V3", S.P("U4", n), d=2)
gp = S.P("U4", "7")
S.wa(gp, (gp[0], gp[1] + 2))
S.pw("GND", (gp[0], gp[1] + 2), absolute=True)
S.gl("NRST", S.P("U4", "10"), "L")
left_lbl = {}
for num, nm, t, *_ in SYM["STM32G0B1CxTx"]["left"]:
    if num == "10":
        continue
    if num in left_lbl:
        S.gl(left_lbl[num], S.P("U4", num), "L")
    else:
        S.nc(S.P("U4", num))
right_lbl = {k: v for k, v in mnet.items() if k not in ("4", "6", "5", "7", "10", "35", "36")}
for num, nm, t, *_ in SYM["STM32G0B1CxTx"]["right"]:
    if num in ("35", "36"):                      # SWD: J2로 선 연결 (v0.9: no-connect 표시 제거 — ERC 오류)
        continue
    if num in right_lbl:
        S.gl(right_lbl[num], S.P("U4", num), "R")
    else:
        S.nc(S.P("U4", num))
for i, (ref, val, fp) in enumerate([("C14", "100n", "C0402"), ("C15", "100n", "C0402"), ("C20", "100n", "C0402"),
                                   ("C18", "4.7u", "C0805")]):
    decap(S, ref, val, fp, 10 + 5 * i, 12, "+3V3")
S.box(6, 7, 38, 21, "MCU DECOUPLING")
S.text("100 nF at VDD, VBAT, VREF+ (C20); 4.7 uF bulk", (6.5, 20.3), 1.27)
S.v2("C21", "C", "100n", FP["C0402"], 128, 13, "NRST", "GND")
S.gl("NRST", S.P("C21", "1"), "U", length=1)
S.gnd_stub(S.P("C21", "2"))
S.box(118, 7, 134, 27, "RESET")
S.text("PWR_FLT: internal pull-up (PB7)", (118.5, 24.9), 1.27)
S.text("SGOOD low = OK -> PA0/PA4 (ADC)", (118.5, 26.3), 1.27)
# v0.9: 리셋 중 떠 있는 입력 고정 — DAC LATCH 10k 풀업 (SCLK 게이트 닫힘), CS 100k 풀업 (ADS1220 9.1.5)
for i, (ref, val, net) in enumerate([("R10", "10k", "DAC1_LATCH"), ("R11", "10k", "DAC2_LATCH"),
                                    ("R12", "100k", "CS_ADC"), ("R13", "100k", "CS_CDC")]):
    S.v2(ref, "R", val, FP["R0402"], 116 + 6 * i, 34.5, "+3V3", net)
    S.sup_stub("+3V3", S.P(ref, "1"))
    S.gl(net, S.P(ref, "2"), "D", length=1)
S.box(112, 29, 140, 46, "PULL-UPS")
sd = S.P("U4", "35")                              # SWD 패드: PA13·PA14와 같은 줄에 두고 곧은 선
S.place("J2", "CONN_SWD", "TC2030-IDC-NL", "Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical",
        98, sd[1] - S.dy + 1, nets={"1": "+3V3", "2": "SWDIO", "4": "SWCLK", "3": "NRST", "5": "GND"})
S.wa(sd, S.P("J2", "2"))
S.wa(S.P("U4", "36"), S.P("J2", "4"))
S.sup_stub("+3V3", S.P("J2", "1"))
S.gl("NRST", S.P("J2", "3"), "L", length=1)
S.nc(S.P("J2", "6"))                      # Cortex-M0+: SWO 없음
S.gnd_stub(S.P("J2", "5"))
S.box(86, sd[1] - S.dy - 7, 110, sd[1] - S.dy + 7, "SWD")
S.box(6, 62, 48, 85, "MCU NOTES (STM32G0B1)")
for i, t in enumerate(["BOOT0 shares PA14/SWCLK - no pull-down.",
                       "Option bytes: nBOOT_SEL=1, nBOOT0=1, IWDG_SW=0, RDP 1",
                       "  -> in-house RS-485 bootloader 0x08000000 (dec. #31).",
                       "VDDA = VDD (LQFP48); VREF+ tied to +3V3 (C20).",
                       "PCB temp (mid): internal sensor, ADC ch TS + TS_CAL.",
                       "Cortex-M0+: no SWO (J2 pin 6 NC).",
                       "Same die as DP2000 (G0B1CCT6); T3 = -40..125 C.",
                       "VIN_SENSE (PB0 ADC_IN8) = VIN_P / 11."]):
    S.text(t, (7, 66 + 2.3 * i), 1.27)

part_table(S, 6, 86, [
    ("U4", "STM32G0B1CCT6", "제어·통신·보정 연산", "Cortex-M0+ 64 MHz, 플래시 256 KB, RAM 144 KB, −40–85 °C (샘플 #39), LQFP48, 내부 온도센서 (PCB 온도). SPI1 = ADS1220, SPI2 = DAC (모드 3, SCLK 게이트), SPI3 = PCAP04"),
    ("J2", "TC2030-IDC-NL", "생산 때 펌웨어 기록 (SWD)", "PCB 패드만 (부품 없음). 이후 업데이트는 RS-485 부트로더"),
    ("C21", "100n", "리셋 노이즈 필터", "NRST 핀, 몰딩 후 EMC 여유"),
    ("R10, R11", "10k", "DAC LATCH 풀업", "리셋 중 LATCH High → SCLK 게이트 닫힘, DAC 오입력 방지 (v0.9)"),
    ("R12, R13", "100k", "CS 풀업", "리셋 중 ADS1220·PCAP04 선택 해제 (디지털 입력 부동 금지)"),
])

# ════════════════════════════ 4. 측정 ════════════════════════════
S = Sheet("measurement.kicad_sch", "Measurement", "Capacitive humidity sensor (PCAP04) and Pt1000 2-wire (ADS1220)",
          dx=4, dy=10)
SHEETS.append(S)
S.place("J3", "CONN_SH4", "SM04B-SRSS-TB", "Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal",
        8, 44, nets={"1": "SENS_C1", "2": "SENS_C2", "3": "PT_P", "4": "PT_N"})
for num, net in (("1", "SENS_C1"), ("2", "SENS_C2"), ("3", "PT_P"), ("4", "PT_N")):
    S.gl(net, S.P("J3", num), "R", length=1)
S.box(2, 37, 21, 52, "SENSOR HEAD  J3")
S.text("harness W-1 from HTX99R, JST SH 1.0", (2.5, 50.8), 1.27)
# ── PCAP04: 센서선은 라벨, 기준 C22는 PC0·PC1에 곧게 ──
S.place("U5", "PCAP04", "PCAP04-AQFM-24", "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm", 52, 19, nets={
    "22": "CREF_A", "23": "CREF_B", "24": "SENS_C1", "1": "SENS_C2", "9": "CS_CDC", "16": "CDC_SCK",
    "15": "CDC_MOSI", "10": "CDC_MISO", "11": "CDC_INT", "13": "GND", "4": "+3V3A", "14": "+3V3A", "3": "CDC_V18",
    "2": "GND", "8": "GND", "25": "GND"})
S.gl("SENS_C1", S.P("U5", "24"), "L", length=1)
S.gl("SENS_C2", S.P("U5", "1"), "L", length=1)
pc0 = S.P("U5", "22")
S.v2("C22", "C", "330p C0G 1%", FP["C0603"], pc0[0] - S.dx - 3, pc0[1] - S.dy, "CREF_A", "CREF_B")
S.wa(S.P("C22", "1"), pc0)
S.wa(S.P("C22", "2"), S.P("U5", "23"))
for num in ("20", "21", "19", "6", "5", "7", "12", "17", "18"):   # 미사용: PC4·PC5·PCAUX·PT·PG2–4 개방
    S.nc(S.P("U5", num))
for num, net in (("9", "CS_CDC"), ("16", "CDC_SCK"), ("15", "CDC_MOSI"), ("10", "CDC_MISO"), ("11", "CDC_INT")):
    S.gl(net, S.P("U5", num), "R")
S.sup_stub("+3V3A", S.P("U5", "4"))
S.sup_stub("+3V3A", S.P("U5", "14"))
for num in ("2", "8", "25"):
    S.gnd_stub(S.P("U5", num))
ie = S.P("U5", "13")
S.gnd_stub(ie)                               # IIC_EN = 0 → SPI
vd = S.P("U5", "3")
S.v2("C25", "C", "10u", FP["C1206"], vd[0] - S.dx + 4, vd[1] - S.dy, "CDC_V18", "GND")
S.wa(vd, S.P("C25", "1"))
S.gnd_stub(S.P("C25", "2"))
S.box(28, 5, 74, 34, "CAPACITIVE HUMIDITY SENSOR  (IST MK)  ->  PCAP04")
S.text("Floating single mode (DC-free, datasheet 7.2): C22 on PC0/PC1, sensor on PC2/PC3. Own SPI3.", (28.5, 33.3), 1.27)
# ── ADS1220: 필터 R17·R18은 입력 핀에 곧게, 기준저항 R19는 REFP0–REFN0 사이에 곧게 ──
S.place("U6", "ADS1220", "ADS1220IPWR", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", 52, 56, nets={
    "11": "PT_P", "10": "PT_SP_F", "7": "PT_SN_F", "1": "SPI_SCK", "2": "CS_ADC", "16": "SPI_MOSI",
    "15": "SPI_MISO", "14": "ADC_DRDY", "3": "GND", "12": "+3V3A", "13": "+3V3", "9": "PT_N", "8": "REF_N",
    "5": "GND", "4": "GND"})
a1, a2 = S.P("U6", "10"), S.P("U6", "7")          # AIN1·AIN2는 3칸 간격 → C27이 두 줄 사이에 곧게
xr = a1[0] - S.dx - 12
S.h2("R17", "R", "1k", FP["R0402"], xr, a1[1] - S.dy, "PT_P", "PT_SP_F")
S.h2("R18", "R", "1k", FP["R0402"], xr, a2[1] - S.dy, "PT_N", "PT_SN_F")
S.v2("C27", "C", "10n C0G", FP["C0603"], xr + 5, a1[1] - S.dy, "PT_SP_F", "PT_SN_F")
S.wa(S.P("R17", "2"), S.P("C27", "1"), a1)
S.wa(S.P("R18", "2"), S.P("C27", "2"), a2)
S.gl("PT_P", S.P("R17", "1"), "L", length=1)
S.gl("PT_N", S.P("R18", "1"), "L", length=1)
S.gl("PT_P", S.P("U6", "11"), "L", length=1)
S.nc(S.P("U6", "6"))
rp0, rn0 = S.P("U6", "9"), S.P("U6", "8")
S.v2("R19", "R", "4.02k 0.02% 5ppm", FP["R0603"], rp0[0] - S.dx, rp0[1] - S.dy, "PT_N", "REF_N")
S.v2("R20", "R", "1k", FP["R0402"], rn0[0] - S.dx, rn0[1] - S.dy + 3, "REF_N", "GND")
S.wa(rn0, S.P("R20", "1"))                 # REFN0 → 아래로 곧게 → R20
S.wa(S.P("R19", "2"), S.P("R20", "1"))    # R19 아래 끝 → 옆으로 곧게
S.gl("PT_N", rp0, "L", length=1)
S.gnd_stub(S.P("R20", "2"))
S.gnd_stub(S.P("U6", "5"))
S.gnd_stub(S.P("U6", "4"))
for num, net in (("1", "SPI_SCK"), ("2", "CS_ADC"), ("16", "SPI_MOSI"), ("15", "SPI_MISO"), ("14", "ADC_DRDY")):
    S.gl(net, S.P("U6", num), "R")
S.gnd_stub(S.P("U6", "3"))
S.sup_stub("+3V3A", S.P("U6", "12"))
S.sup_stub("+3V3", S.P("U6", "13"))
decap(S, "C23", "100n", "C0402", 84, 12, "+3V3A")
decap(S, "C24", "22u 10V", "C1206", 89, 12, "+3V3A")
decap(S, "C28", "100n", "C0402", 84, 50, "+3V3")
decap(S, "C29", "100n", "C0402", 89, 50, "+3V3A")
S.box(22, 40, 74, 76, "Pt1000 2-WIRE -> ADS1220  (ratiometric)")
S.text("IDAC1 (AIN0) -> PT+ ; sense AIN1-AIN2, force/sense split at J3 pads", (22.5, 71.6), 1.27)
S.text("RC filter R17/R18/C27 ; Rref R19 on REFP0/REFN0 ; lead R removed by calibration", (22.5, 73.0), 1.27)
S.text("PCB temp: ADS1220 internal sensor (TS mode)", (22.5, 74.4), 1.27)
S.box(80, 5, 95, 21, "DECOUPLING")
S.box(80, 43, 95, 59, "DECOUPLING")

part_table(S, 22, 78, [
    ("J3", "SM04B-SRSS-TB", "센서 하네스 W-1 연결", "JST SH 1.0 mm 4P 옆 삽입, 1·2 = MK33, 3·4 = Pt1000"),
    ("U5", "PCAP04-AQFM-24", "습도 센서 정전용량 측정", "정전용량–디지털 변환, 기준 C와 비율 측정(방전 시간), DC 없는 구동, 내부 DSP, 전용 SPI3 (모드 1)"),
    ("C25, C24", "10u / 22u", "PCAP04 전원 버퍼", "VDD18 ≥ 4.7 µF, VDD33 ≥ 10 µF (데이터시트 표 2) — DC 바이어스 후에도 충족 (v0.9)"),
    ("C22", "330p C0G 1%", "PCAP04 기준 용량", "센서 MK33-W (300 pF, 결정 #33) 측정 범위 가운데 값, C0G"),
    ("U6", "ADS1220IPWR", "Pt1000 온도 측정", "24비트 ADC, 50/60 Hz 제거, 내부 온도센서 (PCB 온도). 설정: IDAC = 250 µA 고정 (100 µA면 기준 0.40 V < 권장 0.75 V), PGA ≤ 2 (SPI1 모드 1)"),
    ("R19", "4.02k 0.02% 5ppm", "Pt1000 비율 측정 기준저항", "IDAC 전류 오차 상쇄, 온도계수 5 ppm/°C"),
    ("R17, R18, C27", "1k / 10n C0G", "입력 RC 필터", "차동 노이즈 제거 (C0G, 데이터시트 9.2)"),
])

# ════════════════════════════ 5. 아날로그 출력 ════════════════════════════
S = Sheet("analog_out.kicad_sch", "Analog outputs", "2x DAC8760 V/I output with TPS26611 miswiring protection",
          dx=4, dy=2)
SHEETS.append(S)
for ch, y0 in ((1, 10), (2, 46)):
    D, Pr, Bf = f"U{6 + ch}", f"U{8 + ch}", f"U{11 + ch}"
    S.place(D, "DAC8760", "DAC8760IPWP", "Package_SO:HTSSOP-24-1EP_4.4x7.8mm_P0.65mm_EP3.2x5mm", 30, y0 + 10, nets={
        "9": "DAC_MOSI", "8": f"DAC{ch}_SCLK", "7": f"DAC{ch}_LATCH", "10": "DAC_MISO", "3": "DAC_ALARM",
        "21": f"DAC{ch}_OUT", "19": f"DAC{ch}_OUT", "22": f"DAC{ch}_SENSE", "14": f"DAC{ch}_REF", "15": f"DAC{ch}_REF",
        "24": f"DAC{ch}_AVDD", "2": "+3V3", "1": "GND", "4": "GND", "11": "GND", "12": "GND", "25": "GND", "23": "GND",
        "6": "GND", "5": "GND", "16": "GND", "13": f"DAC{ch}_ISET", "17": f"DAC{ch}_CMP"})
    for num, net in (("9", "DAC_MOSI"), ("8", f"DAC{ch}_SCLK"), ("7", f"DAC{ch}_LATCH"), ("10", "DAC_MISO"),
                     ("3", "DAC_ALARM")):
        S.gl(net, S.P(D, num), "L")
    S.nc(S.P(D, "18"))
    for num in ("1", "4", "11", "12", "25", "23", "6", "5", "16"):   # GND 핀은 아래쪽에서 각자 GND
        S.gnd_stub(S.P(D, num))
    # ISET-R: 외부 15k 0.1% (내부 저항보다 온도계수 작음)
    ip = S.P(D, "13")
    S.v2(f"R{22 + 10 * ch}", "R", "15k 0.1% 25ppm", FP["R0603"], ip[0] - S.dx, ip[1] - S.dy + 1,
         f"DAC{ch}_ISET", "GND")
    S.wa(ip, S.P(f"R{22 + 10 * ch}", "1"))
    S.gnd_stub(S.P(f"R{22 + 10 * ch}", "2"))
    # AVDD: 10 Ω 직렬 (데이터시트 10장 — 전원 상승 1 V/ns 이하)
    ap = S.P(D, "24")
    S.v2(f"R{24 + 10 * ch}", "R", "10R", FP["R0402"], ap[0] - S.dx, ap[1] - S.dy - 5, "VAO", f"DAC{ch}_AVDD")
    S.sup_stub("VAO", S.P(f"R{24 + 10 * ch}", "1"))          # v0.9 (IVS320 AO rev 1.0): AVDD = VAO 16.1 V 벅 (시트 Aux)
    am = (ap[0], ap[1] - 1)
    S.wa(S.P(f"R{24 + 10 * ch}", "2"), am, ap)
    S.gl(f"DAC{ch}_AVDD", am, "L", length=0)
    S.sup_stub("+3V3", S.P(D, "2"))
    vo, io = S.P(D, "21"), S.P(D, "19")
    S.wa(io, vo)                                          # VOUT·IOUT 합침 (datasheet 9.1.1.3)
    ro, ri = S.P(D, "14"), S.P(D, "15")
    S.wa(ro, ri)
    S.v2(f"C{30 + 10 * ch}", "C", "100n", FP["C0402"], ri[0] - S.dx + 10, ri[1] - S.dy, f"DAC{ch}_REF", "GND")
    S.wa(ri, S.P(f"C{30 + 10 * ch}", "1"))
    S.gnd_stub(S.P(f"C{30 + 10 * ch}", "2"))
    S.nc(S.P(D, "20"))                                    # BOOST 미사용 — 발열은 VAO 16.1 V로 해결 (결정 #37)
    S.gl(f"DAC{ch}_CMP", S.P(D, "17"), "R", length=1)    # CMP: VOUT–CMP 4.7 nF + CMP–GND 100 pF (SBAS528D 8.3.2)
    # 오결선 보호 TPS26611: IN이 VOUT 줄과 같은 높이 → 곧게
    S.place(Pr, "TPS26611", "TPS26611DDFR", "Package_TO_SOT_SMD:SOT-23-8",
            62, vo[1] - S.dy + 1, nets={
        "4": f"DAC{ch}_OUT", "6": "VAO", "1": "GND", "3": "GND", "2": "GND", "5": f"OUT{ch}_P", "8": f"OUT{ch}_SGOOD"})
    S.wa(vo, (vo[0] + 7, vo[1]), S.P(Pr, "4"))
    S.gl(f"DAC{ch}_OUT", (vo[0] + 7, vo[1]), "U", length=1)    # → CMP 콘덴서·클램프 다이오드 (CH 디커플링 칸)
    S.sup_stub("VAO", S.P(Pr, "6"))                       # +Vs = VAO 16.1 V (결정 #37, 이전 24 V 제너 폴로워)
    for num in ("1", "3", "2"):                           # GND, -Vs = GND (단전원), MODE = GND
        S.gnd_stub(S.P(Pr, num))
    S.nc(S.P(Pr, "7"))                                    # EN 개방 = 켜짐 (내부 풀업)
    S.gl(f"OUT{ch}_SGOOD", S.P(Pr, "8"), "D", length=1)
    op = S.P(Pr, "5")
    yr = op[1] - S.dy
    S.h2(f"R{20 + 10 * ch}", "R", "10R pulse", FP["R2512"], 70, yr, f"OUT{ch}_P", f"OUT{ch}_EXT")
    S.wa(op, S.P(f"R{20 + 10 * ch}", "1"))
    S.v2(f"D{20 + 10 * ch}", "TVS1401", "TVS1401DRBR", "HMT500_260313A:Texas_DRB0008A_PadFloat", 77, yr,
         f"OUT{ch}_EXT", "GND")
    S.v2(f"C{31 + 10 * ch}", "C", "1n 100V", FP["C0603"], 83, yr, f"OUT{ch}_EXT", "GND")
    S.gnd_stub(S.P(f"D{20 + 10 * ch}", "5"))
    S.gnd_stub(S.P(f"C{31 + 10 * ch}", "2"))
    S.w((73, yr), (77, yr), (83, yr), (87, yr))
    S.gl(f"OUT{ch}_EXT", S.o((87, yr)), "R", length=0)   # → 커넥터 시트
    # +VSENSE 버퍼 (OPA197, 이득 1): 단자 전압 감지, 전류 모드에서 +VSENSE 내부 60k 누설 없음
    yb = y0 + 19                                          # 신호 흐름: 단자(오른쪽) → 버퍼 → +VSENSE(왼쪽)
    S.place(Bf, "OPA197", "OPA197IDBVR", "Package_TO_SOT_SMD:SOT-23-5", 76, yb, nets={
        "3": f"OUT{ch}_SNS", "1": f"DAC{ch}_SENSE", "4": f"DAC{ch}_SENSE", "5": f"DAC{ch}_AVDD", "2": "GND"})
    ip_ = S.P(Bf, "3")
    S.h2(f"R{21 + 10 * ch}", "R", "100k", FP["R0402"], ip_[0] - S.dx, yb, f"OUT{ch}_SNS", f"OUT{ch}_EXT")
    S.wa(S.P(Bf, "1"), S.P(Bf, "4"))                      # OUT = -IN (전압 추종기)
    vs = S.P(D, "22")                                     # +VSENSE ← 버퍼 출력: 선으로 (꺾임 2)
    S.wa(vs, (vs[0] + 15, vs[1]), (vs[0] + 15, S.P(Bf, "1")[1]), S.P(Bf, "1"))
    r2 = S.P(f"R{21 + 10 * ch}", "2")                     # 단자 → R31: 선으로 (꺾임 1)
    S.wa(r2, (87 + S.dx, r2[1]), (87 + S.dx, yr + S.dy))
    S.gl(f"DAC{ch}_AVDD", S.P(Bf, "5"), "U", length=1)     # v0.9: V+ = DAC AVDD (10 Ω 뒤) → +VSENSE ≤ AVDD
    S.gnd_stub(S.P(Bf, "2"))
    # 바이패스: DAC AVDD(10 Ω 뒤) 100n, +3V3 100n, OPA197 V+ 100n, VIN_P 벌크 4.7u는 CH1에만 (두 채널 공용)
    ca = f"C{32 + 10 * ch}"
    S.v2(ca, "C", "100n 50V", FP["C0805"], 97, y0, f"DAC{ch}_AVDD", "GND")
    S.gl(f"DAC{ch}_AVDD", S.P(ca, "1"), "R", length=1)
    S.gnd_stub(S.P(ca, "2"))
    decap(S, f"C{34 + 10 * ch}", "100n", "C0402", 107, y0, "+3V3")
    # IVS320 AO rev 1.0 방식 (결정 #37): CMP 보상 + DAC 출력 클램프 (보호기 차단·재연결 과도 → DAC 핀 보호, 외부 검수 H03)
    c47, c48, dcl = f"C{37 + 10 * ch}", f"C{38 + 10 * ch}", f"D{31 + 10 * ch}"
    S.v2(c47, "C", "4.7n", FP["C0402"], 111, y0 - 2, f"DAC{ch}_OUT", f"DAC{ch}_CMP")
    S.gl(f"DAC{ch}_OUT", S.P(c47, "1"), "R", length=1)
    S.v2(c48, "C", "100p C0G", FP["C0402"], 111, y0 + 3, f"DAC{ch}_CMP", "GND")
    S.wa(S.P(c47, "2"), S.P(c48, "1"))
    S.gl(f"DAC{ch}_CMP", S.P(c48, "1"), "R", length=1)
    S.gnd_stub(S.P(c48, "2"))
    S.place(dcl, "BAS70-04", "BAS70-04", FP["SOT23"], 108, y0 + 13, nets={
        "3": f"DAC{ch}_OUT", "2": f"DAC{ch}_AVDD", "1": "GND"})
    S.gl(f"DAC{ch}_OUT", S.P(dcl, "3"), "L", length=1)
    S.gl(f"DAC{ch}_AVDD", S.P(dcl, "2"), "R", length=1)
    S.gnd_stub(S.P(dcl, "1"))
    cb = f"C{35 + 10 * ch}"                                # OPA197 V+ (= DAC AVDD)
    S.v2(cb, "C", "100n 50V", FP["C0805"], 97, y0 + 10.5, f"DAC{ch}_AVDD", "GND")
    S.gl(f"DAC{ch}_AVDD", S.P(cb, "1"), "R", length=1)
    S.gnd_stub(S.P(cb, "2"))
    S.box(8, y0 - 6, 94, y0 + 28, f"ANALOG OUTPUT CH{ch}  -  V/I selectable, TVS +/-14 V  ->  connector pin {3 + ch}")
    S.text(f"VOUT + IOUT one terminal (datasheet 9.1.1.3). +VSENSE = {Bf} OPA197 follower of terminal OUT{ch}_EXT "
           f"(after R{20 + 10 * ch}) via R{21 + 10 * ch}:", (8.5, y0 + 25.6), 1.27)
    S.text("  no +VSENSE 60k leakage in current mode, series-R drop corrected in voltage mode.  "
           f"ISET-R = R{22 + 10 * ch} 15k 0.1%.  SGOOD low = OK.", (8.5, y0 + 27.0), 1.27)
    S.box(95, y0 - 6, 120, y0 + 18, f"CH{ch} DECOUPLING")
    S.text(f"C{35 + 10 * ch}: {Bf} V+.  C{37 + 10 * ch}/C{38 + 10 * ch}: CMP.  D{31 + 10 * ch}: DAC out clamp", (95.5, y0 + 17), 1.27)
S.box(121, 4, 156, 24, "DAC SELECTION  (decision #10)")
for i, t_ in enumerate([
        "U7/U8 fitted: DAC8760 (16-bit, I + V output).",
        "Drop-in alternates (same pinout, no layout change):",
        "  DAC7760  12-bit, I + V  (cost-down, V/I kept)",
        "  DAC8750  16-bit, I only 4-20/0-20/0-24 mA (EE364-equiv.)",
        "  DAC7750  12-bit, I only  (~5 uA/step vs EE364 2 uA)",
        "Current-only (x750): VOUT/+VSENSE/-VSENSE absent -",
        "  check pin handling before fitting (VERIFY).",
]):
    S.text(t_, (121.5, 8.2 + 2.2 * i), 1.27)
S.box(121, 27, 156, 74, "DAC SPI  -  SPI2, SCLK gated per DAC")
for i, t_ in enumerate([
        "DAC8760 rev D: daisy chain removed; multiple devices",
        "need gated SCLK (datasheet 8.5.1.5, Fig. 8-9).",
        "SPI2 mode 3 (CPOL 1, CPHA 1): SCK idles high, so the",
        "OR gate gives no extra edge at LATCH low/high.",
        "DACn_SCLK = DAC_SCK OR DACn_LATCH (PB10 / PB11).",
        "DIN and SDO shared (SDO 3-state after LATCH).",
        "ALARM: open drain, wired-OR, R33 10k pull-up;",
        "  which channel -> read status register.",
]):
    S.text(t_, (121.5, 31.2 + 2.2 * i), 1.27)
S.place("U14", "74LVC2G32", "SN74LVC2G32DCUR", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", 135, 56, nets={
    "1": "DAC_SCK", "2": "DAC1_LATCH", "5": "DAC_SCK", "6": "DAC2_LATCH", "7": "DAC1_SCLK", "3": "DAC2_SCLK",
    "8": "+3V3", "4": "GND"})
S.wa(S.P("U14", "5"), S.P("U14", "1"))              # 1A·2A = DAC_SCK (핀 끝끼리)
for num, net in (("1", "DAC_SCK"), ("2", "DAC1_LATCH"), ("6", "DAC2_LATCH")):
    S.gl(net, S.P("U14", num), "L")
for num, net in (("7", "DAC1_SCLK"), ("3", "DAC2_SCLK")):
    S.gl(net, S.P("U14", num), "R")
S.sup_stub("+3V3", S.P("U14", "8"))
S.gnd_stub(S.P("U14", "4"))
decap(S, "C36", "100n", "C0402", 124, 64, "+3V3")
S.v2("R33", "R", "10k", FP["R0402"], 146, 64, "+3V3", "DAC_ALARM")
S.sup_stub("+3V3", S.P("R33", "1"))
S.gl("DAC_ALARM", S.P("R33", "2"), "D", length=1)

part_table(S, 8, 78, [
    ("U7, U8", "DAC8760IPWP", "아날로그 출력 1·2", "16비트, 4–20 / 0–20 / 0–24 mA · 0–5 / 0–10 V 선택, 내부 기준, 고장 알람 — 대체 DAC7760/8750/7750"),
    ("U9, U10", "TPS26611DDFR", "출력 오결선 보호", "±50 V, 단자 > +Vs 또는 < −0.2 V면 5 µs 차단·자동 복귀, 전류 제한 32 mA, RON 7.5 Ω, SGOOD Low = 정상. +Vs = VAO 16.1 V (벅, 시트 Aux, 결정 #37)"),
    ("R30, R40", "10R pulse (2512)", "서지 전류 제한", "출력 보호기와 TVS 사이 직렬"),
    ("D30, D40", "TVS1401DRBR", "출력 서지 클램프", "±14 V 동작, 클램프 최대 23.55 V @ 30 A/125 C. AO ±28/30 V 지속 오결선 보장 제외 (#41)"),
    ("C41, C51", "1n 100V", "출력 고주파 필터", "케이블로 들어오는 RF 억제"),
    ("U12, U13", "OPA197IDBVR", "+VSENSE 버퍼 (이득 1)", "36 V, 입출력 레일투레일 — 단자 전압을 +VSENSE로, 전류 모드 누설 0. V+ = DAC AVDD"),
    ("R31, R41", "100k", "버퍼 입력 보호", "R30·R40 뒤 단자 전압을 OPA197 + 입력으로 (서지 전류 제한, ±30 V 오배선 9 mW, v0.9)"),
    ("R32, R42", "15k 0.1% 25ppm", "외부 ISET-R (전류 기준)", "내부 저항보다 온도 드리프트 작음 (REXT 비트 설정)"),
    ("R34, R44", "10R", "DAC AVDD 직렬", "VAO → AVDD, 전원 상승 속도 제한 (데이터시트 10장)"),
    ("C47/C48, C57/C58", "4.7n / 100p C0G", "DAC CMP 보상", "VOUT–CMP 4.7 nF + CMP–GND 100 pF (SBAS528D 8.3.2: 470 pF 초과 시 100 pF 추가) — 케이블 용량·보호기 RON 포함 루프 안정 (IVS320 AO rev 1.0)"),
    ("D41, D51", "BAS70-04", "DAC 출력 클램프", "DAC 출력 줄을 GND − 0.3 V ~ AVDD + 0.3 V로 — TPS26611 차단·재연결 순간 DAC 핀 보호 (외부 검수 H03, IVS320과 동일)"),
    ("U14", "SN74LVC2G32DCUR", "DAC별 SCLK 게이트", "OR 2회로: DACn_SCLK = SCK OR LATCHn (SPI2 모드 3)"),
    ("R33", "10k", "ALARM 풀업", "오픈 드레인 ALARM 두 개를 한 선으로 (데이터시트: 외부 10 kΩ)"),
])

# ════════════════════════════ 6. RS-485 ════════════════════════════
S = Sheet("rs485.kicad_sch", "RS-485", "THVD2410 +/-70V fault-protected transceiver", dx=4, dy=4)
SHEETS.append(S)
S.place("U11", "THVD2450", "THVD2410DGKR", "Package_SO:VSSOP-8_3.0x3.0mm_P0.65mm", 30, 21, nets={   # 외부 검수 H02: SOIC → VSSOP (같은 핀), TVS 자리 확보
    "4": "RS485_TX", "1": "RS485_RX", "2": "RS485_DE", "3": "RS485_DE", "8": "+3V3", "6": "RS485_A_EXT",
    "7": "RS485_B_EXT", "5": "GND"})
S.gl("RS485_TX", S.P("U11", "4"), "L", length=2)
S.gl("RS485_RX", S.P("U11", "1"), "L", length=2)
re, de = S.P("U11", "2"), S.P("U11", "3")
S.wa(de, re)                                    # RE·DE 핀 끝끼리
S.gl("RS485_DE", re, "L", length=2)
S.v2("R60", "R", "10k", FP["R0402"], 10, 25, "RS485_DE", "GND")    # v0.9: DE 풀다운 — 리셋·부팅 중 송신 OFF (SLLSF20B 11.1)
S.gl("RS485_DE", S.P("R60", "1"), "U", length=1)
S.gnd_stub(S.P("R60", "2"))
S.sup_stub("+3V3", S.P("U11", "8"), d=2)
S.gnd_stub(S.P("U11", "5"))
S.gl("RS485_A_EXT", S.P("U11", "6"), "R", length=6)
S.gl("RS485_B_EXT", S.P("U11", "7"), "R", length=6)
# v0.9 (외부 검수 H02): 버스 핀 서지 — TVS3301 (±33 V 동작 → ±30 V 오결선 견딤, 최대 42.5 V < THVD2410 ±70 V)
for i_, (ref_, net_) in enumerate((("D60", "RS485_A_EXT"), ("D61", "RS485_B_EXT"))):
    S.v2(ref_, "TVS3301", "TVS3301DRBR", "HMT500_260313A:Texas_DRB0008A_PadFloat", 56 + 8 * i_, 20, net_, "GND")
    S.gl(net_, S.P(ref_, "1"), "U", length=1)
    S.gnd_stub(S.P(ref_, "5"))
decap(S, "C60", "100n", "C0402", 14, 13, "+3V3")
S.box(4, 7, 75, 36, "RS-485  (Modbus RTU)   -   bus pins +/-70 V fault protected")
S.text("No termination on board (fit at bus ends). Fail-safe receiver built in.", (8.5, 34.2), 1.27)
S.text("D60/D61 TVS3301: bus surge (1 kV / 42 ohm ~ 24 A < 27 A), +/-33 V standoff keeps +/-30 V miswiring.", (8.5, 35.5), 1.27)

part_table(S, 8, 40, [
    ("U11", "THVD2410DGKR", "RS-485 (Modbus RTU) 통신", "VSSOP-8 (SOIC와 같은 핀), 3.3 V 반이중 500 kbps (느린 에지 → EMC·반사 유리, v0.9), 버스 핀 ±70 V 고장 보호, IEC ESD 보호 내장, 버스 개방 시 안전 수신"),
    ("R60", "10k", "DE 풀다운", "MCU 리셋·부팅·부트로더 점프 중 송신기 OFF·수신 ON (자체 부트로더 필수, 결정 #31)"),
    ("C60", "100n", "전원 바이패스", "U11 VCC"),
    ("D60, D61", "TVS3301DRBR", "버스 A/B 서지 클램프", "±33 V 평탄 클램프, 최대 42.5 V @ 27 A — THVD2410 ±70 V 안, ±30 V 오결선에 도통 안 함 (외부 검수 H02)"),
])

# ════════════════════════════ 7. 보조 회로 (v0.9) ════════════════════════════
S = Sheet("aux.kicad_sch", "Aux", "AO supply VAO 16.1 V (buck), supply monitor", dx=4, dy=4)
SHEETS.append(S)
# ── AO 전원 VAO 16.1 V (결정 #37, VibrationSensor IVS320 AO rev 1.0과 같은 방식): DAC AVDD·TPS26611 +Vs·OPA197 V+
#   VIN_P(최대 34 V)를 바로 쓰면 DAC 발열(28 V·24 mA 단락 약 0.66 W/채널)과 +Vs(권장 30 V) 여유 문제 → 벅으로 16.1 V 고정.
#   VAO = 0.8 × (1 + 422k/22.1k) = 16.08 V (기준 ±1.5 % → 15.5–16.6 V). VIN_P < 약 17 V는 최대 듀티 98 %로 따라 내려감.
S.place("U15", "LMR51606", "LMR51606YFDBVR", FP["SOT236"], 24, 15, nets={
    "5": "VIN_P", "4": "VIN_P", "1": "VAO_CB", "6": "VAO_SW", "3": "VAO_FB", "2": "GND"})
vin, ven = S.P("U15", "5"), S.P("U15", "4")
S.sup_stub("VIN_P", vin)
S.wa(ven, vin)                                    # EN = VIN (켜짐)
S.gnd_stub(S.P("U15", "2"))
decap(S, "C61", "2.2u 50V", "C0805", 7, 11, "VIN_P")
decap(S, "C62", "100n/50V", "C0603", 15, 11, "VIN_P")
cb, sw = S.P("U15", "1"), S.P("U15", "6")
xc = sw[0] + 3
S.v2("C63", "C", "100n", FP["C0402"], xc - S.dx, sw[1] - 3 - S.dy, "VAO_CB", "VAO_SW")
S.wa(cb, (xc - 1, cb[1]), (xc - 1, sw[1] - 3), S.P("C63", "1"))
S.h2("L3", "L", "22uH", "HMT500_260313A:L_SXN_SMNR4020", xc + 2 - S.dx, sw[1] - S.dy, "VAO_SW", "VAO")
S.wa(sw, S.P("C63", "2"), S.P("L3", "1"))
lo = S.P("L3", "2")
xs = []
for i_, (ref, val, fpk) in enumerate((("C64", "10u 50V", "C1206"), ("C65", "10u 50V", "C1206"),
                                     ("C46", "100n/50V", "C0603"), ("C56", "100n/50V", "C0603"))):
    S.v2(ref, "C", val, FP[fpk], lo[0] + 3 + 5 * i_ - S.dx, lo[1] - S.dy, "VAO", "GND")
    S.gnd_stub(S.P(ref, "2"))
    xs.append(S.P(ref, "1"))
S.wa(lo, *xs, (xs[-1][0] + 3, lo[1]))
S.pw("VAO", (xs[-1][0] + 3, lo[1]), absolute=True)
S.gl("VAO_FB", S.P("U15", "3"), "R", length=1)
S.v2("R51", "R", "422k 1%", FP["R0402"], 60, 8, "VAO", "VAO_FB")
S.sup_stub("VAO", S.P("R51", "1"))
S.v2("R52", "R", "22.1k 1%", FP["R0402"], 60, 13, "VAO_FB", "GND")
S.wa(S.P("R51", "2"), S.P("R52", "1"))
S.gl("VAO_FB", S.P("R52", "1"), "R", length=1)
S.gnd_stub(S.P("R52", "2"))
S.box(4, 4, 68, 27, "AO SUPPLY VAO 16.1 V  -  DC-DC (decision #37)")
S.text("VAO = 0.8 V x (1 + 422k/22.1k) = 16.08 V (15.5-16.6 V). LMR51606 FPWM 1.1 MHz, max duty 98 %.", (4.5, 23.4), 1.27)
S.text("Load 2 x (DAC 27 + OPA197 1.3 + TPS26611 1.75 mA) = 60 mA. C46/C56 at U9/U10 pin 6.", (4.5, 24.8), 1.27)
S.text("VIN_P < ~17 V: VAO follows VIN_P (dropout). 24 mA x 500 ohm OK down to VIN ~15.8 V.", (4.5, 26.2), 1.27)
# ── 전원 전압 감시: VIN_P / 11 → PB0 (ADC_IN8), 32.6 V → 2.96 V ──
S.v2("R14", "R", "100k 1%", FP["R0402"], 72, 10, "VIN_P", "VIN_SENSE")
S.sup_stub("VIN_P", S.P("R14", "1"))
S.v2("R15", "R", "10k 1%", FP["R0402"], 72, 16, "VIN_SENSE", "GND")
S.gnd_stub(S.P("R15", "2"))
S.v2("C30", "C", "100n", FP["C0402"], 82, 16, "VIN_SENSE", "GND")
S.gnd_stub(S.P("C30", "2"))
S.w((72, 13), (72, 16))
S.w((72, 16), (82, 16), (90, 16))
S.gl("VIN_SENSE", S.o((90, 16)), "R", length=0)
S.box(69, 5, 104, 26, "SUPPLY MONITOR")
S.text("VIN_SENSE = VIN_P / 11 -> PB0 (ADC_IN8)", (69.5, 25.0), 1.27)
# v0.9: 검토 권장 DNP 자리(DAC 부스트, HSE 크리스털, 센서선 ESD)는 효과 있는 위치(DAC 핀·MCU OSC 핀·J3 옆)에
#   빈자리가 없어 넣지 않음 (결정 #32) — 대안은 아래 메모
S.box(4, 30, 104, 58, "OPTIONS NOT FITTED ON PCB")
for i_, t_ in enumerate(["DAC8760 IOUT boost: not needed - AVDD = VAO 16.1 V (decision #37) cuts DAC heat",
                         "  from about 0.66 W to 0.39 W per channel (24 mA short, any supply 12-28 V).",
                         "  Thermal test on a potted prototype still planned.",
                         "HSE crystal: no room next to PF0/PF1 -> factory HSI trim + firmware HSI calibration",
                         "  from Modbus frame timing (USART auto-baud / timer capture).",
                         "Sensor-line ESD array: no room next to J3 -> probe ESD test (IEC 61000-4-2) decides;",
                         "  if needed: protect at the HTX99R side or in the next PCB rev."]):
    S.text(t_, (4.5, 34.0 + 2.2 * i_), 1.27)

part_table(S, 4, 62, [
    ("U15", "LMR51606YFDBVR", "AO 전원 VAO 16.1 V 벅", "4–65 V 입력 0.6 A, 1.1 MHz FPWM, SOT-23-6 — DAC AVDD·TPS26611 +Vs·OPA197 V+ 공용 (IVS320 AO rev 1.0과 같은 회로, 결정 #37)"),
    ("L3, C64, C65", "22uH / 10u 50V ×2", "벅 출력", "22 µH 1.05 A 4 × 4 × 2 mm, 10 µF 50 V X7R 1206 × 2 (16 V에서 실효 약 4 µF × 2)"),
    ("R51, R52", "422k / 22.1k 1%", "VAO 설정", "0.8 V × (1 + 422/22.1) = 16.08 V"),
    ("C61, C62, C63", "2.2u 50V / 100n / 100n", "입력·부트스트랩", "VIN 핀 옆 입력 C, CB–SW 100 nF"),
    ("C46, C56", "100n/50V", "+Vs 바이패스", "C46 → U9 6번, C56 → U10 6번 핀 옆"),
    ("R14, R15, C30", "100k / 10k / 100n", "전원 전압 감시", "VIN_P / 11 → PB0 ADC (UVLO 8.9 V ~ DAC 최소 10 V 사이 판정)"),
])

# ════════════════════════════ 출력 ════════════════════════════
ROOT = uid("root")


def prop_pos(p):
    """참조·값 표시 위치(절대 u)."""
    s = SYM[p["sym"]]
    x, y, r = p["x"], p["y"], p["r"]
    if s["kind"] == "ic":
        _, (x1, y1, x2, y2) = ic_geom(s)
        tb = y - y1
        if s["top"]:
            return (x + x2 + 0.5, tb - 1.6, "left"), (x + x2 + 0.5, tb - 0.6, "left")
        return (x + x1, tb - 1.6, "left"), (x + x1, tb - 0.6, "left")
    if s["kind"] in ("pwr", "flag"):
        if s["kind"] == "flag" or s.get("style") == "up":
            return (x, y - 3.2, "center"), (x, y - 2.3, "center")
        if s.get("style") == "rtn":                  # 이름을 기호 오른쪽에 (GND와 구별)
            return (x, y + 0.6, "left"), (x + 0.8, y + 0.7, "left")
        return (x, y + 2.5, "center"), (x, y + 3.0, "center")
    if r in (0, 180):
        return (x + 1.2, y - 0.3, "left"), (x + 1.2, y + 0.7, "left")
    return (x, y - 2.3, "center"), (x, y - 1.3, "center")


def sheet_items(S, sheet_uuid):
    path = f"/{ROOT}/{sheet_uuid}"
    items, used = [], set()
    for ref in S.order:
        p = S.parts[ref]
        used.add(p["sym"])
        s = SYM[p["sym"]]
        key = (S.file, ref)
        (rx, ry, rj), (vx, vy, vj) = S.propxy[ref] if hasattr(S, "propxy") else prop_pos(p)
        hide_ref = s["kind"] in ("pwr", "flag")
        # 180° 회전 부품은 KiCad가 좌우 정렬을 뒤집어 그리므로 미리 뒤집어 둔다
        flipj = {"left": "right", "right": "left", "center": "center"} if p["r"] == 180 else {}
        fx = lambda j: "" if flipj.get(j, j) == "center" else f" (justify {flipj.get(j, j)})"
        fa = 90 if p["r"] in (90, 270) else 0
        hide_val = s["kind"] == "flag" or s.get("style") == "gnd"
        # 구분: 참조번호 = 굵게, 부품값 = 보통, 네트(전원 심볼) 이름 = 기울임 / 신호 네트 = 테두리 있는 전역 라벨
        vstyle = " italic" if s["kind"] == "pwr" else ""
        vface = f' (face "{HANGUL_FACE}")' if has_hangul(p["val"]) else ""
        props = [f'(property "Reference" {q(ref)} (at {mm(rx)} {mm(ry)} {fa}) (effects (font (size {REF_SZ} {REF_SZ}) bold){fx(rj)}{" hide" if hide_ref else ""}))',
                 f'(property "Value" {q(p["val"])} (at {mm(vx)} {mm(vy)} {fa}) (effects (font{vface} (size {VAL_SZ} {VAL_SZ}){vstyle}){fx(vj)}{" hide" if hide_val else ""}))',
                 f'(property "Footprint" {q(("HMT500_260313A:" + p["fp"].split(":")[-1]) if p["fp"] else "")} (at {mm(p["x"])} {mm(p["y"])} 0) {HIDE})',
                 f'(property "Datasheet" "~" (at {mm(p["x"])} {mm(p["y"])} 0) {HIDE})']
        if s.get("verify"):
            props.append(f'(property "VERIFY" "YES - pin numbers are placeholders" (at {mm(p["x"])} {mm(p["y"])} 0) {HIDE})')
        bom = "no" if s["kind"] in ("pwr", "flag") else "yes"
        pu = " ".join(f"(pin {q(pp[0])} (uuid {uid(key, 'pin', pp[0])}))" for pp in pins_of(p["sym"]))
        items.append(f"(symbol (lib_id {q(LIB + ':' + p['sym'])}) (at {mm(p['x'])} {mm(p['y'])} {p['r']}) (unit 1) "
                     f"(in_bom {bom}) (on_board {bom}) (dnp {'yes' if p['kw'].get('dnp') else 'no'}) (uuid {uid(key, 'sym')}) " + " ".join(props) +
                     f" {pu} (instances (project {q(PROJECT)} (path {q(path)} (reference {q(ref)}) (unit 1)))))")
    for i, (a, b) in enumerate(S.wires):
        items.append(f"(wire (pts (xy {mm(a[0])} {mm(a[1])}) (xy {mm(b[0])} {mm(b[1])})) (stroke (width 0) (type default)) (uuid {uid(S.file, 'w', i)}))")
    shapes = label_shapes(S)
    for i, (net, pt, ang, kind) in enumerate(S.labels):
        just = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
        items.append(f"(global_label {q(net)} (shape {shapes[i]}) (at {mm(pt[0])} {mm(pt[1])} {ang}) (fields_autoplaced) "
                     f"(effects (font (size 1.27 1.27)) (justify {just})) (uuid {uid(S.file, 'gl', i)}) "
                     f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {mm(pt[0])} {mm(pt[1])} 0) {HIDE}))')
    for i, pt in enumerate(S.ncs):
        items.append(f"(no_connect (at {mm(pt[0])} {mm(pt[1])}) (uuid {uid(S.file, 'nc', i)}))")
    for i, pt in enumerate(junctions(S)):
        items.append(f"(junction (at {mm(pt[0])} {mm(pt[1])}) (diameter 0) (color 0 0 0 0) (uuid {uid(S.file, 'j', i)}))")
    for i, (a, b) in enumerate(S.boxes):
        items.append(f"(rectangle (start {mm(a[0])} {mm(a[1])}) (end {mm(b[0])} {mm(b[1])}) "
                     f"(stroke (width 0.1524) (type dash) (color 72 72 160 1)) (fill (type none)) (uuid {uid(S.file, 'box', i)}))")
    for i, (t, pt, size, bold) in enumerate(S.texts):
        face = f' (face "{HANGUL_FACE}")' if has_hangul(t) else ""
        items.append(f"(text {q(ko_safe(t))} (at {mm(pt[0])} {mm(pt[1])} 0) (effects (font{face} (size {size} {size}){' bold' if bold else ''}) "
                     f"(justify left bottom)) (uuid {uid(S.file, 'txt', i)}))")
    return items, used


def all_pins(S):
    out = []
    for ref in S.order:
        p = S.parts[ref]
        for num, nm, t, px, py, ang in pins_of(p["sym"]):
            rx, ry = rot(px, py, p["r"])
            out.append(((round(p["x"] + rx, 3), round(p["y"] - ry, 3)), ref, num, t))
    return out


DRV_T = ("output", "tri_state", "open_collector", "power_out")


# 수동 소자만 있는 넷의 신호 흐름 (주는 쪽 부품): 아날로그 출력 → 커넥터, 커넥터 → eFuse, 분압 → 벅 FB
FLOW = {"OUT1_EXT": ("R30",), "OUT2_EXT": ("R40",), "VIN_F": ("R1",), "BUCK_FB": ("R8",)}


def net_roles():
    """넷별 (주는 쪽, 받는 쪽) 핀 집합 {(시트 파일, ref, 핀)}.
    출력·3상태·오픈드레인 핀이 있으면 그것이 주는 쪽, 입력·양방향(MCU)이 받는 쪽.
    출력이 없고 입력과 양방향(MCU GPIO)만 있으면 MCU가 주는 쪽. 수동 소자만 있으면 방향 없음."""
    ends = {}
    for S in SHEETS:
        for ref, m in S.nets.items():
            types = {pn: ty for pn, nm, ty, *_ in pins_of(S.parts[ref]["sym"])}
            for pin, net in m.items():
                ends.setdefault(net, []).append(((S.file, ref, pin), types.get(pin, P)))
    roles = {}
    for net, es in ends.items():
        if net in FLOW:
            drv = {k for k, ty in es if k[1] in FLOW[net]}
            roles[net] = (drv, {k for k, ty in es} - drv, False)
            continue
        drv = {k for k, ty in es if ty in DRV_T}
        rcv = {k for k, ty in es if ty in (I, B)}
        if not drv and any(ty == I for _, ty in es) and any(ty == B for _, ty in es):
            drv = {k for k, ty in es if ty == B}
            rcv = {k for k, ty in es if ty == I}
        roles[net] = (drv, (rcv - drv) if drv else set(), any(ty == B for _, ty in es))
    return roles


def label_shapes(S):
    """라벨마다 KiCad 모양: 주는 쪽 = output, 받는 쪽 = input, 양방향 = bidirectional, 그 밖 = passive."""
    roles = net_roles()
    at = {}
    for pt, ref, num, _ in all_pins(S):
        at.setdefault(pt, []).append((S.file, ref, num))
    out = []
    for (net, pt, ang, kind), src in zip(S.labels, S.label_src):
        drv, rcv, bi = roles.get(net, (set(), set(), False))
        here = at.get(rp(src), [])
        if any(k in drv for k in here):
            sh = "output"
        elif any(k in rcv for k in here):
            sh = "input"
        elif any(k[0] == S.file for k in drv):
            sh = "output"
        elif any(k[0] == S.file for k in rcv):
            sh = "input"
        else:
            sh = "bidirectional" if bi else "passive"
        out.append(sh)
    return out


def rp(pt):
    return (round(pt[0], 3), round(pt[1], 3))


def junctions(S):
    cnt = {}
    for a, b in S.wires:
        for e in (rp(a), rp(b)):
            cnt[e] = cnt.get(e, 0) + 1
    for pt, ref in {(pt, ref) for pt, ref, *_ in all_pins(S)}:   # 겹친 핀(같은 부품)은 한 번만
        if pt in cnt:
            cnt[pt] += 1
    return sorted(pt for pt, c in cnt.items() if c >= 3)


def validate(S):
    errs = []
    ends = {}
    for a, b in S.wires:
        for e in (rp(a), rp(b)):
            ends[e] = ends.get(e, 0) + 1
    pins = all_pins(S)
    pinpts = {}
    for pt, ref, num, t in pins:
        pinpts.setdefault(pt, []).append((ref, num))
    lblpts = {rp(l[1]) for l in S.labels}
    ncpts = {rp(p) for p in S.ncs}
    conn = set(ends) | set(pinpts) | lblpts
    for a, b in S.wires:
        a, b = rp(a), rp(b)
        for pt in conn:
            if pt in (a, b):
                continue
            if a[0] == b[0] == pt[0] and min(a[1], b[1]) < pt[1] < max(a[1], b[1]):
                errs.append(f"point {pt} inside vertical wire {a}-{b}")
            if a[1] == b[1] == pt[1] and min(a[0], b[0]) < pt[0] < max(a[0], b[0]):
                errs.append(f"point {pt} inside horizontal wire {a}-{b}")
    for pt, ref, num, t in pins:
        others = len(pinpts[pt]) - 1 + ends.get(pt, 0) + (pt in lblpts) + (pt in ncpts)
        if others == 0:
            errs.append(f"dangling pin {ref}.{num} at {pt}")
    for l in S.labels:
        if rp(l[1]) not in ends and rp(l[1]) not in pinpts:
            errs.append(f"floating label {l[0]} at {l[1]}")
    W, H = {"A3": (165.3, 116.9), "A4": (116.9, 82.7)}[S.paper]
    for (x, y) in list(ends) + list(pinpts) + [rp(t[1]) for t in S.texts]:
        if x < 4.5 or y < 4.5 or x > W - 4.5 or y > H - 4.5:
            errs.append(f"off-page point {(x, y)}")
        if x > W - 48 and y > H - 17:
            errs.append(f"title-block collision {(x, y)}")
    errs += place_props(S) + overlap_errors(S) + pin_name_errors()
    if errs:
        msg = f"{S.file}:\n  " + "\n  ".join(sorted(set(errs))[:60])
        if os.environ.get("HMT_DRAFT"):          # 작도 확인용: 오류를 보여 주고 파일은 씀
            print(msg)
        else:
            raise SystemExit(msg)


# ════════════════════════════ 글자 배치·겹침 검사 ════════════════════════════
# 단위 u(2.54 mm), y 아래로 +. 글자 폭은 KiCad 기본 글꼴 실측(문자당 약 1.05 × 글자 크기).
def text_rect(t, x, y, size, just="left", bold=False, valign="center"):
    w, h = text_w(t, size, bold), size * 1.2 / U
    x0 = {"left": x, "center": x - w / 2, "right": x - w}[just]
    y0 = {"center": y - h / 2, "bottom": y - h}[valign]
    return (x0, y0, x0 + w, y0 + h)


def _hit(a, b, pad=0.05):
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


TWO_HW = {"rect": 0.45, "cap": 0.85, "ind": 0.35, "ferrite": 0.45, "tvs": 0.75, "gdt": 0.85, "led": 1.05, "zener": 0.85, "schottky": 0.85}


def part_rects(p):
    """부품 몸체·핀·핀 번호가 차지하는 영역 (절대 u)."""
    s = SYM[p["sym"]]
    x, y, r = p["x"], p["y"], p["r"]
    k = s["kind"]
    out = []
    if k == "ic":
        pins, (x1, y1, x2, y2) = ic_geom(s)
        out.append((x + x1, y - y1, x + x2, y - y2))
        for num, nm, t, px, py, ang in pins:
            X, Y = x + px, y - py
            if ang in (0, 180):
                out.append((min(X, x + (x1 if ang == 0 else x2)), Y - 0.45, max(X, x + (x1 if ang == 0 else x2)), Y + 0.45))
            else:
                ey = y - (y1 if ang == 270 else y2)
                out.append((X - 0.45, min(Y, ey), X + 0.45, max(Y, ey)))
        return out
    if k == "pwr":
        st = s["style"]
        if st == "up":
            return [(x - 0.35, y - 0.55, x + 0.35, y)]
        if st in ("gnd", "rtn"):
            return [(x - 0.55, y, x + 0.55, y + 1.05)]
        return [(x - 1.05, y, x + 0.8, y + 1.05)]
    if k == "flag":
        return [(x - 0.45, y - 1.05, x + 0.45, y)]
    hw = TWO_HW[s["draw"]]
    return [(x - hw, y - 1.5, x + hw, y + 1.5)] if r in (0, 180) else [(x - 1.5, y - hw, x + 1.5, y + hw)]


def fixed_rects(S):
    """배치를 바꾸지 않는 요소: 몸체, 선, 라벨, 비연결 표시, 메모 글, 박스 테두리, 전원 심볼 글자."""
    R = []
    for ref in S.order:
        p = S.parts[ref]
        R += [(r_, "body " + ref) for r_ in part_rects(p)]
        s = SYM[p["sym"]]
        if s["kind"] == "pwr" and s["style"] != "gnd":
            (_, _, _), (vx, vy, vj) = prop_pos(p)
            R.append((text_rect(p["val"], vx, vy, VAL_SZ, vj), "net " + p["val"]))
    for a, b in S.wires:
        R.append(((min(a[0], b[0]) - 0.08, min(a[1], b[1]) - 0.08, max(a[0], b[0]) + 0.08, max(a[1], b[1]) + 0.08), "wire"))
    for net, pt, ang, kind in S.labels:
        L = text_w(net, 1.27) + 0.9
        x, y = pt
        rr = {0: (x, y - 0.4, x + L, y + 0.4), 180: (x - L, y - 0.4, x, y + 0.4),
              90: (x - 0.4, y - L, x + 0.4, y), 270: (x - 0.4, y, x + 0.4, y + L)}[ang]
        R.append((rr, "label " + net))
    for pt in S.ncs:
        R.append(((pt[0] - 0.3, pt[1] - 0.3, pt[0] + 0.3, pt[1] + 0.3), "nc"))
    for t, pt, size, bold in S.texts:
        R.append((text_rect(t, pt[0], pt[1], size, "left", bold, "bottom"), "text " + t[:24]))
    for a, b in S.boxes:
        x0, y0, x1, y1 = a[0], a[1], b[0], b[1]
        for e in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
            R.append(((e[0] - 0.05, e[1] - 0.05, e[2] + 0.05, e[3] + 0.05), "box"))
    return R


def prop_candidates(p):
    """(ref, val) 글자 위치 후보 [(x, y, just), (x, y, just)]. 가까운 것부터."""
    s = SYM[p["sym"]]
    x, y, r = p["x"], p["y"], p["r"]
    c = []
    if s["kind"] == "ic":
        pins, (x1, y1, x2, y2) = ic_geom(s)
        top, bot = y - y1, y - y2
        up = 1.4 if s["top"] else 0
        for dy in (0, 1, 2, 3):
            c.append(((x + x1, top - 1.5 - up - dy, "left"), (x + x1, top - 0.6 - up - dy, "left")))
            c.append(((x + x2 + 0.6, top - 1.5 - dy, "left"), (x + x2 + 0.6, top - 0.6 - dy, "left")))
            c.append(((x + x1, bot + 0.9 + (1.4 if s["bottom"] else 0) + dy, "left"),
                      (x + x1, bot + 1.8 + (1.4 if s["bottom"] else 0) + dy, "left")))
            c.append(((x + x2 + 0.6, bot + 0.6 + dy, "left"), (x + x2 + 0.6, bot + 1.5 + dy, "left")))
        return c
    hw = TWO_HW[s["draw"]]
    if r in (0, 180):
        for dy in (0, -1.0, 1.0, -2.0, 2.0, -3.0, 3.0):
            for g in (0.5, 1.5, 2.5):
                c.append(((x + hw + g, y - 0.45 + dy, "left"), (x + hw + g, y + 0.45 + dy, "left")))
                c.append(((x - hw - g, y - 0.45 + dy, "right"), (x - hw - g, y + 0.45 + dy, "right")))
        for dx in (0, 1.5, -1.5, 3.0, -3.0):          # 좁은 곳: 몸체 위·아래
            c.append(((x + dx, y + 2.1, "center"), (x + dx, y + 3.0, "center")))
            c.append(((x + dx, y - 3.0, "center"), (x + dx, y - 2.1, "center")))
        return c
    for dx in (0, 1.0, -1.0, 2.0, -2.0, 3.0, -3.0, 4.0, -4.0):
        for g in (0.5, 1.5):
            c.append(((x + dx, y - hw - g - 0.95, "center"), (x + dx, y - hw - g - 0.05, "center")))
            c.append(((x + dx, y + hw + g + 0.05, "center"), (x + dx, y + hw + g + 0.95, "center")))
    return c


def place_props(S):
    """참조·값 글자를 몸체·선·라벨·다른 글자와 겹치지 않는 첫 후보에 놓는다. 못 놓으면 오류."""
    fixed = fixed_rects(S)
    placed, errs = [], []
    S.propxy = {}
    for ref in S.order:
        p = S.parts[ref]
        s = SYM[p["sym"]]
        if s["kind"] in ("pwr", "flag"):
            S.propxy[ref] = prop_pos(p)
            continue
        own = part_rects(p)
        ok = None
        for (rx, ry, rj), (vx, vy, vj) in prop_candidates(p):
            rr = text_rect(ref, rx, ry, REF_SZ, rj, True)
            vr = text_rect(p["val"], vx, vy, VAL_SZ, vj)
            if any(_hit(t, o) for t in (rr, vr) for o, _ in fixed) or any(_hit(t, o) for t in (rr, vr) for o in placed):
                continue
            ok = ((rx, ry, rj), (vx, vy, vj))
            placed += [rr, vr]
            break
        if ok is None:
            errs.append(f"no free place for {ref} ({p['val']})")
            ok = prop_pos(p)
        S.propxy[ref] = ok
    return errs


def pin_name_errors():
    """IC 몸체 안 핀 이름끼리 겹침 (심볼 정의 단위)."""
    errs = []
    for name, s in SYM.items():
        if s["kind"] != "ic":
            continue
        pins, (x1, y1, x2, y2) = ic_geom(s)
        rr = []
        for num, nm, t, px, py, ang in pins:
            if not nm or nm == "~":
                continue
            w = text_w(nm.replace("~{", "").replace("}", ""), 1.27)
            h = 0.5
            if ang == 0:          # 왼쪽 핀: 이름은 몸체 왼쪽 안
                r_ = (x1 + 0.2, -py - h / 2, x1 + 0.2 + w, -py + h / 2)
            elif ang == 180:
                r_ = (x2 - 0.2 - w, -py - h / 2, x2 - 0.2, -py + h / 2)
            elif ang == 270:      # 위쪽 핀: 세로 글자, 위에서 아래로
                r_ = (px - h / 2, -y1 + 0.2, px + h / 2, -y1 + 0.2 + w)
            else:
                r_ = (px - h / 2, -y2 - 0.2 - w, px + h / 2, -y2 - 0.2)
            rr.append((r_, nm))
        for i, (a, na) in enumerate(rr):
            for b, nb in rr[i + 1:]:
                if _hit(a, b, pad=-0.02):
                    errs.append(f"symbol {name}: pin name {na} overlaps {nb}")
    return errs


def overlap_errors(S):
    """고정 요소끼리의 글자 겹침 (메모 글·라벨·전원 이름이 선·몸체·다른 글자와)."""
    R = fixed_rects(S)
    errs = []
    txt = [(r_, n) for r_, n in R if n.startswith(("text", "net ", "label"))]
    for i, (a, na) in enumerate(txt):
        for b, nb in R:
            if b is a or nb == na:
                continue
            if nb.startswith("box") and na.startswith("text"):
                continue                      # 박스 제목은 테두리 안쪽에 붙음
            if na.startswith("label") and nb == "wire":
                continue                      # 라벨은 선 끝에 붙음
            if na.startswith("net ") and nb in ("wire",) :
                continue
            if _hit(a, b, pad=-0.02):
                errs.append(f"{na} overlaps {nb}")
    PW, PH = {"A3": (165.3, 116.9), "A4": (116.9, 82.7)}[S.paper]
    tb = (PW - 48, PH - 17, PW, PH)
    for r_, n in txt:                                 # 글자가 용지 밖·표제란으로 넘어가지 않게
        if r_[2] > PW - 4.5 or r_[3] > PH - 4.5 or _hit(r_, tb, pad=0):
            errs.append(f"{n} off page / in title block")
    for a0, a1 in S.boxes:
        if _hit((a0[0], a0[1], a1[0], a1[1]), tb, pad=0) or a1[0] > PW - 4.5 or a1[1] > PH - 4.5:
            errs.append(f"box {a0} off page / in title block")
    for i, (a0, a1) in enumerate(S.boxes):          # 박스끼리 겹침 금지
        for b0, b1 in S.boxes[i + 1:]:
            if _hit((a0[0], a0[1], a1[0], a1[1]), (b0[0], b0[1], b1[0], b1[1]), pad=-0.1):
                errs.append(f"box {a0} overlaps box {b0}")
    bodies = [(r_, n) for r_, n in R if n.startswith("body") and not n.startswith("body #")]
    for a, na in bodies:                        # 부품 몸체가 박스 테두리·다른 몸체·글자와 겹침
        for b, nb in R:
            if nb == na or nb.startswith(("wire", "label", "nc", "body #")):
                continue
            if _hit(a, b, pad=-0.02):
                errs.append(f"{na} overlaps {nb}")
    # 선이 부품 몸체를 지나가면 안 됨 (핀 끝에서 닿는 것은 허용: 몸체를 0.15 줄여서 판정)
    wires = [((min(p_[0], q_[0]), min(p_[1], q_[1]), max(p_[0], q_[0]), max(p_[1], q_[1])), (p_, q_)) for p_, q_ in S.wires]
    for a, na in bodies:
        inner = (a[0] + 0.15, a[1] + 0.15, a[2] - 0.15, a[3] - 0.15)
        for w_, seg in wires:
            if inner[0] < inner[2] and inner[1] < inner[3] and _hit(w_, inner, pad=0):
                errs.append(f"wire {seg} crosses {na}")
    # 전원 기호·PWR_FLAG가 다른 부품 몸체와 겹치면 안 됨
    for a, na in [(r_, n) for r_, n in R if n.startswith("body #")]:
        for b, nb in bodies:
            if _hit(a, b, pad=-0.02):
                errs.append(f"{na} overlaps {nb}")
    return errs


def wire_metrics(S):
    """(꺾임 수, 분기점 수): 꺾임 = 핀·라벨이 아닌 점에서 선 두 개가 직각으로 만남."""
    ends = {}
    for a_, b_ in S.wires:
        a_, b_ = rp(a_), rp(b_)
        d = "h" if a_[1] == b_[1] else "v"
        ends.setdefault(a_, []).append(d)
        ends.setdefault(b_, []).append(d)
    pins = {pt for pt, *_ in all_pins(S)}
    lbl = {rp(l[1]) for l in S.labels}
    bends = [pt for pt, ds in ends.items() if len(ds) == 2 and pt not in pins and pt not in lbl and ds[0] != ds[1]]
    return len(bends), len(junctions(S))


def title_block(title):
    return (f'(title_block (title {q(PROJECT + "  " + title)}) (date "2026-10-01") (rev "0.10") '
            f'(company "DOTECH Co., Ltd.") (comment 1 "Project No. {PROJECT}  -  {PRODUCT} oil moisture transmitter") '
            f'(comment 2 "Design notes: docs/hw/circuit-design.md") '
            f'(comment 3 "Pinouts checked vs manufacturer datasheets 2026-09-30 (STM32: KiCad lib)"))')


def write_all():
    from gen_artwork_footprints import generate
    generate()
    os.makedirs(OUT, exist_ok=True)
    uuids = []
    for S in SHEETS:
        validate(S)
        su = uid("sheet", S.file)
        uuids.append(su)
        items, used = sheet_items(S, su)
        libs = "\n".join(lib_symbol(n, True) for n in sorted(used))
        open(os.path.join(OUT, S.file), "w", encoding="utf-8").write(
            f"(kicad_sch (version 20230121) (generator eeschema) (uuid {uid('file', S.file)}) (paper \"{S.paper}\")\n"
            f"{title_block(S.title)}\n(lib_symbols\n{libs}\n)\n" + "\n".join(items) + "\n)\n")
    # 최상위 시트
    items = []
    for i, (S, su) in enumerate(zip(SHEETS, uuids)):
        sx, sy = 8 + (i % 4) * 38, 14 + (i // 4) * 24     # v0.9: 7장 → 4열 2줄 (메모가 용지 안에 들어가게)
        items.append(f"(sheet (at {mm(sx)} {mm(sy)}) (size {mm(34)} {mm(16)}) (fields_autoplaced) "
                     f"(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid {su}) "
                     f'(property "Sheetname" {q(f"{i + 1}. {S.title}")} (at {mm(sx)} {mm(sy - 0.3)} 0) (effects (font (size 1.8 1.8) bold) (justify left bottom))) '
                     f'(property "Sheetfile" {q(S.file)} (at {mm(sx)} {mm(sy + 16.3)} 0) (effects (font (size 1.27 1.27)) (justify left top))) '
                     f'(instances (project {q(PROJECT)} (path {q("/" + ROOT)} (page {q(str(i + 2))})))))')
        lines, cur = [], ""
        for w in S.desc.split(" "):                      # 상자 폭(34)에 맞게 줄바꿈
            if cur and len(cur) + 1 + len(w) > 38:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        for k, t in enumerate(lines):
            items.append(f"(text {q(t)} (at {mm(sx + 1)} {mm(sy + 6 + 2.2 * k)} 0) (effects (font (size 1.4 1.4)) (justify left bottom)) (uuid {uid('rootdesc', i * 10 + k)}))")
    notes = [
        (f"DOTECH {PRODUCT}  -  Oil Moisture Transmitter  -  Schematic v0.9  -  Project No. {PROJECT}", 2.5, True),
        (f"File names (schematic, PCB, Gerber) = {PROJECT}.*   PCB silkscreen marking = {PROJECT}", 1.4, False),
        ("Signal flow: J1 field connector -> protection -> eFuse -> 5 V buck -> 3.3 V LDO; sensor head J3 -> PCAP04 / ADS1220 -> MCU -> DAC8760 x2 / THVD2410 -> J1", 1.4, False),
        ("Outputs: RS-485 Modbus RTU + 2x analog (4-20 mA / 0-20 mA / 0-10 V / 0-5 V selectable).  Supply 12-28 V DC.", 1.4, False),
        ("v0.10: AO D30/D40 TVS1401 +/-14 V. AO +/-28/30 V continuous miswiring is NOT guaranteed (#41).", 1.4, False),
        ("Power symbols: GND, +3V3, +3V3A (analog 3.3 V), +5V, VIN_P (protected input), CHASSIS.  Inter-sheet signals: global labels.", 1.4, False),
        ("History v0.3-v0.8 (MCU G0B1, JST harness, DAC8760/TPS26611 datasheet pinouts, RTN isolation, gated DAC SCLK ...): docs/decision-log.md #9-#26.", 1.4, False),
        ("v0.9: 3-pass review (docs/hw/final-review-260313A.md): OVP 32.6 V (R5 36.5k); AO supply VAO 16.1 V buck U15 (DAC AVDD, TPS26611 +Vs; dec. #37, IVS320 AO); D3 series Schottky; RS-485 TVS D60/D61; D2 -> TVS3301; eFuse IN C2; buck CIN;", 1.4, False),
        ("      RS485_DE 10k pull-down (in-house bootloader, dec. #31); THVD2410; X7R only; R2 HV 1206; SGOOD -> PA0/PA4; CS_CDC -> PA15; VIN_SENSE PB0;", 1.4, False),
        ("      LATCH/CS pull-ups; OPA197 V+ = DAC AVDD; R31/R41 100k; SWD no-connect flags removed; sheet Aux: +Vs clamp, VIN monitor (DAC boost / HSE / sensor ESD: no room, dec. #32).", 1.4, False),
        ("Footprints: KiCad 7.0.11 library + project library HMT500_260313A (GDT Bourns 2035-xx-SM, TVS3301 pad floating).", 1.4, False),
        ("표기 규칙: 부품번호 = 굵은 글자 (R1, U4) / 부품값 = 보통 글자 (10k, DAC8760) / 전원 네트 = 기울인 글자 (+3V3, VIN_P)", 1.4, False),
        ("         신호 네트 = 테두리 있는 라벨 (SPI_SCK, OUT1_EXT) - 네트 이름은 부품번호·부품명과 겹치지 않게 지음", 1.4, False),
        ("         라벨 모양 = 신호 방향: 뾰족한 쪽이 밖 = 이 시트에서 내보냄(출력), 안 = 받음(입력), 양쪽 = 양방향, 네모 = 아날로그·수동", 1.4, False),
        ("글자 겹침: 생성기가 부품 몸체·핀·선·라벨·메모와 겹치지 않는 자리에 자동 배치하고, 겹치면 생성 실패로 처리", 1.4, False),
    ]
    y = 58
    for i, (t, size, bold) in enumerate(notes):
        face = f' (face "{HANGUL_FACE}")' if has_hangul(t) else ""
        items.append(f"(text {q(t)} (at {mm(12)} {mm(y)} 0) (effects (font{face} (size {size} {size}){' bold' if bold else ''}) (justify left bottom)) (uuid {uid('note', i)}))")
        y += 3.2 if i == 0 else 2.2
    open(os.path.join(OUT, PROJECT + ".kicad_sch"), "w", encoding="utf-8").write(
        f"(kicad_sch (version 20230121) (generator eeschema) (uuid {ROOT}) (paper \"A3\")\n{title_block('Top')}\n"
        "(lib_symbols)\n" + "\n".join(items) + '\n(sheet_instances (path "/" (page "1")))\n)\n')
    # 라이브러리, 프로젝트
    body = "\n".join(lib_symbol(n, False) for n in SYM)
    open(os.path.join(OUT, PROJECT + ".kicad_sym"), "w", encoding="utf-8").write(
        f"(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n{body}\n)\n")
    open(os.path.join(OUT, "sym-lib-table"), "w").write(
        f'(sym_lib_table\n  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJECT}.kicad_sym")(options "")(descr "{PROJECT} project symbols"))\n)\n')
    open(os.path.join(OUT, "fp-lib-table"), "w").write(         # 프로젝트 풋프린트 (KiCad 7.0.11 복사본 + 자체 3종)
        f'(fp_lib_table\n  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/../lib/{LIB}.pretty")(options "")(descr "{PROJECT} footprints"))\n)\n')
    pro_path = os.path.join(OUT, PROJECT + ".kicad_pro")
    pro = json.load(open(pro_path)) if os.path.exists(pro_path) else {}   # PCB 설계 규칙(place_pcb.py)은 유지
    pro.update({"meta": {"filename": PROJECT + ".kicad_pro", "version": 1},
                "sheets": [[ROOT, "Root"]] + [[u_, S.title] for S, u_ in zip(SHEETS, uuids)]})
    open(pro_path, "w").write(json.dumps(pro, indent=2) + "\n")
    # BOM
    groups = {}
    for S in SHEETS:
        for ref in S.order:
            if ref.startswith("#"):
                continue
            p = S.parts[ref]
            groups.setdefault((p["sym"], p["val"], p["fp"]), []).append(ref)

    def rk(r):
        return (r.rstrip("0123456789"), int("0" + "".join(c for c in r if c.isdigit())))

    with open(os.path.join(OUT, PROJECT + "_BOM.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["Qty", "References", "Symbol", "Value", "Footprint", "Verify"])
        for (sym, val, fp), refs in sorted(groups.items(), key=lambda kv: rk(sorted(kv[1], key=rk)[0])):
            wr.writerow([len(refs), " ".join(sorted(refs, key=rk)), sym, val, fp,
                         "pin numbers" if SYM[sym].get("verify") else ("footprint" if fp.startswith("TBD") else "")])


def intended_nets():
    """설계 의도 넷: {이름: {(ref, pin)}}"""
    nets = {}
    for S in SHEETS:
        for ref, m in S.nets.items():
            for pin, net in m.items():
                if net:
                    nets.setdefault(net, set()).add((ref, pin))
    return nets


if __name__ == "__main__":
    write_all()
    n = intended_nets()
    print("sheets:", len(SHEETS), "parts:", sum(1 for S in SHEETS for r in S.order if not r.startswith("#")),
          "nets:", len(n))
