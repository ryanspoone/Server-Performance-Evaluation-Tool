# -*- coding: utf-8 -*-
"""Cassandra prerequisite."""

import logging
import os

from ..utilities import download
from ..utilities import extract
from ..utilities import prettify


class Cassandra:
    """Cassandra prerequisite.

    Args:
        version (str): Version number for Cassandra.
        root_dir (str): The main directory for SPET.

    Attributes:
        version (str): Version number for Cassandra.
        src_dir (str): The source directory for installing packages.
        cassandra_dir (str): The source directory for Cassandra.
    """

    def __init__(self, version, root_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.cassandra_dir = self.src_dir + "/cassandra"

    def download(self):
        """Download Cassandra.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        archive = "apache-cassandra-{}-bin.tar.gz".format(self.version)
        url = "http://www.gtlib.gatech.edu/pub/apache/cassandra/{}/{}".format(
            self.version, archive
        )
        archive_path = "{}/{}".format(self.src_dir, archive)

        if os.path.isfile(archive_path):
            return True

        logging.info("Downloading Cassandra.")

        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract Cassandra.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        dir_path = "{}/apache-cassandra-{}".format(self.src_dir, self.version)
        file_path = dir_path + "-bin.tar.gz"

        if os.path.isdir(self.cassandra_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract Cassandra because "{}" could not be found.'.format(
                    file_path
                )
            )
            return False

        logging.info("Extracting Cassandra.")

        extract.tar(file_path, self.src_dir)
        os.rename(dir_path, self.cassandra_dir)

        if os.path.isdir(self.cassandra_dir):
            return True
        return False
