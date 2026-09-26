"""DOTECH HMT500 KiCad 회로도 생성기 (KiCad 7 형식, KiCad 8/9에서 열면 자동 변환).

python3 hardware/kicad/gen_hmt500.py
  → hardware/kicad/HMT500/ 에 프로젝트, 심볼 라이브러리, 계층 시트 생성

회로 내용은 docs/hw/circuit-design.md 를 따른다.
연결은 전역 라벨(net label)로 한다. 부품 배치·배선 정리는 KiCad에서 이어서 한다.
심볼의 VERIFY 필드가 "YES"인 IC는 핀 번호가 가번호이므로 데이터시트로 확인해야 한다.
"""

import json
import os
import uuid

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "HMT500")
PROJECT = "HMT500"
LIB = "HMT500"
NS = uuid.UUID("6f1c0a52-8d7e-4c1a-9a53-4d2f0b7e1a10")
G = 2.54


def uid(*key):
    return str(uuid.uuid5(NS, "/".join(map(str, key))))


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def f(v):
    return f"{round(v, 3):g}"


FONT = "(effects (font (size 1.27 1.27)))"
FONT_HIDE = "(effects (font (size 1.27 1.27)) hide)"

# ───────────────────────── 심볼 정의 ─────────────────────────
# 핀: (번호, 이름, 전기형식)
# 전기형식: input output bidirectional tri_state passive power_in power_out open_collector no_connect
SYMBOLS = {}


def ic(name, left, right, width=20.32, prefix="U", verify=False, desc=""):
    SYMBOLS[name] = dict(kind="ic", left=left, right=right, w=width, prefix=prefix, verify=verify, desc=desc)


def two(name, prefix, draw, desc=""):
    SYMBOLS[name] = dict(kind="two", prefix=prefix, draw=draw, desc=desc)


two("R", "R", "rect", "Resistor")
two("C", "C", "cap", "Capacitor")
two("L", "L", "ind", "Inductor")
two("FB", "FB", "ferrite", "Ferrite bead")
two("TVS_BI", "D", "tvs", "Bidirectional TVS diode")
two("GDT", "GDT", "gdt", "Gas discharge tube")
SYMBOLS["LED"] = dict(kind="two", prefix="D", draw="led", desc="LED (pin1=K, pin2=A)")
SYMBOLS["PWR_FLAG"] = dict(kind="flag", prefix="#FLG", desc="Power flag")

ic("STM32L431RCTx",
   [("1", "VBAT", "power_in"), ("19", "VDD", "power_in"), ("32", "VDD", "power_in"), ("64", "VDD", "power_in"),
    ("48", "VDDUSB", "power_in"), ("13", "VDDA", "power_in"), ("12", "VSSA", "power_in"), ("18", "VSS", "power_in"),
    ("31", "VSS", "power_in"), ("47", "VSS", "power_in"), ("63", "VSS", "power_in"), ("7", "NRST", "bidirectional"),
    ("60", "PH3-BOOT0", "input"), ("5", "PH0", "bidirectional"), ("6", "PH1", "bidirectional")],
   [(n, p, "bidirectional") for n, p in [
       ("14", "PA0"), ("15", "PA1"), ("16", "PA2"), ("17", "PA3"), ("20", "PA4"), ("21", "PA5"), ("22", "PA6"),
       ("23", "PA7"), ("41", "PA8"), ("42", "PA9"), ("43", "PA10"), ("44", "PA11"), ("45", "PA12"), ("46", "PA13"),
       ("49", "PA14"), ("50", "PA15"), ("26", "PB0"), ("27", "PB1"), ("28", "PB2"), ("55", "PB3"), ("56", "PB4"),
       ("57", "PB5"), ("58", "PB6"), ("59", "PB7"), ("61", "PB8"), ("62", "PB9"), ("29", "PB10"), ("30", "PB11"),
       ("33", "PB12"), ("34", "PB13"), ("35", "PB14"), ("36", "PB15"), ("8", "PC0"), ("9", "PC1"), ("10", "PC2"),
       ("11", "PC3"), ("24", "PC4"), ("25", "PC5"), ("37", "PC6"), ("38", "PC7"), ("39", "PC8"), ("40", "PC9"),
       ("51", "PC10"), ("52", "PC11"), ("53", "PC12"), ("2", "PC13"), ("3", "PC14"), ("4", "PC15"), ("54", "PD2")]],
   width=25.4, desc="STM32L431RCT6 LQFP64 (verify pinout with ST datasheet)")

ic("ADS1220",
   [("1", "SCLK", "input"), ("2", "~{CS}", "input"), ("3", "CLK", "input"), ("16", "DIN", "input"),
    ("15", "DOUT/~{DRDY}", "tri_state"), ("14", "~{DRDY}", "output"), ("13", "DVDD", "power_in"),
    ("4", "DGND", "power_in")],
   [("12", "AVDD", "power_in"), ("11", "AIN0/REFP1", "passive"), ("10", "AIN1", "passive"), ("7", "AIN2", "passive"),
    ("6", "AIN3/REFN1", "passive"), ("9", "REFP0", "passive"), ("8", "REFN0", "passive"), ("5", "AVSS", "power_in")],
   width=22.86, desc="TI ADS1220 TSSOP-16")

