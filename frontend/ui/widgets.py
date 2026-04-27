"""
widgets.py — Tekrar kullanılabilir, stillenmiş Kivy bileşenleri
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp

from ui.theme import (
    BG_CARD, ACCENT, ACCENT2, SUCCESS, DANGER,
    TEXT_PRI, TEXT_SEC, BORDER, TRANSPARENT,
    SIZE_TITLE, SIZE_BODY, SIZE_SMALL
)


class CardWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        if not self.canvas: return
        self.canvas.before.clear()
        with self.canvas.before:
            # Subtle Shadow (Gölge efekti)
            Color(0, 0, 0, 0.05) # %5 şeffaf siyah
            RoundedRectangle(pos=(self.x + dp(2), self.y - dp(2)), 
                             size=self.size, radius=[dp(18)])
            # Main Card
            Color(*BG_CARD)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])


class StyledLabel(Label):
    """Varsayılan renk ve metin ayarlı label."""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", TEXT_PRI)
        kwargs.setdefault("font_size", SIZE_BODY)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None) if self.halign != "center" else (self.width, None)


class GradientButton(Button):
    """Mor gradyan arka planlı buton."""

    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", TRANSPARENT)
        kwargs.setdefault("color", TEXT_PRI)
        kwargs.setdefault("font_size", SIZE_BODY)
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        if not self.canvas: return
        self.canvas.before.clear()
        with self.canvas.before:
            # Sol → sağ gradyan simülasyonu (iki renk karışımı)
            Color(*ACCENT)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])

    def on_size(self, *args):
        self._redraw()

    def on_pos(self, *args):
        self._redraw()


class DangerButton(Button):
    """Kırmızı kenarlıklı 'sil' butonu."""

    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", TRANSPARENT)
        kwargs.setdefault("color", DANGER)
        kwargs.setdefault("font_size", SIZE_SMALL)
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        if not self.canvas: return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*DANGER)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(6)), width=1)

    def on_size(self, *args):
        self._redraw()

    def on_pos(self, *args):
        self._redraw()


class SuccessButton(Button):
    """Yeşil 'ekle/onayla' butonu."""

    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", TRANSPARENT)
        kwargs.setdefault("color", TEXT_PRI)
        kwargs.setdefault("font_size", SIZE_BODY)
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        if not self.canvas: return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*SUCCESS)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])

    def on_size(self, *args):
        self._redraw()

    def on_pos(self, *args):
        self._redraw()


class Divider(Widget):
    """İnce yatay çizgi."""

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(1))
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        if not self.canvas: return
        self.canvas.clear()
        with self.canvas:
            Color(*BORDER)
            Line(points=[self.x, self.y + self.height / 2,
                         self.x + self.width, self.y + self.height / 2], width=1)


class CustomTopBar(BoxLayout):
    """Her ekranın üstünde yer alan özel başlık barı."""
    def __init__(self, title_text, right_icon=None, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(56))
        kwargs.setdefault("padding", [dp(16), dp(8)])
        kwargs.setdefault("spacing", dp(16))
        super().__init__(**kwargs)
        
        # Maskot İkonu
        self.add_widget(Image(source='assets/mascot_4.jpg', size_hint_x=None, width=dp(40)))
        
        # Başlık
        self.title_lbl = StyledLabel(text=title_text, font_size=SIZE_TITLE, bold=True, halign="center", color=TEXT_PRI)
        self.add_widget(self.title_lbl)
        
        # Sağ İkon (PNG İkon kullanımına uygun)
        if right_icon:
            self.icon_widget = Image(source=right_icon, size_hint_x=None, width=dp(28))
            self.add_widget(self.icon_widget)
        else:
            self.add_widget(Widget(size_hint_x=None, width=dp(28))) 


class DonutChart(Widget):
    """Donut (Halka) grafik."""
    def __init__(self, percentage, center_text, **kwargs):
        super().__init__(**kwargs)
        self.percentage = percentage
        self.center_text = center_text
        self.bind(pos=self._redraw, size=self._redraw)
        
        # Center Label
        self.lbl = StyledLabel(text=self.center_text, font_size=SIZE_SMALL, bold=True, color=ACCENT, halign="center")
        self.add_widget(self.lbl)
        
    def _redraw(self, *args):
        self.lbl.pos = self.pos
        self.lbl.size = self.size
        if not self.canvas: return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BORDER)
            Line(circle=(self.center_x, self.center_y, min(self.width, self.height)/2 - dp(4)), width=dp(8))
            Color(*ACCENT)
            angle_end = 360 * (self.percentage / 100)
            Line(circle=(self.center_x, self.center_y, min(self.width, self.height)/2 - dp(4), 0, angle_end), width=dp(8))


class ProductCard(CardWidget):
    """Hızlı Liste ve Envanterde kullanılan ürün/malzeme kartı."""
    def __init__(self, name, days_left, total_days=14, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", dp(12))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        
        # Resim (Maskot olarak)
        self.add_widget(Image(source='assets/mascot_4.png', size_hint_y=None, height=dp(50)))
        
        # İsim
        self.add_widget(StyledLabel(text=name, font_size=SIZE_BODY, bold=True, halign="center", size_hint_y=None, height=dp(20)))
        
        # Gün
        color_val = ACCENT if days_left <= 2 else (SUCCESS if days_left <= 5 else ACCENT2)
        days_str = "SÜRESİ DOLDU" if days_left <= 0 else f"{days_left} GÜN KALDI"
        self.add_widget(StyledLabel(text=days_str, font_size=SIZE_SMALL, bold=True, color=TEXT_SEC, halign="center", size_hint_y=None, height=dp(16)))
        
        # İlerleme Çubuğu Container
        self.progress_container = Widget(size_hint_y=None, height=dp(4))
        self.add_widget(self.progress_container)
        
        self.days_left = days_left
        self.total_days = total_days
        self.color_val = color_val
        self.progress_container.bind(pos=self._draw_progress, size=self._draw_progress)

    def _draw_progress(self, *args):
        if not self.progress_container.canvas: return
        self.progress_container.canvas.clear()
        with self.progress_container.canvas:
            Color(*BORDER)
            Line(points=[self.progress_container.x, self.progress_container.center_y, self.progress_container.right, self.progress_container.center_y], width=dp(2))
            Color(*self.color_val)
            ratio = max(0, min(1, self.days_left / self.total_days))
            end_x = self.progress_container.x + (self.progress_container.width * ratio)
            if end_x > self.progress_container.x:
                Line(points=[self.progress_container.x, self.progress_container.center_y, end_x, self.progress_container.center_y], width=dp(2))

class IconButton(BoxLayout):
    """İkon (PNG) ve Metni yan yana gösteren buton."""
    def __init__(self, icon_source, button_text="", **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("spacing", dp(8))
        kwargs.setdefault("padding", [dp(12), dp(8)])
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(48))
        super().__init__(**kwargs)

        self.icon = Image(source=icon_source, size_hint_x=None, width=dp(24))
        self.add_widget(self.icon)

        if button_text:
            self.label = StyledLabel(text=button_text, font_size=SIZE_BODY, bold=True)
            self.add_widget(self.label)