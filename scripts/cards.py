"""Render the GitHub stats and top-languages cards for the profile README.

  python3 scripts/cards.py OUT_DIR

Runs daily in .github/workflows/profile.yml. Standard library only. Uses
GITHUB_TOKEN when present (Actions) and works unauthenticated locally.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = os.environ.get("PROFILE_USER", "miran786")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Consolas, 'SF Mono', Menlo, monospace"
PALETTE = ["#3de6ff", "#8b7bff", "#4ade80", "#fbbf24", "#f472b6", "#60a5fa"]
OTHER = "#4b5263"


def get(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-cards", "Accept": "application/vnd.github+json"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8")
    return body if raw else json.loads(body)


def collect():
    user = get(f"https://api.github.com/users/{USER}")
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    own = [r for r in repos if not r["fork"]]
    langs = {}
    for r in own:
        for lang, size in get(r["languages_url"]).items():
            langs[lang] = langs.get(lang, 0) + size
    html = get(f"https://github.com/users/{USER}/contributions", raw=True)
    m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
    prs = get(f"https://api.github.com/search/issues?q=author:{USER}+type:pr")["total_count"]
    merged = get(f"https://api.github.com/search/issues?q=author:{USER}+type:pr+is:merged")["total_count"]
    return {
        "contributions": int(m.group(1).replace(",", "")) if m else 0,
        "repos": user["public_repos"],
        "since": user["created_at"][:4],
        "prs": prs,
        "merged": merged,
        "langs": langs,
    }


def frame(w, h, title, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">
<defs><radialGradient id="g" cx="100%" cy="0%" r="75%"><stop offset="0" stop-color="#3de6ff" stop-opacity=".1"/><stop offset="1" stop-color="#3de6ff" stop-opacity="0"/></radialGradient></defs>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="#0a0c13" stroke="#ffffff" stroke-opacity=".1"/>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="url(#g)"/>
<text x="26" y="40" font-family="{MONO}" font-size="12" letter-spacing="1.6" fill="#7f889c">{escape(title.upper())}</text>
<text x="{w - 26}" y="40" text-anchor="end" font-family="{MONO}" font-size="12" fill="#3de6ff">@{USER}</text>
{body}
</svg>
"""


def stats_card(s):
    items = [
        (f"{s['contributions']:,}", "contributions, last year"),
        (str(s["repos"]), "public repos"),
        (str(s["prs"]), "pull requests"),
        (str(s["merged"]), "PRs merged"),
        (str(len(s["langs"])), "languages used"),
        (s["since"], "on GitHub since"),
    ]
    body = []
    for i, (value, label) in enumerate(items):
        x = 26 + (i % 3) * 178
        y = 92 + (i // 3) * 74
        body.append(
            f'<text x="{x}" y="{y}" font-family="{SANS}" font-weight="700" font-size="30" fill="#eaeef6">{escape(value)}</text>'
            f'<text x="{x}" y="{y + 22}" font-family="{SANS}" font-size="13" fill="#b9c1d3">{escape(label)}</text>'
        )
    body.append('<rect x="26" y="56" width="36" height="2" rx="1" fill="#3de6ff"/>')
    return frame(560, 210, "GitHub activity", "".join(body))


def languages_card(langs):
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)
    shown = top[:6]
    rest = sum(v for _, v in top[6:])
    rows = [(name, size, PALETTE[i]) for i, (name, size) in enumerate(shown)]
    if rest:
        rows.append(("Other", rest, OTHER))
    body, x = [], 26.0
    bar_w = 508
    body.append(f'<clipPath id="bar"><rect x="26" y="62" width="{bar_w}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">')
    for name, size, color in rows:
        w = bar_w * size / total
        body.append(f'<rect x="{x:.1f}" y="62" width="{w + 0.6:.1f}" height="10" fill="{color}"/>')
        x += w
    body.append("</g>")
    for i, (name, size, color) in enumerate(rows):
        cx = 26 + (i % 2) * 262
        cy = 104 + (i // 2) * 26
        body.append(
            f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{color}"/>'
            f'<text x="{cx + 18}" y="{cy}" font-family="{SANS}" font-size="14" fill="#eaeef6">{escape(name)}</text>'
            f'<text x="{cx + 240}" y="{cy}" text-anchor="end" font-family="{MONO}" font-size="13" fill="#7f889c">{100 * size / total:.1f}%</text>'
        )
    return frame(560, 210, "Top languages · public repos", "".join(body))


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    s = collect()
    (out / "stats.svg").write_text(stats_card(s), encoding="utf-8")
    (out / "languages.svg").write_text(languages_card(s["langs"]), encoding="utf-8")
    print(json.dumps({k: v for k, v in s.items() if k != "langs"}), "| languages:", len(s["langs"]))
