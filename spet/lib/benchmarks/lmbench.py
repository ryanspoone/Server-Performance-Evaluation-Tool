# -*- coding: utf-8 -*-
"""LMbench memory read latency benchmarking.

This module handles the downloading, extracting, setting up, building,
and running LMbench.
"""

import logging
import os

from ..utilities import download
from ..utilities import execute
from ..utilities import extract
from ..utilities import file
from ..utilities import prettify


class LMbench:
    """Benchmark memory latencies using LMbench.

    Notes:
        * Requires `gcc` to be installed.
        * Requires R's `littler` to be installed.

    Args:
        version (str): Version number for LMbench.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for LMbench.
        src_dir (str): The source directory for installing packages.
        lmbench_dir (str): The source directory for LMbench.
        results_dir (str): The results directory for LMbench results.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.lmbench_dir = self.src_dir + "/lmbench"
        self.results_dir = results_dir + "/lmbench"
        self.commands = []

    def download(self):
        """Download LMbench.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        archive_path = "{}/lmbench{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        url = "http://www.bitmover.com/lmbench/lmbench{}.tar.gz".format(self.version)

        logging.info("Downloading LMbench.")

        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract LMbench.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/lmbench{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isdir(self.lmbench_dir):
            return True

        logging.info("Extracting LMbench.")

        extract.tar(file_path, self.src_dir)
        os.rename(self.lmbench_dir + self.version, self.lmbench_dir)

        if os.path.isdir(self.lmbench_dir):
            return True
        return False

    def build(self, arch=None, cores=None, cflags=None):
        """Compiles LMbench.

        Args:
            arch (str, optional): The architecture type of the system.
            cores (int, optional): The number of cores on the system.
            cflags (str, optional): The CFLAGS for GCC.

        Returns:
            Boolean: True if compilation was successful otherwise False.
        """
        if arch is None:
            arch = "x86_64"
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if "-O" not in cflags:
            cflags += " -O3 "

        bin_loc = "{}/bin/{}-linux-gnu/lat_mem_rd".format(self.lmbench_dir, arch)
        shell_env = os.environ.copy()
        shell_env["CFLAGS"] = cflags
        sccs_dir = self.lmbench_dir + "/SCCS"
        sccs_file = sccs_dir + "/s.ChangeSet"

        if os.path.isfile(bin_loc):
            return True

        if not os.path.isdir(self.lmbench_dir):
            text = 'Cannot compile LMbench because "{}" could not be ' "found.".format(
                self.lmbench_dir
            )
            prettify.error_message(text)
            logging.error(text)
            return False

        logging.info(
            'Compiling LMbench using "%s" arch, %d Make threads,' ' and "%s" CFLAGS.',
            arch,
            cores,
            shell_env["CFLAGS"],
        )

        # This file creates errors if it is not present
        if not os.path.exists(sccs_file):
            os.makedirs(sccs_dir, exist_ok=True)
            file.touch(sccs_file)

        cmd = "make -s -j {}".format(cores)

        self.commands.append("Build: CFLAGS = " + cflags)
        self.commands.append("Build: " + cmd)

        execute.output(cmd, working_dir=self.lmbench_dir, environment=shell_env)

        if os.path.isfile(bin_loc):
            return True
        return False

    @staticmethod
    def __closest_cache_latency(cache_size, lmbench_output):
        """The closest LMbench stride cache latency lower than max cache size.

        Args:
            cache_size (float): The cache size to compare.
            lmbench_output (str): The contents of the lmbench results.

        Returns:
            Float: The closest latency to max cache size.
        """
        lines = lmbench_output.split("\n")
        tmp_latency = None
        for line in lines:
            if "stride" in line:
                continue
            words = line.split()
            if not words:
                continue
            current_cache_size = float(words[0])
            current_cache_latency = float(words[1])
            if current_cache_size <= cache_size:
                tmp_latency = current_cache_latency
                continue
            break
        return tmp_latency

    def run(self, l1_cache, l2_cache, l3_cache, arch=None, threads=None):
        """Run High-Performance Linpack three times.

        Args:
            l1_cache (int): The L1-Cache size in B for the system.
            l2_cache (int): The L2-Cache size in B for the system.
            l3_cache (int): The L3-Cache size in B for the system.
            arch (str, optional): The architecture type of the system.
            threads (int): The number of threads on the system.

        Returns:
            If success, a dict containing (unit, run1, run2, run3, average,
            median).

                unit (str): Latency units.
                level1 (float): Latency for L1-Cache.
                level2 (float): Latency for L2-Cache.
                level3 (float): Latency for L3-Cache.

            Else, a dict containing (error).

                error (str): Error message.
        """
        if arch is None:
            arch = "x86_64"
        if threads is None:
            threads = 1

        thread = 0
        stride = 1024
        max_cache = 512
        bin_loc = "{}/bin/{}-linux-gnu/lat_mem_rd".format(self.lmbench_dir, arch)
        results = {"unit": "ns"}

        if not os.path.isfile(bin_loc):
            text = 'Could not find LMbench binaries at "{}".'.format(bin_loc)
            prettify.error_message(text)
            logging.error(text)
            return {"error": text}

        logging.info(
            "Running LMbench using %d L1-Cache, %d L2-Cache, "
            '%d L3-Cache, and "%s" arch.',
            l1_cache,
            l2_cache,
            l3_cache,
            arch,
        )

        os.makedirs(self.results_dir, exist_ok=True)

        if threads >= 3:
            thread = 2

        run_command = "taskset -c {} {} {} {}".format(
            thread, bin_loc, max_cache, stride
        )

        self.commands.append("Run: " + run_command)

        result_file = self.results_dir + "/lmbench_output.txt"
        output = execute.output(run_command)
        file.write(result_file, output)

        l1_latency = self.__closest_cache_latency(
            float(l1_cache) / 1024.0 / 1024.0, output
        )

        if l2_cache:
            l2_latency = self.__closest_cache_latency(
                float(l2_cache) / 1024.0 / 1024.0, output
            )

        if l3_cache:
            l3_latency = self.__closest_cache_latency(
                float(l3_cache) / 1024.0 / 1024.0, output
            )

        if l1_latency:
            results["level1"] = float(l1_latency)
        if l2_latency:
            results["level2"] = float(l2_latency)
        if l3_latency:
            results["level3"] = float(l3_latency)

        logging.info("LMbench results: %s", str(results))
        return results
