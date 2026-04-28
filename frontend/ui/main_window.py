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
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

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
    ("home",      'assets/AnaSayfa.png', "Ana Sayfa"),
    ("inventory", 'assets/Envanter.png', "Envanter"),
    ("recipe",    'assets/Tarifler.png', "Tarifler"),
    ("profile",   'assets/Profil.png', "Profil"),
]

class NavButton(BoxLayout):
    def __init__(self, emoji: str, label: str, **kwargs):
        super().__init__(orientation="vertical", padding=[0, dp(4), 0, dp(4)], spacing=0, **kwargs)
        self._active = False
        
        self.icon = Image(source=emoji, size_hint=(1, 0.6))
        self.add_widget(self.icon)
        
        self.lbl = StyledLabel(text=label, font_size="11sp", halign="center", color=TEXT_SEC, size_hint=(1, 0.4))
        self.add_widget(self.lbl)

        self.register_event_type('on_release')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_release')
            return True
        return super().on_touch_down(touch)

    def on_release(self, *args):
        pass

    def set_active(self, active: bool):
        self._active = active
        self.lbl.color = TEXT_PRI if active else TEXT_SEC
        self.lbl.bold = active
        self.icon.opacity = 1.0 if active else 0.5


class FAB(Button):
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
            Color(*BG_CARD) 
            Ellipse(pos=(self.x - dp(6), self.y - dp(6)), size=(self.width + dp(12), self.height + dp(12)))
            Color(*ACCENT2) 
            Ellipse(pos=self.pos, size=self.size)


