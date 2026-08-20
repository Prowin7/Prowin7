#!/usr/bin/env python3
"""
Regenerate assets/banner-dark.svg and assets/banner-light.svg.

The banner keeps the original 1200x280 "signal" composition and adds a 100px
stage strip underneath (total 1200x380) where a small articulated desk lamp
hops in, lands with a squash, tilts its head up at the name and switches on a
light cone that washes over the text.

The waveform bars in the SIGNAL panel are lifted verbatim out of the existing
banner-dark.svg so the panel keeps its exact shape across regenerations.

Motion follows the classic animation principles rather than UI easing:
  - anticipation + arc on the hop
  - squash on contact, stretch in the air
  - a contact shadow that scales inversely with height (reads as weight)
  - overshoot-and-settle on the landing and on the head turn
  - follow-through: the head keeps a slow idle bob after the pose lands

Everything is expressed as CSS keyframes inside the SVG. GitHub serves these
files through <img>, which runs CSS animations but no script, so no SMIL and
no JS is used. Every animated element resolves to its *final* pose when
transforms are removed, so the prefers-reduced-motion block can simply switch
animations off and still show a composed frame.
"""

import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1200, 420
FLOOR_Y = 396          # ground line the lamp stands on
LAMP_SCALE = 1.4       # the lamp is drawn at unit scale and sized here
LAMP_X = 604           # where the lamp comes to rest (clear of the text column)
HOP_FROM = -740        # offscreen-left start, expressed as an offset from LAMP_X

SIGNAL = "#d11440"
WARM = "#ffcf8a"
WARM_LIGHT = "#e8a94e"   # the pale warm reads as nothing on a white plate

THEMES = {
    "dark": dict(
        name="#e6edf3", muted="#8b949e", stroke="#30363d",
        plate_top="#0d1117", plate_bot="#161b22", plate_op="0.85",
        floor="#30363d", lamp="#c9d1d9", lamp_dark="#8b949e",
        cone_op="0.30", glow_op="0.55", shadow="#010409", shadow_op="0.55", warm=WARM,
    ),
    "light": dict(
        name="#0d1117", muted="#57606a", stroke="#d0d7de",
        plate_top="#ffffff", plate_bot="#f6f8fa", plate_op="0.9",
        floor="#d0d7de", lamp="#57606a", lamp_dark="#8c959f",
        cone_op="0.32", glow_op="0.45", shadow="#57606a", shadow_op="0.28", warm=WARM_LIGHT,
    ),
}



def existing_bars() -> str:
    """Pull the waveform <rect class="bar"> lines out of the current dark banner."""
    src = (ASSETS / "banner-dark.svg").read_text()
    bars = [ln.strip() for ln in src.splitlines() if 'class="bar"' in ln]
    if not bars:
        raise SystemExit("no waveform bars found in assets/banner-dark.svg")
    return "\n    ".join(bars)


