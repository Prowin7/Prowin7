#!/usr/bin/env python3
"""
Regenerate assets/banner-dark.svg and assets/banner-light.svg.

The banner keeps the original 1200x280 "signal" composition and extends the
frame to 1200x400 so a boom microphone can reach in from off-frame on the
right, settle over the empty corridor below the text, and hang there
listening. Capture rings pulse off the capsule and the waveform in the SIGNAL
panel sways on the same period as the boom, so the mic and the signal read as
one system rather than two decorations.

The waveform bars are lifted verbatim out of the existing banner-dark.svg so
the panel keeps its exact shape across regenerations.

Motion follows the classic animation principles rather than UI easing:
  - the boom slides in and overshoots instead of arriving flat
  - the mic drags behind the arm, then overshoots past plumb and settles
    (follow-through and overlapping action - the hanging part never stops at
    the same instant the thing carrying it does)
  - the idle sway on the mic runs slower than the boom's and lags it, so the
    two never look mechanically locked

Everything is expressed as CSS keyframes inside the SVG. GitHub serves these
files through an img element, which runs CSS animations but no script, so no
SMIL and no JS is used.

Every animated element rests at its FINAL state and animates in from a
keyframed start with fill-mode backwards. A renderer that declines to run the
animations then shows the composed banner rather than an empty frame - the
previous version made the text, the bars and the panel border visible only as
a side effect of an animation running, and lost all of them on a cached
decode.
"""

import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1200, 420

# The boom pivots off-frame to the right and reaches left into the corridor
# under the text block. Both endpoints are absolute; the arm is drawn in the
# pivot's local space.
PIVOT_X, PIVOT_Y = 1304, 240
ARM_DX, ARM_DY = -620, 48      # arm end, relative to the pivot
MIC_SCALE = 1.3                # the mic is the subject; the arm is just how it got here
BOOM_IN = 700                  # how far off-frame the rig starts

ARM_ANGLE = math.degrees(math.atan2(ARM_DY, ARM_DX))   # arm slope, for parts riding on it
COLLAR_F = 0.28                                        # collar position along the arm
COLLAR_X, COLLAR_Y = ARM_DX * COLLAR_F, ARM_DY * COLLAR_F

SIGNAL = "#d11440"

THEMES = {
    "dark": dict(
        name="#e6edf3", muted="#8b949e", stroke="#30363d",
        metal="#c9d1d9", metal_dark="#8b949e", grille="#484f58",
        ring_op="0.55",
    ),
    "light": dict(
        name="#0d1117", muted="#57606a", stroke="#d0d7de",
        metal="#57606a", metal_dark="#8c959f", grille="#afb8c1",
        ring_op="0.40",
    ),
}


