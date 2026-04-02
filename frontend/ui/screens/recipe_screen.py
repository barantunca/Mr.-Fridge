"""
recipe_screen.py — Tarif üretme ekranı
Envanterden malzemeleri yükler, kullanıcı checkbox ile seçer,
"Tarif Üret" butonuna basınca backend /recipe/generate'e istek gönderir
ve streaming yanıtı anlık olarak ekranda gösterir.
"""
import threading

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.metrics import dp

import api_client
from ui.theme import (
    ACCENT, ACCENT2, SUCCESS, TEXT_PRI, TEXT_SEC,
    BG_CARD, SIZE_TITLE, SIZE_BODY, SIZE_SMALL
)
from ui.widgets import CardWidget, StyledLabel, GradientButton, Divider, CustomTopBar


class RecipeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ingredient_checkboxes = {}  # name → CheckBox widget
        self._streaming = False
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # ── HEADER ─────────────────────────────────────────────────────────────
        titlebar = CustomTopBar(title_text="Tarifler", right_icon="")
        root.add_widget(titlebar)

        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        # ── MALZEMELERİ SEÇ ───────────────────────────────────────────────────
        ing_card = CardWidget(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(4),
            size_hint_y=None,
            height=dp(160),
        )
        ing_header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28))
        ing_header.add_widget(StyledLabel(
            text="Malzemeleri seç:",
            font_size="13sp",
            bold=True,
            color=ACCENT2,
        ))
        # Maskot resmi (görsel olarak tatlı dursun diye köşeye eklendi)
        mascot = Image(source='assets/mascot_2.jpg', size_hint=(None, None), size=(dp(40), dp(40)))
        ing_header.add_widget(mascot)
        
        ing_card.add_widget(ing_header)
        ing_card.add_widget(Divider())

        ing_scroll = ScrollView(do_scroll_x=False)
        self.ing_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(2),
            size_hint_y=None,
        )
        self.ing_layout.bind(minimum_height=self.ing_layout.setter("height"))
        ing_scroll.add_widget(self.ing_layout)
        ing_card.add_widget(ing_scroll)
        content.add_widget(ing_card)

        # ── ÜRETİL BUTONU ─────────────────────────────────────────────────────
        self.generate_btn = GradientButton(
            text="✨  OpenAI ile Tarif Üret",
            size_hint_y=None,
            height=dp(52),
        )
        self.generate_btn.bind(on_release=self._on_generate)
        content.add_widget(self.generate_btn)

        # ── TARİF KUTUSU ──────────────────────────────────────────────────────
        recipe_card = CardWidget(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(6),
        )
        recipe_card.add_widget(StyledLabel(
            text="📜  Oluşturulan Tarif:",
            font_size="13sp",
            bold=True,
            color=ACCENT2,
            size_hint_y=None,
            height=dp(24),
        ))
        recipe_card.add_widget(Divider())

        recipe_scroll = ScrollView(do_scroll_x=False)
        self.recipe_label = Label(
            text="Malzeme seç ve 'Tarif Üret'e bas…",
            font_size=SIZE_SMALL,
            color=TEXT_SEC,
            halign="left",
            valign="top",
            size_hint_y=None,
            markup=True,
        )
        self.recipe_label.bind(
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(16))
        )
        self.recipe_label.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None))
        )
        recipe_scroll.add_widget(self.recipe_label)
        recipe_card.add_widget(recipe_scroll)
        content.add_widget(recipe_card)

        root.add_widget(content)
        self.add_widget(root)

    # ── EKRANA GİRİŞ ─────────────────────────────────────────────────────────

    def on_enter(self, *args):
        self._load_ingredients()

    # ── MALZEME YÜKLEME ───────────────────────────────────────────────────────

    def _load_ingredients(self):
        self.ing_layout.clear_widgets()
        self._ingredient_checkboxes.clear()
        self.ing_layout.add_widget(StyledLabel(
            text="⏳  Yükleniyor…",
            font_size=SIZE_SMALL,
            color=TEXT_SEC,
            size_hint_y=None,
            height=dp(28),
        ))
        threading.Thread(target=self._fetch_ingredients, daemon=True).start()

    def _fetch_ingredients(self):
        categorized = api_client.get_categorized_inventory()
        Clock.schedule_once(lambda dt: self._render_ingredients(categorized))

    def _render_ingredients(self, categorized: dict):
        self.ing_layout.clear_widgets()
        self._ingredient_checkboxes.clear()

        if not categorized:
            self.ing_layout.add_widget(StyledLabel(
                text="Envanter boş. Önce ürün ekle.",
                font_size=SIZE_SMALL,
                color=TEXT_SEC,
                size_hint_y=None,
                height=dp(28),
            ))
            return

        for category, names in sorted(categorized.items()):
            for name in names:
                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
                cb = CheckBox(active=True, size_hint_x=None, width=dp(32))
                lbl = StyledLabel(text=name, font_size=SIZE_BODY, color=TEXT_PRI)
                row.add_widget(cb)
                row.add_widget(lbl)
                self.ing_layout.add_widget(row)
                self._ingredient_checkboxes[name] = cb

    # ── TARİF OLUŞTUR ─────────────────────────────────────────────────────────

    def _on_generate(self, *args):
        if self._streaming:
            return

        selected = [
            name for name, cb in self._ingredient_checkboxes.items() if cb.active
        ]
        if not selected:
            self.recipe_label.text = "[color=ef4444]⚠️ En az bir malzeme seçmelisiniz.[/color]"
            return

        self._streaming = True
        self.generate_btn.disabled = True
        self.generate_btn.text = "⏳  Üretiliyor…"
        self.recipe_label.color = TEXT_PRI
        self.recipe_label.text = ""

        threading.Thread(
            target=self._stream_recipe, args=(selected,), daemon=True
        ).start()

    def _stream_recipe(self, ingredients: list):
        for chunk in api_client.generate_recipe_stream(ingredients):
            final_chunk = chunk  # lambda kapanımı için
            Clock.schedule_once(lambda dt, c=final_chunk: self._append_text(c))
        Clock.schedule_once(self._on_stream_done)

    def _append_text(self, text: str):
        self.recipe_label.text += text

    def _on_stream_done(self, *args):
        self._streaming = False
        self.generate_btn.disabled = False
        self.generate_btn.text = "✨  Tekrar Üret"

