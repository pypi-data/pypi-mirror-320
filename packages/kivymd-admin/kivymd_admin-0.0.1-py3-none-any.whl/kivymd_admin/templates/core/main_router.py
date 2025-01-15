from kivy.uix.screenmanager import ScreenManager
from screens.first.screen import Screen as FirstScreen
from screens.splash.screen import Screen as SplashScreen


class MainRouter(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_screens()

    def register_screens(self):
        """Register screens statically."""
        self.add_widget(SplashScreen(name="splash"))
        self.add_widget(FirstScreen(name="first"))

    def switch_to_first_screen(self, *args):
        """Switch to the first screen after the splash screen."""
        self.current = "first"
