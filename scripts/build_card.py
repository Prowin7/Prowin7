#!/usr/bin/env python3
"""
Regenerate assets/profile-card.svg — a two-panel GitHub-profile card:
a sidebar (avatar, name, bio, contact, quote) beside a content grid
(neofetch-style "about", languages, stack, contact, live GitHub
stats, tech strip). Static, no animation — this is a card, not the
terminal banner.

Warm off-white throughout, not theme-split: one editorial palette
(three paper tones, tan accent, serif name over sans body) rather
than a light half bolted to a dark half.
"""

import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1400, 830

# Warm off-white throughout: the sidebar is a half-step darker than the
# content field, which is a half-step darker than the panels sitting on it.
# Three tones, no hard black anywhere.
DARK_BG = "#efebe3"      # sidebar
DARK_PANEL2 = "#e7e2d8"  # inset blocks inside the sidebar (quote, social pips)
CREAM = "#f7f5f0"        # content field
CARD = "#fdfcfa"         # panels on the content field
LINE = "#e3ded3"
INK = "#211f1b"
MUTED_INK = "#6f6858"
NAME = "#211f1b"
MUTED = "#6f6858"
SIGNAL = "#a8865c"       # warm tan accent, in place of the old signal red
MONO = "ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"
SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
SERIF = "Georgia, 'Iowan Old Style', 'Times New Roman', serif"

# GitHub sanitizes external <image href> refs out of SVGs it serves, so the
# avatar has to travel as an inline data URI rather than a live URL.
AVATAR_DATA_URI = "data:image/png;base64," + base64.b64encode((ASSETS / "avatar.png").read_bytes()).decode()

SIDEBAR_W = 400

# -- real GitHub stats (api.github.com/users/Prowin7, fetched 2026-08-27) --
STATS = dict(repos=25, followers=0, stars=0, since="2025")


def _wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _icon_react(x, y, s=18):
    return (f'<g transform="translate({x} {y}) scale({s/24})" fill="none" stroke="#61DAFB" stroke-width="1.6">'
            f'<ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/>'
            f'<ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/></g>'
            f'<circle cx="{x + s/2}" cy="{y + s/2}" r="{s*0.09}" fill="#61DAFB"/>')


def _icon_python(x, y, s=18):
    return (f'<g transform="translate({x} {y}) scale({s/24})">'
            '<path d="M8 3h6a3 3 0 013 3v3H9a3 3 0 00-3 3v2H4a3 3 0 01-3-3V8a5 5 0 015-5z" fill="#3776AB"/>'
            '<circle cx="7" cy="6" r="1" fill="#fff"/>'
            '<path d="M16 21h-6a3 3 0 01-3-3v-3h8a3 3 0 003-3V10h2a3 3 0 013 3v3a5 5 0 01-5 5z" fill="#FFD43B"/>'
            '<circle cx="17" cy="18" r="1" fill="#0d1117"/></g>')


def _icon_node(x, y, s=18):
    return (f'<g transform="translate({x} {y}) scale({s/24})" fill="none" stroke="#539E43" stroke-width="1.8">'
            '<path d="M12 2l8 4.5v11L12 22l-8-4.5v-11z"/></g>'
            f'<circle cx="{x + s/2}" cy="{y + s/2}" r="{s*0.11}" fill="#539E43"/>')


def _icon_docker(x, y, s=18):
    return (f'<g transform="translate({x} {y}) scale({s/24})" fill="#2496ED">'
            '<rect x="5" y="8" width="3" height="3"/><rect x="9" y="8" width="3" height="3"/>'
            '<rect x="13" y="8" width="3" height="3"/><rect x="9" y="4" width="3" height="3"/>'
            '<path d="M2 14c1-2 3-3 5-3h10c2 0 3 1 4 3-1 3-4 5-9 5S3 17 2 14z"/></g>')


def _icon_gcp(x, y, s=18):
    return (f'<g transform="translate({x} {y}) scale({s/24})" fill="#4285F4">'
            '<path d="M15 8a5 5 0 00-9.6 1.8A4 4 0 006 18h9a4.5 4.5 0 000-9 5 5 0 000-1z"/></g>')


def _icon_git(x, y, s=18):
    return (f'<g transform="translate({x} {y}) scale({s/24})" fill="none" stroke="#F05033" stroke-width="1.6">'
            '<circle cx="6" cy="6" r="2" fill="#F05033" stroke="none"/>'
            '<circle cx="6" cy="18" r="2" fill="#F05033" stroke="none"/>'
            '<circle cx="17" cy="12" r="2" fill="#F05033" stroke="none"/>'
            '<path d="M6 8v8M6 12h9a2 2 0 002-2"/></g>')


