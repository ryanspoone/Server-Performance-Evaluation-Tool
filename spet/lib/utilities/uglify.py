# -*- coding: utf-8 -*-
"""System-friendly output."""

import logging
import re
import string


def filename(text):
    """Normalizes text to be used as a filename.

    Args:
        text (str): Text to be converted into a filename acceptable string.

    Example:
        >>> filename('Intel Core(TM) i7-7700 CPU')
        'intel_core_i7-7700_cpu'
        >>> filename('Intel(R) Xeon(R) Platinum 8180 CPU @ 2.50GHz')
        'intel_xeon_platinum_8180_cpu_2.50ghz'

    Returns:
        String: The filename ready text.
    """
    try:
        invalid_chars = "[^-_. {}{}]+".format(string.ascii_letters,
                                              string.digits)
        # Convert to lowercase and remove everything within parentheses
        text = re.sub(r"\([^)]*\)", "", text.lower())
        # Remove invalid characters
        text = re.sub(invalid_chars, "", text)
        # Remove double whitespace
        text = re.sub(r"\s+", " ", text)
        # Spaces to underscores
        text = re.sub(r" ", "_", text.strip())

        return text
    except IOError as err:
        logging.error(err)