ic("THVD2450",
   [("4", "D", "input"), ("1", "R", "output"), ("2", "~{RE}", "input"), ("3", "DE", "input")],
   [("8", "VCC", "power_in"), ("6", "A", "bidirectional"), ("7", "B", "bidirectional"), ("5", "GND", "power_in")],
   desc="TI THVD2450 SOIC-8, +/-70V fault protected RS-485")

ic("TPS7A2033",
   [("1", "IN", "power_in"), ("3", "EN", "input"), ("2", "GND", "power_in")],
   [("5", "OUT", "power_out"), ("4", "NC", "no_connect")],
   width=15.24, desc="TI TPS7A2033 SOT-23-5, 3.3V LDO")

ic("TPS2660",
   [("1", "IN", "power_in"), ("2", "EN/UVLO", "input"), ("3", "OVP", "input"), ("4", "~{SHDN}", "input"),
    ("5", "MODE", "input"), ("6", "GND", "power_in")],
   [("7", "OUT", "power_out"), ("8", "~{FLT}", "open_collector"), ("9", "ILIM", "passive"), ("10", "IMON", "passive"),
    ("11", "dVdT", "passive"), ("12", "EP", "passive")],
   verify=True, desc="TI TPS2660 60V eFuse, reverse polarity. PIN NUMBERS ARE PLACEHOLDERS")

ic("LMR36006",
   [("1", "VIN", "power_in"), ("2", "EN", "input"), ("3", "PG", "open_collector"), ("4", "FB", "input"),
    ("5", "AGND", "power_in")],
   [("6", "SW", "power_out"), ("7", "BOOT", "passive"), ("8", "VCC", "passive"), ("9", "PGND", "power_in")],
   verify=True, desc="TI LMR36006 60V 0.6A buck. PIN NUMBERS ARE PLACEHOLDERS")

ic("PCAP04",
   [("1", "VDD", "power_in"), ("2", "VDD18_D", "passive"), ("3", "VDD18_A", "passive"), ("16", "SSN", "input"),
    ("17", "SCK", "input"), ("18", "MOSI", "input"), ("19", "MISO", "tri_state"), ("20", "INTN", "output"),
    ("21", "IIC_EN", "input"), ("4", "VSS", "power_in"), ("24", "VSS", "power_in")],
   [("5", "PC0", "passive"), ("6", "PC1", "passive"), ("7", "PC2", "passive"), ("8", "PC3", "passive"),
    ("9", "PC4", "passive"), ("10", "PC5", "passive"), ("11", "PCAUX", "passive"), ("12", "PT0REF", "passive"),
    ("13", "PT1", "passive"), ("14", "PT2", "passive"), ("15", "PT3", "passive"), ("22", "PG0", "bidirectional"),
    ("23", "PG1", "bidirectional")],
   width=22.86, verify=True, desc="ScioSense PCAP04 CDC. PIN NUMBERS ARE PLACEHOLDERS")

ic("DAC8760",
   [("1", "SCLK", "input"), ("2", "DIN", "input"), ("3", "LATCH", "input"), ("4", "SDO", "tri_state"),
    ("5", "CLR", "input"), ("6", "CLR-SEL", "input"), ("7", "~{ALARM}", "open_collector"), ("8", "DVDD", "power_in"),
    ("9", "DVDD-EN", "input"), ("10", "GND", "power_in"), ("11", "AVSS", "power_in"), ("12", "HART-IN", "input")],
   [("13", "AVDD", "power_in"), ("14", "VOUT", "output"), ("15", "+VSENSE", "input"), ("16", "-VSENSE", "input"),
    ("17", "IOUT", "output"), ("18", "BOOST", "passive"), ("19", "CCOMP", "passive"), ("20", "CAP1", "passive"),
    ("21", "CAP2", "passive"), ("22", "REFOUT", "passive"), ("23", "REFIN", "input"), ("24", "ISET-R", "passive")],
   width=22.86, verify=True, desc="TI DAC8760 V/I output DAC. PIN NUMBERS ARE PLACEHOLDERS")

ic("TPS26611",
   [("1", "IN", "passive"), ("2", "VDD", "power_in"), ("3", "VSS", "power_in")],
   [("4", "OUT", "passive"), ("5", "~{FLT}", "open_collector"), ("6", "MODE", "input")],
   width=17.78, verify=True, desc="TI TPS26611 4-20mA loop / analog I/O protector. PIN NUMBERS ARE PLACEHOLDERS")

ic("CMC", [("1", "A_IN", "passive"), ("3", "B_IN", "passive")], [("2", "A_OUT", "passive"), ("4", "B_OUT", "passive")],
   width=12.7, prefix="L", desc="Common mode choke 2-line")

ic("CONN_M8", [("8", "V+", "passive"), ("6", "GND", "passive"), ("4", "OUT1", "passive"), ("5", "OUT2", "passive"),
               ("3", "RS485_A", "passive"), ("2", "RS485_B", "passive"), ("1", "NC1", "passive"), ("7", "NC7", "passive"),
               ("9", "SHELL", "passive")], [], width=15.24, prefix="J",
   desc="M Connect 8-pin male, panel (pinout = EE364 compatible). Part number TBD")
