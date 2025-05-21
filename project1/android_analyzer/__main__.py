import argparse
import asyncio
import psutil
import subprocess
import time

from .adb_utils import get_packages, get_pkg_uid
from ppadb.client_async import ClientAsync as AdbClient

MAX_WAIT_TIME = 10

async def main():
    adb = None
    device = None
    
    # Start ADB if it is not running
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

    # Connect to the ADB server
    client = AdbClient(host="127.0.0.1", port=5037)
    
    # Select the device analyze
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
    
    # Get a list of installed packages
    print("Getting packages")
    pkg_list = await get_packages(device)

    # Get UIDs associated with each package
    print("Getting UIDs")
    tasks = [get_pkg_uid(device, pkg) for pkg in pkg_list]
    results = await asyncio.gather(*tasks)
    results_dict = dict(results)
    print(results_dict)

    # Close ADB if it was started
    if adb != None:
        adb.terminate()

if __name__ == "__main__":
    asyncio.run(main())
