"""Build favicon set from assets/img/dxn.png — scaled to fit, transparent padding.

Regenerate after editing the source:  python scripts/build_favicons.py
"""
from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "img"
SRC = IMG / "dxn.png"


def flood_knockout_matte(im: Image.Image, tol: int = 48) -> Image.Image:
    """If edges are a flat light matte (e.g. white), flood to transparent."""
    im = im.convert("RGBA").copy()
    w, h = im.size
    px = im.load()
    corners = [px[0, 0][:3], px[w - 1, 0][:3], px[0, h - 1][:3], px[w - 1, h - 1][:3]]
    ref = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    if min(ref) < 200 or sum(ref) // 3 < 230:
        return im

    def matches(r: int, g: int, b: int) -> bool:
        return all(abs((r, g, b)[i] - ref[i]) <= tol for i in range(3))

    q: deque[tuple[int, int]] = deque()
    vis: set[tuple[int, int]] = set()
    for x in range(w):
        for y in (0, h - 1):
            r, g, b, a = px[x, y]
            if a and matches(r, g, b):
                vis.add((x, y))
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if (x, y) in vis:
                continue
            r, g, b, a = px[x, y]
            if a and matches(r, g, b):
                vis.add((x, y))
                q.append((x, y))

    while q:
        x, y = q.popleft()
        r, g, b, _ = px[x, y]
        px[x, y] = (r, g, b, 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in vis:
                continue
            r2, g2, b2, a2 = px[nx, ny]
            if a2 and matches(r2, g2, b2):
                vis.add((nx, ny))
                q.append((nx, ny))
    return im


def trim_alpha(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    a = im.split()[3]
    bbox = a.getbbox()
    if bbox is None:
        return im
    return im.crop(bbox)


def fit_icon_square(img: Image.Image, side: int, *, margin: float = 0.98) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    scale = min(side / w, side / h) * margin
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    out.paste(resized, ((side - nw) // 2, (side - nh) // 2), resized)
    return out


def avg_opaque_rgb(im: Image.Image) -> tuple[int, int, int]:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    rs: list[int] = []
    gs: list[int] = []
    bs: list[int] = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 128:
                rs.append(r)
                gs.append(g)
                bs.append(b)
    if not rs:
        return (16, 26, 32)
    return sum(rs) // len(rs), sum(gs) // len(gs), sum(bs) // len(bs)


def apple_touch_from_master(master: Image.Image, size: int = 180) -> Image.Image:
    small = master.resize((size, size), Image.Resampling.LANCZOS)
    bg = avg_opaque_rgb(small)
    plate = Image.new("RGB", (size, size), bg)
    plate.paste(small, (0, 0), small)
    return plate


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing {SRC}")

    base = Image.open(SRC)
    base = flood_knockout_matte(base)
    base = trim_alpha(base)
    master = fit_icon_square(base, 512, margin=0.98)

    master.resize((16, 16), Image.Resampling.LANCZOS).save(IMG / "favicon-16.png", optimize=True)
    master.resize((32, 32), Image.Resampling.LANCZOS).save(IMG / "favicon-32.png", optimize=True)
    master.resize((32, 32), Image.Resampling.LANCZOS).save(IMG / "favicon.png", optimize=True)
    master.resize((192, 192), Image.Resampling.LANCZOS).save(IMG / "android-chrome-192.png", optimize=True)
    master.resize((512, 512), Image.Resampling.LANCZOS).save(IMG / "android-chrome-512.png", optimize=True)
    apple_touch_from_master(master).save(IMG / "apple-touch-icon.png", optimize=True)
    master.save(IMG / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])

    print(
        "Wrote favicons from dxn.png.\n"
        "Browsers cache favicons aggressively: bump ?v= on every favicon href in HTML "
        "(e.g. ?v=2 → ?v=3), then reload in a private window or clear cached images."
    )


if __name__ == "__main__":
    main()
