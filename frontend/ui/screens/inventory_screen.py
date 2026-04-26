"""
inventory_screen.py — Envanter ekranı
"""
import threading

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp

import api_client
from ui.theme import (
    TEXT_PRI, TEXT_SEC, SIZE_BODY
)
from ui.widgets import (
    StyledLabel, CustomTopBar, ProductCard
)

class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._items = []
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # ── HEADER ─────────────────────────────────────────────────────────────
        titlebar = CustomTopBar(title_text="Envanter", right_icon="")
        root.add_widget(titlebar)

        self.status_lbl = StyledLabel(
            text="Yükleniyor…",
            font_size="12sp",
            color=TEXT_SEC,
            size_hint_y=None,
            height=dp(20),
            halign="center"
        )
        root.add_widget(self.status_lbl)

        # ── KAYDIRMALI LİSTE ──────────────────────────────────────────────────
        self.scroll = ScrollView(do_scroll_x=False)
        self.list_layout = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None,
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self, *args):
        self._load_items()

    def _load_items(self):
        self.status_lbl.text = "⏳  Yükleniyor…"
        self.list_layout.clear_widgets()
        threading.Thread(target=self._fetch_items, daemon=True).start()

    def _fetch_items(self):
        items = api_client.get_inventory_items()
        Clock.schedule_once(lambda dt: self._render_items(items))

    def _render_items(self, items: list):
        self._items = items
        self.list_layout.clear_widgets()

        if not items:
            self.status_lbl.text = ""
            empty_lbl = StyledLabel(
                text="Buzdolabın boş!\nOrtadaki + butonundan ürün ekleyebilirsin.",
                font_size=SIZE_BODY,
                color=TEXT_SEC,
                halign="center",
                size_hint_y=None,
                height=dp(80),
            )
            self.list_layout.add_widget(empty_lbl)
            return

        self.status_lbl.text = f"{len(items)} ürün."

        self.list_layout.add_widget(StyledLabel(
            text="Tüm Ürünler",
            font_size="13sp",
            bold=True,
            color=TEXT_SEC,
            size_hint_y=None,
            height=dp(20)
        ))

        grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, row_default_height=dp(130), row_force_default=True)
        grid.bind(minimum_height=grid.setter('height'))

        # Real items from FastAPI backend
        for item in sorted(items, key=lambda x: x.get('days_left', 99)):
            # get days_left or default to 5 if not mapped natively
            days = item.get("days_left", 5)
            card = ProductCard(name=item["name"], days_left=days)
            grid.add_widget(card)

        self.list_layout.add_widget(grid)

    def _delete_item(self, item_id: int):
        self.status_lbl.text = "⏳  Siliniyor…"
        threading.Thread(target=lambda: self._do_delete(item_id), daemon=True).start()

    def _do_delete(self, item_id: int):
        api_client.delete_item(item_id)
        Clock.schedule_once(lambda dt: self._load_items())

