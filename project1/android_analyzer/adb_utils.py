import asyncio

async def get_packages(device):
    pkg_list = []
    result = await device.shell("cmd package list packages")
    tmp = result.split("\n")
    for pkg in tmp:
        if len(pkg) > 8 and pkg[:8] == "package:":
            pkg_list.append(pkg[8:])
    return pkg_list

async def get_pkg_uid(device, pkg):
    tmp = await device.shell(f"dumpsys package {pkg} | grep appId")
    uid = tmp[tmp.find("appId"):]
    if len(uid) > 6:
        uid = uid[6:].split(" ")[0].strip()
    return uid , pkg
    
async def get_running_processes(device):
    processes = await device.shell("ps -A")
    return processes

