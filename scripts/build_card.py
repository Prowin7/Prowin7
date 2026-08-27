#!/usr/bin/env python3
"""
Regenerate assets/profile-card.svg — a two-panel GitHub-profile card:
a dark sidebar (avatar, name, bio, contact, quote) beside a cream
content grid (neofetch-style "about", languages, stack, contact,
live GitHub stats, tech strip). Static, no animation — this is a
card, not the terminal banner.

Fixed two-tone design (not theme-split): matches the reference layout
exactly rather than adapting per GitHub light/dark mode.
"""

import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

W, H = 1400, 784

DARK_BG = "#0d1117"
DARK_PANEL2 = "#161b22"
CREAM = "#f4efe6"
CARD = "#faf7f0"
LINE = "#ddd6c6"
INK = "#1c1a17"
MUTED_INK = "#6b6558"
NAME = "#e6edf3"
MUTED = "#8b949e"
SIGNAL = "#d11440"
MONO = "ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"

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


def sidebar() -> str:
    bio_lines = _wrap(
        "Building production speech-AI systems on GCP: real-time audio "
        "capture, Gemini-scored assessment, Firestore-backed pipelines "
        "serving paying users internationally.", 34)
    bio_svg = "\n    ".join(
        f'<text x="40" y="{356 + i*20}" font-family="{MONO}" font-size="13" fill="{MUTED}">{l}</text>'
        for i, l in enumerate(bio_lines))

    rows = [
        ("loc", "Prayagraj, India"),
        ("cal", "IIIT Allahabad · Final Year"),
        ("mail", "nukillapraveen1@gmail.com"),
        ("link", "praveennukilla.dev"),
    ]
    y0 = 356 + len(bio_lines) * 20 + 30
    meta_svg = []
    for i, (_, label) in enumerate(rows):
        y = y0 + i * 30
        meta_svg.append(f'<circle cx="46" cy="{y-5}" r="3" fill="{SIGNAL}"/>'
                         f'<text x="60" y="{y}" font-family="{MONO}" font-size="13" fill="{MUTED}">{label}</text>')
    meta_svg = "\n    ".join(meta_svg)

    social_y = y0 + len(rows) * 30 + 28
    socials = ["GH", "in", "@"]
    social_svg = "\n    ".join(
        f'<circle cx="{40 + i*46 + 18}" cy="{social_y}" r="18" fill="{DARK_PANEL2}" stroke="{MUTED}" stroke-width="1"/>'
        f'<text x="{40 + i*46 + 18}" y="{social_y+5}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{NAME}">{s}</text>'
        for i, s in enumerate(socials))

    quote_y = social_y + 30
    return f"""
  <rect x="0" y="0" width="{SIDEBAR_W}" height="{H}" fill="{DARK_BG}"/>

  <circle cx="150" cy="140" r="72" fill="{DARK_PANEL2}"/>
  <clipPath id="avatarClip"><circle cx="150" cy="140" r="68"/></clipPath>
  <image href="{AVATAR_DATA_URI}" x="82" y="72" width="136" height="136" clip-path="url(#avatarClip)"/>
  <circle cx="150" cy="140" r="68" fill="none" stroke="{SIGNAL}" stroke-width="2"/>
  <circle cx="202" cy="192" r="10" fill="#3fb950" stroke="{DARK_BG}" stroke-width="3"/>

  <text x="40" y="252" font-family="{MONO}" font-size="26" font-weight="700" fill="{NAME}">Praveen Nukilla</text>
  <text x="40" y="278" font-family="{MONO}" font-size="15" fill="{SIGNAL}">Applied AI &amp; Backend Engineer</text>

  {bio_svg}

  <line x1="40" y1="{y0-18}" x2="{SIDEBAR_W-40}" y2="{y0-18}" stroke="{DARK_PANEL2}" stroke-width="1"/>
  {meta_svg}

  <line x1="40" y1="{social_y-30}" x2="{SIDEBAR_W-40}" y2="{social_y-30}" stroke="{DARK_PANEL2}" stroke-width="1"/>
  {social_svg}

  <rect x="40" y="{quote_y}" width="{SIDEBAR_W-80}" height="90" rx="10" fill="{DARK_PANEL2}"/>
  <text x="58" y="{quote_y+30}" font-family="{MONO}" font-size="26" fill="{SIGNAL}" opacity="0.6">&#8220;</text>
  <text x="58" y="{quote_y+40}" font-family="{MONO}" font-size="12" fill="{NAME}">Code is like humor. When you have</text>
  <text x="58" y="{quote_y+58}" font-family="{MONO}" font-size="12" fill="{NAME}">to explain it, it's bad.</text>
  <text x="{SIDEBAR_W-58}" y="{quote_y+78}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">&#8212; Cory House</text>
"""


