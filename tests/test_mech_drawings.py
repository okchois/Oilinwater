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
        # Rev H: E+E EE364와 부위별로 같은 외형 (원문 데이터시트 v1.13)
        self.assertAlmostEqual(P.BODY["gthread"]["x"][0] - P.CAP["x_tip"], 34.0)   # 노출 프로브 34 (캡 37.5 중 3.5가 G½ 안)
        self.assertEqual(P.CAP["od"], 12.0)
        self.assertAlmostEqual(P.BODY["gthread"]["x"][0], -14.0)                     # 나사 14 (씰면까지)
        self.assertEqual(P.BODY["hexa"]["af"], 27.0)
        self.assertAlmostEqual(P.BODY["hexa"]["x"][1] - P.BODY["hexa"]["x"][0], 10.0)
        self.assertEqual(P.HOUSING["od"], 30.0)
        self.assertEqual(P.BODY["collar"]["d"], 30.0)
        self.assertEqual(P.ENDCAP["flange"]["d"], 30.0)
        self.assertAlmostEqual(P.ENDCAP["flange"]["x"][1], 77.0)                    # 씰면 ~ 하우징(엔드캡) 끝 77
        self.assertAlmostEqual(P.END_X - P.ENDCAP["flange"]["x"][1], 15.0)          # M12 15
        self.assertAlmostEqual(P.OVERALL, 140.0)
        # 하우징 벽: 나사 바깥 ≥ 2, O링 자리 ≥ 1.5, 가운데 ≥ 2.5
        H = P.HOUSING
        self.assertGreaterEqual((H["od"] - H["thread_d"]) / 2, 2.0)
        self.assertGreaterEqual((H["od"] - H["seal_bore"]) / 2, 1.5)
        self.assertGreaterEqual((H["od"] - H["id"]) / 2, 2.5)
        # O링 홈 바닥과 바디·엔드캡 카운터보어 사이 벽 ≥ 1.2
        for part in (P.BODY, P.ENDCAP):
            self.assertGreaterEqual((P.ORING["groove_d"] - part["cbore"]["d"]) / 2, 1.2)
        # 지지링은 하우징 나사 골지름을 지나감
        self.assertLess(P.PCB_RING["od"], H["thread_minor"] - 0.3)

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
                bores.append(min(P.HOUSING["id"], P.HOUSING["thread_minor"]))
            bore = min(bores)
            edge = math.sqrt((bore / 2) ** 2 - (w / 2) ** 2) - Pc["t"] / 2
            # Rev H: 하우징 나사 골 Ø24.9에서 폭 23 가장자리 여유 3.9 (실제 부품 높이는 placement.json h_allow 로 검사)
            self.assertGreater(edge, 3.9, (x0, x1, w, bore))
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

    def test_sensor_connector_fits(self):
        """Rev F: HTX99R 센서 커넥터·센서 프로브·두텍 필터 캡(390000-001100), 피드스루 없는 관통 통로."""
        B, C, S, SP, O = P.BODY, P.CAP, P.SENSOR_CONN, P.SENSOR_PROBE, P.CONN_ORING
        x = lambda y: S["x0"] - y                                    # noqa: E731
        # 플랜지: Ø11.2 자리에 앉고 뒷면이 턱에 닿음, 앞면 = 바디 앞면
        self.assertGreater(B["conn_cbore"]["d"], S["flange_d"])
        self.assertAlmostEqual(x(S["flange_y"][0]), B["conn_cbore"]["x"][1])
        self.assertAlmostEqual(x(S["flange_y"][1]), B["x_front"])
        # O링 홈 구간은 Ø10 H8 밀봉면 안, 아래 나사 구간은 M10 암나사 안
        g0, g1 = sorted(x(y) for y in S["oring_groove"]["y"])
        self.assertTrue(B["conn_land"]["x"][0] <= g0 and g1 <= B["conn_land"]["x"][1] + 1e-9)
        self.assertEqual(B["conn_land"]["d"], S["body_d"])
        t0, t1 = sorted(x(y) for y in S["thread_lower"]["y"])
        self.assertTrue(B["conn_thread"]["x"][0] <= t0 and t1 <= B["conn_thread"]["x"][1])
        self.assertEqual(B["conn_thread"]["d_major"], S["body_d"])
        # 관통 통로(pass-through, 포팅 없음): 커넥터 뒤 → Ø22 카운터보어까지, 핀 끝은 통로 안, 플러그(대각)가 통과
        self.assertEqual(B["channel"]["x"][0], B["conn_thread"]["x"][1])
        self.assertEqual(B["channel"]["x"][1], B["cbore"]["x"][0])
        self.assertNotIn("seat", B)
        self.assertTrue(B["channel"]["x"][0] < x(S["pin_y"]) < B["channel"]["x"][1])
        self.assertEqual(P.POTTING["x"], B["channel"]["x"])         # 통로 전 길이 에폭시 몰딩 (1차 격벽)
        self.assertEqual(P.POTTING["x"][0], S["x0"])
        pl = P.HARNESS["plug"]
        self.assertLess(math.hypot(pl["x"][1] - pl["x"][0], pl["y"][1] - pl["y"][0]), B["channel"]["d"])
        # O링 압축률 15~30 %, 늘림 < 5 %
        sq = 1 - (S["body_d"] - S["oring_groove"]["d"]) / 2 / O["cs"]
        self.assertTrue(0.15 <= sq <= 0.30, sq)
        self.assertLess(S["oring_groove"]["d"] / O["id"] - 1, 0.05)
        # 필터 캡: 암나사(8.5)가 커넥터 위 나사 구간을 덮고 규격 같음, 열린 끝 = 바디 앞면(플랜지 앞면)
        u0, u1 = sorted(x(y) for y in S["thread_upper"]["y"])
        self.assertTrue(C["thread_x"][0] <= u0 and u1 <= C["thread_x"][1])
        self.assertEqual(C["thread"], S["thread_upper"]["spec"])
        self.assertAlmostEqual(C["x_rear"], B["x_front"])
        self.assertAlmostEqual(C["x_rear"] - C["x_tip"], 32.0 + P.CAP_EXT)       # Rev H: 원 도면 32 + 연장 5.5
        self.assertLess(C["rear_relief"]["d"], B["conn_cbore"]["d"] + 2 * 0.5)
        # 센서 프로브: 플러그가 소켓 면에 닿고, 핀은 소켓 깊이 안, 기판·플러그는 Ø8 센서실 안
        self.assertAlmostEqual(SP["plug"]["x"][1], x(S["socket_face_y"]))
        self.assertLessEqual(SP["pins"]["x"][1] - SP["pins"]["x"][0], S["sock_depth"])
        self.assertGreater(SP["board"]["x"][0], C["bore_x"][0])
        self.assertLess(math.hypot(SP["board"]["w"] / 2, SP["board"]["t"] / 2), C["bore"] / 2)
        self.assertLess(SP["plug"]["d"], C["bore"])
        # 센서 소자 앞에 측면 구멍 줄이 있음
        rows = sorted({hx for hx, _ in C["holes"]})
        self.assertTrue(any(SP["board"]["x"][0] <= r <= SP["plug"]["x"][0] for r in rows))
        self.assertEqual(len(C["holes"]), 25)                    # Rev H: 5줄 × 5개 (연장부 1줄 추가)
        # 튜브가 G1/2 설치 구멍(골지름)을 통과, 캡 Ø12
        # 캡 보호 칼라: 캡 뿌리를 3 mm 이상 감싸고, 캡과 틈 0.1–0.2, HTX99R 맞변 평면(스패너)은 밖에 남음
        sl = B["cap_sleeve"]
        self.assertAlmostEqual(sl["x"][1], C["x_rear"])
        self.assertGreaterEqual(sl["x"][1] - sl["x"][0], 3.0)
        self.assertTrue(0.1 <= (sl["d"] - C["od"]) / 2 <= 0.2)
        self.assertGreaterEqual((B["gthread"]["d_minor"] - sl["d"]) / 2, 3.0)   # G½ 골지름 안 벽 두께
        self.assertAlmostEqual(sl["x"][0], B["gthread"]["x"][0])                  # Ø14 튜브 없음: 칼라가 바디 맨 앞
        S = P.SENSOR_CONN
        self.assertLess(S["x0"] - 12.0, sl["x"][0])            # 맞변 평면 시작(커넥터 y 12) 앞에서 칼라가 끝남
        self.assertEqual(C["od"], 12.0)

    def test_sensor_harness(self):
        """W-1 하네스 + J3 JST SH 헤더: 홀더를 피하고, 높이 한계 안, 전선은 홀더 Ø6 구멍 통과."""
        Pc, J, W, Hh = P.PCB, P.PCB["jst"], P.HARNESS, P.PCB_HOLDER
        self.assertGreater(J["x"][0], Hh["x"][1])                       # 홀더 뒤
        self.assertLessEqual(J["x"][1], Pc["zones"][0][3])             # 측정 구역 안
        lim = {i: row for i, row in enumerate(D.pcb_limits())}
        self.assertLess(Pc["t"] / 2 + J["h"], lim[0][5] + Pc["t"] / 2)  # 중심 높이 한계
        self.assertLess(W["plug"]["z"][1] - Pc["t"] / 2, lim[0][5])
        self.assertEqual(W["plug"]["x"][1], J["x"][0])                  # 옆 삽입: 플러그가 헤더 앞(-x)에 꽂힘
        self.assertGreater(W["plug"]["x"][0], Hh["x"][1])               # 플러그는 홀더 뒤
        zc = sum(W["plug"]["z"]) / 2
        self.assertLess(abs(zc - W["gap_z"]), 0.3)                      # 홀더 구멍 높이 = 플러그 중심 → 굽힘 없음
        # 홀더 구멍 안 전선 묶음: 피치·높이로 본 가장 먼 전선 바깥이 구멍 반지름 안
        n = len(W["pins"])
        yk = (n - 1) / 2 * W["pitch"]
        self.assertLess(math.hypot(yk, W["gap_z"]) + W["wire_d"] / 2, Hh["hole_d"] / 2)
        self.assertGreater(W["gap_z"] - W["wire_d"] / 2, Pc["t"] / 2)   # PCB 위
        self.assertEqual(n, 4)                                          # HTX99R 4핀
        # 경로 길이(커넥터 핀 → J3 플러그) + 조립 여유 ≤ 하네스 길이
        xp = P.SENSOR_CONN["x0"] - P.SENSOR_CONN["pin_y"]
        route = W["plug"]["x"][1] - xp
        self.assertLessEqual(route + 10.0, W["length"])
        # 회로도 J3 핀 = 하네스 핀
        sys.path.insert(0, os.path.join(ROOT, "hardware", "kicad"))
        import gen_hmt500 as g
        j3 = next(S.nets["J3"] for S in g.SHEETS if "J3" in S.nets)
        self.assertEqual({k: v for k, v, _ in W["pins"]}, j3)

    def test_field_harness(self):
        """W-2 + J1 JST GH 8P: 플러그가 PCB 위, 지지링 안쪽, 커넥터와 떨어짐, 높이 한계 안, 회로도 J1 핀 8개."""
        Pc, G, W, R = P.PCB, P.PCB["gh"], P.HARNESS2, P.PCB_RING
        pl = W["plug"]
        self.assertEqual(G["x"][1], pl["x"][0])                         # 플러그는 헤더 입구(+x)에 꽂힘
        self.assertLess(pl["x"][1], P.CONNECTOR["inner"]["x"][0] - 5)   # 전선 굽힘 여유
        self.assertLessEqual(pl["x"][1], Pc["x"][1])
        self.assertLess(math.hypot(pl["y"][1], pl["z"][1]), R["id"] / 2)  # 지지링 안쪽 통과
        lim = D.pcb_limits()
        self.assertLess(G["h"], lim[1][5])
        self.assertLess(math.hypot(G["y"][1], Pc["t"] / 2 + G["h"]), P.HOUSING["id"] / 2)
        route = (P.CONNECTOR["inner"]["x"][0] - pl["x"][1]) + 2 * W["wire_z"] + W["conn_pcd"]
        self.assertLessEqual(route, W["length"])                         # 체결 후 경로
        # 꽂을 때: 하우징 턴버클 시작 위치(체결 길이만큼 뒤) 뒤 끝까지 + 엔드캡을 옆으로 비켜 들 15 mm
        x_rear_pre = P.HOUSING["x"][1] + P.HOUSING["thread_len"]
        self.assertLessEqual(x_rear_pre - pl["x"][1] + 15.0, W["length"])
        sys.path.insert(0, os.path.join(ROOT, "hardware", "kicad"))
        import gen_hmt500 as g
        j1 = next(S.nets["J1"] for S in g.SHEETS if "J1" in S.nets)
        self.assertEqual(len(j1), 6)                                    # 1·7 NC (GH 고정 패드 MP는 PCB 전용)
        self.assertIn("J5", next(S for S in g.SHEETS if "J5" in S.nets).nets)

    def test_rev_i_assembly_margins(self):
        # 최대 1.76 mm PCB가 최소 홈에 들어가야 함: 이전 1.7 mm 홈은 실패.
        for support in (P.PCB_HOLDER, P.PCB_RING):
            self.assertGreaterEqual(support["slot_w"] - P.PCB["t"] - P.PCB["t_tol"], 0.10)
        sp = P.SENSOR_PROBE
        self.assertGreaterEqual(sp["board"]["x"][1] - sp["board"]["x"][0],
                                0.3 + sp["mk33"]["l"] + 0.6 + sp["pt1000"]["l"])
        e, port = P.ENDCAP, P.ENDCAP["ports"]
        slope = math.tan(math.radians(port["tilt_deg"]))
        # 공구의 입구 단면과 M12 어깨 사이 최소 간격 (명목치).
        self.assertGreaterEqual(port["r"] - port["access_d"]/2 * math.sqrt(1+slope*slope)
                                - P.CONNECTOR["body"]["d"]/2, port["access_clearance"])
        # 나사 대경까지 보수적으로 고려해도 O링 홈을 침범하면 안 됨.
        rg = port["r"] + (e["seal"]["groove_x"][1] - e["flange"]["x"][1]) * slope
        self.assertGreaterEqual(P.ORING["groove_d"]/2 - rg - 1.5*math.sqrt(1+slope*slope), .5)

    def test_svg_valid(self):
        for fn in (D.sheet_assembly, D.sheet_body, D.sheet_small, D.sheet_pcb):
            with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
                f.write(fn().svg())
            xml.dom.minidom.parse(f.name)
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
