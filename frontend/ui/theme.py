"""
theme.py — Mr. Fridge renk ve stil sabitleri
Kivy'de kullanılan hex renkleri (0-1 arasında RGBA) burada tanımlanır.
"""


from kivy.storage.jsonstore import JsonStore

# -- AYARLAR VE YEREL DEPO --
store = JsonStore('app_settings.json')

if not store.exists('app'):
    store.put('app', theme='light', capacity=40)
    
if not store.exists('user'):
    store.put('user', name="Mr. Fridge Dayı", email="fridgedayi@email.com", avatar="assets/mascot_3.png", password="***")

app_settings = store.get('app')
is_dark = app_settings.get('theme', 'light') == 'dark'

def get_fridge_capacity() -> int:
    try:
        return int(store.get('app').get('capacity', 40))
    except:
        return 40

def hex_to_kivy(hex_color: str) -> tuple:
    """'#rrggbb' → (r, g, b, 1.0) Kivy formatına çevirir."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return (r, g, b, 1.0)


# -- RENKLER --
if is_dark:
    BG_DARK     = hex_to_kivy("#121212")   # Koyu arka plan
    BG_CARD     = hex_to_kivy("#1E1E1E")   # Koyu kart rengi
    TEXT_PRI    = hex_to_kivy("#FFFFFF")   # Açık ana metin
    TEXT_SEC    = hex_to_kivy("#A0A0A0")   # Açık ikincil metin
    BORDER      = hex_to_kivy("#333333")   # Koyu kenarlıklar
else:
    BG_DARK     = hex_to_kivy("#F7F9F9")   # Çok hafif soğuk gri-beyaz (İkonları parlatır)
    BG_CARD     = hex_to_kivy("#FFFFFF")   # Saf beyaz kartlar
    TEXT_PRI    = hex_to_kivy("#2D3436")   # Daha yumuşak bir siyah
    TEXT_SEC    = hex_to_kivy("#636E72")   # Okunabilir gri
    BORDER      = hex_to_kivy("#EFEFEF")   # Neredeyse görünmez kenarlıklar 

ACCENT      = hex_to_kivy("#55EFC4")   # Daha canlı ama göz yormayan Mint (Vurgu)
ACCENT2     = hex_to_kivy("#81ECEC")   # İkincil yumuşak mavi-yeşil
SUCCESS     = hex_to_kivy("#00B894")   # Gerçek başarı yeşili (Daha önce sarıydı)
WARNING     = hex_to_kivy("#FFEAA7")   # Yeni: Yumuşak sarı (Yaklaşan tarihler için)
DANGER      = hex_to_kivy("#FF7675")   # Yumuşak kırmızı
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

def get_capacity_color(pct: float) -> tuple:
    """
    Doluluk oranına (0-100) göre dinamik Kivy rengi (R, G, B, A) döndürür.
    0% = Kırmızı, 50% = Sarı, 100% = Yeşil
    """
    pct = max(0.0, min(100.0, float(pct)))
    # R (Kırmızı) değeri 0-50 arası 1.0 kalır, 50-100 arası 1.0'dan 0.0'a iner
    r = min(1.0, 2.0 - (pct / 50.0))
    # G (Yeşil) değeri 0-50 arası 0.0'dan 1.0'a çıkar, 50-100 arası 1.0 kalır
    g = min(1.0, pct / 50.0)
    b = 0.0
    return (r, g, b, 1.0)