def _badge(x, y, label, sub, w=118):
    """A rounded letter-badge pill for languages that have no brand mark."""
    return f"""
    <rect x="{x}" y="{y}" width="{w}" height="34" rx="8" fill="#fff" stroke="{LINE}"/>
    <rect x="{x+8}" y="{y+7}" width="20" height="20" rx="4" fill="{INK}"/>
    <text x="{x+18}" y="{y+21}" text-anchor="middle" font-family="{MONO}" font-size="9.5" font-weight="700" fill="#fff">{label}</text>
    <text x="{x+36}" y="{y+22}" font-family="{MONO}" font-size="12.5" fill="{INK}">{sub}</text>"""


_ICON_PATHS = {
    # each drawn inside a 24x24 box, stroked not filled, so one stroke colour
    # recolours the whole set
    "pin": '<path d="M12 21s7-6.3 7-11a7 7 0 10-14 0c0 4.7 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/>',
    "cal": '<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "mail": '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M3 7l9 6 9-6"/>',
    "link": '<path d="M10 14a4 4 0 006 .5l3-3a4 4 0 10-5.7-5.7L11.5 7"/>'
            '<path d="M14 10a4 4 0 00-6-.5l-3 3A4 4 0 1010.7 18l1.8-1.8"/>',
    "github": '<path d="M12 2.5a9.5 9.5 0 00-3 18.5c.5.1.7-.2.7-.5v-1.7c-2.6.6-3.2-1.2-3.2-1.2-.4-1.1-1-1.4-1-1.4-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.3-2.1-.2-4.3-1-4.3-4.6 0-1 .4-1.9 1-2.5-.1-.3-.4-1.3.1-2.6 0 0 .8-.3 2.6 1a9 9 0 014.7 0c1.8-1.3 2.6-1 2.6-1 .5 1.3.2 2.3.1 2.6.6.6 1 1.5 1 2.5 0 3.6-2.2 4.4-4.3 4.6.3.3.6.9.6 1.8v2.7c0 .3.2.6.7.5A9.5 9.5 0 0012 2.5z"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7.5 10v7M7.5 7.2v.1M11.5 17v-4a2.5 2.5 0 015 0v4"/>',
    # panel headers
    "person": '<circle cx="12" cy="8" r="3.8"/><path d="M4.5 20a7.5 7.5 0 0115 0"/>',
    "chevrons": '<path d="M4 7l5 5-5 5M12.5 17H20"/>',
    "layers": '<path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12.5l9 4.5 9-4.5"/>',
    "send": '<path d="M21 3L10.5 13.5M21 3l-6.8 18-3.7-7.5L3 9.8z"/>',
    "chart": '<path d="M4 20V4"/><path d="M4 20h16"/><path d="M8 17v-5M12.5 17V8M17 17v-7"/>',
}


def _line_icon(kind: str, x: float, y: float, size: int = 18, stroke: str | None = None) -> str:
    """One 24x24 stroked glyph, scaled to `size` and placed with its top-left at (x, y)."""
    return (f'<g transform="translate({x} {y}) scale({size/24:.4f})" fill="none" '
            f'stroke="{stroke or SIGNAL}" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round">{_ICON_PATHS[kind]}</g>')


