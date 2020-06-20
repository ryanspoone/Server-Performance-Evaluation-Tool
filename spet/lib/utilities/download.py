# -*- coding: utf-8 -*-
"""Contains wrapper functions for downloading items."""

import logging
import shutil
import urllib.request


def file(url, dest):
    """Download file.

    Args:
        url (str): URL where the file is located.
        dest (str): Where to download the file to on this system.
    """
    agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": agent})
        with urllib.request.urlopen(request) as resp, open(dest, "wb") as out:
            shutil.copyfileobj(resp, out)
    except IOError as err:
        logging.debug(err)
