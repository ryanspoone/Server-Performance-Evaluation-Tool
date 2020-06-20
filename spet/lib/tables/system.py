# -*- coding: utf-8 -*-
"""Handles creating a human-readable system information display."""

import logging

from ..utilities import prettify


def __row_helper(title, value, unit=None, seperator=None):
    """Helps format system information in a standardized way.

    Args:
        title (str): The title of the value. Left aligned.
        value (any): The value to be displayed.
        unit (str, optional): The value's unit.
        seperator (str): The seperator between the value and unit.

    Returns:
        String: Title (left aligned, 50 char) and value with unit (right
        aligned, 28 char).
    """
    title = str(title)

    if seperator is None:
        seperator = " "

    if unit:
        value = "{}{}{}".format(value, seperator, unit)
    else:
        value = str(value)

    length_left = 78 - len(title)

    if length_left - len(value) < 1:
        return "{:30} {:>48}\n".format(title, value)
    else:
        return "{:{}} {:>{}s}\n".format(title, len(title), value, length_left)


def table(system_info, avx512=None):
    """Creates a readable display for the system information.

    Args:
        system_info (namedtuple): The system information.
        avx512 (bool): If AVX-512 instructions are enabled.

    Returns:
        String: Table of system information.
    """
    if not system_info:
        logging.debug("No system information passed.")
        return ""

    boundary = "=" * 79 + "\n"

    seperator = "-" * 79 + "\n"

    header = "System Information".center(79) + "\n"

    display = seperator
    display += header
    display += boundary

    if system_info.processorName:
        display += __row_helper("Processor Name:", system_info.processorName)
    if system_info.l1iCache:
        display += __row_helper(
            "L1 Instruction Cache:",
            prettify.byte_size(system_info.l1iCache, suffix="B"),
        )
    if system_info.l1dCache:
        display += __row_helper(
            "L1 Data Cache:", prettify.byte_size(system_info.l1dCache, suffix="B")
        )
    if system_info.l2Cache:
        display += __row_helper(
            "L2 Cache:", prettify.byte_size(system_info.l2Cache, suffix="B")
        )
    if system_info.l3Cache:
        display += __row_helper(
            "L3 Cache:", prettify.byte_size(system_info.l3Cache, suffix="B")
        )
    if system_info.sockets:
        display += __row_helper("Socket(s):", system_info.sockets)
    if system_info.cores:
        display += __row_helper("Core(s):", system_info.cores)
    if system_info.threads:
        display += __row_helper("Thread(s):", system_info.threads)
    if system_info.numaNodes:
        display += __row_helper("NUMA Node(s):", system_info.numaNodes)

    display += seperator

    if system_info.osName and system_info.osVer:
        display += __row_helper(
            "Operating System:", system_info.osName, unit=system_info.osVer
        )
    if system_info.archBits:
        display += __row_helper(
            "Architecture:", system_info.archBits, unit="bit", seperator="-"
        )
    if system_info.archType:
        display += __row_helper("Architecture Type:", system_info.archType)

    display += seperator

    if system_info.memory:
        display += __row_helper("Total RAM:", system_info.memory, unit="GB")
    if system_info.memoryFrequency:
        display += __row_helper(
            "Memory Frequency:", system_info.memoryFrequency, unit="MHz"
        )

    display += seperator

    if system_info.gccVer:
        display += __row_helper("GNU Compiler Collection (GCC):", system_info.gccVer)
    if system_info.cflags:
        display += __row_helper("C Flags:", system_info.cflags)
    if avx512:
        display += __row_helper("LINPACK AVX-512 Flags:", "Enabled")

    display += seperator

    return display
