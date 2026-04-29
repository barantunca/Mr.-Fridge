"""
main.py — Mr. Fridge Kivy Uygulaması giriş noktası
"""
import os
import sys

# Geliştirme ortamında frontend klasörünü Python yoluna ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Kivy log seviyesini ayarla
os.environ.setdefault("KIVY_LOG_LEVEL", "warning")

# Platform kontrolü için gerekli modül
from kivy.utils import platform

# Kamera ayarını ve pencere boyutunu sadece masaüstünde (PC) zorla
# Mobil cihazlarda (Android/iOS) sistemin kendi değerlerini kullanmasını sağlar
if platform not in ('android', 'ios'):
    # Windows'ta kamera için OpenCV provider zorla
    os.environ.setdefault("KIVY_CAMERA", "opencv")

# Kivy'nin sağ/orta tıklamada ekrana çizdiği kırmızı nokta efektini kapat
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.core.window import Window
from ui.main_window import MainWindow

class MrFridgeApp(App):
    """Mr. Fridge ana uygulama sınıfı."""

    title = "Mr. Fridge"

    def build(self):
        # Masaüstü geliştirme için telefon oranını (9:19.5) sadece PC'de uygula
        # Bu sayede telefonda uygulama tüm ekrana doğru şekilde yayılır
        if platform not in ('android', 'ios'):
            Window.size = (400, 860)
        
        # Arka plan rengi (BG_DARK)
        Window.clearcolor = (15 / 255, 15 / 255, 26 / 255, 1)

        return MainWindow()

    def on_start(self):
        print(f"[OK] Mr. Fridge uygulamasi {platform} platformunda baslatildi.")

if __name__ == "__main__":
    MrFridgeApp().run()