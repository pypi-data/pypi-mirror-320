# PyComGrader: A Python Package for Grading C++ Programs

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

PyComGrader is a Python package designed to help educators and students easily evaluate and grade C++ programs against multiple test cases. It provides a simple and efficient way to test programs against multiple test cases and can be used on multiple platforms, including Windows and Linux. The package can be used as a command-line tool and provides various options to customize the grading process. PyComGrader aims to simplify the process of setting up training contests offline, testing problems against multiple test cases during a contest to get preliminary results, and helping prepare and form competitive programmers. However, please note that this package is not intended for official contests and is solely meant as an educational tool.

## Features

- Grade C++ programs against multiple test cases
- Command-line interface for easy usage
- Customizable time and memory limits
- Detailed status messages for each test case
- Cross-platform support (Windows and Linux)

## Installation

To install PyComGrader, use pip:

```sh
pip install pycomgrader
```

### Prerequisites

Before using PyComGrader, ensure that you have `g++` installed and accessible in your system's PATH. PyComGrader relies on `g++` to compile C++ programs before grading them. You can install `g++` using your system's package manager. For example, on Ubuntu, you can install it with:

```sh
sudo apt-get install g++
```

On Windows, you can install `g++` as part of MinGW or through other means.

## Usage

### Getting Started

To start using PyComGrader, follow these steps:

1. Install PyComGrader by running `pip install pycomgrader` in your terminal.
2. Import the necessary modules: `from pycomgrader import Grader`.
3. Create a `Grader` object with the file to test, time limit, and memory limit: `grader = Grader(2000, 128, exec_file = 'my_program')`
4. Create a corresponding directory for the test cases, and place the input files (with the extension `.in`) and expected output files (with the extension `.out`) inside. The filenames for the input and output files can be arbitrary, but they must have the same name. For example, you can have 01.in, 01.out, 02.in, 02.out, etc.
5. Test the program against one or more test cases using the `grader.grade('test_cases_dir')` method.

### Command Line Interface

PyComGrader can be used as a command-line tool by running `pycomgrader` followed by the path to the file to test and the directory with the test cases. For example:
```bash
$ pycomgrader my_program.cpp test_cases_dir
```
You can specify the time limit (milliseconds) and memory limit (megabytes) as positional arguments respectively:
```bash
$ pycomgrader my_program.cpp test_cases_dir 1000 32
```
One of the key features of PyComGrader is its ability to execute C++ programs directly, without the need for a separate compiler. This makes it easy to use on systems where a C++ compiler is not installed, or where the user has other means of compiling their source code. Users can use the `-e` flag when running PyComGrader to indicate that a file should be executed directly.
```bash
$ pycomgrader my_program test_cases_dir -e
```
This will tell PyComGrader to execute the contents of `my_program` directly, rather than compiling it first.

For detailed usage information, run:
```bash
$ pycomgrader --help
```

## License

PyComGrader is released under the MIT License. See LICENSE for details.
