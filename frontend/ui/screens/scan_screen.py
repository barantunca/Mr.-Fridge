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
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

import api_client
from ui.theme import (
    BG_DARK, BG_CARD, ACCENT, ACCENT2, SUCCESS, DANGER,
    TEXT_PRI, TEXT_SEC, SIZE_TITLE, SIZE_BODY, SIZE_SMALL, TRANSPARENT
)
from ui.widgets import CardWidget, StyledLabel, GradientButton, SuccessButton


class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scan_result = {}
        self._camera_widget = None
        self._camera_card = None
        self._build_ui()

    def _build_ui(self):
        self.root_layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # ── GERİ BUTONU + BAŞLIK ───────────────────────────────────────────────
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(8))

        back_btn = Button(
            text="← Geri",
            size_hint_x=None,
            width=dp(80),
            background_color=TRANSPARENT,
            color=ACCENT2,
            bold=True,
            font_size=SIZE_BODY,
        )
        back_btn.bind(on_release=self._go_back)
        top_bar.add_widget(back_btn)

        title = StyledLabel(
            text="📷  Ürün Tara",
            font_size=SIZE_TITLE,
            bold=True,
            halign="center",
        )
        top_bar.add_widget(title)
        top_bar.add_widget(Widget(size_hint_x=None, width=dp(80)))
        self.root_layout.add_widget(top_bar)

        # ── KAMERA PLACEHOLDER ────────────────────────────────────────────────
        # Gerçek kamera widget'ı on_enter'da oluşturulur
        self.camera_placeholder = CardWidget(
            padding=dp(4), size_hint_y=0.5,
            orientation="vertical",
        )
        self.camera_status_lbl = StyledLabel(
            text="📷  Kamera başlatılıyor…",
            font_size=SIZE_BODY,
            color=TEXT_SEC,
            halign="center",
        )
        self.camera_placeholder.add_widget(self.camera_status_lbl)
        self.root_layout.add_widget(self.camera_placeholder)

        # ── TARA BUTONU ────────────────────────────────────────────────────────
        self.scan_btn = GradientButton(
            text="🔍  Taramayı Başlat",
            size_hint_y=None,
            height=dp(52),
        )
        self.scan_btn.bind(on_release=self._on_scan)
        self.root_layout.add_widget(self.scan_btn)

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
        self.root_layout.add_widget(self.result_card)

        self.root_layout.add_widget(Widget())
        self.add_widget(self.root_layout)

    # ── EKRAN GİRİŞ/ÇIKIŞ ────────────────────────────────────────────────────

    def on_enter(self, *args):
        """Ekrana girilince kamerayı başlat (lazy)."""
        self._scan_result = {}
        self.result_name_lbl.text = "Sonuç burada görünecek…"
        self.result_name_lbl.color = TEXT_SEC
        self.result_cat_lbl.text = ""
        self.add_btn.disabled = True
        self.scan_btn.disabled = False
        self.scan_btn.text = "🔍  Taramayı Başlat"

        Clock.schedule_once(self._start_camera, 0.3)

    def _start_camera(self, dt):
        """Kamerayı lazy olarak başlat."""
        if self._camera_widget is not None:
            # Zaten oluşturulmuş, sadece başlat
            try:
                self._camera_widget.play = True
                self.camera_status_lbl.text = ""
            except Exception:
                pass
            return

        try:
            from kivy.uix.camera import Camera
            cam = Camera(
                play=True,
                resolution=(640, 480),
                allow_stretch=True,
                keep_ratio=True,
            )
            self._camera_widget = cam

            # Placeholder'ı temizle ve kamerayı ekle
            self.camera_placeholder.clear_widgets()
            self.camera_placeholder.add_widget(cam)
            self.camera_status_lbl = StyledLabel(text="", font_size="1sp")  # gizli
        except Exception as e:
            self.camera_status_lbl.text = f"⚠️ Kamera açılamadı:\n{e}\n\nLütfen kamera iznini kontrol edin."
            self.camera_status_lbl.color = DANGER
            self._camera_widget = None

    def on_leave(self, *args):
        """Ekrandan çıkınca kamerayı durdur."""
        if self._camera_widget is not None:
            try:
                self._camera_widget.play = False
            except Exception:
                pass

    def _go_back(self, *args):
        """Ana sayfaya geri dön."""
        if self._camera_widget is not None:
            try:
                self._camera_widget.play = False
            except Exception:
                pass
        if self.manager:
            self.manager.current = "home"
            try:
                main_win = self.manager.parent.parent
                if hasattr(main_win, '_nav_buttons'):
                    for sname, btn in main_win._nav_buttons.items():
                        btn.set_active(sname == "home")
            except Exception:
                pass

    # ── TARAMA ────────────────────────────────────────────────────────────────

    def _on_scan(self, *args):
        if self._camera_widget is None or not self._camera_widget.texture:
            self.result_name_lbl.text = "⚠️ Kamera henüz hazır değil."
            self.result_name_lbl.color = DANGER
            return

        self.scan_btn.disabled = True
        self.scan_btn.text = "⏳  Analiz ediliyor…"
        self.result_name_lbl.text = "Yapay zeka ile analiz ediliyor…"
        self.result_name_lbl.color = TEXT_SEC
        self.result_cat_lbl.text = ""
        self.add_btn.disabled = True

        texture = self._camera_widget.texture
        size = texture.size
        pixels = texture.pixels

        # PIL: RGBA → FLIP → RGB → JPEG → base64
        img = PILImage.frombytes('RGBA', size, pixels)
        img = img.transpose(PILImage.FLIP_TOP_BOTTOM)
        img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
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
            self.result_name_lbl.color = DANGER
            self.result_cat_lbl.text = ""
        else:
            self._scan_result = result
            self.result_name_lbl.text = f"🏷️  {result.get('name', '?')}"
            self.result_name_lbl.color = TEXT_PRI
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
            self.result_name_lbl.color = DANGER
            self.add_btn.disabled = False
        else:
            self.result_name_lbl.text = f"✅  {name} envantere eklendi!"
            self.result_name_lbl.color = SUCCESS
            self.result_cat_lbl.text = ""
            self._scan_result = {}
            self.add_btn.disabled = True