def css(t: dict) -> str:
    return f"""
      .eyebrow {{ font: 600 13px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; letter-spacing: .18em; fill: {SIGNAL}; }}
      .name    {{ font: 700 46px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['name']}; }}
      .role    {{ font: 400 20px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['muted']}; }}
      .caption {{ font: 400 13px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; fill: {t['muted']}; letter-spacing: .02em; }}
      .label   {{ font: 600 11px ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace; letter-spacing: .2em; fill: {t['muted']}; }}

      /* Every animated element below rests at its FINAL state and animates in
         from a keyframed start with fill-mode backwards. Renderers that decline
         to run animations in an img element (a cached decode, a converter, a reader
         view) then show the composed banner instead of an empty frame. */
      .reveal {{ animation: revealText .6s cubic-bezier(.16,1,.3,1) backwards; }}
      @keyframes revealText {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

      /* the name lands with a small overshoot instead of a flat fade */
      .name-in {{
        transform-box: fill-box; transform-origin: left bottom;
        animation: nameIn .72s cubic-bezier(.22,1.42,.36,1) .16s backwards,
                   nameLit 2.6s ease-in-out 3.25s infinite;
      }}
      @keyframes nameIn {{
        0%   {{ opacity: 0; transform: translateY(14px) scale(.94, 1.06); }}
        60%  {{ opacity: 1; transform: translateY(0)    scale(1.02, .98); }}
        100% {{ opacity: 1; transform: translateY(0)    scale(1, 1); }}
      }}
      /* warm bounce light off the lamp, only once the lamp is lit */
      @keyframes nameLit {{
        0%, 100% {{ filter: none; }}
        45%      {{ filter: drop-shadow(0 0 14px rgba(255,207,138,.38)); }}
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

      /* ---------- the lamp ---------- */

      /* horizontal travel: four hops, ground-to-ground, easing out of each push */
      .hop-x {{ animation: hopX 1.72s linear .70s backwards; }}
      @keyframes hopX {{
        0%   {{ transform: translateX({HOP_FROM}px); }}
        25%  {{ transform: translateX({HOP_FROM * 0.62:.0f}px); }}
        50%  {{ transform: translateX({HOP_FROM * 0.34:.0f}px); }}
        75%  {{ transform: translateX({HOP_FROM * 0.13:.0f}px); }}
        100% {{ transform: translateX(0); }}
      }}

      /* vertical arc, kept as its own layer so height and distance stay independent */
      .hop-y {{ animation: hopY 1.72s .70s backwards; }}
      @keyframes hopY {{
        0%,  25%, 50%, 75%, 100% {{ transform: translateY(0);     animation-timing-function: cubic-bezier(.2,.7,.4,1); }}
        12.5%                    {{ transform: translateY(-26px); animation-timing-function: cubic-bezier(.6,0,.8,.35); }}
        37.5%                    {{ transform: translateY(-23px); animation-timing-function: cubic-bezier(.6,0,.8,.35); }}
        62.5%                    {{ transform: translateY(-19px); animation-timing-function: cubic-bezier(.6,0,.8,.35); }}
        87.5%                    {{ transform: translateY(-14px); animation-timing-function: cubic-bezier(.6,0,.8,.35); }}
      }}

      /* squash on every contact, stretch at the top of every arc, then settle */
      .squash {{ animation: squash 2.16s .70s backwards; }}
      @keyframes squash {{
        0%    {{ transform: scale(1.16, .84); }}
        6%    {{ transform: scale(.93, 1.07); }}
        16%   {{ transform: scale(1, 1); }}
        20%   {{ transform: scale(1.14, .86); }}
        26%   {{ transform: scale(.94, 1.06); }}
        36%   {{ transform: scale(1, 1); }}
        40%   {{ transform: scale(1.12, .88); }}
        46%   {{ transform: scale(.95, 1.05); }}
        56%   {{ transform: scale(1, 1); }}
        60%   {{ transform: scale(1.10, .90); }}
        66%   {{ transform: scale(.96, 1.04); }}
        76%   {{ transform: scale(1, 1); }}
        80%   {{ transform: scale(1.18, .82); }}   /* the landing, the biggest hit */
        87%   {{ transform: scale(.96, 1.05); }}
        94%   {{ transform: scale(1.02, .98); }}
        100%  {{ transform: scale(1, 1); }}
      }}

      /* the arms wind up on take-off and unfold as the lamp settles */
      .lower {{ animation: lowerArm 2.16s cubic-bezier(.22,1.2,.36,1) .70s backwards; }}
      @keyframes lowerArm {{
        0%   {{ transform: rotate(24deg); }}
        50%  {{ transform: rotate(14deg); }}
        80%  {{ transform: rotate(-7deg); }}
        90%  {{ transform: rotate(3deg); }}
        100% {{ transform: rotate(0deg); }}
      }}
      .upper {{ animation: upperArm 2.16s cubic-bezier(.22,1.2,.36,1) .70s backwards; }}
      @keyframes upperArm {{
        0%   {{ transform: rotate(-34deg); }}
        50%  {{ transform: rotate(-20deg); }}
        80%  {{ transform: rotate(11deg); }}
        90%  {{ transform: rotate(-5deg); }}
        100% {{ transform: rotate(0deg); }}
      }}

      /* the head turn is the story beat: it arrives late and overshoots */
      .head {{ animation: headTurn .62s cubic-bezier(.34,1.5,.5,1) 2.46s backwards; }}
      @keyframes headTurn {{
        0%   {{ transform: rotate(52deg); }}
        100% {{ transform: rotate(0deg); }}
      }}
      /* follow-through: a slow idle bob, on its own layer so it can't fight the turn */
      .head-bob {{ animation: headBob 4.2s ease-in-out 3.2s infinite; }}
      @keyframes headBob {{
        0%, 100% {{ transform: rotate(0deg); }}
        50%      {{ transform: rotate(-3.2deg); }}
      }}

      /* contact shadow: wide and dark on the ground, small and faint in the air */
      .shadow {{ animation: shadowHop 2.16s .70s backwards; }}
      @keyframes shadowHop {{
        0%,  20%, 40%, 60%, 80%, 100% {{ opacity: {t['shadow_op']}; transform: scale(1, 1); }}
        6%,  26%, 46%, 66%            {{ opacity: {float(t['shadow_op']) * 0.4:.2f}; transform: scale(.62, .62); }}
        86%                           {{ opacity: {t['shadow_op']}; transform: scale(1.12, 1); }}
      }}

      /* the bulb clicks on after the head has finished turning */
      .glow {{ animation: bulbOn .5s ease-out 2.86s backwards, bulbBreathe 3.4s ease-in-out 3.4s infinite; }}
      @keyframes bulbOn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      @keyframes bulbBreathe {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .78; }} }}

      .cone {{ animation: coneOn .55s ease-out 2.90s backwards, coneFlicker 5.5s ease-in-out 3.5s infinite; }}
      @keyframes coneOn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      @keyframes coneFlicker {{ 0%, 100% {{ opacity: 1; }} 42% {{ opacity: .82; }} 47% {{ opacity: .95; }} }}

      @media (prefers-reduced-motion: reduce) {{
        .bar, .reveal, .name-in, .panel-border, .rec-dot,
        .hop-x, .hop-y, .squash, .lower, .upper, .head, .head-bob,
        .shadow, .glow, .cone {{
          animation: none !important;
          opacity: 1 !important;
          transform: none !important;
          filter: none !important;
          stroke-dashoffset: 0 !important;
        }}
        .shadow {{ opacity: {t['shadow_op']} !important; }}
      }}
"""


