# -*- coding: utf-8 -*-
"""Maven prerequisite."""

import logging
import os

from spet.lib.utilities import download
from spet.lib.utilities import extract
from spet.lib.utilities import prettify


class Maven:
    """Maven prerequisite.

    Args:
        version (str): Version number for Maven
        root_dir (str): The main directory for SPET.

    Attributes:
        version (str): Version number for Maven.
        src_dir (str): The source directory for installing packages.
        maven_dir (str): The source directory for Maven.
    """

    def __init__(self, version, root_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.maven_dir = self.src_dir + "/maven"

    def download(self):
        """Download Maven.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        major_ver = self.version.split(".")[0]
        archive = "apache-maven-{}-bin.tar.gz".format(self.version)
        url = (
            "http://apache.mirrors.lucidnetworks.net/maven/maven-{}/{}/"
            "binaries/{}".format(major_ver, self.version, archive)
        )
        archive_path = "{}/{}".format(self.src_dir, archive)

        if os.path.isfile(archive_path):
            return True

        logging.info("Downloading Maven.")

        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract Maven.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        dir_path = "{}/apache-maven-{}".format(self.src_dir, self.version)
        file_path = dir_path + "-bin.tar.gz"

        if os.path.isdir(self.maven_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract Maven because "{}" could not be found.'.format(
                    file_path
                )
            )
            return False

        logging.info("Extracting Maven.")

        extract.tar(file_path, self.src_dir)
        os.rename(dir_path, self.maven_dir)

        if os.path.isdir(self.maven_dir):
            return True
        return False
