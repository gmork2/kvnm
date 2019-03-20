import NetworkManager

from widgets.tableview import Table, Columns, Rows, h

__c = NetworkManager.const
__NM = NetworkManager.NetworkManager

NAME, STATE, DRIVER, MANAGED = 'name', 'state', 'driver', 'managed'


def get_available_devices() -> Table:
    """
    Return all available devices.

    :return:
    """
    cols: Columns = [
        {'title': h(field), 'key': field, 'hint_text': ''}
        for field in (NAME, STATE, DRIVER, MANAGED)
    ]
    rows: Rows = [{col['key']: col['title'] for col in cols}]

    for dev in __NM.GetDevices():
        rows.append({
            NAME: str(dev.Interface),
            STATE: str(__c('device_state', dev.State)),
            DRIVER: str(dev.Driver),
            MANAGED: str(dev.Managed),
        })
    return cols, rows
