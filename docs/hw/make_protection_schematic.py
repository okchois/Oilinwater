"""보호 회로 구성도 SVG 생성기 → docs/hw/protection-schematic.svg"""

import os

o = []
a = o.append
W, H = 1180, 900
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
  "font-family=\"'Noto Sans KR','Malgun Gothic','NanumGothic',sans-serif\">")
a('<rect width="100%" height="100%" fill="#fff"/>')
a('<style>.w{stroke:#0f172a;stroke-width:2;fill:none}.t{font-size:12px;fill:#0f172a}'
  '.s{font-size:10.5px;fill:#475569}.h{font-size:15px;font-weight:700;fill:#0f172a}'
  '.b{fill:#fff;stroke:#0f172a;stroke-width:1.6}.ic{fill:#eff6ff;stroke:#1d4ed8;stroke-width:1.8}'
  '.pin{fill:#f1f5f9;stroke:#475569;stroke-width:1.6}</style>')
a('<text x="20" y="32" font-size="20" font-weight="700" fill="#0f172a">DOTECH HMT500 — 서지·오결선 보호 회로 구성도 v0.1</text>')
a('<text x="20" y="54" class="s">초기 부품값 · 회로도 CAD 입력 전 · 오결선 요구: 임의의 두 핀 사이 ±30 V 연속 인가에 손상 없음</text>')


def line(*pts):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    a(f'<path class="w" d="{d}"/>')


