# -*- coding: utf-8 -*-
"""OpenBLAS prerequisite."""

import logging
import os

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import prettify


class OpenBLAS:
    """OpenBLAS prerequisite.

    Args:
        version (str): Version number for OpenBLAS
        root_dir (str): The main directory for SPET.

    Attributes:
        version (str): Version number for OpenBLAS.
        src_dir (str): The source directory for installing packages.
        openblas_dir (str): The source directory for OpenBLAS.
    """

    def __init__(self, version, root_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.openblas_dir = self.src_dir + "/openblas"

    def download(self):
        """Download OpenBLAS.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        url = "http://github.com/xianyi/OpenBLAS/archive/v{}.tar.gz".format(
            self.version
        )
        archive_path = "{}/openblas-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        logging.info("Downloading OpenBLAS.")
        logging.debug("URL: %s", url)

        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract OpenBLAS.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/openblas-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isdir(self.openblas_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract OpenBLAS because "{}" could not be found.'.format(
                    file_path
                )
            )
            return False

        logging.info("Extracting OpenBLAS.")
        extract.tar(file_path, self.src_dir)
        os.rename(
            "{}/OpenBLAS-{}".format(self.src_dir, self.version), self.openblas_dir
        )

        if os.path.isdir(self.openblas_dir):
            return True
        return False

    def build(self, threads, cores=None, cflags=None, avx512=None):
        """Compiles OpenBLAS.

        Args:
            threads (int): The number of threads on the system.
            cores (int, optional): The number of cores on the system.
            cflags (str, optional): The CFLAGS for GCC.
            avx512 (bool, optional): Whether to enable AVX-512 CFLAGS.

        Returns:
            Boolean: True if compilation was successful otherwise False.
        """
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if "-O" not in cflags:
            cflags += " -O3 "
        if avx512 is True:
            cflags += (
                " -mavx512f -mavx512cd -mavx512bw -mavx512dq -mavx512vl"
                " -mavx512ifma -mavx512vbmi "
            )

        bin_loc = self.openblas_dir + "/libopenblas.so"
        shell_env = os.environ.copy()
        shell_env["CFLAGS"] = cflags
        shell_env["OMP_NUM_THREADS"] = str(threads)
        openmpi_dir = self.src_dir + "/openmpi/build/bin"
        mpifort_bin = openmpi_dir + "/mpifort"
        mpicc_bin = openmpi_dir + "/mpicc"

        if os.path.isfile(bin_loc):
            return True

        if not os.path.isdir(self.openblas_dir):
            prettify.error_message(
                'Cannot compile OpenBLAS because "{}" could not be found.'.format(
                    self.openblas_dir
                )
            )
            return False

        logging.info(
            "Compiling OpenBLAS using %d OMP threads, %d Make threads, "
            'and "%s" CFLAGS.',
            threads,
            cores,
            cflags,
        )

        execute.output(
            "make -j {} FC={} CC={} USE_OPENMP=1 USE_THREAD=1".format(
                cores, mpifort_bin, mpicc_bin
            ),
            self.openblas_dir,
            environment=shell_env,
        )

        if os.path.isfile(bin_loc):
            return True
        return False
