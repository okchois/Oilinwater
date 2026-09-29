"""DOTECH HMT500 KiCad 회로도 생성기 v0.3 — 배치·배선된 정식 회로도.

python3 hardware/kicad/gen_hmt500.py  →  hardware/kicad/HMT500/

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

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "HMT500")
PROJECT = LIB = "HMT500"
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


def text_w(t, size, bold=False):
    w = sum((1.0 if has_hangul(ch) else 1.05) for ch in str(t)) * size / U
    return w * (1.08 if bold else 1.0)


FONT = "(effects (font (size 1.27 1.27)))"
HIDE = "(effects (font (size 1.27 1.27)) hide)"
ST = "(stroke (width 0.254) (type default))"

# ════════════════════════════ 심볼 정의 ════════════════════════════
SYM = {}


def ic(name, left=(), right=(), top=(), bottom=(), w=8, prefix="U", verify=False, desc="", ts=2, toff=0):
    SYM[name] = dict(kind="ic", left=list(left), right=list(right), top=list(top), bottom=list(bottom),
                     w=w, prefix=prefix, verify=verify, desc=desc, ts=ts, toff=toff)


def two(name, prefix, draw, desc):
    SYM[name] = dict(kind="two", prefix=prefix, draw=draw, desc=desc)


def pwr(name, style, desc):
    SYM[name] = dict(kind="pwr", prefix="#PWR", style=style, desc=desc)


two("R", "R", "rect", "Resistor")
two("C", "C", "cap", "Capacitor")
two("L", "L", "ind", "Inductor")
two("FB", "FB", "ferrite", "Ferrite bead")
two("TVS_BI", "D", "tvs", "Bidirectional TVS diode")
two("GDT", "GDT", "gdt", "Gas discharge tube")
two("LED", "D", "led", "LED (pin1 = K, pin2 = A)")
SYM["PWR_FLAG"] = dict(kind="flag", prefix="#FLG", desc="Power flag")
for n in ("+3V3", "+3V3A", "+5V", "VIN_P", "VDDA"):
    pwr(n, "up", f"Power symbol {n}")
pwr("GND", "gnd", "Ground")
pwr("CHASSIS", "chassis", "Chassis / housing (earth via process pipe)")

B, I, O, P, PI, PO, OC, T, NC = ("bidirectional", "input", "output", "passive", "power_in", "power_out",
                                 "open_collector", "tri_state", "no_connect")

ic("CONN_GH8", right=[("8", "V+", P), ("6", "GND", P), ("4", "OUT1", P), ("5", "OUT2", P), ("3", "RS485_A", P),
                      ("2", "RS485_B", P), ("1", "NC", P), ("7", "NC", P)],
   w=6, prefix="J", desc="JST GH 1.25 mm 8-pin side-entry header. Harness W-2 to M12 8P field connector (pin n = M12 pin n)")
ic("CONN_CH", right=[("1", "CHASSIS", P)], w=6, prefix="J",
   desc="PCB-to-housing chassis contact (spring finger on PCB edge). P/N TBD")
ic("CMC", left=[("1", "", P), ("3", "", P)], right=[("2", "", P), ("4", "", P)], w=4, prefix="L",
   desc="2-line common mode choke")
ic("TPS2660", left=[("1", "IN", PI), ("2", "IN", P), ("3", "UVLO", I), ("5", "OVP", I), ("7", "~{SHDN}", I),
                   ("6", "MODE", I), ("4", "NC", NC)],
   right=[("15", "OUT", PO), ("16", "OUT", P), ("14", "~{FLT}", OC), ("11", "ILIM", P), ("10", "IMON", P),
          ("12", "dVdT", P), ("13", "NC", NC)],
   bottom=[("9", "GND", PI), ("8", "RTN", P), ("17", "EP", P)], w=8, verify=True,
   desc="TI TPS26600PWP 60V eFuse, HTSSOP-16 (pinout: KiCad TPS26600PWP). VERIFY RTN/GND wiring for reverse polarity")
ic("LMR36006", left=[("1", "VIN", PI), ("2", "EN", I), ("3", "PG", OC), ("4", "FB", I)],
   right=[("7", "BOOT", P), ("6", "SW", PO), ("8", "VCC", P)], bottom=[("5", "AGND", PI), ("9", "PGND", PI)],
   w=8, verify=True, desc="TI LMR36006 60V 0.6A buck. PIN NUMBERS ARE PLACEHOLDERS")
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
ic("CONN_SWD", left=[("1", "VCC", P), ("2", "SWDIO", P), ("4", "SWCLK", P), ("6", "SWO", P), ("3", "NRST", P),
                     ("5", "GND", P)], w=6, prefix="J", desc="Tag-Connect TC2030 SWD")
ic("CONN_SH4", right=[("1", "SENS_1", P), ("2", "SENS_2", P), ("3", "PT+", P), ("4", "PT-", P)], w=6, prefix="J",
   desc="JST SH 1.0 mm 4-pin side-entry (right angle) header. Sensor harness W-1 direct from HTX99R connector (MK sensor + Pt1000 2-wire)")
ic("PCAP04", left=[("6", "PC1", P), ("5", "PC0", P), ("7", "PC2", P), ("8", "PC3", P), ("9", "PC4", P),
                   ("10", "PC5", P), ("11", "PCAUX", P), ("12", "PT0REF", P), ("13", "PT1", P), ("14", "PT2", P),
                   ("15", "PT3", P), ("22", "PG0", B), ("23", "PG1", B)],
   right=[("16", "SSN", I), ("17", "SCK", I), ("18", "MOSI", I), ("19", "MISO", T), ("20", "INTN", O),
          ("21", "IIC_EN", I)],
   top=[("1", "VDD", PI), ("2", "VDD18_D", P), ("3", "VDD18_A", P)], bottom=[("4", "VSS", PI), ("24", "VSS", PI)],
   w=10, verify=True, desc="ScioSense PCAP04 capacitance-to-digital. PIN NUMBERS ARE PLACEHOLDERS")
ic("ADS1220", left=[("11", "AIN0/REFP1", P), ("10", "AIN1", P), ("7", "AIN2", P), ("6", "AIN3/REFN1", P)],
   right=[("1", "SCLK", I), ("2", "~{CS}", I), ("16", "DIN", I), ("15", "DOUT/~{DRDY}", T), ("14", "~{DRDY}", O),
          ("3", "CLK", I)],
   top=[("12", "AVDD", PI), ("13", "DVDD", PI)], ts=4,
   bottom=[("9", "REFP0", P), ("8", "REFN0", P), ("5", "AVSS", PI), ("4", "DGND", PI)],
   w=16, desc="TI ADS1220 24-bit ADC, TSSOP-16")
ic("DAC8760", left=[("1", "SCLK", I), ("2", "DIN", I), ("3", "LATCH", I), ("4", "SDO", T), ("7", "~{ALARM}", OC),
                    ("5", "CLR", I), ("6", "CLR-SEL", I), ("9", "DVDD-EN", I), ("12", "HART-IN", I)],
   right=[("14", "VOUT", O), ("17", "IOUT", O), ("15", "+VSENSE", I), ("22", "REFOUT", P), ("23", "REFIN", I),
          ("24", "ISET-R", P), ("18", "BOOST", P), ("19", "CCOMP", P), ("20", "CAP1", P), ("21", "CAP2", P),
          ("16", "-VSENSE", I)],
   top=[("13", "AVDD", PI), ("8", "DVDD", PI)], ts=4, bottom=[("10", "GND", PI), ("11", "AVSS", PI)],
   w=10, verify=True, desc="TI DAC8760 16-bit V/I output DAC. PIN NUMBERS ARE PLACEHOLDERS")
ic("TPS26611", left=[("1", "IN", P)], right=[("4", "OUT", P), ("5", "~{FLT}", OC), ("6", "MODE", I)],
   top=[("2", "VDD", PI)], bottom=[("3", "VSS", PI)], w=6, verify=True,
   desc="TI TPS26611 analog I/O miswiring protector. PIN NUMBERS ARE PLACEHOLDERS")
ic("THVD2450", left=[("4", "D", I), ("1", "R", O), ("2", "~{RE}", I), ("3", "DE", I)],
   right=[("6", "A", B), ("7", "B", B)], top=[("8", "VCC", PI)], bottom=[("5", "GND", PI)], w=8,
   desc="TI THVD2450 +/-70V fault-protected RS-485, SOIC-8")


# ── 심볼 기하 (라이브러리 좌표, u 단위, y 위쪽 +) ──
def ic_geom(s):
    n = max(len(s["left"]), len(s["right"]), 1)
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
            pins.append((num, nm, t, (s.get("ts", 2) if side == "t" else 2) * (i - (k - 1) / 2) + (s.get("toff", 0) if side == "t" else 0), y, ang))
    return pins, (-hw, btop, hw, bbot)


def pins_of(name):
    s = SYM[name]
    if s["kind"] == "ic":
        return ic_geom(s)[0]
    if s["kind"] in ("pwr", "flag"):
        return [("1", name if s["kind"] == "pwr" else "pwr", "power_in" if s["kind"] == "pwr" else "power_out", 0, 0,
                 90 if s.get("style") == "up" or s["kind"] == "flag" else 270)]
    return [("1", "~", P, 0, 1.5, 270), ("2", "~", P, 0, -1.5, 90)]


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
        if s["style"] == "gnd":
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


class Sheet:
    def __init__(self, file, title, desc, dx=0, dy=0, paper="A3"):
        self.file, self.title, self.desc, self.dx, self.dy, self.paper = file, title, desc, dx, dy, paper
        self.parts = {}      # ref -> dict
        self.order = []
        self.wires = []      # ((x1,y1),(x2,y2))
        self.labels = []     # (net, (x,y), ang, kind)
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
        self.nets[ref] = {"1": n1, "2": n2}
        return ref

    def h2(self, ref, sym, val, fp, xleft, y, n1, n2, **kw):
        self.parts[ref] = dict(sym=sym, val=val, fp=fp, x=xleft + 1.5 + self.dx, y=y + self.dy, r=90, kw=kw)
        self.order.append(ref)
        self.nets[ref] = {"1": n1, "2": n2}
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
          ("ANALOG OUTPUT CH", "아날로그 출력 {ch}"), ("CH", "채널 {ch} 바이패스"), ("DAC SELECTION", "DAC 선정 (결정 #10)"),
          ("RS-485", "RS-485 통신"), ("RESET", "리셋")]

FP = {
    "R0603": "Resistor_SMD:R_0603_1608Metric", "R2512": "Resistor_SMD:R_2512_6332Metric",
    "RMELF": "Resistor_SMD:R_MELF_MMB-0207", "C0603": "Capacitor_SMD:C_0603_1608Metric",
    "C0805": "Capacitor_SMD:C_0805_2012Metric", "C1206": "Capacitor_SMD:C_1206_3216Metric",
    "C1210": "Capacitor_SMD:C_1210_3225Metric", "C1812": "Capacitor_SMD:C_1812_4532Metric",
    "SMA": "Diode_SMD:D_SMA", "SMB": "Diode_SMD:D_SMB", "SMC": "Diode_SMD:D_SMC",
    "FB0603": "Inductor_SMD:L_0603_1608Metric", "LED": "LED_SMD:LED_0603_1608Metric",
}


def decap(S, ref, val, fp, x, ytop, net):
    """전원 심볼(위) — 커패시터 — GND(아래) 한 벌."""
    S.v2(ref, "C", val, FP[fp], x, ytop, net, "GND")
    S.sup_stub(net, S.P(ref, "1"))
    S.gnd_stub(S.P(ref, "2"))


# ════════════════════════════ 1. 커넥터·입력 보호 ════════════════════════════
S = Sheet("connector.kicad_sch", "Connector & input protection",
          "Field connector, 2-stage bidirectional TVS surge protection, chassis isolation", dx=2, dy=2, paper="A4")
SHEETS.append(S)
S.place("J1", "CONN_GH8", "SM08B-GHS-TB", "Connector_JST:JST_GH_SM08B-GHS-TB_1x08-1MP_P1.25mm_Horizontal",
        16, 29, nets={"8": "VIN_EXT", "6": "GND_IN", "4": "OUT1_EXT", "5": "OUT2_EXT", "3": "RS485_A_EXT",
                      "2": "RS485_B_EXT"})
S.place("L1", "CMC", "CMC 2x1mH 0.3A", "TBD:CMC_WE-SL", 32.5, 26,
        nets={"1": "VIN_EXT", "2": "VIN_L", "3": "GND_IN", "4": "GND"})
S.wa(S.P("J1", "8"), S.P("L1", "1"))
S.wa(S.P("J1", "6"), S.P("L1", "3"))
b = S.P("L1", "4")
S.wa(b, (b[0] + 1.5, b[1]))
S.flag((b[0] + 1.5, b[1]), absolute=True)
S.gnd_stub((b[0] + 1.5, b[1]))
a = S.P("L1", "2")
S.v2("D1", "TVS_BI", "SMDJ36CA", FP["SMC"], 37, 26, "VIN_L", "GND")
S.h2("R1", "R", "4.7R 1W pulse", FP["RMELF"], 42, 26, "VIN_L", "VIN_F")
S.wa(a, S.P("D1", "1"), S.P("R1", "1"))
S.gnd_stub(S.P("D1", "2"))
S.v2("D2", "TVS_BI", "SMBJ33CA", FP["SMB"], 49, 26, "VIN_F", "GND")
S.v2("C1", "C", "100n 100V", FP["C0805"], 55, 26, "VIN_F", "GND")
for r_ in ("D2", "C1"):
    S.gnd_stub(S.P(r_, "2"))
S.w((45, 26), (49, 26), (55, 26), (61, 26), (66, 26))
S.flag((66, 26))
S.gl("VIN_F", S.o((66, 26)), "R")
for num, net in (("4", "OUT1_EXT"), ("5", "OUT2_EXT"), ("3", "RS485_A_EXT"), ("2", "RS485_B_EXT")):
    S.gl(net, S.P("J1", num), "R", length=1)
S.nc(S.P("J1", "1"))
S.nc(S.P("J1", "7"))
S.place("J5", "CONN_CH", "Chassis contact", "TBD:Chassis_Spring_Contact", 16, 45, nets={"1": "CHASSIS"})
sh = S.P("J5", "1")
S.v2("R2", "R", "1M", FP["R0603"], 36, 44, "CHASSIS", "GND")
S.v2("C3", "C", "4.7n 2kV Y2", FP["C1812"], 42, 44, "CHASSIS", "GND")
S.place("GDT1", "GDT", "GDT 230V", "TBD:GDT_Bourns_2038", 52, 45.5, nets={"1": "CHASSIS", "2": "GND"})
S.wa(sh, (26, sh[1]), (26, 43 + S.dy))
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
S.text("SMDJ 3 kW (1st) -> R1 -> SMBJ (2nd) -> eFuse on sheet Power", (29.5, 34), 1.27)
S.box(32, 39.5, 75, 54, "CIRCUIT GND <-> CHASSIS  (floating)")
S.text("GDT conducts only on line-to-ground surge", (56, 52.5), 1.27)
S.text("PCB-housing creepage >= 2 mm", (56, 50), 1.27)

# ════════════════════════════ 2. 전원 ════════════════════════════
S = Sheet("power.kicad_sch", "Power", "eFuse (reverse/OV/UV), 60V buck to 5V, LDO 3.3V", dx=4, dy=14)
SHEETS.append(S)
S.place("U1", "TPS2660", "TPS26600PWPR",
        "Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.66x2.46mm_ThermalVias", 30, 23, nets={
    "1": "VIN_F", "2": "VIN_F", "3": "UV_DIV", "5": "OV_DIV", "6": "GND", "9": "GND", "8": "EF_RTN", "17": "EF_RTN",
    "15": "VIN_P", "16": "VIN_P", "14": "PWR_FLT", "11": "EF_ILIM", "10": "EF_IMON", "12": "EF_DVDT"})
S.v2("R3", "R", "866k 1%", FP["R0603"], 14, 20, "VIN_F", "UV_DIV")
S.v2("R4", "R", "97.6k 1%", FP["R0603"], 14, 23, "UV_DIV", "OV_DIV")
S.v2("R5", "R", "36.5k 1%", FP["R0603"], 14, 26, "OV_DIV", "GND")
S.gnd_stub(S.P("R5", "2"))
S.gl("VIN_F", S.o((10, 20)), "L", length=0)
S.w((10, 20), (14, 20))
p1, p2 = S.P("U1", "1"), S.P("U1", "2")
S.wa(S.o((14, 20)), (p1[0] - 1, p1[1]), p1)
S.wa(p2, (p1[0] - 1, p2[1]), (p1[0] - 1, p1[1]))
S.wa(S.P("R3", "2"), S.o((18, 23)), S.o((18, 22)), S.P("U1", "3"))
S.wa(S.P("R4", "2"), S.o((20, 26)), S.o((20, 23)), S.P("U1", "5"))
S.nc(S.P("U1", "7"))
S.nc(S.P("U1", "4"))
S.nc(S.P("U1", "13"))
m = S.P("U1", "6")
S.wa(m, (m[0] - 2, m[1]))
S.gnd_stub((m[0] - 2, m[1]))
S.gnd_stub(S.P("U1", "9"))
r8, r17 = S.P("U1", "8"), S.P("U1", "17")
S.v2("R22", "R", "0R RTN link*", FP["R0603"], r17[0] - S.dx, r17[1] - S.dy + 2, "EF_RTN", "GND")
S.wa(r17, (r17[0], r8[1] + 1), S.P("R22", "1"))
S.wa(r8, (r8[0], r8[1] + 1), (r17[0], r8[1] + 1))
S.gnd_stub(S.P("R22", "2"))
S.text("*R22 RTN link: verify vs TPS2660 datasheet - RTN tied to GND disables reverse-polarity protection", (6, 40), 1.27)
S.gl("PWR_FLT", S.P("U1", "14"), "R", length=2)
S.v2("R6", "R", "R_ILIM *", FP["R0603"], 46, 23, "EF_ILIM", "GND")
S.v2("R7", "R", "10k", FP["R0603"], 43, 24, "EF_IMON", "GND")
S.v2("C4", "C", "22n", FP["C0603"], 40, 25, "EF_DVDT", "GND")
S.wa(S.P("U1", "11"), S.P("R6", "1"))
S.wa(S.P("U1", "10"), S.P("R7", "1"))
S.wa(S.P("U1", "12"), S.P("C4", "1"))
for r_ in ("R6", "R7", "C4"):
    S.gnd_stub(S.P(r_, "2"))
S.v2("C5", "C", "10u 50V", FP["C1210"], 52, 20, "VIN_P", "GND")
S.v2("C7", "C", "2.2u 100V", FP["C1210"], 66, 20, "VIN_P", "GND")
for r_ in ("C5", "C7"):
    S.gnd_stub(S.P(r_, "2"))
S.place("U2", "LMR36006", "LMR36006", "TBD:VQFN-HR-12_LMR36006", 78, 21, nets={
    "1": "VIN_P", "2": "VIN_P", "4": "BUCK_FB", "5": "GND", "7": "BUCK_BOOT", "6": "BUCK_SW",
    "8": "BUCK_VCC", "9": "GND"})
po1, po2 = S.P("U1", "15"), S.P("U1", "16")
S.wa(po2, (po1[0] + 1, po2[1]), (po1[0] + 1, po1[1]))
S.wa(S.P("U1", "15"), (po1[0] + 1, po1[1]), S.o((52, 20)), S.o((57, 20)), S.o((62, 20)), S.o((66, 20)), S.o((71, 20)), S.P("U2", "1"))
S.sup_stub("VIN_P", S.o((62, 20)), d=2)
S.wa(S.P("U2", "2"), S.o((71, 21)), S.o((71, 20)))
S.nc(S.P("U2", "3"))
S.gnd_stub(S.P("U2", "5"))
S.gnd_stub(S.P("U2", "9"))
bt = S.P("U2", "7")
S.h2("C8", "C", "100n", FP["C0603"], 84, 17, "BUCK_BOOT", "BUCK_SW")
S.wa(bt, (bt[0] + 1, bt[1]), S.P("C8", "1"))
S.h2("L2", "L", "22uH", "TBD:L_4x4mm", 88, 21, "BUCK_SW", "+5V")
S.wa(S.P("U2", "6"), S.o((87, 21)), S.P("L2", "1"))
S.wa(S.P("C8", "2"), S.o((87, 21)))
S.v2("C9", "C", "1u", FP["C0603"], 85, 22, "BUCK_VCC", "GND")
S.wa(S.P("U2", "8"), S.P("C9", "1"))
S.gnd_stub(S.P("C9", "2"))
S.v2("C10", "C", "22u 10V", FP["C0805"], 95, 21, "+5V", "GND")
S.v2("R8", "R", "100k 1%", FP["R0603"], 101, 21, "+5V", "BUCK_FB")
S.v2("R9", "R", "24.9k 1%", FP["R0603"], 101, 24, "BUCK_FB", "GND")
S.gnd_stub(S.P("C10", "2"))
S.gnd_stub(S.P("R9", "2"))
S.wa(S.P("R8", "2"), S.o((99, 24)), S.o((99, 31)), S.o((69, 31)), S.o((69, 23)), S.P("U2", "4"))
S.place("U3", "TPS7A2033", "TPS7A2033PDBVR", "Package_TO_SOT_SMD:SOT-23-5", 124, 21,
        nets={"1": "+5V", "3": "+5V", "5": "+3V3", "2": "GND"})
S.wa(S.P("L2", "2"), S.o((95, 21)), S.o((101, 21)), S.o((105, 21)), S.o((109, 21)), S.o((113, 21)),
     S.o((118, 21)), S.P("U3", "1"))
S.flag((105, 21))
S.pw("+5V", (109, 21))
S.wa(S.P("U3", "3"), S.o((118, 22)), S.o((118, 21)))
S.gnd_stub(S.P("U3", "2"))
S.nc(S.P("U3", "4"))
S.v2("C12", "C", "1u", FP["C0603"], 130, 21, "+3V3", "GND")
S.h2("FB1", "FB", "600R@100MHz", FP["FB0603"], 136, 21, "+3V3", "+3V3A")
S.v2("C13", "C", "10u", FP["C0805"], 143, 21, "+3V3A", "GND")
S.gnd_stub(S.P("C12", "2"))
S.gnd_stub(S.P("C13", "2"))
S.wa(S.P("U3", "5"), S.o((130, 21)), S.o((133, 21)), S.P("FB1", "1"))
S.pw("+3V3", (133, 21))
S.wa(S.P("FB1", "2"), S.o((143, 21)), S.o((146, 21)), S.o((149, 21)))
S.flag((146, 21))
S.pw("+3V3A", (149, 21))
S.box(6, 12, 63.5, 34.5, "eFuse  TPS2660   reverse -60 V  /  OVP 33 V  /  UVLO 9 V")
S.text("UVLO = 1.2 V x (R3+R4+R5)/(R4+R5) = 8.9 V", (6.5, 35.5), 1.27)
S.text("OVP  = 1.2 V x (R3+R4+R5)/R5 = 32.9 V   (Vref 1.2 V: VERIFY)", (6.5, 37), 1.27)
S.text("* R6 sets current limit 150 mA (formula in TPS2660 datasheet)", (6.5, 38.5), 1.27)
S.box(64, 12, 111, 33, "BUCK 5 V   LMR36006  (4.2-60 V in, 0.6 A)")
S.text("Vout = 1.0 V x (1 + R8/R9) = 5.0 V   (Vref 1.0 V: VERIFY)", (64, 35.5), 1.27)
S.box(112, 14, 153, 29, "LDO 3.3 V   TPS7A2033   +   analog rail +3V3A")

# ════════════════════════════ 3. MCU ════════════════════════════
S = Sheet("mcu.kicad_sch", "MCU", "STM32G0B1CCT3, SWD, reset, internal temperature sensor", dx=6, dy=6)
SHEETS.append(S)
mnet = {"4": "+3V3", "6": "+3V3", "5": "+3V3", "7": "GND", "10": "NRST",
        "12": "RS485_DE", "13": "RS485_TX", "14": "RS485_RX", "16": "SPI_SCK", "17": "SPI_MISO", "18": "SPI_MOSI",
        "35": "SWDIO", "36": "SWCLK", "19": "CS_CDC", "20": "CS_ADC", "21": "ADC_DRDY",
        "22": "DAC1_LATCH", "23": "DAC2_LATCH", "24": "CDC_INT", "30": "OUT1_FLT", "31": "OUT2_FLT",
        "25": "DAC1_ALARM", "26": "DAC2_ALARM", "27": "PWR_FLT"}
S.place("U4", "STM32G0B1CxTx", "STM32G0B1CCT3", "Package_QFP:LQFP-48_7x7mm_P0.5mm", 62, 52, nets=mnet)
tops = [S.P("U4", n) for n in ("4", "6")]
ytop = tops[0][1] - 2
for p in tops:
    S.wa(p, (p[0], ytop))
S.wa(*[(p[0], ytop) for p in tops])
S.pw("+3V3", (tops[0][0], ytop), absolute=True)
S.sup_stub("+3V3", S.P("U4", "5"), d=2)          # VREF+ = VDD (MCU ADC는 내부 온도센서·진단용)
gp = S.P("U4", "7")
S.wa(gp, (gp[0], gp[1] + 2))
S.pw("GND", (gp[0], gp[1] + 2), absolute=True)
S.gl("NRST", S.P("U4", "10"), "L")
left_lbl = {"30": "OUT1_FLT", "31": "OUT2_FLT"}
for num, nm, t, *_ in SYM["STM32G0B1CxTx"]["left"]:
    if num == "10":
        continue
    if num in left_lbl:
        S.gl(left_lbl[num], S.P("U4", num), "L")
    else:
        S.nc(S.P("U4", num))
right_lbl = {"12": "RS485_DE", "13": "RS485_TX", "14": "RS485_RX", "16": "SPI_SCK", "17": "SPI_MISO",
             "18": "SPI_MOSI", "35": "SWDIO", "36": "SWCLK", "19": "CS_CDC", "20": "CS_ADC",
             "21": "ADC_DRDY", "22": "DAC1_LATCH", "23": "DAC2_LATCH", "24": "CDC_INT",
             "25": "DAC1_ALARM", "26": "DAC2_ALARM", "27": "PWR_FLT"}
for num, nm, t, *_ in SYM["STM32G0B1CxTx"]["right"]:
    if num in right_lbl:
        S.gl(right_lbl[num], S.P("U4", num), "R")
    else:
        S.nc(S.P("U4", num))
for i, (ref, val, fp) in enumerate([("C14", "100n", "C0603"), ("C15", "100n", "C0603"), ("C20", "100n", "C0603"),
                                   ("C18", "4.7u", "C0805")]):
    decap(S, ref, val, fp, 10 + 5 * i, 12, "+3V3")
S.box(6, 7, 38, 21, "MCU DECOUPLING")
S.text("100 nF at VDD, VBAT, VREF+ (C20); 4.7 uF bulk", (6.5, 20.3), 1.27)
S.v2("C21", "C", "100n", FP["C0603"], 128, 13, "NRST", "GND")
S.gl("NRST", S.P("C21", "1"), "U", length=1)
S.gnd_stub(S.P("C21", "2"))
S.box(118, 7, 134, 27, "RESET")
S.text("Fault lines: MCU pull-ups", (118.5, 24.9), 1.27)
S.text("(PB13-15, PC6-7 internal)", (118.5, 26.3), 1.27)
S.place("J2", "CONN_SWD", "TC2030-IDC-NL", "Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical", 126, 38,
        nets={"1": "+3V3", "2": "SWDIO", "4": "SWCLK", "3": "NRST", "5": "GND"})
v = S.P("J2", "1")
S.wa(v, (v[0] - 2, v[1]))
S.sup_stub("+3V3", (v[0] - 2, v[1]))
for num, net in (("2", "SWDIO"), ("4", "SWCLK"), ("3", "NRST")):
    S.gl(net, S.P("J2", num), "L", length=3)
S.nc(S.P("J2", "6"))                      # Cortex-M0+: SWO 없음
g_ = S.P("J2", "5")
S.wa(g_, (g_[0] - 1, g_[1]))
S.gnd_stub((g_[0] - 1, g_[1]))
S.box(106, 31, 134, 47, "SWD  (production programming)")
S.box(6, 62, 48, 82, "MCU NOTES (STM32G0B1)")
for i, t in enumerate(["BOOT0 shares PA14/SWCLK - no pull-down.",
                       "Option bytes: nBOOT_SEL=1, nBOOT0=1",
                       "  -> boot from flash (RS-485 bootloader 0x08000000).",
                       "VDDA = VDD (LQFP48); VREF+ tied to +3V3 (C20).",
                       "PCB temp (mid): internal sensor, ADC ch TS + TS_CAL.",
                       "Cortex-M0+: no SWO (J2 pin 6 NC).",
                       "Same die as DP2000 (G0B1CCT6); T3 = -40..125 C."]):
    S.text(t, (7, 66 + 2.3 * i), 1.27)

# ════════════════════════════ 4. 측정 ════════════════════════════
S = Sheet("measurement.kicad_sch", "Measurement", "Capacitive humidity sensor (PCAP04) and Pt1000 2-wire (ADS1220)",
          dx=4, dy=10)
SHEETS.append(S)
S.place("J3", "CONN_SH4", "SM04B-SRSS-TB", "Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal",
        6, 31, nets={"1": "SENS_C1", "2": "SENS_C2", "3": "PT_P", "4": "PT_N"})
S.text("SENSOR HEAD", (2, 25.8), 1.6, True)
S.text("harness W-1", (2, 37.8), 1.27)
S.text("JST SH 1.0", (2, 39.1), 1.27)
S.place("U5", "PCAP04", "PCAP04-AQFM-24", "TBD:QFN-24_PCAP04", 44, 18, nets={
    "6": "CREF_B", "5": "CREF_A", "7": "SENS_C1", "8": "SENS_C2", "16": "CS_CDC", "17": "SPI_SCK",
    "18": "SPI_MOSI", "19": "SPI_MISO", "20": "CDC_INT", "21": "GND", "1": "+3V3A", "2": "CDC_V18D",
    "3": "CDC_V18A", "4": "GND", "24": "GND"})
S.wa(S.P("J3", "1"), S.o((26, 30)), S.o((26, 14)), S.P("U5", "7"))
S.wa(S.P("J3", "2"), S.o((28, 31)), S.o((28, 15)), S.P("U5", "8"))
S.v2("C22", "C", "220p C0G 1%", FP["C0603"], 30, 10, "CREF_B", "CREF_A")
S.wa(S.P("U5", "5"), S.P("C22", "2"))
S.wa(S.P("C22", "1"), S.o((36, 10)), S.o((36, 12)), S.P("U5", "6"))
for num in ("9", "10", "11", "12", "13", "14", "15", "22", "23"):
    S.nc(S.P("U5", num))
for num, net in (("16", "CS_CDC"), ("17", "SPI_SCK"), ("18", "SPI_MOSI"), ("19", "SPI_MISO"), ("20", "CDC_INT")):
    S.gl(net, S.P("U5", num), "R")
ie = S.P("U5", "21")
S.wa(ie, (ie[0] + 1, ie[1]))
S.gnd_stub((ie[0] + 1, ie[1]))
S.sup_stub("+3V3A", S.P("U5", "1"), d=2)
S.v2("C25", "C", "1u", FP["C0603"], 66, 4, "CDC_V18D", "GND")
S.v2("C26", "C", "1u", FP["C0603"], 61, 6, "CDC_V18A", "GND")
S.wa(S.P("U5", "2"), S.o((44, 4)), S.P("C25", "1"))
S.wa(S.P("U5", "3"), S.o((46, 6)), S.P("C26", "1"))
S.gnd_stub(S.P("C25", "2"))
S.gnd_stub(S.P("C26", "2"))
S.gnd_stub(S.P("U5", "4"))
S.gnd_stub(S.P("U5", "24"))
S.place("U6", "ADS1220", "ADS1220IPWR", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", 47, 45, nets={
    "11": "PT_P", "10": "PT_SP_F", "7": "PT_SN_F", "1": "SPI_SCK", "2": "CS_ADC", "16": "SPI_MOSI",
    "15": "SPI_MISO", "14": "ADC_DRDY", "3": "GND", "12": "+3V3A", "13": "+3V3", "9": "PT_N", "8": "REF_N",
    "5": "GND", "4": "GND"})
S.h2("R17", "R", "1k", FP["R0603"], 27, 44, "PT_P", "PT_SP_F")
S.h2("R18", "R", "1k", FP["R0603"], 27, 47, "PT_N", "PT_SN_F")
S.v2("C27", "C", "10n", FP["C0603"], 33, 44, "PT_SP_F", "PT_SN_F")
S.wa(S.P("J3", "3"), S.o((24, 32)), S.o((24, 43)), S.P("U6", "11"))   # 2선식: J3 패드에서 힘/감지 분기
S.wa(S.o((24, 43)), S.o((24, 44)), S.P("R17", "1"))
S.wa(S.P("J3", "4"), S.o((20, 33)), S.o((20, 47)), S.P("R18", "1"))
S.wa(S.o((20, 47)), S.o((20, 53)))
S.wa(S.P("R17", "2"), S.o((33, 44)), S.P("U6", "10"))
S.wa(S.P("R18", "2"), S.o((33, 47)), S.o((36, 47)), S.o((36, 45)), S.P("U6", "7"))
S.nc(S.P("U6", "6"))
S.v2("R19", "R", "4.02k 0.01% 5ppm", FP["R0603"], 44, 53, "PT_N", "REF_N")
S.v2("R20", "R", "1k", FP["R0603"], 44, 56, "REF_N", "GND")
S.gnd_stub(S.P("R20", "2"))
S.wa(S.o((20, 53)), S.o((44, 53)))
S.wa(S.P("U6", "9"), S.o((44, 53)))
S.wa(S.P("R19", "2"), S.o((46, 56)), S.P("U6", "8"))
S.gnd_stub(S.P("U6", "5"))
S.gnd_stub(S.P("U6", "4"))
for num, net in (("1", "SPI_SCK"), ("2", "CS_ADC"), ("16", "SPI_MOSI"), ("15", "SPI_MISO"), ("14", "ADC_DRDY")):
    S.gl(net, S.P("U6", num), "R")
ck = S.P("U6", "3")
S.wa(ck, (ck[0] + 1, ck[1]))
S.gnd_stub((ck[0] + 1, ck[1]))
S.sup_stub("+3V3A", S.P("U6", "12"))
S.sup_stub("+3V3", S.P("U6", "13"))
decap(S, "C23", "100n", "C0603", 82, 12, "+3V3A")
decap(S, "C24", "1u", "C0603", 87, 12, "+3V3A")
decap(S, "C28", "100n", "C0603", 82, 42, "+3V3")
decap(S, "C29", "100n", "C0603", 87, 42, "+3V3A")
S.box(14, 0.5, 72, 28.5, "CAPACITIVE HUMIDITY SENSOR  (IST MK)  ->  PCAP04")
S.text("Floating mode: C22 reference on PC0/PC1, sensor on PC2/PC3 (VERIFY with PCAP04 datasheet)", (14.5, 3.2), 1.27)
S.box(14, 37, 72, 62, "Pt1000 2-WIRE -> ADS1220", tdx=11.2, ko_next=True)
S.text("ratiometric: Rref R19 on REFP0/REFN0", (25.2, 40.9), 1.27)
S.text("IDAC1 (AIN0) -> PT+ ; sense AIN1-AIN2, split at J3 pads", (46, 57.3), 1.27)
S.text("Lead R (harness+HTX99R+probe) removed by calibration", (46, 58.6), 1.27)
S.text("PCB temp: ADS1220 internal sensor (TS mode)", (46, 61.2), 1.27)
S.text("RC filter R17/R18/C27 (differential + common mode)", (50, 59.9), 1.27)
S.box(78, 5, 93, 21, "DECOUPLING")
S.box(78, 35, 93, 51, "DECOUPLING")

# ════════════════════════════ 5. 아날로그 출력 ════════════════════════════
S = Sheet("analog_out.kicad_sch", "Analog outputs", "2x DAC8760 V/I output with TPS26611 miswiring protection",
          dx=4, dy=2)
SHEETS.append(S)
for ch, y0 in ((1, 10), (2, 44)):
    D, Pr = f"U{6 + ch}", f"U{8 + ch}"
    S.place(D, "DAC8760", "DAC8760IPWP", "TBD:HTSSOP-24_DAC8760", 30, y0 + 10, nets={
        "1": "SPI_SCK", "2": "SPI_MOSI", "3": f"DAC{ch}_LATCH", "4": "SPI_MISO", "7": f"DAC{ch}_ALARM",
        "5": "GND", "6": "GND", "9": "GND", "14": f"DAC{ch}_OUT", "17": f"DAC{ch}_OUT", "15": f"DAC{ch}_SENSE",
        "22": f"DAC{ch}_REF", "23": f"DAC{ch}_REF", "16": "GND", "13": "VIN_P", "8": "+3V3", "10": "GND",
        "11": "GND"})
    for num, net in (("1", "SPI_SCK"), ("2", "SPI_MOSI"), ("3", f"DAC{ch}_LATCH"), ("4", "SPI_MISO"),
                     ("7", f"DAC{ch}_ALARM")):
        S.gl(net, S.P(D, num), "L")
    c5, c6, c9 = S.P(D, "5"), S.P(D, "6"), S.P(D, "9")
    bx = c5[0] - 2
    S.wa(c5, (bx, c5[1]))
    S.wa(c6, (bx, c6[1]))
    S.wa(c9, (bx, c9[1]))
    S.wa((bx, c5[1]), (bx, c6[1]), (bx, c9[1]))
    S.gnd_stub((bx, c9[1]), d=1)
    S.nc(S.P(D, "12"))
    S.sup_stub("VIN_P", S.P(D, "13"))
    S.sup_stub("+3V3", S.P(D, "8"))
    S.gnd_stub(S.P(D, "10"))
    S.gnd_stub(S.P(D, "11"))
    vo, io, sp = S.P(D, "14"), S.P(D, "17"), S.P(D, "15")
    S.wa(vo, (vo[0] + 2, vo[1]))
    S.wa(io, (io[0] + 2, io[1]), (io[0] + 2, vo[1]))
    ro, ri = S.P(D, "22"), S.P(D, "23")
    S.wa(ro, (ro[0] + 1, ro[1]), (ro[0] + 1, ri[1]))
    S.wa(ri, (ri[0] + 1, ri[1]), (ri[0] + 4, ri[1]))
    S.v2(f"C{30 + 10 * ch}", "C", "100n", FP["C0603"], ri[0] - S.dx + 4, ri[1] - S.dy, f"DAC{ch}_REF", "GND")
    S.gnd_stub(S.P(f"C{30 + 10 * ch}", "2"))
    for num in ("24", "18", "19", "20", "21"):
        S.nc(S.P(D, num))
    vs = S.P(D, "16")
    S.wa(vs, (vs[0] + 1, vs[1]))
    S.gnd_stub((vs[0] + 1, vs[1]))
    S.place(Pr, "TPS26611", "TPS26611", "TBD:TPS26611", 46, vo[1] - S.dy + 1, nets={
        "1": f"DAC{ch}_OUT", "2": "VIN_P", "3": "GND", "4": f"OUT{ch}_P", "5": f"OUT{ch}_FLT", "6": "GND"})
    S.wa((vo[0] + 2, vo[1]), S.P(Pr, "1"))
    S.sup_stub("VIN_P", S.P(Pr, "2"))
    S.gnd_stub(S.P(Pr, "3"))
    md = S.P(Pr, "6")
    S.wa(md, (md[0] + 1, md[1]))
    S.gnd_stub((md[0] + 1, md[1]))
    S.gl(f"OUT{ch}_FLT", S.P(Pr, "5"), "R", length=3)
    op = S.P(Pr, "4")
    yr = op[1] - S.dy
    S.h2(f"R{20 + 10 * ch}", "R", "10R pulse", FP["R2512"], 57, yr, f"OUT{ch}_P", f"OUT{ch}_EXT")
    S.wa(op, S.P(f"R{20 + 10 * ch}", "1"))
    S.v2(f"D{20 + 10 * ch}", "TVS_BI", "SMAJ33CA", FP["SMA"], 65, yr, f"OUT{ch}_EXT", "GND")
    S.v2(f"C{31 + 10 * ch}", "C", "1n 100V", FP["C0603"], 72, yr, f"OUT{ch}_EXT", "GND")
    S.gnd_stub(S.P(f"D{20 + 10 * ch}", "2"))
    S.gnd_stub(S.P(f"C{31 + 10 * ch}", "2"))
    S.w((60, yr), (65, yr), (72, yr), (77, yr), (80, yr))
    S.gl(f"OUT{ch}_EXT", S.o((80, yr)), "R", length=0)
    S.h2(f"R{21 + 10 * ch}", "R", "10k", FP["R0603"], 74, yr - 6, f"DAC{ch}_SENSE", f"OUT{ch}_EXT")
    S.w((77, yr), (77, yr - 6))
    S.wa(S.P(f"R{21 + 10 * ch}", "1"), (sp[0] + 3, yr - 6 + S.dy), (sp[0] + 3, sp[1]), sp)
    for j, (val, fp, net) in enumerate((("100n 50V", "C0805", "VIN_P"), ("4.7u 50V", "C1210", "VIN_P"),
                                        ("100n", "C0603", "+3V3"))):
        decap(S, f"C{32 + j + 10 * ch}", val, fp, 97 + 6 * j, y0 + 3, net)
    S.box(8, y0 - 6, 92, y0 + 26, f"ANALOG OUTPUT CH{ch}  -  V/I selectable, miswiring protected  ->  connector pin {3 + ch}")
    S.text(f"VOUT and IOUT combined (per TI TIDUBK2 - VERIFY). +VSENSE taken after R{20 + 10 * ch} to cancel series drop.",
           (8.5, y0 + 25.3), 1.27)
    S.box(93, y0 - 6, 115, y0 + 12, f"CH{ch} DECOUPLING")
S.box(8, 74, 115, 88, "DAC SELECTION  (decision 2026-09-26: fit DAC8760 now; final part after output spec is fixed)")
for i, t in enumerate([
        "U7/U8 fitted: DAC8760 (16-bit, current + voltage output).  Same package/pinout family - drop-in alternates, no layout change:",
        "  DAC7760  12-bit, current + voltage   (cost-down if V/I selectable output is kept)",
        "  DAC8750  16-bit, current only 4-20/0-20/0-24 mA   (EE364-equivalent, 3-wire)",
        "  DAC7750  12-bit, current only   (lowest cost; ~5 uA/step vs EE364 2 uA)",
        "Current-only (x750): VOUT/+VSENSE/-VSENSE functions absent - check pin handling in datasheet before fitting (VERIFY).",
]):
    S.text(t, (8.5, 77.5 + 2.2 * i), 1.27)

# ════════════════════════════ 6. RS-485 ════════════════════════════
S = Sheet("rs485.kicad_sch", "RS-485", "THVD2450 +/-70V fault-protected transceiver", dx=4, dy=4, paper="A4")
SHEETS.append(S)
S.place("U11", "THVD2450", "THVD2450DR", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", 30, 21, nets={
    "4": "RS485_TX", "1": "RS485_RX", "2": "RS485_DE", "3": "RS485_DE", "8": "+3V3", "6": "RS485_A_EXT",
    "7": "RS485_B_EXT", "5": "GND"})
S.gl("RS485_TX", S.P("U11", "4"), "L", length=3)
S.gl("RS485_RX", S.P("U11", "1"), "L", length=3)
re, de = S.P("U11", "2"), S.P("U11", "3")
S.wa(re, (re[0] - 2, re[1]), (re[0] - 2, de[1]), de)
S.gl("RS485_DE", (re[0] - 2, re[1]), "L", length=1)
S.sup_stub("+3V3", S.P("U11", "8"), d=2)
S.gnd_stub(S.P("U11", "5"))
S.wa(S.P("U11", "6"), S.o((60, 20)))
bb = S.P("U11", "7")
S.wa(bb, (bb[0] + 1, bb[1]), (bb[0] + 1, 27 + S.dy), S.o((62, 27)))
S.gl("RS485_A_EXT", S.o((60, 20)), "R", length=0)
S.gl("RS485_B_EXT", S.o((62, 27)), "R", length=0)
decap(S, "C60", "100n", "C0603", 14, 13, "+3V3")
S.box(8, 7, 75, 36, "RS-485  (Modbus RTU)   -   bus pins +/-70 V fault protected")
S.text("No termination on board (fit at bus ends). Fail-safe receiver built in.", (8.5, 34.2), 1.27)
S.text("No series R / TVS: THVD2450 has +/-70 V bus fault and IEC ESD protection built in.", (8.5, 35.5), 1.27)

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
                 f'(property "Footprint" {q(p["fp"])} (at {mm(p["x"])} {mm(p["y"])} 0) {HIDE})',
                 f'(property "Datasheet" "~" (at {mm(p["x"])} {mm(p["y"])} 0) {HIDE})']
        if s.get("verify"):
            props.append(f'(property "VERIFY" "YES - pin numbers are placeholders" (at {mm(p["x"])} {mm(p["y"])} 0) {HIDE})')
        bom = "no" if s["kind"] in ("pwr", "flag") else "yes"
        pu = " ".join(f"(pin {q(pp[0])} (uuid {uid(key, 'pin', pp[0])}))" for pp in pins_of(p["sym"]))
        items.append(f"(symbol (lib_id {q(LIB + ':' + p['sym'])}) (at {mm(p['x'])} {mm(p['y'])} {p['r']}) (unit 1) "
                     f"(in_bom {bom}) (on_board {bom}) (dnp no) (uuid {uid(key, 'sym')}) " + " ".join(props) +
                     f" {pu} (instances (project {q(PROJECT)} (path {q(path)} (reference {q(ref)}) (unit 1)))))")
    for i, (a, b) in enumerate(S.wires):
        items.append(f"(wire (pts (xy {mm(a[0])} {mm(a[1])}) (xy {mm(b[0])} {mm(b[1])})) (stroke (width 0) (type default)) (uuid {uid(S.file, 'w', i)}))")
    for i, (net, pt, ang, kind) in enumerate(S.labels):
        just = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
        items.append(f"(global_label {q(net)} (shape passive) (at {mm(pt[0])} {mm(pt[1])} {ang}) (fields_autoplaced) "
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
        items.append(f"(text {q(t)} (at {mm(pt[0])} {mm(pt[1])} 0) (effects (font{face} (size {size} {size}){' bold' if bold else ''}) "
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


def rp(pt):
    return (round(pt[0], 3), round(pt[1], 3))


def junctions(S):
    cnt = {}
    for a, b in S.wires:
        for e in (rp(a), rp(b)):
            cnt[e] = cnt.get(e, 0) + 1
    for pt, *_ in all_pins(S):
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
    errs += place_props(S) + overlap_errors(S)
    if errs:
        raise SystemExit(f"{S.file}:\n  " + "\n  ".join(sorted(set(errs))[:60]))


# ════════════════════════════ 글자 배치·겹침 검사 ════════════════════════════
# 단위 u(2.54 mm), y 아래로 +. 글자 폭은 KiCad 기본 글꼴 실측(문자당 약 1.05 × 글자 크기).
def text_rect(t, x, y, size, just="left", bold=False, valign="center"):
    w, h = text_w(t, size, bold), size * 1.2 / U
    x0 = {"left": x, "center": x - w / 2, "right": x - w}[just]
    y0 = {"center": y - h / 2, "bottom": y - h}[valign]
    return (x0, y0, x0 + w, y0 + h)


def _hit(a, b, pad=0.05):
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


TWO_HW = {"rect": 0.45, "cap": 0.85, "ind": 0.35, "ferrite": 0.45, "tvs": 0.75, "gdt": 0.85, "led": 1.05}


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
        if st == "gnd":
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
    bodies = [(r_, n) for r_, n in R if n.startswith("body") and not n.startswith("body #")]
    for a, na in bodies:                        # 부품 몸체가 박스 테두리·다른 몸체·글자와 겹침
        for b, nb in R:
            if nb == na or nb.startswith(("wire", "label", "nc", "body #")):
                continue
            if _hit(a, b, pad=-0.02):
                errs.append(f"{na} overlaps {nb}")
    return errs


def title_block(title):
    return (f'(title_block (title {q("HMT500  " + title)}) (date "2026-09-29") (rev "0.6") '
            f'(company "DOTECH Co., Ltd.") (comment 1 "Oil moisture transmitter HMT500 - RS-485 + 2x V/I analog output") '
            f'(comment 2 "Design notes: docs/hw/circuit-design.md") '
            f'(comment 3 "VERIFY=YES parts: pin numbers LMR36006/PCAP04/DAC8760/TPS26611; TPS2660 R22"))')


def write_all():
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
        sx, sy = 12 + (i % 3) * 50, 22 + (i // 3) * 30
        items.append(f"(sheet (at {mm(sx)} {mm(sy)}) (size {mm(42)} {mm(18)}) (fields_autoplaced) "
                     f"(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid {su}) "
                     f'(property "Sheetname" {q(f"{i + 1}. {S.title}")} (at {mm(sx)} {mm(sy - 0.3)} 0) (effects (font (size 1.8 1.8) bold) (justify left bottom))) '
                     f'(property "Sheetfile" {q(S.file)} (at {mm(sx)} {mm(sy + 18.3)} 0) (effects (font (size 1.27 1.27)) (justify left top))) '
                     f'(instances (project {q(PROJECT)} (path {q("/" + ROOT)} (page {q(str(i + 2))})))))')
        items.append(f"(text {q(S.desc)} (at {mm(sx + 1)} {mm(sy + 9)} 0) (effects (font (size 1.4 1.4)) (justify left bottom)) (uuid {uid('rootdesc', i)}))")
    notes = [
        ("DOTECH HMT500  -  Oil Moisture Transmitter  -  Schematic v0.6", 2.5, True),
        ("v0.5: J1 = JST GH 1.25 mm 8P side entry (SM08B-GHS-TB), harness W-2 to M12 8P; J5 chassis spring contact (was M12 shell pin).", 1.4, False),
        ("v0.4: J3 = JST SH 1.0 mm 4P (SM04B-SRSS-TB side entry, v0.5) for sensor harness W-1 direct from HTX99R (no feedthrough, mech Rev F); Pt1000 2-wire (Kelvin split at J3 pads).", 1.4, False),
        ("v0.3: MCU STM32G0B1CCT3 (LQFP48, -40..125 C, in-house part); TPS26600PWP official pinout; single axial PCB 57x23 (mech Rev C).", 1.4, False),
        ("Signal flow: J1 field connector -> protection -> eFuse -> 5 V buck -> 3.3 V LDO; sensor head J3 -> PCAP04 / ADS1220 -> MCU -> DAC8760 x2 / THVD2450 -> J1", 1.4, False),
        ("Outputs: RS-485 Modbus RTU + 2x analog (4-20 mA / 0-20 mA / 0-10 V / 0-5 V selectable).  Supply 12-30 V DC.", 1.4, False),
        ("Protection target: any pin pair +/-30 V continuous (miswiring), surge +/-1 kV, ESD +/-8 kV contact.", 1.4, False),
        ("Power symbols: GND, +3V3, +3V3A (analog 3.3 V), +5V, VIN_P (protected input), CHASSIS.  Inter-sheet signals: global labels.", 1.4, False),
        ("v0.6: parts cleanup (-16: pull-ups R11-15, LED D3/R16, RS-485 R60/61 D60/61, FB2 C19 C11 C2 C6); PCB temperature = ADS1220 + MCU internal sensors.", 1.4, False),
        ("VERIFY: LMR36006, PCAP04, DAC8760, TPS26611 pin numbers are placeholders (datasheets not accessible when drawn). TPS2660: RTN link R22 to confirm.", 1.4, False),
        ("TBD footprints: J5 chassis contact, CMC, GDT, buck inductor, LMR36006, PCAP04, DAC8760, TPS26611.", 1.4, False),
        ("표기 규칙: 부품번호 = 굵은 글자 (R1, U4) / 부품값 = 보통 글자 (10k, DAC8760) / 전원 네트 = 기울인 글자 (+3V3, VIN_P)", 1.4, False),
        ("         신호 네트 = 테두리 있는 라벨 (SPI_SCK, OUT1_EXT) - 네트 이름은 부품번호·부품명과 겹치지 않게 지음", 1.4, False),
        ("글자 겹침: 생성기가 부품 몸체·핀·선·라벨·메모와 겹치지 않는 자리에 자동 배치하고, 겹치면 생성 실패로 처리", 1.4, False),
    ]
    y = 77
    for i, (t, size, bold) in enumerate(notes):
        face = f' (face "{HANGUL_FACE}")' if has_hangul(t) else ""
        items.append(f"(text {q(t)} (at {mm(12)} {mm(y)} 0) (effects (font{face} (size {size} {size}){' bold' if bold else ''}) (justify left bottom)) (uuid {uid('note', i)}))")
        y += 3.2 if i == 0 else 2.2
    open(os.path.join(OUT, PROJECT + ".kicad_sch"), "w", encoding="utf-8").write(
        f"(kicad_sch (version 20230121) (generator eeschema) (uuid {ROOT}) (paper \"A3\")\n{title_block('Top')}\n"
        "(lib_symbols)\n" + "\n".join(items) + '\n(sheet_instances (path "/" (page "1")))\n)\n')
    # 라이브러리, 프로젝트
    body = "\n".join(lib_symbol(n, False) for n in SYM)
    open(os.path.join(OUT, LIB + ".kicad_sym"), "w", encoding="utf-8").write(
        f"(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n{body}\n)\n")
    open(os.path.join(OUT, "sym-lib-table"), "w").write(
        f'(sym_lib_table\n  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.kicad_sym")(options "")(descr "HMT500 project symbols"))\n)\n')
    pro = {"meta": {"filename": PROJECT + ".kicad_pro", "version": 1},
           "sheets": [[ROOT, "Root"]] + [[u_, S.title] for S, u_ in zip(SHEETS, uuids)]}
    open(os.path.join(OUT, PROJECT + ".kicad_pro"), "w").write(json.dumps(pro, indent=2) + "\n")
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
