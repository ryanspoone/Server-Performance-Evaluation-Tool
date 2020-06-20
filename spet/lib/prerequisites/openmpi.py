# -*- coding: utf-8 -*-
"""OpenMPI prerequisite."""

import logging
import os

from ..utilities import download
from ..utilities import execute
from ..utilities import extract
from ..utilities import prettify


class OpenMPI:
    """OpenMPI prerequisite.

    Args:
        version (str): Version number for OpenMPI
        root_dir (str): The main directory for SPET.

    Attributes:
        version (str): Version number for OpenMPI.
        src_dir (str): The source directory for installing packages.
        mpi_dir (str): The source directory for OpenMPI.
    """

    def __init__(self, version, root_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.mpi_dir = self.src_dir + "/openmpi"

    def download(self):
        """Download OpenMPI.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        # Remove last number from version
        short_version = ".".join(self.version.split(".")[:-1])

        url = (
            "https://www.open-mpi.org/software/ompi/v{}/downloads/" "openmpi-{}.tar.gz"
        ).format(short_version, self.version)
        archive_path = "{}/openmpi-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        logging.info("Downloading OpenMPI.")
        logging.debug("URL: %s", url)

        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract OpenMPI.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/openmpi-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isdir(self.mpi_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract OpenMPI because "{}" could not be found.'.format(
                    file_path
                )
            )
            return False

        logging.info("Extracting OpenMPI.")
        extract.tar(file_path, self.src_dir)
        os.rename("{}-{}".format(self.mpi_dir, self.version), self.mpi_dir)

        if os.path.isdir(self.mpi_dir):
            return True
        return False

    def build(self, cores=None, cflags=None):
        """Compiles OpenMPI.

        Args:
            cores (int, optional): The number of cores on the system.
            cflags (str, optional): The CFLAGS for GCC.

        Returns:
            Boolean: True if compilation was successful otherwise False.
        """
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if "-O" not in cflags:
            cflags += " -O3 "

        build_dir = self.mpi_dir + "/build"
        bin_loc = build_dir + "/bin/mpicc"
        shell_env = os.environ.copy()
        shell_env["CFLAGS"] = cflags

        if os.path.isfile(bin_loc):
            return True

        if not os.path.isdir(self.mpi_dir):
            prettify.error_message(
                'Cannot compile OpenMPI because "{}" could not be found.'.format(
                    self.mpi_dir
                )
            )
            return False

        logging.info(
            'Compiling OpenMPI using %d Make threads and "%s" CFLAGS.', cores, cflags
        )

        os.makedirs(build_dir, exist_ok=True)

        execute.output(
            "../configure --prefix=" + build_dir, build_dir, environment=shell_env
        )
        execute.output(
            "make -s -j {} all".format(cores), build_dir, environment=shell_env
        )

        return True

    def install(self, cores=None):
        """Installs OpenMPI.

        Args:
            cores (int, optional): The number of cores on the system.

        Returns:
            Boolean: True if installation was successful otherwise False.
        """
        if cores is None:
            cores = 1

        build_dir = self.mpi_dir + "/build"
        bin_loc = build_dir + "/bin/mpicc"

        if os.path.isfile(bin_loc):
            return True

        if not os.path.isdir(build_dir):
            prettify.error_message(
                'Cannot install OpenMPI because "{}" could not be found.'.format(
                    self.mpi_dir
                )
            )
            return False

        logging.info("Installing OpenMPI using %d Make threads.", cores)

        execute.output("sudo -E make -s -j {} install".format(cores), build_dir)

        if os.path.exists(bin_loc):
            return True
        return False
