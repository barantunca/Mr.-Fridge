"""
theme.py — Mr. Fridge renk ve stil sabitleri
Kivy'de kullanılan hex renkleri (0-1 arasında RGBA) burada tanımlanır.
"""


def hex_to_kivy(hex_color: str) -> tuple:
    """'#rrggbb' → (r, g, b, 1.0) Kivy formatına çevirir."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return (r, g, b, 1.0)


# ── RENKLER ───────────────────────────────────────────────────────────────────
BG_DARK   = hex_to_kivy("#D4EBE0")   # Ana arka plan (Pastel Mint Green)
BG_CARD   = hex_to_kivy("#FDFBF7")   # Kart arka planı (Krem)
BG_INPUT  = hex_to_kivy("#FFFFFF")   # Input arka planı
ACCENT    = hex_to_kivy("#E57373")   # Kırmızı Vurgu
ACCENT2   = hex_to_kivy("#A5D6A7")   # Yeşil Vurgu
SUCCESS   = hex_to_kivy("#FFF59D")   # Sarı Vurgu (Uyarı/Geçiş)
DANGER    = hex_to_kivy("#D32F2F")   # Kırmızı (Tehlike)
TEXT_PRI  = hex_to_kivy("#2F4F4F")   # Birincil metin (Koyu yeşil/gri)
TEXT_SEC  = hex_to_kivy("#78909C")   # İkincil metin (Açık gri)
BORDER    = hex_to_kivy("#E0E0E0")   # Kenarlık
TRANSPARENT = (0, 0, 0, 0)

# Sık kullanılan font boyutları (sp cinsinden str)
SIZE_TITLE = "22sp"
SIZE_BODY  = "15sp"
SIZE_SMALL = "12sp"
SIZE_ICON  = "18sp"

# Yarıçap (Radius)
RADIUS_CARD = 20
