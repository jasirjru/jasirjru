"""Generate the light and dark GitHub profile panels from public GitHub data.

The owned portrait asset is embedded into each SVG so GitHub can render it
without loading a second image from inside an SVG document.
"""

from __future__ import annotations

import base64
import json
import os
import struct
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
USER = "jasirjru"
PORTRAIT = ROOT / "assets" / "portrait-illustrated.png"
THEMES = {
    "dark": {
        "bg": "#0d151d", "bar": "#14212b", "border": "#36545d",
        "fg": "#f3f0e7", "muted": "#bacdcc", "key": "#83ded4",
        "accent": "#edb56e", "rule": "#35545d", "art_a": "#143a43",
        "art_b": "#604327",
    },
    "light": {
        "bg": "#faf7ee", "bar": "#e9eee8", "border": "#799898",
        "fg": "#18313a", "muted": "#3b5c61", "key": "#006a74",
        "accent": "#9e4c16", "rule": "#aac4bf", "art_a": "#d9e9e5",
        "art_b": "#f3dbaf",
    },
}


def github_json(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jasir-profile-generator",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com{path}", headers=headers)
    try:
        with urlopen(request, timeout=25) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"GitHub API request failed for {path}: {error}") from error


def metrics() -> tuple[int, int, int]:
    profile = github_json(f"/users/{USER}")
    if profile.get("login", "").lower() != USER:
        raise RuntimeError("GitHub returned a different profile")
    repos = []
    page = 1
    while True:
        batch = github_json(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError("GitHub returned an invalid repository list")
        repos.extend(
            repo for repo in batch
            if repo.get("owner", {}).get("login", "").lower() == USER
            and not repo.get("private")
        )
        if len(batch) < 100:
            break
        page += 1
    count = profile["public_repos"]
    if len(repos) != count:
        raise RuntimeError(f"Incomplete repository listing: expected {count}, received {len(repos)}")
    return count, sum(repo["stargazers_count"] for repo in repos), profile["followers"]


def portrait_data() -> tuple[str, int, int]:
    data = PORTRAIT.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Portrait asset is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if width < 800 or height < 800 or data[25] != 6:
        raise RuntimeError("Portrait must be a high-resolution RGBA PNG")
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii"), width, height


def text(x: int, y: int, value: str, color: str, size: int, weight: int = 400) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
        f'font-weight="{weight}">{escape(value)}</text>'
    )


def portrait(x: int, y: int, width: int, height: int, c: dict[str, str]) -> str:
    # SVG viewport crops the 1309x1202 original; source pixels are never enlarged.
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{c["art_a"]}"/>'
        f'<rect x="{x + width // 2}" y="{y}" width="{width - width // 2}" '
        f'height="{height}" fill="{c["art_b"]}"/>'
        f'<svg x="{x}" y="{y}" width="{width}" height="{height}" '
        'viewBox="180 0 950 1025" overflow="hidden"><use href="#portrait-source"/></svg>'
        f'<path d="M{x} {y+18}V{y}H{x+18} M{x+width-18} {y}H{x+width}V{y+18} '
        f'M{x} {y+height-18}V{y+height}H{x+18} '
        f'M{x+width-18} {y+height}H{x+width}V{y+height-18}" '
        f'fill="none" stroke="{c["key"]}" stroke-width="2"/>'
    )


