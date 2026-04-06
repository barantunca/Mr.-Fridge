"""
main_window.py — ScreenManager + Bottom Navigation + FAB Pop-up
"""
import threading

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp
from kivy.uix.modalview import ModalView
from kivy.clock import Clock

from ui.theme import (
    BG_DARK, BG_CARD, ACCENT, ACCENT2, TEXT_PRI, TEXT_SEC, TRANSPARENT, SIZE_TITLE, SUCCESS, DANGER
)
from ui.widgets import StyledLabel, CardWidget

from ui.screens.home_screen import HomeScreen
from ui.screens.inventory_screen import InventoryScreen
from ui.screens.recipe_screen import RecipeScreen
from ui.screens.profile_screen import ProfileScreen
from ui.screens.scan_screen import ScanScreen

import api_client


TABS = [
    ("home",      "🏠", "Ana Sayfa"),
    ("inventory", "📦", "Envanter"),
    ("recipe",    "🍳", "Tarifler"),
    ("profile",   "👤", "Profil"),
]

class NavButton(Button):
    def __init__(self, emoji: str, label: str, **kwargs):
        super().__init__(
            text=f"{emoji}\n{label}",
            background_color=TRANSPARENT,
            color=TEXT_SEC,
            font_size="11sp",
            halign="center",
            **kwargs,
        )
        self._active = False

    def set_active(self, active: bool):
        self._active = active
        self.color = TEXT_PRI if active else TEXT_SEC
        self.bold = active


class FAB(Button):
    """Floating Action Button."""
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(64), dp(64)))
        kwargs.setdefault("background_color", TRANSPARENT)
        kwargs.setdefault("text", "+")
        kwargs.setdefault("font_size", "36sp")
        kwargs.setdefault("color", BG_CARD)
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_CARD) # Outer stroke padding
            Ellipse(pos=(self.x - dp(6), self.y - dp(6)), size=(self.width + dp(12), self.height + dp(12)))
            Color(*ACCENT2) # Inner fill
            Ellipse(pos=self.pos, size=self.size)


class ManualAddPopup(ModalView):
    """Manuel ürün ekleme formu."""
    def __init__(self, on_added_callback=None, **kwargs):
        kwargs.setdefault("size_hint", (0.9, None))
        kwargs.setdefault("height", dp(300))
        kwargs.setdefault("background_color", TRANSPARENT)
        super().__init__(**kwargs)
        self.on_added_callback = on_added_callback

        card = CardWidget(orientation="vertical", padding=dp(20), spacing=dp(12))

        # Başlık
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        header.add_widget(StyledLabel(text="✍️", font_size="28sp", size_hint_x=None, width=dp(40)))
        header.add_widget(StyledLabel(text="Manuel Ürün Ekle", font_size=SIZE_TITLE, bold=True, color=TEXT_PRI))
        card.add_widget(header)

        # Ürün adı
        card.add_widget(StyledLabel(text="Ürün Adı:", font_size="13sp", color=TEXT_SEC,
                                    size_hint_y=None, height=dp(20)))
        self.name_input = TextInput(
            hint_text="Örn: Domates",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            background_color=(0.15, 0.15, 0.25, 1),
            foreground_color=TEXT_PRI,
            cursor_color=ACCENT,
            padding=[dp(12), dp(10)],
        )
        card.add_widget(self.name_input)

        # Kategori
        card.add_widget(StyledLabel(text="Kategori:", font_size="13sp", color=TEXT_SEC,
                                    size_hint_y=None, height=dp(20)))
        self.cat_input = TextInput(
            hint_text="Örn: Sebze  (boş bırakabilirsin)",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            background_color=(0.15, 0.15, 0.25, 1),
            foreground_color=TEXT_PRI,
            cursor_color=ACCENT,
            padding=[dp(12), dp(10)],
        )
        card.add_widget(self.cat_input)

        # Durum etiketi
        self.status_lbl = StyledLabel(text="", font_size="12sp", color=TEXT_SEC,
                                      size_hint_y=None, height=dp(20), halign="center")
        card.add_widget(self.status_lbl)

        # Butonlar
        btn_row = BoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(44))

        btn_cancel = Button(
            text="İptal",
            background_color=TRANSPARENT,
            color=TEXT_SEC,
            bold=True,
        )
        btn_cancel.bind(on_release=lambda *a: self.dismiss())

        self.btn_add = Button(
            text="✅  Ekle",
            background_color=TRANSPARENT,
            color=TEXT_PRI,
            bold=True,
        )
        with self.btn_add.canvas.before:
            Color(*SUCCESS)
            self.btn_add.rect = RoundedRectangle(
                pos=self.btn_add.pos, size=self.btn_add.size, radius=[dp(10)]
            )
        self.btn_add.bind(
            pos=lambda inst, val: setattr(inst.rect, "pos", val),
            size=lambda inst, val: setattr(inst.rect, "size", val),
        )
        self.btn_add.bind(on_release=self._on_add)

        btn_row.add_widget(btn_cancel)
        btn_row.add_widget(self.btn_add)
        card.add_widget(btn_row)

        self.add_widget(card)

    def _on_add(self, *args):
        name = self.name_input.text.strip()
        if not name:
            self.status_lbl.text = "⚠️  Ürün adı boş olamaz!"
            self.status_lbl.color = DANGER
            return

        category = self.cat_input.text.strip() or "Diğer"
        self.btn_add.disabled = True
        self.status_lbl.text = "⏳  Ekleniyor…"
        self.status_lbl.color = TEXT_SEC

        def do_add():
            resp = api_client.add_item(name, category)
            Clock.schedule_once(lambda dt: self._on_done(resp, name))

        threading.Thread(target=do_add, daemon=True).start()

    def _on_done(self, resp: dict, name: str):
        if "error" in resp:
            self.status_lbl.text = f"❌ Hata: {resp['error']}"
            self.status_lbl.color = DANGER
            self.btn_add.disabled = False
        else:
            self.status_lbl.text = f"✅  {name} eklendi!"
            self.status_lbl.color = SUCCESS
            if self.on_added_callback:
                self.on_added_callback()
            Clock.schedule_once(lambda dt: self.dismiss(), 1.2)


