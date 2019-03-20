import NetworkManager

from widgets.tableview import Table, Columns, Rows, h

__c = NetworkManager.const
__NM = NetworkManager.NetworkManager

SSID, FREQUENCY, STRENGTH = 'ssid', 'frequency', 'strength'


def get_ssids() -> Table:
    """
    Return all visible SSIDs.

    :return:
    """
    cols: Columns = [
        {'title': h(field), 'key': field, 'hint_text': ''}
        for field in (SSID, FREQUENCY, STRENGTH)
    ]
    rows: Rows = [{col['key']: col['title'] for col in cols}]

    for dev in __NM.GetDevices():
        if dev.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
            continue

        for ap in dev.GetAccessPoints():
            rows.append({
                SSID: str(ap.Ssid),
                FREQUENCY: str(ap.Frequency)+'MHz',
                STRENGTH: str(ap.Strength)
            })

    return cols, rows

