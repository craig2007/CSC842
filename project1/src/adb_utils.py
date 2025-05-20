from ppadb.client import Client as AdbClient

class AdbUtils():
    def __init__(self, android_device, adb_host="127.0.0.1", adb_port=5037):
        self.client = AdbClient(host=adb_host, port=adb_port)
        self.device = self.client.device(android_device)

    def get_packages(self):
        result = self.device.shell("cmd package list packages")
        if result.exit_code == 0:
            return result.output
        return result.error
