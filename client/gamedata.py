"""
Données de jeu côté client : noms d'armes (d'après l'icône HUD) et mise en
forme de l'argent.

Le mod transmet le nom de la ressource affichée par `WeaponImage` dans le HUD.
Dans la DE c'est un material instance nommé d'après le sprite du jeu original :
`MI_HUD_Info_Fist`, `MI_HUD_Info_Pistol`… (liste relevée dans l'index du pak de
III DE). On normalise le nom (préfixe retiré, minuscules, alphanumérique) puis
on cherche dans la table ; `config.json` → `weapons` permet de surcharger /
traduire, avec des clés brutes (`MI_HUD_Info_Fist`) ou normalisées (`fist`).
"""

from __future__ import annotations

import re
from typing import Optional

# Nom normalisé du sprite → nom affiché (anglais, noms du jeu original).
# Armes de GTA III : poings, batte, pistolet, Uzi, fusil à pompe, AK-47, M16,
# fusil de précision, lance-roquettes, lance-flammes, Molotov, grenades, détonateur.
WEAPONS: dict[str, str] = {
    "fist": "Fists",
    "bat": "Baseball Bat",
    "pistol": "Pistol",
    "colt45": "Pistol",
    "uzi": "Uzi",
    "shotgun": "Shotgun",
    "ak47": "AK-47",
    "m16": "M16",
    "sniper": "Sniper Rifle",
    "rocket": "Rocket Launcher",
    "rpg": "Rocket Launcher",
    "flame": "Flamethrower",
    "flamethrower": "Flamethrower",
    "molotov": "Molotov Cocktails",
    "grenade": "Grenades",
    "detonator": "Detonator",
    # Icônes présentes dans le pak mais hors GTA III (assets communs à la trilogie)
    "remotegrenade": "Remote Grenades",
    "mac10": "Mac-10",
    "axe": "Axe",
    "chisel": "Chisel",
    "hockeystick": "Hockey Stick",
    "phone": "Phone",
}

# Préfixes retirés avant la recherche (du plus long au plus court).
ICON_PREFIXES = (
    "mi_hud_info_", "m_hud_info_", "t_hud_info_", "hud_info_",
    "mi_hud_", "m_hud_", "t_hud_", "hud_",
)


def normalize_icon(icon: str) -> str:
    n = icon.strip().lower()
    for p in ICON_PREFIXES:
        if n.startswith(p):
            n = n[len(p):]
            break
    return re.sub(r"[^a-z0-9]", "", n)


def weapon_name(icon: Optional[str], overrides: Optional[dict[str, str]] = None) -> Optional[str]:
    """Nom de l'arme d'après le nom de la ressource HUD. Correspondance exacte sur
    le nom normalisé, sinon la clé la plus longue que le nom contient
    (« uzi2 » avant « uzi »). None si inconnue."""
    if not icon:
        return None
    table = dict(WEAPONS)
    if overrides:
        for k, v in overrides.items():
            table[normalize_icon(k)] = v
            table[k.lower()] = v
    if icon.lower() in table:
        return table[icon.lower()]
    name = normalize_icon(icon)
    if not name:
        return None
    if name in table:
        return table[name]
    for key in sorted(table, key=len, reverse=True):
        if key and key in name:
            return table[key]
    return None


def parse_money(raw: Optional[str]) -> Optional[int]:
    """« $00001069 » / « -$250 » / « 1 000 000 $ » → entier (négatif si signe -)."""
    if not raw:
        return None
    digits = re.sub(r"[^\d]", "", raw)
    if not digits:
        return None
    value = int(digits)
    return -value if "-" in raw else value


def format_money(raw: Optional[str], template: str = "{sign}${amount:,}") -> Optional[str]:
    """Met en forme le texte argent du HUD selon `template` ({amount} = entier absolu,
    {sign} = « - » ou vide). Par défaut « $1,069 »."""
    value = parse_money(raw)
    if value is None:
        return None
    sign = "-" if value < 0 else ""
    try:
        return template.format(amount=abs(value), sign=sign)
    except (KeyError, ValueError, IndexError):
        return f"{sign}${abs(value):,}"


def article(word: Optional[str]) -> str:
    """« a » / « an » selon l'initiale (pour « In an Oceanic »)."""
    if not word:
        return "a"
    return "an" if word[0].lower() in "aeiou" else "a"


def format_mission(name: Optional[str], mode: str = "keep") -> Optional[str]:
    """Casse du titre de mission. Dans GTA III les titres sont en capitales
    (« PAS DE SPANK POUR LA PÉPÉE ») : `title` → « Pas De Spank Pour La Pépée »,
    `sentence` → « Pas de spank pour la pépée », `keep` → inchangé. Un titre qui
    n'est pas entièrement en capitales est laissé tel quel ; les acronymes
    (« S.A.M. ») aussi."""
    if not name:
        return None
    name = name.strip().strip("'\"")
    if not name or mode not in ("title", "sentence") or name != name.upper():
        return name
    words = []
    for i, word in enumerate(name.split(" ")):
        if _ACRONYM.fullmatch(word):
            words.append(word)
        elif mode == "sentence" and i > 0:
            words.append(word.lower())
        else:
            words.append(_title_word(word.lower()))
    return " ".join(words)


_ACRONYM = re.compile(r"(?:[A-Za-z]\.)+[A-Za-z]?\.?")


def _title_word(word: str) -> str:
    """Majuscule en tête de mot et après un tiret, une parenthèse ou un guillemet
    ouvrant ('CHUNKY'), pas après une apostrophe interne (DON'T)."""
    out: list[str] = []
    new_word = True
    for ch in word:
        if ch.isalpha():
            out.append(ch.upper() if new_word else ch)
            new_word = False
        else:
            out.append(ch)
            new_word = ch in "-(/&" or (new_word and ch in "'\"")
    return "".join(out)
