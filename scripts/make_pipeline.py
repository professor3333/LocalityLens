"""Generate docs/assets/pipeline.svg.

Usage: python scripts/make_pipeline.py docs/assets/pipeline.svg [STAGE=STATUS,...]
STAGE is a 0-based index; STATUS is built | partial | planned, e.g. "1=partial".
"""

import sys

W, H = 1280, 330
AMBER, TEAL, PINK, INK, GREY, LAV = "#F4B860", "#5FD3B5", "#F28DB2", "#E9F4F0", "#8A9A95", "#B9A6FF"
mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
sans = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
# (title, line1, line2, status, actor)  status: built|partial|planned ; actor: code|llm
STAGES = [
    ("Locality text", "verbatim label,", "kept immutable", "built", "code"),
    ("Extraction", "LLM or rules", "→ exact quotes", "built", "llm"),
    ("Validation", "quotes → spans in", "the original text", "built", "code"),
    ("Retrieval", "GNIS candidates", "with evidence", "built", "code"),
    ("Disambiguation", "optional second", "LLM call", "planned", "llm"),
    ("Geometry", "point-radius +", "cited uncertainty", "built", "code"),
    ("Review & export", "curator decision", "→ Darwin Core", "built", "code"),
]
if len(sys.argv) > 2:
    for item in sys.argv[2].split(","):
        i, st = item.split("=")
        t = list(STAGES[int(i)])
        t[3] = st
        STAGES[int(i)] = tuple(t)
BW, BH, GAP, X0, Y0 = 156, 108, 22, 28, 92
out = []
for i, (title, l1, l2, status, actor) in enumerate(STAGES):
    x = X0 + i * (BW + GAP)
    if status == "built":
        box = f'<rect x="{x}" y="{Y0}" width="{BW}" height="{BH}" rx="14" fill="#14463E" stroke="{TEAL}" stroke-width="2"/>'
        tc, sc, num_fill, num_text = "#FFFFFF", "#BFE3D8", TEAL, "#0B2422"
    elif status == "partial":
        box = f'<rect x="{x}" y="{Y0}" width="{BW}" height="{BH}" rx="14" fill="#14463E" stroke="{AMBER}" stroke-width="2" stroke-dasharray="7 4"/>'
        tc, sc, num_fill, num_text = "#FFFFFF", "#E6D3B0", AMBER, "#0B2422"
    else:
        box = f'<rect x="{x}" y="{Y0}" width="{BW}" height="{BH}" rx="14" fill="#0B2422" fill-opacity="0.55" stroke="{GREY}" stroke-width="1.5" stroke-dasharray="4 5"/>'
        tc, sc, num_fill, num_text = "#C9D6D2", "#8FA6A0", "#2A4A44", "#C9D6D2"
    cx = x + BW / 2
    out.append(box)
    out.append(
        f'<circle cx="{x + 22}" cy="{Y0 + 22}" r="11" fill="{num_fill}"/><text x="{x + 22}" y="{Y0 + 26.5}" text-anchor="middle" font-family="{sans}" font-size="12" font-weight="700" fill="{num_text}">{i + 1}</text>'
    )
    out.append(
        f'<text x="{cx}" y="{Y0 + 56}" text-anchor="middle" font-family="{sans}" font-size="16" font-weight="700" fill="{tc}">{title.replace("&", "&amp;")}</text>'
    )
    out.append(
        f'<text x="{cx}" y="{Y0 + 78}" text-anchor="middle" font-family="{sans}" font-size="12.5" fill="{sc}">{l1}</text>'
    )
    out.append(
        f'<text x="{cx}" y="{Y0 + 95}" text-anchor="middle" font-family="{sans}" font-size="12.5" fill="{sc}">{l2}</text>'
    )
    if i < len(STAGES) - 1:
        ax = x + BW + 3
        out.append(
            f'<line x1="{ax}" y1="{Y0 + BH / 2}" x2="{ax + GAP - 8}" y2="{Y0 + BH / 2}" stroke="#7FB8A8" stroke-width="2" marker-end="url(#a)"/>'
        )
    # actor lane
    col = LAV if actor == "llm" else TEAL
    out.append(
        f'<rect x="{x}" y="{Y0 + BH + 14}" width="{BW}" height="6" rx="3" fill="{col}" fill-opacity="{0.9 if actor == "llm" else 0.55}"/>'
    )
legend_y = 290
legend = f'''
<g font-family="{sans}" font-size="13" fill="#A9C9BF">
  <rect x="28" y="{legend_y - 11}" width="26" height="14" rx="4" fill="#14463E" stroke="{TEAL}" stroke-width="2"/><text x="62" y="{legend_y}">built</text>
  <rect x="112" y="{legend_y - 11}" width="26" height="14" rx="4" fill="#14463E" stroke="{AMBER}" stroke-width="2" stroke-dasharray="5 3"/><text x="146" y="{legend_y}">partly built</text>
  <rect x="240" y="{legend_y - 11}" width="26" height="14" rx="4" fill="none" stroke="{GREY}" stroke-width="1.5" stroke-dasharray="3 3"/><text x="274" y="{legend_y}">planned</text>
  <rect x="420" y="{legend_y - 7}" width="26" height="6" rx="3" fill="{LAV}" fill-opacity="0.9"/><text x="454" y="{legend_y}">language model reads text</text>
  <rect x="660" y="{legend_y - 7}" width="26" height="6" rx="3" fill="{TEAL}" fill-opacity="0.55"/><text x="694" y="{legend_y}">deterministic, tested code</text>
</g>
<text x="{W - 28}" y="{legend_y}" text-anchor="end" font-family="{mono}" font-size="12.5" fill="{AMBER}">the model never outputs coordinates</text>'''
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">LocalityLens pipeline</title>
  <desc id="d">Seven stages: locality text, extraction, validation, retrieval, disambiguation, geometry, and review and export. Each is marked built, partly built, or planned, and each is labelled as language-model or deterministic-code work.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0B2422"/><stop offset="1" stop-color="#123F37"/>
    </linearGradient>
    <marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7FB8A8"/></marker>
  </defs>
  <rect width="{W}" height="{H}" rx="20" fill="url(#bg)"/>
  <text x="28" y="50" font-family="{sans}" font-size="13.5" font-weight="600" letter-spacing="2.6" fill="{TEAL}">HOW A RECORD MOVES THROUGH LOCALITYLENS</text>
  {"".join(out)}
  {legend}
</svg>
'''
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write(svg)
