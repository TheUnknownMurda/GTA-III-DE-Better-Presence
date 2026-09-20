"""
Génère les images de la Rich Presence dans assets/ :
    logo.png (grande image de secours), onfoot.png, vehicle.png, menu.png,
    wanted_1.png … wanted_6.png

À uploader dans l'application Discord (Rich Presence → Art Assets) avec le nom
du fichier sans extension comme clé (cf. client/config.json → images). Remplace
`logo` par la jaquette du jeu si tu préfères.

Discord recommande 512×512 minimum et affiche la petite image rognée en cercle :
tout le dessin tient donc dans un disque. Rendu en 4× puis réduit (anti-aliasing).
Palette « Liberty City » : nuit bleu marine, orange du logo III, fenêtres jaunes.

Usage :  client\\.venv\\Scripts\\python tools\\make_assets.py   (nécessite Pillow)
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 512
SS = 4  # facteur de sur-échantillonnage
S = SIZE * SS

BG = (14, 22, 40, 255)          # nuit bleu marine
FG = (255, 255, 255, 255)
ORANGE = (246, 140, 30, 255)    # orange du « III »
WINDOW = (255, 220, 120, 255)   # fenêtres allumées
SKY = (40, 62, 110, 255)        # halo de la ville
GOLD = (255, 196, 0, 255)
GOLD_DARK = (120, 80, 0, 255)

OUT_DIR = Path(__file__).resolve().parent.parent / "assets"
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\verdanab.ttf",
]


def canvas(fill: tuple[int, int, int, int] = BG) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, S - 1, S - 1), fill=fill)
    return img, d


def save(img: Image.Image, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT_DIR / f"{name}.png", optimize=True)
    print(f"  {name}.png")


def load_font(px: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, px)
        except OSError:
            continue
    return ImageFont.load_default()  # type: ignore[return-value]


def star_points(cx: float, cy: float, r_out: float, r_in: float) -> list[tuple[float, float]]:
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def skyline(d: ImageDraw.ImageDraw, u: float, base_y: float, scale: float = 1.0,
            color: tuple[int, int, int, int] = (22, 34, 60, 255), windows: bool = False) -> None:
    """Silhouette de gratte-ciel (Liberty City) posée sur base_y, vers le haut."""
    # (x, largeur, hauteur) en % — de gauche à droite
    towers = [(4, 9, 22), (14, 7, 34), (22, 10, 27), (33, 6, 46), (40, 12, 30),
              (53, 7, 52), (61, 9, 36), (71, 8, 24), (80, 11, 40), (92, 6, 18)]
    for x, w, h in towers:
        h *= scale
        d.rectangle((x * u, (base_y - h) * u, (x + w) * u, base_y * u), fill=color)
        if windows:
            for wy in range(int(base_y - h + 3), int(base_y - 2), 4):
                for wx in range(int(x + 1.5), int(x + w - 1.5), 3):
                    if (wx * 7 + wy * 13) % 5 < 3:
                        d.rectangle((wx * u, wy * u, (wx + 1.2) * u, (wy + 1.6) * u), fill=WINDOW)


# --------------------------------------------------------------------------- #
def make_logo() -> None:
    """Grande image de secours : skyline de Liberty City la nuit, texte « III » orange."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = S / 100
    d.rounded_rectangle((0, 0, S - 1, S - 1), radius=int(18 * u), fill=BG)
    # halo de la ville à l'horizon
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-10 * u, 50 * u, 110 * u, 110 * u), fill=(60, 90, 150, 170))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(radius=int(8 * u))))
    # lune
    d.ellipse((76 * u, 14 * u, 88 * u, 26 * u), fill=(230, 235, 245, 255))
    d.ellipse((79 * u, 12 * u, 90 * u, 23 * u), fill=BG)
    # deux plans de skyline
    skyline(d, u, 86, scale=0.75, color=SKY)
    skyline(d, u, 90, scale=1.0, color=(18, 26, 46, 255), windows=True)
    # sol (bandeau) avec « LIBERTY CITY »
    d.rectangle((0, 88 * u, S, S), fill=(10, 16, 30, 255))
    small = load_font(int(6 * u))
    sub_text = "LIBERTY CITY"
    bbox = d.textbbox((0, 0), sub_text, font=small)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((50 * u - w / 2 - bbox[0], 94 * u - h / 2 - bbox[1]), sub_text, font=small, fill=FG)
    # texte « III »
    font = load_font(int(34 * u))
    text = "III"
    bbox = d.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x0, y0 = 50 * u - w / 2 - bbox[0], 22 * u - bbox[1]
    d.text((x0 + 1.2 * u, y0 + 1.2 * u), text, font=font, fill=(0, 0, 0, 200))
    d.text((x0, y0), text, font=font, fill=ORANGE)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT_DIR / "logo.png", optimize=True)
    print("  logo.png")