def svg(theme: str, image_uri: str, image_width: int, image_height: int,
        counts: tuple[int, int, int]) -> str:
    c = THEMES[theme]
    public_repos, stars, followers = counts
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="620" height="640" '
        'viewBox="0 0 620 640" role="img" '
        f'aria-label="Jasir Abdul Hameed, Applied AI and ML Engineer in Kerala, India. '
        f'{public_repos} public repositories, {stars} owned-repository stars, '
        f'{followers} followers.">',
        '<title>Jasir Abdul Hameed — Applied AI / ML Engineer</title>',
        '<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}'
        '.mobile{display:none}@media(max-width:480px){.desktop{display:none}'
        '.mobile{display:inline}}</style>',
        f'<defs><image id="portrait-source" x="0" y="0" width="{image_width}" '
        f'height="{image_height}" href="{image_uri}"/></defs>',
        f'<rect x="1" y="1" width="618" height="638" rx="14" '
        f'fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="2"/>',
        f'<path d="M15 1H605Q619 1 619 15V44H1V15Q1 1 15 1Z" fill="{c["bar"]}"/>',
        f'<path d="M1 44H619" stroke="{c["border"]}"/>',
        text(23, 29, ">", c["key"], 17, 700),
        text(46, 29, "jasirjru / profile", c["muted"], 13),
        text(518, 29, "AI / ML", c["accent"], 12, 700),
        '<g class="desktop">',
        text(230, 76, "jasirjru @ github", c["key"], 15, 700),
        text(230, 106, "Jasir Abdul Hameed", c["fg"], 22, 700),
        text(230, 132, "Applied AI / ML Engineer", c["accent"], 16, 700),
        text(230, 154, "Kerala, India", c["muted"], 14),
        f'<path d="M230 171H592" stroke="{c["rule"]}"/>',
        portrait(26, 145, 190, 220, c),
        text(27, 391, "JASIR / KERALA", c["key"], 13, 700),
        text(27, 417, "full-stack engineering", c["muted"], 12),
        f'<path d="M27 437H203" stroke="{c["rule"]}"/>',
        f'<rect x="27" y="450" width="44" height="5" fill="{c["key"]}"/>'
        f'<rect x="77" y="450" width="44" height="5" fill="{c["accent"]}"/>'
        f'<rect x="127" y="450" width="44" height="5" fill="{c["fg"]}"/>',
    ]
    desktop_rows = (
        ("Languages", "Python · JavaScript · TypeScript", 203),
        ("AI/ML", "PyTorch · scikit-learn", 239),
        ("LLM", "RAG · LoRA / QLoRA", 295),
        ("Backend", "FastAPI · Node.js", 349),
        ("Data", "Qdrant · SQLite", 384),
        ("Tools", "Git · Ollama · Ruff", 419),
        ("Focus", "RAG · production AI", 454),
    )
    for key, value, y in desktop_rows:
        parts.extend((text(230, y, key, c["key"], 15, 700),
                      text(339, y, value, c["fg"], 14)))
    parts.extend((
        text(339, 259, "Hugging Face", c["fg"], 14),
        text(339, 315, "LLM evaluation", c["fg"], 14),
    ))
    parts.extend(metric_block(c, counts, mobile=False))
    parts.extend((
        '</g><g class="mobile">',
        portrait(26, 63, 145, 155, c),
        text(185, 83, "jasirjru @ github", c["key"], 18, 700),
        text(185, 111, "Jasir Abdul Hameed", c["fg"], 22, 700),
        text(185, 139, "Applied AI / ML Engineer", c["accent"], 17, 700),
        text(185, 165, "Kerala, India", c["muted"], 17),
        text(185, 189, "full-stack engineering", c["muted"], 14),
        f'<path d="M27 230H593" stroke="{c["rule"]}"/>',
    ))
    mobile_rows = (
        ("Languages", "Python · JavaScript · TypeScript", 260),
        ("AI/ML", "PyTorch · scikit-learn", 291),
        ("LLM", "RAG · LoRA / QLoRA", 354),
        ("Backend", "FastAPI · Node.js", 417),
        ("Data", "Qdrant · SQLite", 448),
        ("Tools", "Git · Ollama · Ruff", 479),
        ("Focus", "RAG · production AI", 510),
    )
    for key, value, y in mobile_rows:
        parts.extend((text(28, y, key, c["key"], 19, 700),
                      text(175, y, value, c["fg"], 19)))
    parts.extend((
        text(175, 313, "Hugging Face", c["fg"], 19),
        text(175, 376, "LLM evaluation", c["fg"], 19),
        *metric_block(c, counts, mobile=True),
        '</g></svg>\n',
    ))
    return "".join(parts)


