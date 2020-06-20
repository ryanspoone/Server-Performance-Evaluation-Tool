# -*- coding: utf-8 -*-
"""Contains functions dealing with access and permissions."""

import logging
import os
import stat


def is_root():
    """If SPET has root access or not.

    Example:
        >>> is_root()
        True

    Returns:
        Boolean: If root access or not.
    """
    try:
        return os.getuid() == 0  # pylint: disable=I0011,E1101
    except IOError as err:
        logging.error(err)


def make_executable(bin_loc):
    """Make file executable. Equivalent to `chmod +x bin_loc`.

    Args:
        bin_loc (str): The binary to make executable.
    """
    try:
        if os.access(bin_loc, os.X_OK):
            return
        if not os.path.isfile(bin_loc):
            raise FileNotFoundError
        status = os.stat(bin_loc)
        os.chmod(bin_loc, status.st_mode | stat.S_IEXEC)
        logging.debug("%s access: %s", bin_loc, os.access(bin_loc, os.X_OK))
    except IOError as err:
        logging.error(err)
