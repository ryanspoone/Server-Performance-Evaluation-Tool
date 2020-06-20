# -*- coding: utf-8 -*-
"""The detected Java information."""

import logging
import re

from ..utilities import execute


def version():
    """The default Java version.

    Example:
        >>> version()
        '1.8.0_151'

    Returns:
        String: The detected version or the string "Unknown".
    """
    try:
        java_ver = execute.output("java -version")
        java_ver = java_ver.rstrip().split("\n")[0]

        if java_ver:
            pattern = r"(\w+?)\sversion\s\"(.+?)\""
            sub = r"\1-\2"
            java_ver = re.sub(pattern, sub, java_ver)
            return java_ver

        return "Unknown"
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)
