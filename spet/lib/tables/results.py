# -*- coding: utf-8 -*-
"""Used for creating a human readable display for SPET results."""

import textwrap

from ..utilities import prettify


def __format_helper(title, value, unit=None):
    """Helper to format the result table.

    Args:
        title (str): The title of the value. Left aligned.
        value (any): The value to be displayed.
        unit (str, optional): The value's unit.

    Returns:
        String: Title (left aligned, 50 char) and value with unit (right
        aligned, 28 char).
    """
    if isinstance(value, float):
        value = "{:.2f}".format(value)
    if unit:
        value = "{} {}".format(value, unit)

    length_left = 78 - len(title)

    if length_left - len(value) < 1:
        return "{:30} {:>48}\n".format(title, value)
    else:
        return "{:{}} {:>{}s}\n".format(title, len(title), value, length_left)


def __variance_percentage(vrange, median):
    """Helper to compute the variance.

    Args:
        vrange (float): The range total.
        median (float): The median amount.

    Returns:
        String: The percentage of variance.
    """
    return "{:.2f}%".format(vrange / median)


def table(results):
    """A formatted table of the results for the results file.

    Args:
        results (dict): The SPET results for the table.

    Returns:
        String: Results table.
    """

    display = "\n"
    display += "System Performance Results".center(79) + "\n"
    display += "==========================".center(79) + "\n"
    display += compilation(results["Timed Kernel Compilation"], detailed=True)
    display += zlib(results["zlib"], detailed=True)
    display += lmbench(results["LMbench"])
    display += mlc(results["MLC"])
    display += openssl(results["OpenSSL"], detailed=True)
    display += stream(results["STREAM"], detailed=True)
    display += linpack(results["High-Performance Linpack"])
    display += sql(results["YCSB SQL"], detailed=True)
    display += nosql(results["YCSB NoSQL"], detailed=True)
    display += docker(results["Docker"])

    return display


