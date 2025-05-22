class PackageData():
    pkg = None
    uid = None
    data_tx = None
    data_rx = None

    def __init__(self, pkg):
        self.pkg = pkg

    def print(self):
        print(f"Package: {self.pkg}, UID: {self.uid}, Transmitted Data: {self.data_tx}, Received Data: {self.data_rx}")