def sidebar() -> str:
    bio_lines = _wrap(
        "Building production speech-AI systems on GCP: real-time audio "
        "capture, Gemini-scored assessment, Firestore-backed pipelines "
        "serving paying users internationally.", 34)
    bio_svg = "\n    ".join(
        f'<text x="40" y="{356 + i*22}" font-family="{SANS}" font-size="14" fill="{MUTED}">{l}</text>'
        for i, l in enumerate(bio_lines))

    rows = [
        ("pin", "Prayagraj, India"),
        ("cal", "IIIT Allahabad · Final Year"),
        ("mail", "nukillapraveen1@gmail.com"),
        ("link", "praveennukilla.dev"),
    ]
    y0 = 356 + len(bio_lines) * 22 + 34
    meta_svg = []
    for i, (kind, label) in enumerate(rows):
        y = y0 + i * 32
        meta_svg.append(f'{_line_icon(kind, 40, y - 14)}'
                         f'<text x="66" y="{y}" font-family="{SANS}" font-size="14" fill="{MUTED}">{label}</text>')
    meta_svg = "\n    ".join(meta_svg)

    social_y = y0 + len(rows) * 32 + 28
    social_svg = "\n    ".join(
        f'<rect x="{40 + i*46}" y="{social_y-18}" width="36" height="36" rx="10" fill="{DARK_PANEL2}"/>'
        f'{_line_icon(kind, 46 + i*46, social_y - 12, stroke=INK)}'
        for i, kind in enumerate(["github", "linkedin", "mail"]))

    quote_y = social_y + 30
    return f"""
  <rect x="0" y="0" width="{SIDEBAR_W}" height="{H}" fill="{DARK_BG}"/>

  <circle cx="150" cy="140" r="78" fill="none" stroke="{LINE}" stroke-width="1.2"/>
  <clipPath id="avatarClip"><circle cx="150" cy="140" r="68"/></clipPath>
  <image href="{AVATAR_DATA_URI}" x="82" y="72" width="136" height="136" clip-path="url(#avatarClip)"/>
  <circle cx="205" cy="195" r="9" fill="{SIGNAL}"/>

  <text x="40" y="256" font-family="{SERIF}" font-size="30" fill="{NAME}">Praveen Nukilla</text>
  <text x="40" y="284" font-family="{SANS}" font-size="15" fill="{SIGNAL}">Applied AI &amp; Backend Engineer</text>

  {bio_svg}

  <line x1="40" y1="{y0-22}" x2="{SIDEBAR_W-40}" y2="{y0-22}" stroke="{LINE}" stroke-width="1"/>
  {meta_svg}

  <line x1="40" y1="{social_y-34}" x2="{SIDEBAR_W-40}" y2="{social_y-34}" stroke="{LINE}" stroke-width="1"/>
  {social_svg}

  <rect x="40" y="{quote_y}" width="{SIDEBAR_W-80}" height="100" rx="10" fill="{DARK_PANEL2}"/>
  <text x="58" y="{quote_y+34}" font-family="{SERIF}" font-size="30" fill="{SIGNAL}" opacity="0.75">&#8220;</text>
  <text x="58" y="{quote_y+52}" font-family="{SANS}" font-size="13.5" fill="{NAME}">Code is like humor. When you have</text>
  <text x="58" y="{quote_y+72}" font-family="{SANS}" font-size="13.5" fill="{NAME}">to explain it, it's bad.</text>
  <text x="{SIDEBAR_W-58}" y="{quote_y+92}" text-anchor="end" font-family="{SANS}" font-size="12.5" fill="{SIGNAL}">&#8212; Cory House</text>
"""


def panel_box(x, y, w, h, title, icon_kind="pin") -> str:
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{CARD}" stroke="{LINE}"/>'
            f'{_line_icon(icon_kind, x + 24, y + 18, size=19, stroke=INK)}'
            f'<text x="{x+52}" y="{y+33}" font-family="{SANS}" font-size="13.5" font-weight="700" '
            f'letter-spacing="0.1em" fill="{INK}">{title}</text>')


def kv_rows(x, y, rows, key_w=88) -> str:
    """Label / colon / value, with a hairline running down the bullet column —
    the reference's quiet spine holding the rows together."""
    out = []
    if len(rows) > 1:
        out.append(f'<line x1="{x}" y1="{y-8}" x2="{x}" y2="{y + (len(rows)-1)*29 - 4}" '
                    f'stroke="{LINE}" stroke-width="1"/>')
    for i, (k, v) in enumerate(rows):
        ry = y + i * 29
        out.append(f'<circle cx="{x}" cy="{ry-5}" r="3" fill="{SIGNAL}" opacity="0.55"/>'
                    f'<text x="{x+16}" y="{ry}" font-family="{SANS}" font-size="13.5" fill="{MUTED_INK}">{k}</text>'
                    f'<text x="{x+key_w}" y="{ry}" font-family="{SANS}" font-size="13.5" fill="{MUTED_INK}">:</text>'
                    f'<text x="{x+key_w+20}" y="{ry}" font-family="{SANS}" font-size="13.5" fill="{INK}">{v}</text>')
    return "\n    ".join(out)


