"""Gera os ícones PNG do Lunara a partir de um desenho único.

Uso: python tools/make_icons.py
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "static" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

BASE = 1024
TOP = (247, 168, 190)
MID = (224, 85, 123)
BOTTOM = (169, 77, 127)
CREAM = (255, 250, 244)


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def background(size: int) -> Image.Image:
    image = Image.new("RGB", (size, size))
    pixels = image.load()
    for y in range(size):
        t = y / max(1, size - 1)
        color = lerp(TOP, MID, t / 0.55) if t <= 0.55 else lerp(MID, BOTTOM, (t - 0.55) / 0.45)
        for x in range(size):
            # leve luz diagonal, sem alterar a matiz
            glow = max(0.0, 1.0 - math.hypot(x / size - 0.18, y / size - 0.12) / 0.72)
            pixels[x, y] = tuple(min(255, round(c + glow * 13)) for c in color)
    return image


def crescent(size: int, scale: float, dx: float = 0.0, dy: float = 0.0) -> Image.Image:
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    cx = size * (0.47 + dx)
    cy = size * (0.55 + dy)
    r = size * scale
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    cut = Image.new("L", (size, size), 0)
    cut_draw = ImageDraw.Draw(cut)
    ox = cx + r * 0.50
    oy = cy - r * 0.50
    cut_draw.ellipse((ox - r * 0.93, oy - r * 0.93, ox + r * 0.93, oy + r * 0.93), fill=255)
    mask = Image.composite(Image.new("L", (size, size), 0), mask, cut)
    # suaviza a borda do recorte
    mask = mask.filter(ImageFilter.GaussianBlur(size * 0.004))
    layer.paste(Image.new("RGBA", (size, size), CREAM + (255,)), (0, 0), mask)
    return layer


def sparkle(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill, points: int = 4):
    coords = []
    for i in range(points * 2):
        angle = -math.pi / 2 + i * math.pi / points
        radius = r if i % 2 == 0 else r * 0.24
        coords.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    draw.polygon(coords, fill=fill)


def compose(size: int, scale: float, with_sparkles: bool = True) -> Image.Image:
    image = background(size).convert("RGBA")

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse(
        (size * 0.16, size * 0.12, size * 0.62, size * 0.58),
        fill=(255, 255, 255, 26),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.09))
    image = Image.alpha_composite(image, glow)

    image = Image.alpha_composite(image, crescent(size, scale))

    if with_sparkles:
        draw = ImageDraw.Draw(image)
        sparkle(draw, size * 0.735, size * 0.235, size * 0.092, CREAM + (245,))
        draw.ellipse(
            (size * 0.79, size * 0.40, size * 0.815, size * 0.425),
            fill=CREAM + (190,),
        )
        draw.ellipse(
            (size * 0.245, size * 0.775, size * 0.263, size * 0.793),
            fill=CREAM + (150,),
        )
    return image


def save(image: Image.Image, name: str, size: int):
    image.resize((size, size), Image.LANCZOS).convert("RGB").save(
        OUT / name, "PNG", optimize=True
    )


def main():
    standard = compose(BASE, 0.36)
    save(standard, "icon-512.png", 512)
    save(standard, "icon-192.png", 192)
    save(standard, "apple-touch-icon.png", 180)

    # Maskable: desenho dentro da zona segura (80% central).
    maskable = compose(BASE, 0.30, with_sparkles=True)
    save(maskable, "icon-maskable-512.png", 512)

    print("Ícones gerados em", OUT)


if __name__ == "__main__":
    main()
