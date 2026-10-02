"""Build JLCPCB PCBA files (BOM + CPL) for HMT500(ED260313A): one board, 4 layers, parts on both sides.

  python3 manufacturing/jlc/make_jlcpcb_files.py     (needs kicad-cli)
    -> manufacturing/jlc/jlcpcb/HMT500(ED260313A)_BOM_JLC.csv   Comment, Designator, Footprint, LCSC Part #
    -> manufacturing/jlc/jlcpcb/HMT500(ED260313A)_CPL_JLC.csv   Designator, Mid X, Mid Y, Layer, Rotation
    -> manufacturing/jlc/jlcpcb/jlc_parts_map.csv             value/footprint -> LCSC number (filled in after lookup)

- The CPL comes straight from the KiCad placement (same coordinates as the Gerbers, absolute KiCad coordinates).
- LCSC numbers come from make_parts_list.LCSC (decision #34). Parts marked "글로벌 소싱" have an empty LCSC column:
  on JLC's parts matching page pick them through Global Sourcing (JLC buys the exact MPN) or supply them.
- Board-only footprints are left out: J2 (Tag-Connect pads) and J5 (chassis wire solder hole).
- Rotation: KiCad values. JLC's rotation origin differs for some packages, so check them in JLC's
  placement preview before ordering. Put fixes in the rot_offset column of the map.
"""

import csv
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KICAD = os.path.join(HERE, "..", "..", "hardware", "kicad")
sys.path.insert(0, KICAD)
import make_parts_list as PL  # noqa: E402

PROJECT = PL.PROJECT
OUT = os.path.join(HERE, "jlcpcb")
MAP_CSV = os.path.join(OUT, "jlc_parts_map.csv")
BOARD_ONLY = {"J2", "J5"}              # no part placed (pads / hole only)
MAP_FIELDS = ["symbol", "value", "footprint", "refs", "qty", "mfr", "mpn", "lcsc", "jlc_type", "rot_offset", "note"]


DNP = set()


def bom_rows():
    with open(os.path.join(KICAD, PROJECT, PROJECT + "_BOM.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_map():
    """Keep the lcsc / jlc_type / rot_offset / note already entered by hand; refresh everything else from the schematic."""
    old = {}
    if os.path.exists(MAP_CSV):
        with open(MAP_CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                old[(r["symbol"], r["value"])] = r
    rows = []
    for b in bom_rows():
        key = (b["Symbol"], b["Value"])
        if key[1].startswith("DNP"):                 # 미실장: BOM·CPL에서 뺌 (풋프린트만 PCB에)
            DNP.update(b["References"].split())
            continue
        refs = [r for r in b["References"].split() if r not in BOARD_ONLY]
        if not refs:
            continue
        _, mfr, mpn, *_ = PL.MAP[key]
        o = old.get(key, {})
        lcsc, jt, note = o.get("lcsc", ""), o.get("jlc_type", ""), o.get("note", "")
        if key in PL.LCSC:                           # 결정 #34: 부품리스트의 LCSC 품번이 기준
            mfr, mpn, lcsc, jt, note = PL.LCSC[key]
        rows.append(dict(symbol=key[0], value=key[1], footprint=b["Footprint"].split(":")[-1], refs=" ".join(refs),
                         qty=len(refs), mfr=mfr, mpn=mpn, lcsc=lcsc, jlc_type=jt,
                         rot_offset=o.get("rot_offset", ""), note=note))
    return rows


def positions():
    tmp = os.path.join(OUT, "_pos.csv")
    subprocess.run(["kicad-cli", "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
                    "-o", tmp, os.path.join(KICAD, PROJECT, PROJECT + ".kicad_pcb")], check=True, capture_output=True)
    with open(tmp, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    os.remove(tmp)
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    m = load_map()
    with open(MAP_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=MAP_FIELDS)
        w.writeheader()
        w.writerows(m)
    with open(os.path.join(OUT, PROJECT + "_BOM_JLC.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for r in m:
            w.writerow([f"{r['value']} {r['mpn']}".strip(), ",".join(r["refs"].split()), r["footprint"], r["lcsc"]])
    rot = {}
    for r in m:
        for ref in r["refs"].split():
            rot[ref] = float(r["rot_offset"] or 0)
    n = 0
    with open(os.path.join(OUT, PROJECT + "_CPL_JLC.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for p in positions():
            ref = p["Ref"]
            if ref in BOARD_ONLY or ref in DNP:
                continue
            layer = "Top" if p["Side"].lower().startswith("top") else "Bottom"
            w.writerow([ref, f"{float(p['PosX']):.3f}mm", f"{float(p['PosY']):.3f}mm", layer,
                        f"{(float(p['Rot']) + rot.get(ref, 0)) % 360:g}"])
            n += 1
    done = sum(1 for r in m if r["lcsc"])
    print(f"BOM lines {len(m)} (LCSC filled {done}), CPL parts {n}")


if __name__ == "__main__":
    main()
