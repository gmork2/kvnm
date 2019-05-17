import NetworkManager

from widgets.tableview import Table, Columns, Rows, h
from widgets.treeview import Tree

__c = NetworkManager.const
__NM = NetworkManager.NetworkManager

NAME, TYPE, DEFAULT, DEVICES = 'name', 'type', 'default', 'devices'


def add_active_connection(tree: Tree, settings: dict,
                          devices: str) -> Tree:
    """
    Add an active connection to tree.

    :param tree:
    :param settings:
    :param devices:
    :return:
    """
    node: Tree = dict(
        node_id="%s%s" % (settings['connection']['id'], devices),
        children=[]
    )
    tree['children'].append(node)

    for key, val in sorted(settings.items()):
        node2: Tree = dict(node_id="%s" % key.title(), children=[])
        node['children'].append(node2)

        for name, value in val.items():
            node3: Tree = dict(
                node_id="{}: {}".format(str(name), str(value)),
                children=[]
            )
            node2['children'].append(node3)
    return node


def add_devices(conn: NetworkManager.ActiveConnection,
                parent: Tree):
    """
    Add device nodes to parent tree.

    :param conn:
    :param parent:
    :return:
    """
    node2: Tree = dict(node_id="devices", children=[])
    parent['children'].append(node2)

    for dev in conn.Devices:
        node3: Tree = dict(node_id="Device: %s" % dev.Interface, children=[])
        node2['children'].append(node3)

        node4: Tree = dict(
            node_id="%s" % __c('device_type', dev.DeviceType),
            children=[])
        node3['children'].append(node4)

        if hasattr(dev, 'HwAddress'):
            node4: Tree = dict(
                node_id="MAC address %s" % dev.HwAddress, children=[]
            )
            node3['children'].append(node4)

        node4: Tree = dict(node_id="IPv4 config", children=[])
        node3['children'].append(node4)
        node5: Tree = dict(node_id="Addresses", children=[])
        node4['children'].append(node5)

        for addr in dev.Ip4Config.Addresses:
            node6: Tree = dict(node_id="%s/%d -> %s" % tuple(addr), children=[])
            node5['children'].append(node6)

        node5: Tree = dict(node_id="Routes", children=[])
        node4['children'].append(node5)

        for route in dev.Ip4Config.Routes:
            node6: Tree = dict(
                node_id="%s/%d -> %s (%d)" % tuple(route),
                children=[]
            )
            node5['children'].append(node6)

        node5: Tree = dict(node_id="Nameservers", children=[])
        node4['children'].append(node5)

        for ns in dev.Ip4Config.Nameservers:
            node6: Tree = dict(node_id="%s" % ns, children=[])
            node5['children'].append(node6)


def get_connection_details() -> Tree:
    """
    Return a tree with detailed information about currently
    active connections.

    :return:
    """
    tree: Tree = dict(node_id="Active connections", children=[])

    for conn in __NM.ActiveConnections:
        settings: dict = conn.Connection.GetSettings()

        for s in list(settings.keys()):
            if 'data' in settings[s]:
                settings[s + '-data'] = settings[s].pop('data')

        secrets: dict = conn.Connection.GetSecrets()
        for key in secrets:
            settings[key].update(secrets[key])

        devices = ""
        if conn.Devices:
            devices: str = " (on %s)" % ", ".join([x.Interface for x in conn.Devices])

        node: Tree = add_active_connection(tree, settings, devices)
        add_devices(conn, node)

    return tree


def get_active_connections() -> Table:
    """
    Return a table with active connections.

    :return:
    """
    cols: Columns = [
        {'title': h(field), 'key': field, 'hint_text': ''}
        for field in (NAME, TYPE, DEFAULT, DEVICES)
    ]
    rows: Rows = [{col['key']: col['title'] for col in cols}]

    for conn in __NM.ActiveConnections:
        settings: dict = conn.Connection.GetSettings()['connection']
        rows.append({
            NAME: str(settings['id']),
            TYPE: str(settings['type']),
            DEFAULT: str(conn.Default),
            DEVICES: ", ".join([x.Interface for x in conn.Devices])
        })
    return cols, rows


def get_available_connections() -> Table:
    """
    Return a table with available connections.

    :return:
    """
    cols: Columns = [
        {'title': h(NAME), 'key': NAME, 'hint_text': ''},
        {'title': h(TYPE), 'key': TYPE, 'hint_text': ''},
    ]
    rows: Rows = [{col['key']: col['title'] for col in cols}]

    for conn in NetworkManager.Settings.ListConnections():
        settings: dict = conn.GetSettings()['connection']

        rows.append({
            NAME: str(settings['id']),
            TYPE: str(settings['type']),
        })
    return cols, rows
