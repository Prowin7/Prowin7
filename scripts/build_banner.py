#!/usr/bin/env python3
"""
Regenerate assets/banner-dark.svg, assets/banner-light.svg and assets/rule.svg.

Layout
------
Text block on the left, SIGNAL panel on the right, and a curtain that covers
the whole 1200x320 frame for the first moment of the reveal. Nothing is parked
in the corridor at x 490-740 any more: the character that used to hover there
(a listening unit, and a boom mic before that) is gone, and the curtain needs
the full width, so the corridor is now plain breathing room between the two
blocks rather than a slot something has to fit into.

Motion
------
The curtain drops. One cloth in nine vertical panels: they fall in together
from above the frame, hold there covering the banner, then let go one after
another from the left, so the reveal travels across the frame instead of
lifting as a slab. Each panel falls top edge first and keeps going past the
bottom, which is why every part of the banner is revealed from the top down.

The panels are drawn below the frame and spend the whole animation above where
they were drawn (see Constraints), so the run ends with the cloth already at
its markup position - nothing is held by a fill mode and nothing snaps.

The SIGNAL panel is no longer decorative. A playhead sweeps it on a loop and
each bar kicks as the playhead reaches it - the bars' animation delays are
derived from their own x position, so the kick travels left to right at exactly
the playhead's speed. The section rules under each heading run the same
travelling ripple, which is why they are generated here too.

Constraints
-----------
GitHub serves these through an img element: CSS animations run, scripts do not,
so there is no SMIL and no JS here.

Every animated element rests at its FINAL state and animates in from a keyframed
start with fill-mode backwards. A renderer that declines to run the animations
then shows the composed banner rather than an empty frame.

That rule is weaker than it looks, and the curtain is why it had to be written
down. "Animations do not run" is not the only failure - they can also be *held
at time zero*. A browser pauses CSS animations in a hidden or backgrounded tab,
and screenshot tooling captures whatever the first frame is. Verified while
building this (2026-08-20): with the tab hidden, every element sat on its own
first keyframe indefinitely, which for the text means the banner renders as a
bare SIGNAL panel with no name on it.

For the text that is cosmetic. For anything that covers the frame it is fatal:
a curtain whose first keyframe is the covering position is a curtain that
never comes up. So the curtain takes the stricter rule - frame zero is
off-stage, and no animation-delay anywhere, since a delay makes frame zero last
as long as the delay does. Anything added later that can occlude the banner
needs the same treatment.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1200, 320

# The curtain. Panels overhang the frame by OVERHANG at the top so that a
# panel still mid-fall never shows a gap above its own top edge.
#
# One animation per panel, all the same length, all starting together - the
# stagger lives inside the keyframes (see curtain_keyframes) rather than in
# animation-delay. That is forced by the freeze described in Constraints: a
# delayed animation shows its *first* keyframe for the length of the delay, and
# a renderer stopped at t=0 shows it forever, so the covering position can
# never be frame zero of anything.
CURTAIN_PANELS = 9
OVERHANG = 40
CURTAIN_DUR = 1.6         # whole run: drop in, hold, peel away left to right
DROP_PCT = 20             # cloth has arrived and covers the frame
HOLD_PCT = 34             # leftmost panel starts falling away
HOLD_STEP = 3.5           # each panel waits this much longer than its left neighbour
FALL_PCT = 38             # a panel's own fall, frame top to clear of the bottom

# Playhead sweep across the SIGNAL panel. The bars derive their timing from
# these, so the kick and the playhead cannot drift apart.
PANEL_X, PANEL_W = 740, 420
SCAN_X0, SCAN_X1 = 750, 1150
SCAN_PERIOD = 2.8         # seconds for one sweep
SCAN_START = 1.5          # after the bars have risen

PANEL_INNER = 176         # usable height inside the panel border

# A bar's kick is capped so a tall bar cannot scale out through the panel
# border - the previous breathe only ever shrank bars, so nothing caught this.
# Bucketed rather than per-bar because keyframes cannot be parameterised, and
# five named steps beat one custom property that has to resolve inside a
# keyframe on every renderer.
SCAN_STEPS = [1.0, 1.15, 1.3, 1.45, 1.6]

SIGNAL = "#d11440"

THEMES = {
    "dark": dict(
        name="#e6edf3", muted="#8b949e", stroke="#30363d",
        scan_op="0.85",
    ),
    "light": dict(
        name="#0d1117", muted="#57606a", stroke="#d0d7de",
        scan_op="0.7",
    ),
}

RECT = re.compile(
    r'x="(?P<x>[\d.]+)"\s+y="(?P<y>[\d.]+)"\s+width="(?P<w>[\d.]+)"\s+'
    r'height="(?P<h>[\d.]+)"\s+rx="(?P<rx>[\d.]+)"\s+fill="[^"]+"\s+opacity="(?P<op>[\d.]+)"'
)


def parse_rects(path: pathlib.Path, marker: str) -> list[dict]:
    """Lift the generated waveform rects out of an existing asset, unchanged."""
    rows = []
    for line in path.read_text().splitlines():
        if marker not in line:
            continue
        m = RECT.search(line)
        if m:
            rows.append({k: float(v) for k, v in m.groupdict().items()})
    if not rows:
        raise SystemExit(f"no waveform rects found in {path.name}")
    return rows


def scan_bucket(height: float) -> int:
    """Largest kick this bar can take without growing through the panel border."""
    allowed = PANEL_INNER / height if height else SCAN_STEPS[-1]
    idx = 0
    for i, step in enumerate(SCAN_STEPS):
        if step <= allowed:
            idx = i
    return idx


def scan_keyframes() -> str:
    """
    One keyframe set per kick size: a hit as the playhead arrives, then decay.

    Two braces, not four. This function's own f-string collapses `{{` to `{`,
    and the result is *interpolated* into css()'s f-string rather than formatted
    again - so four braces reached the stylesheet as a literal `{{`, which is
    not valid CSS. Every @keyframes scan* block was being dropped by the parser,
    and the bars, whose animation names those blocks, silently never kicked.
    """
    out = []
    for i, k in enumerate(SCAN_STEPS):
        dip = 1 - (k - 1) * 0.4          # louder kick, deeper trough after it
        out.append(f"""      @keyframes scan{i} {{
        0%   {{ transform: scaleY(1); }}
        6%   {{ transform: scaleY({k}); }}
        22%  {{ transform: scaleY({dip:.3f}); }}
        45%  {{ transform: scaleY(1.02); }}
        100% {{ transform: scaleY(1); }}
      }}""")
    return "\n".join(out)


def curtain_keyframes() -> str:
    """
    One keyframe set per curtain panel, plus the rule that names it.

    Three positions, in the panel's own coordinates (it is drawn one frame
    height below the viewBox, so 0 means off-stage below):

        ABOVE   - a whole frame further up again, out of sight over the top
        COVER   - exactly over the frame
        0       - back where the markup drew it, off-stage below

    All nine share ABOVE -> COVER, so the cloth arrives as one sheet. They part
    company at the hold: panel i waits HOLD_STEP longer than the panel to its
    left before letting go, which is what makes the reveal travel across the
    frame instead of dropping as a slab. Every panel's fall is the same length
    (FALL_PCT), so a panel that waited longer does not also fall faster.
    """
    above = 2 * H + 2 * OVERHANG
    cover = H + OVERHANG
    ease = "cubic-bezier(.55,.06,.68,.19)"

    out = []
    for i in range(CURTAIN_PANELS):
        hold = HOLD_PCT + i * HOLD_STEP
        landed = hold + FALL_PCT
        out.append(f"""      .d{i} {{ animation-name: fall{i}; }}
      @keyframes fall{i} {{
        0%      {{ transform: translateY(-{above}px); animation-timing-function: {ease}; }}
        {DROP_PCT}%     {{ transform: translateY(-{cover}px); }}
        {hold:g}%   {{ transform: translateY(-{cover}px); animation-timing-function: {ease}; }}
        {landed:g}%   {{ transform: translateY(0); }}
        100%    {{ transform: translateY(0); }}
      }}""")
    return "\n".join(out)


def bars_svg(rows: list[dict]) -> str:
    """
    Re-emit the panel's bars with scan timing derived from each bar's own x.

    A bar at fraction f across the sweep starts its kick at SCAN_START + f *
    SCAN_PERIOD, and the playhead covers the same fraction of its travel in the
    same time, so the kick tracks the playhead by construction rather than by a
    hand-tuned delay per bar.
    """
    span = SCAN_X1 - SCAN_X0
    out = []
    for i, r in enumerate(rows):
        f = min(max((r["x"] - SCAN_X0) / span, 0.0), 1.0)
        rise_delay = 0.35 + i * 0.018
        scan_delay = SCAN_START + f * SCAN_PERIOD
        out.append(
            f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["w"]:.0f}" height="{r["h"]}" '
            f'rx="{r["rx"]}" fill="{SIGNAL}" opacity="{r["op"]}" class="bar" '
            f'style="transform-box:fill-box;transform-origin:center;'
            f'animation:riseIn .42s cubic-bezier(.22,1.61,.36,1) {rise_delay:.3f}s 1 both,'
            f'scan{scan_bucket(r["h"])} {SCAN_PERIOD}s ease-out {scan_delay:.3f}s infinite;"/>'
        )
    return "\n      ".join(out)


def css(t: dict) -> str:
    return f"""
      .eyebrow {{ font: 600 13px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; letter-spacing: .18em; fill: {SIGNAL}; }}
      .name    {{ font: 700 46px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['name']}; }}
      .role    {{ font: 400 20px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['muted']}; }}
      .caption {{ font: 400 13px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['muted']}; letter-spacing: .02em; }}
      .label   {{ font: 600 11px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; letter-spacing: .2em; fill: {t['muted']}; }}

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

      @keyframes riseIn {{
        0%   {{ transform: scaleY(0); opacity: 0; }}
        55%  {{ transform: scaleY(1.12); opacity: 1; }}
        100% {{ transform: scaleY(1); opacity: 1; }}
      }}
      /* one bar's share of the sweep, at each capped kick size */
{scan_keyframes()}

      .playhead {{ opacity: 0; animation: sweep {SCAN_PERIOD}s linear {SCAN_START}s infinite backwards; }}
      @keyframes sweep {{
        from {{ opacity: 1; transform: translateX(0); }}
        to   {{ opacity: 1; transform: translateX({SCAN_X1 - SCAN_X0}px); }}
      }}

      .panel-border {{ stroke-dasharray: 100; animation: draw .55s ease-out .05s backwards; }}
      @keyframes draw {{ from {{ stroke-dashoffset: 100; }} to {{ stroke-dashoffset: 0; }} }}

      .rec-dot {{
        transform-box: fill-box; transform-origin: center;
        animation: recPop .3s cubic-bezier(.34,1.56,.64,1) .65s backwards,
                   pulse 1.7s ease-in-out .95s infinite;
      }}
      @keyframes recPop {{ from {{ transform: scale(0); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
      @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}

      /* ---------- the curtain ---------- */

      /* Every panel runs for the same length with no delay and no fill mode,
         so frame zero is the only state a frozen renderer can show - and frame
         zero is the cloth still above the frame, out of sight. The panel then
         drops in, holds, and falls away; its last keyframe is the resting
         position the markup already draws, so nothing snaps when it ends.

         The falls are shaped like gravity - slow to let go, fastest at the
         end. An ease-out would read as the cloth being lowered on a winch. */
      .drape {{ animation-duration: {CURTAIN_DUR}s; animation-timing-function: linear; }}
{curtain_keyframes()}

      /* The playhead is pure motion - it carries no content. Unlike everything
         else here it rests at opacity 0, because a playhead parked at the left
         edge of a still frame reads as a stray rule, not as a composed panel. */

      @media (prefers-reduced-motion: reduce) {{
        .bar, .reveal, .name-in, .panel-border, .rec-dot {{
          animation: none !important;
          opacity: 1 !important;
          transform: none !important;
          stroke-dashoffset: 0 !important;
        }}
        .playhead {{ animation: none !important; opacity: 0 !important; }}
        /* Killing the animation is enough to hide the curtain - its resting
           position is already below the frame. Don't add transform:none to
           the rule above and sweep this in with it: that is a no-op here, but
           it would also stop this comment being true if the panels were ever
           drawn on top of the frame instead. */
        .drape {{ animation: none !important; }}
      }}
"""


def curtain() -> str:
    """
    The curtain: one cloth, cut into vertical panels that fall in sequence.

    Each panel is drawn starting at y=H - that is, immediately *below* the
    frame, where none of it is visible. Everything the panel does happens in
    the animation, which starts it further above the frame than the frame is
    tall and ends it back here. Reading the markup alone therefore shows the
    finished banner, which is the fallback this file is built around.

    Panels are 1px wider than their share and start half a pixel early, so
    neighbours overlap rather than leaving a hairline of banner showing
    between them when the renderer rounds their edges to device pixels.

    The panel is only two rects deep: the flat crimson, then a horizontal
    gradient over it that darkens both edges and lifts the middle. That is
    what makes a flat fill read as a hanging pleat, and it costs one shared
    gradient rather than per-panel shading.
    """
    span = W / CURTAIN_PANELS
    panels = []
    for i in range(CURTAIN_PANELS):
        x = i * span - 0.5
        w = span + 1
        panels.append(f"""
    <g class="drape d{i}">
      <rect x="{x:.1f}" y="{H}" width="{w:.1f}" height="{H + OVERHANG}" fill="{SIGNAL}"/>
      <rect x="{x:.1f}" y="{H}" width="{w:.1f}" height="{H + OVERHANG}" fill="url(#pleat)"/>
      <!-- The top edge is what leads the fall, so it carries the detail: a lit
           fold, and the shadow the fold throws down the cloth beneath it. -->
      <rect x="{x:.1f}" y="{H}" width="{w:.1f}" height="6" fill="#ffffff" opacity="0.22"/>
      <rect x="{x:.1f}" y="{H + 6}" width="{w:.1f}" height="12" fill="#000000" opacity="0.16"/>
    </g>""")

    return f"""
  <g class="curtain" aria-hidden="true">{''.join(panels)}
  </g>
"""


def build_banner(t: dict, bars: str) -> str:
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Praveen Nukilla &#8212; Applied AI &amp; Backend Engineer">
  <defs>
    <linearGradient id="scanfade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0"   stop-color="{SIGNAL}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{SIGNAL}" stop-opacity="{t['scan_op']}"/>
      <stop offset="1"   stop-color="{SIGNAL}" stop-opacity="0"/>
    </linearGradient>
    <!-- One pleat, reused by every curtain panel: dark at the folds either
         side, lit just off centre where the cloth turns towards the light. -->
    <linearGradient id="pleat" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"    stop-color="#000000" stop-opacity="0.42"/>
      <stop offset="0.30" stop-color="#ffffff" stop-opacity="0.10"/>
      <stop offset="0.66" stop-color="#000000" stop-opacity="0.08"/>
      <stop offset="1"    stop-color="#000000" stop-opacity="0.44"/>
    </linearGradient>
    <style>{css(t)}</style>
  </defs>

  <text x="64" y="92"  class="eyebrow reveal" style="animation-delay:.05s">APPLIED AI &#183; BACKEND ENGINEER</text>
  <text x="64" y="152" class="name name-in">Praveen Nukilla</text>
  <text x="64" y="188" class="role reveal"    style="animation-delay:.28s">Speech-AI systems on GCP + Gemini</text>
  <text x="64" y="222" class="caption reveal" style="animation-delay:.38s">IIIT Allahabad &#183; Final Year &#183; ECE</text>
  <text x="64" y="252" class="caption reveal" style="animation-delay:.48s" fill="{SIGNAL}">400+ DSA solved &#183; live products, real users</text>

  <text x="{PANEL_X}" y="28" class="label reveal" style="animation-delay:0s">SIGNAL</text>
  <rect x="{PANEL_X}" y="40" width="{PANEL_W}" height="200" rx="8" fill="{SIGNAL}" fill-opacity="0.04"/>
  <rect class="panel-border" pathLength="100" x="{PANEL_X}" y="40" width="{PANEL_W}" height="200" rx="8" fill="none" stroke="{t['stroke']}" stroke-width="1"/>
  <circle cx="762" cy="66" r="4" fill="{SIGNAL}" class="rec-dot"/>
  <text x="774" y="70" class="caption reveal" style="animation-delay:0.65s">REC</text>
      {bars}
  <g class="playhead">
    <rect x="{SCAN_X0}" y="52" width="2" height="176" fill="url(#scanfade)"/>
  </g>
  <text x="756" y="224" class="caption reveal" style="animation-delay:.9s">44.1kHz &#183; Silero VAD</text>
{curtain()}</svg>
"""


def build_rule(rows: list[dict]) -> str:
    """
    Section rule: the same travelling ripple as the panel, much quieter.

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
    panel_rows = parse_rects(ASSETS / "banner-dark.svg", 'class="bar"')
    rule_rows = parse_rects(ASSETS / "rule.svg", "<rect")

    bars = bars_svg(panel_rows)
    for theme_name, t in THEMES.items():
        out = ASSETS / f"banner-{theme_name}.svg"
        out.write_text(build_banner(t, bars))
        print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")

    out = ASSETS / "rule.svg"
    out.write_text(build_rule(rule_rows))
    print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
