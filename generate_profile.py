"""Generate Jasir's GitHub profile SVGs from public GitHub data.

The 40x40 portrait is an original pixel study sampled from Jasir's GitHub
avatar (https://avatars.githubusercontent.com/u/144598391?v=4). It is stored
as palette indices so generation needs only Python's standard library.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
USER = "jasirjru"
PALETTE = (
    "#fefdfd", "#fdfdfe", "#fdfdfd", "#fdfdfc", "#fcfdfc", "#f3e7cc",
    "#f1b475", "#e0963e", "#b49660", "#966840", "#455f5a", "#177686",
    "#167382", "#232625", "#061d27", "#050709",
)
PORTRAIT_ROWS = (
    "2222222222223458bbbcccb86544222222222222",
    "2222222224358bccccccccc97776533222222222",
    "22222222448bccccaaaaaac97777765232222222",
    "222222245bccbccaddffddd97777777543222222",
    "22222248cccbcaddffffffdd9977777764122222",
    "222234bbccbbcadffffdfffffd97777775332222",
    "22224bcbbbbbbaffadffffffffdd777775533222",
    "22238cbbbbbbcdf9999ffdffffff977775553222",
    "2245bbbbbbbbbad66679dfffddfdd97775554222",
    "224bcbbbbbbbbc8666567affdffff97775555322",
    "248cbbbbbbbbcaa98ada97dffffff97775555522",
    "24bbbbbbbbbc88996998988dffffd97775555542",
    "28bbbbbbbbbb8b986898867dd99ff97775555552",
    "4bbbbbbbbbbba8666666666d997dd77775555552",
    "5bbbbbbbbbbbba868866667a887d977775555554",
    "5bbbbbbbbcbbbc9886766678869d977775555554",
    "8bbbbb88888888986897777989fd97777abbccc8",
    "bbbbbb77777777866867778a9fdd97777abbcccb",
    "bbbbbb7777777778966779a79fd977777abbbbcb",
    "bbbbbb77777777766689aa86997777777abbbbbb",
    "bbbbbb7777777779dafea8769f9777777abbbbbb",
    "bbbbbb777777779dd7da76669fd997acbbbbbbbb",
    "bccbcb77799999d8869a87678eedd9aacbcbbbcb",
    "555555799deedd66666677679eeefdd999acbbc8",
    "4555569deeeee96666668766deeeeeeeeeddacc5",
    "45556deeefefd6689966868defffeeeeeeee9cc4",
    "35559eeeefff86886689888dfffeeeeeeeeedab3",
    "2558deeeeffa679d996666559eeeeeeeeeeee952",
    "245deeefefd667d79d97666669edddeeefeeea42",
    "226deeeffd6677a79ffd9787669dadefffeee842",
    "214deefff6679df89fffedd86669ddfffffea422",
    "2225eeff8678eff8fffffffd7666aefffeee5122",
    "22248ff8677dfffdfffffffea76669ffffe83222",
    "22224a86779ffffffffffffee866669ffea42222",
    "2222245778dfffeefffeeeeeea766669fa422222",
    "222220467afffffeefffeeffff97666664222222",
    "222223235dffffffeeeefeffffd7766532222222",
    "2222222235affffffeeeeefffffa764322222222",
    "222222222225aeeeeeeffffffffa542222222222",
    "222222222222245aaefeeeeaa842222222222222",
)


def github_json(path: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "jasir-profile-generator"}
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
        repos.extend(repo for repo in batch if repo.get("owner", {}).get("login", "").lower() == USER and not repo.get("private"))
        if len(batch) < 100:
            break
        page += 1
    count = profile["public_repos"]
    if len(repos) != count:
        raise RuntimeError(f"Incomplete repository listing: expected {count}, received {len(repos)}")
    return count, sum(repo["stargazers_count"] for repo in repos), profile["followers"]


def pixel_rects() -> str:
    if len(PORTRAIT_ROWS) != 40 or any(len(row) != 40 for row in PORTRAIT_ROWS):
        raise RuntimeError("Portrait grid must be 40 x 40")
    parts = []
    for y, row in enumerate(PORTRAIT_ROWS):
        x = 0
        while x < 40:
            color = row[x]
            end = x + 1
            while end < 40 and row[end] == color:
                end += 1
            # The near-white avatar canvas becomes transparent around the portrait.
            if color not in "01234":
                parts.append(f'<rect x="{x}" y="{y}" width="{end-x}" height="1" fill="{PALETTE[int(color, 16)]}"/>')
            x = end
    return "".join(parts)


def write_if_changed(name: str, content: str) -> bool:
    path = ROOT / name
    encoded = content.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return False
    path.write_bytes(encoded)
    return True


def portrait_svg(pixels: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 40 40" '
        'role="img" aria-label="Pixel portrait of Jasir Abdul Hameed based on his GitHub avatar">'
        f'<title>Jasir Abdul Hameed — pixel portrait</title><g shape-rendering="crispEdges">{pixels}</g></svg>\n'
    )


THEMES = {
    "dark": {"bg": "#0d151d", "bar": "#14212b", "border": "#34515a", "fg": "#f3f0e7", "muted": "#b8cbc9", "key": "#7dd6ce", "accent": "#e3ad62", "rule": "#31505a"},
    "light": {"bg": "#f7f4e9", "bar": "#e8e9dc", "border": "#7b9b9b", "fg": "#18313a", "muted": "#3a5d64", "key": "#006e78", "accent": "#a45418", "rule": "#a8c2bd"},
}


def label(x: int, y: int, value: str, color: str, size: int = 16, weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'


def profile_svg(theme: str, pixels: str, counts: tuple[int, int, int]) -> str:
    c = THEMES[theme]
    public_repos, stars, followers = counts
    lines = [
        ("Name", "Jasir Abdul Hameed", 153),
        ("Role", "Applied AI / ML Engineer", 184),
        ("Location", "Kerala, India", 215),
        ("Languages", "Python · JavaScript · TS", 246),
        ("AI/ML", "PyTorch · scikit-learn", 277),
        ("LLM", "LoRA / QLoRA · LLM eval", 330),
        ("Backend", "FastAPI · Node.js", 361),
        ("Data", "SQLite", 392),
        ("Tools", "Git · Ollama · Ruff", 423),
        ("Focus", "Applied AI · React apps", 454),
    ]
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="620" height="610" viewBox="0 0 620 610" role="img" aria-label="Jasir Abdul Hameed, Applied AI and ML Engineer in Kerala, India. {public_repos} public repositories, {stars} stars, {followers} followers.">',
        '<title>Jasir Abdul Hameed — GitHub profile</title>',
        '<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;dominant-baseline:alphabetic}.mobile{display:none}@media(max-width:480px){.desktop{display:none}.mobile{display:inline}}</style>',
        f'<rect x="1" y="1" width="618" height="608" rx="14" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="2"/>',
        f'<path d="M15 1H605Q619 1 619 15V44H1V15Q1 1 15 1Z" fill="{c["bar"]}"/>',
        f'<path d="M1 44H619" stroke="{c["border"]}"/>',
        '<circle cx="24" cy="23" r="5" fill="#e77676"/><circle cx="42" cy="23" r="5" fill="#e3ad62"/><circle cx="60" cy="23" r="5" fill="#78b88f"/>',
        label(92, 29, "profile / jasirjru", c["muted"], 13),
        '<g class="desktop">',
        label(228, 83, "jasirjru", c["accent"], 25, 700),
        label(362, 83, "@github", c["fg"], 25, 700),
        label(230, 106, "Applied AI / ML Engineer", c["muted"], 14),
        f'<path d="M228 119H590" stroke="{c["rule"]}"/>',
        f'<rect x="25" y="145" width="190" height="190" fill="{c["bar"]}"/>',
        f'<path d="M25 163V145H43 M197 145H215V163 M25 317V335H43 M197 335H215V317" fill="none" stroke="{c["key"]}" stroke-width="2"/>',
        f'<g transform="translate(30 150) scale(4.5)" shape-rendering="crispEdges">{pixels}</g>',
        label(27, 366, "AVATAR / PIXEL STUDY", c["key"], 12, 700),
        label(27, 387, "JASIR ABDUL HAMEED", c["muted"], 11),
        f'<path d="M27 412H203" stroke="{c["rule"]}"/>',
        label(27, 438, "full-stack engineer", c["muted"], 12),
        f'<rect x="27" y="454" width="43" height="5" fill="{c["key"]}"/><rect x="76" y="454" width="43" height="5" fill="{c["accent"]}"/><rect x="125" y="454" width="43" height="5" fill="{c["fg"]}"/>',
    ]
    for key, value, y in lines:
        pieces.extend((label(230, y, key, c["key"], 15, 700), label(328, y, value, c["fg"], 15)))
    pieces.append(label(328, 298, "Hugging Face", c["fg"], 15))
    # The AI/ML row has a second line; LLM remains a distinct row below it.
    pieces.append(f'<path d="M26 497H594" stroke="{c["rule"]}"/>')
    for x, number, title in ((29, public_repos, "PUBLIC REPOS"), (227, stars, "TOTAL STARS"), (425, followers, "FOLLOWERS")):
        pieces.append(label(x, 546, f"{number:,}", c["accent"], 29, 700))
        pieces.append(label(x, 570, title, c["muted"], 12, 700))
    pieces.extend((
        f'<path d="M212 516V575 M410 516V575" stroke="{c["rule"]}"/>',
        label(29, 592, "github.com/jasirjru", c["muted"], 11),
        label(451, 592, "built from public data", c["muted"], 10),
        '</g><g class="mobile">',
        f'<rect x="26" y="65" width="136" height="136" fill="{c["bar"]}"/>',
        f'<path d="M26 81V65H42 M146 65H162V81 M26 185V201H42 M146 201H162V185" fill="none" stroke="{c["key"]}" stroke-width="2"/>',
        f'<g transform="translate(28 67) scale(3.3)" shape-rendering="crispEdges">{pixels}</g>',
        label(180, 85, "jasirjru@github", c["accent"], 23, 700),
        label(180, 113, "Applied AI / ML Engineer", c["fg"], 17),
        label(180, 141, "full-stack engineer", c["muted"], 15),
        f'<path d="M28 210H592" stroke="{c["rule"]}"/>',
    ))
    mobile_rows = [
        ("Name", "Jasir Abdul Hameed", 234),
        ("Role", "Applied AI / ML Engineer", 263),
        ("Location", "Kerala, India", 292),
        ("Languages", "Python · JavaScript · TS", 321),
        ("AI/ML", "PyTorch · scikit-learn", 350),
        ("LLM", "LoRA / QLoRA · LLM eval", 397),
        ("Backend", "FastAPI · Node.js", 426),
        ("Data", "SQLite", 455),
        ("Tools", "Git · Ollama · Ruff", 484),
        ("Focus", "Applied AI · React apps", 513),
    ]
    for key, value, y in mobile_rows:
        pieces.extend((label(29, y, key, c["key"], 19, 700), label(179, y, value, c["fg"], 19)))
    pieces.extend((
        label(179, 371, "Hugging Face", c["fg"], 19),
        f'<path d="M27 527H593" stroke="{c["rule"]}"/>',
    ))
    for x, number, title in ((29, public_repos, "PUBLIC REPOS"), (227, stars, "TOTAL STARS"), (425, followers, "FOLLOWERS")):
        pieces.append(label(x, 563, f"{number:,}", c["accent"], 27, 700))
        pieces.append(label(x, 582, title, c["muted"], 12, 700))
    pieces.extend((
        f'<path d="M212 540V584 M410 540V584" stroke="{c["rule"]}"/>',
        label(29, 600, "github.com/jasirjru", c["muted"], 11),
        '</g></svg>\n',
    ))
    return "".join(pieces)


def main() -> None:
    pixels = pixel_rects()
    counts = metrics()
    changed = []
    for name, content in (
        ("portrait.svg", portrait_svg(pixels)),
        ("dark_mode.svg", profile_svg("dark", pixels, counts)),
        ("light_mode.svg", profile_svg("light", pixels, counts)),
    ):
        if write_if_changed(name, content):
            changed.append(name)
    print(f"public repos={counts[0]}, owned repo stars={counts[1]}, followers={counts[2]}")
    print("updated: " + (", ".join(changed) if changed else "none"))


if __name__ == "__main__":
    main()
