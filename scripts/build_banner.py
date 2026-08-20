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

# The bot floats in the corridor between the text block (which ends at x~478)
# and the SIGNAL panel (which starts at x=740).
BOT_X, BOT_Y = 614, 150
EYE_Y = -14               # eye centre, relative to the bot's own origin
PUPIL_THROW = 11          # how far the pupil travels to either side
LENS_R = 24               # must clear PUPIL_THROW + the iris radius, or the
                          # iris bleeds off the lens at the ends of the sweep

# Playhead sweep across the SIGNAL panel. The bars derive their timing from
# these, so the kick and the playhead cannot drift apart.
PANEL_X, PANEL_W = 740, 420
SCAN_X0, SCAN_X1 = 750, 1150
SCAN_PERIOD = 2.8         # seconds for one sweep
SCAN_START = 1.5          # after the bars have risen

# The bot spends its first sweep reading the name, then locks onto the panel.
# Offsetting by a whole period keeps the pupil in phase with the playhead: both
# are driven from these two constants, so they cannot drift apart.
LOOK_START = 1.5
TRACK_START = SCAN_START + SCAN_PERIOD
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
        metal="#c9d1d9", metal_dark="#8b949e",
        visor="#0d1117", lens="#161b22",
        scan_op="0.85",
    ),
    "light": dict(
        name="#0d1117", muted="#57606a", stroke="#d0d7de",
        metal="#57606a", metal_dark="#8c959f",
        visor="#161b22", lens="#0d1117",
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

      /* ---------- the bot ---------- */

      /* arrives with a settle rather than a fade */
      .bot-in {{ animation: botIn .9s cubic-bezier(.2,1.32,.36,1) .45s backwards; }}
      @keyframes botIn {{
        from {{ opacity: 0; transform: translateY(-38px) scale(.86); }}
        to   {{ opacity: 1; transform: translateY(0)     scale(1); }}
      }}

      /* hovering, on a period that shares no factor with the sweep */
      .bob {{ animation: bob 4.3s ease-in-out 1.3s infinite; }}
      @keyframes bob {{
        0%, 100% {{ transform: translateY(-3px); }}
        50%      {{ transform: translateY(3px); }}
      }}

      /* the head leads the eye: it turns to the name, then tracks the panel */
      .head-turn {{
        animation: headLook {SCAN_PERIOD}s cubic-bezier(.3,1.3,.4,1) {LOOK_START}s both,
                   headTrack {SCAN_PERIOD}s linear {TRACK_START}s infinite;
      }}
      @keyframes headLook {{
        0%   {{ transform: rotate(0deg); }}
        18%  {{ transform: rotate(-4.5deg); }}
        70%  {{ transform: rotate(-4.5deg); }}
        100% {{ transform: rotate(-2.6deg); }}
      }}
      @keyframes headTrack {{
        from {{ transform: rotate(-2.6deg); }}
        to   {{ transform: rotate(2.6deg); }}
      }}

      /* boot: the aperture opens */
      .iris-open {{ animation: irisOpen .42s cubic-bezier(.3,1.4,.4,1) 1.05s backwards; }}
      @keyframes irisOpen {{ from {{ transform: scale(.05); }} to {{ transform: scale(1); }} }}

      /* blink on twice the sweep period, so it never lands mid-saccade */
      .lid {{ animation: blink {SCAN_PERIOD * 2}s ease-in-out {TRACK_START + 1.1}s infinite; }}
      @keyframes blink {{
        0%, 91%, 100% {{ transform: scaleY(1); }}
        94%           {{ transform: scaleY(.06); }}
        97%           {{ transform: scaleY(1); }}
      }}

      /* The pupil reads the name first, then hands off to the playhead. The
         look ends exactly where the track begins, so the handoff at
         TRACK_START is seamless rather than a jump. */
      .pupil {{
        animation: pupilLook {SCAN_PERIOD}s cubic-bezier(.3,1.5,.4,1) {LOOK_START}s both,
                   pupilTrack {SCAN_PERIOD}s linear {TRACK_START}s infinite;
      }}
      @keyframes pupilLook {{
        0%   {{ transform: translateX(0); }}
        14%  {{ transform: translateX(-{PUPIL_THROW}px); }}
        70%  {{ transform: translateX(-{PUPIL_THROW}px); }}
        84%  {{ transform: translateX(-3px); }}
        100% {{ transform: translateX(-{PUPIL_THROW}px); }}
      }}
      @keyframes pupilTrack {{
        from {{ transform: translateX(-{PUPIL_THROW}px); }}
        to   {{ transform: translateX({PUPIL_THROW}px); }}
      }}

      /* The playhead is pure motion - it carries no content. Unlike everything
         else here it rests at opacity 0, because a playhead parked at the left
         edge of a still frame reads as a stray rule, not as a composed panel. */

      .live {{
        transform-box: fill-box; transform-origin: center;
        animation: recPop .34s cubic-bezier(.34,1.56,.64,1) 1.9s backwards,
                   pulse 1.7s ease-in-out 2.2s infinite;
      }}

      @media (prefers-reduced-motion: reduce) {{
        .bar, .reveal, .name-in, .panel-border, .rec-dot,
        .bot-in, .bob, .head-turn, .iris-open, .lid, .pupil, .live {{
          animation: none !important;
          opacity: 1 !important;
          transform: none !important;
          stroke-dashoffset: 0 !important;
        }}
        .playhead {{ animation: none !important; opacity: 0 !important; }}
      }}
"""


def bot(t: dict) -> str:
    """
    The listening unit.

    Transform origins come from nested translate/rotate group pairs rather than
    CSS transform-origin, so they do not depend on transform-box support: each
    animated group transforms about its own local origin and the wrapper before
    it puts that origin where the joint is. The eye stack is
    lid > iris > pupil, all nested, so blinking, opening and looking compose
    instead of overwriting one another's transform.
    """
    return f"""
  <g class="bot-in">
    <g transform="translate({BOT_X},{BOT_Y})">
      <g class="bob">
        <g class="head-turn">
          <!-- antenna -->
          <rect x="-2" y="-84" width="4" height="26" rx="2" fill="{t['metal_dark']}"/>
          <circle cx="0" cy="-88" r="4.5" fill="{SIGNAL}" class="live"/>

          <!-- shell -->
          <rect x="-54" y="-58" width="108" height="94" rx="24" fill="{t['metal']}"/>
          <rect x="-54" y="-58" width="108" height="94" rx="24" fill="none" stroke="{t['metal_dark']}" stroke-width="1.5" opacity="0.5"/>
          <!-- side mounts -->
          <rect x="-62" y="-24" width="9" height="26" rx="4" fill="{t['metal_dark']}"/>
          <rect x="53" y="-24" width="9" height="26" rx="4" fill="{t['metal_dark']}"/>

          <!-- visor -->
          <rect x="-44" y="-46" width="88" height="62" rx="18" fill="{t['visor']}"/>

          <!-- eye -->
          <g transform="translate(0,{EYE_Y})">
            <g class="lid">
              <g class="iris-open">
                <circle r="{LENS_R}" fill="{t['lens']}"/>
                <circle r="{LENS_R}" fill="none" stroke="{SIGNAL}" stroke-width="1.5" opacity="0.55"/>
                <g class="pupil">
                  <circle r="12" fill="{SIGNAL}"/>
                  <circle r="5.5" fill="{t['visor']}"/>
                  <circle cx="-4.5" cy="-5" r="3" fill="#ffffff" opacity="0.75"/>
                </g>
              </g>
            </g>
          </g>

          <!-- vent, and the thruster nubs it hovers on -->
          <path d="M -22 26 H 22 M -16 32 H 16" stroke="{t['metal_dark']}" stroke-width="2.5" stroke-linecap="round" opacity="0.6"/>
          <rect x="-30" y="35" width="16" height="8" rx="4" fill="{t['metal_dark']}"/>
          <rect x="14" y="35" width="16" height="8" rx="4" fill="{t['metal_dark']}"/>
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
{bot(t)}</svg>
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
