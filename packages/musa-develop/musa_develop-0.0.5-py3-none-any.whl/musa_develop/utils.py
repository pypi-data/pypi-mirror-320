import subprocess
import platform
import argparse


def parse_arg(value):
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected format 'component=version'")
    component, version = value.split("=", 1)
    return component, version


def ping(url):
    # 参数解析：'-n' 表示发送的echo请求的次数，'-w' 表示等待回复的超时时间（毫秒）
    # 这些参数在不同的操作系统中可能有所不同，这里以Windows为例
    parameter = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", parameter, "1", url]  # 对URL执行一次ping操作

    try:
        response = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # ping命令执行成功，返回码为0
        if response.returncode == 0:
            print(f"Ping {url} successful")
            return True
        else:
            print(f"Ping {url} failed")
            return False
    except Exception as e:
        print(f"Error pinging {url}: {e}")
        return False


def FormatGitVersion(version: str = None):
    split_version = version.split("+")
    return (
        split_version[0] + "+" + split_version[1][0:7]
        if len(split_version) == 2
        else version
    )


class SHELL:
    def __init__(self, shell=True, text_mode=True):
        self.shell = shell
        self.text_mode = text_mode

    def run_cmd(self, cmd: str, is_split=True):
        completed_process = subprocess.run(
            cmd,
            shell=self.shell,
            text=self.text_mode,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        # Flexible control of whether to preprocess the original output
        if is_split:
            completed_process.stdout = self.check_output(completed_process.stdout)
        return (
            completed_process.stdout,
            completed_process.stderr,
            completed_process.returncode,
        )

    def check_output(self, output) -> list:
        """
        If the output is a string with newline characters, split it into a list
        """
        if isinstance(output, str):
            output = output.strip()
            if "\n" in output:
                return [line.strip() for line in output.splitlines()]
            else:
                return output
        else:
            return output


def FontGreen(string: str):
    return "\033[32m" + string + "\033[0m"


def FontRed(string: str):
    return "\033[91m" + string + "\033[0m"


REPORT_TITLE = """\
=====================================================================
======================= MOORE THREADS REPORT ========================
====================================================================="""

CHECK_TITLE = """\
=====================================================================
======================== MOORE THREADS CHECK ========================
====================================================================="""

REPORT_END_LINE = """\
====================================================================="""

SEPARATION_LINE = """\
---------------------------------------------------------------------"""