def compilation(result, detailed=None):
    """An user-friendly display for compilation results.

    Args:
        results (dict): The compilation results.

    Returns:
        String: User-friendly display.
    """
    if detailed is None:
        detailed = False
    unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"
    title = "Linux Kernel Compilation"

    display = seperator
    header = (
        "Software development and compute compilation performance. "
        "Lower time is better."
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary

    if "error" in result:
        display += __format_helper(title, "INVALID")
    elif "skipped" in result:
        display += __format_helper(title, "SKIPPED")
    else:
        if "unit" in result:
            unit = str(result["unit"])
        if detailed:
            if "run1" in result:
                display += __format_helper(title + ": Run 1", result["run1"], unit=unit)
            if "run2" in result:
                display += __format_helper(title + ": Run 2", result["run2"], unit=unit)
            if "run3" in result:
                display += __format_helper(title + ": Run 3", result["run3"], unit=unit)
            if "median" in result:
                display += seperator
                display += __format_helper(
                    title + ": Median", result["median"], unit=unit
                )
        else:
            if "median" in result:
                display += __format_helper(title, result["median"], unit=unit)

    display += seperator + "\n"

    return display


def zlib(result, detailed=None):
    """An user-friendly display for zlib results.

    Args:
        results (dict): The zlib results.

    Returns:
        String: User-friendly display.
    """
    if detailed is None:
        detailed = False
    unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"

    display = seperator
    header = (
        "Compression and decompression performance for a 2 GB file "
        "using zlib. Lower time is better."
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary

    if "error" in result:
        display += __format_helper("Compression", "INVALID")
        display += __format_helper("Decompression", "INVALID")
    elif "skipped" in result:
        display += __format_helper("Compression", "SKIPPED")
        display += __format_helper("Decompression", "SKIPPED")
    else:
        if "unit" in result:
            unit = str(result["unit"])
        if detailed:
            # Compression runs
            if "run1" in result and "compress" in result["run1"]:
                display += __format_helper(
                    "Compression: Run 1", result["run1"]["compress"], unit=unit
                )
            if "run2" in result and "compress" in result["run2"]:
                display += __format_helper(
                    "Compression: Run 2", result["run2"]["compress"], unit=unit
                )
            if "run3" in result and "compress" in result["run3"]:
                display += __format_helper(
                    "Compression: Run 3", result["run3"]["compress"], unit=unit
                )
            display += seperator
            # Decompression Runs
            if "run1" in result and "decompress" in result["run1"]:
                display += __format_helper(
                    "Decompression: Run 1", result["run1"]["decompress"], unit=unit
                )
            if "run2" in result and "decompress" in result["run2"]:
                display += __format_helper(
                    "Decompression: Run 2", result["run2"]["decompress"], unit=unit
                )
            if "run3" in result and "decompress" in result["run3"]:
                display += __format_helper(
                    "Decompression: Run 3", result["run3"]["decompress"], unit=unit
                )
            display += seperator
            # Compression median
            if "median" in result and "compress" in result["median"]:
                display += __format_helper(
                    "Compression: Median", result["median"]["compress"], unit=unit
                )
            # Decompression median
            if "median" in result and "decompress" in result["median"]:
                display += __format_helper(
                    "Decompression: Median", result["median"]["decompress"], unit=unit
                )
        else:
            if "median" in result and "compress" in result["median"]:
                display += __format_helper(
                    "Compression", result["median"]["compress"], unit=unit
                )
            if "median" in result and "decompress" in result["median"]:
                display += __format_helper(
                    "Decompression", result["median"]["decompress"], unit=unit
                )

    display += seperator + "\n"

    return display


def lmbench(result):
    """An user-friendly display for LMbench results.

    Args:
        results (dict): The LMbench results.

    Returns:
        String: User-friendly display.
    """
    unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"

    display = seperator
    header = "Cache latencies using LMbench. Lower latency is better."
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary
    if "error" in result:
        display += __format_helper("L1-Cache Read Latency", "INVALID")
        display += __format_helper("L2-Cache Read Latency", "INVALID")
        display += __format_helper("L3-Cache Read Latency", "INVALID")
    elif "skipped" in result:
        display += __format_helper("L1-Cache Read Latency", "SKIPPED")
        display += __format_helper("L2-Cache Read Latency", "SKIPPED")
        display += __format_helper("L3-Cache Read Latency", "SKIPPED")
    else:
        if "unit" in result:
            unit = str(result["unit"])
        if "level1" in result:
            display += __format_helper(
                "L1-Cache Read Latency", result["level1"], unit=unit
            )
        if "level2" in result:
            display += __format_helper(
                "L2-Cache Read Latency", result["level2"], unit=unit
            )
        if "level3" in result:
            display += __format_helper(
                "L3-Cache Read Latency", result["level3"], unit=unit
            )

    display += seperator + "\n"

    return display


def mlc(result):
    """An user-friendly display for MLC results.

    Args:
        results (dict): The MLC results.

    Returns:
        String: User-friendly display.
    """
    unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"

    display = seperator
    header = (
        "Processor node-to-node memory latencies using Intel(R) "
        "Memory Latency Checker. Lower latency is better."
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary
    if "error" in result:
        display += __format_helper("Node Latency", "INVALID")
    elif "skipped" in result:
        display += __format_helper("Node Latency", "SKIPPED")
    else:
        if "unit" in result:
            unit = str(result["unit"])
        if "latencies" in result:
            for node_latency in result["latencies"]:
                node = result["latencies"].index(node_latency)
                title = "Node0-Node{} Latency".format(node)
                if result["latencies"].index(node_latency) == 0:
                    title = "Node0 Latency"
                display += __format_helper(title, node_latency, unit)

    display += seperator + "\n"

    return display


def openssl(results, detailed=None):
    """An user-friendly display for OpenSSL results.

    Args:
        results (dict): The OpenSSL results.

    Returns:
        String: User-friendly display.
    """
    if detailed is None:
        detailed = False
    unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"

    display = seperator
    header = (
        "Cryptography using OpenSSL AES-GCM 8192 bytes. " "Higher throughput is better."
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary
    count = 0
    if "error" in results:
        display += __format_helper("Encryption", "INVALID")
        display += __format_helper("Decryption", "INVALID")
    elif "skipped" in results:
        display += __format_helper("Encryption", "SKIPPED")
        display += __format_helper("Decryption", "SKIPPED")
    else:
        if detailed:
            for test, result in results.items():  # pylint: disable=W0612
                if "unit" in result:
                    unit = str(result["unit"])
                # Encryption runs
                if "run1" in result and "encrypt" in result["run1"]:
                    display += __format_helper(
                        "Encryption Throughput ({}-bit): Run 1".format(
                            result["test_bit_size"]
                        ),
                        prettify.byte_per_second(
                            result["run1"]["encrypt"], suffix=unit
                        ),
                    )
                if "run2" in result and "encrypt" in result["run2"]:
                    display += __format_helper(
                        "Encryption Throughput ({}-bit): Run 2".format(
                            result["test_bit_size"]
                        ),
                        prettify.byte_per_second(
                            result["run2"]["encrypt"], suffix=unit
                        ),
                    )
                if "run3" in result and "encrypt" in result["run3"]:
                    display += __format_helper(
                        "Encryption Throughput ({}-bit): Run 3".format(
                            result["test_bit_size"]
                        ),
                        prettify.byte_per_second(
                            result["run3"]["encrypt"], suffix=unit
                        ),
                    )
                display += seperator
                # Decryption runs
                if "run1" in result and "decrypt" in result["run1"]:
                    display += __format_helper(
                        "Decryption Throughput ({}-bit): Run 1".format(
                            result["test_bit_size"]
                        ),
                        prettify.byte_per_second(
                            result["run1"]["decrypt"], suffix=unit
                        ),
                    )
                if "run2" in result and "decrypt" in result["run2"]:
                    display += __format_helper(
                        "Decryption Throughput ({}-bit): Run 2".format(
                            result["test_bit_size"]
                        ),
                        prettify.byte_per_second(
                            result["run2"]["decrypt"], suffix=unit
                        ),
                    )
                if "run3" in result and "decrypt" in result["run3"]:
                    display += __format_helper(
                        "Decryption Throughput ({}-bit): Run 3".format(
                            result["test_bit_size"]
                        ),
                        prettify.byte_per_second(
                            result["run3"]["decrypt"], suffix=unit
                        ),
                    )
                display += seperator

        for test, result in results.items():  # pylint: disable=W0612
            if "unit" in result:
                unit = str(result["unit"])
            # Median
            if detailed and "median" in result and "encrypt" in result["median"]:
                display += __format_helper(
                    "Encryption Throughput ({}-bit): Median".format(
                        result["test_bit_size"]
                    ),
                    prettify.byte_per_second(result["median"]["encrypt"], suffix=unit),
                )
            elif not detailed and "median" in result and "encrypt" in result["median"]:
                display += __format_helper(
                    "Encryption Throughput ({}-bit)".format(result["test_bit_size"]),
                    prettify.byte_per_second(result["median"]["encrypt"], suffix=unit),
                )
            if detailed and "median" in result and "decrypt" in result["median"]:
                display += __format_helper(
                    "Decryption Throughput ({}-bit): Median".format(
                        result["test_bit_size"]
                    ),
                    prettify.byte_per_second(result["median"]["decrypt"], suffix=unit),
                )
            elif not detailed and "median" in result and "decrypt" in result["median"]:
                display += __format_helper(
                    "Decryption Throughput ({}-bit)".format(result["test_bit_size"]),
                    prettify.byte_per_second(result["median"]["decrypt"], suffix=unit),
                )
        count += 1
    display += seperator + "\n"

    return display


def stream(result, detailed=None):
    """An user-friendly display for STREAM results.

    Args:
        results (dict): The STREAM results.

    Returns:
        String: User-friendly display.
    """
    if detailed is None:
        detailed = False
    unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"
    title = "Triad Bandwidth"

    display = seperator
    header = (
        "Memory bandwidth using STREAM and OpenMPI. " "Higher throughput is better."
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary

    if "error" in result:
        display += __format_helper(title, "INVALID")
    elif "skipped" in result:
        display += __format_helper(title, "SKIPPED")
    else:
        if "unit" in result:
            unit = str(result["unit"])
        if detailed:
            # Runs
            if "run1" in result:
                display += __format_helper(
                    title + ": Run 1",
                    prettify.byte_per_second(result["run1"], suffix=unit),
                )
            if "run2" in result:
                display += __format_helper(
                    title + ": Run 2",
                    prettify.byte_per_second(result["run2"], suffix=unit),
                )
            if "run3" in result:
                display += __format_helper(
                    title + ": Run 3",
                    prettify.byte_per_second(result["run3"], suffix=unit),
                )
            display += seperator
            # Median
            if "median" in result:
                display += __format_helper(
                    title + ": Median",
                    prettify.byte_per_second(result["median"], suffix=unit),
                )
        else:
            if "median" in result:
                display += __format_helper(
                    title, prettify.byte_per_second(result["median"], suffix=unit)
                )

    display += seperator + "\n"

    return display


def linpack(result):
    """An user-friendly display for LINPACK results.

    Args:
        results (dict): The LINPACK results.

    Returns:
        String: User-friendly display.
    """
    unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"
    title = "Operations Per Second"
    mathlib = ""

    if "mathlib" in result and result["mathlib"] == "mkl":
        mathlib = " Intel(R) MKL,"
    elif "mathlib" in result and result["mathlib"] == "blis":
        mathlib = " AMD BLIS*,"
    elif "mathlib" in result and result["mathlib"] == "openblas":
        mathlib = " OpenBLAS,"

    display = seperator
    header = (
        "Floating-point and math computing performance using "
        "High-Performance Linpack,{} and OpenMPI. "
        "Higher FLOPS is better.".format(mathlib)
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    if "mathlib" in result and result["mathlib"] is "blis":
        display += seperator
        display += "* Copyright (C) 2017, Advanced Micro Devices, Inc.\n"
        display += "* Copyright (C) 2014, The University of Texas at Austin\n"
    display += boundary

    if "error" in result:
        display += __format_helper(title, "INVALID")
    elif "skipped" in result:
        display += __format_helper(title, "SKIPPED")
    else:
        if "unit" in result:
            unit = str(result["unit"])
        if "score" in result:
            display += __format_helper(
                title, prettify.flops(result["score"], suffix=unit)
            )

    display += seperator + "\n"

    return display


def sql(result, detailed=None):
    """An user-friendly display for SQL results.

    Args:
        results (dict): The SQL results.

    Returns:
        String: User-friendly display.
    """
    if detailed is None:
        detailed = False
    lat_unit = None
    tp_unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"

    display = seperator
    header = (
        "SQL database computing performance using YCSB and MySQL. "
        "Higher throughput is better. Lower latency is better."
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary

    if "error" in result:
        display += __format_helper("Throughput", "INVALID")
        display += __format_helper("95th Percentile Read Latency", "INVALID")
        display += __format_helper("95th Percentile Update Latency", "INVALID")
    elif "skipped" in result:
        display += __format_helper("Throughput", "SKIPPED")
        display += __format_helper("95th Percentile Read Latency", "SKIPPED")
        display += __format_helper("95th Percentile Update Latency", "SKIPPED")
    else:
        if "unit" in result and "throughput" in result["unit"]:
            tp_unit = result["unit"]["throughput"]
        if "unit" in result and "latency" in result["unit"]:
            lat_unit = result["unit"]["latency"]

        if detailed:
            # Run 1
            if "run1" in result and "throughput" in result["run1"]:
                display += __format_helper(
                    "Throughput: Run 1", result["run1"]["throughput"], unit=tp_unit
                )
            if "run1" in result and "read_latency" in result["run1"]:
                display += __format_helper(
                    "95th Percentile Read Latency: Run 1",
                    prettify.small_time(
                        result["run1"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "run1" in result and "update_latency" in result["run1"]:
                display += __format_helper(
                    "95th Percentile Update Latency: Run 1",
                    prettify.small_time(
                        result["run1"]["update_latency"], suffix=lat_unit
                    ),
                )
            display += seperator
            # Run 2
            if "run2" in result and "throughput" in result["run2"]:
                display += __format_helper(
                    "Throughput: Run 2", result["run2"]["throughput"], unit=tp_unit
                )
            if "run2" in result and "read_latency" in result["run2"]:
                display += __format_helper(
                    "95th Percentile Read Latency: Run 2",
                    prettify.small_time(
                        result["run2"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "run2" in result and "update_latency" in result["run2"]:
                display += __format_helper(
                    "95th Percentile Update Latency: Run 2",
                    prettify.small_time(
                        result["run2"]["update_latency"], suffix=lat_unit
                    ),
                )
            display += seperator
            # Run 3
            if "run3" in result and "throughput" in result["run3"]:
                display += __format_helper(
                    "Throughput: Run 3", result["run3"]["throughput"], unit=tp_unit
                )
            if "run3" in result and "read_latency" in result["run3"]:
                display += __format_helper(
                    "95th Percentile Read Latency: Run 3",
                    prettify.small_time(
                        result["run3"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "run3" in result and "update_latency" in result["run3"]:
                display += __format_helper(
                    "95th Percentile Update Latency: Run 3",
                    prettify.small_time(
                        result["run3"]["update_latency"], suffix=lat_unit
                    ),
                )
            display += seperator
            # Medians
            if "median" in result and "throughput" in result["median"]:
                display += __format_helper(
                    "Throughput: Median", result["median"]["throughput"], unit=tp_unit
                )
            if "median" in result and "read_latency" in result["median"]:
                display += __format_helper(
                    "95th Percentile Read Latency: Median",
                    prettify.small_time(
                        result["median"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "median" in result and "update_latency" in result["median"]:
                display += __format_helper(
                    "95th Percentile Update Latency: Median",
                    prettify.small_time(
                        result["median"]["update_latency"], suffix=lat_unit
                    ),
                )
        else:
            if "median" in result and "throughput" in result["median"]:
                display += __format_helper(
                    "Throughput", int(result["median"]["throughput"]), unit=tp_unit
                )
            if "median" in result and "read_latency" in result["median"]:
                display += __format_helper(
                    "95th Percentile Read Latency",
                    prettify.small_time(
                        result["median"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "median" in result and "update_latency" in result["median"]:
                display += __format_helper(
                    "95th Percentile Update Latency",
                    prettify.small_time(
                        result["median"]["update_latency"], suffix=lat_unit
                    ),
                )
        # Variance
        if (
            "median" in result
            and "throughput" in result["median"]
            and "range" in result
            and "throughput" in result["range"]
        ):
            display += __format_helper(
                "Thoughput Variance",
                __variance_percentage(
                    result["range"]["throughput"], result["median"]["throughput"]
                ),
            )

    display += seperator + "\n"

    return display


def nosql(result, detailed=None):
    """An user-friendly display for NoSQL results.

    Args:
        results (dict): The NoSQL results.

    Returns:
        String: User-friendly display.
    """
    if detailed is None:
        detailed = False
    lat_unit = None
    tp_unit = None
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"

    display = seperator
    header = (
        "NoSQL database computing performance using YCSB and Cassandra. "
        "Higher throughput is better. Lower latency is better."
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary

    if "error" in result:
        display += __format_helper("Throughput", "INVALID")
        display += __format_helper("95th Percentile Read Latency", "INVALID")
        display += __format_helper("95th Percentile Update Latency", "INVALID")
    elif "skipped" in result:
        display += __format_helper("Throughput", "SKIPPED")
        display += __format_helper("95th Percentile Read Latency", "SKIPPED")
        display += __format_helper("95th Percentile Update Latency", "SKIPPED")
    else:
        if "unit" in result and "throughput" in result["unit"]:
            tp_unit = result["unit"]["throughput"]
        if "unit" in result and "latency" in result["unit"]:
            lat_unit = result["unit"]["latency"]

        if detailed:
            # Run 1
            if "run1" in result and "throughput" in result["run1"]:
                display += __format_helper(
                    "Throughput: Run 1", result["run1"]["throughput"], unit=tp_unit
                )
            if "run1" in result and "read_latency" in result["run1"]:
                display += __format_helper(
                    "95th Percentile Read Latency: Run 1",
                    prettify.small_time(
                        result["run1"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "run1" in result and "update_latency" in result["run1"]:
                display += __format_helper(
                    "95th Percentile Update Latency: Run 1",
                    prettify.small_time(
                        result["run1"]["update_latency"], suffix=lat_unit
                    ),
                )
            display += seperator
            # Run 2
            if "run2" in result and "throughput" in result["run2"]:
                display += __format_helper(
                    "Throughput: Run 2", result["run2"]["throughput"], unit=tp_unit
                )
            if "run2" in result and "read_latency" in result["run2"]:
                display += __format_helper(
                    "95th Percentile Read Latency: Run 2",
                    prettify.small_time(
                        result["run2"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "run2" in result and "update_latency" in result["run2"]:
                display += __format_helper(
                    "95th Percentile Update Latency: Run 2",
                    prettify.small_time(
                        result["run2"]["update_latency"], suffix=lat_unit
                    ),
                )
            display += seperator
            # Run 3
            if "run3" in result and "throughput" in result["run3"]:
                display += __format_helper(
                    "Throughput: Run 3", result["run3"]["throughput"], unit=tp_unit
                )
            if "run3" in result and "read_latency" in result["run3"]:
                display += __format_helper(
                    "95th Percentile Read Latency: Run 3",
                    prettify.small_time(
                        result["run3"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "run3" in result and "update_latency" in result["run3"]:
                display += __format_helper(
                    "95th Percentile Update Latency: Run 3",
                    prettify.small_time(
                        result["run3"]["update_latency"], suffix=lat_unit
                    ),
                )
            display += seperator
            # Medians
            if "median" in result and "throughput" in result["median"]:
                display += __format_helper(
                    "Throughput: Median", result["median"]["throughput"], unit=tp_unit
                )
            if "median" in result and "read_latency" in result["median"]:
                display += __format_helper(
                    "95th Percentile Read Latency: Median",
                    prettify.small_time(
                        result["median"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "median" in result and "update_latency" in result["median"]:
                display += __format_helper(
                    "95th Percentile Update Latency: Median",
                    prettify.small_time(
                        result["median"]["update_latency"], suffix=lat_unit
                    ),
                )
        else:
            if "median" in result and "throughput" in result["median"]:
                display += __format_helper(
                    "Throughput", int(result["median"]["throughput"]), unit=tp_unit
                )
            if "median" in result and "read_latency" in result["median"]:
                display += __format_helper(
                    "95th Percentile Read Latency",
                    prettify.small_time(
                        result["median"]["read_latency"], suffix=lat_unit
                    ),
                )
            if "median" in result and "update_latency" in result["median"]:
                display += __format_helper(
                    "95th Percentile Update Latency",
                    prettify.small_time(
                        result["median"]["update_latency"], suffix=lat_unit
                    ),
                )
        # Variance
        if (
            "median" in result
            and "throughput" in result["median"]
            and "range" in result
            and "throughput" in result["range"]
        ):
            display += __format_helper(
                "Thoughput Variance",
                __variance_percentage(
                    result["range"]["throughput"], result["median"]["throughput"]
                ),
            )

    display += seperator + "\n"

    return display


def docker(result):
    """An user-friendly display for Docker results.

    Args:
        results (dict): The Docker results.

    Returns:
        String: User-friendly display.
    """
    boundary = "=" * 79 + "\n"
    seperator = "-" * 79 + "\n"
    unit = None
    title = "Linux Kernel Compilation: Average"

    display = seperator
    header = (
        "Compilation performance with up to 100 containers using Docker."
        " More containers and lower time is better."
    )
    display += (
        textwrap.fill(header, width=79, break_long_words=False, break_on_hyphens=False)
        + "\n"
    )
    display += boundary

    if "error" in result:
        display += __format_helper(title, "INVALID")
    elif "skipped" in result:
        display += __format_helper(title, "SKIPPED")
    else:
        if "unit" in result:
            unit = str(result["unit"])
        if "average" in result and "times" in result:
            container_count = len(result["times"])
            value = "{} Containers @ {:.2f}".format(container_count, result["average"])
            display += __format_helper(title, value, unit=unit)

    display += seperator + "\n"

    return display
