"""
This module provides a command-line interface (CLI) for grading C++ programs.
"""

import argparse
import time
from enum import Enum
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

try:
    from pycomgrader import Grader, GraderError, Status
except ImportError:
    from src.pycomgrader import Grader, GraderError, Status


class StatusMessage(Enum):
    """
    Enumeration class representing different status messages.
    """

    AC = "[bold green]accepted[/bold green]"
    WA = "[bold red]wrong answer[/bold red]"
    TLE = "[bold red]time limit exceeded[/bold red]"
    MLE = "[bold red]memory limit exceeded[/bold red]"
    RTE = "[bold yellow]runtime error[/bold yellow]"
    CE = "[bold blue]compile error[/bold blue]"


def run_cli_grader():
    """
    Command-line interface for grading C++ programs.
    """
    parser = argparse.ArgumentParser(description="offline grader for C++ programs")
    parser.add_argument(
        "file",
        type=Path,
        help="path to the program to submit",
    )
    parser.add_argument(
        "dir",
        type=Path,
        help="path to the directory containing the test cases",
    )
    parser.add_argument(
        "time",
        nargs="?",
        type=int,
        default=1000,
        help="maximum amount of time (in milliseconds) to run the program",
    )
    parser.add_argument(
        "mem",
        nargs="?",
        type=int,
        default=32,
        help="maximum amount of memory (in MB) to use for the program",
    )
    parser.add_argument(
        "-e",
        "--executable",
        action="store_true",
        help="notifies the grader that the file is executable",
    )
    args = parser.parse_args()

    _grade(args.file, args.dir, args.time, args.mem, args.executable)


def _grade(
    file: str | Path, directory: str | Path, time_limit=1000, mem=32, executable=False
):
    """
    Grades a C++ program using PyComGrader.

    Parameters:
        file (str | Path): The path to the program file.
        directory (str | Path): The path to the directory containing the test cases.
        time (int, optional): The maximum amount of time (in milliseconds) to run the program.
        Defaults to 1000.
        mem (int, optional): The maximum amount of memory (in MB) to use for the program.
        Defaults to 32.
        executable (bool, optional): Whether the file is an executable.
        Defaults to False.
    """
    try:
        grader = (
            Grader(exec_file=file, time_limit=time_limit, memory_limit=mem)
            if executable
            else Grader(source_file=file, time_limit=time_limit, memory_limit=mem)
        )
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(
            f"file '{file}' is not a valid C++ program file"
        ) from None

    console = Console()

    try:
        results = grader.grade(directory)
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(
            f"directory '{directory}' doesn't exist"
        ) from None
    except GraderError:
        console.print(StatusMessage.CE.value)
        return

    _print_results(console, file, results)


def _print_results(console, file, results):
    """
    Prints the results of the grading process.

    Parameters:
        console (Console): The console object for printing.
        file (str | Path): The path to the program file.
        results (list): The list of grading results.
    """
    file_path = Path(file)
    console.print(f"[bold]running {file_path.stem}...[/bold]")

    accepted = 0
    total_tests = len(results)

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Grading...", total=total_tests)

        for result in results:
            time.sleep(0.3)  # Simulate some delay for the animation
            message = (
                f"test case {result.name}:\t{StatusMessage[result.status.name].value}\t"
                + f"[{result.time:.3f} s, {result.mem:.2f} MB]"
            )
            console.print(message)
            if result.status == Status.AC:
                accepted += 1
            progress.update(task, advance=1)
        progress.remove_task(task)

    if results:
        points = accepted * 100 / len(results)
    else:
        points = 0.0

    console.print(
        f"[bold]final score: {accepted}/{len(results)} ({points:.1f} points)[/bold]"
    )


if __name__ == "__main__":
    run_cli_grader()
