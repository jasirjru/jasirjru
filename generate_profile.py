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
        '<circle cx="24" cy="23" r="5" fill="#df7775"/>'
        '<circle cx="42" cy="23" r="5" fill="#e3ad62"/>'
        '<circle cx="60" cy="23" r="5" fill="#78b88f"/>',
        text(92, 29, "profile / jasirjru", c["muted"], 13),
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


def write_if_changed(name: str, content: str) -> bool:
    path = ROOT / name
    encoded = content.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return False
    path.write_bytes(encoded)
    return True


def main() -> None:
    image_uri, width, height = portrait_data()
    counts = metrics()
    changed = [name for name, theme in (("dark_mode.svg", "dark"),
                                      ("light_mode.svg", "light"))
               if write_if_changed(name, svg(theme, image_uri, width, height, counts))]
    print(f"public repos={counts[0]}, owned repo stars={counts[1]}, followers={counts[2]}")
    print("updated: " + (", ".join(changed) if changed else "none"))


if __name__ == "__main__":
    main()
