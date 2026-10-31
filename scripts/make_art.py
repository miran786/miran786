"""Build the static art for the GitHub profile README.

  python scripts/make_art.py path/to/headshot.webp

Writes assets/banner.svg (animated particle portrait + name) and one card per
featured project in assets/projects/. Needs Pillow. Re-run after editing the
data below.
"""
import math
import random
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ACCENT = (61, 230, 255)
SANS = "'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Consolas, 'SF Mono', Menlo, monospace"
random.seed(11)


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)


def portrait_dots(src, height, step, ox, oy):
    """Sample the headshot into dots, like the website hero."""
    img = Image.open(src).convert("RGB")
    w = round(img.width * height / img.height)
    img = img.resize((w, height), Image.LANCZOS)
    px = img.load()
    dots = []
    for y in range(0, height, step):
        for x in range(0, w, step):
            r, g, b = px[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            sat = 0 if mx == 0 else (mx - mn) / mx
            if lum > 0.8 and sat < 0.1:
                continue  # studio background
            edge = min(min(x / w, 1 - x / w) / 0.16, (1 - y / height) / 0.24, 1)
            if random.random() > edge:
                continue
            lift = min(1, max(0, (0.38 - lum) / 0.38)) * 0.8
            col = [c + (a * 0.5 - c) * lift for c, a in zip((r, g, b), ACCENT)]
            twinkle = lift > 0.3 and random.random() < 0.05
            if twinkle:
                col = ACCENT
            jx, jy = (random.random() - 0.5) * step * 0.5, (random.random() - 0.5) * step * 0.5
            rad = step * (0.34 + 0.1 * random.random() + 0.08 * lum)
            dots.append((ox + x + jx, oy + y + jy, rad, hexc(col), twinkle))
    return dots, w


def banner(headshot):
    W, H = 1200, 380
    dots, pw = portrait_dots(headshot, 352, 5, 0, 22)
    px0 = W - pw - 70
    # Twelve fly-in directions keep the file small: each dot picks one and a delay.
    dirs = [(round(260 * math.cos(k / 12 * math.tau)), round(200 * math.sin(k / 12 * math.tau))) for k in range(12)]
    dir_css = "".join(f".d{k}{{--x:{x}px;--y:{y}px}}" for k, (x, y) in enumerate(dirs))

    circles = []
    for x, y, r, col, tw in dots:
        k = random.randrange(12)
        delay = 0.15 + random.random() * 1.1 + (y / H) * 0.5
        cls = f"p d{k} t" if tw else f"p d{k}"
        circles.append(
            f'<circle class="{cls}" style="--d:{delay:.2f}s" cx="{x + px0:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/>'
        )

    chips = ["2 IEEE papers", "1 published patent", "Intern @ IDeaS", "CGPA 9.24"]
    chip_svg, cx = [], 64
    for i, label in enumerate(chips):
        w = len(label) * 8.6 + 30
        chip_svg.append(
            f'<g class="f f{5 + i}"><rect x="{cx}" y="292" width="{w:.0f}" height="34" rx="17" fill="#0a1e24" stroke="#3de6ff" stroke-opacity=".55"/>'
            f'<text x="{cx + w / 2:.0f}" y="314" text-anchor="middle" font-family="{MONO}" font-size="14" fill="#eaeef6">{escape(label)}</text></g>'
        )
        cx += w + 12

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Miran Jamadar, Software and AI Engineer">
<title>Miran Jamadar · Software &amp; AI Engineer</title>
<style>
.p{{opacity:0;animation:fly 2.2s cubic-bezier(.22,1,.36,1) var(--d) forwards}}
.t{{animation:fly 2.2s cubic-bezier(.22,1,.36,1) var(--d) forwards,tw 2.6s ease-in-out calc(var(--d) + 2.2s) infinite}}
{dir_css}
@keyframes fly{{from{{opacity:0;transform:translate(var(--x),var(--y))}}to{{opacity:1;transform:translate(0,0)}}}}
@keyframes tw{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
.f{{opacity:0;animation:up .9s cubic-bezier(.22,1,.36,1) forwards}}
{"".join(f".f{i}{{animation-delay:{0.1 + i * 0.12:.2f}s}}" for i in range(10))}
@keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.dot{{animation:pulse 2.4s infinite}}
@keyframes pulse{{50%{{opacity:.35}}}}
@media (prefers-reduced-motion:reduce){{.p,.t,.f,.dot{{animation:none;opacity:1}}}}
</style>
<defs>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity=".035"/></pattern>
<radialGradient id="g1" cx="78%" cy="45%" r="45%"><stop offset="0" stop-color="#3de6ff" stop-opacity=".16"/><stop offset="1" stop-color="#3de6ff" stop-opacity="0"/></radialGradient>
<radialGradient id="g2" cx="96%" cy="100%" r="40%"><stop offset="0" stop-color="#8b7bff" stop-opacity=".14"/><stop offset="1" stop-color="#8b7bff" stop-opacity="0"/></radialGradient>
<linearGradient id="name" x1="0" y1="0" x2="0" y2="1"><stop offset=".35" stop-color="#eaeef6"/><stop offset="1" stop-color="#eaeef6" stop-opacity=".45"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="#05060a"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<rect width="{W}" height="{H}" fill="url(#g1)"/>
<rect width="{W}" height="{H}" fill="url(#g2)"/>
{"".join(circles)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="21.5" fill="none" stroke="#ffffff" stroke-opacity=".09"/>
<g class="f f0"><rect x="64" y="44" width="40" height="40" rx="11" fill="none" stroke="#3de6ff" stroke-width="1.5"/>
<text x="84" y="70" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="16" fill="#3de6ff">MJ</text>
<circle class="dot" cx="124" cy="64" r="4" fill="#3de6ff"/>
<text x="138" y="69" font-family="{MONO}" font-size="14" fill="#7f889c">open to 2027 SDE &amp; AI/ML roles</text></g>
<text class="f f1" x="60" y="168" font-family="{SANS}" font-weight="700" font-size="76" letter-spacing="-2.5" fill="url(#name)">Miran Jamadar</text>
<text class="f f2" x="64" y="214" font-family="{SANS}" font-weight="600" font-size="27" fill="#3de6ff">Software &amp; AI Engineer</text>
<text class="f f3" x="64" y="252" font-family="{SANS}" font-size="19" fill="#b9c1d3">B.Tech CSE (AI) · VIT Pune · ML systems, backend &amp; research</text>
{"".join(chip_svg)}
</svg>
"""
    (ASSETS / "banner.svg").write_text(svg, encoding="utf-8")
    print(f"banner.svg: {len(dots)} dots, {len(svg) // 1024} KB")


GLYPHS = {
    "scan": '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1.2"/>',
    "map": '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z"/><path d="M9 4v14M15 6v14"/>',
    "face": '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M9 10v1M15 10v1M12 10v3h-1M9.5 16a4 4 0 0 0 5 0"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z"/><path d="M14 3v5h5M8 13h8M8 17h5"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.4 8.3 8 9 4.6-.7 8-4 8-9V6l-8-3Z"/><path d="m9 12 2 2 4-4"/>',
    "pulse": '<path d="M3 12h4l2-5 4 10 2-5h6"/>',
}

PROJECTS = [
    ("dermascan", "scan", "DEEP LEARNING · HEALTHCARE", "DermaScan AI", "Skin-condition classifier that learns from dermatologists", ["PyTorch", "FastAPI", "AWS Lambda", "Docker"]),
    ("jansahyog", "map", "FULL STACK · CIVIC TECH", "JanSahyog", "Civic issues, reported once and tracked to resolution", ["React Native", "React", "Firebase"]),
    ("facewallet", "face", "BIOMETRICS · SECURITY", "FaceWallet", "A digital wallet you unlock with your face", ["React", "Node.js", "face-api.js"]),
    ("marksheet", "doc", "COMPUTER VISION · BACKEND", "Marksheet Reader", "OCR for college ERPs, built at EduplusCampus", ["FastAPI", "EasyOCR", "OpenCV"]),
    ("stealthguard", "shield", "NETWORKING · ANDROID", "StealthGuard VPN", "A private, lightweight Android VPN", ["Android", "OpenVPN", "AWS Lambda"]),
    ("healthguard", "pulse", "HACKATHON · HEALTHCARE", "HealthGuard", "Wearable vitals, ML risk zones and a Gemini assistant", ["React Native", "ML", "Gemini"]),
]


def project_card(slug, glyph, domain, name, kicker, tags):
    W, H = 560, 170
    tag_svg, x = [], 112
    for t in tags:
        w = len(t) * 7.2 + 20
        tag_svg.append(
            f'<rect x="{x:.0f}" y="124" width="{w:.0f}" height="24" rx="12" fill="#ffffff" fill-opacity=".03" stroke="#ffffff" stroke-opacity=".12"/>'
            f'<text x="{x + w / 2:.0f}" y="140" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="#b9c1d3">{escape(t)}</text>'
        )
        x += w + 8
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{escape(name)}: {escape(kicker)}">
<defs><radialGradient id="g" cx="0%" cy="0%" r="70%"><stop offset="0" stop-color="#3de6ff" stop-opacity=".12"/><stop offset="1" stop-color="#3de6ff" stop-opacity="0"/></radialGradient></defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="#0a0c13" stroke="#ffffff" stroke-opacity=".1"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="url(#g)"/>
<rect x="24" y="26" width="68" height="68" rx="16" fill="#3de6ff" fill-opacity=".08" stroke="#3de6ff" stroke-opacity=".3"/>
<g transform="translate(36 38) scale(1.8)" fill="none" stroke="#3de6ff" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">{GLYPHS[glyph]}</g>
<text x="112" y="44" font-family="{MONO}" font-size="11.5" letter-spacing="1.4" fill="#7f889c">{escape(domain)}</text>
<text x="112" y="76" font-family="{SANS}" font-weight="700" font-size="26" fill="#eaeef6">{escape(name)}</text>
<text x="112" y="104" font-family="{SANS}" font-size="15" fill="#3de6ff">{escape(kicker)}</text>
{"".join(tag_svg)}
<text x="{W - 24}" y="44" text-anchor="end" font-family="{SANS}" font-size="18" fill="#7f889c">↗</text>
</svg>
"""
    out = ASSETS / "projects" / f"{slug}.svg"
    out.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    (ASSETS / "projects").mkdir(parents=True, exist_ok=True)
    banner(sys.argv[1])
    for p in PROJECTS:
        project_card(*p)
    print(f"{len(PROJECTS)} project cards")
