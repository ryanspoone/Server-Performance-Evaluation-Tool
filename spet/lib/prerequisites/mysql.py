# -*- coding: utf-8 -*-
"""MySQL prerequisite."""

import logging
import os

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import prettify


class MySQL:
    """MySQL prerequisite.

    Args:
        mysql_ver (str): Version number for MySQL
        glibc_ver (str): Version number for MySQL glibc.
        root_dir (str): The main directory for SPET.

    Attributes:
        mysql_ver (str): Version number for MySQL.
        mysql_ver (str): Version number for MySQL glibc.
        src_dir (str): The source directory for installing packages.
        mysql_dir (str): The source directory for MySQL.
    """

    def __init__(self, mysql_ver, glibc_ver, root_dir):
        self.mysql_ver = mysql_ver
        self.glibc_ver = glibc_ver
        self.src_dir = root_dir + "/src"
        self.mysql_dir = self.src_dir + "/mysql"

    def download(self):
        """Download MySQL.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        minor_ver = ".".join(self.mysql_ver.split(".")[:2])
        archive = "mysql-{}-linux-glibc{}-x86_64.tar.gz".format(
            self.mysql_ver, self.glibc_ver)
        url = "https://dev.mysql.com/get/Downloads/MySQL-{}/{}".format(
            minor_ver, archive)
        archive_path = "{}/{}".format(self.src_dir, archive)

        if os.path.isfile(archive_path):
            return True

        logging.info("Downloading MySQL.")
        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract MySQL.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        dir_path = "{}/mysql-{}-linux-glibc{}-x86_64".format(
            self.src_dir, self.mysql_ver, self.glibc_ver)
        file_path = dir_path + ".tar.gz"

        if os.path.isdir(self.mysql_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract MySQL because "{}" could not be found.'.format(
                    file_path))
            return False

        logging.info("Extracting MySQL.")

        extract.tar(file_path, self.src_dir)
        os.rename(dir_path, self.mysql_dir)

        if os.path.isdir(self.mysql_dir):
            return True
        return False

    def setup(self):
        """Extract MySQL.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        files_dir = self.mysql_dir + "/mysql-files"

        if not os.path.isdir(self.mysql_dir):
            prettify.error_message(
                'Cannot setup MySQL because "{}" could not be found.'.format(
                    self.mysql_dir))
            return False

        if os.path.isdir(files_dir) and os.listdir(files_dir):
            return True

        os.makedirs(files_dir, exist_ok=True)
        os.chmod(files_dir, 0o750)
        execute.output(
            "./bin/mysqld --initialize-insecure --user=root --basedir={} "
            "--datadir={}".format(self.mysql_dir, files_dir),
            working_dir=self.mysql_dir,
        )
        execute.output(
            "./bin/mysql_ssl_rsa_setup --user=root --basedir={} --datadir={}".
            format(self.mysql_dir, files_dir),
            working_dir=self.mysql_dir,
        )
        return True
