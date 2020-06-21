# -*- coding: utf-8 -*-
"""The detected operating system information."""

import logging
import os
import re
import shutil

from spet.lib.utilities import execute
from spet.lib.utilities import file
from spet.lib.utilities import grep


def distribution():
    """The detected operating system distribution information.

    Example:
        >>> distribution()
        ('Ubuntu', '17.04')

    Returns:
        A tuple of (distribution_name, distribution_version).

            distribution_name (str): The operating system name.
            distribution_version (str): The operating system version.
    """
    try:
        if os.path.isfile("/etc/os-release"):
            distribution_name = execute.output(
                r'. /etc/os-release && echo "${NAME}"')
            distribution_version = execute.output(
                r'. /etc/os-release && echo "${VERSION}"')
        elif os.path.isfile("/etc/lsb-release"):
            distribution_name = execute.output(
                r'. /etc/lsb-release && echo "${DISTRIB_ID}"')
            distribution_version = execute.output(
                r'. /etc/lsb-release && echo "${DISTRIB_RELEASE}"')
        elif os.path.isfile("/etc/debian_version"):
            distribution_name = "Debian"
            distribution_version = file.read("/etc/debian_version")
        elif os.path.isfile("/etc/redhat-release"):
            distribution_name = "Redhat"
            distribution_version = file.read("/etc/redhat-release")
        else:
            distribution_name = os.uname().sysname  # pylint: disable=E1101
            distribution_version = os.uname().release  # pylint: disable=E1101
        return distribution_name.strip(), distribution_version.strip()
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def architecture():
    """The system architecture.

    Example:
        >>> architecture()
        (64, 'x86_64')

    Returns:
        A tuple of (bits, type).

            bits (int): The architecture bit version (32 or 64).
            type (str): The machine type.
    """
    try:
        first_pattern = r"architecture:\s*"
        second_pattern = r"/x86_"
        third_pattern = r"i[3-6]86"
        machine_type = os.uname().machine  # pylint: disable=E1101

        if shutil.which("lscpu"):
            lscpu_output = execute.output("lscpu")
            arch = grep.text(lscpu_output, "Architecture:")
            arch = re.sub(first_pattern, "", arch[0])
            arch = re.sub(second_pattern, "", arch)
            arch = re.sub(third_pattern, "32", arch)

        if not arch:
            arch = machine_type
            arch = re.sub(second_pattern, "", arch)
            arch = re.sub(third_pattern, "32", arch)

        arch = arch.lower()

        if "arm" in arch:
            arm_ver = re.sub("armv", "", arch)

            if int(arm_ver) >= 8:
                arch = 64
            else:
                arch = 32

        if "64" in arch:
            arch = 64

        return int(arch), machine_type
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)
