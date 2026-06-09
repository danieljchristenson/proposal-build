"""Recolor the black St. Nick's logo to ivory white, preserving alpha."""
from pathlib import Path
from PIL import Image

src = Path("skill_assets/Branding/ST NICKS LOGO.png")
dst = Path("skill_assets/Branding/ST NICKS LOGO WHITE.png")
im = Image.open(src).convert("RGBA")
px = im.load()
for y in range(im.height):
    for x in range(im.width):
        r, g, b, a = px[x, y]
        px[x, y] = (244, 234, 222, a)  # ivory #F4EADE, keep alpha
im.save(dst)
print("wrote", dst)
