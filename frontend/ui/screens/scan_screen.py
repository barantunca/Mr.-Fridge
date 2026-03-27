"""
scan_screen.py — Kamera Tarama ekranı
OpenCV ile canlı kamera akışını çeker, kareyi base64'e çevirir,
backend /camera/scan endpoint'ine gönderir, sonuç gösterir
ve onaylanınca /inventory/add'e ekler.
"""
import base64
import threading
from io import BytesIO

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.metrics import dp

import api_client
from ui.theme import (
    BG_DARK, BG_CARD, ACCENT, ACCENT2, SUCCESS, DANGER,
    TEXT_PRI, TEXT_SEC, SIZE_TITLE, SIZE_BODY, SIZE_SMALL
)
from ui.widgets import CardWidget, StyledLabel, GradientButton, SuccessButton, Divider

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._capture = None
        self._clock_event = None
        self._last_frame_bytes = None
        self._scan_result = None  # {"name": str, "category": str}
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # ── BAŞLIK ─────────────────────────────────────────────────────────────
        title = StyledLabel(
            text="📷  Ürün Tara",
            font_size=SIZE_TITLE,
            bold=True,
            size_hint_y=None,
            height=dp(44),
        )
        root.add_widget(title)

        # ── KAMERA GÖRÜNTÜSÜ ───────────────────────────────────────────────────
        self.camera_image = KivyImage(
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.5,
        )
        camera_card = CardWidget(padding=dp(4), size_hint_y=0.5)
        camera_card.add_widget(self.camera_image)
        root.add_widget(camera_card)

        # ── TARA BUTONU ────────────────────────────────────────────────────────
        self.scan_btn = GradientButton(
            text="🔍  Taramayı Başlat",
            size_hint_y=None,
            height=dp(52),
        )
        self.scan_btn.bind(on_release=self._on_scan)
        root.add_widget(self.scan_btn)

        # ── SONUÇ KARTI ────────────────────────────────────────────────────────
        self.result_card = CardWidget(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(140),
        )
        self.result_name_lbl = StyledLabel(
            text="Sonuç burada görünecek…",
            font_size=SIZE_BODY,
            color=TEXT_SEC,
            halign="center",
        )
        self.result_cat_lbl = StyledLabel(
            text="",
            font_size=SIZE_SMALL,
            color=ACCENT2,
            halign="center",
        )

        self.add_btn = SuccessButton(
            text="✅  Envantere Ekle",
            size_hint_y=None,
            height=dp(44),
            disabled=True,
        )
        self.add_btn.bind(on_release=self._on_add_item)

        self.result_card.add_widget(self.result_name_lbl)
        self.result_card.add_widget(self.result_cat_lbl)
        self.result_card.add_widget(self.add_btn)
        root.add_widget(self.result_card)

        root.add_widget(Widget())
        self.add_widget(root)

    # ── EKRAN GİRİŞ/ÇIKIŞ ────────────────────────────────────────────────────

    def on_enter(self, *args):
        """Ekrana girilince kamerayı başlat."""
        if CV2_AVAILABLE:
            self._capture = cv2.VideoCapture(0)
            self._clock_event = Clock.schedule_interval(self._update_frame, 1 / 30)
        else:
            self.camera_image.source = ""
            self.result_name_lbl.text = "⚠️ opencv-python yüklü değil.\nPip: pip install opencv-python"

    def on_leave(self, *args):
        """Ekrandan çıkınca kamerayı kapat."""
        if self._clock_event:
            self._clock_event.cancel()
        if self._capture:
            self._capture.release()
            self._capture = None

    # ── KAMERA FRAME GÜNCELLEME ───────────────────────────────────────────────

    def _update_frame(self, dt):
        if not self._capture or not self._capture.isOpened():
            return
        ret, frame = self._capture.read()
        if not ret:
            return

        # Frame'i sakla (tarama için kullanılacak)
        ret2, jpeg = cv2.imencode(".jpg", frame)
        if ret2:
            self._last_frame_bytes = jpeg.tobytes()

        # Kivy texture'a çevir (BGR → RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_flipped = cv2.flip(frame_rgb, 0)
        h, w, _ = frame_flipped.shape
        texture = Texture.create(size=(w, h), colorfmt="rgb")
        texture.blit_buffer(frame_flipped.tobytes(), colorfmt="rgb", bufferfmt="ubyte")
        self.camera_image.texture = texture

    # ── TARAMA ────────────────────────────────────────────────────────────────

    def _on_scan(self, *args):
        if not self._last_frame_bytes:
            self.result_name_lbl.text = "⚠️ Kamera hazır değil."
            return

        self.scan_btn.disabled = True
        self.scan_btn.text = "⏳  Analiz ediliyor…"
        self.result_name_lbl.text = "GPT-4o ile analiz ediliyor…"
        self.result_cat_lbl.text = ""
        self.add_btn.disabled = True

        b64 = base64.b64encode(self._last_frame_bytes).decode("utf-8")
        threading.Thread(target=self._do_scan, args=(b64,), daemon=True).start()

    def _do_scan(self, b64: str):
        result = api_client.scan_item(b64)
        Clock.schedule_once(lambda dt: self._on_scan_done(result))

    def _on_scan_done(self, result: dict):
        self.scan_btn.disabled = False
        self.scan_btn.text = "🔍  Tekrar Tara"
        if "error" in result:
            self.result_name_lbl.text = f"❌ Hata: {result['error']}"
            self.result_cat_lbl.text = ""
        else:
            self._scan_result = result
            self.result_name_lbl.text = f"🏷️  {result.get('name', '?')}"
            self.result_cat_lbl.text = f"Kategori: {result.get('category', '?')}"
            self.add_btn.disabled = False

    # ── ENVANTERE EKLE ────────────────────────────────────────────────────────

    def _on_add_item(self, *args):
        if not self._scan_result:
            return
        name = self._scan_result.get("name", "")
        category = self._scan_result.get("category", "Diğer")
        self.add_btn.disabled = True

        def do_add():
            resp = api_client.add_item(name, category)
            Clock.schedule_once(lambda dt: self._on_add_done(resp, name))

        threading.Thread(target=do_add, daemon=True).start()

    def _on_add_done(self, resp: dict, name: str):
        if "error" in resp:
            self.result_name_lbl.text = f"❌ Eklenemedi: {resp['error']}"
        else:
            self.result_name_lbl.text = f"✅  {name} envantere eklendi!"
            self.result_cat_lbl.text = ""
            self._scan_result = None
        self.add_btn.disabled = False
