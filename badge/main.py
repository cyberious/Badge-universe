# This file is copied from /system/main.py to /main.py on first run

import sys
import os
from badgeware import run, io
import machine
import gc
import powman
import network

SKIP_CINEMATIC = powman.get_wake_reason() == powman.WAKE_WATCHDOG

running_app = None

# WiFi connection helper function
def connect_wifi_multi(timeout_per_network=30):
    """
    Attempt to connect to WiFi using multiple configured networks.
    Returns True if connected, False if all networks failed.
    """
    try:
        from secrets import WIFI_NETWORKS
    except ImportError:
        try:
            # Fallback to old single network format
            from secrets import WIFI_SSID, WIFI_PASSWORD
            WIFI_NETWORKS = [{"ssid": WIFI_SSID, "password": WIFI_PASSWORD}]
        except ImportError:
            print("No WiFi credentials found in secrets.py")
            return False
    
    if not WIFI_NETWORKS:
        print("No WiFi networks configured")
        return False
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Check if already connected
    if wlan.isconnected():
        print("Already connected to WiFi")
        return True
    
    print(f"Attempting to connect to {len(WIFI_NETWORKS)} WiFi network(s)...")
    
    for i, network_config in enumerate(WIFI_NETWORKS):
        ssid = network_config["ssid"]
        password = network_config["password"]
        
        print(f"Trying network '{ssid}' ({i+1}/{len(WIFI_NETWORKS)})...")
        
        # Scan for the network
        try:
            scans = wlan.scan()
            ssid_found = False
            
            for scan in scans:
                scan_ssid = scan[0]
                if isinstance(scan_ssid, (bytes, bytearray)):
                    try:
                        scan_ssid = scan_ssid.decode("utf-8", "ignore")
                    except Exception:
                        scan_ssid = str(scan_ssid)
                
                if scan_ssid == ssid:
                    ssid_found = True
                    break
            
            if not ssid_found:
                print(f"  Network '{ssid}' not found in scan")
                continue
                
        except Exception as e:
            print(f"  Scan failed: {e}")
            continue
        
        # Attempt to connect
        try:
            wlan.connect(ssid, password)
            
            # Wait for connection with timeout
            start_time = io.ticks
            
            while not wlan.isconnected():
                if io.ticks - start_time > timeout_per_network * 1000:
                    print(f"  Connection to '{ssid}' timed out")
                    break
                machine.idle()  # Allow other tasks to run while waiting
            
            if wlan.isconnected():
                print(f"  Successfully connected to '{ssid}'!")
                print(f"  IP address: {wlan.ifconfig()[0]}")
                return True
            else:
                print(f"  Failed to connect to '{ssid}'")
                
        except Exception as e:
            print(f"  Connection error for '{ssid}': {e}")
            continue
    
    print("All WiFi networks failed")
    return False


def quit_to_launcher(pin):
    global running_app
    getattr(running_app, "on_exit", lambda: None)()
    # If we reset while boot is low, bad times
    while not pin.value():
        pass
    machine.reset()


if not SKIP_CINEMATIC:
    startup = __import__("/system/apps/startup")

    run(startup.update)

    if sys.path[0].startswith("/system/apps"):
        sys.path.pop(0)

    del startup

    gc.collect()

menu = __import__("/system/apps/menu")

app = run(menu.update)

if sys.path[0].startswith("/system/apps"):
    sys.path.pop(0)

del menu

# make sure these can be re-imported by the app
del sys.modules["ui"]
del sys.modules["icon"]

gc.collect()

# Don't pass the b press into the app
while io.held:
    io.poll()

machine.Pin.board.BUTTON_HOME.irq(
    trigger=machine.Pin.IRQ_FALLING, handler=quit_to_launcher
)

sys.path.insert(0, app)
os.chdir(app)

running_app = __import__(app)

getattr(running_app, "init", lambda: None)()

run(running_app.update)

# Unreachable, in theory!
machine.reset()

