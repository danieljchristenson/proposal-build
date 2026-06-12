"""Build the dark-page St. Nick's logo: colored Santa + ivory text, transparent bg.

The source `ST NICKS LOGO.png` is a COLORED Santa (red hat, etc.) plus a black
script wordmark on a solid white, fully opaque background. For dark editorial
pages we want a two-tone knockout:
  - the colored Santa is kept as-is (so it doesn't flatten to a white blob),
  - the black wordmark/tagline becomes ivory,
  - the white background becomes transparent.
This reads premium on the near-black ground with no white chip behind it.
"""
from pathlib import Path
from PIL import Image

SRC = Path("skill_assets/Branding/ST NICKS LOGO.png")
DST = Path("skill_assets/Branding/ST NICKS LOGO WHITE.png")
INK = (244, 234, 222)  # ivory for the wordmark
SAT_THRESHOLD = 55     # above this chroma, treat a pixel as part of the colored Santa

im = Image.open(SRC).convert("RGBA")
out = Image.new("RGBA", im.size, (0, 0, 0, 0))
src, dst = im.load(), out.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = src[x, y]
        sat = max(r, g, b) - min(r, g, b)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if a > 40 and sat > SAT_THRESHOLD:
            # Colored Santa pixel — keep original color/alpha.
            dst[x, y] = (r, g, b, a)
        else:
            # Grayscale: dark wordmark -> ivory (opaque), white background -> transparent.
            alpha = int(max(0, min(255, 255 - lum)))
            dst[x, y] = (INK[0], INK[1], INK[2], min(alpha, a))

out.save(DST)
print("wrote", DST)
