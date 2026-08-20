#!/usr/bin/env python3
"""
Regenerate assets/banner-dark.svg, assets/banner-light.svg and assets/rule.svg.

Layout
------
Text block on the left (name, role, captions). Everything to its right, out
to the frame edge, is a scattered field of tech-stack icons - there is no
SIGNAL panel any more; the whole right two-thirds of the banner belongs to
the icons.

Motion
------
Each icon just floats: a slow vertical drift plus a few degrees of rotation,
looped forever, on one of three shared keyframe shapes (floatA/B/C) so eleven
icons don't need eleven bespoke keyframe blocks. Duration and delay are set
per icon inline so the drift reads as scattered rather than synchronized.

The section rules under each `##` heading in the README are a separate,
much quieter animation: a travelling ripple across a thin strip, built by
build_rule() below. They have nothing to do with the banner's icon field.

Constraints
-----------
GitHub serves these through an img element: CSS animations run, scripts do not,
so there is no SMIL and no JS here.

Every animated element rests at its FINAL state and animates in from a keyframed
start with fill-mode backwards. A renderer that declines to run the animations
then shows the composed banner rather than an empty frame.

The icon float loops are the exception, and deliberately so: they are
decorative, never occlude the text, and their own frame zero (the
untranslated, unrotated position) already looks correct at rest.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1200, 320

# The floating icon field: a scattered set of tech-stack marks filling the
# right two-thirds of the frame, each drifting on one of three shared
# keyframe shapes (see ICON_FLOATS) with its own duration/delay so the set
# doesn't move in lockstep.
#
# (icon key, x, y, size in px, base opacity, float variant 0-2, duration s, delay s)
ICONS = [
    ("react",      545,  55, 32, 0.85, 0, 4.2, 0.0),
    ("tensorflow", 655, 100, 26, 0.80, 1, 4.8, 0.5),
    ("sparkle",    570, 180, 24, 0.85, 2, 3.7, 1.2),
    ("docker",     705,  50, 30, 0.85, 2, 3.9, 1.0),
    ("terminal",   825,  90, 30, 0.75, 0, 4.4, 0.6),
    ("gcp",        955,  55, 26, 0.80, 1, 4.1, 1.4),
    ("python",     625, 255, 32, 0.90, 0, 4.6, 0.3),
    ("jupyter",    765, 205, 26, 0.80, 2, 5.0, 0.7),
    ("node",       885, 235, 28, 0.80, 0, 3.8, 1.1),
    ("java",      1005, 155, 26, 0.85, 1, 4.5, 0.2),
    ("git",       1085, 255, 26, 0.85, 2, 4.3, 1.6),
]

SIGNAL = "#d11440"

THEMES = {
    "dark": dict(name="#e6edf3", muted="#8b949e"),
    "light": dict(name="#0d1117", muted="#57606a"),
}

RECT = re.compile(
    r'x="(?P<x>[\d.]+)"\s+y="(?P<y>[\d.]+)"\s+width="(?P<w>[\d.]+)"\s+'
    r'height="(?P<h>[\d.]+)"\s+rx="(?P<rx>[\d.]+)"\s+fill="[^"]+"\s+opacity="(?P<op>[\d.]+)"'
)


def parse_rects(path: pathlib.Path, marker: str) -> list[dict]:
    """Lift the generated ripple rects out of an existing asset, unchanged."""
    rows = []
    for line in path.read_text().splitlines():
        if marker not in line:
            continue
        m = RECT.search(line)
        if m:
            rows.append({k: float(v) for k, v in m.groupdict().items()})
    if not rows:
        raise SystemExit(f"no rects found in {path.name}")
    return rows


ICON_FLOATS = [
    ("floatA", -9, -3),   # drifts up, tilts left
    ("floatB",  7,  2.5), # drifts down, tilts right
    ("floatC", -6,  3),   # drifts up, tilts right
]


def icon_float_keyframes() -> str:
    """Three drift shapes, shared by every icon via its float variant index."""
    out = []
    for name, dy, rot in ICON_FLOATS:
        out.append(f"""      @keyframes {name} {{
        0%   {{ transform: translateY(0) rotate(0deg); }}
        50%  {{ transform: translateY({dy}px) rotate({rot}deg); }}
        100% {{ transform: translateY(0) rotate(0deg); }}
      }}""")
    return "\n".join(out)


# Simplified, small-scale marks for each tech icon - a 24x24 box, filled in
# with each brand's colour. They are decorative at ~24-32px so they trade
# logo fidelity for reading cleanly at that size.
def _icon_react() -> str:
    return ("""<g fill="none" stroke="#61DAFB" stroke-width="1.4">
      <ellipse cx="12" cy="12" rx="10" ry="4"/>
      <ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/>
      <ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/>
    </g><circle cx="12" cy="12" r="2" fill="#61DAFB"/>""")


def _icon_tensorflow() -> str:
    return ("""<path d="M12 2l7 4v3l-7-4-7 4V6z" fill="#FF6F00"/>
    <path d="M12 9l7 4v3l-7-4-7 4v-3z" fill="#FF6F00" opacity="0.8"/>
    <path d="M12 16l5 3-5 3-5-3z" fill="#FF6F00" opacity="0.6"/>""")


def _icon_docker() -> str:
    return ("""<rect x="5" y="8" width="3" height="3" fill="#2496ED"/>
    <rect x="9" y="8" width="3" height="3" fill="#2496ED"/>
    <rect x="13" y="8" width="3" height="3" fill="#2496ED"/>
    <rect x="9" y="4" width="3" height="3" fill="#2496ED"/>
    <path d="M2 14c1-2 3-3 5-3h10c2 0 3 1 4 3-1 3-4 5-9 5S3 17 2 14z" fill="#2496ED"/>""")


def _icon_python() -> str:
    return ("""<path d="M8 3h6a3 3 0 013 3v3H9a3 3 0 00-3 3v2H4a3 3 0 01-3-3V8a5 5 0 015-5z" fill="#3776AB"/>
    <circle cx="7" cy="6" r="1" fill="#fff"/>
    <path d="M16 21h-6a3 3 0 01-3-3v-3h8a3 3 0 003-3V10h2a3 3 0 013 3v3a5 5 0 01-5 5z" fill="#FFD43B"/>
    <circle cx="17" cy="18" r="1" fill="#0d1117"/>""")


def _icon_gcp() -> str:
    return """<path d="M15 8a5 5 0 00-9.6 1.8A4 4 0 006 18h9a4.5 4.5 0 000-9 5 5 0 000-1z" fill="#4285F4"/>"""


def _icon_jupyter() -> str:
    return ("""<circle cx="12" cy="7" r="3" fill="none" stroke="#F37626" stroke-width="1.3"/>
    <circle cx="7" cy="16" r="3" fill="none" stroke="#F37626" stroke-width="1.3"/>
    <circle cx="17" cy="16" r="3" fill="none" stroke="#F37626" stroke-width="1.3"/>
    <circle cx="12" cy="13" r="1.6" fill="#F37626"/>""")


def _icon_node() -> str:
    return ("""<path d="M12 2l8 4.5v11L12 22l-8-4.5v-11z" fill="none" stroke="#539E43" stroke-width="1.6"/>
    <circle cx="12" cy="12" r="2.2" fill="#539E43"/>""")


def _icon_java() -> str:
    return ("""<rect x="5" y="9" width="12" height="7" rx="1.5" fill="#f89820"/>
    <path d="M17 10.5h1a2 2 0 010 4h-1" fill="none" stroke="#f89820" stroke-width="1.4"/>
    <path d="M9 20c3 1.4 6 1.4 9 0" stroke="#f89820" stroke-width="1.2" fill="none"/>
    <path d="M9 5c-1 1-1 2 0 3M13 5c-1 1-1 2 0 3" stroke="#f89820" stroke-width="1.1" fill="none" stroke-linecap="round"/>""")


def _icon_git() -> str:
    return ("""<circle cx="6" cy="6" r="2" fill="#F05033"/>
    <circle cx="6" cy="18" r="2" fill="#F05033"/>
    <circle cx="17" cy="12" r="2" fill="#F05033"/>
    <path d="M6 8v8M6 12h9a2 2 0 002-2" stroke="#F05033" stroke-width="1.4" fill="none"/>""")


def _icon_sparkle() -> str:
    return ("""<path d="M12 2l1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8z" fill="#8ab4f8"/>
    <path d="M19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z" fill="#c58af9"/>""")


def _icon_terminal() -> str:
    return ("""<rect x="2" y="4" width="20" height="16" rx="2" fill="#161b22" stroke="#8b949e" stroke-width="1.2"/>
    <path d="M6 9l4 3-4 3" fill="none" stroke="#3fb950" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    <line x1="12" y1="15" x2="17" y2="15" stroke="#3fb950" stroke-width="1.6" stroke-linecap="round"/>""")


ICON_SHAPES = {
    "react": _icon_react, "tensorflow": _icon_tensorflow, "docker": _icon_docker,
    "python": _icon_python, "gcp": _icon_gcp, "jupyter": _icon_jupyter,
    "node": _icon_node, "java": _icon_java, "git": _icon_git,
    "sparkle": _icon_sparkle, "terminal": _icon_terminal,
}


def icon_field() -> str:
    """
    The scattered tech-icon background. Each icon is a 24x24 mark scaled to
    its own size, centred on (x, y), with its float animation set inline
    (variant, duration, delay) rather than via a per-icon class - only three
    keyframe shapes exist, and every icon just picks one and times itself.

    Position and size live on an outer <g transform="...">; the float
    animation lives on an inner <g style="animation:...">. They have to be
    two separate groups - a CSS animation on `transform` replaces the whole
    property, so if the static translate/scale lived on the same element as
    the animated one, every keyframe tick would wipe out the icon's position
    and size along with it.
    """
    out = []
    for key, x, y, size, op, variant, dur, delay in ICONS:
        scale = size / 24
        name, _, _ = ICON_FLOATS[variant]
        out.append(f"""
    <g transform="translate({x - size / 2:.1f} {y - size / 2:.1f}) scale({scale:.3f})" opacity="{op}">
      <g style="transform-box:fill-box;transform-origin:center;animation:{name} {dur}s ease-in-out {delay}s infinite;">
        {ICON_SHAPES[key]()}
      </g>
    </g>""")
    return f"""
  <g class="icons" aria-hidden="true">{''.join(out)}
  </g>
