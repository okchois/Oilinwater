"""기구 구조도(측면 + 내부 투시) SVG 생성기. 치수는 설계안(mm).

python3 docs/mech/make_drawing.py  →  docs/mech/assembly.svg
"""

import os

S = 4.4           # px / mm
X0, CY = 150, 300  # 프로브 끝 x, 중심선 y

# (이름, 시작 mm, 끝 mm, 외경 mm, 색)
SEG = [
    ("보호캡", 0, 22, 12, "#e2e8f0"),
    ("프로브 튜브", 22, 34, 12, "#cbd5e1"),
    ("G½ 나사", 34, 48, 20.96, "#cbd5e1"),
    ("언더컷", 48, 50, 17, "#cbd5e1"),
    ("육각 SW27", 50, 62, 31.2, "#94a3b8"),
    ("넥", 62, 64, 24, "#cbd5e1"),
    ("하우징", 64, 124, 30, "#e2e8f0"),
    ("엔드캡", 124, 130, 30, "#cbd5e1"),
    ("커넥터", 130, 145, 12, "#94a3b8"),
]


def x(mm):
    return X0 + mm * S


def r(d):
    return d * S / 2


out = []
add = out.append
add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 720" width="1180" height="720" '
    "font-family=\"'Noto Sans KR','Malgun Gothic','NanumGothic',sans-serif\">")
add('<defs><marker id="d" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" '
    'orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="#0f172a"/></marker>'
    '<pattern id="thr" width="6" height="8" patternUnits="userSpaceOnUse">'
    '<path d="M0,8 L6,0" stroke="#64748b" stroke-width="1"/></pattern></defs>')
add('<rect width="1180" height="720" fill="#fff"/>')
add('<text x="20" y="34" font-size="20" font-weight="700" fill="#0f172a">DOTECH HMT500 오일 수분 트랜스미터 — 기구 구조 설계안</text>')
add('<text x="20" y="56" font-size="12" fill="#475569">측면 + 내부 투시 · 치수 단위 mm · 개념 설계(시제 전) · 견적용 참고 도면</text>')
# 표제란
tb = [("품명", "HMT500 오일 수분 트랜스미터"), ("도번", "HMT500-M-000"), ("Rev / 일자", "A / 2026-09-26"),
      ("단위 / 척도", "mm / NTS"), ("작성", "(주)두텍 DOTECH")]
add('<rect x="880" y="70" width="280" height="110" fill="#fff" stroke="#0f172a" stroke-width="1.5"/>')
for k, (a, b) in enumerate(tb):
    yy = 70 + 22 * k
    if k:
        add(f'<line x1="880" y1="{yy}" x2="1160" y2="{yy}" stroke="#0f172a"/>')
    add(f'<text x="888" y="{yy + 15}" font-size="11" fill="#475569">{a}</text>')
    add(f'<text x="965" y="{yy + 15}" font-size="12" font-weight="600" fill="#0f172a">{b}</text>')
add('<line x1="958" y1="70" x2="958" y2="180" stroke="#0f172a"/>')

# 중심선
add(f'<line x1="{x(-6)}" y1="{CY}" x2="{x(164)}" y2="{CY}" stroke="#94a3b8" stroke-dasharray="12 4 2 4"/>')

# 외형
for name, a, b, d, col in SEG:
    fill = "url(#thr)" if name == "G½ 나사" else col
    add(f'<rect x="{x(a):.1f}" y="{CY - r(d):.1f}" width="{(b - a) * S:.1f}" height="{2 * r(d):.1f}" '
        f'fill="{fill}" stroke="#334155" stroke-width="1.5"/>')
# 육각 모서리선
for yy in (-r(27) / 2, r(27) / 2):
    add(f'<line x1="{x(50)}" y1="{CY + yy:.1f}" x2="{x(62)}" y2="{CY + yy:.1f}" stroke="#334155"/>')

# 본디드 씰 (녹색)
add(f'<rect x="{x(50) - 2.2 * S:.1f}" y="{CY - r(28):.1f}" width="{2.2 * S:.1f}" height="{2 * r(28):.1f}" '
    'fill="#86efac" stroke="#15803d" stroke-width="1.5"/>')

# 보호캡 구멍
for cx_mm in (4, 9, 14, 19):
    for dy in (-r(12) * 0.45, r(12) * 0.45):
        add(f'<circle cx="{x(cx_mm):.1f}" cy="{CY + dy:.1f}" r="{1.3 * S:.1f}" fill="#fff" stroke="#334155"/>')
add(f'<rect x="{x(0) - 1:.1f}" y="{CY - 1.2 * S:.1f}" width="3" height="{2.4 * S:.1f}" fill="#fff" stroke="#334155"/>')

# 내부 (점선)
def ghost(a, b, d, col, label=None):
    add(f'<rect x="{x(a):.1f}" y="{CY - r(d):.1f}" width="{(b - a) * S:.1f}" height="{2 * r(d):.1f}" '
        f'fill="{col}" fill-opacity="0.55" stroke="#1e293b" stroke-dasharray="4 3"/>')

ghost(3, 15, 6.5, "#fde68a")      # MK 센서 + Pt1000 캐리어
ghost(20, 23, 10, "#e9d5ff")      # 캡 결합부(나사)
ghost(28, 46, 7, "#fca5a5")       # 압력 격벽 피드스루
ghost(46, 64, 4, "#fecaca")       # 리드선 통로
for px in (70, 96):               # PCB 2장
    ghost(px, px + 1.6, 26, "#86efac")
