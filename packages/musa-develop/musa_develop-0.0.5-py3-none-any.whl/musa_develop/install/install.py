from abc import ABC, abstractmethod

from musa_develop.download import Downloader
from musa_develop.check import CHECKER
from musa_develop.check.utils import CheckModuleNames, Status


class PackageManager(ABC):

    def __init__(self, name: str = None, version: str = None):
        self._name = name
        self._downloader = None
        self._checker = None
        self._pkg_path = None
        self._preinstaller = None

        # =========
        # need check name

    def update_version(self, version: str = None):
        self._target_version = version

    @abstractmethod
    def uninstall_cmd(self):
        # 卸载完成后，需要查看，是否卸载成功
        # torch_musa存在需要多次卸载的情况
        pass

    def uninstall(self):
        self.uninstall_cmd()

    @abstractmethod
    def install_cmd(self):
        pass

    def version_lookup(self):
        pre_component_version = "v1.0.0"
        pass
        return pre_component_version

    def install(self):
        status = self._checker.run()
        if (
            status["name"].version == self._target_version
            and status["name"].status == Status.SUCCESS
        ):
            print("has already installed successfully!")
            exit()
        # =============
        if self._preinstaller:
            pre_version = self.version_lookup()
            self._preinstaller.update_version(pre_version)
            self._preinstaller.install()
        else:
            self.uninstall()
            self.install_cmd()
        # =============

    def update(self):
        self.uninstall()
        self.install()


class DriverPkgMgr(PackageManager):

    def __init__(self, name: str = None, version: str = None):
        super().__init__(name, version)
        self._downloader = Downloader(name, version)
        self._checker = CHECKER[CheckModuleNames.driver.name]()

    def uninstall_cmd(self):
        pass

    def install_cmd(self):
        pass


class ContainerToolkitsPkgMgr(PackageManager):

    def __init__(self, name: str = None, version: str = None):
        super().__init__(name, version)
        self._downloader = Downloader(name, version)
        self._checker = CHECKER[CheckModuleNames.container_toolkit.name]()

    def uninstall_cmd(self):
        pass

    def install_cmd(self):
        pass


class MusaPkgMgr(PackageManager):

    def __init__(self, name: str = None, version: str = None):
        super().__init__(name, version)
        self._downloader = Downloader(name, version)
        self._checker = CHECKER[CheckModuleNames.musa.name]()
        self._preinstaller = [
            DriverPkgMgr(name, version),
        ]

    def uninstall_cmd(self):
        pass

    def install_cmd(self):
        pass
