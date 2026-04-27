"""
theme.py — Mr. Fridge renk ve stil sabitleri
Kivy'de kullanılan hex renkleri (0-1 arasında RGBA) burada tanımlanır.
"""


def hex_to_kivy(hex_color: str) -> tuple:
    """'#rrggbb' → (r, g, b, 1.0) Kivy formatına çevirir."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return (r, g, b, 1.0)


# -- RENKLER --
BG_DARK     = hex_to_kivy("#F7F9F9")   # Çok hafif soğuk gri-beyaz (İkonları parlatır)
BG_CARD     = hex_to_kivy("#FFFFFF")   # Saf beyaz kartlar
ACCENT      = hex_to_kivy("#55EFC4")   # Daha canlı ama göz yormayan Mint (Vurgu)
ACCENT2     = hex_to_kivy("#81ECEC")   # İkincil yumuşak mavi-yeşil
SUCCESS     = hex_to_kivy("#00B894")   # Gerçek başarı yeşili (Daha önce sarıydı)
WARNING     = hex_to_kivy("#FFEAA7")   # Yeni: Yumuşak sarı (Yaklaşan tarihler için)
DANGER      = hex_to_kivy("#FF7675")   # Yumuşak kırmızı
TEXT_PRI    = hex_to_kivy("#2D3436")   # Daha yumuşak bir siyah
TEXT_SEC    = hex_to_kivy("#636E72")   # Okunabilir gri
BORDER      = hex_to_kivy("#EFEFEF")   # Neredeyse görünmez kenarlıklar 
TRANSPARENT = (0, 0, 0, 0)

# Sık kullanılan font boyutları (sp cinsinden str)
SIZE_TITLE = "22sp"
SIZE_BODY  = "15sp"
SIZE_SMALL = "12sp"
SIZE_ICON  = "18sp"

# Yarıçap (Radius)
RADIUS_CARD = 20
# İkon Boyutları (dp cinsinden kullanım için)
ICON_SIZE_SMALL = 16
ICON_SIZE_MEDIUM = 24
ICON_SIZE_LARGE = 32