ic("CONN_PROBE", [("1", "SENS_1", "passive"), ("2", "SENS_2", "passive"), ("3", "PT_F+", "passive"),
                  ("4", "PT_S+", "passive"), ("5", "PT_S-", "passive"), ("6", "PT_F-", "passive")], [],
   width=15.24, prefix="J", desc="Pressure feedthrough to sensor head (MK sensor + Pt1000 4-wire)")
ic("CONN_SWD", [("1", "VCC", "passive"), ("2", "SWDIO", "passive"), ("3", "NRST", "passive"),
                ("4", "SWCLK", "passive"), ("5", "GND", "passive"), ("6", "SWO", "passive")], [],
   width=12.7, prefix="J", desc="Tag-Connect TC2030 SWD")


def ic_geom(s):
    n = max(len(s["left"]), len(s["right"]))
    top = ((n - 1) // 2) * G
    w = s["w"]
    pins = []
    for i, (num, name, t) in enumerate(s["left"]):
        pins.append((num, name, t, -w / 2 - G, top - i * G, 0))
    for i, (num, name, t) in enumerate(s["right"]):
        pins.append((num, name, t, w / 2 + G, top - i * G, 180))
    bottom = top - (n - 1) * G
    return pins, (-w / 2, top + G, w / 2, bottom - G)


def two_pins():
    return [("1", "~", "passive", 0, 3.81, 270), ("2", "~", "passive", 0, -3.81, 90)]


def sym_pins(name):
    s = SYMBOLS[name]
    if s["kind"] == "ic":
        return ic_geom(s)[0]
    if s["kind"] == "flag":
        return [("1", "pwr", "power_out", 0, 0, 90)]
    return two_pins()


def graphics(name):
    s = SYMBOLS[name]
    st = "(stroke (width 0.254) (type default))"
    if s["kind"] == "ic":
        x1, y1, x2, y2 = ic_geom(s)[1]
        return [f"(rectangle (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) {st} (fill (type background)))"]
    if s["kind"] == "flag":
        return [f"(polyline (pts (xy 0 0) (xy 0 1.27) (xy -1.016 1.905) (xy 0 2.54) (xy 1.016 1.905) (xy 0 1.27)) {st} (fill (type none)))"]
    d = s["draw"]
    if d == "rect":
        return [f"(rectangle (start -1.016 2.54) (end 1.016 -2.54) {st} (fill (type none)))"]
    if d == "cap":
        return [f"(polyline (pts (xy -2.032 0.508) (xy 2.032 0.508)) {st} (fill (type none)))",
                f"(polyline (pts (xy -2.032 -0.508) (xy 2.032 -0.508)) {st} (fill (type none)))",
                f"(polyline (pts (xy 0 2.54) (xy 0 0.508)) {st} (fill (type none)))",
                f"(polyline (pts (xy 0 -2.54) (xy 0 -0.508)) {st} (fill (type none)))"]
    if d in ("ind", "ferrite"):
        fill = "outline" if d == "ferrite" else "none"
        return [f"(rectangle (start -0.762 2.54) (end 0.762 -2.54) {st} (fill (type {fill})))"]
    if d == "tvs":
        return [f"(polyline (pts (xy -1.27 2.54) (xy 1.27 2.54) (xy 0 0) (xy -1.27 2.54)) {st} (fill (type none)))",
                f"(polyline (pts (xy -1.27 -2.54) (xy 1.27 -2.54) (xy 0 0) (xy -1.27 -2.54)) {st} (fill (type none)))",
                f"(polyline (pts (xy -1.778 -0.508) (xy -1.27 0) (xy 1.27 0) (xy 1.778 0.508)) {st} (fill (type none)))"]
    if d == "gdt":
        return [f"(circle (center 0 0) (radius 2.032) {st} (fill (type none)))",
                f"(polyline (pts (xy -1.27 0.508) (xy 1.27 0.508)) {st} (fill (type none)))",
                f"(polyline (pts (xy -1.27 -0.508) (xy 1.27 -0.508)) {st} (fill (type none)))"]
    if d == "led":  # pin1 (위, y=+3.81) = K, pin2 (아래) = A → 전류 아래에서 위로
        return [f"(polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27) (xy 0 1.27) (xy -1.27 -1.27)) {st} (fill (type none)))",
                f"(polyline (pts (xy -1.27 1.27) (xy 1.27 1.27)) {st} (fill (type none)))"]
    raise ValueError(d)


def lib_symbol(name, prefixed):
    s = SYMBOLS[name]
    full = f"{LIB}:{name}" if prefixed else name
    power = " (power)" if s["kind"] == "flag" else ""
    hide_nums = " (pin_numbers hide)" if s["kind"] in ("two", "flag") else ""
    hide_names = " (pin_names (offset 0) hide)" if s["kind"] in ("two", "flag") else " (pin_names (offset 1.016))"
    out = [f"(symbol {q(full)}{power}{hide_nums}{hide_names} (in_bom {'no' if s['kind'] == 'flag' else 'yes'}) (on_board {'no' if s['kind'] == 'flag' else 'yes'})"]
    ref = s["prefix"]
    out.append(f'(property "Reference" {q(ref)} (at 0 {f(6.35 if s["kind"] != "ic" else ic_geom(s)[1][1] + 1.27)} 0) {FONT})')
    out.append(f'(property "Value" {q(name)} (at 0 -6.35 0) {FONT})')
    out.append(f'(property "Footprint" "" (at 0 0 0) {FONT_HIDE})')
    out.append(f'(property "Datasheet" "~" (at 0 0 0) {FONT_HIDE})')
    out.append(f'(property "ki_description" {q(s.get("desc", ""))} (at 0 0 0) {FONT_HIDE})')
    if s.get("verify"):
        out.append(f'(property "VERIFY" "YES - pin numbers are placeholders" (at 0 0 0) {FONT_HIDE})')
    out.append(f"(symbol {q(name + '_0_1')} " + " ".join(graphics(name)) + ")")
    pins = []
    for num, pname, t, x, y, ang in sym_pins(name):
        length = 2.54 if s["kind"] == "ic" else (1.27 if s["kind"] == "two" else 0)
        hide = " hide" if t == "no_connect" and False else ""
        pins.append(f"(pin {t} line (at {f(x)} {f(y)} {ang}) (length {f(length)}){hide} (name {q(pname)} {FONT}) (number {q(num)} {FONT}))")
    out.append(f"(symbol {q(name + '_1_1')} " + " ".join(pins) + ")")
    out.append(")")
    return " ".join(out)


# ───────────────────────── 회로 (부품별 핀→넷) ─────────────────────────
# (참조, 심볼, 값, 풋프린트, {핀번호: 넷}, 옵션)
# 넷이 None 이면 미연결(NC 표시)
FP = {
    "R0603": "Resistor_SMD:R_0603_1608Metric", "R2512": "Resistor_SMD:R_2512_6332Metric",
    "RMELF": "Resistor_SMD:R_MELF_MMB-0207", "C0603": "Capacitor_SMD:C_0603_1608Metric",
    "C0805": "Capacitor_SMD:C_0805_2012Metric", "C1206": "Capacitor_SMD:C_1206_3216Metric",
    "C1812": "Capacitor_SMD:C_1812_4532Metric", "SMA": "Diode_SMD:D_SMA", "SMB": "Diode_SMD:D_SMB",
    "SMC": "Diode_SMD:D_SMC", "FB0603": "Inductor_SMD:L_0603_1608Metric", "LED": "LED_SMD:LED_0603_1608Metric",
}

SHEETS = []


def sheet(file, title, parts):
    SHEETS.append(dict(file=file, title=title, parts=parts))


def R(ref, val, a, b, fp="R0603", **kw):
    return (ref, "R", val, FP.get(fp, fp), {"1": a, "2": b}, kw)


def C(ref, val, a, b, fp="C0603", **kw):
    return (ref, "C", val, FP.get(fp, fp), {"1": a, "2": b}, kw)


def TVS(ref, val, a, b, fp):
    return (ref, "TVS_BI", val, FP[fp], {"1": a, "2": b}, {})


def FLAG(ref, net):
    return (ref, "PWR_FLAG", "PWR_FLAG", "", {"1": net}, {})


sheet("connector.kicad_sch", "Connector, input surge protection, chassis", [
    ("J1", "CONN_M8", "M_Connect_8P_Male", "TBD:M_Connect_8P", {
        "8": "VIN_EXT", "6": "GND_IN", "4": "OUT1_EXT", "5": "OUT2_EXT", "3": "RS485_A_EXT", "2": "RS485_B_EXT",
        "1": None, "7": None, "9": "CHASSIS"}, {}),
    ("L1", "CMC", "CMC 2x1mH 0.3A", "TBD:CMC_WE-SL", {"1": "VIN_EXT", "2": "VIN_L", "3": "GND_IN", "4": "GND"}, {}),
    TVS("D1", "SMDJ36CA", "VIN_L", "GND", "SMC"),
    R("R1", "4.7 1W pulse", "VIN_L", "VIN_F", "RMELF"),
    TVS("D2", "SMBJ33CA", "VIN_F", "GND", "SMB"),
    C("C1", "100n 100V", "VIN_F", "GND", "C0805"),
    C("C2", "10u 50V", "VIN_F", "GND", "C1206"),
    R("R2", "1M", "GND", "CHASSIS", "R0603"),
    C("C3", "4.7n 2kV Y", "GND", "CHASSIS", "C1812"),
    ("GDT1", "GDT", "230V (Bourns 2038-23-SM)", "TBD:GDT_2038", {"1": "GND", "2": "CHASSIS"}, {}),
    FLAG("#FLG01", "GND"), FLAG("#FLG02", "VIN_F"),
])

sheet("power.kicad_sch", "eFuse, buck 5V, LDO 3.3V", [
    ("U1", "TPS2660", "TPS26600", "TBD:HTSSOP-16_TPS2660", {
        "1": "VIN_F", "2": "UV_DIV", "3": "OV_DIV", "4": "VIN_F", "5": "GND", "6": "GND",
        "7": "VIN_P", "8": "PWR_FLT", "9": "ILIM", "10": "IMON", "11": "DVDT", "12": "GND"}, {}),
    R("R3", "866k 1%", "VIN_F", "UV_DIV"),
    R("R4", "97.6k 1%", "UV_DIV", "OV_DIV"),
    R("R5", "36.5k 1%", "OV_DIV", "GND"),
    R("R6", "TBD (ILIM 150mA)", "ILIM", "GND"),
    R("R7", "10k", "IMON", "GND"),
    C("C4", "22n", "DVDT", "GND"),
    C("C5", "10u 50V", "VIN_P", "GND", "C1206"),
    C("C6", "100n 100V", "VIN_P", "GND", "C0805"),
    ("U2", "LMR36006", "LMR36006", "TBD:VQFN-HR-12_LMR36006", {
        "1": "VIN_P", "2": "VIN_P", "3": None, "4": "BUCK_FB", "5": "GND",
        "6": "BUCK_SW", "7": "BUCK_BOOT", "8": "BUCK_VCC", "9": "GND"}, {}),
    C("C7", "2.2u 100V", "VIN_P", "GND", "C1206"),
    C("C8", "100n", "BUCK_BOOT", "BUCK_SW"),
    C("C9", "1u", "BUCK_VCC", "GND"),
    ("L2", "L", "22uH", "TBD:L_4x4mm", {"1": "BUCK_SW", "2": "+5V"}, {}),
    C("C10", "22u 10V", "+5V", "GND", "C0805"),
    R("R8", "100k 1%", "+5V", "BUCK_FB"),
    R("R9", "24.9k 1%", "BUCK_FB", "GND"),
    ("U3", "TPS7A2033", "TPS7A2033PDBVR", "Package_TO_SOT_SMD:SOT-23-5", {
        "1": "+5V", "3": "+5V", "2": "GND", "5": "+3V3", "4": None}, {}),
    C("C11", "1u", "+5V", "GND"),
    C("C12", "1u", "+3V3", "GND"),
    ("FB1", "FB", "600R@100MHz", FP["FB0603"], {"1": "+3V3", "2": "+3V3A"}, {}),
    C("C13", "10u", "+3V3A", "GND", "C0805"),
    FLAG("#FLG03", "+5V"), FLAG("#FLG04", "+3V3A"),
])

mcu_nets = {
    "1": "+3V3", "19": "+3V3", "32": "+3V3", "64": "+3V3", "48": "+3V3", "13": "VDDA", "12": "GND",
    "18": "GND", "31": "GND", "47": "GND", "63": "GND", "7": "NRST", "60": "BOOT0", "5": None, "6": None,
    "15": "RS485_DE", "16": "RS485_TX", "17": "RS485_RX", "21": "SPI_SCK", "22": "SPI_MISO", "23": "SPI_MOSI",
    "46": "SWDIO", "49": "SWCLK", "55": "SWO", "26": "CS_CDC", "27": "CS_ADC", "28": "ADC_DRDY",
    "29": "DAC1_LATCH", "30": "DAC2_LATCH", "33": "CDC_INT", "57": "LED", "37": "OUT1_FLT", "38": "OUT2_FLT",
    "39": "DAC1_ALARM", "40": "DAC2_ALARM", "51": "PWR_FLT",
}
for num, _, _ in SYMBOLS["STM32L431RCTx"]["right"]:
    mcu_nets.setdefault(num, None)

sheet("mcu.kicad_sch", "MCU STM32L431, SWD, status LED", [
    ("U4", "STM32L431RCTx", "STM32L431RCT6", "Package_QFP:LQFP-64_10x10mm_P0.5mm", mcu_nets, {}),
    C("C14", "100n", "+3V3", "GND"), C("C15", "100n", "+3V3", "GND"), C("C16", "100n", "+3V3", "GND"),
    C("C17", "100n", "+3V3", "GND"), C("C18", "4.7u", "+3V3", "GND", "C0805"),
    ("FB2", "FB", "600R@100MHz", FP["FB0603"], {"1": "+3V3", "2": "VDDA"}, {}),
    C("C19", "1u", "VDDA", "GND"), C("C20", "100n", "VDDA", "GND"),
    C("C21", "100n", "NRST", "GND"),
    R("R10", "10k", "BOOT0", "GND"),
    R("R11", "10k", "+3V3", "PWR_FLT"), R("R12", "10k", "+3V3", "OUT1_FLT"), R("R13", "10k", "+3V3", "OUT2_FLT"),
    R("R14", "10k", "+3V3", "DAC1_ALARM"), R("R15", "10k", "+3V3", "DAC2_ALARM"),
    R("R16", "1k", "LED", "LED_A"),
    ("D3", "LED", "Green", FP["LED"], {"1": "GND", "2": "LED_A"}, {}),
    ("J2", "CONN_SWD", "TC2030-IDC-NL", "Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical", {
        "1": "+3V3", "2": "SWDIO", "3": "NRST", "4": "SWCLK", "5": "GND", "6": "SWO"}, {}),
    FLAG("#FLG05", "VDDA"),
])

sheet("measurement.kicad_sch", "Capacitance (PCAP04) and Pt1000 (ADS1220)", [
    ("J3", "CONN_PROBE", "Feedthrough 6P", "TBD:Feedthrough_6P", {
        "1": "SENS_C1", "2": "SENS_C2", "3": "PT_FP", "4": "PT_SP", "5": "PT_SN", "6": "REF_P"}, {}),
    ("U5", "PCAP04", "PCAP04-AQFM-24", "TBD:QFN-24_PCAP04", {
        "1": "+3V3A", "2": "CDC_V18D", "3": "CDC_V18A", "16": "CS_CDC", "17": "SPI_SCK", "18": "SPI_MOSI",
        "19": "SPI_MISO", "20": "CDC_INT", "21": "GND", "4": "GND", "24": "GND",
        "5": "CREF_A", "6": "CREF_B", "7": "SENS_C1", "8": "SENS_C2", "9": None, "10": None, "11": None,
        "12": None, "13": None, "14": None, "15": None, "22": None, "23": None}, {}),
    C("C22", "220p C0G 1%", "CREF_A", "CREF_B"),
    C("C23", "100n", "+3V3A", "GND"), C("C24", "1u", "+3V3A", "GND"),
    C("C25", "1u", "CDC_V18D", "GND"), C("C26", "1u", "CDC_V18A", "GND"),
    ("U6", "ADS1220", "ADS1220IPWR", "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", {
        "1": "SPI_SCK", "2": "CS_ADC", "3": "GND", "16": "SPI_MOSI", "15": "SPI_MISO", "14": "ADC_DRDY",
        "13": "+3V3", "4": "GND", "12": "+3V3A", "11": "PT_FP", "10": "PT_SP_F", "7": "PT_SN_F", "6": None,
        "9": "REF_P", "8": "REF_N", "5": "GND"}, {}),
    R("R17", "1k", "PT_SP", "PT_SP_F"), R("R18", "1k", "PT_SN", "PT_SN_F"),
    C("C27", "10n C0G", "PT_SP_F", "PT_SN_F"),
    R("R19", "4.02k 0.01% 5ppm", "REF_P", "REF_N", "R0603"),
    R("R20", "1k", "REF_N", "GND"),
    C("C28", "100n", "+3V3", "GND"), C("C29", "100n", "+3V3A", "GND"),
])

ao = []
for ch in (1, 2):
    b = ch * 10
    ao += [
        (f"U{6 + ch}", "DAC8760", "DAC8760IPWP", "TBD:HTSSOP-24_DAC8760", {
            "1": "SPI_SCK", "2": "SPI_MOSI", "3": f"DAC{ch}_LATCH", "4": "SPI_MISO", "5": "GND", "6": "GND",
            "7": f"DAC{ch}_ALARM", "8": "+3V3", "9": "GND", "10": "GND", "11": "GND", "12": None,
            "13": "VIN_P", "14": f"DAC{ch}_OUT", "15": f"DAC{ch}_SENSE", "16": "GND", "17": f"DAC{ch}_OUT",
            "18": None, "19": None, "20": None, "21": None, "22": f"DAC{ch}_REF", "23": f"DAC{ch}_REF", "24": None}, {}),
        (f"U{8 + ch}", "TPS26611", "TPS26611", "TBD:TPS26611", {
            "1": f"DAC{ch}_OUT", "2": "VIN_P", "3": "GND", "4": f"OUT{ch}_P", "5": f"OUT{ch}_FLT", "6": "GND"}, {}),
        R(f"R{20 + b}", "10 0.5W pulse", f"OUT{ch}_P", f"OUT{ch}_EXT", "R2512"),
        TVS(f"D{20 + b}", "SMAJ33CA", f"OUT{ch}_EXT", "GND", "SMA"),
        C(f"C{30 + b}", "1n 100V", f"OUT{ch}_EXT", "GND", "C0603"),
        R(f"R{21 + b}", "10k", f"OUT{ch}_EXT", f"DAC{ch}_SENSE"),
        C(f"C{31 + b}", "100n 50V", "VIN_P", "GND", "C0805"),
        C(f"C{32 + b}", "4.7u 50V", "VIN_P", "GND", "C1206"),
        C(f"C{33 + b}", "100n", "+3V3", "GND"),
        C(f"C{34 + b}", "100n", f"DAC{ch}_REF", "GND"),
    ]
sheet("analog_out.kicad_sch", "Analog outputs x2 (V/I selectable) with miswiring protection", ao)

sheet("rs485.kicad_sch", "RS-485 (+/-70V fault protected)", [
    ("U11", "THVD2450", "THVD2450DR", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", {
        "4": "RS485_TX", "1": "RS485_RX", "2": "RS485_DE", "3": "RS485_DE", "8": "+3V3", "6": "RS485_A",
        "7": "RS485_B", "5": "GND"}, {}),
    C("C60", "100n", "+3V3", "GND"),
    R("R60", "2.2 (or 0R)", "RS485_A", "RS485_A_EXT", "R0603"),
    R("R61", "2.2 (or 0R)", "RS485_B", "RS485_B_EXT", "R0603"),
    TVS("D60", "SMAJ40CA (DNP opt)", "RS485_A_EXT", "GND", "SMA"),
    TVS("D61", "SMAJ40CA (DNP opt)", "RS485_B_EXT", "GND", "SMA"),
])

