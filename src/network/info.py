"""
Display information about everything network-related that network-manager can
say something about.
"""

from collections import namedtuple
from typing import NamedTuple, List

import NetworkManager

__c = NetworkManager.const
__NM = NetworkManager.NetworkManager


def get_general_info() -> dict:
    """

    :return:
    """
    return {
        'version': __NM.Version,
        'hostname': NetworkManager.Settings.Hostname,
        'can_modify': NetworkManager.Settings.CanModify,
        'networking_enabled': __NM.NetworkingEnabled,
        'wireless_enabled': __NM.WirelessEnabled,
        'wireless_hw_enabled': __NM.WirelessHardwareEnabled,
        'wwan_enabled': __NM.WwanEnabled,
        'wwan_hw_enabled': __NM.WwanHardwareEnabled,
        'wimax_enabled': __NM.WimaxEnabled,
        'wimax_hw_enabled': __NM.WimaxHardwareEnabled,
        'overall_state': __c('state', __NM.State)
    }


def get_permissions() -> dict:
    """
    Get current network permissions.

    :return:
    """
    return {
        '.'.join(perm.split('.')[3:]).lower(): val.lower()
        for perm, val in sorted(__NM.GetPermissions().items())
    }


def get_available_devices() -> List[NamedTuple]:
    """
    Get list of available network devices.

    :return:
    """
    Device: NamedTuple = namedtuple('Device', ['name', 'state', 'driver', 'managed'])
    return [
        Device(dev.Interface, __c('device_state', dev.State), dev.Driver, dev.Managed)
        for dev in __NM.GetDevices()
    ]


def get_available_connections() -> List[NamedTuple]:
    """
    Get available connections.

    :return:
    """
    Connection: NamedTuple = namedtuple('Connection', ['name', 'type'])
    conns: List = list()

    for conn in NetworkManager.Settings.ListConnections():
        settings: dict = conn.GetSettings()['connection']
        conns.append(Connection(settings['id'], settings['type']))

    return conns


def get_active_connections() -> List[NamedTuple]:
    """
    Get active connections.

    :return:
    """
    ActiveConnection: NamedTuple = namedtuple('ActiveConnection', [
        'name', 'type', 'default', 'devices'])
    active_conns: List = list()

    for conn in __NM.ActiveConnections:
        settings: dict = conn.Connection.GetSettings()['connection']
        devices: str = ", ".join([x.Interface for x in conn.Devices])
        active_conns.append(
            ActiveConnection(settings['id'], settings['type'], conn.Default, devices)
        )
    return active_conns
