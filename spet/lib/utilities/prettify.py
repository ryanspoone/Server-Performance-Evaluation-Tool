# -*- coding: utf-8 -*-
"""User-friendly output."""

import logging
import textwrap


def error_message(text):
    """Print out texted wrapped version of the inputted message.

    Args:
        text (str): Error message.

    Returns:
        String: Text-wrapped, color-coded error message.
    """
    try:
        print(
            textwrap.fill(
                u"\u001b[31mError\u001b[0m: %s" % text,
                80,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    except IOError as err:
        logging.error(err)


def byte_size(nbytes, suffix="B"):
    """Human readable byte sizes.

    Args:
        nbytes (float): The number of bytes.
        suffix (str, optional): The suffix of bytes in inputted number.

    Returns:
        String: The best readable byte size.
    """
    try:
        suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
        index = 0

        if suffixes.index(suffix) >= 0:
            value = nbytes * (1024.0 ** suffixes.index(suffix))
        else:
            value = nbytes

        while value >= 1024.0 and index < len(suffixes) - 1:
            value /= 1024.0
            index += 1
        temp = "{:.2f}".format(value).rstrip("0").rstrip(".")
        return "{} {}".format(temp, suffixes[index])
    except IOError as err:
        logging.error(err)


def byte_per_second(nbytes, suffix="B/s"):
    """Human readable bytes per second sizes.

    Args:
        nbytes (float): The number of bytes per second.
        suffix (str, optional): The suffix of bytes per second in inputted
            number.

    Returns:
        String: The best readable byte per second size.
    """
    try:
        suffixes = ["B/s", "KB/s", "MB/s", "GB/s", "TB/s", "PB/s"]
        index = 0

        if suffixes.index(suffix) >= 0:
            value = nbytes * (1024.0 ** suffixes.index(suffix))
        else:
            value = nbytes

        while value >= 1024.0 and index < len(suffixes) - 1:
            value /= 1024.0
            index += 1
        temp = "{:.2f}".format(value).rstrip("0").rstrip(".")
        return "{} {}".format(temp, suffixes[index])
    except IOError as err:
        logging.error(err)


def time_elapsed(time, suffix="s"):
    """Human readable time elapsed.

    Args:
        time (float): The time elapsed.
        suffix (str, optional): The suffix of time in inputted number.

    Returns:
        String: The best readable time elapsed.
    """
    try:
        suffixes = ["s", "min", "h"]
        index = 0

        if suffixes.index(suffix) >= 0:
            value = time * (60.0 ** suffixes.index(suffix))
        else:
            value = time

        while value >= 60.0 and index < len(suffixes) - 1:
            value /= 60.0
            index += 1
        temp = "{:.2f}".format(value).rstrip("0").rstrip(".")
        return "{} {}".format(temp, suffixes[index])
    except IOError as err:
        logging.error(err)


def small_time(time, suffix="us"):
    """Human readable sub-second time.

    Args:
        time (float): The time elapsed.
        suffix (str, optional): The suffix of time in inputted number.

    Returns:
        String: The best readable time elapsed.
    """
    try:
        suffixes = ["us", "ms"]
        index = 0

        if suffixes.index(suffix) >= 0:
            value = time * (1000.0 ** suffixes.index(suffix))
        else:
            value = time

        while value >= 1000.0 and index < len(suffixes) - 1:
            value /= 1000.0
            index += 1
        temp = "{:.2f}".format(value).rstrip("0").rstrip(".")
        return "{} {}".format(temp, suffixes[index])
    except IOError as err:
        logging.error(err)


def flops(nflops, suffix="FLOPS"):
    """Human readable flops.

    Args:
        nflops (float): The number of flops.
        suffix (str, optional): The suffix of flops in inputted number.

    Returns:
        String: The best readable FLOPS.
    """
    try:
        suffixes = ["FLOPS", "KFLOPS", "MFLOPS", "GFLOPS", "TFLOPS", "PFLOPS"]
        index = 0

        if suffixes.index(suffix) >= 0:
            value = nflops * (1000.0 ** suffixes.index(suffix))
        else:
            value = nflops

        while value >= 1000.0 and index < len(suffixes) - 1:
            value /= 1000.0
            index += 1
        temp = "{:.2f}".format(value).rstrip("0").rstrip(".")
        return "{} {}".format(temp, suffixes[index])
    except IOError as err:
        logging.error(err)


def numbers(num):
    """Human readable numbers.

    Args:
        num (float): The number.

    Returns:
        String: The best readable number.
    """
    try:
        suffixes = ["", "Thousand", "Million", "Billion", "Trillion"]
        index = 0
        value = num

        while value >= 1000.0 and index < len(suffixes) - 1:
            value /= 1000.0
            index += 1
        temp = "{:.2f}".format(value).rstrip("0").rstrip(".")
        return "{} {}".format(temp, suffixes[index]).strip()
    except IOError as err:
        logging.error(err)


def exponential(number):
    """Number to scientific notation.

    Args:
        number (float): The number.

    Returns:
        String: The number in scientific notation.
    """
    try:
        return "{:.2E}".format(number)
    except IOError as err:
        logging.error(err)