def still_life(x, y, w, h) -> str:
    """A quiet desk scene — leafy branch in a vase, stacked books, a steaming
    mug — sitting on a lit surface with long soft shadows. Drawn in the card's
    own sage/tan/clay tones so it reads as part of the palette, not clip art."""
    sage, sage_d, clay, paper, shadow = "#9aa68f", "#7e8b74", "#c8a882", "#efeae0", "#dfd9cc"
    base = y + h * 0.78  # the tabletop line everything stands on

    leaves = []
    for i, (ang, ll) in enumerate([(-58, 30), (-28, 36), (4, 34), (34, 30), (-42, 24), (18, 24)]):
        lx, ly = x + w * 0.24, base - 104 + i * 9
        leaves.append(f'<g transform="translate({lx:.1f} {ly:.1f}) rotate({ang})">'
                       f'<ellipse cx="{ll/2:.1f}" cy="0" rx="{ll/2:.1f}" ry="6.5" '
                       f'fill="{sage if i % 2 else sage_d}" opacity="0.85"/></g>')

    return f"""
    <clipPath id="stillClip"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{paper}"/>
    <g clip-path="url(#stillClip)">
      <!-- window light falling across the back wall -->
      <path d="M{x} {y} L{x+w*0.42} {y} L{x+w*0.66} {base} L{x} {base} Z" fill="#f7f4ec"/>
      <path d="M{x+w*0.46} {y} L{x+w*0.6} {y} L{x+w*0.82} {base} L{x+w*0.68} {base} Z" fill="#f7f4ec" opacity="0.7"/>
      <rect x="{x}" y="{base}" width="{w}" height="{y+h-base}" fill="{shadow}"/>

      <!-- branch: stems then leaves, so leaves sit on top of the stems -->
      <g stroke="{sage_d}" stroke-width="1.6" fill="none" stroke-linecap="round">
        <path d="M{x+w*0.24} {base-30} C{x+w*0.23} {base-70} {x+w*0.22} {base-90} {x+w*0.2} {base-112}"/>
        <path d="M{x+w*0.24} {base-40} C{x+w*0.27} {base-70} {x+w*0.3} {base-84} {x+w*0.33} {base-98}"/>
      </g>
      {''.join(leaves)}

      <!-- vase -->
      <path d="M{x+w*0.19} {base-34} q{w*0.05} -14 {w*0.1} 0 l0 30 q0 6 -6 6 h-{w*0.075} q-6 0 -6 -6 z"
            fill="{paper}" stroke="{shadow}" stroke-width="1.4"/>

      <!-- stacked books -->
      <g stroke="{shadow}" stroke-width="1.2">
        <rect x="{x+w*0.34}" y="{base-30}" width="{w*0.3}" height="11" rx="2" fill="{paper}"/>
        <rect x="{x+w*0.36}" y="{base-19}" width="{w*0.3}" height="11" rx="2" fill="#e6e0d3"/>
        <rect x="{x+w*0.35}" y="{base-8}" width="{w*0.31}" height="10" rx="2" fill="{sage}" opacity="0.55"/>
      </g>

      <!-- mug, with a curl of steam -->
      <path d="M{x+w*0.75} {base-38} h{w*0.13} v26 q0 10 -10 10 h-{w*0.055} q-10 0 -10 -10 z"
            fill="{paper}" stroke="{shadow}" stroke-width="1.4"/>
      <path d="M{x+w*0.88} {base-30} q12 0 12 9 t-12 9" fill="none" stroke="{shadow}" stroke-width="1.4"/>
      <path d="M{x+w*0.755} {base-38} h{w*0.12} v5 h-{w*0.12} z" fill="{clay}" opacity="0.55"/>
      <path d="M{x+w*0.79} {base-48} q-5 -8 0 -15 q5 -7 0 -14" fill="none" stroke="{shadow}" stroke-width="1.5" stroke-linecap="round"/>

      <!-- contact shadows pooling to the right of each object -->
      <g fill="{shadow}" opacity="0.55">
        <ellipse cx="{x+w*0.28}" cy="{base+3}" rx="{w*0.1}" ry="4"/>
        <ellipse cx="{x+w*0.52}" cy="{base+4}" rx="{w*0.17}" ry="4"/>
        <ellipse cx="{x+w*0.82}" cy="{base+3}" rx="{w*0.09}" ry="4"/>
      </g>
    </g>"""


def stats_ring(cx, cy, r=38) -> str:
    """A donut gauge with the commit sparkline nested inside it, echoing the
    reference's stats dial."""
    pts = [(0, 26), (12, 20), (24, 23), (36, 8), (48, 15), (60, 3), (72, 10)]
    sx, sy, sw = cx - 26, cy - 12, 52
    path = "M" + " L".join(f"{sx+px*(sw/72):.1f} {sy+26-py:.1f}" for px, py in pts)
    circ = 2 * 3.14159 * r
    return f"""
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="9"/>
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SIGNAL}" stroke-width="9"
            stroke-linecap="round" stroke-dasharray="{circ*0.68:.1f} {circ:.1f}"
            transform="rotate(-90 {cx} {cy})"/>
    <path d="{path}" fill="none" stroke="{SIGNAL}" stroke-width="1.8" stroke-linejoin="round"/>
    <circle cx="{sx+72*(sw/72):.1f}" cy="{sy+26-10:.1f}" r="2.6" fill="{SIGNAL}"/>"""