"""


def css(t: dict) -> str:
    return f"""
      .eyebrow {{ font: 600 13px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; letter-spacing: .18em; fill: {SIGNAL}; }}
      .name    {{ font: 700 46px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['name']}; }}
      .role    {{ font: 400 20px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['muted']}; }}
      .caption {{ font: 400 13px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['muted']}; letter-spacing: .02em; }}

      /* Every animated element below rests at its FINAL state and animates in
         from a keyframed start with fill-mode backwards, so a renderer that
         skips animations still shows the composed banner. */

      .reveal {{ animation: revealText .6s cubic-bezier(.16,1,.3,1) backwards; }}
      @keyframes revealText {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

      .name-in {{
        transform-box: fill-box; transform-origin: left bottom;
        animation: nameIn .72s cubic-bezier(.22,1.42,.36,1) .16s backwards;
      }}
      @keyframes nameIn {{
        0%   {{ opacity: 0; transform: translateY(14px) scale(.94, 1.06); }}
        60%  {{ opacity: 1; transform: translateY(0)    scale(1.02, .98); }}
        100% {{ opacity: 1; transform: translateY(0)    scale(1, 1); }}
      }}

      /* ---------- floating icon field ---------- */
{icon_float_keyframes()}

      @media (prefers-reduced-motion: reduce) {{
        .reveal, .name-in {{
          animation: none !important;
          opacity: 1 !important;
          transform: none !important;
        }}
        .icons g g {{ animation: none !important; transform: none !important; }}
      }}
"""


def build_banner(t: dict) -> str:
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Praveen Nukilla &#8212; Applied AI &amp; Backend Engineer">
  <defs>
    <style>{css(t)}</style>
  </defs>
{icon_field()}
  <text x="64" y="92"  class="eyebrow reveal" style="animation-delay:.05s">APPLIED AI &#183; BACKEND ENGINEER</text>
  <text x="64" y="152" class="name name-in">Praveen Nukilla</text>
  <text x="64" y="188" class="role reveal"    style="animation-delay:.28s">Speech-AI systems on GCP + Gemini</text>
  <text x="64" y="222" class="caption reveal" style="animation-delay:.38s">IIIT Allahabad &#183; Final Year &#183; ECE</text>
  <text x="64" y="252" class="caption reveal" style="animation-delay:.48s" fill="{SIGNAL}">400+ DSA solved &#183; live products, real users</text>
</svg>
"""


def build_rule(rows: list[dict]) -> str:
    """
    Section rule: a quiet travelling ripple across a thin strip, unrelated
    to the banner's icon field.

    It appears four times down the README, so the kick is small and the period
    is long enough that two rules on screen at once do not read as a strobe.
    """
    # Timed against where the bars actually are, not the viewBox: the rule's
    # bars only occupy the left part of the 1200-wide frame, so dividing by the
    # full width left half of every cycle with nothing happening in it.
    x0 = min(r["x"] for r in rows)
    span = max(max(r["x"] for r in rows) - x0, 1.0)
    period, start = 4.6, 0.2
    out = []
    for r in rows:
        f = (r["x"] - x0) / span
        out.append(
            f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["w"]:.0f}" height="{r["h"]}" '
            f'rx="{r["rx"]}" fill="{SIGNAL}" opacity="{r["op"]}" '
            f'style="transform-box:fill-box;transform-origin:center;'
            f'animation:ripple {period}s ease-out {start + f * period:.3f}s infinite;"/>'
        )
    bars = "\n    ".join(out)
    return f"""<svg width="1200" height="28" viewBox="0 0 1200 28" fill="none" xmlns="http://www.w3.org/2000/svg" role="presentation">
  <defs>
    <style>
      @keyframes ripple {{
        0%   {{ transform: scaleY(1); }}
        5%   {{ transform: scaleY(1.7); }}
        18%  {{ transform: scaleY(.92); }}
        34%  {{ transform: scaleY(1); }}
        100% {{ transform: scaleY(1); }}
      }}
      @media (prefers-reduced-motion: reduce) {{
        rect {{ animation: none !important; transform: none !important; }}
      }}
    </style>
  </defs>
  <g opacity="0.55">
    {bars}
  </g>
</svg>
"""


def main() -> None:
    rule_rows = parse_rects(ASSETS / "rule.svg", "<rect")

    for theme_name, t in THEMES.items():
        out = ASSETS / f"banner-{theme_name}.svg"
        out.write_text(build_banner(t))
        print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")

    out = ASSETS / "rule.svg"
    out.write_text(build_rule(rule_rows))
    print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
