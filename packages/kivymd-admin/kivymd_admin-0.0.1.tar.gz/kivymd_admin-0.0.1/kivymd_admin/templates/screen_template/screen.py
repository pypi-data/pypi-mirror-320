from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel


class Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical", padding=50, spacing=20)

        label = MDLabel(text="New Screen", halign="center", font_style="H3")
        layout.add_widget(label)
        self.add_widget(layout)
