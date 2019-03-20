import os
import uuid
from typing import Dict

Default = Dict[str, str]


DEFAULT_SSID = {'ssids': 'network.ssid.get_ssids'}

DEFAULT_CONNECTION = {
    'connection_details': 'network.connection.get_connection_details',
    'available_connections': 'network.connection.get_available_connections',
    'active_connections': 'network.connection.get_active_connections'
}

DEFAULT_DEVICE = {
    'available_devices': 'network.device.get_available_devices',
}

DEFAULT_ADD_CONNECTION = {
    'name': 'New name',
    'load': os.environ['HOME'],
    'mode': 'infrastructure',
    'security': '802-11-wireless-security',
    'ssid': '',
    'auth-alg': 'open',
    'key-mgmt': 'wpa-eap',
    'eap': 'peap',
    'identity': '',
    'password': '',
    'phase2-auth': 'mschapv2',
    'id': '',
    'type': '802-11-wireless',
    'uuid': str(uuid.uuid4()),
    'ipv4_method': 'auto',
    'ipv6_method': 'auto',
}
