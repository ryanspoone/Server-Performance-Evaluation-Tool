# -*- coding: utf-8 -*-
"""The detected GNU Compiler information."""

import logging
import re

from spet.lib.system import processor
from spet.lib.utilities import execute
from spet.lib.utilities import grep


def version():
    """The default GCC version.

    Example:
        >>> version()
        '6.2.0'

    Returns:
        String: The detected version or the string "Unknown".
    """
    try:
        gcc_ver = execute.output("gcc --version")
        gcc_ver = gcc_ver.rstrip().split("\n")[0]

        if gcc_ver:
            pattern = r"gcc\s\(.*\)\s([.0-9]+).*"
            sub = r"\1"
            gcc_ver = re.sub(pattern, sub, gcc_ver)
            return gcc_ver

        return "Unknown"
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def flags():
    """The detected `-march=|-mcpu=` and `-mtune=` flags for GCC.

    Example:
        >>> flags()
        '-march=native -march=native'

    Returns:
        A string of march and mtune.

            march (str): The complete flag for `-march=` or `-mcpu=`.
            mtune (str): The complete flag for `-mtune=`.
    """
    try:
        march_mcpu = "march"
        cpu_name = processor.name().lower()

        if "power" in cpu_name or "ppc" in cpu_name:
            march_mcpu = "mcpu"

        march_output = execute.output(
            "gcc -{}=native -Q --help=target".format(march_mcpu)
        )
        march_flag = grep.text(march_output, "-{}=".format(march_mcpu))
        march_flag = march_flag[0].rstrip().split()[1].strip()

        if "native" in march_flag or not march_flag:
            march_flag = "native"

        mtune_output = execute.output(
            "gcc -{}={}  -mtune=native -Q --help=target".format(march_mcpu, march_flag)
        )
        mtune_flag = grep.text(mtune_output, "-mtune=")
        mtune_flag = mtune_flag[0].rstrip().split()[1].strip()

        if "native" in mtune_flag or not mtune_flag:
            mtune_flag = "native"

        march = "-{}={}".format(march_mcpu, march_flag)
        mtune = "-mtune=" + mtune_flag

        return march + " " + mtune
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)
