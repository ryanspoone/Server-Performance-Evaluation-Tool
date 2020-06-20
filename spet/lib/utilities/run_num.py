# -*- coding: utf-8 -*-
"""Contains miscellaneous functions to help complete common tasks."""

import logging
import os

from . import file


def write(lock_file):
    """Write the persistant Intel Test Suite run number.

    Args:
        lock_file (str): The path to the .lock file.
    """
    try:
        run_num = 1
        if os.path.isfile(lock_file):
            current_value = file.read(lock_file)
            if current_value:
                run_num = int(current_value) + 1

        file.write(lock_file, str(run_num))
    except IOError as err:
        logging.error(err)


def read(lock_file):
    """Get the current Intel Test Suite run number.

    Args:
        lock_file (str): The path to the .lock file.

    Returns:
        String: Intel Test Suite run number.
    """
    try:
        return "{:03d}".format(int(file.read(lock_file).strip()))
    except IOError as err:
        logging.error(err)
