import argparse
import asyncio
import os
from pathlib import PurePath

from android_analyzer_common import path_type, select_device, start_adb
from ppadb.client_async import ClientAsync as AdbClient

from .adb_package_utils import AdbPackage


async def main():
    parser = argparse.ArgumentParser(
        prog="android_package_analyzer",
        description="A follow-up tool to android-analyzer. After triaging packages that need further investigation with android-analyzer, this tool is designed to help begin analysis of a specific package.",
    )
    parser.add_argument("-d", "--device", default=None, help="The serial number of the Android device to be analyzed")
    parser.add_argument(
        "-o", "--outdir", type=path_type, default=PurePath(os.getcwd(), "out"), help="Directory to output results to"
    )
    parser.add_argument("package_name", type=str, help="The package to be analyzed")
    args = parser.parse_args()

    start_adb()

    # Connect to the ADB server
    client = AdbClient(host="127.0.0.1", port=5037)

    device = await select_device(client, args.device)

    # Get information about the package from dumpsys
    pkg = AdbPackage(args.package_name, device)
    await pkg.parse_pkg_info()
    pkg.print_pkg_info()
    await pkg.pull_pkg()


if __name__ == "__main__":
    asyncio.run(main())
