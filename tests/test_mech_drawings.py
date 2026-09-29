"""기구 도면 생성 점검: SVG가 올바른 XML이고, 조립 치수가 설치 호환 치수를 지키는지."""

import os
import sys
import math
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

    def test_pcb_fits(self):
        """Rev C: 긴 PCB 1장이 보어 안에 들어가고 부품 높이 여유가 있는지."""
        Pc, Hh, R = P.PCB, P.PCB_HOLDER, P.PCB_RING
        secs = Pc["sections"]
        self.assertEqual(secs[0][0], Pc["x"][0])
        self.assertEqual(secs[-1][1], Pc["x"][1])
        for (a0, a1, _), (b0, _, _) in zip(secs, secs[1:]):
            self.assertEqual(a1, b0)
        for x0, x1, w in secs:
            # 구간을 둘러싼 가장 좁은 보어
            bores = []
            if x0 < P.BODY["cbore"]["x"][1]:
                bores.append(P.BODY["cbore"]["d"])
            if x1 > P.ENDCAP["cbore"]["x"][0]:
                bores.append(P.ENDCAP["cbore"]["d"])
            if x1 > P.BODY["cbore"]["x"][1] and x0 < P.ENDCAP["cbore"]["x"][0]:
                bores.append(P.HOUSING["id"])
            bore = min(bores)
            edge = math.sqrt((bore / 2) ** 2 - (w / 2) ** 2) - Pc["t"] / 2
            self.assertGreater(edge, 5.0, (x0, x1, w, bore))
        # 앞 끝은 홀더 홈 안, 뒤 끝은 커넥터 안쪽 나사부와 떨어짐
        self.assertTrue(Hh["slot_x"][0] <= Pc["x"][0] < Hh["slot_x"][1])
        self.assertLess(Pc["x"][1], P.CONNECTOR["inner"]["x"][0])
        # 홀더는 바디 카운터보어 안, 홀더 가로 나사는 PCB 구멍과 일치
        self.assertLess(Hh["d"], P.BODY["cbore"]["d"])
        self.assertLess(Hh["x"][1], P.BODY["cbore"]["x"][1])
        self.assertEqual(sorted(Pc["holes"]), sorted((Hh["cross"]["x"], y) for y in Hh["cross"]["y"]))
        self.assertEqual(Hh["screw_pcd"], P.BODY["holder_taps"]["pcd"])
        # 지지링: 하우징 Ø27 구간 안, PCB 넓은 구간이 링 홈에 물림
        self.assertLess(R["od"], P.HOUSING["thread_minor"])
        wide = [s for s in secs if s[0] <= R["x"][0] and R["x"][1] <= s[1]][0]
        self.assertTrue(R["id"] / 2 < wide[2] / 2 < R["slot_y"])
        # 피드스루 핀은 홀더 구멍 안에서 끝남 (PCB 앞 끝과 겹치지 않음)
        self.assertTrue(Hh["x"][0] < P.HEADER["pin_rear"] < Pc["x"][0])

    def test_sensor_connector_fits(self):
        """Rev E: HTX99R 센서 커넥터(M10×0.75 ×2)·센서 프로브·보호캡·피드스루 끼워맞춤."""
        B, C, S, SP, O, Hd = P.BODY, P.CAP, P.SENSOR_CONN, P.SENSOR_PROBE, P.CONN_ORING, P.HEADER
        x = lambda y: S["x0"] - y                                    # noqa: E731
        # 플랜지: Ø11.2 자리에 앉고 뒷면이 턱에 닿음, 앞면 = 바디 앞면
        self.assertGreater(B["conn_cbore"]["d"], S["flange_d"])
        self.assertAlmostEqual(x(S["flange_y"][0]), B["conn_cbore"]["x"][1])
        self.assertAlmostEqual(x(S["flange_y"][1]), B["x_front"])
        # O링 홈 구간은 Ø10 H8 밀봉면 안, 아래 나사 구간은 M10×0.75 암나사 안
        g0, g1 = sorted(x(y) for y in S["oring_groove"]["y"])
        self.assertTrue(B["conn_land"]["x"][0] <= g0 and g1 <= B["conn_land"]["x"][1] + 1e-9)
        self.assertEqual(B["conn_land"]["d"], S["body_d"])
        t0, t1 = sorted(x(y) for y in S["thread_lower"]["y"])
        self.assertTrue(B["conn_thread"]["x"][0] <= t0 and t1 <= B["conn_thread"]["x"][1])
        self.assertEqual(B["conn_thread"]["d_major"], S["body_d"])
        # 핀 끝은 배선 통로 안, 통로 뒤에 피드스루 (뒤에서 삽입: 통로 < 피드스루 = 턱)
        self.assertTrue(B["channel"]["x"][0] < x(S["pin_y"]) < B["channel"]["x"][1])
        self.assertEqual(B["channel"]["x"][1], B["seat"]["x"][0])
        self.assertLess(B["channel"]["d"], Hd["d"])
        self.assertEqual(B["seat"]["x"][1], B["cbore"]["x"][0])                 # 용접부는 Ø22 카운터보어 바닥
        self.assertEqual(Hd["x"], B["seat"]["x"])
        # O링 압축률 15~30 %, 늘림 < 5 %
        sq = 1 - (S["body_d"] - S["oring_groove"]["d"]) / 2 / O["cs"]
        self.assertTrue(0.15 <= sq <= 0.30, sq)
        self.assertLess(S["oring_groove"]["d"] / O["id"] - 1, 0.05)
        # 보호캡: 커넥터 위 나사 구간에 체결, 뒷면 = 바디 앞면
        u0, u1 = sorted(x(y) for y in S["thread_upper"]["y"])
        self.assertAlmostEqual(C["thread_x"][0], u0)
        self.assertLessEqual(C["thread_x"][1], u1 + 1e-9)
        self.assertAlmostEqual(C["x_rear"], B["x_front"])
        self.assertGreater(C["relief"]["d"], S["body_d"])
        # 센서 프로브: 플러그가 소켓 면에 닿고, 핀은 소켓 깊이 안, 기판·플러그는 센서실 안
        self.assertAlmostEqual(SP["plug"]["x"][1], x(S["socket_face_y"]))
        self.assertLessEqual(SP["pins"]["x"][1] - SP["pins"]["x"][0], S["sock_depth"])
        self.assertGreater(SP["board"]["x"][0], C["x_tip"] + C["tip_wall"])
        self.assertLess(SP["board"]["w"], C["bore"])
        self.assertLess(SP["plug"]["d"], C["bore"])
        # 튜브가 G1/2 설치 구멍(골지름)을 통과, 캡은 EE364와 같은 Ø12
        self.assertLess(B["tube"]["d"], B["gthread"]["d_minor"])
        self.assertEqual(C["od"], 12.0)

    def test_svg_valid(self):
        for fn in (D.sheet_assembly, D.sheet_body, D.sheet_small, D.sheet_pcb):
            with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
                f.write(fn().svg())
            xml.dom.minidom.parse(f.name)
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