def metric_block(c: dict[str, str], counts: tuple[int, int, int],
                 mobile: bool) -> list[str]:
    public_repos, stars, followers = counts
    line_y, number_y, label_y, footer_y = (530, 570, 590, 625) if mobile else (506, 559, 581, 619)
    parts = [f'<path d="M27 {line_y}H593" stroke="{c["rule"]}"/>']
    for x, value, label in ((29, public_repos, "PUBLIC REPOS"),
                            (227, stars, "TOTAL STARS"),
                            (425, followers, "FOLLOWERS")):
        parts.append(text(x, number_y, f"{value:,}", c["accent"], 29, 700))
        parts.append(text(x, label_y, label, c["muted"], 12, 700))
    parts.extend((
        f'<path d="M212 {line_y + 18}V{label_y + 5} M410 {line_y + 18}V{label_y + 5}" '
        f'stroke="{c["rule"]}"/>',
        text(29, footer_y, "github.com/jasirjru", c["muted"], 11),
    ))
    return parts


def panel_shell(theme: str, height: int, title: str) -> list[str]:
    c = THEMES[theme]
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" width="620" '
        f'height="{height}" viewBox="0 0 620 {height}" role="img">',
        '<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}'
        '.mobile{display:none}@media(max-width:480px){.desktop{display:none}'
        '.mobile{display:inline}}'
        '@keyframes cursor{50%{opacity:0}}.cursor{animation:cursor 1.2s steps(1,end) infinite}'
        '@media(prefers-reduced-motion:reduce){.cursor{animation:none}}</style>',
        f'<rect x="1" y="1" width="618" height="{height-2}" rx="10" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<path d="M20 43H600" stroke="{c["rule"]}"/>',
        text(22, 30, ">", c["key"], 16, 700),
        text(43, 30, title, c["fg"], 15, 700),
    ]


def focus_svg(theme: str) -> str:
    c = THEMES[theme]
    parts = panel_shell(theme, 208, "CURRENTLY BUILDING")
    parts.extend((
        '<title>Currently building Jruva AI and GroundDesk</title>',
        '<g class="desktop">',
        text(26, 75, "JRUVA AI", c["key"], 20, 700),
        text(26, 101, "hybrid RAG · grounded answers", c["fg"], 15),
        text(326, 75, "GROUNDDESK", c["key"], 20, 700),
        text(326, 101, "evaluation-first support RAG", c["fg"], 15),
        f'<path d="M309 58V118" stroke="{c["rule"]}"/>',
        f'<path d="M26 130H594" stroke="{c["rule"]}"/>',
        text(26, 158, "RESEARCH", c["accent"], 13, 700),
        text(126, 158, "LoRA / QLoRA · groundedness evaluation", c["muted"], 15),
        text(26, 189, "active work / applied AI systems", c["muted"], 12),
        '</g><g class="mobile">',
        text(26, 73, "JRUVA AI", c["key"], 23, 700),
        text(184, 73, "hybrid RAG", c["fg"], 20),
        text(26, 106, "GROUNDDESK", c["key"], 23, 700),
        text(224, 106, "support RAG + eval", c["fg"], 19),
        f'<path d="M26 124H594" stroke="{c["rule"]}"/>',
        text(26, 154, "RESEARCH", c["accent"], 19, 700),
        text(170, 154, "LoRA / QLoRA", c["muted"], 20),
        text(170, 181, "groundedness evaluation", c["muted"], 19),
        '</g>',
        f'<rect class="cursor" x="578" y="17" width="8" height="14" fill="{c["accent"]}"/>',
        '</svg>\n',
    ))
    return "".join(parts)


