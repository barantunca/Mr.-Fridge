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
        self.status_lbl.text = "Yükleniyor…"
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

        from collections import defaultdict
        grouped_items = defaultdict(list)
        for item in sorted(items, key=lambda x: x.get('days_left', 99)):
            cat = item.get("category", "Diğer")
            if not cat:
                cat = "Diğer"
            grouped_items[cat].append(item)

        for category_name, cat_items in grouped_items.items():
            # Kategori Başlığı
            self.list_layout.add_widget(StyledLabel(
                text=str(category_name).upper(),
                font_size="14sp",
                bold=True,
                color=TEXT_PRI,
                size_hint_y=None,
                height=dp(30)
            ))

            # Ürünlerin grid'i
            grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, row_default_height=dp(130), row_force_default=True)
            grid.bind(minimum_height=grid.setter('height'))

            for item in cat_items:
                days = item.get("days_left", 5)
                card = ProductCard(
                    name=item["name"], 
                    category=item.get("category", "Diğer"),
                    days_left=days,
                    item_id=item.get("id"),
                    on_delete=self._delete_item
                )
                grid.add_widget(card)

            if len(cat_items) % 2 != 0:
                grid.add_widget(Widget()) # Force second column for 50% width

            self.list_layout.add_widget(grid)
            
            # Kategoriler arası ekstra esneme boşluğu
            self.list_layout.add_widget(Widget(size_hint_y=None, height=dp(10)))

    def _delete_item(self, item_id: int):
        self.status_lbl.text = "Siliniyor…"
        threading.Thread(target=lambda: self._do_delete(item_id), daemon=True).start()

    def _do_delete(self, item_id: int):
        api_client.delete_item(item_id)
        Clock.schedule_once(lambda dt: self._load_items())