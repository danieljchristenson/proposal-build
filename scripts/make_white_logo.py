"""Build a white (ivory) knockout of the St. Nick's logo for dark pages.

The source `ST NICKS LOGO.png` is a dark wordmark on a SOLID WHITE, fully
opaque background (no transparency). Simply recoloring opaque pixels produces a
solid box. Instead we knock out the background: alpha is derived from how DARK
each source pixel is (dark wordmark -> opaque, white background -> transparent),
and the visible color is ivory. Result: an ivory wordmark on transparency that
reads cleanly on the editorial near-black ground.
"""
from pathlib import Path
from PIL import Image

SRC = Path("skill_assets/Branding/ST NICKS LOGO.png")
DST = Path("skill_assets/Branding/ST NICKS LOGO WHITE.png")
INK = (244, 234, 222)  # ivory

im = Image.open(SRC).convert("RGBA")
px = im.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        # Dark source pixels (the wordmark) -> opaque; white background -> transparent.
        alpha = int(max(0, min(255, 255 - lum)))
        # Respect any pre-existing transparency in the source.
        alpha = min(alpha, a)
        px[x, y] = (INK[0], INK[1], INK[2], alpha)

im.save(DST)
print("wrote", DST)