PROJECTS = (
    ("domaintune", "DomainTune", "LoRA/QLoRA training for support-ticket triage.",
     "Structured evaluation across model and data changes.", "PYTORCH  /  TRANSFORMERS  /  PEFT"),
    ("customeriq", "CustomerIQ", "Churn-scoring API with strict input contracts.",
     "Explicit model limitations and serving boundaries.", "SCIKIT-LEARN  /  FASTAPI  /  DOCKER"),
    ("nexus", "NEXUS", "Evidence-grounded Ethereum intelligence.",
     "Anomaly and risk models with an inspectable API.", "SCIKIT-LEARN  /  FASTAPI  /  REACT  /  SQLITE"),
)


def project_svg(theme: str, project: tuple[str, str, str, str, str]) -> str:
    c = THEMES[theme]
    slug, name, line1, line2, stack = project
    mobile_lines = {
        "domaintune": ("LoRA/QLoRA support-ticket triage.", "Structured model + data evaluation."),
        "customeriq": ("Churn-scoring API with strict inputs.", "Clear model limits and serving rules."),
        "nexus": ("Evidence-grounded Ethereum AI.", "Anomaly + risk models with an API."),
    }
    mobile_line1, mobile_line2 = mobile_lines[slug]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="620" height="145" '
        'viewBox="0 0 620 145" role="img">',
        f'<title>{escape(name)} — {escape(line1)} {escape(line2)}</title>',
        '<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}</style>',
        f'<rect x="1" y="1" width="618" height="143" rx="10" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<path d="M22 48H598 M22 111H598" stroke="{c["rule"]}"/>',
        '<style>.mobile{display:none}@media(max-width:480px){.desktop{display:none}'
        '.mobile{display:inline}}</style>',
        '<g class="desktop">',
        text(25, 34, name, c["key"], 23, 700),
        text(502, 32, "VIEW REPO ↗", c["accent"], 12, 700),
        text(25, 73, line1, c["fg"], 17),
        text(25, 99, line2, c["fg"], 16),
        text(25, 132, stack, c["muted"], 12, 700),
        '</g><g class="mobile">',
        text(25, 35, name, c["key"], 26, 700),
        text(485, 32, "VIEW REPO ↗", c["accent"], 16, 700),
        text(25, 75, mobile_line1, c["fg"], 21),
        text(25, 102, mobile_line2, c["fg"], 21),
        text(25, 133, stack, c["muted"], 15, 700),
        '</g>',
        '</svg>\n',
    ]
    return "".join(parts)


def stack_svg(theme: str) -> str:
    c = THEMES[theme]
    parts = panel_shell(theme, 304, "TECHNICAL STACK")
    rows = (
        ("AI / ML", "Python · PyTorch · scikit-learn · Hugging Face", 78),
        ("LLM", "RAG · LoRA / QLoRA · evaluation", 124),
        ("BUILD", "FastAPI · Node.js · Express · React", 170),
        ("DATA", "Qdrant · SQLite", 216),
        ("TOOLS", "Git · GitHub Actions · Ollama · Ruff", 262),
    )
    parts.append('<title>Technical stack across AI, LLMs, web, data, and tools</title>')
    parts.append('<g class="desktop">')
    for label, value, y in rows:
        parts.extend((
            text(27, y, label, c["key"], 15, 700),
            text(155, y, value, c["fg"], 16),
            f'<path d="M27 {y+16}H593" stroke="{c["rule"]}"/>',
        ))
    parts.append('</g><g class="mobile">')
    mobile_rows = (
        ("AI / ML", "Python · PyTorch · scikit-learn · HF", 72),
        ("LLM", "RAG · LoRA / QLoRA · evaluation", 119),
        ("BUILD", "FastAPI · Node.js · Express · React", 166),
        ("DATA", "Qdrant · SQLite", 213),
        ("TOOLS", "Git · Actions · Ollama · Ruff", 260),
    )
    for label, value, y in mobile_rows:
        parts.extend((
            text(27, y, label, c["key"], 17, 700),
            text(160, y, value, c["fg"], 18),
            f'<path d="M27 {y+16}H593" stroke="{c["rule"]}"/>',
        ))
    parts.extend(('</g>', '</svg>\n'))
    return "".join(parts)


