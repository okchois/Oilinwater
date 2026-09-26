"""KiCad 회로도 생성기 점검.

- 그리기 규칙(선 중간 핀, 연결 안 된 핀, 용지 밖, 표제란 침범) 위반이 없어야 한다.
- 모든 설계 넷은 두 개 이상의 핀을 잇고, 참조번호는 중복되지 않아야 한다.
- kicad-cli가 있으면 넷리스트를 내보내 그린 회로 = 설계 의도인지 확인한다.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "hardware", "kicad"))

import check_netlist  # noqa: E402
import gen_hmt500 as g  # noqa: E402
import gen_pcb_outline as pcb  # noqa: E402


class KicadGenTest(unittest.TestCase):
    def test_drawing_rules(self):
        for S in g.SHEETS:
            g.validate(S)

    def test_nets_have_two_or_more_pins(self):
        single = [n for n, nodes in g.intended_nets().items() if len(nodes) < 2]
        self.assertEqual(single, [])

    def test_unique_references(self):
        refs = [r for S in g.SHEETS for r in S.order if not r.startswith("#")]
        self.assertEqual(len(refs), len(set(refs)))

    def test_every_part_pin_has_intent(self):
        for S in g.SHEETS:
            for ref in S.order:
                if ref.startswith("#"):
                    continue
                self.assertIn(ref, S.nets, f"{ref} has no net intent")

    @unittest.skipUnless(shutil.which("kicad-cli"), "kicad-cli not installed")
    def test_drawn_netlist_matches_intent(self):
        g.write_all()
        with tempfile.TemporaryDirectory() as d:
            net = os.path.join(d, "hmt500.net")
            subprocess.run(["kicad-cli", "sch", "export", "netlist", "-o", net,
                            os.path.join(g.OUT, "HMT500.kicad_sch")], check=True, capture_output=True)
            self.assertEqual(check_netlist.main(net), 0)


class PcbOutlineTest(unittest.TestCase):
    def test_outline_closed_and_balanced(self):
        body = pcb.build()
        self.assertEqual(body.count("("), body.count(")"))
        segs = pcb.fillet_outline(pcb.outline_pts(), pcb.P.PCB["corner_r"])
        ends = [s[-1] for s in segs]
        starts = [s[1] for s in segs]
        for e, s in zip(ends, starts[1:] + starts[:1]):
            self.assertAlmostEqual(e[0], s[0], places=6)
            self.assertAlmostEqual(e[1], s[1], places=6)

    @unittest.skipUnless(shutil.which("kicad-cli"), "kicad-cli 없음")
    def test_kicad_loads_board(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "b.kicad_pcb")
            open(f, "w", encoding="utf-8").write(pcb.build())
            r = subprocess.run(["kicad-cli", "pcb", "export", "svg", "--layers", "Edge.Cuts", "-o",
                                os.path.join(d, "b.svg"), f], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