# ───────────────────────── 시트 파일 생성 ─────────────────────────
ROOT_UUID = uid("root")


def label(net, x, y, ang, key):
    just = "right" if ang == 180 else "left"
    return (f"(global_label {q(net)} (shape passive) (at {f(x)} {f(y)} {ang}) (fields_autoplaced) "
            f"(effects (font (size 1.27 1.27)) (justify {just})) (uuid {uid(key, 'lbl')}) "
            f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {f(x)} {f(y)} 0) {FONT_HIDE}))')


def wire(x1, y1, x2, y2, key):
    return f"(wire (pts (xy {f(x1)} {f(y1)}) (xy {f(x2)} {f(y2)})) (stroke (width 0) (type default)) (uuid {uid(key, 'w')}))"


def footprint_box(symname):
    s = SYMBOLS[symname]
    if s["kind"] == "ic":
        x1, y1, x2, y2 = ic_geom(s)[1]
        lw = 30.48 if s["left"] else 0
        rw = 30.48 if s["right"] else 0
        return (x2 - x1) + lw + rw + 10.16, (y1 - y2) + 12.7, lw + (x2 - x1) / 2 + 5.08, y1 + 7.62
    return 33.02, 25.4, 5.08, 10.16


def snap(v):
    return round(v / G) * G


