import asyncio

from .package import PackageData

async def get_packages(device):
    pkg_list = []
    result = await device.shell("cmd package list packages")
    tmp = result.split("\n")
    for pkg in tmp:
        if len(pkg) > 8 and pkg[:8] == "package:":
            pkg_list.append(PackageData(pkg[8:]))
    return pkg_list

async def get_pkg_uid(device, pkg):
    tmp = await device.shell(f"dumpsys package {pkg.pkg} | grep appId")
    uid = tmp[tmp.find("appId"):]
    if len(uid) > 6:
        pkg.uid = uid[6:].split(" ")[0].strip()
    return pkg

async def get_net_data(device):
    net_data = []
    tmp = await device.shell("dumpsys netstats")
    start = tmp.find("mAppUidStatsMap:\n")
    if start > -1:
        lines = tmp[start:].split("\n")
    if len(lines) > 1:
        lines = lines[1:]
    for line in lines:
        if len(line) < 4 or line[:4] != "    ":
            break
        net_data.append(line.strip().split(" "))
    return net_data

async def get_running_processes(device):
    processes = await device.shell("ps -A")
    return processes

