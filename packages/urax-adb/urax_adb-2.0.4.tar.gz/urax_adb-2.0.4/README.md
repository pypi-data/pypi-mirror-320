# Urax ADB
![PyPI Package - Visit](https://img.shields.io/badge/PyPI%20Package-Visit-dark?style=flat-square&logo=PyPI&link=https%3A%2F%2Fpypi.org%2Fpackage%2Furax-adb) ![PyPI - Downloads](https://img.shields.io/pypi/dm/urax-adb?label="Package%20Downloads"&style="flat-square") ![PyPI - Version](https://img.shields.io/pypi/v/urax-adb?label=Package%20Version&style=flat-square)

A Python library to interact with Android devices using ADB.

# Installation
**Note: If you are using Pylance v2024.12.100 (pre-release) extension on Visual Studio Code, set the value of `python.analysis.supportRestructuredText` to `false` in settings to be able to see function comments correctly**

To install with `pip`, run the command:
```bash
pip install urax_adb
```

For specific versions, run the command:
```bash
pip install urax_adb==<VERSION>
```

# Functions
| Functions | Feature |
|:-:|:-:|
| `urax_adb.connect(device, type, port)` | Connect to device |
| `urax_adb.disconnect(device)` | Disconnect from device |
| `urax_adb.devices()` | List all connected devices |
| `urax_adb.shell(shell_commands)` | Execute multiple adb shell commands |
| `urax_adb.execute(command)` | Execute a adb command |
