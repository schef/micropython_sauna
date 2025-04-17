import network
import asyncio
import credentials

wlan = None
mac = None
rssi = 0
on_connection_changed_callback = None
reboot_requested = False

def init():
    global wlan, mac
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    mac = "".join(['{:02X}'.format(x) for x in wlan.config('mac')])

async def connect_wifi():
    global rssi
    if not wlan.isconnected():
        print(f"[WLAN]: scan[{wlan.scan()}]")
        print("[WLAN]: connecting")
        wlan.connect(credentials.wifi_ssid, credentials.wifi_password)
        counter = 0
        while not wlan.isconnected():
            await asyncio.sleep(1)
            counter += 1
            if counter >= 10:
                reset_wifi()
                return
    print(f"[WLAN]: connected[{wlan.ifconfig()}]")
    rssi = wlan.status("rssi")
    if on_connection_changed_callback is not None:
        on_connection_changed_callback()

def register_on_connection_changed_callback(func):
    global on_connection_changed_callback
    on_connection_changed_callback = func

def check_link():
    return wlan.isconnected()

async def reset_wifi():
    print("[WLAN]: Disabling Wi-Fi chip...")
    wlan.active(False)
    await asyncio.sleep(2)
    print("[WLAN]: Re-enabling Wi-Fi chip...")
    wlan.active(True)

def request_reboot():
    print("[WLAN]: request reboot")
    global reboot_requested
    reboot_requested = True

def print_status():
    print(f"[DEBUG] mac[{mac}] active[{wlan.active()}] isconnected[{wlan.isconnected()}] status[{wlan.status()}] ip[{wlan.ifconfig()}]")

async def loop():
    global rssi
    while True:
        if not wlan.isconnected():
            print("[WLAN]: no connection")
            rssi = 0
            if on_connection_changed_callback is not None:
                on_connection_changed_callback()
            await connect_wifi()
        else:
            new_rssi = wlan.status("rssi")
            if rssi != new_rssi:
                rssi = new_rssi
                print(f"[WLAN]: rssi {rssi}")
                if on_connection_changed_callback is not None:
                    on_connection_changed_callback()
        await asyncio.sleep(10)