class FABMenu(ModalView):
    """Ortadaki + butonuna basıldığında açılan menü."""
    def __init__(self, on_camera=None, on_manual=None, **kwargs):
        kwargs.setdefault("size_hint", (0.9, None))
        kwargs.setdefault("height", dp(200))
        kwargs.setdefault("background_color", TRANSPARENT)
        super().__init__(**kwargs)
        self.on_camera = on_camera
        self.on_manual = on_manual

        card = CardWidget(orientation="vertical", padding=dp(20), spacing=dp(10))
        # Maskot ve Başlık
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        header.add_widget(StyledLabel(text="🧊", font_size="32sp", size_hint_x=None, width=dp(40)))
        header.add_widget(StyledLabel(text="Ürün Ekle", font_size=SIZE_TITLE, bold=True, color=TEXT_PRI))
        card.add_widget(header)

        # Butonlar
        btns = BoxLayout(orientation="horizontal", spacing=dp(16))

        btn_cam = Button(text="📷\nFOTOĞRAF ÇEK", halign="center",
                         background_color=TRANSPARENT, color=TEXT_PRI, bold=True)
        with btn_cam.canvas.before:
            Color(*ACCENT2)
            btn_cam.rect = RoundedRectangle(pos=btn_cam.pos, size=btn_cam.size, radius=[dp(12)])
        btn_cam.bind(pos=lambda inst, val: setattr(inst.rect, 'pos', val),
                     size=lambda inst, val: setattr(inst.rect, 'size', val))
        btn_cam.bind(on_release=self._go_camera)

        btn_manual = Button(text="✍️\nMANUEL EKLE", halign="center",
                            background_color=TRANSPARENT, color=TEXT_PRI, bold=True)
        with btn_manual.canvas.before:
            Color(*ACCENT)
            btn_manual.rect = RoundedRectangle(pos=btn_manual.pos, size=btn_manual.size, radius=[dp(12)])
        btn_manual.bind(pos=lambda inst, val: setattr(inst.rect, 'pos', val),
                        size=lambda inst, val: setattr(inst.rect, 'size', val))
        btn_manual.bind(on_release=self._go_manual)

        btns.add_widget(btn_cam)
        btns.add_widget(btn_manual)
        card.add_widget(btns)

        self.add_widget(card)

    def _go_camera(self, *args):
        self.dismiss()
        if self.on_camera:
            Clock.schedule_once(lambda dt: self.on_camera(), 0.1)

    def _go_manual(self, *args):
        self.dismiss()
        if self.on_manual:
            Clock.schedule_once(lambda dt: self.on_manual(), 0.1)


