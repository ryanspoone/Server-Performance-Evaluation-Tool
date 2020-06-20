# -*- coding: utf-8 -*-
"""STREAM memory bandwidth benchmarking.

This module handles the downloading, building, and running GCC compiled STREAM
OMP.
"""

import logging
import os
import stat
import statistics
import time

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import file
from spet.lib.utilities import grep
from spet.lib.utilities import optimize
from spet.lib.utilities import prettify


class STREAM:
    """GCC compiled STREAM memory bandwidth benchmarking.

    Notes:
        * Requires `gcc` to be installed.

    Args:
        version (str): Version number for STREAM.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for STREAM.
        src_dir (str): The source directory for installing packages.
        stream_dir (str): The source directory for the STREAM.
        results_dir (str): The results directory for the STREAM results.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.stream_dir = self.src_dir + "/stream"
        self.results_dir = results_dir + "/stream"
        self.commands = []

    def download(self):
        """Download STREAM source.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        url = "https://www.cs.virginia.edu/stream/FTP/Code/stream.c"
        target_file = self.stream_dir + "/stream.c"

        if os.path.isfile(target_file):
            return True

        logging.info("Downloading STREAM.")

        os.makedirs(self.stream_dir, exist_ok=True)
        download.file(url, target_file)

        if os.path.isfile(target_file):
            return True
        return False

    @staticmethod
    def __set_array_size(cache, sockets):
        """Determines how large the STREAM array size should be.

        Args:
            cache (int): The cache size in bytes (usually L3).
            sockets (int): The number of sockets on the system.

        Returns:
            Integer: STREAM array size
        """
        multiplier = 4
        min_array_size = 10000000

        stream_array_size = multiplier * (cache * sockets) / 8

        if stream_array_size < min_array_size:
            stream_array_size = min_array_size

        return int(stream_array_size)

    def build(self, cache, sockets, cflags=None, stream_array_size=None):
        """Compiles STREAM with GCC.

        Args:
            cache (int): The cache size in bytes (usually L3).
            sockets (int): The number of sockets on the system.
            cflags (str, optional): The CFLAGS for GCC.
            stream_array_size (int, optional): The array size for STREAM.

        Returns:
            Boolean: True if compilation was successful otherwise False.
        """
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if "-O" not in cflags:
            cflags += " -O3 "

        cflags += " -fopenmp "

        stream_file = self.stream_dir + "/stream.c"
        stream_exe = self.stream_dir + "/stream"
        shell_env = os.environ.copy()
        mpi_root = self.src_dir + "/openmpi/build"
        mpi_path = mpi_root + "/bin"
        mpi_lib = mpi_root + "/lib"
        shell_env["PATH"] += ":" + mpi_path
        if "LD_LIBRARY_PATH" in shell_env:
            shell_env["LD_LIBRARY_PATH"] += mpi_lib
        else:
            shell_env["LD_LIBRARY_PATH"] = mpi_lib

        mpicc = mpi_path + "/mpicc"

        if os.path.isfile(stream_exe):
            return True

        if not os.path.isfile(stream_file):
            prettify.error_message(
                'Cannot compile STREAM because "{}" could '
                "not be found.".format(stream_file)
            )
            return False

        if stream_array_size is None:
            stream_array_size = self.__set_array_size(cache, sockets)

        if stream_array_size > 4000000000:
            cflags += " -mcmodel=medium "

        cflags += " -D_OPENMP "
        cflags += " -DSTREAM_ARRAY_SIZE={} ".format(stream_array_size)
        cflags += " -DNTIMES=1000 "

        build_cmd = "{} {} stream.c -o stream".format(mpicc, cflags)

        logging.info(
            'Compiling STREAM with %d array size, and "%s" CFLAGS.',
            stream_array_size,
            cflags,
        )

        self.commands.append("Build: " + build_cmd)

        output = execute.output(
            build_cmd, working_dir=self.stream_dir, environment=shell_env
        )

        logging.debug(output)

        if os.path.isfile(stream_exe):
            status = os.stat(stream_exe)
            os.chmod(stream_exe, status.st_mode | stat.S_IEXEC)

        if os.path.isfile(stream_exe):
            return True
        return False

    def run(self, threads):
        """Run GCC compiled STREAM three times.

        Args:
            threads (int): The total number of threads on the system.

        Returns:
            If success, a dict containing (unit, run1, run2, run3, average,
            median).

                unit (str): Score units.
                run1 (float): Score for the first run.
                run2 (float): Score for the second run.
                run3 (float): Score for the third run.
                average (float): Average of run1, run2, and run3.
                median (float): Median of run1, run2, and run3.

            Else, a dict containing (error).

                error (str): Error message.
        """
        stream_bin = self.stream_dir + "/stream"
        shell_env = os.environ.copy()
        shell_env["OMP_NUM_THREADS"] = str(threads)
        mpi_root = self.src_dir + "/openmpi/build"
        mpi_path = mpi_root + "/bin"
        mpi_lib = mpi_root + "/lib"
        shell_env["PATH"] += ":" + mpi_path
        if "LD_LIBRARY_PATH" in shell_env:
            shell_env["LD_LIBRARY_PATH"] += mpi_lib
        else:
            shell_env["LD_LIBRARY_PATH"] = mpi_lib
        results = {"unit": "MB/s"}

        shell_env["OMP_PROC_BIND"] = "true"

        if not os.path.isfile(stream_bin):
            text = 'Cannot run STREAM because "{}" could not be found.'.format(
                stream_bin
            )
            prettify.error_message(text)
            return {"error": text}

        logging.info("Running STREAM with %d OMP threads.", threads)

        os.makedirs(self.results_dir, exist_ok=True)

        tmp_results = []

        cmd = "./stream"

        self.commands.append("Run: OMP_NUM_THREADS = " + str(threads))
        self.commands.append("Run: OMP_PROC_BIND = true")
        self.commands.append("Run: " + cmd)

        for count in range(1, 4):
            run_num = "run" + str(count)
            result_file = "{}/stream_{}.txt".format(self.results_dir, run_num)

            optimize.prerun()
            time.sleep(10)

            output = execute.output(
                cmd, working_dir=self.stream_dir, environment=shell_env
            )

            file.write(result_file, output)

            result = grep.text(output, "Triad")
            result = result[0].split()[1]  # 2nd word
            result = float(result)
            results[run_num] = result
            tmp_results.append(result)

        results["average"] = statistics.mean(tmp_results)
        results["median"] = statistics.median(tmp_results)
        results["variance"] = statistics.variance(tmp_results)
        sorted_results = sorted(tmp_results)
        results["range"] = sorted_results[-1] - sorted_results[0]

        logging.info("STREAM results: %s", str(results))

        return results
