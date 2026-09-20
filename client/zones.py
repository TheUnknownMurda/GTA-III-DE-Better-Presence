"""
Géographie de Liberty City : île et quartier à partir des coordonnées.

Le mod envoie la position en unités Unreal (cm, axe Y inversé). Conversion
vérifiée sur SA DE et VC DE (même moteur) : III_x = UE_x / 100,
III_y = -UE_y / 100, III_z = UE_z / 100.

Les boîtes ci-dessous sont celles de `data/gta3.zon` du jeu original (zones de
navigation, c'est-à-dire celles dont le nom s'affiche à l'écran), avec les
noms anglais du GXT. La DE réutilise ces données. Le nom affiché par le HUD
(titre montré à chaque changement de quartier, dans la langue du jeu) a la
priorité ; le calcul ci-dessous sert de repli tant qu'aucun titre n'a été vu,
et donne toujours l'île.
"""

from __future__ import annotations

from typing import Optional

ISLAND_PORTLAND = "Portland"
ISLAND_STAUNTON = "Staunton Island"
ISLAND_SHORESIDE = "Shoreside Vale"
ISLANDS = {1: ISLAND_PORTLAND, 2: ISLAND_STAUNTON, 3: ISLAND_SHORESIDE}

# (nom, x_min, y_min, z_min, x_max, y_max, z_max, île) — gta3.zon, zones de
# navigation (type 0 et 1). Les zones d'info (type 2 : commissariat, hôpital,
# concessions…) ne s'affichent pas dans le jeu et sont omises.
ZONES: tuple[tuple[str, float, float, float, float, float, float, int], ...] = (
    # Portland
    ("Callahan Bridge",      617.442, -958.347,   6.261, 1065.44,  -908.347, 206.261, 1),
    ("Callahan Point",       751.68, -1178.22,  -13.872, 1065.68,  -958.725, 136.128, 1),
    ("Atlantic Quays",      1065.88, -1251.55,  -13.505, 1501.88, -1069.93,  136.495, 1),
    ("Portland Harbor",     1363.68, -1069.65,  -18.864, 1815.68,  -613.646, 131.136, 1),
    ("Trenton",             1065.88, -1069.85,    1.499, 1363.38,  -742.054, 151.499, 1),
    ("Chinatown",            745.421, -908.289, -21.203, 1065.42,  -463.69,  129.593, 1),
    ("Red Light District",   745.378, -463.616, -22.668, 1065.38,  -282.616, 147.332, 1),
    ("Hepburn Heights",      745.421, -282.4,   -13.412, 1065.42,   -78.77,  136.588, 1),
    ("Saint Mark's",        1065.9,  -512.324,  -14.296, 1388.9,    -78.324, 135.704, 1),
    ("Harwood",              745.979,  -78.178, -48.583, 1388.98,   322.676, 101.417, 1),
    ("Portland Beach",      1389.37,  -613.467, -29.883, 1797.6,    199.628, 120.117, 1),
    ("Portland View",       1066.1,   -741.806, -34.207, 1363.6,   -512.806, 115.793, 1),
    ("Portland",             617.151, -1329.72, -117.535, 1902.66,  434.115, 482.465, 1),
    # Staunton Island
    ("Callahan Bridge",      444.768, -958.298,  30.744,  614.878, -908.298, 180.744, 2),
    ("Fort Staunton",        239.878, -411.617,   0.0,    614.322,  -61.617, 163.819, 2),
    ("Aspatria",            -225.764, -412.604,   0.0,    116.236,  160.496, 120.271, 2),
    ("Torrington",           199.766, -1672.42, -61.759,  577.766, -1059.93, 432.688, 2),
    ("Bedford Point",       -224.438, -1672.05, -61.318,  199.562, -1004.45, 432.352, 2),
    ("Newport",              200.107, -1059.19,   0.0,    615.107,  -412.193, 198.864, 2),
    ("Belleville Park",     -121.567, -1003.07, -46.746,  199.271,  -413.068, 224.163, 2),
    ("Liberty Campus",       117.268, -411.622,   0.0,    239.268,   -61.622, 166.36,  2),
    ("Rockford",             117.236,  -61.111, -17.071,  615.236,   268.889,  83.754, 2),
    ("Staunton Island",     -265.479, -1719.97, -114.769, 615.52,    367.265, 485.231, 2),
    # Shoreside Vale
    ("Francis Intl. Airport", -1632.97, -1344.71, -45.94, -468.629, -268.443, 254.696, 3),
    ("Wichita Gardens",      -811.835, -268.074, -45.875, -371.041,   92.726, 254.241, 3),
    ("Cedar Grove",          -867.229,   93.388, -50.113, -266.914,  650.058, 250.426, 3),
    ("Pike Creek",          -1407.57,  -267.966, -49.679, -812.306,   92.756, 250.437, 3),
    ("Cochrane Dam",        -1394.5,     93.444, -46.741, -867.52,   704.544, 253.344, 3),
    ("Shoreside Vale",      -1644.64, -1351.38, -117.0,  -266.895, 1206.35,  483.0,   3),
    ("Shoreside Vale",       -265.444,  161.113, -41.709, -121.287,  367.043, 358.291, 3),
    ("Shoreside Vale",       -265.434,   79.092, -45.82,  -226.334,  161.064, 354.18,  3),
)

ISLAND_NAMES = frozenset(ISLANDS.values())
ZONE_NAMES = frozenset(z[0] for z in ZONES)


def ue_to_iii(x: float, y: float, z: float = 0.0) -> tuple[float, float, float]:
    return x / 100.0, -y / 100.0, z / 100.0


def _volume(z: tuple) -> float:
    return (z[4] - z[1]) * (z[5] - z[2]) * (z[6] - z[3])


def zone_from_iii(x: float, y: float, z: Optional[float] = None) -> Optional[tuple[str, str]]:
    """(quartier, île) pour des coordonnées III (mètres). Le quartier est la plus
    petite zone contenant le point ; None si hors de toute zone. La hauteur est
    ignorée si inconnue."""
    best = None
    for zone in ZONES:
        name, x0, y0, z0, x1, y1, z1, lvl = zone
        if x0 <= x <= x1 and y0 <= y <= y1 and (z is None or z0 <= z <= z1):
            if best is None or _volume(zone) < _volume(best):
                best = zone
    if best is None:
        return None
    return best[0], ISLANDS[best[7]]


INTERIOR_MIN_Z = 500.0  # hors carte : intérieurs / positions invalides


def is_interior_ue(z: Optional[float]) -> bool:
    return z is not None and z / 100.0 > INTERIOR_MIN_Z


def zone_from_ue(x: Optional[float], y: Optional[float], z: Optional[float] = None) -> tuple[Optional[str], Optional[str]]:
    """(quartier, île) pour une position Unreal. (None, None) si inconnue, hors
    carte ou en intérieur."""
    if x is None or y is None or is_interior_ue(z):
        return None, None
    ix, iy, iz = ue_to_iii(x, y, z or 0.0)
    if abs(ix) > 3000 or abs(iy) > 3000:
        return None, None
    # On tente d'abord avec la hauteur (élimine les ponts/tunnels superposés),
    # puis sans (la boîte Z du .zon est parfois serrée).
    hit = zone_from_iii(ix, iy, iz if z is not None else None) or zone_from_iii(ix, iy, None)
    if hit is None:
        return None, None
    return hit


def island_from_ue(x: Optional[float], y: Optional[float], z: Optional[float] = None) -> Optional[str]:
    return zone_from_ue(x, y, z)[1]
