import sys
import os
from musa_develop.check.utils import CheckModuleNames
from musa_develop.utils import FontRed, FontGreen

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env


@set_env("EXECUTED_ON_HOST_FLAG", "False")
def test_check_musa_installed_inside_container():
    """
    check musa installed, whether it works or not

    Simulation Log Details:
        - `simulation_log["MUSAToolkits"]`: A tuple where the second element
          (`True` or `False`) signifies the installation status.
        - other log do not impact the installation check
    """
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [("", "", 0), True],
        "musa_version": (
            """\
musa_toolkits:
{
        "version":      "3.0.0",
        "git branch":   "dev3.0.0",
        "git tag":      "No tag",
        "commit id":    "f50264844211b581e1d9b0dab2447243c8d4cfb0",
        "commit date":  "2024-06-21 15:20:10 +0800
}""",
            "",
            0,
        ),
        "test_musa": ("", "", 0),
    }
    musa_ground_truth = "MUSAToolkits                Version: 3.0.0+f502648"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


@set_env("EXECUTED_ON_HOST_FLAG", "False")
def test_check_musa_uninstalled_inside_container():
    """
    check musa uninstalled, whether it works or not
    see more in function above: test_check_musa_installed_inside_container
    """
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": [("", "", 0), False],
        "musa_version": (
            """\
musa_toolkits:
{
        "version":      "3.0.0",
        "git branch":   "dev3.0.0",
        "git tag":      "No tag",
        "commit id":    "f50264844211b581e1d9b0dab2447243c8d4cfb0",
        "commit date":  "2024-06-21 15:20:10 +0800
}""",
            "",
            0,
        ),
        "test_musa": ("", "", 0),
    }
    musa_ground_truth = f"""\
MUSAToolkits
    - status: {FontRed('UNINSTALLED')}
    - {FontGreen("Recommendation")}: Unable to find /usr/local/musa directory, please check if musa_toolkits is installed."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_musa_installed_inside_container()