def activity_svg(theme: str, counts: tuple[int, int, int]) -> str:
    c = THEMES[theme]
    repos, stars, followers = counts
    parts = panel_shell(theme, 164, "GITHUB ACTIVITY")
    parts.extend((
        '<title>Live public GitHub metrics and contribution activity</title>',
        '<g class="desktop">',
        text(27, 89, str(repos), c["accent"], 31, 700),
        text(221, 89, str(stars), c["accent"], 31, 700),
        text(415, 89, str(followers), c["accent"], 31, 700),
        text(27, 111, "PUBLIC REPOS", c["muted"], 13, 700),
        text(221, 111, "OWNED STARS", c["muted"], 13, 700),
        text(415, 111, "FOLLOWERS", c["muted"], 13, 700),
        '</g><g class="mobile">',
        text(27, 89, str(repos), c["accent"], 36, 700),
        text(221, 89, str(stars), c["accent"], 36, 700),
        text(415, 89, str(followers), c["accent"], 36, 700),
        text(27, 113, "PUBLIC REPOS", c["muted"], 17, 700),
        text(221, 113, "OWNED STARS", c["muted"], 17, 700),
        text(415, 113, "FOLLOWERS", c["muted"], 17, 700),
        '</g>',
        f'<path d="M205 57V118 M399 57V118 M27 127H593" stroke="{c["rule"]}"/>',
        text(27, 150, "source: GitHub public API", c["muted"], 12),
        text(437, 150, "REFRESH / DAILY", c["key"], 12, 700),
        '</svg>\n',
    ))
    return "".join(parts)


def connect_svg(theme: str, label: str, width: int = 143) -> str:
    c = THEMES[theme]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="53" '
        f'viewBox="0 0 {width} 53" role="img">',
        f'<title>Connect on {escape(label)}</title>',
        '<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}</style>',
        f'<rect x="1" y="1" width="{width-2}" height="51" rx="8" '
        f'fill="{c["bar"]}" stroke="{c["border"]}"/>',
        text(16, 33, label, c["fg"], 15, 700),
        text(width - 24, 33, "↗", c["key"], 18, 700),
        '</svg>\n',
    ]
    return "".join(parts)


def write_if_changed(name: str, content: str) -> bool:
    path = ROOT / name
    encoded = content.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return True


def main() -> None:
    image_uri, width, height = portrait_data()
    counts = metrics()
    outputs = {}
    for theme in ("dark", "light"):
        outputs[f"{theme}_mode.svg"] = svg(theme, image_uri, width, height, counts)
        outputs[f"assets/profile/focus_{theme}.svg"] = focus_svg(theme)
        outputs[f"assets/profile/stack_{theme}.svg"] = stack_svg(theme)
        outputs[f"assets/profile/activity_{theme}.svg"] = activity_svg(theme, counts)
        for project in PROJECTS:
            outputs[f"assets/profile/{project[0]}_{theme}.svg"] = project_svg(theme, project)
        for label in ("GitHub", "LinkedIn", "Hugging Face", "Email"):
            slug = label.lower().replace(" ", "_")
            outputs[f"assets/profile/connect_{slug}_{theme}.svg"] = connect_svg(theme, label)
        for slug, label, button_width in (
            ("jruva", "JRUVA AI / LIVE", 181),
            ("model", "MODEL / HUGGING FACE", 245),
            ("repositories", "BROWSE REPOSITORIES", 226),
            ("contributions", "VIEW CONTRIBUTIONS", 221),
        ):
            outputs[f"assets/profile/link_{slug}_{theme}.svg"] = connect_svg(theme, label, button_width)
    changed = [name for name, content in outputs.items() if write_if_changed(name, content)]
    print(f"public repos={counts[0]}, owned repo stars={counts[1]}, followers={counts[2]}")
    print("updated: " + (", ".join(changed) if changed else "none"))


if __name__ == "__main__":
    main()
