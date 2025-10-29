import sys
import os

sys.path.insert(0, "/system/apps/badge")
os.chdir("/system/apps/badge")


from badgeware import io, brushes, shapes, Image, run, PixelFont, screen, Matrix, file_exists
import random
import math
import network
from urllib.urequest import urlopen
import gc
import sys
import json


phosphor = brushes.color(211, 250, 55, 150)
white = brushes.color(235, 245, 255)
faded = brushes.color(235, 245, 255, 100)
small_font = PixelFont.load("/system/assets/fonts/ark.ppf")
large_font = PixelFont.load("/system/assets/fonts/absolute.ppf")

WIFI_TIMEOUT = 120
CONTRIB_URL = "https://github.com/{user}.contribs"
USER_AVATAR = "https://wsrv.nl/?url=https://github.com/{user}.png&w=75&output=png"
DETAILS_URL = "https://api.github.com/users/{user}"

WIFI_PASSWORD = None
WIFI_SSID = None
WIFI_NETWORKS = []
current_network_index = 0
network_attempt_start = None

wlan = None
connected = False
ticks_start = None


def message(text):
    print(text)


def get_connection_details(user):
    global WIFI_PASSWORD, WIFI_SSID, WIFI_NETWORKS

    if WIFI_SSID is not None and user.handle is not None:
        return True

    try:
        sys.path.insert(0, "/")
        from secrets import WIFI_PASSWORD, WIFI_SSID, GITHUB_USERNAME, WIFI_NETWORKS
        sys.path.pop(0)
    except ImportError:
        try:
            # Try importing just the old format
            sys.path.insert(0, "/")
            from secrets import WIFI_PASSWORD, WIFI_SSID, GITHUB_USERNAME
            sys.path.pop(0)
            WIFI_NETWORKS = []
        except ImportError:
            WIFI_PASSWORD = None
            WIFI_SSID = None
            GITHUB_USERNAME = None
            WIFI_NETWORKS = []

    if not WIFI_SSID and not WIFI_NETWORKS:
        return False

    if not GITHUB_USERNAME:
        return False

    user.handle = GITHUB_USERNAME

    return True


def wlan_start():
    global wlan, ticks_start, connected, WIFI_PASSWORD, WIFI_SSID, WIFI_NETWORKS
    global current_network_index, network_attempt_start

    if ticks_start is None:
        ticks_start = io.ticks
        current_network_index = 0
        network_attempt_start = io.ticks

    if connected:
        return True

    if wlan is None:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        if wlan.isconnected():
            connected = True
            return True

    # Determine which networks to try - prioritize WIFI_NETWORKS if available
    networks_to_try = []
    if WIFI_NETWORKS:
        networks_to_try = WIFI_NETWORKS
    elif WIFI_SSID and WIFI_PASSWORD:
        networks_to_try = [{"ssid": WIFI_SSID, "password": WIFI_PASSWORD}]
    
    if not networks_to_try:
        print("No WiFi networks configured")
        return False

    # Check if we've exhausted all networks
    if current_network_index >= len(networks_to_try):
        print("All WiFi networks failed - giving up")
        return False

    # Get current network to try
    current_network = networks_to_try[current_network_index]
    current_ssid = current_network["ssid"]
    current_password = current_network["password"]

    try:
        # Check if we should move to the next network (timeout reached)
        network_timeout = WIFI_TIMEOUT * 1000 // len(networks_to_try)  # Divide timeout among networks
        if io.ticks - network_attempt_start > network_timeout:
            print(f"Timeout reached for network '{current_ssid}', trying next network...")
            current_network_index += 1
            network_attempt_start = io.ticks
            if current_network_index >= len(networks_to_try):
                return False
            current_network = networks_to_try[current_network_index]
            current_ssid = current_network["ssid"]
            current_password = current_network["password"]

        # Scan for available networks
        ssid_found = False
        try:
            scans = wlan.scan()
        except Exception:
            scans = []

        for s in scans:
            # s[0] is SSID (bytes or str)
            ss = s[0]
            if isinstance(ss, (bytes, bytearray)):
                try:
                    ss = ss.decode("utf-8", "ignore")
                except Exception:
                    ss = str(ss)
            if ss == current_ssid:
                ssid_found = True
                break

        if not ssid_found:
            # SSID not found yet; if still within network timeout, keep trying
            if io.ticks - network_attempt_start < network_timeout:
                # Print status occasionally to avoid spamming
                if (io.ticks - network_attempt_start) % 3000 < 50:
                    print(f"Searching for network '{current_ssid}' ({current_network_index + 1}/{len(networks_to_try)})...")
                return True
            else:
                # Move to next network
                print(f"Network '{current_ssid}' not found, trying next...")
                current_network_index += 1
                network_attempt_start = io.ticks
                return True

        # SSID is visible; attempt to connect
        try:
            print(f"Connecting to '{current_ssid}'...")
            wlan.connect(current_ssid, current_password)
        except Exception as e:
            print(f"Connection failed for '{current_ssid}': {e}")
            # Move to next network on connection failure
            current_network_index += 1
            network_attempt_start = io.ticks
            return True

        # Check connection status
        connected = wlan.isconnected()
        
        if connected:
            print(f"Successfully connected to '{current_ssid}'!")
            return True
        
        # Still connecting, wait a bit more
        if io.ticks - network_attempt_start < network_timeout:
            return True
        
        # Timeout reached, try next network
        print(f"Connection timeout for '{current_ssid}', trying next...")
        current_network_index += 1
        network_attempt_start = io.ticks
        return True

    except Exception as e:
        # on unexpected errors, don't crash the UI; report and try next network
        try:
            print(f"wlan_start error with '{current_ssid}': {e}")
            current_network_index += 1
            network_attempt_start = io.ticks
        except Exception:
            pass
        return True if current_network_index < len(networks_to_try) else False


