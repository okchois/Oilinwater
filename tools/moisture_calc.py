"""오일 내 수분 환산 참조 구현 (water activity <-> ppm).

용해도 모델:  log10(Ws[ppm]) = A + B / T[K]
  ppm = aw * Ws(T)          (aw = 0..1, %RS = aw * 100)

계수 A, B 는 오일 종류·열화 상태에 따라 다르므로 제품에서는
사용자가 설정할 수 있어야 한다. 아래 값은 문헌 기반의 대표값이다.
"""

import argparse
import math

# (A, B) 대표 계수. 실제 적용 전 대상 오일로 KF 적정 검증 필요.
OILS = {
    # 광유계 변압기유 (Vaisala/문헌에서 널리 쓰이는 값: log S = 7.0895 - 1567/T)
    "mineral_transformer": (7.0895, -1567.0),
}


def saturation_ppm(temp_c: float, a: float, b: float) -> float:
    """해당 온도에서의 포화 수분량 [ppm, mg/kg]."""
    return 10 ** (a + b / (temp_c + 273.15))


def aw_to_ppm(aw: float, temp_c: float, a: float, b: float) -> float:
    return aw * saturation_ppm(temp_c, a, b)


def ppm_to_aw(ppm: float, temp_c: float, a: float, b: float) -> float:
    return ppm / saturation_ppm(temp_c, a, b)


def fit_coefficients(points):
    """(온도[°C], 포화 ppm) 쌍 2개 이상으로 A, B 를 최소제곱 산출."""
    xs = [1.0 / (t + 273.15) for t, _ in points]
    ys = [math.log10(s) for _, s in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--oil", default="mineral_transformer", choices=OILS)
    p.add_argument("--temp", type=float, required=True, help="오일 온도 [°C]")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--aw", type=float, help="수분 활동도 0..1")
    g.add_argument("--ppm", type=float, help="수분 함량 [ppm]")
    args = p.parse_args()

    a, b = OILS[args.oil]
    ws = saturation_ppm(args.temp, a, b)
    if args.aw is not None:
        print(f"T={args.temp:.1f}°C  Ws={ws:.1f} ppm  aw={args.aw:.3f} -> {aw_to_ppm(args.aw, args.temp, a, b):.1f} ppm")
    else:
        print(f"T={args.temp:.1f}°C  Ws={ws:.1f} ppm  {args.ppm:.1f} ppm -> aw={ppm_to_aw(args.ppm, args.temp, a, b):.3f}")


if __name__ == "__main__":
    main()