class MainWindow(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._nav_buttons = {}
        self._build()

    def _build(self):
        # Arka plan
        with self.canvas.before:
            Color(*BG_DARK)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # ── SCREEN MANAGER ─────────────────────────────────────────────────────
        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(InventoryScreen(name="inventory"))
        self.sm.add_widget(RecipeScreen(name="recipe"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        self.sm.add_widget(ScanScreen(name="scan"))

        # Ekranı biraz yukarıdan bırakalım ki BottomNav üzerine binmesin
        sm_container = BoxLayout(padding=[0, 0, 0, dp(64)])
        sm_container.add_widget(self.sm)
        self.add_widget(sm_container)

        # ── ALT NAVİGASYON ─────────────────────────────────────────────────────
        self.nav_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(70),
            pos_hint={'x': 0, 'y': 0}
        )
        with self.nav_bar.canvas.before:
            Color(*BG_CARD)
            self._nav_rect = RoundedRectangle(pos=self.nav_bar.pos, size=self.nav_bar.size, radius=[dp(24), dp(24), 0, 0])
        self.nav_bar.bind(pos=self._update_nav_bg, size=self._update_nav_bg)

        # Tabs
        self._add_nav_button(*TABS[0]) # Home
        self._add_nav_button(*TABS[1]) # Inventory

        # Center empty space for FAB
        self.nav_bar.add_widget(Widget(size_hint_x=0.5))

        self._add_nav_button(*TABS[2]) # Recipe
        self._add_nav_button(*TABS[3]) # Profile

        self.add_widget(self.nav_bar)

        # ── FAB ─────────────────────────────────────────────────────────────
        self.fab = FAB(pos_hint={'center_x': 0.5})
        self.fab.y = dp(28) # Overlap bottom nav
        self.fab.bind(on_release=self._open_fab_menu)
        self.add_widget(self.fab)

        self._switch_screen("home")

    def _add_nav_button(self, screen_name, emoji, label):
        btn = NavButton(emoji=emoji, label=label)
        btn.bind(on_release=lambda b, s=screen_name: self._switch_screen(s))
        self._nav_buttons[screen_name] = btn
        self.nav_bar.add_widget(btn)

    def _open_fab_menu(self, *args):
        self.fab_menu = FABMenu(
            on_camera=self._go_to_scan,
            on_manual=self._open_manual_add,
        )
        self.fab_menu.open()

    def _go_to_scan(self):
        """Kamera tarama ekranına geç."""
        self.sm.current = "scan"
        # Nav butonlarını güncelle (scan bir tab değil, sadece ekran)
        for btn in self._nav_buttons.values():
            btn.set_active(False)

    def _open_manual_add(self):
        """Manuel ekleme popup'ını aç."""
        def on_item_added():
            # Mevcut ekranı yenile (home veya inventory ise)
            if self.sm.current in ("home", "inventory"):
                screen = self.sm.get_screen(self.sm.current)
                if hasattr(screen, "on_enter"):
                    screen.on_enter()

        popup = ManualAddPopup(on_added_callback=on_item_added)
        popup.open()

    def _switch_screen(self, name: str):
        if getattr(self, 'sm', None) and self.sm.current:
            try:
                current_idx = [t[0] for t in TABS].index(self.sm.current)
                target_idx = [t[0] for t in TABS].index(name)
                if target_idx > current_idx:
                    self.sm.transition.direction = 'left'
                elif target_idx < current_idx:
                    self.sm.transition.direction = 'right'
            except ValueError:
                pass

        self.sm.current = name
        for sname, btn in self._nav_buttons.items():
            btn.set_active(sname == name)

    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _update_nav_bg(self, *args):
        self._nav_rect.pos = self.nav_bar.pos
        self._nav_rect.size = self.nav_bar.size

    def on_touch_down(self, touch):
        if touch.y > dp(70):
            touch.ud['swipe_x'] = touch.x
            touch.ud['swipe_y'] = touch.y
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if 'swipe_x' in touch.ud:
            dx = touch.x - touch.ud['swipe_x']
            dy = touch.y - touch.ud['swipe_y']
            if abs(dx) > dp(50) and abs(dx) > abs(dy):
                try:
                    current_idx = [t[0] for t in TABS].index(self.sm.current)
                    if dx < 0 and current_idx < len(TABS) - 1:
                        self._switch_screen(TABS[current_idx + 1][0])
                        return True
                    elif dx > 0 and current_idx > 0:
                        self._switch_screen(TABS[current_idx - 1][0])
                        return True
                except ValueError:
                    pass
        return super().on_touch_up(touch)