def panel_box(x, y, w, h, title, icon_kind="dot") -> str:
    mark = f'<circle cx="{x+24}" cy="{y+27}" r="3.5" fill="{SIGNAL}"/>'
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{CARD}" stroke="{LINE}"/>'
            f'{mark}<text x="{x+36}" y="{y+32}" font-family="{MONO}" font-size="13" font-weight="700" '
            f'letter-spacing="0.06em" fill="{INK}">{title}</text>'
            f'<line x1="{x+24}" y1="{y+48}" x2="{x+w-24}" y2="{y+48}" stroke="{LINE}" stroke-width="1"/>')


def kv_rows(x, y, rows, key_w=88) -> str:
    out = []
    for i, (k, v) in enumerate(rows):
        ry = y + i * 27
        out.append(f'<circle cx="{x}" cy="{ry-4}" r="2.5" fill="{SIGNAL}" opacity="0.6"/>'
                    f'<text x="{x+12}" y="{ry}" font-family="{MONO}" font-size="12.5" fill="{MUTED_INK}">{k}</text>'
                    f'<text x="{x+key_w}" y="{ry}" font-family="{MONO}" font-size="12.5" fill="{INK}">:</text>'
                    f'<text x="{x+key_w+16}" y="{ry}" font-family="{MONO}" font-size="12.5" fill="{INK}">{v}</text>')
    return "\n    ".join(out)


def mountains(x, y, w, h) -> str:
    sun_cx, sun_cy = x + w * 0.62, y + h * 0.38
    return f"""
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#e9e2d0"/>
    <clipPath id="mtnClip"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/></clipPath>
    <g clip-path="url(#mtnClip)">
      <circle cx="{sun_cx}" cy="{sun_cy}" r="34" fill="#d8b98a"/>
      <path d="M{x} {y+h*0.62} L{x+w*0.22} {y+h*0.32} L{x+w*0.4} {y+h*0.62} L{x+w*0.58} {y+h*0.26} L{x+w*0.8} {y+h*0.6} L{x+w} {y+h*0.4} L{x+w} {y+h} L{x} {y+h} Z" fill="#c9beac"/>
      <path d="M{x} {y+h*0.78} L{x+w*0.3} {y+h*0.55} L{x+w*0.55} {y+h*0.8} L{x+w*0.78} {y+h*0.6} L{x+w} {y+h*0.75} L{x+w} {y+h} L{x} {y+h} Z" fill="#b3a68f"/>
      <g fill="#4a4438">
        <path d="M{x+w*0.14} {y+h*0.9} l10 -34 10 34z"/>
        <path d="M{x+w*0.2} {y+h*0.92} l9 -28 9 28z"/>
        <path d="M{x+w*0.86} {y+h*0.9} l10 -30 10 30z"/>
        <path d="M{x+w*0.92} {y+h*0.92} l8 -22 8 22z"/>
      </g>
    </g>"""


def stats_sparkline(x, y, w, h) -> str:
    pts = [(0, 30), (14, 24), (28, 26), (42, 10), (56, 18), (70, 4), (84, 12)]
    path = "M" + " L".join(f"{x+px*(w/84):.1f} {y+h-py:.1f}" for px, py in pts)
    dots = "\n      ".join(f'<circle cx="{x+px*(w/84):.1f}" cy="{y+h-py:.1f}" r="2.4" fill="{SIGNAL}"/>' for px, py in pts)
    return f'<path d="{path}" fill="none" stroke="{SIGNAL}" stroke-width="2"/>\n      {dots}'