def content() -> str:
    L = SIDEBAR_W + 48
    R = W - 48
    top = 40

    out = [f'<rect x="{SIDEBAR_W}" y="0" width="{W-SIDEBAR_W}" height="{H}" fill="{CREAM}"/>']

    row1_y = top
    row1_h = 250
    about_w = (R - L) * 0.56
    out.append(panel_box(L, row1_y, about_w, row1_h, "ABOUT ME", "person"))
    about_rows = [
        ("OS", "macOS, Ubuntu (GCP)"),
        ("Host", "Applied AI &amp; Backend Eng."),
        ("Kernel", "Prayagraj, India"),
        ("IDE", "VS Code"),
        ("Shell", "zsh"),
        ("Education", "B.Tech ECE, IIIT-A, 2026"),
    ]
    out.append(kv_rows(L + 24, row1_y + 78, about_rows))

    art_x = L + about_w + 24
    out.append(still_life(art_x, row1_y, R - art_x, row1_h))

    row2_y = row1_y + row1_h + 24
    row2_h = 150
    half = (R - L - 24) / 2
    out.append(panel_box(L, row2_y, half, row2_h, "LANGUAGES", "chevrons"))
    out.append(kv_rows(L + 24, row2_y + 78, [
        ("Programming", "TypeScript, Python, C++"),
        ("Human", "English, Hindi"),
    ], key_w=100))

    stack_x = L + half + 24
    out.append(panel_box(stack_x, row2_y, half, row2_h, "STACK", "layers"))
    out.append(kv_rows(stack_x + 24, row2_y + 78, [
        ("Mobile", "Swift (native iOS)"),
        ("Web", "React, Node/Express"),
        ("AI/ML", "Gemini, PyTorch, HF"),
    ], key_w=80))

    row3_y = row2_y + row2_h + 24
    row3_h = 170
    out.append(panel_box(L, row3_y, half, row3_h, "CONTACT", "send"))
    out.append(kv_rows(L + 24, row3_y + 78, [
        ("Email", "nukillapraveen1@gmail.com"),
        ("Portfolio", "praveennukilla.dev"),
        ("LinkedIn", "praveen-nukilla-753a2a334"),
        ("LeetCode", "Praveen763"),
    ], key_w=90))

    gh_x = stack_x
    out.append(panel_box(gh_x, row3_y, half, row3_h, "GITHUB STATS", "chart"))
    out.append(kv_rows(gh_x + 24, row3_y + 78, [
        ("Repositories", str(STATS["repos"])),
        ("Followers", str(STATS["followers"])),
        ("Member since", STATS["since"]),
    ], key_w=110))
    out.append(stats_ring(gh_x + half - 78, row3_y + 108))

    row4_y = row3_y + row3_h + 24
    row4_h = 78
    out.append(f'<rect x="{L}" y="{row4_y}" width="{R-L}" height="{row4_h}" rx="14" fill="{CARD}" stroke="{LINE}"/>')
    out.append(f'<text x="{L+26}" y="{row4_y+row4_h/2+4}" font-family="{SANS}" font-size="11.5" font-weight="700" '
                f'letter-spacing="0.12em" fill="{MUTED_INK}">TECHNOLOGIES</text>')
    # divider between the label and the mark strip, as in the reference
    out.append(f'<line x1="{L+150}" y1="{row4_y+16}" x2="{L+150}" y2="{row4_y+row4_h-16}" stroke="{LINE}" stroke-width="1"/>')

    marks = [("React", _icon_react), ("Python", _icon_python), ("Node.js", _icon_node),
             ("Docker", _icon_docker), ("GCP", _icon_gcp), ("Git", _icon_git)]
    step = (R - L - 176) / len(marks)
    for i, (lbl, draw) in enumerate(marks):
        mx = L + 176 + i * step
        my = row4_y + row4_h / 2
        out.append(f'<rect x="{mx}" y="{my-15}" width="30" height="30" rx="8" fill="{CREAM}" stroke="{LINE}"/>')
        out.append(draw(mx + 7, my - 8, 16))
        out.append(f'<text x="{mx+40}" y="{my+5}" font-family="{SANS}" font-size="13" fill="{INK}">{lbl}</text>')

    return "\n".join(out)


def build_card() -> str:
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Praveen Nukilla profile card">
  <defs>
    <style>text {{ font-family: {SANS}; }}</style>
  </defs>
{sidebar()}
{content()}
</svg>
"""


def main() -> None:
    out = ASSETS / "profile-card.svg"
    out.write_text(build_card())
    print(f"wrote {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