class ManualAddPopup(ModalView):
    def __init__(self, on_added_callback=None, **kwargs):
        kwargs.setdefault("size_hint", (0.9, None))
        kwargs.setdefault("height", dp(300))
        kwargs.setdefault("background_color", TRANSPARENT)
        super().__init__(**kwargs)
        self.on_added_callback = on_added_callback

        card = CardWidget(orientation="vertical", padding=dp(20), spacing=dp(12))

        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(16))
        
        # Sola yaslamak için boşluk ekleyebiliriz ya da sağa yaslamak için ortaya Widget() atabiliriz
        header.add_widget(Widget()) # Başlığı ve ikonu sağ üstte tutmak için boşluğu sola alıyoruz
        
        header.add_widget(Image(source='assets/ManuelEkle.png', size_hint=(None, None), size=(dp(40), dp(40)), pos_hint={'center_y': 0.5}))
        header.add_widget(StyledLabel(text="Manuel Ürün Ekle", font_size="20sp", bold=True, color=TEXT_PRI, size_hint_x=None, width=dp(180), halign="right"))
        
        card.add_widget(header)

        card.add_widget(StyledLabel(text="Ürün Adı:", font_size="13sp", color=TEXT_SEC,
                                    size_hint_y=None, height=dp(20)))
        self.name_input = TextInput(
            hint_text="Örn: Domates",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            background_color=(0.96, 0.96, 0.96, 1), # Çok açık gri arka plan (#F5F5F5)
            foreground_color=(0.1, 0.1, 0.1, 1),    # Net okunabilir koyu siyah/gri
            cursor_color=ACCENT,
            padding=[dp(12), dp(10)],
        )
        card.add_widget(self.name_input)

        card.add_widget(StyledLabel(text="Kategori:", font_size="13sp", color=TEXT_SEC,
                                    size_hint_y=None, height=dp(20)))
        self.cat_input = TextInput(
            hint_text="Örn: Sebze  (boş bırakabilirsin)",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            background_color=(0.96, 0.96, 0.96, 1), # Çok açık gri arka plan (#F5F5F5)
            foreground_color=(0.1, 0.1, 0.1, 1),    # Net okunabilir koyu siyah/gri
            cursor_color=ACCENT,
            padding=[dp(12), dp(10)],
        )
        card.add_widget(self.cat_input)

        self.status_lbl = StyledLabel(text="", font_size="12sp", color=TEXT_SEC,
                                      size_hint_y=None, height=dp(20), halign="center")
        card.add_widget(self.status_lbl)

        btn_row = BoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(44))

        btn_cancel = Button(
            text="İptal",
            background_color=TRANSPARENT,
            color=TEXT_SEC,
            bold=True,
        )
        btn_cancel.bind(on_release=lambda *a: self.dismiss())

        self.btn_add = Button(
            text="Ekle",
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
            self.status_lbl.text = "Ürün adı boş olamaz!"
            self.status_lbl.color = DANGER
            return

        category = self.cat_input.text.strip() or "Diğer"
        self.btn_add.disabled = True
        self.status_lbl.text = "Ekleniyor…"
        self.status_lbl.color = TEXT_SEC

        def do_add():
            resp = api_client.add_item(name, category)
            Clock.schedule_once(lambda dt: self._on_done(resp, name))

        threading.Thread(target=do_add, daemon=True).start()

    def _on_done(self, resp: dict, name: str):
        if "error" in resp:
            self.status_lbl.text = f"Hata: {resp['error']}"
            self.status_lbl.color = DANGER
            self.btn_add.disabled = False
        else:
            self.status_lbl.text = f"{name} eklendi!"
            self.status_lbl.color = SUCCESS
            if self.on_added_callback:
                self.on_added_callback()
            Clock.schedule_once(lambda dt: self.dismiss(), 1.2)


class FABMenu(ModalView):
    def __init__(self, on_camera=None, on_manual=None, **kwargs):
        kwargs.setdefault("size_hint", (0.9, None))
        kwargs.setdefault("height", dp(200))
        kwargs.setdefault("background_color", TRANSPARENT)
        super().__init__(**kwargs)
        self.on_camera = on_camera
        self.on_manual = on_manual

        card = CardWidget(orientation="vertical", padding=dp(24), spacing=dp(15))
        
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        header.add_widget(StyledLabel(text="Ürün Ekle", font_size=SIZE_TITLE, bold=True, color=TEXT_PRI, halign="center"))
        card.add_widget(header)

        btns = BoxLayout(orientation="horizontal", spacing=dp(16))

        class FABButton(ButtonBehavior, BoxLayout):
            def __init__(self, icon_path, label_text, bg_color, **kwargs):
                super().__init__(orientation="vertical", padding=dp(10), spacing=dp(5), **kwargs)
                with self.canvas.before:
                    Color(*bg_color)
                    self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
                self.bind(pos=self._update_rect, size=self._update_rect)
                self.add_widget(Image(source=icon_path, size_hint_y=0.6))
                self.add_widget(StyledLabel(text=label_text, halign="center", bold=True, color=TEXT_PRI, size_hint_y=0.4))
                
            def _update_rect(self, *args):
                self.rect.pos = self.pos
                self.rect.size = self.size

        btn_cam = FABButton('assets/Foto_Cek.png', "FOTOĞRAF\nÇEK", ACCENT2)
        btn_cam.bind(on_release=self._go_camera)

        btn_manual = FABButton('assets/ManuelEkle.png', "MANUEL\nEKLE", ACCENT)
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
        with self.canvas.before:
            Color(*BG_DARK)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(InventoryScreen(name="inventory"))
        self.sm.add_widget(RecipeScreen(name="recipe"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        self.sm.add_widget(ScanScreen(name="scan"))

        sm_container = BoxLayout(padding=[0, 0, 0, dp(64)])
        sm_container.add_widget(self.sm)
        self.add_widget(sm_container)

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

        self._add_nav_button(*TABS[0]) 
        self._add_nav_button(*TABS[1]) 

        self.nav_bar.add_widget(Widget(size_hint_x=0.5))

        self._add_nav_button(*TABS[2]) 
        self._add_nav_button(*TABS[3]) 

        self.add_widget(self.nav_bar)

        self.fab = FAB(pos_hint={'center_x': 0.5})
        self.fab.y = dp(28) 
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
        self.sm.current = "scan"
        for btn in self._nav_buttons.values():
            btn.set_active(False)

    def _open_manual_add(self):
        def on_item_added():
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