# -*- coding: utf-8 -*-
"""Contains miscellaneous functions to with common file tasks."""

import logging
import os
import re


def read(file_path):
    """Reads contents of the file.

    Args:
        file_path (str): File to read.

    Returns:
        String: File contents.
    """
    try:
        file = open(file_path)
        content = file.read()
        logging.debug("File contents: %s", str(content))
        file.close()
        return content
    except IOError as err:
        logging.error(err)


def touch(file_path):
    """Creates empty file.

    Args:
        file_path (str): File to create.
    """
    try:
        basedir = os.path.dirname(file_path)
        # Create directory tree if necessary
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        # Create an empty file
        with open(file_path, "a"):
            os.utime(file_path, None)
    except IOError as err:
        logging.error(err)


def write(file_path, text, append=False):
    """Write text to file.

    Args:
        file_path (str): File to write.
        text (str): Text to write to file.
        append (bool, optional): Whether to append the text to the file or not.
    """
    try:
        write_type = "w"
        if append:
            write_type = "a"
        file = open(file_path, write_type)
        file.write(text)
        file.close()
    except IOError as err:
        logging.error(err)


def replace_line(file_path, pattern, subst):
    """Replace line in file.

    Args:
        file_path (str): The file to modify.
        pattern (str): Pattern in line to search for.
        subst (str): What to substitute the pattern with.
    """
    try:
        with open(file_path, "r") as sources:
            lines = sources.readlines()
        with open(file_path, "w") as sources:
            for line in lines:
                sources.write(re.sub(pattern, subst, line))
    except IOError as err:
        logging.error(err)
