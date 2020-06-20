# -*- coding: utf-8 -*-
"""BLIS prerequisite."""

import logging
import os

from ..utilities import download
from ..utilities import extract
from ..utilities import prettify


class BLIS:
    """BLIS prerequisite.

    Args:
        version (str): Version number for BLIS
        root_dir (str): The main directory for SPET.

    Attributes:
        version (str): Version number for BLIS.
        src_dir (str): The source directory for installing packages.
        blis_dir (str): The source directory for BLIS.
    """

    def __init__(self, version, root_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.blis_dir = self.src_dir + "/blis"

    def download(self, url=None):
        """Download BLIS.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        archive_path = "{}/AMD-BLIS-Linux-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        if url is None:
            prettify.error_message(
                "Unable to find an URL for BLIS. Please visit "
                '"http://developer.amd.com/amd-cpu-libraries/blas-library/" to'
                ' download BLIS and place the archive in the "{}" directory.'.format(
                    self.src_dir
                )
            )
            return False

        logging.info("Downloading BLIS.")
        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract BLIS.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        dir_path = "{}/AMD-BLIS-Linux-{}".format(self.src_dir, self.version)
        file_path = dir_path + ".tar.gz"

        if os.path.isdir(self.blis_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract BLIS because "{}" could not be found.'.format(file_path)
            )
            return False

        logging.info("Extracting BLIS.")

        extract.tar(file_path, self.src_dir)
        extracted_name = self.src_dir + "/amd-blis-" + self.version.lower()
        os.rename(extracted_name, self.blis_dir)

        if os.path.isdir(self.blis_dir):
            return True
        return False
