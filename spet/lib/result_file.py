# -*- coding: utf-8 -*-
"""SPET result file creation functions."""

import datetime
import logging


def header(version):
    """Header for the results file.

    Args:
        version (str): SPET version.

    Returns:
        String: Result file header.
    """
    head = "Server Performance Evaluation Tool Summary".center(79)
    head += "\n"
    head += version.center(79)
    head += "\n"
    date = str(datetime.datetime.now())
    head += date.center(79)
    head += "\n\n"
    logging.debug("head:\n%s", head)
    return head


def footer():
    """Footer for the results file.

    Returns:
        String: Result file footer.
    """
    foot = "\n\nFor questions about this result, please contact the tester.\n"
    year = str(datetime.datetime.now().year)
    foot += "Copyright %s Ryan Spoone\n" % year
    logging.debug("foot:\n%s", foot)
    return foot
