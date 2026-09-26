"""그린 회로도(KiCad 넷리스트)가 설계 의도(gen_hmt500.py의 nets=...)와 같은지 검사한다.

KiCad 7 CLI에는 ERC가 없어서 이 검사로 연결을 검증한다.
  kicad-cli sch export netlist -o hmt500.net hardware/kicad/HMT500/HMT500.kicad_sch
  python3 hardware/kicad/check_netlist.py hmt500.net

비교 방법: 핀을 넷으로 나눈 분할(partition)이 같아야 한다.
이름이 있는 넷(전원 심볼, 전역 라벨)은 이름까지 같아야 한다.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_hmt500 as g  # noqa: E402


def parse(path):
    txt = open(path, encoding="utf-8").read()
    nets = {}
    blocks = re.split(r"\(net \(code ", txt)[1:]
    for blk in blocks:
        name = re.search(r'\(name "([^"]*)"\)', blk).group(1).lstrip("/")
        nodes = frozenset(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', blk))
        nets[name] = nodes
    return nets


def main(path):
    got = parse(path)
    want = {k: frozenset(v) for k, v in g.intended_nets().items()}
    got_sets = {v: k for k, v in got.items() if not k.startswith("unconnected-")}
    errors = 0
    for name, nodes in sorted(want.items()):
        if nodes in got_sets:
            gname = got_sets[nodes]
            if not gname.startswith("Net-") and gname != name:
                print(f"NAME MISMATCH: intended {name} drawn as {gname}")
                errors += 1
            continue
        # 어느 넷에 섞였는지 보고
        hits = {k: v & nodes for k, v in got.items() if v & nodes}
        print(f"NET {name}: intended {sorted(nodes)}")
        for k, v in hits.items():
            print(f"    drawn in {k}: {sorted(got[k])}")
        errors += 1
    want_sets = set(want.values())
    for k, v in got.items():
        if k.startswith("unconnected-"):
            continue
        if v not in want_sets:
            print(f"EXTRA/WRONG NET {k}: {sorted(v)}")
            errors += 1
    print(f"intended nets: {len(want)}, drawn nets: {sum(1 for k in got if not k.startswith('unconnected-'))}, errors: {errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
