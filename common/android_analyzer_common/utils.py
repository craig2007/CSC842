import asyncio
import subprocess
import time
from pathlib import PurePath

import psutil
from ppadb.client_async import ClientAsync as AdbClient

MAX_WAIT_TIME = 10

def path_type(arg):
    return PurePath(arg)

# Function to start the ADB daemon if it is not currently running
def start_adb():
    if "adb" not in (p.name() for p in psutil.process_iter()):
        print("Starting ADB")
        adb = subprocess.Popen(["adb", "start-server"])
    i = 0
    for i in range(0, MAX_WAIT_TIME):
        time.sleep(1)
        if "adb" in (p.name() for p in psutil.process_iter()):
            break
    if i == MAX_WAIT_TIME:
        print("ERROR: ADB failed to start")
        raise Exception("ADB failed to start")

async def select_device(client: AdbClient=None, device: str = None):
    if client == None:
        print("ERROR: ADB client cannot be None")
        raise Exception("ADB client cannot be None")
    device = await client.device(device)
    if device == None:
        devices = await client.devices()
        print("Select from the following devices:")
        for i in range(0, len(devices)):
            print(f"\t{i}) {devices[i].serial}")
        try:
            selection = int(input("Selection: "))
            device = devices[selection]
        except:
            print("Invalid selection")
    if device == None:
        print("ERROR: No device selected")
        raise Exception("No device selected")
    print(f"Selected {device.serial}")
    return device
