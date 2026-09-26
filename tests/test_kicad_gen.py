"""KiCad 회로도 생성기 점검: 모든 핀에 넷(또는 NC)이 지정되고, 한 번만 쓰인 넷이 없어야 한다."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "hardware", "kicad"))

import gen_hmt500 as g  # noqa: E402


class KicadGenTest(unittest.TestCase):
    def test_every_pin_assigned(self):
        for sh in g.SHEETS:
            for ref, sym, val, fp, nets, opt in sh["parts"]:
                pins = {p[0] for p in g.sym_pins(sym)}
                self.assertEqual(pins, set(nets), f"{ref} ({sym}) pin/net mismatch")

    def test_no_single_use_nets(self):
        count = {}
        for sh in g.SHEETS:
            for ref, sym, val, fp, nets, opt in sh["parts"]:
                for n in nets.values():
                    if n:
                        count[n] = count.get(n, 0) + 1
        self.assertEqual([n for n, c in count.items() if c < 2], [])

    def test_unique_references(self):
        refs = [p[0] for sh in g.SHEETS for p in sh["parts"]]
        self.assertEqual(len(refs), len(set(refs)))


if __name__ == "__main__":
    unittest.main()
