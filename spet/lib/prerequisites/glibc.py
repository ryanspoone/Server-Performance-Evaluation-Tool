# -*- coding: utf-8 -*-
"""Glibc prerequisite."""

import logging
import os

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import prettify


class GLibC:
    """Glibc prerequisite.

    Args:
        version (str): Version number for glibc
        root_dir (str): The main directory for SPET.

    Attributes:
        version (str): Version number for glibc.
        src_dir (str): The source directory for installing packages.
        glibc_dir (str): The source directory for glibc.
    """

    def __init__(self, version, root_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.glibc_dir = self.src_dir + "/glibc"

    def download(self):
        """Download glibc.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        url = "https://ftp.gnu.org/gnu/glibc/glibc-{}.tar.gz".format(self.version)
        archive_path = "{}/glibc-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        logging.info("Downloading glibc.")

        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract glibc.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/glibc-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isdir(self.glibc_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract glibc because "{}" could not be found.'.format(
                    file_path
                )
            )
            return False

        logging.info("Extracting glibc.")

        extract.tar(file_path, self.src_dir)
        os.rename("{}-{}".format(self.glibc_dir, self.version), self.glibc_dir)

        if os.path.isdir(self.glibc_dir):
            return True
        return False

    def build(self, cores=None, cflags=None):
        """Compiles glibc.

        Args:
            cores (int, optional): The number of cores on the system.
            cflags (str, optional): The CFLAGS for GCC.

        Returns:
            Boolean: True if compilation was successful otherwise False.
        """
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = ""
        # `-ffast-math` cannot be used to compile glibc
        if "-Ofast" in cflags:
            cflags = cflags.replace("-Ofast", "")
        if "-ffast-math" in cflags:
            cflags = cflags.replace("-ffast-math", "")
        # `-O3` fails sometimes
        if "-O3" in cflags:
            cflags = cflags.replace("-O3", "")
        # Optimizations are needed for glibc
        if "-O" not in cflags:
            cflags += " -O2 "

        shell_env = os.environ.copy()
        shell_env["CFLAGS"] = cflags
        build_dir = self.glibc_dir + "/build"
        bin_loc = build_dir + "/libc.so"

        if os.path.isfile(bin_loc):
            return True

        if not os.path.isdir(self.glibc_dir):
            prettify.error_message(
                'Cannot compile glibc because "{}" could not be found.'.format(
                    self.glibc_dir
                )
            )
            return False

        logging.info(
            'Compiling glibc using %d Make threads and "%s" CFLAGS', cores, cflags
        )

        os.makedirs(build_dir, exist_ok=True)

        execute.output(
            "spet.lib./configure --prefix=/usr/local/glibc",
            build_dir,
            environment=shell_env,
        )
        execute.output("make -j " + str(cores), build_dir, environment=shell_env)

        if os.path.isfile(bin_loc):
            return True
        return False

    def install(self, cores=None):
        """Installs glibc.

        Args:
            cores (int, optional): The number of cores on the system.

        Returns:
            Boolean: True if installation was successful otherwise False.
        """
        if cores is None:
            cores = 1

        bin_loc = "/usr/local/glibc/lib/ld-{}.so".format(self.version)
        build_dir = self.glibc_dir + "/build"

        if os.path.isfile(bin_loc):
            return True

        if not os.path.isdir(build_dir):
            prettify.error_message(
                'Cannot install glibc because "{}" could not be found.'.format(
                    build_dir
                )
            )
            return False

        logging.info("Installing glibc using %d Make threads.", cores)

        execute.output("sudo -E make -j {} install".format(cores), build_dir)

        if os.path.isfile(bin_loc):
            return True
        return False
