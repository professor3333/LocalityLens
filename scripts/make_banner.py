"""Generate docs/assets/banner.svg.

Usage: python scripts/make_banner.py docs/assets/banner.svg
"""

import math
import random
import sys

random.seed(7)
W, H = 1280, 340
PX, PY = 900, 228  # reference peak
L = 170  # "2 mi" in banner pixels
TX, TY = PX + L * math.sin(math.radians(45)), PY - L * math.cos(math.radians(45))


def contour(cx, cy, r, wob, n=14, phase=0.0):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (
            1
            + wob * math.sin(3 * a + phase)
            + 0.6 * wob * math.cos(5 * a + phase * 1.7)
            + random.uniform(-wob, wob) * 0.35
        )
        pts.append((cx + rr * math.cos(a) * 1.35, cy + rr * math.sin(a) * 0.78))
    # closed Catmull-Rom -> cubic Bezier
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + " Z"


contours = []
for k, r in enumerate([18, 38, 60, 84, 110, 138, 168, 200, 234, 270]):
    op = 0.30 - k * 0.022
    contours.append(
        f'<path d="{contour(PX + 6 * k, PY - 4 * k, r, 0.07 + 0.012 * k, phase=k * 0.6)}" stroke-opacity="{op:.2f}"/>'
    )
contours2 = []
for k, r in enumerate([22, 46, 72, 100]):
    contours2.append(
        f'<path d="{contour(1180, 70, r, 0.09, phase=2 + k)}" stroke-opacity="{0.16 - k * 0.03:.2f}"/>'
    )


def wedge(cx, cy, r, a0, a1):
    x0, y0 = cx + r * math.sin(math.radians(a0)), cy - r * math.cos(math.radians(a0))
    x1, y1 = cx + r * math.sin(math.radians(a1)), cy - r * math.cos(math.radians(a1))
    return f"M{cx},{cy} L{x0:.1f},{y0:.1f} A{r},{r} 0 0 1 {x1:.1f},{y1:.1f} Z"


AMBER, TEAL, PINK, BLUE, INK = "#F4B860", "#5FD3B5", "#F28DB2", "#9DB7FF", "#E9F4F0"
mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
sans = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

chip_x, chip_y, chip_w, chip_h = 64, 236, 520, 46
legend = [
    ("reference feature", AMBER),
    ("distance", TEAL),
    ("direction", PINK),
    ("admin area", BLUE),
]
lx = chip_x + 4
leg = []
for label, col in legend:
    leg.append(
        f'<circle cx="{lx + 5}" cy="306" r="5" fill="{col}"/><text x="{lx + 16}" y="310.5" font-family="{sans}" font-size="13" fill="#A9C9BF">{label}</text>'
    )
    lx += 16 + len(label) * 6.3 + 30

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
  <title id="title">LocalityLens</title>
  <desc id="desc">A label, "Larimer Co., Colo., 2 mi NE of Longs Peak summit.", with its reference feature, distance, direction and admin area highlighted, beside a topographic sketch showing a peak, a 2-mile offset to the north-east, a direction sector, and an uncertainty region instead of a single pin.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0B2422"/>
      <stop offset="0.55" stop-color="#103A34"/>
      <stop offset="1" stop-color="#16503F"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{PINK}" stop-opacity="0.38"/>
      <stop offset="0.7" stop-color="{PINK}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0B2422" stop-opacity="1"/>
      <stop offset="0.42" stop-color="#0B2422" stop-opacity="0"/>
    </linearGradient>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{TEAL}"/>
    </marker>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <g fill="none" stroke="#7FE0C4" stroke-width="1.4">
      {"".join(contours)}
      {"".join(contours2)}
    </g>
    <rect width="{W}" height="{H}" fill="url(#fade)"/>
    <!-- direction sector, offset, uncertainty -->
    <path d="{wedge(PX, PY, 250, 22.5, 67.5)}" fill="{PINK}" fill-opacity="0.07" stroke="{PINK}" stroke-opacity="0.35" stroke-dasharray="3 5"/>
    <circle cx="{TX:.1f}" cy="{TY:.1f}" r="78" fill="url(#glow)"/>
    <circle cx="{TX:.1f}" cy="{TY:.1f}" r="54" fill="none" stroke="{INK}" stroke-opacity="0.85" stroke-width="1.6" stroke-dasharray="6 6"/>
    <line x1="{PX}" y1="{PY}" x2="{TX - 4:.1f}" y2="{TY + 4:.1f}" stroke="{TEAL}" stroke-width="2.4" marker-end="url(#arrow)"/>
    <circle cx="{TX:.1f}" cy="{TY:.1f}" r="3.5" fill="{INK}"/>
    <path d="M{PX},{PY - 15} L{PX + 13},{PY + 8} L{PX - 13},{PY + 8} Z" fill="{AMBER}" stroke="#0B2422" stroke-width="1.5"/>
    <text x="{PX - 18}" y="{PY + 30}" font-family="{mono}" font-size="13" fill="{AMBER}">Longs Peak · GNIS 204979</text>
    <text x="{PX + 38}" y="{PY - 70}" font-family="{mono}" font-size="13" fill="{TEAL}" transform="rotate(-45 {PX + 38} {PY - 70})">2 mi</text>
    <text x="{PX + 188}" y="{PY - 176}" font-family="{mono}" font-size="13" fill="{PINK}">NE sector</text>
    <text x="{TX + 62:.1f}" y="{TY + 40:.1f}" font-family="{mono}" font-size="13" fill="{INK}" fill-opacity="0.85">uncertainty,</text>
    <text x="{TX + 62:.1f}" y="{TY + 57:.1f}" font-family="{mono}" font-size="13" fill="{INK}" fill-opacity="0.85">not a pin</text>
    <!-- text block -->
    <text x="64" y="74" font-family="{sans}" font-size="13.5" font-weight="600" letter-spacing="2.6" fill="{TEAL}">LLM-ASSISTED GEOREFERENCING FOR NATURAL HISTORY COLLECTIONS</text>
    <text x="62" y="140" font-family="{sans}" font-size="62" font-weight="700" letter-spacing="-1" fill="#FFFFFF">Locality<tspan fill="{AMBER}">Lens</tspan></text>
    <text x="64" y="180" font-family="{sans}" font-size="21" fill="#CFE7DF">Turn historical specimen descriptions into</text>
    <text x="64" y="208" font-family="{sans}" font-size="21" fill="#CFE7DF">reviewable, uncertainty-aware geographic records.</text>
    <rect x="{chip_x}" y="{chip_y}" width="{chip_w}" height="{chip_h}" rx="10" fill="#071A18" fill-opacity="0.75" stroke="#2C6B5C"/>
    <text x="{chip_x + 18}" y="{chip_y + 29}" font-family="{mono}" font-size="16" fill="#8FB3A8"><tspan fill="{BLUE}">Larimer Co., Colo.</tspan>, <tspan fill="{TEAL}" font-weight="700">2 mi</tspan> <tspan fill="{PINK}" font-weight="700">NE</tspan> of <tspan fill="{AMBER}" font-weight="700">Longs Peak</tspan> summit.</text>
    {"".join(leg)}
  </g>
</svg>
'''
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write(svg)