def make_onfoot() -> None:
    """Piéton stylisé : tête, torse, jambes en marche."""
    img, d = canvas()
    u = S / 100
    # tête
    d.ellipse((44 * u, 16 * u, 58 * u, 30 * u), fill=FG)
    # torse (incliné vers l'avant)
    d.polygon([(46 * u, 32 * u), (58 * u, 33 * u), (55 * u, 58 * u), (43 * u, 57 * u)], fill=FG)
    # bras
    d.line([(52 * u, 36 * u), (66 * u, 47 * u), (63 * u, 58 * u)], fill=FG, width=int(6 * u), joint="curve")
    d.line([(49 * u, 36 * u), (36 * u, 46 * u), (40 * u, 52 * u)], fill=FG, width=int(6 * u), joint="curve")
    # jambes
    d.line([(49 * u, 56 * u), (36 * u, 70 * u), (34 * u, 86 * u)], fill=FG, width=int(7 * u), joint="curve")
    d.line([(53 * u, 56 * u), (62 * u, 70 * u), (74 * u, 82 * u)], fill=FG, width=int(7 * u), joint="curve")
    save(img, "onfoot")


def make_vehicle() -> None:
    """Voiture vue de profil."""
    img, d = canvas()
    u = S / 100
    # carrosserie
    d.rounded_rectangle((16 * u, 48 * u, 84 * u, 68 * u), radius=int(5 * u), fill=FG)
    # habitacle
    d.polygon([(30 * u, 49 * u), (40 * u, 34 * u), (64 * u, 34 * u), (74 * u, 49 * u)], fill=FG)
    # vitres (découpe en couleur de fond)
    d.polygon([(34 * u, 48 * u), (42 * u, 37 * u), (51 * u, 37 * u), (51 * u, 48 * u)], fill=BG)
    d.polygon([(54 * u, 48 * u), (54 * u, 37 * u), (62 * u, 37 * u), (69 * u, 48 * u)], fill=BG)
    # roues
    for cx in (32, 68):
        d.ellipse(((cx - 8) * u, 60 * u, (cx + 8) * u, 76 * u), fill=BG)
        d.ellipse(((cx - 7) * u, 61 * u, (cx + 7) * u, 75 * u), fill=FG)
        d.ellipse(((cx - 3) * u, 65 * u, (cx + 3) * u, 71 * u), fill=BG)
    save(img, "vehicle")


def make_menu() -> None:
    """Icône pause (deux barres) sur fond orange."""
    img, d = canvas(ORANGE)
    u = S / 100
    d.rounded_rectangle((32 * u, 28 * u, 45 * u, 72 * u), radius=int(3 * u), fill=FG)
    d.rounded_rectangle((55 * u, 28 * u, 68 * u, 72 * u), radius=int(3 * u), fill=FG)
    save(img, "menu")


def make_wanted(level: int) -> None:
    """Étoile dorée avec le niveau de recherche en chiffre."""
    img, d = canvas()
    u = S / 100
    d.polygon(star_points(50 * u, 53 * u, 44 * u, 19 * u), fill=GOLD)
    font = load_font(int(30 * u))
    text = str(level)
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((50 * u - w / 2 - bbox[0], 55 * u - h / 2 - bbox[1]), text, font=font, fill=GOLD_DARK)
    save(img, f"wanted_{level}")


def make_preview() -> None:
    """Planche de contrôle (non destinée à Discord)."""
    names = ["logo", "onfoot", "vehicle", "menu"] + [f"wanted_{i}" for i in range(1, 7)]
    tile = 128
    sheet = Image.new("RGBA", (tile * len(names), tile), (54, 57, 63, 255))
    for i, n in enumerate(names):
        im = Image.open(OUT_DIR / f"{n}.png").resize((tile - 16, tile - 16), Image.LANCZOS)
        sheet.alpha_composite(im, (i * tile + 8, 8))
    sheet.save(OUT_DIR / "_preview.png")
    print("  _preview.png (planche de contrôle)")


if __name__ == "__main__":
    print(f"Génération dans {OUT_DIR}")
    make_logo()
    make_onfoot()
    make_vehicle()
    make_menu()
    for lvl in range(1, 7):
        make_wanted(lvl)
    make_preview()
