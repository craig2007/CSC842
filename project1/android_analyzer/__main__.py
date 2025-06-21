import argparse
import asyncio
import os
from pathlib import PurePath, PurePosixPath

from android_analyzer_common import path_type, select_device, start_adb
from ppadb.client_async import ClientAsync as AdbClient

from .adb_utils import get_running_processes
from .package import PackageData
from .utils import get_app_net_stats


def list_of_strings(arg):
    return arg.split(",")


async def main():
    adb = None
    device = None

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        prog="android_analyer",
        description="android-analyzer is a Python library to help with viewing processes and packages on an Android device to help with identifying packages that are using more data than they should or are displaying unusual or suspicious behavior.",
    )
    parser.add_argument("-d", "--device", default=None, help="The serial number of the Android device to be analyzed")
    parser.add_argument(
        "-o", "--outdir", type=path_type, default=PurePath(os.getcwd(), "out"), help="Directory to output results to"
    )
    parser.add_argument(
        "-a",
        "--analyzers",
        type=list_of_strings,
        default=["appnetstats", "processes"],
        help="A comma delimited list of which analytics to run. Current values: appnetstats, processes",
    )
    args = parser.parse_args()

    start_adb()

    # Connect to the ADB server
    client = AdbClient(host="127.0.0.1", port=5037)

    device = await select_device(client, args.device)

    if "appnetstats" in args.analyzers:
        # Get a list of installed packages
        print("Getting packages")
        await get_app_net_stats(device, args.outdir)

    if "processes" in args.analyzers:
        # Get running processes from the device
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
