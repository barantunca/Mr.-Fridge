"""
scan_screen.py — Kamera Tarama ekranı
OpenCV (CAP_DSHOW) ile canlı akışı çeker, kareyi base64'e çevirir,
backend /camera/scan endpoint'ine gönderir, sonuç gösterir
ve onaylanınca /inventory/add'e ekler.
"""
import base64
import threading
import io
import numpy as np
from PIL import Image as PILImage

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics.texture import Texture

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
        self._cap = None            # cv2.VideoCapture nesnesi
        self._camera_image = None   # KivyImage (canvas'ta gösterim)
        self._clock_event = None    # Clock döngüsü
        self._last_frame = None     # Son yakalanan ham frame (numpy array)
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

        # ── KAMERA ALANI ────────────────────────────────────────────────────
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

        # KivyImage — kare buraya yazılacak
        self._camera_image = KivyImage(allow_stretch=True, keep_ratio=True)
        self.camera_placeholder.add_widget(self._camera_image)

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
        """Ekrana girilince kamerayı başlat."""
        self._scan_result = {}
        self.result_name_lbl.text = "Sonuç burada görünecek…"
        self.result_name_lbl.color = TEXT_SEC
        self.result_cat_lbl.text = ""
        self.add_btn.disabled = True
        self.scan_btn.disabled = False
        self.scan_btn.text = "🔍  Taramayı Başlat"

        Clock.schedule_once(self._start_camera, 0.3)

    def _start_camera(self, dt):
        """OpenCV ile kamerayı başlat (arka planda)."""
        if self._cap is not None and self._cap.isOpened():
            # Zaten açık — döngüyü yeniden başlat
            self._start_frame_loop()
            return

        self.camera_status_lbl.text = "📷  Kamera açılıyor…"
        threading.Thread(target=self._open_camera_thread, daemon=True).start()

    def _open_camera_thread(self):
        """Kamerayı arka planda aç (CAP_DSHOW Windows'ta çok daha hızlı)."""
        try:
            import cv2
            # DirectShow backend: Windows'ta varsayılan MF'den çok daha hızlı
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                # DSHOW çalışmazsa varsayılan dene
                cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                Clock.schedule_once(lambda dt: self._on_camera_error("Kamera bulunamadı veya erişim reddedildi."))
                return
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self._cap = cap
            Clock.schedule_once(lambda dt: self._on_camera_ready())
        except ImportError:
            Clock.schedule_once(lambda dt: self._on_camera_error(
                "opencv-python yüklü değil.\npip install opencv-python"
            ))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_camera_error(str(e)))

    def _on_camera_ready(self):
        self.camera_status_lbl.text = ""
        self._start_frame_loop()

    def _on_camera_error(self, msg: str):
        self.camera_status_lbl.text = f"⚠️ Kamera açılamadı:\n{msg}\n\nLütfen kamera iznini kontrol edin."
        self.camera_status_lbl.color = DANGER

    def _start_frame_loop(self):
        """Clock ile 30 FPS kare güncelleme döngüsü."""
        if self._clock_event is not None:
            return
        self._clock_event = Clock.schedule_interval(self._update_frame, 1.0 / 30)

    def _update_frame(self, dt):
        """Her karede OpenCV'den kare al, KivyImage'a yaz."""
        if self._cap is None or not self._cap.isOpened():
            return
        try:
            import cv2
            ret, frame = self._cap.read()
            if not ret:
                return
            # BGR → RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Kivy için dikey flip (koordinat sistemi farkı)
            frame_flip = np.flipud(frame_rgb)
            h, w, _ = frame_flip.shape
            self._last_frame = frame_rgb  # scan için orijinal (flip'siz) kaydet

            texture = Texture.create(size=(w, h), colorfmt='rgb')
            texture.blit_buffer(frame_flip.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self._camera_image.texture = texture
        except Exception:
            pass

    def on_leave(self, *args):
        """Ekrandan çıkınca kamerayı durdur."""
        self._stop_camera()

    def _stop_camera(self):
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        self._last_frame = None

    def _go_back(self, *args):
        """Ana sayfaya geri dön."""
        self._stop_camera()
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
        if self._last_frame is None:
            self.result_name_lbl.text = "⚠️ Kamera henüz hazır değil."
            self.result_name_lbl.color = DANGER
            return

        self.scan_btn.disabled = True
        self.scan_btn.text = "⏳  Analiz ediliyor…"
        self.result_name_lbl.text = "Yapay zeka ile analiz ediliyor…"
        self.result_name_lbl.color = TEXT_SEC
        self.result_cat_lbl.text = ""
        self.add_btn.disabled = True

        frame = self._last_frame.copy()  # thread-safe kopya

        # numpy RGB → PIL → JPEG → base64
        img = PILImage.fromarray(frame)
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