def dot(x, y):
    a(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#0f172a"/>')


def res(x, y, label, sub=""):  # 수평 저항 (중심 x,y), 폭 44
    line((x - 30, y), (x - 22, y))
    a(f'<rect class="b" x="{x - 22}" y="{y - 8}" width="44" height="16"/>')
    line((x + 22, y), (x + 30, y))
    a(f'<text x="{x}" y="{y - 13}" class="t" text-anchor="middle">{label}</text>')
    if sub:
        a(f'<text x="{x}" y="{y + 24}" class="s" text-anchor="middle">{sub}</text>')


def tvs(x, y1, y2, label, sub=""):  # 수직 양방향 TVS (y1 위, y2 아래)
    m = (y1 + y2) / 2
    line((x, y1), (x, m - 16))
    line((x, m + 16), (x, y2))
    a(f'<path d="M{x - 9},{m - 16} L{x + 9},{m - 16} L{x},{m} Z" fill="#fee2e2" stroke="#b91c1c" stroke-width="1.6"/>')
    a(f'<path d="M{x - 9},{m + 16} L{x + 9},{m + 16} L{x},{m} Z" fill="#fee2e2" stroke="#b91c1c" stroke-width="1.6"/>')
    a(f'<path d="M{x - 11},{m - 3} L{x - 9},{m} L{x + 9},{m} L{x + 11},{m + 3}" stroke="#b91c1c" stroke-width="1.8" fill="none"/>')
    a(f'<text x="{x + 14}" y="{m - 2}" class="t">{label}</text>')
    if sub:
        a(f'<text x="{x + 14}" y="{m + 12}" class="s">{sub}</text>')


def cap(x, y1, y2, label):
    m = (y1 + y2) / 2
    line((x, y1), (x, m - 4))
    line((x, m + 4), (x, y2))
    line((x - 10, m - 4), (x + 10, m - 4))
    line((x - 10, m + 4), (x + 10, m + 4))
    a(f'<text x="{x + 14}" y="{m + 4}" class="t">{label}</text>')


def gnd(x, y):
    line((x, y), (x, y + 6))
    line((x - 9, y + 6), (x + 9, y + 6))
    line((x - 5, y + 10), (x + 5, y + 10))


def box(x, y, w, h, title, lines, cls="ic"):
    a(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>')
    a(f'<text x="{x + 8}" y="{y + 18}" class="t" font-weight="700">{title}</text>')
    for i, t in enumerate(lines):
        a(f'<text x="{x + 8}" y="{y + 35 + 15 * i}" class="s">{t}</text>')


def pin(x, y, label):
    a(f'<rect class="pin" x="{x - 44}" y="{y - 12}" width="88" height="24" rx="4"/>')
    a(f'<text x="{x}" y="{y + 4}" class="t" text-anchor="middle" font-weight="700">{label}</text>')


def panel(x, y, w, h, title):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="#cbd5e1" stroke-width="1.5"/>')
    a(f'<text x="{x + 14}" y="{y + 24}" class="h">{title}</text>')


# ── A. 전원 입력 ───────────────────────────────────────────
panel(15, 70, 1150, 250, "A. 전원 입력 — 역극성 / 과전압 / 서지 (±60 V 내성)")
Y, G = 150, 270
pin(75, Y, "8: V+")
pin(75, G, "6: GND")
box(140, Y - 25, 90, 150, "L1", ["공통모드", "초크", "V+·GND", "동시 통과"], cls="b")
line((119, Y), (140, Y)); line((230, Y), (270, Y))
line((119, G), (140, G)); line((230, G), (270, G))
dot(290, Y); dot(290, G)
line((270, Y), (330, Y)); line((270, G), (1080, G))
tvs(290, Y, G, "D1 SMDJ36CA", "양방향 3000 W (1단)")
res(430, Y, "R1 4.7 Ω", "펄스 정격 1 W")
line((330, Y), (400, Y)); line((460, Y), (560, Y))
dot(520, Y); dot(520, G)
tvs(520, Y, G, "D2 SMBJ33CA", "양방향 (2단)")
dot(640, Y); dot(640, G)
line((560, Y), (700, Y))
cap(640, Y, G, "C1")
a(f'<text x="600" y="{G + 18}" class="s">C1: 100 nF/100 V + 10 µF/50 V</text>')
box(700, Y - 30, 190, 95, "U1 TPS2660 eFuse", ["±60 V 내성, 역극성 차단", "OVP 29 V · UVLO 8.6 V (v0.8)", "ILIM 149 mA · FLT→MCU"])
line((795, Y + 65), (795, G)); dot(795, G)
line((890, Y), (1080, Y))
a(f'<text x="905" y="{Y - 8}" class="t" font-weight="700">VIN_P (12–33 V)</text>')
a(f'<text x="905" y="{Y + 22}" class="s">→ DAC8760 AVDD ×2, TPS2661</text>')
a(f'<text x="905" y="{Y + 38}" class="s">→ LMR36006 → 5 V → TPS7A20 → 3.3 V</text>')
a(f'<text x="905" y="{G - 8}" class="t">GND</text>')

# ── B. 아날로그 출력 (1채널) ────────────────────────────────
panel(15, 335, 700, 290, "B. 아날로그 출력 (채널당) — 전압/전류 선택, 오결선 차단")
Y = 480
box(35, Y - 55, 150, 120, "U2 DAC8760", ["AVDD = VIN_P", "VOUT / IOUT 결합", "+VSENSE 입력", "ALARM → MCU"])
box(225, Y - 35, 145, 70, "U3 TPS26611", ["오결선 시 경로 차단", "FLT → MCU"])
line((185, Y), (225, Y)); line((370, Y), (400, Y))
res(430, Y, "R2 10 Ω", "펄스 정격")
line((460, Y), (640, Y))
dot(510, Y); dot(595, Y)
tvs(510, Y, 585, "D3", "TVS3301")
cap(595, Y, 585, "")
a(f'<text x="607" y="{Y + 58}" class="s">C2 1 nF</text>')
gnd(510, 585); gnd(595, 585)
pin(670, Y, "4 / 5: OUT")
dot(610, Y)
line((610, Y), (610, Y - 70), (110, Y - 70), (110, Y - 55))
res(360, Y - 70, "R4 10 kΩ", "")
a('<text x="35" y="612" class="s">+VSENSE(R4): 출력 단자 전압을 되먹임해 R2·스위치 저항의 전압강하 보정</text>')

# ── C. RS-485 ──────────────────────────────────────────────
panel(730, 335, 435, 290, "C. RS-485 — 버스 ±70 V 내성")
A_, B_ = 425, 525
box(750, 400, 150, 150, "U4 THVD2450", ["3.3 V 전원", "버스 ±70 V 내성", "±25 V 공통모드", "IEC ESD ±12 kV", "EFT ±4 kV", "TX/RX/DE ← MCU"])
line((900, A_), (960, A_)); line((900, B_), (960, B_))
res(990, A_, "R5 2.2 Ω", "(선택)")
res(990, B_, "R6 2.2 Ω", "(선택)")
line((1020, A_), (1100, A_)); line((1020, B_), (1100, B_))
dot(1050, A_); dot(1050, B_)
tvs(1050, A_, 475, "", "")
tvs(1050, 475, B_, "", "")
dot(1050, 475)
line((1050, 475), (1010, 475)); gnd(1010, 475)
a('<text x="1062" y="470" class="s">D4·D5 SMAJ40CA</text>')
a('<text x="1062" y="484" class="s">(선택, 36 V 이상)</text>')
pin(1110, A_ - 30, "3: A (D+)")
pin(1110, B_ + 30, "2: B (D−)")
line((1100, A_), (1110, A_), (1110, A_ - 18))
line((1100, B_), (1110, B_), (1110, B_ + 18))

# ── D. 접지 ───────────────────────────────────────────────
panel(15, 640, 700, 245, "D. 회로 GND ↔ 하우징 — 평소 분리, 서지 때만 연결")
GY, HY = 700, 830
a(f'<text x="40" y="{GY + 4}" class="t" font-weight="700">회로 GND</text>')
a(f'<text x="40" y="{HY + 4}" class="t" font-weight="700">하우징 (SUS, 배관 접지)</text>')
line((120, GY), (560, GY)); line((200, HY), (560, HY))
for x_ in (260, 400, 540):
    dot(x_, GY); dot(x_, HY)
res_x = 260
line((res_x, GY), (res_x, GY + 40))
a(f'<rect class="b" x="{res_x - 8}" y="{GY + 40}" width="16" height="44"/>')
line((res_x, GY + 84), (res_x, HY))
a(f'<text x="{res_x + 14}" y="{GY + 66}" class="t">1 MΩ</text>')
cap(400, GY, HY, "4.7 nF 2 kV (Y)")
line((540, GY), (540, GY + 45))
a(f'<ellipse cx="540" cy="{(GY + HY) / 2}" rx="16" ry="20" fill="#fef9c3" stroke="#a16207" stroke-width="1.6"/>')
a(f'<text x="540" y="{(GY + HY) / 2 + 4}" class="s" text-anchor="middle">GDT</text>')
line((540, GY + 85), (540, HY))
a(f'<text x="562" y="{(GY + HY) / 2 - 4}" class="t">GDT 230 V</text>')
a(f'<text x="562" y="{(GY + HY) / 2 + 12}" class="s">선–접지 서지 때만 방전</text>')

# ── 핵심 규칙 ──────────────────────────────────────────────
panel(730, 640, 435, 245, "설계 규칙")
rules = [
    "① 외부 핀의 TVS는 모두 양방향, 동작전압 ≥ 33 V",
    "   → −30 V 오결선에서 TVS가 도통하지 않음",
    "② 1단(대용량 TVS) → 직렬 저항 → 2단(소형 TVS)",
    "   → 잔류 전압을 IC 정격 이하로",
    "③ 오결선은 IC가 차단: TPS2660 / TPS2661 / THVD2450",
    "   → 퓨즈 교체 없이 자동 복귀",
    "④ 1, 7번 핀은 PCB에서 연결하지 않음 (NC)",
    "⑤ PCB–하우징 연면·공간거리 ≥ 2 mm",
    "⑥ 모든 FLT/ALARM 신호는 MCU가 기록 → Modbus 상태",
]
for i, t in enumerate(rules):
    a(f'<text x="748" y="{690 + 20 * i}" class="t">{t}</text>')

a("</svg>")
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "protection-schematic.svg")
open(p, "w", encoding="utf-8").write("\n".join(o))
print(p)
