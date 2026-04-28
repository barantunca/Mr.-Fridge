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
from kivy.clock import Clock

from ui.theme import (
    BG_CARD, ACCENT, ACCENT2, SUCCESS, DANGER,
    TEXT_PRI, TEXT_SEC, BORDER, TRANSPARENT,
    SIZE_TITLE, SIZE_BODY, SIZE_SMALL
)


class CardWidget(BoxLayout):
    def __init__(self, **kwargs):
        self.bg_color = kwargs.pop("bg_color", BG_CARD)
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
            Color(*self.bg_color)
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

class CancelButton(Button):
    """Gri kenarlıklı 'iptal' butonu."""
    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", TRANSPARENT)
        kwargs.setdefault("color", TEXT_SEC)
        kwargs.setdefault("font_size", SIZE_SMALL)
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        if not self.canvas: return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*TEXT_SEC)
            from kivy.graphics import Line
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
    def __init__(self, percentage, center_text, color=None, **kwargs):
        super().__init__(**kwargs)
        self.percentage = percentage
        self.center_text = center_text
        self.color = color or ACCENT
        self.bind(pos=self._redraw, size=self._redraw)
        
        # Center Label
        self.lbl = StyledLabel(text=self.center_text, font_size=SIZE_SMALL, bold=True, color=self.color, halign="center")
        self.add_widget(self.lbl)
        
    def _redraw(self, *args):
        self.lbl.pos = self.pos
        self.lbl.size = self.size
        if not self.canvas: return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BORDER)
            Line(circle=(self.center_x, self.center_y, min(self.width, self.height)/2 - dp(4)), width=dp(8))
            Color(*self.color)
            angle_end = 360 * (self.percentage / 100)
            Line(circle=(self.center_x, self.center_y, min(self.width, self.height)/2 - dp(4), 0, angle_end), width=dp(8))


