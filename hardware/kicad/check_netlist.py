"""KiCad가 내보낸 넷리스트가 생성기의 설계 의도와 같은지 검사한다 (KiCad 7 CLI에는 ERC가 없어서 대체).

kicad-cli sch export netlist -o hmt500.net hardware/kicad/HMT500/HMT500.kicad_sch
python3 hardware/kicad/check_netlist.py hmt500.net
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_hmt500 as g  # noqa: E402


def parse(path):
    txt = open(path, encoding="utf-8").read()
    nets = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', txt, re.S):
        name = m.group(1).lstrip("/")
        nodes = set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)))
        nets[name] = nodes
    return nets


def main(path):
    got = parse(path)
    want = {}
    for sh in g.SHEETS:
        for ref, sym, val, fp, nets, opt in sh["parts"]:
            if ref.startswith("#"):
                continue
            for pin, net in nets.items():
                if net:
                    want.setdefault(net, set()).add((ref, pin))
    errors = 0
    for net, nodes in sorted(want.items()):
        if net not in got:
            print("MISSING NET", net)
            errors += 1
            continue
        if got[net] != nodes:
            print("MISMATCH", net, "missing:", sorted(nodes - got[net]), "extra:", sorted(got[net] - nodes))
            errors += 1
    unexpected = [n for n in got if n not in want and not n.startswith("unconnected-") and not n.startswith("Net-")]
    for n in unexpected:
        print("UNEXPECTED NET", n, sorted(got[n]))
        errors += 1
    stray = [n for n in got if n.startswith("Net-")]
    for n in stray:
        print("UNLABELED NET", n, sorted(got[n]))
        errors += 1
    print(f"nets checked: {len(want)}, errors: {errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
