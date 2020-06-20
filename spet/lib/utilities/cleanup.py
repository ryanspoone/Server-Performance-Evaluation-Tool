# -*- coding: utf-8 -*-
"""Contains functions for cleaning up files."""

import logging
import os
import re
import shutil
import tempfile


def remove_color_codes(file_path):
    """Removes all ANSI escape sequences from a file.

    Args:
        file_path (str): The file to clean.
    """
    try:
        ansi_escape = re.compile(r"\x1b[^m]*m")

        logging.debug("Create temp file.")
        file_descr, abs_path = tempfile.mkstemp()

        with os.fdopen(file_descr, "w") as new_file:
            with open(file_path) as old_file:
                for line in old_file:
                    new_file.write(ansi_escape.sub("", line))

        logging.debug("Remove original file.")
        os.remove(file_path)

        logging.debug("Move new file.")
        shutil.move(abs_path, file_path)
    except IOError as err:
        logging.error(err)
