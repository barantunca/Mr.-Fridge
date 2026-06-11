"""
home_screen.py — Home screen
Displays the fridge summary, notifications, and a quick list.
"""
import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

import api_client
from ui.theme import (
    ACCENT, ACCENT2, DANGER, TEXT_PRI, TEXT_SEC, SIZE_TITLE, SIZE_BODY, SIZE_SMALL
)
from ui.widgets import CardWidget, StyledLabel, CustomTopBar, DonutChart, ProductCard

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # ── HEADER (Custom Top Bar) ────────────────────────────────────────────
        root.add_widget(CustomTopBar(title_text="Home", right_icon=""))

        # Make content scrollable
        scroll = ScrollView(do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(20), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self, *args):
        # Fetch inventory every time the screen is visited
        self.content.clear_widgets()
        self.content.add_widget(StyledLabel(text="Loading...", color=TEXT_SEC, font_size="14sp", halign="center"))
        threading.Thread(target=self._fetch_summary, daemon=True).start()

    def _fetch_summary(self):
        items = api_client.get_inventory_items()
        Clock.schedule_once(lambda dt: self._render_ui(items))

    def _render_ui(self, items):
        self.content.clear_widgets()
        
        total_items = len(items)
        # Fill percentage algorithm
        fill_pct = min(100, int((total_items / 40.0) * 100)) if items else 0

        # Determine urgent items
        urgent = [i for i in items if i.get("days_left", 5) <= 3]
        
        # ── FRIDGE SUMMARY CARD ──────────────────────────────────────────────
        summary_card = CardWidget(orientation="horizontal", padding=dp(16), spacing=dp(16), size_hint_y=None, height=dp(140))
        
        # Left section: Total Items
        left_box = BoxLayout(orientation="vertical", spacing=dp(4))
        left_box.add_widget(StyledLabel(text="TOTAL", font_size="10sp", bold=True, color=TEXT_SEC, halign="center"))
        left_box.add_widget(StyledLabel(text=str(total_items), font_size="36sp", bold=True, color=TEXT_PRI, halign="center"))
        left_box.add_widget(StyledLabel(text="ITEMS", font_size="10sp", bold=True, color=TEXT_SEC, halign="center"))
        summary_card.add_widget(left_box)

        # Center: Donut Chart
        chart_text = "ALERT" if urgent else "GOOD"
        chart = DonutChart(percentage=fill_pct, center_text=chart_text, size_hint=(None, None), size=(dp(100), dp(100)))
        summary_card.add_widget(chart)

        # Right section: Fill %
        right_box = BoxLayout(orientation="vertical", spacing=dp(4))
        right_box.add_widget(StyledLabel(text="FILL", font_size="10sp", bold=True, color=TEXT_SEC, halign="center"))
        right_box.add_widget(StyledLabel(text=f"%{fill_pct}", font_size="28sp", bold=True, color=TEXT_PRI, halign="center"))
        right_box.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Empty space
        summary_card.add_widget(right_box)

        self.content.add_widget(summary_card)

        # ── NOTIFICATIONS ──────────────────────────────────────────────────────
        self.content.add_widget(StyledLabel(text="NOTIFICATIONS", font_size="13sp", bold=True, color=TEXT_SEC, size_hint_y=None, height=dp(20)))
        
        alert_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60))
        
        # Red or green accent strip
        strip_color = DANGER if urgent else ACCENT
        strip = Widget(size_hint_x=None, width=dp(8))
        with strip.canvas.before:
            Color(*strip_color)
            strip.rect = RoundedRectangle(pos=strip.pos, size=strip.size, radius=[dp(8), 0, 0, dp(8)])
        strip.bind(pos=lambda inst, val: setattr(inst.rect, "pos", val),
                   size=lambda inst, val: setattr(inst.rect, "size", val))
        
        alert_content = CardWidget(orientation="horizontal", padding=[dp(12), dp(10)], spacing=dp(12))
        
        # Mascot image
        mascot = Image(source='assets/mascot_1.jpg', size_hint_x=None, width=dp(40))
        alert_content.add_widget(mascot)
        
        texts = BoxLayout(orientation="vertical")
        if urgent:
            texts.add_widget(StyledLabel(text=f"Critical: {urgent[0]['name']}", font_size=SIZE_BODY, bold=True, color=DANGER))
            texts.add_widget(StyledLabel(text="Expiration date is very close!", font_size=SIZE_SMALL, color=TEXT_SEC))
        else:
            texts.add_widget(StyledLabel(text="All Good!", font_size=SIZE_BODY, bold=True, color=ACCENT))
            texts.add_widget(StyledLabel(text="Try generating a new recipe.", font_size=SIZE_SMALL, color=TEXT_SEC))
            
        alert_content.add_widget(texts)
        
        alert_box.add_widget(strip)
        alert_box.add_widget(alert_content)
        self.content.add_widget(alert_box)

        # ── QUICK LIST ──────────────────────────────────────────────────────────
        self.content.add_widget(StyledLabel(text="QUICK LIST", font_size="13sp", bold=True, color=TEXT_SEC, size_hint_y=None, height=dp(20)))

        if not items:
            self.content.add_widget(StyledLabel(text="Your fridge is empty.", color=TEXT_SEC, font_size="13sp", halign="center"))
        else:
            grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, row_default_height=dp(130), row_force_default=True)
            grid.bind(minimum_height=grid.setter('height'))
            
            # Show up to 4 items
            for i, item in enumerate(sorted(items, key=lambda x: x.get('days_left', 99))):
                if i >= 4:
                    break
                days = item.get("days_left", 5)
                grid.add_widget(ProductCard(name=item["name"], days_left=days))

            self.content.add_widget(grid)
