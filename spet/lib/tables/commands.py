# -*- coding: utf-8 -*-
"""Used for creating a human readable display for SPET commands."""

import os
import textwrap


def __remove_paths(command):
    """Removes all preceding paths from commands.

    Args:
        command (str): The shell command.

    Example:
    >>> __remove_paths('modprobe msr; /src/mlc/mlc_avx512 --latency_matrix')
    'modprobe msr; mlc_avx512 --latency_matrix'

    Returns:
        String: Pathless commands.
    """
    cmd = []
    for part in command.split():
        cmd.append(os.path.split(part)[1])
    return " ".join(cmd)


def formatted(commands):
    """A formatted display of the commands for the results file.

    Args:
        commands (dict): The SPET commands for the formatted display.

    Returns:
        String: Commands display.
    """
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"

    display = "\n"
    display += "Primary Commands Used".center(79) + "\n"
    display += "=====================".center(79) + "\n"

    if "Timed Kernel Compilation" in commands:
        display += seperator
        display += "Timed Kernel Compilation".center(79) + "\n"
        display += boundary
        for command in commands["Timed Kernel Compilation"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "zlib" in commands:
        display += seperator
        display += "zlib".center(79) + "\n"
        display += boundary
        for command in commands["zlib"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "LMbench" in commands:
        display += seperator
        display += "LMbench".center(79) + "\n"
        display += boundary
        for command in commands["LMbench"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "MLC" in commands:
        display += seperator
        display += "Intel(R) Memory Latency Checker".center(79) + "\n"
        display += boundary
        for command in commands["MLC"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "OpenSSL" in commands:
        display += boundary
        display += "OpenSSL".center(79) + "\n"
        display += boundary
        for command in commands["OpenSSL"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "STREAM" in commands:
        display += seperator
        display += "STREAM".center(79) + "\n"
        display += boundary
        for command in commands["STREAM"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "High-Performance Linpack" in commands:
        display += seperator
        display += "High-Performance Linpack".center(79) + "\n"
        display += boundary
        for command in commands["High-Performance Linpack"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "YCSB SQL" in commands:
        display += boundary
        display += "YCSB SQL using MySQL".center(79) + "\n"
        display += boundary
        for command in commands["YCSB SQL"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "YCSB NoSQL" in commands:
        display += seperator
        display += "YCSB NoSQL using Cassandra".center(79) + "\n"
        display += boundary
        for command in commands["YCSB NoSQL"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    if "Docker" in commands:
        display += seperator
        display += "Docker".center(79) + "\n"
        display += boundary
        for command in commands["Docker"]:
            display += (
                textwrap.fill(
                    __remove_paths(command),
                    break_long_words=False,
                    break_on_hyphens=False,
                    subsequent_indent="        ",
                )
                + "\n"
            )
            display += seperator
        display += "\n"

    return display