def build_sheet(sh, sheet_uuid, used_libs):
    items = []
    x0, y0, rowh, x = 20.32, 30.48, 0, 20.32
    maxx = 400
    path = f"/{ROOT_UUID}/{sheet_uuid}"
    for ref, sym, val, fp, nets, opt in sh["parts"]:
        used_libs.add(sym)
        w, h, ox, oy = footprint_box(sym)
        if x + w > maxx:
            x = x0
            y0 += rowh
            rowh = 0
        cx, cy = snap(x + ox), snap(y0 + oy)
        x += w
        rowh = max(rowh, h)
        s = SYMBOLS[sym]
        key = (sh["file"], ref)
        pin_uuids = " ".join(f"(pin {q(p[0])} (uuid {uid(key, 'pin', p[0])}))" for p in sym_pins(sym))
        props = [f'(property "Reference" {q(ref)} (at {f(cx + 2.54)} {f(cy - (ic_geom(s)[1][1] + 2.54 if s["kind"] == "ic" else 1.27))} 0) (effects (font (size 1.27 1.27)) (justify left)))',
                 f'(property "Value" {q(val)} (at {f(cx + 2.54)} {f(cy + (-ic_geom(s)[1][3] + 2.54 if s["kind"] == "ic" else 1.27))} 0) (effects (font (size 1.27 1.27)) (justify left)))',
                 f'(property "Footprint" {q(fp)} (at {f(cx)} {f(cy)} 0) {FONT_HIDE})',
                 f'(property "Datasheet" "~" (at {f(cx)} {f(cy)} 0) {FONT_HIDE})']
        if s.get("verify"):
            props.append(f'(property "VERIFY" "YES - pin numbers are placeholders" (at {f(cx)} {f(cy)} 0) {FONT_HIDE})')
        if "DNP" in val:
            props.append(f'(property "Note" "DNP if surge pre-test passes without it" (at {f(cx)} {f(cy)} 0) {FONT_HIDE})')
        items.append(f"(symbol (lib_id {q(LIB + ':' + sym)}) (at {f(cx)} {f(cy)} 0) (unit 1) "
                     f"(in_bom {'no' if s['kind'] == 'flag' else 'yes'}) (on_board {'no' if s['kind'] == 'flag' else 'yes'}) (dnp no) "
                     f"(uuid {uid(key, 'sym')}) " + " ".join(props) + f" {pin_uuids} "
                     f"(instances (project {q(PROJECT)} (path {q(path)} (reference {q(ref)}) (unit 1)))))")
        for num, pname, t, px, py, ang in sym_pins(sym):
            ex, ey = cx + px, cy - py
            net = nets.get(num, "__missing__")
            if net == "__missing__":
                raise SystemExit(f"{ref} pin {num} ({pname}) has no net assignment")
            if net is None or t == "no_connect":
                items.append(f"(no_connect (at {f(ex)} {f(ey)}) (uuid {uid(key, 'nc', num)}))")
                continue
            if s["kind"] == "flag":
                lx, ly, la = ex, ey - G, 0
            elif ang == 0:      # 왼쪽 핀
                lx, ly, la = ex - G, ey, 180
            elif ang == 180:    # 오른쪽 핀
                lx, ly, la = ex + G, ey, 0
            elif ang == 270:    # 위쪽 핀
                lx, ly, la = ex, ey - G, 0
            else:               # 아래쪽 핀
                lx, ly, la = ex, ey + G, 0
            items.append(wire(ex, ey, lx, ly, key + (num,)))
            items.append(label(net, lx, ly, la, key + (num,)))
    return items


