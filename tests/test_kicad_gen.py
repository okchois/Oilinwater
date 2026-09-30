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

    def test_net_names_distinct_from_parts(self):
        """네트 이름은 참조번호·부품값·심볼 이름과 같거나 참조번호 모양(R12 등)이면 안 된다."""
        import re
        nets = set(g.intended_nets())
        refs = {r for S in g.SHEETS for r in S.order if not r.startswith("#")}
        vals = {S.parts[r]["val"] for S in g.SHEETS for r in S.order if not r.startswith("#")}
        syms = {k for k, v in g.SYM.items() if v["kind"] not in ("pwr", "flag")}
        self.assertEqual(nets & (refs | vals | syms), set())
        self.assertEqual([n for n in nets if re.fullmatch(r"(R|C|L|U|D|J|FB|Q|GDT)\d+", n)], [])

    def test_label_direction(self):
        """라벨 모양이 신호 방향을 나타냄: MCU가 주는 선은 MCU 쪽 output, 받는 쪽 input."""
        sh = {}
        for S in g.SHEETS:
            for (net, *_), s in zip(S.labels, g.label_shapes(S)):
                sh.setdefault((S.file.split("_", 1)[1], net), set()).add(s)
        self.assertEqual(sh[("mcu.kicad_sch", "DAC_MOSI")], {"output"})
        self.assertEqual(sh[("analog_out.kicad_sch", "DAC_MOSI")], {"input"})
        self.assertEqual(sh[("mcu.kicad_sch", "DAC_MISO")], {"input"})
        self.assertEqual(sh[("analog_out.kicad_sch", "DAC_ALARM")], {"output"})
        self.assertEqual(sh[("rs485.kicad_sch", "RS485_RX")], {"output"})
        self.assertEqual(sh[("connector.kicad_sch", "RS485_A_EXT")], {"bidirectional"})
        self.assertEqual(sh[("measurement.kicad_sch", "PT_P")], {"passive"})

    def test_wiring_straight(self):
        """작도 규칙: 가까운 같은 시트 연결은 라벨 대신 선으로 (꺾임은 연결당 2개 이하, 시트당 6개 이하),
        분기점은 실제 3갈래 노드만 (전체 40개 이하)."""
        total_j = 0
        for S in g.SHEETS:
            bends, js = g.wire_metrics(S)
            self.assertLessEqual(bends, 6, S.file)
            total_j += js
        self.assertLessEqual(total_j, 40)

    def test_near_labels_wired(self):
        """같은 시트에서 라벨로만 잇는 넷은 멀리 떨어진 것만 허용 (가까운 것은 선으로)."""
        import math
        for S in g.SHEETS:
            pts = {}
            for net, pt, *_ in S.labels:
                pts.setdefault(net, []).append(pt)
            for net, ps in pts.items():
                for i, a in enumerate(ps):
                    for b in ps[i + 1:]:
                        d = math.dist(a, b)
                        self.assertTrue(d < 1.5 or d > 10, f"{S.file}: {net} labels {a} {b} only {d:.1f} apart")

    def test_hangul_font_has_all_glyphs(self):
        """한글 글자(나눔고딕으로 출력)에 쓰인 모든 문자가 글꼴에 있어야 한다 (네모 깨짐 방지)."""
        try:
            from fontTools.ttLib import TTFont
        except ImportError:
            self.skipTest("fontTools 없음")
        path = subprocess.run(["fc-match", "-f", "%{file}", g.HANGUL_FACE], capture_output=True, text=True).stdout
        if not path or "Nanum" not in path:
            self.skipTest("NanumGothic 없음")
        cmap = TTFont(path).getBestCmap()
        for S in g.SHEETS:
            for t, *_ in S.texts:
                if g.has_hangul(t):
                    missing = {ch for ch in g.ko_safe(t) if ord(ch) not in cmap}
                    self.assertEqual(missing, set(), t)

    def test_hangul_uses_truetype_face(self):
        """한글이 들어간 글자는 트루타입 글꼴(face)을 지정해야 깨지지 않는다."""
        g.write_all()
        for f in os.listdir(g.OUT):
            if not f.endswith(".kicad_sch"):
                continue
            for line in open(os.path.join(g.OUT, f), encoding="utf-8").read().split("(text ")[1:]:
                head = line.split("(uuid")[0]
                if g.has_hangul(head.split('" (at')[0]):
                    self.assertIn(f'(face "{g.HANGUL_FACE}")', head, f)

    @unittest.skipUnless(shutil.which("kicad-cli"), "kicad-cli not installed")
    def test_drawn_netlist_matches_intent(self):
        g.write_all()
        with tempfile.TemporaryDirectory() as d:
            net = os.path.join(d, "hmt500.net")
            subprocess.run(["kicad-cli", "sch", "export", "netlist", "-o", net,
                            os.path.join(g.OUT, g.PROJECT + ".kicad_sch")], check=True, capture_output=True)
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


class PcbPlacementTest(unittest.TestCase):
    """place_pcb.py 결과(placement.json) — pcbnew 없이 검사."""

    @classmethod
    def setUpClass(cls):
        import json
        cls.d = json.load(open(os.path.join(ROOT, "hardware", "kicad", g.PROJECT, "placement.json"), encoding="utf-8"))
        cls.parts = {p["ref"]: p for p in cls.d["parts"]}

    def test_all_parts_placed(self):
        want = {r for S in g.SHEETS for r in S.order if not r.startswith("#")}
        self.assertEqual(set(self.parts), want)
        self.assertEqual(self.d["meta"]["unplaced"], [])

    def test_no_courtyard_overlap(self):
        ps = list(self.parts.values())
        for i, a in enumerate(ps):
            for b in ps[i + 1:]:
                if a["side"] != b["side"]:
                    continue
                A, B = a["crt"], b["crt"]
                hit = A[0] < B[2] and B[0] < A[2] and A[1] < B[3] and B[1] < A[3]
                self.assertFalse(hit, (a["ref"], b["ref"]))

    def test_heights_fit_bore(self):
        for p in self.parts.values():
            if p["ref"] != "J5":          # 샤시 접점: 하우징 내면까지 닿는지는 조립 검토 항목
                self.assertLessEqual(p["h"], p["h_allow"], p["ref"])

    def test_harness_plug_paths_clear_on_top(self):
        for p in self.parts.values():
            if p["side"] != "T" or p["ref"] in ("J3", "J1"):
                continue
            x0, y0, x1, y1 = p["crt"]
            for (a, b, w, hmax) in self.d["meta"]["harness_bands_top"]:
                if x0 < b and x1 > a and y0 < w and y1 > -w:
                    self.assertIsNotNone(hmax, p["ref"])
                    self.assertLessEqual(p["h"], hmax, p["ref"])

    def test_pad_nets_match_schematic(self):
        nets = g.intended_nets()
        for net, nodes in nets.items():
            for ref, pin in nodes:
                got = {q["net"] for q in self.parts[ref]["pads"] if q["n"] == pin}
                self.assertEqual(got, {net}, (ref, pin))


if __name__ == "__main__":
    unittest.main()
