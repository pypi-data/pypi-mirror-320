from core.main_router import MainRouter
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp


class MainApp(MDApp):
    def build(self):
        self.sm = MainRouter()
        Clock.schedule_once(
            self.sm.switch_to_first_screen, 5
        )  # Switch from splash to first screen after 5 seconds
        return self.sm


if __name__ == "__main__":
    MainApp().run()
