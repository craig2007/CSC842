import argparse
import asyncio
import hashlib
import os
from pathlib import PurePath

import requests
from android_analyzer_common import path_type, select_device, start_adb
from ppadb.client_async import ClientAsync as AdbClient

from .adb_package_utils import AdbPackage


def sha256_of_apk(apk_file):
    try:
        sha256hash = hashlib.sha256()
        with open(apk_file, "rb") as f:
            while chunk := f.read(4096):
                sha256hash.update(chunk)
        return sha256hash.hexdigest()
    except:
        return None


async def main():
    parser = argparse.ArgumentParser(
        prog="android_package_analyzer",
        description="A follow-up tool to android-analyzer. After triaging packages that need further investigation with android-analyzer, this tool is designed to help begin analysis of a specific package.",
    )
    parser.add_argument("-d", "--device", default=None, help="The serial number of the Android device to be analyzed")
    parser.add_argument(
        "-o", "--outdir", type=path_type, default=PurePath(os.getcwd(), "out"), help="Directory to output results to"
    )
    parser.add_argument(
        "-s", "--scan", action="store_true", help="Flag to submit package to VirusTotal to be scanned for malware"
    )
    parser.add_argument(
        "-k", "--key-file", default=None, help="A file containing an API key for submitting to VirusTotoal"
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
    apk_file = await pkg.pull_pkg()

    if args.scan:
        if args.key_file == None:
            print("ERROR: An API key needs to be provided to send to VirusTotal")
        else:
            with open(args.key_file, "r") as f:
                apikey = f.read().strip()
            apk_hash = sha256_of_apk(apk_file)
            url = f"https://www.virustotal.com/api/v3/files/{apk_hash}"
            headers = {"accept": "application/json", "x-apikey": apikey}

            response = requests.get(url, headers=headers)
            print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
