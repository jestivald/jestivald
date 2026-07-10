#!/usr/bin/env python3
"""Generate assets/terminal.svg — animated terminal intro for the profile README.

The SVG is self-contained (CSS animations only, no scripts) and renders
inside GitHub's <img> sandbox. Run with --static to bake the final frame
(no animations) for quick visual preview.

    python3 assets/make_terminal.py            # -> assets/terminal.svg
    python3 assets/make_terminal.py --static out.svg
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------- palette --
BG      = "#1B1D24"   # graphite window
BAR     = "#20232C"   # titlebar
BORDER  = "#2A2E3A"
TEXT    = "#C9CED8"
DIM     = "#6E7480"
INDIGO  = "#6597E2"   # accent / prompt arrow / dir
RED     = "#E06C75"   # soft red host
GREEN   = "#98C379"
YELLOW  = "#E5C07B"
PURPLE  = "#8B5CF6"   # bokeh only

FONT = ("ui-monospace,'SF Mono','JetBrains Mono','Cascadia Code',"
        "Menlo,Consolas,'DejaVu Sans Mono',monospace")

W, H = 860, 372            # viewBox
WX, WY, WW, WH = 12, 10, 836, 340   # window rect
FS = 15                    # font size
X0 = 40                    # text left margin

NBSP = " "


def esc(s: str) -> str:
    """XML-escape + swap spaces for NBSP (WebKit collapses plain spaces)."""
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.replace(" ", NBSP)


def span(text, fill=TEXT, cls=None, delay=None, extra=""):
    a = f' fill="{fill}"'
    if cls:
        a += f' class="{cls}"'
    if delay is not None:
        a += f' style="animation-delay:{delay:.2f}s"'
    return f"<tspan{a}{extra}>{esc(text)}</tspan>"


def prompt_spans():
    return (span("jestivald", RED) + span(" in ", DIM)
            + span("~", INDIGO) + span(" ❯ ", INDIGO))


def typed_spans(cmd: str, start: float, per: float):
    """One tspan per character, revealed in sequence."""
    out, t = [], start
    for ch in cmd:
        out.append(span(ch, TEXT, cls="c", delay=t))
        t += per
    return "".join(out), t


STATIC = "--static" in sys.argv

lines = []          # collected <text> elements
def text_line(y, inner, cls="f", delay=0.0, size=FS, anchor=None, x=X0, op=None):
    a = f'x="{x}" y="{y}" font-size="{size}"'
    if anchor:
        a += f' text-anchor="{anchor}"'
    if op:
        a += f' opacity="{op}"'
    if not STATIC:
        a += f' class="{cls}" style="animation-delay:{delay:.2f}s"'
    lines.append(f"<text {a}>{inner}</text>")


# ---------------------------------------------------------------- session --
y, LH, GAP = 78, 28, 14

# ❯ whoami
p = prompt_spans()
typed, t_end = typed_spans("whoami", 0.90, 0.08)
text_line(y, p + typed, delay=0.40)
y += LH
text_line(y, span("student", TEXT) + span("  ·  ", DIM)
             + span("self-hosted everything", TEXT) + span("  ·  ", DIM)
             + span("doctore claude", INDIGO),
          delay=t_end + 0.35)
y += LH + GAP

# ❯ ls ~/projects
typed, t_end = typed_spans("ls ~/projects", 2.60, 0.07)
text_line(y, prompt_spans() + typed, delay=2.20)
y += LH
text_line(y, span("node-accelerator", GREEN) + span(" ★123", YELLOW)
             + span("   ", DIM) + span("server-bench", GREEN)
             + span("   ", DIM) + span("jestivald.tech", GREEN)
             + span("   ", DIM) + span(".claude", DIM),
          delay=t_end + 0.35)
y += LH + GAP

# ❯ sudo make coffee
typed, t_end = typed_spans("sudo make coffee", 4.90, 0.07)
text_line(y, prompt_spans() + typed, delay=4.50)
y += LH
text_line(y, span("Nice try.", RED), delay=t_end + 0.40)
y += LH + GAP

# final prompt + solid block cursor (non-blinking, like the site)
text_line(y, prompt_spans() + span("█", INDIGO), delay=7.60)

# footer easter egg
text_line(WY + WH - 12, span("// hack the planet", DIM), delay=8.20,
          size=11, anchor="end", x=WX + WW - 22, op="0.55")

body = "\n    ".join(lines)

css = "" if STATIC else """
    <style>
      .f{opacity:0;animation:in .25s ease-out forwards}
      .c{opacity:0;animation:in .01s steps(1) forwards}
      @keyframes in{to{opacity:1}}
      @media (prefers-reduced-motion:reduce){.f,.c{animation:none;opacity:1}}
    </style>"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img"
     aria-label="Terminal: whoami — student, self-hosted everything, doctore claude; ls ~/projects — node-accelerator, server-bench, jestivald.tech; sudo make coffee — Nice try.">
  <defs>
    <clipPath id="win"><rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="12"/></clipPath>
    <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.05"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <filter id="blur40" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="40"/>
    </filter>
    <filter id="shadow" x="-8%" y="-8%" width="116%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" stitchTiles="stitch"/>
      <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.03 0"/>
    </filter>
  </defs>{css}

  <!-- window -->
  <rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="12" fill="{BG}" filter="url(#shadow)"/>
  <g clip-path="url(#win)">
    <circle cx="700" cy="80" r="120" fill="{INDIGO}" opacity="0.08" filter="url(#blur40)"/>
    <circle cx="170" cy="310" r="100" fill="{PURPLE}" opacity="0.07" filter="url(#blur40)"/>
    <rect x="{WX}" y="{WY}" width="{WW}" height="36" fill="{BAR}"/>
    <rect x="{WX}" y="{WY + 36}" width="{WW}" height="1" fill="{BORDER}"/>
    <rect x="{WX}" y="{WY}" width="{WW}" height="90" fill="url(#glass)"/>
    <rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" filter="url(#grain)" opacity="0.5"/>
  </g>
  <rect x="{WX + 0.5}" y="{WY + 0.5}" width="{WW - 1}" height="{WH - 1}" rx="11.5"
        fill="none" stroke="{BORDER}"/>

  <!-- traffic lights + title -->
  <circle cx="34" cy="28" r="6.5" fill="#FF5F57"/>
  <circle cx="56" cy="28" r="6.5" fill="#FEBC2E"/>
  <circle cx="78" cy="28" r="6.5" fill="#28C840"/>
  <text x="{W / 2}" y="33" font-size="12" fill="{DIM}" text-anchor="middle"
        font-family="{FONT}">{esc("jestivald — zsh")}</text>

  <!-- session -->
  <g font-family="{FONT}">
    {body}
  </g>
</svg>
"""

out = Path(sys.argv[sys.argv.index("--static") + 1]) if STATIC and \
    len(sys.argv) > sys.argv.index("--static") + 1 else \
    Path(__file__).parent / "terminal.svg"
out.write_text(svg, encoding="utf-8")
print(f"wrote {out} ({len(svg)} bytes)")
