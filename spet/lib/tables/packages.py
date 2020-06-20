# -*- coding: utf-8 -*-
"""Used for creating a human readable display for SPET packages."""

from spet.lib.system import java


def __row_helper(title, value, unit=None, seperator=None):
    """Helps format package information in a standardized way.

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


def table(packages, processor):
    """A formatted display of the packages for the results file.

    Args:
        packages (namedtuple): The SPET packages for the formatted display.
        processor (str): The processor name

    Returns:
        String: Packages display.
    """
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"

    display = "\n"
    display += seperator
    display += "Primary Packages Used".center(79) + "\n"
    display += boundary

    java_ver = java.version()

    if packages.lmbench:
        display += __row_helper("LMbench:", packages.lmbench)
    if packages.mlc:
        display += __row_helper("Intel(R) Memory Latency Checker:", packages.mlc)
    if packages.openssl:
        display += __row_helper("OpenSSL:", packages.openssl)
    if packages.linpack:
        display += __row_helper("High-Performance Linpack:", packages.linpack)
    if packages.stream:
        display += __row_helper("STREAM:", packages.stream)
    if packages.linux:
        display += __row_helper("Linux Kernel:", packages.linux)
    if packages.zlib:
        display += __row_helper("zlib:", packages.zlib)
    if packages.cassandra:
        display += __row_helper("Cassandra:", packages.cassandra)
    if packages.ycsb:
        display += __row_helper("YCSB:", packages.ycsb)
    if packages.mysql:
        display += __row_helper("MySQL:", packages.mysql)
    if packages.mysql_glibc:
        display += __row_helper("MySQL GLibC:", packages.mysql_glibc)
    if packages.docker:
        display += __row_helper("Docker:", packages.docker)
    display += seperator
    if packages.openmpi:
        display += __row_helper("OpenMPI:", packages.openmpi)
    if packages.glibc:
        display += __row_helper("GNU C Library (glibc):", packages.glibc)
    if (
        "amd" not in processor.lower()
        and "intel" not in processor.lower()
        and packages.openblas
    ):
        display += __row_helper("OpenBLAS", packages.openblas)
    if packages.maven:
        display += __row_helper("Maven:", packages.maven)
    if "intel" in processor.lower() and packages.mkl:
        display += __row_helper("Intel(R) Math Kernel Library:", packages.mkl)
    if "amd" in processor.lower() and packages.blis:
        display += __row_helper("AMD BLIS*:", packages.blis)
    if packages.jconnect:
        display += __row_helper("MySQL Connector/J:", packages.jconnect)
    if java_ver:
        display += __row_helper("Java:", java_ver)
    display += seperator
    if "amd" in processor.lower() and packages.blis:
        display += "* Copyright (C) 2017, Advanced Micro Devices, Inc.\n"
        display += "* Copyright (C) 2014, The University of Texas at Austin\n"
        display += seperator
    display += "\n"

    return display
