"""
profile_screen.py — Profil ekranı
Kullanıcı bilgileri ve ayarlar menüsünü içerir.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle

from ui.theme import TEXT_PRI, TEXT_SEC, SUCCESS, BG_CARD, TRANSPARENT, SIZE_BODY, SIZE_SMALL, SIZE_TITLE, store
from ui.widgets import CardWidget, StyledLabel, CustomTopBar, SuccessButton

class MenuRow(ButtonBehavior, BoxLayout):
    def __init__(self, title, is_expanded, icon_source=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(20), dp(10), dp(16), dp(10)] # Sol padding
        self.spacing = dp(15) # İkon ve metin arası boşluk
        
        with self.canvas.before:
            Color(*BG_CARD)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # 1. İkon ekleme
        if icon_source:
            self.add_widget(Image(
                source=icon_source,
                size_hint=(None, None),
                size=(dp(28), dp(28)),
                pos_hint={'center_y': 0.5}
            ))
        
        # 2. Başlık (Metin)
        self.add_widget(StyledLabel(
            text=title, 
            font_size=SIZE_BODY, 
            bold=True, 
            color=TEXT_PRI,
            halign="left"
        ))
        
        # 3. Aşağı/Yukarı Oku
        icon = "v" if not is_expanded else "^" 
        self.add_widget(StyledLabel(
            text=icon, 
            font_size="18sp", 
            color=TEXT_SEC, 
            size_hint_x=None, 
            width=dp(30), 
            halign="right"
        ))
        
    # EKSİK OLAN VE HATAYA SEBEP OLAN FONKSİYON:
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ProfileScreen(Screen):
    """
    Kullanıcının kişisel bilgilerini ve akıllı tarif asistanı için 
    yemek tercihlerini (alerjiler, diyet, porsiyon) yönettiği ekran.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Verileri çek
        self.user_data = store.get('user') if store.exists('user') else {}
        self.avatar_list = ['assets/mascot_1.png', 'assets/mascot_2.png', 'assets/mascot_3.png', 'assets/mascot_4.png']
        self.current_avatar_idx = self.avatar_list.index(self.user_data.get('avatar', 'assets/mascot_3.png')) if self.user_data.get('avatar', 'assets/mascot_3.png') in self.avatar_list else 2
        
        self.expanded_section = None # "kisisel", "tercihler" veya None
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        root.add_widget(CustomTopBar(title_text="Profil", right_icon=""))

        self.scroll = ScrollView()
        self.content_area = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), size_hint_y=None)
        self.content_area.bind(minimum_height=self.content_area.setter("height"))
        
        self.scroll.add_widget(self.content_area)
        root.add_widget(self.scroll)
        self.add_widget(root)
        
        self._render_content()

    def _render_content(self):
        """Açılır kapanır menü durumuna (expanded_section) göre ekranı baştan çizer."""
        self.content_area.clear_widgets()
        
        # 1. Avatar 
        avatar_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(120), spacing=dp(10))
        self.avatar_img = Button(
            background_normal=self.avatar_list[self.current_avatar_idx],
            background_down=self.avatar_list[self.current_avatar_idx],
            size_hint=(None, None), size=(dp(80), dp(80)),
            pos_hint={'center_x': 0.5}
        )
        self.avatar_img.bind(on_release=self._cycle_avatar)
        avatar_box.add_widget(self.avatar_img)
        avatar_box.add_widget(StyledLabel(text="Değiştirmek için fotoğrafa dokun", font_size="10sp", color=TEXT_SEC, halign="center"))
        self.content_area.add_widget(avatar_box)

        # 2. Kişisel Bilgiler Satırı (İkon eklendi)
        row1 = MenuRow(
            title="Kişisel Bilgiler", 
            is_expanded=(self.expanded_section == "kisisel"),
            icon_source="assets/KisiselBilgiler.png" # İkon dosyanın adı
        )
        row1.bind(on_release=lambda x: self._toggle_section("kisisel"))
        self.content_area.add_widget(row1)
        
        if self.expanded_section == "kisisel":
            self.content_area.add_widget(self._build_kisisel_content())

        # 3. Yemek Tercihleri Satırı (İkon eklendi)
        row2 = MenuRow(
            title="Yemek Tercihleri", 
            is_expanded=(self.expanded_section == "tercihler"),
            icon_source="assets/YemekTercihleri.png" # İkon dosyanın adı
        )
        row2.bind(on_release=lambda x: self._toggle_section("tercihler"))
        self.content_area.add_widget(row2)
        
        if self.expanded_section == "tercihler":
            self.content_area.add_widget(self._build_tercihler_content())
            
        self.content_area.add_widget(Widget(size_hint_y=None, height=dp(50))) # Alttan boşluk

    def _toggle_section(self, section):
        """İlgili menü satırını (accordion) açar veya zaten açıksa kapatır."""
        if self.expanded_section == section:
            self.expanded_section = None # Kapat
        else:
            self.expanded_section = section # Aç
        self._render_content()

    def _build_kisisel_content(self):
        """Kişisel Bilgiler sekmesinin form içeriğini (İsim, E-posta, Şifre) oluşturur."""
        profile_card = CardWidget(orientation="vertical", padding=dp(16), spacing=dp(10), size_hint_y=None, height=dp(200))
        
        self.name_input = self._create_input("İsim", self.user_data.get("name", ""))
        self.email_input = self._create_input("E-posta", self.user_data.get("email", ""))
        self.pass_input = self._create_input("Şifre", self.user_data.get("password", ""), password=True)
        
        profile_card.add_widget(self.name_input)
        profile_card.add_widget(self.email_input)
        profile_card.add_widget(self.pass_input)
        
        save_btn = SuccessButton(text="BİLGİLERİ KAYDET", size_hint_y=None, height=dp(50))
        save_btn.bind(on_release=self._save_kisisel)
        profile_card.add_widget(save_btn)
        
        # Bu kart biraz daha büyük olmalı ki buton sığsın
        profile_card.height = dp(220)
        return profile_card

    def _build_tercihler_content(self):
        """Yemek Tercihleri sekmesinin form içeriğini (Alerji, Diyet Türü, Porsiyon) oluşturur."""
        pref_card = CardWidget(orientation="vertical", padding=dp(16), spacing=dp(20), size_hint_y=None, height=dp(220))
        
        # Alerjiler
        alerji_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(60), spacing=dp(5))
        alerji_box.add_widget(StyledLabel(text="Alerjiler ve Hassasiyetler (Örn: Glüten, Fıstık)", font_size=SIZE_BODY, color=TEXT_PRI))
        self.allergy_input = TextInput(
            text=self.user_data.get("allergies", ""), multiline=False,
            background_normal="", background_active="",
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            padding=[dp(10), dp(10)]
        )
        alerji_box.add_widget(self.allergy_input)
        pref_card.add_widget(alerji_box)

        # Diyet Türü
        diyet_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        diyet_box.add_widget(StyledLabel(text="Diyet Türü", font_size=SIZE_BODY, color=TEXT_PRI))
        self.diet_spinner = Spinner(
            text=self.user_data.get("diet", "Hepçil"),
            values=("Hepçil", "Vegan", "Vejetaryen", "Ketojenik", "Düşük Karbonhidratlı"),
            size_hint_x=None, width=dp(150),
            background_normal="", background_down="",
            background_color=(0.99, 0.96, 0.90, 1), color=(0.1,0.1,0.1,1)
        )
        diyet_box.add_widget(self.diet_spinner)
        pref_card.add_widget(diyet_box)

        # Porsiyon
        porsiyon_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        porsiyon_box.add_widget(StyledLabel(text="Varsayılan Porsiyon", font_size=SIZE_BODY, color=TEXT_PRI))
        self.portion_spinner = Spinner(
            text=self.user_data.get("portion", "2 Kişilik"),
            values=("1 Kişilik", "2 Kişilik", "3 Kişilik", "4 Kişilik", "5+ Kişilik"),
            size_hint_x=None, width=dp(150),
            background_normal="", background_down="",
            background_color=(0.99, 0.96, 0.90, 1), color=(0.1,0.1,0.1,1)
        )
        porsiyon_box.add_widget(self.portion_spinner)
        pref_card.add_widget(porsiyon_box)
        
        save_btn = SuccessButton(text="TERCİHLERİ KAYDET", size_hint_y=None, height=dp(50))
        save_btn.bind(on_release=self._save_tercihler)
        pref_card.add_widget(save_btn)
        
        pref_card.height = dp(280)
        return pref_card

    def _create_input(self, hint, text, password=False):
        box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        box.add_widget(StyledLabel(text=hint, size_hint_x=0.3, font_size=SIZE_BODY, color=TEXT_SEC))
        inp = TextInput(
            text=text, password=password, multiline=False,
            background_normal="", background_active="",
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            padding=[dp(10), dp(10)]
        )
        box.add_widget(inp)
        return box

    def _cycle_avatar(self, instance):
        self.current_avatar_idx = (self.current_avatar_idx + 1) % len(self.avatar_list)
        instance.background_normal = self.avatar_list[self.current_avatar_idx]
        instance.background_down = self.avatar_list[self.current_avatar_idx]

    def _save_kisisel(self, instance):
        """Kişisel bilgileri yerel JSON dosyasına kaydeder ve butonda geri bildirim gösterir."""
        self.user_data['name'] = self.name_input.children[0].text
        self.user_data['email'] = self.email_input.children[0].text
        self.user_data['password'] = self.pass_input.children[0].text
        self.user_data['avatar'] = self.avatar_list[self.current_avatar_idx]
        store.put('user', **self.user_data)
        
        instance.text = "BAŞARIYLA KAYDEDİLDİ!"
        Clock.schedule_once(lambda dt: setattr(instance, 'text', 'KİŞİSEL BİLGİLERİ KAYDET'), 2)
        
    def _save_tercihler(self, instance):
        """Akıllı tarif tercihlerini yerel JSON dosyasına kaydeder."""
        self.user_data['allergies'] = self.allergy_input.text
        self.user_data['diet'] = self.diet_spinner.text
        self.user_data['portion'] = self.portion_spinner.text
        store.put('user', **self.user_data)
        
        instance.text = "BAŞARIYLA KAYDEDİLDİ!"
        Clock.schedule_once(lambda dt: setattr(instance, 'text', 'TERCİHLERİ KAYDET'), 2)