def content() -> str:
    L = SIDEBAR_W + 48
    R = W - 48
    top = 40

    out = [f'<rect x="{SIDEBAR_W}" y="0" width="{W-SIDEBAR_W}" height="{H}" fill="{CREAM}"/>']

    row1_y = top
    row1_h = 210
    about_w = (R - L) * 0.56
    out.append(panel_box(L, row1_y, about_w, row1_h, "ABOUT ME"))
    about_rows = [
        ("OS", "macOS, Ubuntu (GCP)"),
        ("Host", "Applied AI &amp; Backend Eng."),
        ("Kernel", "Prayagraj, India"),
        ("IDE", "VS Code"),
        ("Shell", "zsh"),
        ("Education", "B.Tech ECE, IIIT-A, 2026"),
    ]
    out.append(kv_rows(L + 24, row1_y + 78, about_rows))

    mtn_x = L + about_w + 24
    mtn_w = R - mtn_x
    out.append(mountains(mtn_x, row1_y, mtn_w, row1_h))

    row2_y = row1_y + row1_h + 24
    row2_h = 150
    half = (R - L - 24) / 2
    out.append(panel_box(L, row2_y, half, row2_h, "LANGUAGES"))
    out.append(kv_rows(L + 24, row2_y + 78, [
        ("Programming", "TypeScript, Python, C++"),
        ("Human", "English, Hindi"),
    ], key_w=100))

    stack_x = L + half + 24
    out.append(panel_box(stack_x, row2_y, half, row2_h, "STACK"))
    out.append(kv_rows(stack_x + 24, row2_y + 78, [
        ("Mobile", "Swift (native iOS)"),
        ("Web", "React, Node/Express"),
        ("AI/ML", "Gemini, PyTorch, HF"),
    ], key_w=80))

    row3_y = row2_y + row2_h + 24
    row3_h = 170
    out.append(panel_box(L, row3_y, half, row3_h, "CONTACT"))
    out.append(kv_rows(L + 24, row3_y + 78, [
        ("Email", "nukillapraveen1@gmail.com"),
        ("Portfolio", "praveennukilla.dev"),
        ("LinkedIn", "praveen-nukilla-753a2a334"),
        ("LeetCode", "Praveen763"),
    ], key_w=90))

    gh_x = stack_x
    out.append(panel_box(gh_x, row3_y, half, row3_h, "GITHUB STATS"))
    out.append(kv_rows(gh_x + 24, row3_y + 78, [
        ("Repositories", str(STATS["repos"])),
        ("Followers", str(STATS["followers"])),
        ("Member since", STATS["since"]),
    ], key_w=110))
    out.append(stats_sparkline(gh_x + half - 130, row3_y + 66, 100, 44))

    row4_y = row3_y + row3_h + 24
    out.append(f'<rect x="{L}" y="{row4_y}" width="{R-L}" height="72" rx="12" fill="{CARD}" stroke="{LINE}"/>')
    out.append(f'<text x="{L+24}" y="{row4_y+26}" font-family="{MONO}" font-size="12" font-weight="700" '
                f'letter-spacing="0.06em" fill="{MUTED_INK}">TECHNOLOGIES</text>')
    bx, by = L + 24, row4_y + 36
    icons = [
        _icon_react(bx, by), _icon_python(bx + 150, by), _icon_node(bx + 300, by),
        _icon_docker(bx + 450, by), _icon_gcp(bx + 600, by), _icon_git(bx + 750, by),
    ]
    labels = ["React", "Python", "Node.js", "Docker", "GCP", "Git"]
    for i, lbl in enumerate(labels):
        out.append(f'<text x="{bx + i*150 + 26}" y="{by+14}" font-family="{MONO}" font-size="12.5" fill="{INK}">{lbl}</text>')
    out.extend(icons)

    return "\n".join(out)


def build_card() -> str:
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Praveen Nukilla profile card">
  <defs>
    <style>text {{ font-family: {MONO}; }}</style>
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
