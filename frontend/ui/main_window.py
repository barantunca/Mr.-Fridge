"""
main_window.py — ScreenManager + Bottom Navigation + FAB Pop-up
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp
from kivy.uix.modalview import ModalView

from ui.theme import (
    BG_DARK, BG_CARD, ACCENT, ACCENT2, TEXT_PRI, TEXT_SEC, TRANSPARENT, SIZE_TITLE
)
from ui.widgets import StyledLabel, CardWidget

from ui.screens.home_screen import HomeScreen
from ui.screens.inventory_screen import InventoryScreen
from ui.screens.recipe_screen import RecipeScreen
from ui.screens.profile_screen import ProfileScreen


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

class FABMenu(ModalView):
    """Ortadaki + butonuna basıldığında açılan animasyonlu veya popup menü."""
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (0.9, None))
        kwargs.setdefault("height", dp(200))
        kwargs.setdefault("background_color", TRANSPARENT)
        super().__init__(**kwargs)
        
        card = CardWidget(orientation="vertical", padding=dp(20), spacing=dp(10))
        # Maskot ve Başlık
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        header.add_widget(StyledLabel(text="🧊", font_size="32sp", size_hint_x=None, width=dp(40)))
        header.add_widget(StyledLabel(text="Ürün Ekle", font_size=SIZE_TITLE, bold=True, color=TEXT_PRI))
        card.add_widget(header)
        
        # Butonlar
        btns = BoxLayout(orientation="horizontal", spacing=dp(16))
        
        btn_cam = Button(text="📷\nFOTOĞRAF ÇEK", halign="center", background_color=TRANSPARENT, color=TEXT_PRI, bold=True)
        with btn_cam.canvas.before:
            Color(*ACCENT2)
            btn_cam.rect = RoundedRectangle(pos=btn_cam.pos, size=btn_cam.size, radius=[dp(12)])
        btn_cam.bind(pos=lambda inst, val: setattr(inst.rect, 'pos', val), size=lambda inst, val: setattr(inst.rect, 'size', val))
        
        btn_manual = Button(text="✍️\nMANUEL EKLE", halign="center", background_color=TRANSPARENT, color=TEXT_PRI, bold=True)
        with btn_manual.canvas.before:
            Color(*ACCENT)
            btn_manual.rect = RoundedRectangle(pos=btn_manual.pos, size=btn_manual.size, radius=[dp(12)])
        btn_manual.bind(pos=lambda inst, val: setattr(inst.rect, 'pos', val), size=lambda inst, val: setattr(inst.rect, 'size', val))

        btns.add_widget(btn_cam)
        btns.add_widget(btn_manual)
        card.add_widget(btns)
        
        self.add_widget(card)

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
        self.sm = ScreenManager(transition=FadeTransition(duration=0.15))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(InventoryScreen(name="inventory"))
        self.sm.add_widget(RecipeScreen(name="recipe"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        
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
        self.fab_menu = FABMenu()
        self.fab_menu.open()

    def _switch_screen(self, name: str):
        self.sm.current = name
        for sname, btn in self._nav_buttons.items():
            btn.set_active(sname == name)

    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _update_nav_bg(self, *args):
        self._nav_rect.pos = self.nav_bar.pos
        self._nav_rect.size = self.nav_bar.size
