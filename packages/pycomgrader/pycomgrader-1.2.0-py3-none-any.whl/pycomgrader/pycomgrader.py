"""
This module provides a grader for C++ programs.
"""

import os
import subprocess
import time
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import psutil


class GraderError(Exception):
    """
    Raised when there's an error while grading a submission.
    """


class Status(Enum):
    """
    Possible statuses for a test case.
    """

    AC = auto()
    WA = auto()
    TLE = auto()
    MLE = auto()
    RTE = auto()


@dataclass
class TestCase:
    """
    Represents a test case.

    Attributes:
        name (str): The name of the test case.
        status (Status): The status of the test case.
        time (float): The time taken by the program to complete the test case.
        mem (float): The maximum memory used by the program during the test case.
        error_message (str, optional): The error message if any.
    """

    name: str
    status: Status
    time: float
    mem: float
    error_message: str = None


class Grader:
    """
    Manages the grading process for a programming assignment.
    """

    def __init__(
        self,
        time_limit=1000,
        memory_limit=32,
        *,
        source_file: str | Path = None,
        exec_file: str | Path = None,
    ):
        """
        Initializes a Grader instance.

        Parameters:
            time_limit (int, optional): The maximum amount of time (in milliseconds) allowed
            for the grading process. Defaults to 1000.
            memory_limit (int, optional): The maximum amount of memory (in megabytes) allowed
            for the grading process. Defaults to 32.
            source_file (str or Path, optional): The path to the source code file to be graded.
            If not provided, an executable file must be provided.
            exec_file (str or Path, optional): The path to the executable file to be graded.
            If not provided, a source file must be provided.

        Raises:
            GraderError: If both a source file and an executable file are provided,
            or if neither a source file nor an executable file is provided.
        """
        if (source_file is None) == (exec_file is None):
            raise GraderError(
                "expected either a source code file or an executable but not both"
            )

        self.time_limit = time_limit / 1000
        self.memory_limit = memory_limit
        self._source_file = self._valid_file(source_file) if source_file else None
        self._exec_file = self._valid_file(exec_file) if exec_file else None

    @property
    def source_file(self):
        return self._source_file

    @source_file.setter
    def source_file(self, source_file):
        self._source_file = self._valid_file(source_file) if source_file else None
        if self._source_file:
            self._exec_file = None

    @property
    def exec_file(self):
        return self._exec_file

    @exec_file.setter
    def exec_file(self, exec_file):
        self._exec_file = self._valid_file(exec_file) if exec_file else None
        if self._exec_file:
            self._source_file = None

    def grade(self, test_cases_dir: str | Path):
        """
        Grades a set of test cases located in the specified directory.

        Parameters:
            test_cases_dir (str | Path): The directory containing the test cases.

        Returns:
            List[TestCase]: A list of `TestCase` objects, each representing a test case
            and containing information about its name, status, time, and memory usage.
        """
        test_cases_dir = self._valid_dir(test_cases_dir)
        in_list = sorted(test_cases_dir.glob("*.in"))
        out_list = sorted(test_cases_dir.glob("*.out"))
        results = []

        for input_file, output_file in zip(in_list, out_list):
            test_case = self.check_test_case(input_file, output_file)
            results.append(test_case)

        return results

    def check_test_case(self, input_file: str | Path, expected_output: str | Path):
        """
        Checks a test case against the expected output.

        Parameters:
            input_file (str | Path): The path to the input file for the test case.
            expected_output (str | Path): The path to the expected output file for the test case.

        Returns:
            TestCase: An object containing information about the test case, including its name,
            status, execution time, and memory usage.
        """
        if self.exec_file is None:
            self._compile()

        input_file = self._valid_file(input_file)
        expected_output = self._valid_file(expected_output)
        submission_output = self.exec_file.with_suffix(".out.tmp")

        with (
            open(input_file, encoding="UTF-8") as input_file_handle,
            open(submission_output, "w", encoding="UTF-8") as output_file_handle,
        ):
            process = self._start_process(input_file_handle, output_file_handle)
            start = time.perf_counter()
            max_mem = 0

            status, max_mem = self._monitor_process(process, start, max_mem)
            end = time.perf_counter()

        if status is None:
            status = self._compare_output(submission_output, expected_output)

        error_message = process.stderr
        return TestCase(input_file.stem, status, end - start, max_mem, error_message)

    def _valid_file(self, file):
        """
        Returns a `Path` object if the file exists and is a regular file.

        Parameters:
            file (str): File path or name

        Return:
            Path: A `Path` instance representing the valid file

        Raises:
            FileNotFoundError: If the file does not exist or is not a regular file.
        """
        path = Path(file)
        if path.exists() and path.is_file():
            return path

        raise FileNotFoundError(f"file doesn't exist ({file})")

    def _valid_dir(self, directory):
        """
        Returns a `Path` object if the directory exists and is a regular directory.

        Parameters:
            directory (str): Directory path or name

        Return:
            Path: A `Path` instance representing the valid directory

        Raises:
            FileNotFoundError: If the directory does not exist or is not a regular directory.
        """
        path = Path(directory)
        if path.exists() and path.is_dir():
            return path

        raise FileNotFoundError(f"directory doesn't exist ({directory})")

    def _compile(self):
        """
        Compiles the submitted program.

        Raises:
            GraderError: If there are any compilation errors.
        """
        try:
            subprocess.check_output(
                ["g++", self._source_file, "-o", self._source_file.with_suffix(".o")],
                stderr=subprocess.DEVNULL,
            )
            self.exec_file = self._source_file.with_suffix(".o")
        except subprocess.CalledProcessError:
            raise GraderError("compile error") from None

    def _start_process(self, input_file_handle, output_file_handle):
        """
        Starts the process for the submitted program.

        Parameters:
            input_file_handle (file object): The input file handle.
            output_file_handle (file object): The output file handle.

        Returns:
            subprocess.Popen: The process object.
        """
        try:
            return subprocess.Popen(
                [os.path.join(".", str(self.exec_file))],
                stdin=input_file_handle,
                stdout=output_file_handle,
                stderr=subprocess.PIPE,
            )
        except Exception:
            raise GraderError(f"error while executing {self.exec_file}") from None

    def _monitor_process(self, process, start, max_mem):
        """
        Monitors the process for time and memory limits.

        Parameters:
            process (subprocess.Popen): The process object.
            start (float): The start time.
            max_mem (float): The maximum memory used.

        Returns:
            tuple: The status and error message.
        """
        while process.poll() is None:
            time.sleep(0.001)
            if self._is_time_limit_exceeded(start):
                self._kill_process_rec(process.pid)
                return Status.TLE, max_mem

            max_mem = max(max_mem, self._get_process_memory(process.pid))
            if max_mem > self.memory_limit:
                self._kill_process_rec(process.pid)
                return Status.MLE, max_mem

        if process.returncode:
            return Status.RTE, max_mem

        return None, max_mem

    def _compare_output(self, submission_output, expected_output):
        """
        Compares the submission output with the expected output.

        Parameters:
            submission_output (Path): The path to the submission output file.
            expected_output (Path): The path to the expected output file.

        Returns:
            tuple: The status and error message.
        """
        try:
            with (
                submission_output.open(encoding="UTF-8") as subm_file,
                expected_output.open(encoding="UTF-8") as expected_file,
            ):
                if subm_file.read() == expected_file.read():
                    return Status.AC
                return Status.WA
        except Exception:
            raise GraderError("error while trying to open output files") from None

    def _is_time_limit_exceeded(self, start):
        """
        Checks if the time limit is exceeded.

        Parameters:
            start (float): The start time.

        Returns:
            bool: True if the time limit is exceeded, False otherwise.
        """
        return time.perf_counter() - start > self.time_limit

    def _get_process_memory(self, proc_pid):
        """
        Gets the resident set size (RSS) of a process with the given PID.

        Parameters:
            proc_pid (int): The process ID of the process to get the memory usage for.

        Returns:
            int: The RSS of the process in bytes.
        """
        try:
            process = psutil.Process(proc_pid)
            mem_info = process.memory_info()
            return mem_info.rss / 1024**2
        except psutil.NoSuchProcess:
            return 0

    def _kill_process_rec(self, pid):
        """
        Kills a process and all its children.

        Parameters:
            pid (int): The process ID of the process to kill.
        """
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        except psutil.NoSuchProcess:
            pass