def existing_bars() -> str:
    """Pull the waveform rects out of the current dark banner, unchanged."""
    src = (ASSETS / "banner-dark.svg").read_text()
    bars = [ln.strip() for ln in src.splitlines() if 'class="bar"' in ln]
    if not bars:
        raise SystemExit("no waveform bars found in assets/banner-dark.svg")
    return "\n      ".join(bars)


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
      @keyframes breathe {{
        0%, 100% {{ transform: scaleY(1); }}
        50%      {{ transform: scaleY(0.82); }}
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

      /* ---------- the boom ---------- */

      /* the rig pushes in from off-frame and overshoots before settling */
      .boom-in {{ animation: boomIn 1.15s cubic-bezier(.18,1.24,.34,1) .55s backwards; }}
      @keyframes boomIn {{ from {{ transform: translateX({BOOM_IN}px); }} to {{ transform: translateX(0); }} }}

      /* the arm keeps swaying: the slower of the two idle periods */
      .boom-idle {{ animation: boomIdle 7.5s ease-in-out 2.1s infinite; }}
      @keyframes boomIdle {{
        0%, 100% {{ transform: rotate(0deg); }}
        50%      {{ transform: rotate(-1.1deg); }}
      }}

      /* follow-through: the mic lags the arm, swings past plumb, then settles */
      .mic-drag {{ animation: micDrag 2.05s cubic-bezier(.26,1.1,.4,1) .55s backwards; }}
      @keyframes micDrag {{
        0%   {{ transform: rotate(38deg); }}
        38%  {{ transform: rotate(-14deg); }}
        60%  {{ transform: rotate(7deg); }}
        78%  {{ transform: rotate(-3.4deg); }}
        90%  {{ transform: rotate(1.4deg); }}
        100% {{ transform: rotate(0deg); }}
      }}
      /* a longer idle period than the arm's, and offset, so they never lock */
      .mic-idle {{ animation: micIdle 6.1s ease-in-out 2.6s infinite; }}
      @keyframes micIdle {{
        0%, 100% {{ transform: rotate(1.6deg); }}
        50%      {{ transform: rotate(-2.4deg); }}
      }}

      /* capture rings leaving the capsule */
      .ring {{ animation: ringOut 2.6s ease-out infinite backwards; }}
      @keyframes ringOut {{
        0%   {{ opacity: 0;   transform: scale(.35); }}
        18%  {{ opacity: {t['ring_op']}; }}
        100% {{ opacity: 0;   transform: scale(1.9); }}
      }}

      .live {{
        transform-box: fill-box; transform-origin: center;
        animation: livePop .34s cubic-bezier(.34,1.56,.64,1) 2.2s backwards,
                   pulse 1.7s ease-in-out 2.5s infinite;
      }}
      @keyframes livePop {{ from {{ transform: scale(0); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}

      /* The panel answers the mic: same period as the boom's sway, same phase.
         Translation only - a scale here would be taken about the SVG origin,
         not the panel, and would push the bars straight out through the
         panel border. */
      .bars-sway {{ animation: barsSway 7.5s ease-in-out 2.1s infinite; }}
      @keyframes barsSway {{
        0%, 100% {{ transform: translateX(0); }}
        50%      {{ transform: translateX(-3px); }}
      }}

      @media (prefers-reduced-motion: reduce) {{
        .bar, .reveal, .name-in, .panel-border, .rec-dot,
        .boom-in, .boom-idle, .mic-drag, .mic-idle, .ring, .live, .bars-sway {{
          animation: none !important;
          opacity: 1 !important;
          transform: none !important;
          stroke-dashoffset: 0 !important;
        }}
        .ring {{ opacity: {t['ring_op']} !important; }}
      }}
"""


def boom(t: dict) -> str:
    """
    Boom arm and microphone.

    Rotation centres are set by nested translate/rotate group pairs rather than
    CSS transform-origin, so they do not depend on transform-box support: each
    rotating group turns about its own local origin, and the wrapper before it
    puts that origin where the joint is.
    """
    return f"""
  <g class="boom-in">
    <g transform="translate({PIVOT_X},{PIVOT_Y})">
      <g class="boom-idle">
        <!-- arm, drawn from the off-frame pivot to the mount -->
        <line x1="0" y1="0" x2="{ARM_DX}" y2="{ARM_DY}" stroke="{t['metal']}" stroke-width="8" stroke-linecap="round"/>
        <line x1="-14" y1="1" x2="{ARM_DX + 18}" y2="{ARM_DY - 1}" stroke="{t['metal_dark']}" stroke-width="2" stroke-linecap="round" opacity="0.65"/>
        <!-- collar, where a real boom's sections telescope; sits ON the arm,
             so its centre and rotation are derived from the arm vector -->
        <rect x="{COLLAR_X - 13}" y="{COLLAR_Y - 7}" width="26" height="14" rx="4" fill="{t['metal_dark']}" transform="rotate({ARM_ANGLE:.2f} {COLLAR_X} {COLLAR_Y})"/>

        <g transform="translate({ARM_DX},{ARM_DY})">
          <!-- mount, and the mic hanging off it -->
          <circle cx="0" cy="0" r="6" fill="{t['metal_dark']}"/>
          <!-- clamp stays with the arm, so the joint reads as connected even at
               the extremes of the mic's swing -->
          <rect x="-5" y="-2" width="10" height="13" rx="3" fill="{t['metal_dark']}"/>
          <g class="mic-drag">
            <g class="mic-idle">
             <g transform="scale({MIC_SCALE})">
              <!-- yoke -->
              <path d="M -10 4 L -10 18 M 10 4 L 10 18" stroke="{t['metal_dark']}" stroke-width="3" stroke-linecap="round"/>
              <rect x="-12" y="16" width="24" height="9" rx="4" fill="{t['metal_dark']}"/>

              <!-- body, hanging nose-down and angled at the text block -->
              <g transform="translate(0,24) rotate(-19)">
                <rect x="-12" y="0" width="24" height="36" rx="6" fill="{t['metal']}"/>
                <rect x="-12" y="32" width="24" height="42" rx="12" fill="{t['grille']}"/>
                <!-- grille lines -->
                <path d="M -9 42 H 9 M -10 50 H 10 M -10 58 H 10 M -9 66 H 9"
                      stroke="{t['metal_dark']}" stroke-width="1.6" stroke-linecap="round" opacity="0.75"/>
                <rect x="-12" y="27" width="24" height="4" rx="2" fill="{SIGNAL}"/>
                <circle class="live" cx="0" cy="13" r="3.2" fill="{SIGNAL}"/>

                <!-- capture rings, leaving the capsule -->
                <g transform="translate(0,53)">
                  <g class="ring" style="animation-delay:2.4s">
                    <circle r="17" fill="none" stroke="{SIGNAL}" stroke-width="1.6"/>
                  </g>
                  <g class="ring" style="animation-delay:3.27s">
                    <circle r="17" fill="none" stroke="{SIGNAL}" stroke-width="1.6"/>
                  </g>
                  <g class="ring" style="animation-delay:4.13s">
                    <circle r="17" fill="none" stroke="{SIGNAL}" stroke-width="1.6"/>
                  </g>
                </g>
              </g>
             </g>
            </g>
          </g>
        </g>
      </g>
    </g>
  </g>
"""


def build(t: dict, bars: str) -> str:
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Praveen Nukilla &#8212; Applied AI &amp; Backend Engineer">
  <defs>
    <style>{css(t)}</style>
  </defs>

  <text x="64" y="92"  class="eyebrow reveal" style="animation-delay:.05s">APPLIED AI &#183; BACKEND ENGINEER</text>
  <text x="64" y="152" class="name name-in">Praveen Nukilla</text>
  <text x="64" y="188" class="role reveal"    style="animation-delay:.28s">Speech-AI systems on GCP + Gemini</text>
  <text x="64" y="222" class="caption reveal" style="animation-delay:.38s">IIIT Allahabad &#183; Final Year &#183; ECE</text>
  <text x="64" y="252" class="caption reveal" style="animation-delay:.48s" fill="{SIGNAL}">400+ DSA solved &#183; live products, real users</text>

  <text x="740" y="28" class="label reveal" style="animation-delay:0s">SIGNAL</text>
  <rect x="740" y="40" width="420" height="200" rx="8" fill="{SIGNAL}" fill-opacity="0.04"/>
  <rect class="panel-border" pathLength="100" x="740" y="40" width="420" height="200" rx="8" fill="none" stroke="{t['stroke']}" stroke-width="1"/>
  <circle cx="762" cy="66" r="4" fill="{SIGNAL}" class="rec-dot"/>
  <text x="774" y="70" class="caption reveal" style="animation-delay:0.65s">REC</text>
  <g class="bars-sway">
      {bars}
  </g>
  <text x="756" y="224" class="caption reveal" style="animation-delay:.9s">44.1kHz &#183; Silero VAD</text>
{boom(t)}</svg>
"""


def main() -> None:
    bars = existing_bars()
    for theme_name, t in THEMES.items():
        out = ASSETS / f"banner-{theme_name}.svg"
        out.write_text(build(t, bars))
        print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
