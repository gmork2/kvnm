import os

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App

from main import BASE_DIR

Builder.load_file(os.path.join(BASE_DIR, 'layout', 'settings.kv'))


class SettingsScreen(Screen):
    """

    """
    def __init__(self, **kwargs):
        """

        :param kwargs:
        """
        super().__init__(**kwargs)
        self.open_settings()

    @staticmethod
    def open_settings():
        """

        :return:
        """
        app: App = App.get_running_app()
        app.open_settings()
