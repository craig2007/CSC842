import asyncio

from ppadb.device_async import DeviceAsync as AdbDevice


class AdbPackage:
    device = None
    pkg_name = None
    path = None
    declared_perms = []
    req_perms = []
    install_perms = []
    main_activity = None

    def __init__(self, pkg_name: str, device: AdbDevice):
        self.device = device
        self.pkg_name = pkg_name

    # Get the path to the APK, which can be used for pulling the APK off the device for further analysis
    def parse_path(self, dumpsys_result):
        path_begin = dumpsys_result.find("path: ")
        if path_begin != -1 and path_begin + len("path: ") < len(dumpsys_result):
            path_begin = path_begin + len("path: ")
            path_end = dumpsys_result.find("\n", path_begin)
            self.path = dumpsys_result[path_begin:path_end]

    # Get the permissions available to the package
    def parse_permissions(self, dumpsys_result):
        declared_perms_begin = dumpsys_result.find("declared permissions:\n")
        req_perms_begin = dumpsys_result.find("requested permissions:\n")
        install_perms_begin = dumpsys_result.find("install permissions:\n")
        if declared_perms_begin != -1 and req_perms_begin != -1 and install_perms_begin != -1:
            if declared_perms_begin < req_perms_begin and req_perms_begin < install_perms_begin:
                declared_perms_begin = declared_perms_begin + len("declared permissions:\n")
                declared_perms = dumpsys_result[declared_perms_begin:req_perms_begin].split("\n")
                for perm in declared_perms:
                    tmp = perm.strip()
                    if len(tmp) > 0:
                        self.declared_perms.append(tmp)
                req_perms_begin = req_perms_begin + len("requested permissions:\n")
                req_perms = dumpsys_result[req_perms_begin:install_perms_begin].split("\n")
                for perm in req_perms:
                    tmp = perm.strip()
                    if len(tmp) > 0:
                        self.req_perms.append(tmp)
                install_perms_begin = install_perms_begin + len("install permissions:\n")
                install_perms_end = dumpsys_result.find("User ", install_perms_begin)
                install_perms = dumpsys_result[install_perms_begin:install_perms_end].split("\n")
                for perm in install_perms:
                    tmp = perm.strip()
                    if len(tmp) > 0:
                        self.install_perms.append(tmp)

    # Find the main activity of the package which can be used to start the app over ADB using intents
    def parse_main_activity(self, dumpsys_result):
        tmp = dumpsys_result.find("android.intent.action.MAIN:\n")
        begin = tmp + len("android.intent.action.MAIN:\n")
        if tmp != -1 and begin < len(dumpsys_result):
            end = dumpsys_result.find("\n", begin)
            line_data = dumpsys_result[begin:end].strip().split()
            if len(line_data) > 1:
                self.main_activity = line_data[1]

    async def parse_pkg_info(self):
        dumpsys_result = await self.device.shell(f"dumpsys package {self.pkg_name}")
        self.parse_path(dumpsys_result)
        self.parse_permissions(dumpsys_result)
        self.parse_main_activity(dumpsys_result)

    def print_pkg_info(self):
        print(f"Package: {self.pkg_name}")
        print(f"APK path: {self.path}")
        print(f"Main activity: {self.main_activity}")
        print("Permissions:")
        print("  Declared:")
        for perm in self.declared_perms:
            print(f"    {perm}")
        print("  Requested:")
        for perm in self.req_perms:
            print(f"    {perm}")
        print("  Install:")
        for perm in self.install_perms:
            print(f"    {perm}")

    async def pull_pkg(self, out_file="out.apk"):
        return await self.device.pull(self.path, out_file)
