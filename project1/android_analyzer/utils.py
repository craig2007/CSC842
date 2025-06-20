import asyncio
from pathlib import PurePath, PurePosixPath
import os

from .adb_utils import (get_net_data, get_packages, get_pkg_uid)

async def get_app_net_stats(device, outdir=PurePath(os.getcwd(), "out")):
    pkg_list = await get_packages(device)

    # Get UIDs associated with each package
    tasks = [get_pkg_uid(device, pkg) for pkg in pkg_list]
    results = await asyncio.gather(*tasks)

    # Get network data usage
    netstat_list = await get_net_data(device)
    for netstat_data in netstat_list:
        for pkg in pkg_list:
            if len(netstat_data) == 5 and netstat_data[0] == pkg.uid:
                pkg.data_rx = netstat_data[1]
                pkg.data_tx = netstat_data[3]

    # Output results to a file in the output directory
    if isinstance(outdir, PurePosixPath):
        path_str = outdir.as_posix() + "/"
    else:
        path_str = str(outdir) + "\\"
    os.makedirs(path_str, exist_ok=True)
    with open(f"{path_str}app_netstats.csv", "w") as f:
        f.write("UID,Package,Transmitted Data,Received Data\n")
        for pkg in pkg_list:
            f.write(pkg.to_csv())