def async_fetch_to_disk(url, file, force_update=False):
    if not force_update and file_exists(file):
        return
    try:
        # Grab the data
        response = urlopen(url, headers={"User-Agent": "GitHub Universe Badge 2025"})
        data = bytearray(512)
        total = 0
        with open(file, "wb") as f:
            while True:
                if (length := response.readinto(data)) == 0:
                    break
                total += length
                message(f"Fetched {total} bytes")
                f.write(data[:length])
                yield
        del data
        del response
    except Exception as e:
        raise RuntimeError(f"Fetch from {url} to {file} failed. {e}") from e


def get_user_data(user, force_update=False):
    message(f"Getting user data for {user.handle}...")
    yield from async_fetch_to_disk(DETAILS_URL.format(user=user.handle), "/user_data.json", force_update)
    r = json.loads(open("/user_data.json", "r").read())
    user.name = r["name"]
    user.handle = r["login"]
    user.followers = r["followers"]
    user.repos = r["public_repos"]
    del r
    gc.collect()


def get_contrib_data(user, force_update=False):
    message(f"Getting contribution data for {user.handle}...")
    yield from async_fetch_to_disk(CONTRIB_URL.format(user=user.handle), "/contrib_data.json", force_update)
    r = json.loads(open("/contrib_data.json", "r").read())
    user.contribs = r["total_contributions"]
    user.contribution_data = [[0 for _ in range(53)] for _ in range(7)]
    for w, week in enumerate(r["weeks"]):
        for day in range(7):
            try:
                user.contribution_data[day][w] = week["contribution_days"][day]["level"]
            except IndexError:
                pass
    del r
    gc.collect()


def get_avatar(user, force_update=False):
    message(f"Getting avatar for {user.handle}...")
    yield from async_fetch_to_disk(USER_AVATAR.format(user=user.handle), "/avatar.png", force_update)
    user.avatar = Image.load("/avatar.png")


def fake_number():
    return random.randint(10000, 99999)


def placeholder_if_none(text):
    if text:
        return text
    old_seed = random.seed()
    random.seed(int(io.ticks / 100))
    chars = "!\"£$%^&*()_+-={}[]:@~;'#<>?,./\\|"
    text = ""
    for _ in range(20):
        text += random.choice(chars)
    random.seed(old_seed)
    return text


