# -*- coding: utf-8 -*-
"""The detected memory information."""

import logging
import math
import os
import re
import shutil

from ..utilities import execute
from ..utilities import grep


def __closest_power_of_two(number):
    """Closest n^2.

    Example:
        >>> __closest_power_of_two(67)
        64
        >>> __closest_power_of_two(64)
        64

    Returns:
        Integer: Closest power of two.
    """
    try:
        return int(math.pow(2, int(math.log(number, 2) + 0.5)))
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def total():
    """The total system memory in GB.

    Examples:
        >>> total()
        64

    Returns:
        Integer: RAM in GB.
    """
    try:
        ram_gb = None
        ram_kb = None

        if shutil.which("lshw"):
            lshw_output = (
                execute.output(
                    "lshw -class memory | grep -A 9 'bank:' | awk '/size:/ "
                    "{print $2}'"
                )
                .rstrip()
                .split("\n")
            )
            # lshw is in binary prefixed notation; however, it is actually
            # usually SI prefixed. Will do binary prefixed (kibibyte KiB)
            # conversion to SI prefixed (kilobyte KB); then at the end, do
            # rounding the the nearest n^2 to handle inconsistencies.
            for dimm in lshw_output:
                if "GiB" in dimm:
                    dimm = re.sub(r"[^0-9]", "", dimm)
                    ram_gb += int(dimm)
                elif "Mib" in dimm:
                    dimm = re.sub(r"[^0-9]", "", dimm)
                    dimm = int(dimm) * 1024
                    ram_gb += __closest_power_of_two(dimm)
                elif "Kib" in dimm:
                    dimm = re.sub(r"[^0-9]", "", dimm)
                    dimm = int(dimm) * 1024 * 1024
                    ram_gb += __closest_power_of_two(dimm)

        if not ram_gb and os.path.isfile("/proc/meminfo"):
            meminfo_output = grep.file("/proc/meminfo", "MemTotal")
            ram_kb = re.sub("MemTotal:", "", meminfo_output[0])
            ram_kb = re.sub("kB", "", ram_kb)
            ram_kb = ram_kb.strip().split()[0]
            # 1024/1000 seems to work instead of either
            # a) 1000/1000
            # b) 1024/1024
            ram_gb = int(ram_kb) / 1024 / 1000

        return ram_gb
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def frequency():
    """The detected memory frequency.

    Example:
        >>> frequency()
        2666

    Returns:
        Integer: The memory frequency in MHz.
    """

    dimm_freq = None
    freq = None

    try:
        if shutil.which("dmidecode"):
            output = None
            dmidecode_output = execute.output("dmidecode -t memory")
            outputs = grep.text(dmidecode_output, r"^\s*Speed:")
            for dimm in outputs:
                if "Unknown" in dimm:
                    continue
                output = dimm
                break
            if output:
                dimm_freq = output.strip().split()[1]

        if not dimm_freq and shutil.which("lshw"):
            lshw_output = execute.output("lshw -short -C memory")
            dimms = grep.text(lshw_output, "DIMM")
            if dimms:
                dimm_freq = dimms[0].strip().split()[6]

        if "." in dimm_freq:
            freq = int(float(dimm_freq))
        elif dimm_freq and dimm_freq.isdigit():
            freq = int(dimm_freq)

        return freq
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)
