# -*- coding: utf-8 -*-
"""MKL prerequisite."""

import logging
import os

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import prettify


class MKL:
    """MKL prerequisite.

    Args:
        version (str): Version number for MKL
        root_dir (str): The main directory for SPET.

    Attributes:
        version (str): Version number for MKL.
        src_dir (str): The source directory for installing packages.
        mkl_dir (str): The source directory for MKL.
    """

    def __init__(self, version, root_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.mkl_dir = self.src_dir + "/mkl"

    def download(self, url=None):
        """Download MKL.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        archive_path = "{}/l_mkl_{}.tgz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        if url is None:
            prettify.error_message(
                "Unable to find an URL for MKL. Please visit "
                "https://software.intel.com/en-us/mkl to download MKL and "
                "place the archive in the {} directory.".format(self.src_dir)
            )
            return False

        logging.info("Downloading MKL.")
        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract MKL.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        dir_path = "{}/l_mkl_{}".format(self.src_dir, self.version)
        file_path = dir_path + ".tgz"

        if os.path.isdir(self.mkl_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract MKL because "{}" could not be found.'.format(file_path)
            )
            return False

        logging.info("Extracting MKL.")

        extract.tar(file_path, self.src_dir)
        os.rename(dir_path, self.mkl_dir)

        if os.path.isdir(self.mkl_dir):
            return True
        return False

    def install(self):
        """Install MKL.

        Returns:
            Boolean: True if installation was successful otherwise False.
        """

        if os.path.isdir("/opt/intel/mkl"):
            return True

        if not os.path.isdir(self.mkl_dir):
            prettify.error_message(
                'Cannot install MKL because "{}" could not be found.'.format(
                    self.mkl_dir
                )
            )
            return False

        logging.info("Installing MKL.")

        execute.output(
            '{}/install.sh --silent "{}/provided/silent.cfg"'.format(
                self.mkl_dir, self.src_dir
            )
        )

        if os.path.isdir(self.mkl_dir):
            return True
        return False
