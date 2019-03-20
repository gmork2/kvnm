from kivy.app import App
from kivy.logger import Logger
from kivy.uix.screenmanager import NoTransition
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.config import ConfigParser

from main import BASE_DIR, DEBUG_MODE, ICON_PATH
from gui.manager import Manager
from .settings import CustomSettings
from network.info import get_general_info, get_permissions
from .defaults import *

MESSAGE = "Thanks for use KvNM"
GITHUB_URL = 'https://github.com/gmork2/kvnm'

OPTIONS = [
    ('General', 'info.json'),
    ('Permissions', 'permissions.json'),
    ('Connections', 'connection.json'),
    ('SSID', 'ssid.json'),
    ('Devices', 'device.json'),
]


class Application(App):
    """
    Main entry point into the run loop.
    """
    use_kivy_settings: bool = DEBUG_MODE

    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        path = os.path.join(BASE_DIR, 'application.ini')

        if not os.path.exists(path):
            self.msg_id = 1
            self.msg: str = MESSAGE

            Clock.schedule_once(self.notify, 1)

        super().__init__(*args, **kwargs)

    def create_settings(self):
        """

        :return:
        """
        settings: CustomSettings = super().create_settings()
        return settings

    def get_application_config(self) -> str:
        """
        File path where the configuration will be automatically
        saved.

        :return:
        """
        return super(Application, self).get_application_config(
            os.path.join(BASE_DIR, 'application.ini')
        )

    def build_config(self, config: ConfigParser) -> None:
        """
        Default section, key and value for config file before
        save configuration.

        :param config:
        :return:
        """
        config.setdefaults('permissions', get_permissions())
        config.setdefaults('info', get_general_info())

        config.setdefaults('ssid', DEFAULT_SSID)
        config.setdefaults('connection', DEFAULT_CONNECTION)
        config.setdefaults('device', DEFAULT_DEVICE)

    def build(self) -> Manager:
        """

        :return:
        """
        self.title = 'Network Manager'
        self.icon: str = ICON_PATH
        self.settings_cls = CustomSettings
        self.root = root = Manager(transition=NoTransition())

        return root

    def notify(self, *args, **kwargs) -> None:
        """

        :return:
        """
        from pydbus import SessionBus

        Logger.debug(f'Application: notify({args} {kwargs})')
        bus = SessionBus()
        notifications = bus.get('.Notifications')

        notifications.Notify(
            'kvnm', self.msg_id, self.icon, "KVNM",
            self.msg, [], {}, 5000)

    def build_settings(self, settings: CustomSettings) -> None:
        """

        :param settings:
        :return:
        """
        settings.create_json_from_dict(
            get_permissions(), 'permissions', 'permissions.json')

        for pref in OPTIONS:
            json_data = os.path.join(BASE_DIR, 'json', pref[1])
            settings.add_json_panel(pref[0], self.config, json_data)

    def on_config_change(self, config: ConfigParser,
                         section: str, key: str, value: str) -> None:
        """

        :param config:
        :param section:
        :param key:
        :param value:
        :return:
        """
        if config is self.config:
            # token = (section, key)
            Logger.debug(f'Application: on_config_change('
                         f'{section}, {key}, {value})')

    def display_settings(self, settings: CustomSettings) -> None:
        """
        Display settings inside popup.

        :param settings:
        :return:
        """
        try:
            p = self.settings_popup
        except AttributeError:
            self.settings_popup = Popup(
                title="Configuration", content=settings)
            p = self.settings_popup

        if p.content is not settings:
            p.content = settings
        p.open()

    def close_settings(self, *args) -> None:
        """

        :param args:
        :return:
        """
        try:
            p = self.settings_popup
            p.dismiss()
        except AttributeError:
            pass  # Settings popup doesn't exist

    def on_stop(self) -> None:
        """

        :return:
        """
        print("\n* KvNM is licensed under GNU GPLv3 (\33[32mhttp://fsf.org/\33[0m)")
        print(f'* Visit at \33[32m{GITHUB_URL}\33[0m\n')

