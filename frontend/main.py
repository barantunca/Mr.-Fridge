"""
main.py — Mr. Fridge Kivy Uygulaması giriş noktası

Çalıştırmak için:
    cd frontend
    pip install "kivy[base]" requests Pillow opencv-python
    python main.py
"""
import os
import sys

# Geliştirme ortamında frontend klasörünü Python yoluna ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Kivy log seviyesini ayarla (isteğe bağlı)
os.environ.setdefault("KIVY_LOG_LEVEL", "warning")

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp

from ui.main_window import MainWindow


class MrFridgeApp(App):
    """Mr. Fridge ana uygulama sınıfı."""

    title = "Mr. Fridge"

    def build(self):
        # Pencere boyutu — masaüstü geliştirme için telefon oranı (9:19.5)
        Window.size = (400, 860)
        Window.clearcolor = (15 / 255, 15 / 255, 26 / 255, 1)  # BG_DARK

        return MainWindow()

    def on_start(self):
        print("[OK] Mr. Fridge uygulamasi baslatildi.")


if __name__ == "__main__":
    MrFridgeApp().run()
