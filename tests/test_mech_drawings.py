"""기구 도면 생성 점검: SVG가 올바른 XML이고, 조립 치수가 설치 호환 치수를 지키는지."""

import os
import sys
import tempfile
import unittest
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "hardware", "mech"))

import hmt500_drawings as D  # noqa: E402
import hmt500_params as P  # noqa: E402


class MechTest(unittest.TestCase):
    def test_install_dimensions(self):
        self.assertAlmostEqual(P.BODY["gthread"]["x"][0] - P.CAP["x_tip"], 34.0)   # 노출 프로브
        self.assertAlmostEqual(P.BODY["gthread"]["x"][0], -14.0)                     # 나사 14 (씰면까지)
        self.assertEqual(P.BODY["hexa"]["af"], 27.0)
        self.assertEqual(P.HOUSING["od"], 30.0)

    def test_fits_are_consistent(self):
        self.assertEqual(P.BODY["wspigot"]["d"], P.HOUSING["id"])
        self.assertEqual(P.ENDCAP["spigot"]["d"], P.HOUSING["id"])
        self.assertEqual(P.HOUSING["x"][0], P.BODY["collar"]["x"][1])
        self.assertEqual(P.HOUSING["x"][1], P.ENDCAP["flange"]["x"][0])

    def test_svg_valid(self):
        for fn in (D.sheet_assembly, D.sheet_body, D.sheet_small):
            with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
                f.write(fn().svg())
            xml.dom.minidom.parse(f.name)
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
