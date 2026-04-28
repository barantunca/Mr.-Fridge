"""
home_screen.py — Ana Sayfa ekranı
Buzdolabı özeti, bildirimler ve hızlı liste gösterir.
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
    ACCENT, ACCENT2, DANGER, TEXT_PRI, TEXT_SEC, SIZE_TITLE, SIZE_BODY, SIZE_SMALL, get_capacity_color, get_fridge_capacity
)
from ui.widgets import CardWidget, StyledLabel, CustomTopBar, DonutChart, ProductCard

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # ── HEADER (Özel Top Bar) ──────────────────────────────────────────────
        root.add_widget(CustomTopBar(title_text="Ana Sayfa", right_icon=""))

        # İçeriği kaydırılabilir yapalım
        scroll = ScrollView(do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(20), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self, *args):
        # Ekrana her dönüldüğünde envanteri çek
        self.content.clear_widgets()
        self.content.add_widget(StyledLabel(text="Yükleniyor...", color=TEXT_SEC, font_size="14sp", halign="center"))
        threading.Thread(target=self._fetch_summary, daemon=True).start()

    def _fetch_summary(self):
        items = api_client.get_inventory_items()
        Clock.schedule_once(lambda dt: self._render_ui(items))

    def _render_ui(self, items):
        self.content.clear_widgets()
        
        total_items = len(items)
        capacity = get_fridge_capacity()
        fill_pct = min(100, int((total_items / capacity) * 100)) if items else 0

        # Uyarı olacak ürünleri hesapla
        urgent = [i for i in items if i.get("days_left", 5) <= 3]
        
        # ── BUZDOLABI ÖZETİ KARTI ─────────────────────────────────────────────
        summary_card = CardWidget(orientation="horizontal", padding=dp(16), spacing=dp(16), size_hint_y=None, height=dp(140))
        
        # Sol Kısım: Toplam Ürün
        left_box = BoxLayout(orientation="vertical", spacing=dp(4))
        left_box.add_widget(StyledLabel(text="TOPLAM", font_size="10sp", bold=True, color=TEXT_SEC, halign="center"))
        left_box.add_widget(StyledLabel(text=str(total_items), font_size="36sp", bold=True, color=TEXT_PRI, halign="center"))
        left_box.add_widget(StyledLabel(text="ÜRÜN", font_size="10sp", bold=True, color=TEXT_SEC, halign="center"))
        summary_card.add_widget(left_box)

        # Orta Kısım: Donut Chart
        if fill_pct == 0:
            chart_text = "Boş"
        elif 1 <= fill_pct <= 25:
            chart_text = "Neredeyse\nBoş"
        elif 26 <= fill_pct <= 55:
            chart_text = "Ortalama"
        elif 56 <= fill_pct <= 85:
            chart_text = "Dolu"
        else:
            chart_text = "Ful\nDolu"
            
        dyn_color = get_capacity_color(fill_pct)
        chart = DonutChart(percentage=fill_pct, center_text=chart_text, color=dyn_color, size_hint=(None, None), size=(dp(100), dp(100)))
        summary_card.add_widget(chart)

        # Sağ Kısım: Doluluk
        right_box = BoxLayout(orientation="vertical", spacing=dp(4))
        right_box.add_widget(StyledLabel(text="DOLULUK", font_size="10sp", bold=True, color=TEXT_SEC, halign="center"))
        right_box.add_widget(StyledLabel(text=f"%{fill_pct}", font_size="28sp", bold=True, color=dyn_color, halign="center"))
        right_box.add_widget(Widget(size_hint_y=None, height=dp(10))) # Empty space
        summary_card.add_widget(right_box)

        self.content.add_widget(summary_card)

        # ── BİLDİRİMLER ───────────────────────────────────────────────────────
        self.content.add_widget(StyledLabel(text="BİLDİRİMLER", font_size="13sp", bold=True, color=TEXT_SEC, size_hint_y=None, height=dp(20)))
        
        alert_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60))
        
        # Kırmızı veya yeşil şerit
        strip_color = DANGER if urgent else ACCENT
        strip = Widget(size_hint_x=None, width=dp(8))
        with strip.canvas.before:
            Color(*strip_color)
            strip.rect = RoundedRectangle(pos=strip.pos, size=strip.size, radius=[dp(8), 0, 0, dp(8)])
        strip.bind(pos=lambda inst, val: setattr(inst.rect, "pos", val),
                   size=lambda inst, val: setattr(inst.rect, "size", val))
        
        alert_content = CardWidget(orientation="horizontal", padding=[dp(12), dp(10)], spacing=dp(12))
        
        # Mascot Görseli
        mascot = Image(source='assets/mascot_1.png', size_hint_x=None, width=dp(40))
        alert_content.add_widget(mascot)
        
        texts = BoxLayout(orientation="vertical")
        if urgent:
            texts.add_widget(StyledLabel(text=f"Kritik: {urgent[0]['name']}", font_size=SIZE_BODY, bold=True, color=DANGER))
            texts.add_widget(StyledLabel(text="Tüketim tarihi çok yakın!", font_size=SIZE_SMALL, color=TEXT_SEC))
        else:
            texts.add_widget(StyledLabel(text="Her Şey Yolunda!", font_size=SIZE_BODY, bold=True, color=ACCENT))
            texts.add_widget(StyledLabel(text="Hemen yeni bir tarif üret.", font_size=SIZE_SMALL, color=TEXT_SEC))
            
        alert_content.add_widget(texts)
        
        alert_box.add_widget(strip)
        alert_box.add_widget(alert_content)
        self.content.add_widget(alert_box)

        # ── EN SON EKLENENLER ───────────────────────────────────────────────────────
        self.content.add_widget(StyledLabel(text="EN SON EKLENENLER", font_size="13sp", bold=True, color=TEXT_SEC, size_hint_y=None, height=dp(20)))

        if not items:
            self.content.add_widget(StyledLabel(text="Buzdolabın boş.", color=TEXT_SEC, font_size="13sp", halign="center"))
        else:
            grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, row_default_height=dp(130), row_force_default=True)
            grid.bind(minimum_height=grid.setter('height'))
            
            # Show up to 4 items (Zaten backend'den en son eklenenler en üstte geliyor)
            count = 0
            for i, item in enumerate(items):
                if i >= 4:
                    break
                days = item.get("days_left", 5)
                card = ProductCard(
                    name=item["name"], 
                    category=item.get("category", "Diğer"),
                    days_left=days,
                    item_id=item.get("id"),
                    on_delete=self._delete_item
                )
                grid.add_widget(card)
                count += 1

            if count % 2 != 0:
                grid.add_widget(Widget()) # Force second column to keep card width 50%

            self.content.add_widget(grid)

    def _delete_item(self, item_id: int):
        threading.Thread(target=lambda: self._do_delete(item_id), daemon=True).start()

    def _do_delete(self, item_id: int):
        api_client.delete_item(item_id)
        Clock.schedule_once(lambda dt: self._fetch_summary())
