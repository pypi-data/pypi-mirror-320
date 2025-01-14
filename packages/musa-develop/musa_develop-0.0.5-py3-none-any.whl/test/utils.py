import sys
import io
import re
import os
from functools import wraps

from musa_develop.check import CHECKER
from musa_develop.report import report

RED_PREFIX = "\x1b[91m"
GREEN_PREFIX = "\x1b[32m"
COLOR_SUFFIX = "\x1b[0m"


def capture_print(func, arguments=None):
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured_output
    if arguments:
        func(arguments)
    else:
        func()
    sys.stdout = original_stdout
    captured = captured_output.getvalue()
    captured_output.close()
    return captured


def set_env(key, value):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            os.environ[key] = value
            try:
                result = func(*args, **kwargs)
            finally:
                del os.environ[key]
            return result

        return wrapper

    return decorator


class TestChecker:

    def __init__(self, checker_name: str = None):
        self._checker = CHECKER[checker_name]()
        self._is_successful_ground_truth = True
        self._simulation_log = dict()
        self._report_string = None
        self._report_string_ground_truth = None
        self._ground_truth = None

    def set_is_successful_ground_truth(self, is_successful_ground_truth: bool = True):
        self._is_successful_ground_truth = is_successful_ground_truth

    def set_simulation_log(self, simulation_log: dict = None):
        self._simulation_log = simulation_log

    def set_module_ground_truth(self, ground_truth: str):
        self._ground_truth = ground_truth

    def set_summary(self, summary: str):
        self._summary = summary

    def set_report_ground_truth(self, report_ground_truth: str):
        self._report_string_ground_truth = report_ground_truth

    def test_core_module(self):
        assert (
            self._ground_truth
        ), "Test failed. Ground Truth is empty, please check the ground truth!"
        assert (
            self._ground_truth in self._report_string
        ), f"Test failed. Report '{self._report_string}' should contain GroundTruth '{self._ground_truth}', but it does not!"

    def test_overall_status(self):
        assert (
            self._checker._is_successful == self._is_successful_ground_truth
        ), f"Overall status test failed. Expect Ground Truth value is {self._is_successful_ground_truth}, but got value is {self._checker._is_successful}!"
        if self._is_successful_ground_truth:
            ground_truth = f"\x1b[32m{self._checker._tag.upper()} CHECK OVERALL Status: \x1b[0mSUCCESSFUL"
        else:
            ground_truth = f"\x1b[32m{self._checker._tag.upper()} CHECK OVERALL Status: \x1b[0mFAILED"
        assert (
            ground_truth in self._report_string
        ), f"Overall status test failed. Report string should contain Ground Truth value {ground_truth}, but report result is {self._report_string}!"

    def test_report_title(self):
        ground_truth = """\
=====================================================================
======================== MOORE THREADS CHECK ========================
=====================================================================\
"""
        assert (
            ground_truth in self._report_string
        ), f"Report title test failed. Report string should contain Ground Truth value {ground_truth}, but report result is {self._report_string}!"

    def test_report_endline(self):
        ground_truth = (
            "====================================================================="
        )
        assert (
            ground_truth in self._report_string
        ), f"Report title test failed. Report string should contain Ground Truth value {ground_truth}, but report result is {self._report_string}!"

    def test_summary(self):
        matched = re.search(
            self._summary,
            self._report_string.replace(RED_PREFIX, "")
            .replace(COLOR_SUFFIX, "")
            .replace("\n", ""),
        )

        assert (
            matched
        ), f"Summary test failed. Report string should contain Ground Truth value {self._summary}, but report result is {self._report_string}!"

    def test_single_module(self):
        self._checker.inject_inspect_log(self._simulation_log)
        self._checker.check()
        self._report_string = capture_print(self._checker.report)

        assert self._report_string, "Report string test failed. Report string is empty!"
        self.test_report_title()
        self.test_core_module()
        self.test_report_endline()

    def test_all(self):
        self._checker.inject_inspect_log(self._simulation_log)
        self._checker.check()
        self._report_string = capture_print(self._checker.report)

        assert self._report_string, "Report string test failed. Report string is empty!"
        self.test_report_title()
        self.test_overall_status()
        self.test_core_module()
        self.test_summary()
        self.test_report_endline()

    def test_whole_report(self):
        self._checker.inject_inspect_log(self._simulation_log)
        self._checker.check()
        self._report_string = capture_print(self._checker.report)

        assert (
            self._report_string == self._report_string_ground_truth
        ), "The whole Report test failed!"


def ReportTest(inject_log: dict = None, ground_truth: str = None):
    report_string = capture_print(report, inject_log)
    # 0. test prompt
    prompt_ground_truth = (
        "The report is being generated, please wait for a moment......"
    )
    assert (
        prompt_ground_truth in report_string
    ), f"Prompt string test failed, expected ground truth is:\n{prompt_ground_truth}\nbut it is not found in result:\n{report_string}\n"
    # 1. test title
    title_ground_truth = """\
=====================================================================
======================= MOORE THREADS REPORT ========================
====================================================================="""
    assert (
        title_ground_truth in report_string
    ), "Title string test failed, expected ground truth is:\n{title_ground_truth}\nbut it is not found in result:\n{report_string}\n"

    # 2. test key module
    assert (
        ground_truth
    ), "'ground_truth' must not be None or empty string when testing Report!"
    ground_truth_list = ground_truth.split("\n")
    for ground_truth_value in ground_truth_list:
        assert (
            ground_truth_value in report_string
        ), "Key string test failed, expected ground truth is:\n{ground_truth_value}\nbut it is not found in result:\n{report_string}\n"

    # 3. test end line
    last_line = report_string.split("\n")[-2]
    last_line_ground_truth = """\
====================================================================="""
    assert (
        last_line_ground_truth == last_line
    ), "Last end line test failed, expected ground truth is:\n{last_line_ground_truth}\nbut it is not found in result:\n{report_string}\n"
