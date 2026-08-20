#!/usr/bin/env python3
"""
Regenerate assets/banner-dark.svg, assets/banner-light.svg and assets/rule.svg.

Layout
------
The mic hangs from above into the vertical corridor between the text block and
the SIGNAL panel. The previous version reached in on a long boom from the right
and had three problems that only showed up on the live profile, where the
README column scales the banner down: the arm ran along the panel's bottom edge
and its collar overlapped the border, the arm itself read as a thin scratch
across the whole banner rather than as an object, and the bottom-left corner was
dead space. Dropping in from above removes all three - the corridor at x 490-740
is empty at every height, so nothing has to dodge anything, and the frame is
back to 1200x320 with no empty band.

Motion
------
The mic drops in, drags behind its mount, swings past plumb and settles, then
idles on two periods that do not divide into each other, so the mount and the
capsule never look mechanically locked.

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
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1200, 320

# The mic drops into the corridor between the text block (which ends at x~478)
# and the SIGNAL panel (which starts at x=740).
MOUNT_X, MOUNT_Y = 624, 74
DROP_FROM = -210          # how far above the mount the rig starts

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
        metal="#c9d1d9", metal_dark="#8b949e", grille="#484f58",
        ring_op="0.5", scan_op="0.85",
    ),
    "light": dict(
        name="#0d1117", muted="#57606a", stroke="#d0d7de",
        metal="#57606a", metal_dark="#8c959f", grille="#afb8c1",
        ring_op="0.38", scan_op="0.7",
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
    """One keyframe set per kick size: a hit as the playhead arrives, then decay."""
    out = []
    for i, k in enumerate(SCAN_STEPS):
        dip = 1 - (k - 1) * 0.4          # louder kick, deeper trough after it
        out.append(f"""      @keyframes scan{i} {{{{
        0%   {{{{ transform: scaleY(1); }}}}
        6%   {{{{ transform: scaleY({k}); }}}}
        22%  {{{{ transform: scaleY({dip:.3f}); }}}}
        45%  {{{{ transform: scaleY(1.02); }}}}
        100% {{{{ transform: scaleY(1); }}}}
      }}}}""")
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

      /* ---------- the mic ---------- */

      /* the rig drops in and overshoots */
      .drop {{ animation: drop 1.05s cubic-bezier(.2,1.3,.36,1) .5s backwards; }}
      @keyframes drop {{ from {{ transform: translateY({DROP_FROM}px); }} to {{ transform: translateY(0); }} }}

      /* follow-through: the capsule lags the mount, swings past plumb, settles */
      .swing {{ animation: swing 2.1s cubic-bezier(.26,1.1,.4,1) .5s backwards; }}
      @keyframes swing {{
        0%   {{ transform: rotate(-15deg); }}
        30%  {{ transform: rotate(11deg); }}
        52%  {{ transform: rotate(-6deg); }}
        72%  {{ transform: rotate(3deg); }}
        88%  {{ transform: rotate(-1.3deg); }}
        100% {{ transform: rotate(0deg); }}
      }}
      /* two idle periods that do not divide into each other */
      .sway-mount {{ animation: swayMount 7.5s ease-in-out 2.2s infinite; }}
      @keyframes swayMount {{
        0%, 100% {{ transform: rotate(.8deg); }}
        50%      {{ transform: rotate(-.8deg); }}
      }}
      .sway-caps {{ animation: swayCaps 6.1s ease-in-out 2.6s infinite; }}
      @keyframes swayCaps {{
        0%, 100% {{ transform: rotate(-1.5deg); }}
        50%      {{ transform: rotate(2.2deg); }}
      }}

      /* Capture rings and the playhead are pure motion - they carry no content.
         Unlike everything else here they rest at opacity 0, because a ring
         frozen mid-expansion reads as a rendering bug, not as a still frame. */
      .ring {{ opacity: 0; animation: ringOut 2.6s ease-out infinite backwards; }}
      @keyframes ringOut {{
        0%   {{ opacity: 0;   transform: scale(.35); }}
        18%  {{ opacity: {t['ring_op']}; }}
        100% {{ opacity: 0;   transform: scale(2); }}
      }}

      .live {{
        transform-box: fill-box; transform-origin: center;
        animation: recPop .34s cubic-bezier(.34,1.56,.64,1) 1.9s backwards,
                   pulse 1.7s ease-in-out 2.2s infinite;
      }}

      @media (prefers-reduced-motion: reduce) {{
        .bar, .reveal, .name-in, .panel-border, .rec-dot,
        .drop, .swing, .sway-mount, .sway-caps, .live {{
          animation: none !important;
          opacity: 1 !important;
          transform: none !important;
          stroke-dashoffset: 0 !important;
        }}
        .ring, .playhead {{ animation: none !important; opacity: 0 !important; }}
      }}
"""


def mic(t: dict) -> str:
    """
    Microphone on a drop rod.

    Rotation centres come from nested translate/rotate group pairs rather than
    CSS transform-origin, so they do not depend on transform-box support: each
    rotating group turns about its own local origin and the wrapper before it
    puts that origin on the joint.
    """
    return f"""
  <g class="drop">
    <g transform="translate({MOUNT_X},{MOUNT_Y})">
      <g class="sway-mount">
        <!-- rod, running up out of frame -->
        <rect x="-3" y="{-MOUNT_Y - 10}" width="6" height="{MOUNT_Y + 10}" rx="3" fill="{t['metal']}"/>
        <rect x="-6" y="-30" width="12" height="15" rx="4" fill="{t['metal_dark']}"/>
        <circle cx="0" cy="0" r="6" fill="{t['metal_dark']}"/>
        <!-- clamp stays with the rod, so the joint reads as connected at the
             extremes of the swing -->
        <rect x="-5" y="-3" width="10" height="13" rx="3" fill="{t['metal_dark']}"/>

        <g class="swing">
          <g class="sway-caps">
            <!-- yoke -->
            <path d="M -12 6 L -12 22 M 12 6 L 12 22" stroke="{t['metal_dark']}" stroke-width="3.5" stroke-linecap="round"/>
            <rect x="-15" y="20" width="30" height="10" rx="5" fill="{t['metal_dark']}"/>

            <!-- body, hanging nose-down and angled at the text block -->
            <g transform="translate(0,29) rotate(-16)">
              <rect x="-14" y="0" width="28" height="44" rx="7" fill="{t['metal']}"/>
              <rect x="-14" y="39" width="28" height="52" rx="14" fill="{t['grille']}"/>
              <path d="M -11 52 H 11 M -12 62 H 12 M -12 72 H 12 M -11 82 H 11"
                    stroke="{t['metal_dark']}" stroke-width="1.8" stroke-linecap="round" opacity="0.75"/>
              <rect x="-14" y="33" width="28" height="5" rx="2.5" fill="{SIGNAL}"/>
              <circle class="live" cx="0" cy="16" r="3.6" fill="{SIGNAL}"/>

              <!-- capture rings, leaving the capsule -->
              <g transform="translate(0,66)">
                <g class="ring" style="animation-delay:2.1s"><circle r="20" fill="none" stroke="{SIGNAL}" stroke-width="1.6"/></g>
                <g class="ring" style="animation-delay:2.97s"><circle r="20" fill="none" stroke="{SIGNAL}" stroke-width="1.6"/></g>
                <g class="ring" style="animation-delay:3.83s"><circle r="20" fill="none" stroke="{SIGNAL}" stroke-width="1.6"/></g>
              </g>
            </g>
          </g>
        </g>
      </g>
    </g>
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
{mic(t)}</svg>
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
