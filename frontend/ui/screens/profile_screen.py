"""
profile_screen.py — Profile screen
Contains user information and settings menu.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.metrics import dp

from ui.theme import TEXT_PRI, TEXT_SEC, SUCCESS, BG_CARD, DANGER, TEXT_SEC, TRANSPARENT, SIZE_BODY, SIZE_SMALL, SIZE_TITLE
from ui.widgets import CardWidget, StyledLabel, Divider

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(30))
        
        # 1. Avatar and User Information
        avatar_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(150), spacing=dp(10))
        
        # Circular mascot avatar
        avatar_label = Image(
            source='assets/mascot_3.jpg',
            size_hint_y=None, 
            height=dp(80)
        )
        avatar_box.add_widget(avatar_label)
        
        # Name and email
        avatar_box.add_widget(StyledLabel(
            text="Mr. Fridge", 
            font_size=SIZE_TITLE, 
            bold=True, 
            halign="center", 
            color=TEXT_PRI,
            size_hint_y=None, height=dp(30)
        ))
        avatar_box.add_widget(StyledLabel(
            text="fridgedayi@email.com", 
            font_size=SIZE_SMALL, 
            halign="center", 
            color=TEXT_SEC,
            size_hint_y=None, height=dp(20)
        ))
        
        root.add_widget(avatar_box)
        
        # 2. Menu Panel (single tall white menu card)
        menu_card = CardWidget(orientation="vertical", padding=[dp(16), dp(8)], spacing=0, size_hint_y=None, height=dp(260))
        
        menu_items = [
            ("", "Account Settings"),
            ("", "Food Preferences"),
            ("", "Notifications"),
            ("", "App Settings"),
            ("", "Support"),
        ]
        
        for i, (emoji, title) in enumerate(menu_items):
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(16))
            row.add_widget(StyledLabel(text=emoji, font_size="20sp", size_hint_x=None, width=dp(30)))
            row.add_widget(StyledLabel(text=title, font_size=SIZE_BODY, bold=True, color=TEXT_PRI))
            menu_card.add_widget(row)
            if i < len(menu_items) - 1:
                menu_card.add_widget(Divider())
                
        root.add_widget(menu_card)
        
        root.add_widget(Widget())  # Spacer
        
        # 3. Sign Out Button
        logout_btn = Button(
            text="Sign Out",
            color=TEXT_SEC,
            background_color=TRANSPARENT,
            font_size=SIZE_BODY,
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(logout_btn)
        
        self.add_widget(root)
