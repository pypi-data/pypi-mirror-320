import yaml
from typing import Literal
from functools import namedtuple
from dataclasses import dataclass
import os


@dataclass
class ImageClass:
    image_type: str
    driver_version: str
    gpu_type: str
    image_tag: str = "tag"


class YAML:

    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        self.yaml_data = self.get_yaml_data(self.yaml_path)

    def get_yaml_data(self, file_path):
        """reade yaml file"""
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        return data

    def get_sub_key_list(self, module_name):
        dict_list = self.yaml_data[module_name]
        sub_key_list = list(dict_list[0].keys())
        return sub_key_list

    def get_dict_in_list(self, module_name: str, special_version: str) -> int:
        """
        Determine this dictionary in the list by v of the first kv pair in the dictionary
        return the index of the dictionary

        Example:
        'driver': [{'Driver_Version_From_Dpkg': '2.7.0-rc3-0822',
             'dependency': {'supported_kernel': ['5.4.0-42-generic',
                                                 '5.15.0-105-generic'],
                            'unsupported_kernel': ['5.15.0-127-generic']}}],
        special_version_dict, first_key = YAML(file_path).get_dict_in_list('driver', '2.7.0-rc3-0822')

        special_version_dict:
                    {'Driver_Version_From_Dpkg': '2.7.0-rc3-0822',
                    'dependency': {'supported_kernel': ['5.4.0-42-generic',
                                                        '5.15.0-105-generic'],
                                    'unsupported_kernel': ['5.15.0-127-generic']}}
        first_key: 'Driver_Version_From_Dpkg'
        """
        dict_list = self.yaml_data[module_name]  # get special module version list
        first_key, *_ = self.get_sub_key_list(module_name)
        for d in dict_list:
            if str(d[first_key]) == special_version:
                return d


class ImageYaml(YAML):
    def __init__(self):
        super().__init__()
        self.torch_musa_image = os.path.join(
            self.root_path, "download/images/torch_musa_images.yaml"
        )
        self.ubuntu_image = os.path.join(
            self.root_path, "download/images/ubuntu_images.yaml"
        )
        self.vllm_image = os.path.join(
            self.root_path, "download/images/vllm_images.yaml"
        )
        self.images_dict = {
            "torch_musa": self.torch_musa_image,
            "ubuntu": self.ubuntu_image,
            "vllm": self.vllm_image,
        }

    def _get_image_data(self, image_type: str):
        # read image yaml
        data = self.get_yaml_data(self.images_dict[image_type])
        # get image data
        image_dicts = data[image_type]
        # get image_name without tag
        image_name = image_dicts["image_name"]
        # get version list
        image_list = image_dicts["version"]
        return image_name, image_list

    def get_image_name(self, image_args: ImageClass):
        """get image name
        ImageClass:
        - image_type: ubuntu, torch_musa, mtt-vllm
        - dri_version: xxxx
        - gpu_type: s70, s80, s3000, s4000, all
        - tag: py38, py39, py310
        """
        image_name, image_list = self._get_image_data(image_args.image_type)
        image_tag = str(self._get_image_tag(image_list, image_args))
        return image_name + ":" + image_tag

    def get_image_list(
        self, image_type: str, image_version: str, gpu_arch: str
    ) -> list:
        """
        Get image list from yaml file according to image type and driver version
        """
        image_list = []
        image_name, image_all_versions_list = self._get_image_data(image_type)
        for images in image_all_versions_list:
            if images["version"] == image_version:
                for gpu_type in list(images.keys())[1:]:
                    if gpu_type == gpu_arch:
                        image_list += list(images[gpu_type].values())

                return [image_name + ":" + image_tag for image_tag in image_list]

    def _get_image_tag(self, image_list: list, image_args: ImageClass):
        if image_args.image_type in ["mtt-vllm", "ubuntu", "torch_musa"]:
            image_dict = self.get_dict_in_list(image_args.driver_version, image_list)
            image_tag = image_dict[image_args.gpu_type][image_args.image_tag]
            return image_tag
        else:
            print("Image type not supported, only support mtt-vllm, ubuntu, torch_musa")
            exit()


Component_Info = namedtuple("Component_Info", ["version", "url", "sha"])


class ComponentsYaml(YAML):
    """
    get driver、mtml、mt-container-toolkit、sgpu_dkms info
    """

    def __init__(self):
        super().__init__()
        self.driver_yaml = os.path.join(self.root_path, "download/driver.yaml")
        self.mtml_yaml = os.path.join(self.root_path, "download/mtml.yaml")
        self.mt_container_toolkit_yaml = os.path.join(
            self.root_path, "download/mt-container-toolkit.yaml"
        )
        self.sgpu_dkms_yaml = os.path.join(self.root_path, "download/sgpu_dkms.yaml")
        self.requirements = os.path.join(self.root_path, "version_requirements.yaml")
        self.components_dict = {
            "driver": self.driver_yaml,
            "mtml": self.mtml_yaml,
            "mt-container-toolkit": self.mt_container_toolkit_yaml,
            "sgpu_dkms": self.sgpu_dkms_yaml,
            "components": self.requirements,
        }

    def get_component_info(self, component_type, version: str) -> Component_Info:  # type: ignore
        """
        get info: version, url, sha256
        """
        file_path = self.components_dict[component_type]
        data = self.get_yaml_data(file_path)
        # get version list
        component_list = data["download"]
        # get component url
        component_dict = self.get_dict_in_list(version, component_list)

        return Component_Info(
            component_dict["version"], component_dict["url"], component_dict["sha256"]
        )

    def get_dependency_component_version(
        self,
        component_name: Literal[
            "mt-container-toolkit", "driver", "musa_runtime", "torch_musa"
        ],
        component_version: str,
        component_commit_id: str = "",
    ):
        data = self.get_yaml_data(self.requirements)
        # musa_runtime need commit id for query
        query_version = component_version + component_commit_id
        dependency_component_info = data[component_name][query_version]
        return dependency_component_info


if __name__ == "__main__":
    # yaml_obj = ImageYaml()
    # image_class = ImageClass("torch_musa", "1.3.0", "s80", "py38")
    # # 获取特定镜像
    # print(yaml_obj.get_image_name(image_class))
    # print("*"*30)
    # # 获取特定驱动支持的镜像列表
    # print(yaml_obj.get_image_list('torch_musa', "s80", '1.3.0'))
    # print("*"*30)
    # components_obj = ComponentsYaml()
    # print(
    #     components_obj.get_dependency_component_version(
    #         "mt-container-toolkit", "1.9.0-1"
    #     )
    # )
    # print(components_obj.get_dependency_component_version("driver", "2.7.0-rc3-0822"))
    # print(components_obj.get_dependency_component_version("musa_runtime", ""))

    dependency_obj = YAML("version_requirements.yaml")
    dict, first_key = dependency_obj.get_dict_in_list("torch_musa", "1.3.0+60e54d8")
    first_key = dependency_obj.get_first_key("torch_musa")
    print(first_key)
