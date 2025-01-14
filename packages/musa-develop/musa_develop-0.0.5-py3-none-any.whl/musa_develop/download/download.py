# import SHELL


class Downloader:

    def __init__(self, name: str = None, version: str = None, folder_path: str = None) -> None:
        self._name = name
        self._yaml_dict = dict()  # READ_YAML
        self._version = version
        self._inhouse = False  # ping(10.10.129.5)
        self._prechecker = None  # CHECKER["self._name"]
        self._folder_path = folder_path
        self._download_link = None

    def precheck(self):
        pre_module_status = self._prechecker.precheck(self._version)
        return pre_module_status.version

    def get_version_and_download_link(self):
        # pre_module_version = self.precheck()

        # auto(newest)
        # specified by argument
        # self._yaml_dict

        # self._download_link = ["xxxxxxxx"] # list: 内网链接，外网链接
        pass

    def make_folder(self):
        if not self._folder_path:
            # generating a default folder name according to time and name
            self._folder_path = self._name + self._version + "_2025-01-08-21-55"
        if self._folder_path:
            # 判断文件夹具有可写入权限吗?
            pass

    def download(self):
        if not self._inhouse:
            # verify md5sum
            pass
        else:
            # verify md5sum
            pass

    def run(self):
        self.get_version_and_download_link()
        self.make_folder()
        self.download()
