# Taken from https://github.com/Huluk/kivy-table
from typing import Tuple, List, Dict, Callable
import sys

from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ObjectProperty

Columns = Rows = List[Dict[str, str]]
Table = Tuple[Columns, Rows]


def h(s: str) -> str:
    """
    Convert a string into a header format.

    :param s:
    :return:
    """
    return "<{}>".format(s.title())


class TableColumn(Widget):
    """
    A column provides a shared method of cell construction,
    data access, and data updates.
    Assumes that underlying data is accessable via data[key].
    """
    title = StringProperty()
    hint_text = StringProperty()

    def __init__(self, title: str, key: str,
                 update_function: Callable = (lambda row, new_value: None),
                 hint_text: str = ''):
        """

        :param title:
        :param key:
        :param update_function:
        :param hint_text:
        """
        self.title = title
        self.key = key
        self.update_function = update_function
        self.hint_text = hint_text

    def get_cell(self, row) -> "TableCell":
        """

        :param row:
        :return:
        """
        return TableCell(self, row)

    def on_cell_edit(self, row, new_value):
        """

        :param row:
        :param new_value:
        :return:
        """
        self.update_function(row, new_value)


class TableRow(BoxLayout):
    """
    A layout which contains the row cells and pointers to the data.
    """
    def __init__(self, table, index):
        """

        :param table:
        :param index:
        """
        super(TableRow, self).__init__(orientation='horizontal')
        self.table: TableView = table
        self.index = index

        for col in table.columns:
            self.add_widget(col.get_cell(self))

    def data(self, key):
        """

        :param key:
        :return:
        """
        return self.table.data_rows[self.index][key]

    def set_data(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """
        self.table.data_rows[self.index][key] = value

    def update(self):
        """
        Reload data for all cells.

        :return:
        """
        for cell in self.children:
            cell.update()

    def move_focus(self, index_diff, column):
        """
        Move focus from a cell in this row to the corresponding
        cell in the row with index_diff offset to this row.

        :param index_diff:
        :param column:
        :return:
        """
        self.table.set_focus(self.index + index_diff, column)

    def focus_on_cell(self, column):
        """

        :param column:
        :return:
        """
        for cell in self.children:
            if cell.column == column:
                cell.focus = True
                break

    def scroll_into_view(self):
        """

        :return:
        """
        self.table.scroll_to(self)


class TableCell(TextInput):
    """
    A single cell, formatted and updated according to column,
    with data from row.
    """
    row = ObjectProperty(None, True)
    column = ObjectProperty(None, True)

    MOVEMENT_KEYS = {'up': -1, 'down': 1,
                     'pageup': -sys.maxsize, 'pagedown': sys.maxsize}

    def __init__(self, column, row):
        """

        :param column:
        :param row:
        """
        self.column = column
        self.row = row
        super(TableCell, self).__init__()

        self.update()

    def update(self):
        """
        Reset text to data from row

        :return:
        """
        self.text = str(self.row.data(self.column.key))

    def on_text_validate(self):
        """
        Let column validate and possibly update the input.

        :return:
        """
        self.column.on_cell_edit(self.row, self.text)

    def on_focus(self, instance, value):
        """

        :param instance:
        :param value:
        :return:
        """
        if value:
            self.row.scroll_into_view()
        else:
            self.update()

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """
        Check for special navigation keys, otherwise call super.

        :param window:
        :param keycode:
        :param text:
        :param modifiers:
        :return:
        """
        if keycode[1] in self.MOVEMENT_KEYS:
            self.on_text_validate()
            self.focus = False
            self.row.move_focus(self.MOVEMENT_KEYS[keycode[1]], self.column)
        else:
            super(TableCell, self).keyboard_on_key_down(window, keycode, text, modifiers)


class TableView(ScrollView):
    """
    A scrollable table where each row corresponds to a data point
    and each column to a specific attribute of the data points.
    Currently, each attribute is an editable field.
    """
    def __init__(self, size, pos_hint):
        """

        :param size:
        :param pos_hint:
        """
        super(TableView, self).__init__(size_hint=(None, 1), size=size,
                                        pos_hint=pos_hint, do_scroll_x=False)

        self.layout = GridLayout(cols=1,
                                 size_hint=(None, None), width=size[0])
        self.layout.bind(width=self.setter('width'))
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.columns = []
        self.data_rows = []
        self.layout_rows = []
        self.add_widget(self.layout)

    def add_column(self, column):
        """

        :param column:
        :return:
        """
        self.columns.append(column)

        for row in self.layout_rows:
            row.add_widget(column.get_cell(row))

    def add_row(self, data):
        """

        :param data:
        :return:
        """
        self.data_rows.append(data)
        row = TableRow(self, len(self.data_rows) - 1)
        self.layout_rows.append(row)
        self.layout.add_widget(row)

    def set_focus(self, row_index, column):
        """

        :param row_index:
        :param column:
        :return:
        """
        if len(self.layout_rows) == 0:
            return
        row_index = min(max(row_index, 0), len(self.layout_rows) - 1)
        self.layout_rows[row_index].focus_on_cell(column)

