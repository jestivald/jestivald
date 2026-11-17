#!/usr/bin/env python3
"""Generate assets/terminal.svg — animated terminal intro for the profile README.

The SVG is self-contained (CSS animations only, no scripts) and renders
inside GitHub's <img> sandbox. Run with --static to bake the final frame
(no animations) for quick visual preview.

    python3 assets/make_terminal.py            # -> assets/terminal.svg
    python3 assets/make_terminal.py --static out.svg

The look follows jestivald.tech: matte warm graphite, fine grain, a muted
sage accent. The session mirrors the terminal window on the homepage.
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------- palette --
BG_TOP  = "#1C1C19"   # window, top of the gradient
BG_END  = "#131311"   # window, bottom
BAR     = "#1A1A17"   # titlebar
BORDER  = "#45443D"
LINE    = "#2E2D29"   # hairline under the titlebar
TEXT    = "#F1F0EB"
SOFT    = "#B9B7B0"   # command output
DIM     = "#8B897E"   # separators, title, footer
DOT     = "#3B3A34"   # window buttons
SAGE    = "#ACC9B4"   # accent / prompt arrow / cursor
SAND    = "#D8C9A8"   # directories, star

FONT = ("ui-monospace,'SF Mono','JetBrains Mono','Cascadia Code',"
        "Menlo,Consolas,'DejaVu Sans Mono',monospace")

STARS = 150                # node-accelerator, snapshot of 2026-11-17

W, H = 860, 400            # viewBox
WX, WY, WW, WH = 12, 10, 836, 366   # window rect
FS = 15                    # font size
X0 = 40                    # text left margin

NBSP = "\u00a0"


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
    return span("❯ ", SAGE)


def typed_spans(cmd: str, start: float, per: float):
    """One tspan per character, revealed in sequence."""
    out, t = [], start
    for ch in cmd:
        out.append(span(ch, TEXT, cls="c", delay=t))
        t += per
    return "".join(out), t


def dirs(*names):
    """`ls` output: directory names separated by three spaces."""
    return span("   ", DIM).join(names)


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
y, LH, GAP = 80, 28, 14
INDENT = X0 + 18           # output lines sit under the command text

# ❯ whoami
typed, t_end = typed_spans("whoami", 0.90, 0.08)
text_line(y, prompt_spans() + typed, delay=0.40)
y += LH
text_line(y, span("student", SOFT) + span("  ·  ", DIM)
             + span("self-hosted everything", SOFT) + span("  ·  ", DIM)
             + span("doctore claude", SAGE),
          delay=t_end + 0.35, x=INDENT)
y += LH + GAP

# ❯ ls ~/work
typed, t_end = typed_spans("ls ~/work", 2.50, 0.07)
text_line(y, prompt_spans() + typed, delay=2.10)
y += LH
text_line(y, dirs(span("node-accelerator/", SAND) + span(f" ★{STARS}", SAGE),
                  span("server-bench/", SAND), span("vneplena/", SAND),
                  span("monitoring/", SAND)),
          delay=t_end + 0.35, x=INDENT)
y += LH
text_line(y, dirs(span("infra-billing/", SAND), span("deeeway/", SAND),
                  span("home-win-mcp/", SAND), span(".claude/", DIM)),
          delay=t_end + 0.50, x=INDENT)
y += LH + GAP

# ❯ sudo make coffee
typed, t_end = typed_spans("sudo make coffee", 4.80, 0.07)
text_line(y, prompt_spans() + typed, delay=4.40)
y += LH
text_line(y, span("Nice try.", SOFT), delay=t_end + 0.40, x=INDENT)
y += LH + GAP

# final prompt + solid block cursor (non-blinking)
text_line(y, prompt_spans() + span("█", SAGE), delay=7.50)

# footer easter egg
text_line(WY + WH - 14, span("// hack the planet", DIM), delay=8.10,
          size=11, anchor="end", x=WX + WW - 22, op="0.7")

body = "\n    ".join(lines)

# Typed characters use step-start, not steps(1): with an end jump the final value depends on
# (delay + duration) - delay >= duration, and for most delays that float subtraction comes out a
# hair short, so Chrome leaves the character at opacity 0 forever.
css = "" if STATIC else """
    <style>
      .f{opacity:0;animation:in .25s ease-out forwards}
      .c{opacity:0;animation:in .01s step-start forwards}
      @keyframes in{to{opacity:1}}
      @media (prefers-reduced-motion:reduce){.f,.c{animation:none;opacity:1}}
    </style>"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img"
     aria-label="Terminal: whoami — student, self-hosted everything, doctore claude; ls ~/work — node-accelerator, server-bench, vneplena, monitoring, infra-billing, deeeway, home-win-mcp; sudo make coffee — Nice try.">
  <defs>
    <clipPath id="win"><rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="14"/></clipPath>
    <linearGradient id="body" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG_TOP}"/>
      <stop offset="0.62" stop-color="{BG_END}"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.045"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <filter id="blur40" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="44"/>
    </filter>
    <filter id="shadow" x="-8%" y="-8%" width="116%" height="124%">
      <feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" stitchTiles="stitch"/>
      <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.035 0"/>
    </filter>
  </defs>{css}

  <!-- window -->
  <rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="14" fill="url(#body)" filter="url(#shadow)"/>
  <g clip-path="url(#win)">
    <circle cx="700" cy="90" r="130" fill="{SAGE}" opacity="0.09" filter="url(#blur40)"/>
    <circle cx="150" cy="330" r="110" fill="#EEE1C6" opacity="0.05" filter="url(#blur40)"/>
    <rect x="{WX}" y="{WY}" width="{WW}" height="38" fill="{BAR}"/>
    <rect x="{WX}" y="{WY + 38}" width="{WW}" height="1" fill="{LINE}"/>
    <rect x="{WX}" y="{WY}" width="{WW}" height="90" fill="url(#glass)"/>
    <rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" filter="url(#grain)" opacity="0.55"/>
  </g>
  <rect x="{WX + 0.5}" y="{WY + 0.5}" width="{WW - 1}" height="{WH - 1}" rx="13.5"
        fill="none" stroke="{BORDER}"/>

  <!-- window buttons + title -->
  <circle cx="34" cy="29" r="5" fill="{DOT}"/>
  <circle cx="51" cy="29" r="5" fill="{DOT}"/>
  <circle cx="68" cy="29" r="5" fill="{DOT}"/>
  <text x="{W / 2}" y="33" font-size="12" fill="{DIM}" text-anchor="middle"
        font-family="{FONT}">{esc("jestivald@workspace: ~")}</text>
  <text x="{WX + WW - 20}" y="33" font-size="11" fill="{DIM}" text-anchor="end"
        font-family="{FONT}">zsh</text>

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
