# -*- coding: utf-8 -*-
"""JSON functions."""

import json
import logging

from . import file


def write(file_path, json_data):
    """Writes JSON to file.

    Args:
        file_path (str): JSON file to write to.
        json_data (json): JSON data to write.
    """
    try:
        file.write(file_path, json.dumps(json_data, sort_keys=True, indent=4))
    except IOError as err:
        logging.error(err)


def read(data):
    """Reads pretty JSON from dict.

    Args:
        data (dict): JSON data to read from.

    Returns:
        String: Prettified JSON data.
    """
    try:
        return json.dumps(data, sort_keys=True, indent=4)
    except IOError as err:
        logging.error(err)
