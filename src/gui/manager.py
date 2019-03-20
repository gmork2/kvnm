from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager

from gui.screen import SettingsScreen


class Manager(ScreenManager):
    """

    """
    settings: SettingsScreen = ObjectProperty()

    def __init__(self, **kwargs):
        """
        Move to kv string.

        :param kwargs:
        """
        super().__init__(**kwargs)

        self.settings = SettingsScreen(name='settings')
        self.add_widget(self.settings)

    def on_settings(self, instance, value):
        """

        :param instance:
        :param value:
        :return:
        """
        pass