ghost(71.6, 96, 3, "#e2e8f0")     # 스페이서/보드간 커넥터
ghost(125, 132, 10, "#bfdbfe")    # 커넥터 인서트

# 용접/결합부
for jm in (64, 124):
    add(f'<line x1="{x(jm)}" y1="{CY - r(30) - 6}" x2="{x(jm)}" y2="{CY + r(30) + 6}" stroke="#dc2626" stroke-width="2" stroke-dasharray="3 3"/>')


# 부품 번호 풍선
def balloon(n, px, py, tx, ty):
    add(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="#0f172a"/>')
    add(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="13" fill="#fff" stroke="#0f172a" stroke-width="1.5"/>')
    add(f'<text x="{tx:.1f}" y="{ty + 4.5:.1f}" font-size="13" font-weight="700" text-anchor="middle" fill="#0f172a">{n}</text>')

balloon(1, x(12), CY - r(12), x(8), 150)
balloon(2, x(9), CY, x(0), 200)
balloon(3, x(21.5), CY - r(10), x(22), 150)
balloon(4, x(36), CY - r(7), x(36), 170)
balloon(5, x(41), CY - r(21), x(47), 130)
balloon(6, x(49), CY - r(28), x(58), 130)
balloon(7, x(56), CY - r(31.2), x(70), 150)
balloon(8, x(88), CY - r(30), x(88), 150)
balloon(9, x(71), CY - r(26), x(78), 190)
balloon(10, x(64), CY + r(30), x(64), 400)
balloon(11, x(127), CY - r(30), x(127), 150)
balloon(12, x(138), CY - r(12), x(145), 190)

# 치수선
def dim_h(a, b, y, text):
    add(f'<line x1="{x(a)}" y1="{y}" x2="{x(b)}" y2="{y}" stroke="#0f172a" marker-start="url(#d)" marker-end="url(#d)"/>')
    for m in (a, b):
        add(f'<line x1="{x(m)}" y1="{y - 8}" x2="{x(m)}" y2="{y + 4}" stroke="#94a3b8"/>')
    add(f'<text x="{(x(a) + x(b)) / 2:.1f}" y="{y - 5}" font-size="12" text-anchor="middle" fill="#0f172a">{text}</text>')

dim_h(0, 34, 420, "노출 프로브 34")
dim_h(34, 48, 450, "나사 14")
dim_h(50, 62, 420, "AF27")
dim_h(50, 130, 450, "씰면~하우징 끝 80")
dim_h(0, 145, 490, "전장 약 145")


def dim_v(mm, d, text, dx=0):
    xx = x(mm) + dx
    add(f'<line x1="{xx}" y1="{CY - r(d)}" x2="{xx}" y2="{CY + r(d)}" stroke="#0f172a" marker-start="url(#d)" marker-end="url(#d)"/>')
    add(f'<text x="{xx + 6}" y="{CY + r(d) + 16}" font-size="12" fill="#0f172a">{text}</text>')

dim_v(28, 12, "Ø12")
dim_v(110, 30, "Ø30")

# 부품표
parts = [
    "① 보호캡 — SUS316L, 측면 구멍 Ø2.6×8 + 끝단 구멍, 교체형(나사 결합), 유속별 2종",
    "② 센서 헤드 — IST MK 정전용량 소자 + Pt1000, 세라믹/폴리이미드 캐리어, 오일 노출",
    "③ 캡 결합부 — M10×1.0 나사 + 풀림 방지(록타이트 또는 코킹)",
    "④ 압력 격벽 — 유리-금속 밀봉(GTMS) 피드스루 4~6핀, 50 bar 기본 / 200 bar 고압형",
    "⑤ 프로세스 바디 — SUS316L 일체 선삭: 프로브 튜브 + G½ ISO 228-1 + 언더컷",
    "⑥ 본디드 씰 — G½용 USIT/DIN 3869 형, 금속+FKM (에스테르유: EPDM/FFKM)",
    "⑦ 육각 SW27 — 체결 토크 부위, 바디와 일체",
    "⑧ 하우징 튜브 — SUS316L Ø30×60, 두께 1.5, 레이저 마킹 라벨",
    "⑨ PCB 2장 — Ø26 원형 4층: 측정 보드(피드스루 쪽) / 전원·출력 보드",
    "⑩ 결합부 1 — 바디–하우징 레이저 용접 또는 나사+O링 (적색 점선)",
    "⑪ 엔드캡 — SUS316L, 커넥터 체결·O링 밀봉, IP67",
    "⑫ M Connect 8핀 수컷 — 패널형, PCB에 FPC/리드로 연결",
]
add('<text x="20" y="535" font-size="14" font-weight="700" fill="#0f172a">부품 구성</text>')
for i, p in enumerate(parts):
    col, row = divmod(i, 6)
    add(f'<text x="{20 + col * 580}" y="{560 + row * 22}" font-size="12" fill="#1e293b">{p}</text>')

add('<text x="20" y="705" font-size="11" fill="#64748b">점선 = 내부 부품 · 녹색 링 = 본디드 씰 · 적색 점선 = 용접/결합부 · 모든 치수는 시제품 전 설계안이며 PCB 외형·피드스루 선정 후 확정</text>')
add("</svg>")

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assembly.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(path)