def title_block(title, page):
    return (f'(title_block (title {q("HMT500 - " + title)}) (date "2026-09-26") (rev "0.1") '
            f'(company "DOTECH Co., Ltd.") (comment 1 "Oil moisture transmitter HMT500") '
            f'(comment 2 "Generated by hardware/kicad/gen_hmt500.py - see docs/hw/circuit-design.md") '
            f'(comment 3 "Symbols with VERIFY=YES have placeholder pin numbers"))')


def write_sheet(sh, idx):
    sheet_uuid = uid("sheet", sh["file"])
    used = set()
    body = build_sheet(sh, sheet_uuid, used)
    libs = "\n".join(lib_symbol(n, True) for n in sorted(used))
    txt = (f"(kicad_sch (version 20230121) (generator eeschema) (uuid {uid('file', sh['file'])}) (paper \"A3\")\n"
           f"{title_block(sh['title'], idx)}\n(lib_symbols\n{libs}\n)\n" + "\n".join(body) + "\n)\n")
    open(os.path.join(OUT, sh["file"]), "w", encoding="utf-8").write(txt)
    return sheet_uuid


def write_root(sheet_uuids):
    items = []
    x, y = 30.48, 50.8
    for i, (sh, su) in enumerate(zip(SHEETS, sheet_uuids)):
        sx, sy = x + (i % 3) * 127, y + (i // 3) * 76.2
        items.append(f"(sheet (at {f(sx)} {f(sy)}) (size 101.6 50.8) (fields_autoplaced) "
                     f"(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid {su}) "
                     f'(property "Sheetname" {q(sh["title"])} (at {f(sx)} {f(sy - 0.7)} 0) (effects (font (size 1.27 1.27)) (justify left bottom))) '
                     f'(property "Sheetfile" {q(sh["file"])} (at {f(sx)} {f(sy + 51.4)} 0) (effects (font (size 1.27 1.27)) (justify left top))) '
                     f'(instances (project {q(PROJECT)} (path {q("/" + ROOT_UUID)} (page {q(str(i + 2))})))))')
    notes = [
        "DOTECH HMT500 Oil Moisture Transmitter - Schematic v0.1",
        "Outputs: RS-485 Modbus RTU + 2x analog (V/I selectable). Supply 12-30 V DC.",
        "Protection: any pin pair +/-30 V continuous miswiring, surge +/-1 kV (design target).",
        "Connections are made with global net labels. Placement/wiring cleanup is next step in KiCad.",
        "Parts with field VERIFY=YES (TPS2660, LMR36006, PCAP04, DAC8760, TPS26611) have PLACEHOLDER pin numbers.",
        "TBD footprints: M Connect 8P, CMC, GDT, feedthrough, inductor, placeholder-pinout ICs.",
    ]
    for i, n in enumerate(notes):
        items.append(f"(text {q(n)} (at 30.48 {f(210 + i * 7.62)} 0) (effects (font (size 2 2)) (justify left bottom)) (uuid {uid('note', i)}))")
    txt = (f"(kicad_sch (version 20230121) (generator eeschema) (uuid {ROOT_UUID}) (paper \"A3\")\n"
           f"{title_block('Top', 1)}\n(lib_symbols)\n" + "\n".join(items) +
           '\n(sheet_instances (path "/" (page "1")))\n)\n')
    open(os.path.join(OUT, PROJECT + ".kicad_sch"), "w", encoding="utf-8").write(txt)


def write_lib():
    body = "\n".join(lib_symbol(n, False) for n in SYMBOLS)
    open(os.path.join(OUT, LIB + ".kicad_sym"), "w", encoding="utf-8").write(
        f"(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n{body}\n)\n")
    open(os.path.join(OUT, "sym-lib-table"), "w").write(
        f'(sym_lib_table\n  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.kicad_sym")(options "")(descr "HMT500 project symbols"))\n)\n')


def write_project():
    pro = {"meta": {"filename": PROJECT + ".kicad_pro", "version": 1},
           "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
           "sheets": [[ROOT_UUID, "Root"]] + [[uid("sheet", s["file"]), s["title"]] for s in SHEETS],
           "text_variables": {}}
    open(os.path.join(OUT, PROJECT + ".kicad_pro"), "w").write(json.dumps(pro, indent=2) + "\n")


def write_bom():
    import csv
    groups = {}
    for sh in SHEETS:
        for ref, sym, val, fp, nets, opt in sh["parts"]:
            if ref.startswith("#"):
                continue
            k = (sym, val, fp)
            groups.setdefault(k, []).append(ref)
    with open(os.path.join(OUT, PROJECT + "_BOM.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Qty", "References", "Symbol", "Value", "Footprint", "Verify"])
        for (sym, val, fp), refs in sorted(groups.items(), key=lambda kv: kv[1][0]):
            w.writerow([len(refs), " ".join(sorted(refs, key=lambda r: (r.rstrip("0123456789"), int("0" + "".join(c for c in r if c.isdigit()))))),
                        sym, val, fp, "pin numbers" if SYMBOLS[sym].get("verify") else ("footprint" if fp.startswith("TBD") else "")])


def main():
    os.makedirs(OUT, exist_ok=True)
    write_bom()
    write_lib()
    uuids = [write_sheet(sh, i + 2) for i, sh in enumerate(SHEETS)]
    write_root(uuids)
    write_project()
    # 넷 사용 횟수 점검: 한 번만 쓰인 넷은 연결 누락 가능성
    count = {}
    for sh in SHEETS:
        for ref, sym, val, fp, nets, opt in sh["parts"]:
            for n in nets.values():
                if n:
                    count[n] = count.get(n, 0) + 1
    single = sorted(n for n, c in count.items() if c < 2)
    print("sheets:", len(SHEETS), "parts:", sum(len(s["parts"]) for s in SHEETS), "nets:", len(count))
    if single:
        print("WARNING single-use nets:", single)


if __name__ == "__main__":
    main()
