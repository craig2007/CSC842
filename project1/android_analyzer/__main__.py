import argparse
import asyncio
import os
import psutil
import subprocess
import time

from .adb_utils import get_net_data, get_packages, get_pkg_uid, get_running_processes
from .package import PackageData
from ppadb.client_async import ClientAsync as AdbClient

MAX_WAIT_TIME = 10

def list_of_strings(arg):
    return arg.split(",")

async def main():
    adb = None
    device = None

    parser = argparse.ArgumentParser(
         prog="android_analyer",
         description="android-analyzer is a Python library to help with viewing processes and packages on an Android device to help with identifying packages that are using more data than they should or are displaying unusual or suspicious behavior.",
    )
    parser.add_argument("-d", "--device", help="The serial number of the Android device to be analyzed", default=None)
    parser.add_argument("-o", "--outdir", help="Directory to output results to", default=f"{os.getcwd()}/out")
    parser.add_argument("-a", "--analyzers", type=list_of_strings, default=["appnetstats", "processes"], help="A comma delimited list of which analytics to run. Current values: appnetstats, processes")
    args = parser.parse_args()

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
    device = await client.device(args.device)
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
    
    if "appnetstats" in args.analyzers:
        # Get a list of installed packages
        print("Getting packages")
        pkg_list = await get_packages(device)

        # Get UIDs associated with each package
        print("Getting UIDs")
        tasks = [get_pkg_uid(device, pkg) for pkg in pkg_list]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(f"Package: {result.pkg}, UID: {result.uid}")

        # Get network data usage
        netstat_list = await get_net_data(device)
        for netstat_data in netstat_list:
            for pkg in pkg_list:
                if len(netstat_data) == 5 and netstat_data[0] == pkg.uid:
                    pkg.data_rx = netstat_data[1]
                    pkg.data_tx = netstat_data[3]

        # Output results to a file in the output directory
        os.makedirs(args.outdir, exist_ok=True)
        with open(f"{args.outdir}/app_netstats.csv", "w") as f:
            f.write("UID,Package,Transmitted Data,Received Data\n")
            for pkg in pkg_list:
                f.write(pkg.to_csv())

    if "processes" in args.analyzers:
        processes = await get_running_processes(device)
        proc_list = processes.split("\n")
        with open(f"{args.outdir}/processes.csv", "w") as f:
            for proc in proc_list:
                f.write(f"{','.join(proc.split())}\n")

    # Close ADB if it was started
    if adb != None:
        adb.terminate()

if __name__ == "__main__":
    asyncio.run(main())
