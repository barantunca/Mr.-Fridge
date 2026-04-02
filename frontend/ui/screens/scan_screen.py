"""
scan_screen.py — Kamera Tarama ekranı
Kivy native Camera ile canlı akışı çeker, kareyi base64'e çevirir,
backend /camera/scan endpoint'ine gönderir, sonuç gösterir
ve onaylanınca /inventory/add'e ekler.
"""
import base64
import threading
import io
from PIL import Image as PILImage

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp

import api_client
from ui.theme import (
    BG_DARK, BG_CARD, ACCENT, ACCENT2, SUCCESS, DANGER,
    TEXT_PRI, TEXT_SEC, SIZE_TITLE, SIZE_BODY, SIZE_SMALL
)
from ui.widgets import CardWidget, StyledLabel, GradientButton, SuccessButton, Divider


class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scan_result = {}  # {"name": str, "category": str}
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
        self.camera_widget = Camera(
            play=False,
            resolution=(640, 480),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.5,
        )
        camera_card = CardWidget(padding=dp(4), size_hint_y=0.5)
        camera_card.add_widget(self.camera_widget)
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
        self.camera_widget.play = True

    def on_leave(self, *args):
        """Ekrandan çıkınca kamerayı kapat."""
        self.camera_widget.play = False

    # ── TARAMA ────────────────────────────────────────────────────────────────

    def _on_scan(self, *args):
        if not self.camera_widget.texture:
            self.result_name_lbl.text = "⚠️ Kamera henüz hazır değil."
            return

        self.scan_btn.disabled = True
        self.scan_btn.text = "⏳  Analiz ediliyor…"
        self.result_name_lbl.text = "Yapay zeka ile analiz ediliyor…"
        self.result_cat_lbl.text = ""
        self.add_btn.disabled = True

        texture = self.camera_widget.texture
        size = texture.size
        pixels = texture.pixels

        # PIL ile Kivy Texture'ü RGBA'dan JPEG'e çeviriyoruz
        img = PILImage.frombytes('RGBA', size, pixels)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

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
            self._scan_result = {}
        self.add_btn.disabled = False