def lamp(t: dict) -> str:
    """
    Articulated desk lamp, drawn in local coordinates with the base pivot at 0,0.

    Joints are nested translate/rotate group pairs rather than CSS
    transform-origin, so the rotation centres do not depend on transform-box
    support. Each rotating group turns about its own local origin.
    """
    return f"""
  <!-- stage -->
  <rect x="0" y="280" width="{W}" height="{H - 280}" fill="url(#plate)" opacity="{t['plate_op']}"/>
  <rect x="0" y="{FLOOR_Y}" width="{W}" height="1" fill="{t['floor']}" opacity="0.9"/>

  <!-- contact shadow: shares the hop's horizontal travel but never leaves the ground -->
  <g transform="translate({LAMP_X},{FLOOR_Y})">
    <g class="hop-x">
      <g class="shadow">
        <ellipse cx="{6 * LAMP_SCALE:.0f}" cy="1" rx="{34 * LAMP_SCALE:.0f}" ry="{6 * LAMP_SCALE:.0f}" fill="url(#contact)" opacity="{t['shadow_op']}"/>
      </g>
    </g>
  </g>

  <!-- lamp -->
  <g transform="translate({LAMP_X},{FLOOR_Y})">
    <g class="hop-x">
      <g class="hop-y">
       <g transform="scale({LAMP_SCALE})">
        <g class="squash">
          <!-- base -->
          <path d="M -20 0 L 20 0 L 15 -7 L -15 -7 Z" fill="{t['lamp']}"/>
          <ellipse cx="0" cy="0" rx="21" ry="4" fill="{t['lamp_dark']}"/>
          <!-- lower arm, pivots on the base -->
          <g transform="rotate(-14)">
           <g class="lower">
            <rect x="-2" y="-34" width="4" height="34" rx="2" fill="{t['lamp']}"/>
            <circle cx="0" cy="-34" r="3.4" fill="{t['lamp_dark']}"/>
            <!-- upper arm, pivots on the elbow -->
            <g transform="translate(0,-34)">
              <g transform="rotate(30)">
               <g class="upper">
                <rect x="-2" y="-30" width="4" height="30" rx="2" fill="{t['lamp']}"/>
                <circle cx="0" cy="-30" r="3.4" fill="{t['lamp_dark']}"/>
                <!-- head, pivots on the neck -->
                <g transform="translate(0,-30)">
                  <g class="head">
                    <g class="head-bob">
                      <!-- shade points up and to the left, at the name -->
                      <g transform="rotate(30)">
                        <!-- light cone, drawn behind the shade -->
                        <g class="cone">
                          <path d="M -7 -6 L -215 -84 L -215 76 L -7 6 Z" fill="url(#cone)"/>
                        </g>
                        <path d="M 2 -11 L 2 11 L -15 17 L -15 -17 Z" fill="{SIGNAL}"/>
                        <path d="M 2 -11 L 2 11 L 7 8 L 7 -8 Z" fill="{t['lamp_dark']}"/>
                        <g class="glow">
                          <ellipse cx="-15" cy="0" rx="7" ry="15" fill="url(#bulb)"/>
                          <ellipse cx="-30" cy="0" rx="26" ry="30" fill="url(#bulb)" opacity="0.45"/>
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
        </g>
       </g>
      </g>
    </g>
  </g>
"""


def build(theme_name: str, t: dict, bars: str) -> str:
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Praveen Nukilla &#8212; Applied AI &amp; Backend Engineer">
  <defs>
    <linearGradient id="plate" x1="0" y1="280" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{t['plate_top']}" stop-opacity="0"/>
      <stop offset="1" stop-color="{t['plate_bot']}"/>
    </linearGradient>
    <radialGradient id="contact">
      <stop offset="0" stop-color="{t['shadow']}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{t['shadow']}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="bulb">
      <stop offset="0" stop-color="{t['warm']}" stop-opacity="{t['glow_op']}"/>
      <stop offset="1" stop-color="{t['warm']}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="cone" x1="0" y1="0" x2="-215" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{t['warm']}" stop-opacity="{t['cone_op']}"/>
      <stop offset="1" stop-color="{t['warm']}" stop-opacity="0"/>
    </linearGradient>
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
    {bars}
  <text x="756" y="224" class="caption reveal" style="animation-delay:.9s">44.1kHz &#183; Silero VAD</text>
{lamp(t)}</svg>
"""


def main() -> None:
    bars = existing_bars()
    for theme_name, t in THEMES.items():
        out = ASSETS / f"banner-{theme_name}.svg"
        out.write_text(build(theme_name, t, bars))
        print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