class User:
    levels = [
        brushes.color(21 / 2,  27 / 2,  35 / 2),
        brushes.color(3 / 2,  58 / 2,  22 / 2),
        brushes.color(25 / 2, 108 / 2,  46 / 2),
        brushes.color(46 / 2, 160 / 2,  67 / 2),
        brushes.color(86 / 2, 211 / 2, 100 / 2),
    ]

    def __init__(self):
        self.handle = None
        self.update()

    def update(self, force_update=False):
        self.name = None
        self.followers = None
        self.contribs = None
        self.contribution_data = None
        self.repos = None
        self.avatar = None
        self._task = None
        self._force_update = force_update

    def draw_stat(self, title, value, x, y):
        screen.brush = white if value else faded
        screen.font = large_font
        screen.text(str(value) if value is not None else str(fake_number()), x, y)
        screen.font = small_font
        screen.brush = phosphor
        screen.text(title, x - 1, y + 13)

    def draw(self, connected):
        # draw contribution graph background
        size = 15
        graph_width = 53 * (size + 2)
        xo = int(-math.sin(io.ticks / 5000) *
                 ((graph_width - 160) / 2)) + ((graph_width - 160) / 2)

        screen.font = small_font
        rect = shapes.rounded_rectangle(0, 0, size, size, 2)
        for y in range(7):
            for x in range(53):
                if self.contribution_data:
                    level = self.contribution_data[y][x]
                    screen.brush = User.levels[level]
                else:
                    screen.brush = User.levels[1]
                pos = (x * (size + 2) - xo, y * (size + 2) + 1)
                if pos[0] + size < 0 or pos[0] > 160:
                    # skip tiles that aren't in view
                    continue
                rect.transform = Matrix().translate(*pos)
                screen.draw(rect)

        # draw handle
        screen.font = large_font
        handle = self.handle

        # use the handle area to show loading progress if not everything is ready
        if (not self.handle or not self.avatar or not self.contribs) and connected:
            if not self.name:
                handle = "fetching user data..."
                if not self._task:
                    self._task = get_user_data(self, self._force_update)
            elif not self.contribs:
                handle = "fetching contribs..."
                if not self._task:
                    self._task = get_contrib_data(self, self._force_update)
            else:
                handle = "fetching avatar..."
                if not self._task:
                    self._task = get_avatar(self, self._force_update)

            try:
                next(self._task)
            except StopIteration:
                self._task = None
            except:
                self._task = None
                handle = "fetch error"

        if not connected:
            handle = "connecting..."

        w, _ = screen.measure_text(handle)
        screen.brush = white
        screen.text(handle, 80 - (w / 2), 2)

        # draw name
        screen.font = small_font
        screen.brush = phosphor
        name = placeholder_if_none(self.name)
        w, _ = screen.measure_text(name)
        screen.text(name, 80 - (w / 2), 16)

        # draw statistics
        self.draw_stat("followers", self.followers, 88, 33)
        self.draw_stat("contribs", self.contribs, 88, 62)
        self.draw_stat("repos", self.repos, 88, 91)

        # draw avatar imagee
        if not self.avatar:
            # create a spinning loading animation while we wait for the avatar to load
            screen.brush = phosphor
            squircle = shapes.squircle(0, 0, 10, 5)
            screen.brush = brushes.color(211, 250, 55, 50)
            for i in range(4):
                mul = math.sin(io.ticks / 1000) * 14000
                squircle.transform = Matrix().translate(42, 75).rotate(
                    (io.ticks + i * mul) / 40).scale(1 + i / 1.3)
                screen.draw(squircle)
        else:
            screen.blit(self.avatar, 5, 37)


user = User()
connected = file_exists("/contrib_data.json") and file_exists("/user_data.json") and file_exists("/avatar.png")
force_update = False


def center_text(text, y):
  w, h = screen.measure_text(text)
  screen.text(text, 80 - (w / 2), y)


def wrap_text(text, x, y):
  lines = text.splitlines()
  for line in lines:
    _, h = screen.measure_text(line)
    screen.text(line, x, y)
    y += h * 0.8


# tell the user where to fill in their details
def no_secrets_error():
  screen.font = large_font
  screen.brush = white
  center_text("Missing Details!", 5)

  screen.text("1:", 10, 23)
  screen.text("2:", 10, 55)
  screen.text("3:", 10, 87)

  screen.brush = phosphor
  screen.font = small_font
  wrap_text("""Put your badge into\ndisk mode (tap\nRESET twice)""", 30, 24)

  wrap_text("""Edit 'secrets.py' to\nset WiFi details and\nGitHub username.""", 30, 56)

  wrap_text("""Reload to see your\nsweet sweet stats!""", 30, 88)


# tell the user that the connection failed :-(
def connection_error():
  screen.font = large_font
  screen.brush = white
  center_text("Connection Failed!", 5)

  screen.text("1:", 10, 63)
  screen.text("2:", 10, 95)

  screen.brush = phosphor
  screen.font = small_font
  wrap_text("""Could not connect\nto the WiFi network.\n\n:-(""", 16, 20)

  wrap_text("""Edit 'secrets.py' to\nset WiFi details and\nGitHub username.""", 30, 65)

  wrap_text("""Reload to see your\nsweet sweet stats!""", 30, 96)


def update():
    global connected, force_update

    screen.brush = brushes.color(0, 0, 0)
    screen.draw(shapes.rectangle(0, 0, 160, 120))

    force_update = False

    if io.BUTTON_A in io.held and io.BUTTON_C in io.held:
        connected = False
        user.update(True)

    if get_connection_details(user):
        if wlan_start():
            user.draw(connected)
        else:  # Connection Failed
            connection_error()
    else:      # Get Details Failed
        no_secrets_error()


if __name__ == "__main__":
    run(update)
