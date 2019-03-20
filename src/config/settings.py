import os
import json
from typing import Dict, Union, overload, Optional

from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, SettingItem, SettingsPanel
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.uix.treeview import TreeView

from widgets.treeview import populate_tree_view, Tree
from widgets.tableview import TableColumn, TableView, Table

from main import BASE_DIR

TABLE_SIZE = (500, 320)
POPUP_SIZE_HINT = (None, 0.95)
TEMPLATE: Dict[str, Union[str, bool]] = {
    "type": "string",
    "title": '',
    "section": '',
    "disabled": True,
    "key": ''
}


@overload
def _get_data(instance: "SettingTable") -> Table:
    pass


def _get_data(instance: "SettingTree") -> Tree:
    """

    :param instance:
    :return:
    """
    path = instance.value.split('.')
    func = path.pop()
    module = ".".join(path)

    Factory.register(func, module=module)
    return getattr(Factory, func)()


class SettingTree(SettingItem):
    """
    Implementation of a Tree setting on top of a :class:`SettingItem`.
    It is visualized with a :class:`~kivy.uix.switch.Switch` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    :class:`~kivy.uix.treeview.TreeView` so the user can expand
    label nodes.
    """
    # Used to store the current popup when it is shown.
    popup: Optional[Popup] = ObjectProperty(None, allownone=True)

    def on_panel(self, instance: "SettingTree",
                 value: SettingsPanel) -> None:
        """
        On release create popup.

        :param instance:
        :param value:
        :return:
        """
        if value is None:
            return
        self.fbind('on_release', self._create_popup)

    @staticmethod
    def _create_tree(instance: "SettingTree") -> TreeView:
        """

        :return:
        """
        tree: Tree = _get_data(instance)
        tv = TreeView(hide_root=True)
        tv.bind(minimum_height=tv.setter('height'))

        populate_tree_view(tv, None, tree)
        return tv

    def _create_popup(self, instance: "SettingTree") -> None:
        """

        :param instance:
        :return:
        """
        root = ScrollView(pos=(0, 0))
        root.add_widget(self._create_tree(instance))

        popup_width = min(0.95 * Window.width, dp(500))
        popup = Popup(
            title=self.title, content=root,
            size_hint=POPUP_SIZE_HINT,
            width=popup_width
        )
        self.popup = popup

        popup.open()


class SettingTable(SettingItem):
    """
    Implementation of a Table setting on top of a :class:`SettingItem`.
    It is visualized with a :class:`~kivy.uix.switch.Switch` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    :class:`~kivy.uix.tableview.TableView`.
    """
    # Used to store the current popup when it is shown.
    popup: Optional[Popup] = ObjectProperty(None, allownone=True)

    def on_panel(self, instance: "SettingTable", value: SettingsPanel):
        """

        :param instance:
        :param value:
        :return:
        """
        if value is None:
            return
        self.fbind('on_release', self._create_popup)

    @staticmethod
    def _create_table(instance: "SettingTable") -> TableView:
        """

        :param instance:
        :return:
        """
        cols, rows = _get_data(instance)
        table = TableView(
            size=TABLE_SIZE,
            pos_hint={'x': 0.1, 'center_y': .5}
        )
        for col in cols:
            table.add_column(TableColumn(**col))

        for row in rows:
            table.add_row(row)

        return table

    def _create_popup(self, instance: "SettingTable"):
        """

        :param instance:
        :return:
        """
        root = ScrollView(pos=(0, 0))
        root.add_widget(self._create_table(instance))

        popup_width = min(0.95 * Window.width, dp(500))

        self.popup = popup = Popup(
            title=self.title, content=root,
            size_hint=POPUP_SIZE_HINT,
            width=popup_width
        )
        popup.open()


class CustomSettings(Settings):
    """

    """
    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.register_type('tree', SettingTree)
        self.register_type('table', SettingTable)

    @staticmethod
    def create_json_from_dict(d: dict, section: str, filename: str) -> None:
        """

        :param d:
        :param section:
        :param filename:
        :return:
        """
        path = os.path.join(BASE_DIR, 'json', filename)
        data = [
            {**TEMPLATE, 'section': section, 'title': perm, 'key': perm}
            for perm in d.keys()
        ]
        with open(path, 'w') as outfile:
            json.dump(data, outfile)

    def on_close(self) -> None:
        """

        :return:
        """
        Logger.info("Settings: CustomSettings.on_close({})".format(self))

    def on_config_change(self, config, section, key, value) -> None:
        """

        :param config:
        :param section:
        :param key:
        :param value:
        :return:
        """
        Logger.debug(
            "Settings: CustomSettings.on_config_change: "
            "{0}, {1}, {2}, {3}".format(config, section, key, value))