class ProductCard(CardWidget):
    """Hızlı Liste ve Envanterde kullanılan ürün/malzeme kartı."""
    def __init__(self, name, days_left, category="Diğer", total_days=14, item_id=None, on_delete=None, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", dp(12))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        
        self.item_id = item_id
        self.item_name = name
        self.item_category = category
        self.on_delete_callback = on_delete
        self._long_press_event = None
        self._is_delete_mode = False
        
        # Kategoriye göre ikon seçimi
        cat_lower = category.lower()
        
        if "sebze" in cat_lower or "yeşillik" in cat_lower:
            img_src = 'assets/Sebzeler.png'
        elif "süt" in cat_lower or "peynir" in cat_lower or "yoğurt" in cat_lower:
            img_src = 'assets/SutUrunleri.png'
        elif "meyve" in cat_lower:
            img_src = 'assets/Meyveler.png'
        elif "kahvaltı" in cat_lower or "yumurta" in cat_lower or "reçel" in cat_lower:
            img_src = 'assets/Kahvaltilik.png'
        elif "içecek" in cat_lower or "su" in cat_lower or "kola" in cat_lower:
            img_src = 'assets/Icecekler.png'
        elif "hamur" in cat_lower or "ekmek" in cat_lower or "makarna" in cat_lower:
            img_src = 'assets/Hamur_isi.png'
        elif "et" in cat_lower or "tavuk" in cat_lower or "kıyma" in cat_lower or "sucuk" in cat_lower or "salam" in cat_lower:
            img_src = 'assets/EtUrunleri.png'
        elif "bakliyat" in cat_lower or "pirinç" in cat_lower or "mercimek" in cat_lower:
            img_src = 'assets/Bakliyatlar.png'
        else:
            img_src = 'assets/Diger.png'
        
        # Resim (Maskot olarak)
        self.add_widget(Image(source=img_src, size_hint_y=None, height=dp(50)))
        
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
            # Line'ın kendi kalınlığından (width) dolayı kenarlardan taşmasını engellemek için pay (pad) bırakıyoruz
            pad = dp(3) 
            start_x = self.progress_container.x + pad
            end_x = self.progress_container.right - pad
            
            if end_x <= start_x:
                return # Container çok küçükse çizme
                
            Color(*BORDER)
            Line(points=[start_x, self.progress_container.center_y, end_x, self.progress_container.center_y], width=dp(2.5), cap='round')
            
            Color(*self.color_val)
            ratio = max(0, min(1, self.days_left / self.total_days))
            fill_end = start_x + (end_x - start_x) * ratio
            
            if fill_end > start_x:
                Line(points=[start_x, self.progress_container.center_y, fill_end, self.progress_container.center_y], width=dp(2.5), cap='round')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not self._is_delete_mode:
                self._long_press_event = Clock.schedule_once(self._on_long_press, 0.6)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._long_press_event:
            self._long_press_event.cancel()
            self._long_press_event = None
        return super().on_touch_up(touch)
        
    def on_touch_move(self, touch):
        if self._long_press_event:
            if abs(touch.dx) > dp(5) or abs(touch.dy) > dp(5):
                self._long_press_event.cancel()
                self._long_press_event = None
        return super().on_touch_move(touch)
        
    def _on_long_press(self, dt):
        self._long_press_event = None
        if not self.on_delete_callback or not self.item_id:
            return
            
        from kivy.uix.modalview import ModalView
        from kivy.uix.floatlayout import FloatLayout
        from kivy.core.window import Window
        from kivy.animation import Animation
        
        # Kartın ekrandaki mutlak pozisyonunu hesapla
        x, y = self.to_window(self.x, self.y)
        
        self.overlay_modal = ModalView(
            size_hint=(1, 1), 
            background_color=(0, 0, 0, 0.75), # Ekranı karartan yarı saydam katman
            auto_dismiss=True
        )
        
        layout = FloatLayout()
        
        # Orijinal renk ve parlaklığı koruyan Klon Kart
        clone = ProductCard(name=self.item_name, days_left=self.days_left, category=self.item_category, item_id=self.item_id)
        clone.size_hint = (None, None)
        clone.size = self.size
        clone.pos = (x, y)
        self.clone_ref = clone
        
        # SİL Butonu (Yukarıda)
        del_y = y + self.height + dp(15)
        if del_y + dp(40) > Window.height:
            del_y = Window.height - dp(45)
            
        del_btn = DangerButton(text="SİL (Yukarı Sürükle)", font_size="13sp", size_hint=(None, None), size=(self.width, dp(40)), pos=(x, del_y))
        del_btn.bind(on_release=self._confirm_delete)
        self.del_btn_ref = del_btn
        
        # İPTAL Butonu (Aşağıda)
        cancel_y = y - dp(55)
        if cancel_y < 0:
            cancel_y = dp(10)
            
        cancel_btn = CancelButton(text="İPTAL (Aşağı Sürükle)", font_size="13sp", size_hint=(None, None), size=(self.width, dp(40)), pos=(x, cancel_y))
        cancel_btn.bind(on_release=lambda *a: self.overlay_modal.dismiss())
        self.cancel_btn_ref = cancel_btn
        
        layout.add_widget(del_btn)
        layout.add_widget(cancel_btn)
        layout.add_widget(clone)
        self.overlay_modal.add_widget(layout)
        
        # --- Sürükle Bırak (Drag) Mantığı ---
        self._drag_start_y = y
        
        def clone_on_touch_down(touch):
            if clone.collide_point(*touch.pos):
                touch.grab(clone)
                return True
            return False

        def clone_on_touch_move(touch):
            if touch.grab_current is clone:
                # Yukarı veya aşağı serbest sürükleme
                clone.y += touch.dy
                    
                # Yukarıda SİL butonuna değerse kırmızı yap (Görsel geribildirim)
                if clone.collide_widget(del_btn):
                    if clone.bg_color != (0.9, 0.2, 0.2, 0.85):
                        clone.bg_color = (0.9, 0.2, 0.2, 0.85)
                        clone._redraw()
                # Aşağıda İPTAL butonuna değerse gri yap
                elif clone.collide_widget(cancel_btn):
                    if clone.bg_color != (0.4, 0.4, 0.4, 0.85):
                        clone.bg_color = (0.4, 0.4, 0.4, 0.85)
                        clone._redraw()
                else:
                    if clone.bg_color != BG_CARD:
                        clone.bg_color = BG_CARD
                        clone._redraw()
                        
                return True
            return False

        def clone_on_touch_up(touch):
            if touch.grab_current is clone:
                touch.ungrab(clone)
                # Bırakıldığında butonlarla çarpışma (drop) kontrolü
                if clone.collide_widget(del_btn):
                    self._confirm_delete()
                elif clone.collide_widget(cancel_btn):
                    self.overlay_modal.dismiss()
                else:
                    # Rengi normale döndür ve geri yaylan
                    clone.bg_color = BG_CARD
                    clone._redraw()
                    anim = Animation(y=self._drag_start_y, t='out_bounce', duration=0.3)
                    anim.start(clone)
                return True
            return False

        clone.on_touch_down = clone_on_touch_down
        clone.on_touch_move = clone_on_touch_move
        clone.on_touch_up = clone_on_touch_up
        
        self.overlay_modal.open()

    def _confirm_delete(self, *args):
        # 1. Bubble Burst (Patlama) Animasyonu
        if hasattr(self, 'clone_ref') and self.clone_ref:
            from kivy.animation import Animation
            
            # Etraftaki butonları hemen gizle
            if hasattr(self, 'del_btn_ref') and self.del_btn_ref:
                self.del_btn_ref.opacity = 0
            if hasattr(self, 'cancel_btn_ref') and self.cancel_btn_ref:
                self.cancel_btn_ref.opacity = 0
                
            center_x, center_y = self.clone_ref.center
            
            # Animasyon Zinciri: Önce %10 büyü (şişme), sonra sıfıra küçülerek şeffaflaş (patlama)
            anim = Animation(size=(self.width * 1.1, self.height * 1.1), center=(center_x, center_y), duration=0.1) + \
                   Animation(size=(0, 0), center=(center_x, center_y), opacity=0, duration=0.2)
                   
            def on_burst_complete(*a):
                if hasattr(self, 'overlay_modal') and self.overlay_modal:
                    self.overlay_modal.dismiss()
                self._do_actual_delete()
                
            anim.bind(on_complete=on_burst_complete)
            anim.start(self.clone_ref)
        else:
            if hasattr(self, 'overlay_modal') and self.overlay_modal:
                self.overlay_modal.dismiss()
            self._do_actual_delete()

    def _do_actual_delete(self):
        # 2. Orijinal kartın kaybolma animasyonu (Yumuşak kayma hazırlığı)
        from kivy.animation import Animation
        anim = Animation(opacity=0, duration=0.15)
        
        def final_delete(*a):
            if self.on_delete_callback and self.item_id:
                self.on_delete_callback(self.item_id)
                
        anim.bind(on_complete=final_delete)
        anim.start(self)

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