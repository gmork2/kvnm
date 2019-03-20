import sys
import uuid
import time
import dbus.mainloop.glib
import NetworkManager
import pyotp
import traceback
import secretstorage
import asyncio


try:
    # sudo apt install python-gi python-gi-cairo python3-gi python3-gi-cairo gir1.2-gtk-3.0
    # sudo apt install libcairo2-dev python3.7 python3.7-dev
    # sudo apt install libgirepository1.0-dev
    # pip install gobject PyGObject
    from gi.repository import GObject
except ImportError:
    pass


c = NetworkManager.const
# Cache the ssids, as the SSid property will be unavailable when an AP
# disappears
ssids = {}


connection1 = {
     '802-11-wireless': {'mode': 'infrastructure',
                         'security': '802-11-wireless-security',
                         'ssid': 'n-m-example-connection'},
     '802-11-wireless-security': {'auth-alg': 'open', 'key-mgmt': 'wpa-eap'},
     '802-1x': {'eap': ['peap'],
                'identity': 'eap-identity-goes-here',
                'password': 'eap-password-goes-here',
                'phase2-auth': 'mschapv2'},
     'connection': {'id': 'nm-example-connection',
                    'type': '802-11-wireless',
                    'uuid': str(uuid.uuid4())},
     'ipv4': {'method': 'auto'},
     'ipv6': {'method': 'auto'}
}


def add_connection(conn):
    return NetworkManager.Settings.AddConnection(conn)













def activate_connection(name):
    """
    Activate a connection by name
    """
    print("Activate connection")
    # Find the connection
    name = "TELLO-C74F56"

    connections = NetworkManager.Settings.ListConnections()
    connections = dict([(x.GetSettings()['connection']['id'], x) for x in connections])
    conn = connections[name]

    # Find a suitable device
    ctype = conn.GetSettings()['connection']['type']
    if ctype == 'vpn':
        for dev in NetworkManager.NetworkManager.GetDevices():
            if dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED and dev.Managed:
                break
        else:
            print("No active, managed device found")
            sys.exit(1)
    else:
        dtype = {
            '802-11-wireless': NetworkManager.NM_DEVICE_TYPE_WIFI,
            '802-3-ethernet': NetworkManager.NM_DEVICE_TYPE_ETHERNET,
            'gsm': NetworkManager.NM_DEVICE_TYPE_MODEM,
        }.get(ctype,ctype)
        devices = NetworkManager.NetworkManager.GetDevices()

        for dev in devices:
            if dev.DeviceType == dtype and dev.State == NetworkManager.NM_DEVICE_STATE_DISCONNECTED:
                break
        else:
            print("No suitable and available %s device found" % ctype)
            sys.exit(1)
    # And connect
    NetworkManager.NetworkManager.ActivateConnection(conn, dev, "/")


def display_ssids():
    """
    Display all visible SSIDs
    """
    print("display_ssids")
    for dev in NetworkManager.NetworkManager.GetDevices():
        if dev.DeviceType != NetworkManager.NM_DEVICE_TYPE_WIFI:
            continue
        for ap in dev.GetAccessPoints():
            print('%-30s %dMHz %d%%' % (ap.Ssid, ap.Frequency, ap.Strength))


def otp_agent(arg):

    """
    Automate vpn connections that require a one-time password.
    Requirements:
    - secretstorage (find on pypi)
    - pyotp (likewise)

    usage: ./otp-agent name-of-connection

    The connection will be activated and when networkmanager asks for a secret,
    it will be provided. If the secret isn't known yet, it will be asked and
    stored with the secretstorage api (so in e.g. your gnome keyring)
    """
    print("Connecting to %s" % sys.argv[1])
    for connection in NetworkManager.Settings.ListConnections():
        settings = connection.GetSettings()['connection']
        if settings['id'] == arg:
            NetworkManager.NetworkManager.ActivateConnection(connection, "/", "/")
            loop.run()
            break
    else:
        print("Connection %s not found" % sys.argv[1])


class SecretAgent(NetworkManager.SecretAgent):
    def __init__(self, loop):
        self.loop = loop
        self.collection = secretstorage.get_default_collection(secretstorage.dbus_init())
        super(SecretAgent, self).__init__('net.seveas.otp-agent')

    def GetSecrets(self, settings, connection, setting_name, hints, flags):
        try:
            print("NetworkManager is asking us for a secret")
            if setting_name != 'vpn':
                return {}
            attrs = {
                'xdg:schema': 'net.seveas.otp-agent',
                'hostname': settings['vpn']['data']['remote'],
            }
            items = list(self.collection.search_items(attrs))
            if not items:
                print("No secrets found yet, asking user")
                secret = input("Enter secret code for %s: " % settings['vpn']['data']['remote'])
                self.collection.create_item(settings['vpn']['data']['remote'], attrs, secret)
                items = list(self.collection.search_items(attrs))
            else:
                print("Found secret key, generating otp code")
            secret = items[0].get_secret().decode('ascii')
            otp = pyotp.TOTP(secret).now()
            print("otp code: %s" % otp)
            return {setting_name: {'secrets': {'password': otp}}}
        except:
            import traceback
            traceback.print_exc()
            return {}
        finally:
            self.loop.quit()


def out(msg):
    print("%s %s" % (time.strftime('%H:%M:%S'), msg))


def statechange(nm, interface, signal, state):
    out("State changed to %s" % NetworkManager.const('STATE', state))


def adddevice(nm, interface, signal, device_path):
    try:
        out("Device %s added" % device_path.IpInterface)
    except NetworkManager.ObjectVanished:
        # Sometimes this signal is sent for *removed* devices. Ignore.
        pass


def removedevice(*args, **kw):
    out("removedevice: {} {}".format(args, kw))


def ap_added(dev, interface, signal, access_point):
    ssids[access_point.object_path] = access_point.Ssid
    print("+ %-30s %s %sMHz %s%%" % (
    access_point.Ssid, access_point.HwAddress, access_point.Frequency, access_point.Strength))
    access_point.OnPropertiesChanged(ap_propchange)


def ap_removed(dev, interface, signal, access_point):
    print("- %-30s" % ssids.pop(access_point.object_path))


def ap_propchange(ap, interface, signal, properties):
    if 'Strength' in properties:
        print("  %-30s %s %sMHz %s%%" % (ap.Ssid, ap.HwAddress, ap.Frequency, properties['Strength']))

# https://stackoverflow.com/questions/39804102/python-3-4-gtk-async


if __name__ == "__main__":

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    option = 'listener'

    if option == 'listener':
        NetworkManager.NetworkManager.OnStateChanged(statechange)
        NetworkManager.NetworkManager.OnDeviceAdded(adddevice)
        NetworkManager.NetworkManager.OnDeviceRemoved(removedevice)
    elif option == 'wifi_monitor':
        # Listen for added and removed access points
        for dev in NetworkManager.Device.all():
            if dev.DeviceType == NetworkManager.NM_DEVICE_TYPE_WIFI:
                dev.OnAccessPointAdded(ap_added)
                dev.OnAccessPointRemoved(ap_removed)
        for ap in NetworkManager.AccessPoint.all():
            try:
                ssids[ap.object_path] = ap.Ssid
                print("* %-30s %s %sMHz %s%%" % (ap.Ssid, ap.HwAddress, ap.Frequency, ap.Strength))
                ap.OnPropertiesChanged(ap_propchange)
            except NetworkManager.ObjectVanished:
                pass

    #loop = GObject.MainLoop()

    if option == "opt_agent":
        #agent = SecretAgent(loop)
        otp_agent("id?")

    #loop.run()


    display_ssids()

