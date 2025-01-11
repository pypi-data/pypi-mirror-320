import subprocess
from colorama import Fore, init
import ppadb.client as adb
import requests
from packaging import version
import urllib3

VERSION = "2.0.4"

"""
# Urax ADB (v{})
A Python library to interact with Android devices using ADB
""".format(VERSION)

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

adb_client = adb.Client(host="127.0.0.1", port=5037)
subprocess.run(["adb", "start-server"])

class VersionChecker:
    def __init__(self):
        self.version = VERSION
        
    def fetchLatestVer():
        url = "https://pypi.org/pypi/urax-adb/json"
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            data = response.json()
            return data['info']['version']
        except requests.exceptions.RequestException:
            return None

    latestVer = fetchLatestVer()

    if latestVer:
        if version.parse(VERSION) == version.parse(latestVer):
            checkVer = f"{Fore.GREEN}(latest)"
        elif version.parse(VERSION) < version.parse(latestVer):
            checkVer = f"{Fore.YELLOW}(New version available)"
        elif "-beta" in VERSION or "-dev" in VERSION:
            checkVer = f"{Fore.YELLOW}(beta/dev version)"
        else:
            checkVer = f"{Fore.RED}(unofficial)"
    else:
        checkVer = f"{Fore.RED}(failed to fetch latest version)"

    print(f"urax_adb v{VERSION} {checkVer}\n")

def connect(device, type="USB", port=5555):
    """
    ## Connect to device
    :param device: IP address or Device name
    :param type: Connection type, USB or TCP (Default: USB)
    :param port: Port number (Default: 5555)
    """
    if type.lower() == "usb":
        adb_client.device(device)
    elif type.lower() == "tcp":
        adb_client.remote_connect(device, port)
    else:
        print(f"{Fore.RED}Invalid connection type")

def disconnect(device):
    """
    ## Disconnect from device
    :param device: IP address or Device name
    """
    adb_client.remote_disconnect(device)

def devices():
    """## List all connected devices"""
    device_list = adb_client.devices()
    if not device_list:
        print(f"{Fore.RED}No Android devices detected. Make sure you are connected properly.")
    for device in device_list:
        print(device)

def shell(shell_commands):
    """
    ## Execute multiple adb shell commands
    :param shell_commands: List of shell commands
    """
    device = adb_client.devices()[0]
    command_str = " && ".join(shell_commands)
    result = device.shell(command_str)
    print(result)

def execute(command):
    """
    ## Execute a adb command
    :param command: Execution command
    """
    if "adb connect" in command:
        print(f"{Fore.RED}You should use 'connect()' to connect to the Android device when using urax_adb")
    subprocess.run(command, shell=True)