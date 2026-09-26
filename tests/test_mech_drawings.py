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
        self.assertEqual(P.HOUSING["od"], 32.0)
        self.assertAlmostEqual(P.OVERALL, 144.0)

    def test_fits_are_consistent(self):
        # Rev B: 나사(M28x1) + 반경 O링. 수나사·밀봉 지름이 하우징 암나사·보어와 맞는지
        for part in (P.BODY, P.ENDCAP):
            self.assertEqual(part["mthread"]["d"], P.HOUSING["thread_d"])
            self.assertEqual(part["seal"]["d"], P.HOUSING["seal_bore"])
            g0, g1 = part["seal"]["groove_x"]
            self.assertAlmostEqual(g1 - g0, P.ORING["groove_w"])
            self.assertLess(P.ORING["groove_d"], P.ORING["id"] + 2 * P.ORING["cs"])
        # O링 압축률 (반경 방향) 15~30 %
        squeeze = 1 - (P.HOUSING["seal_bore"] - P.ORING["groove_d"]) / 2 / P.ORING["cs"]
        self.assertTrue(0.10 <= squeeze <= 0.30, squeeze)
        # 나사·O링 자리가 하우징 끝과 맞물림: 바디 밀봉부 시작 = 하우징 시작, 엔드캡 밀봉부 끝 = 하우징 끝
        self.assertEqual(P.BODY["seal"]["x"][0], P.HOUSING["x"][0])
        self.assertEqual(P.ENDCAP["seal"]["x"][1], P.HOUSING["x"][1])
        # 하우징 최소 벽 두께 (밀봉 보어) ≥ 1.4 mm
        self.assertGreaterEqual((P.HOUSING["od"] - P.HOUSING["seal_bore"]) / 2, 1.4)
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
