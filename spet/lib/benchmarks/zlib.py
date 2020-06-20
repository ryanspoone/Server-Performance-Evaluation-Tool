# -*- coding: utf-8 -*-
"""Zlib compression and decompression benchmarking.

This module handles the downloading, extracting, setting up, building,
and running compilation speed tests for zlib.
"""

import logging
import os
import statistics
import time

from ..utilities import download
from ..utilities import execute
from ..utilities import extract
from ..utilities import file
from ..utilities import optimize
from ..utilities import prettify


class Zlib:
    """Zlib compression and decompression benchmarking.

    Notes:
        * Requires `gcc` to be installed.

    Args:
        version (str): Version number for zlib.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for zlib.
        src_dir (str): The source directory for installing packages.
        zlib_dir (str): The source directory for the zlib.
        results_dir (str): The results directory for the zlib results.
        corpus_dir (str): The source directory for the corpus.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.zlib_dir = self.src_dir + "/zlib"
        self.results_dir = results_dir + "/zlib"
        self.corpus_dir = self.src_dir + "/corpus"
        self.commands = []

    def download(self):
        """Download zlib.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        url = "https://zlib.net/zlib-{}.tar.gz".format(self.version)
        archive_path = "{}/zlib-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            logging.debug('"%s" exists, exiting early.', archive_path)
            return True

        logging.info("Downloading zlib.")
        download.file(url, archive_path)
        logging.debug("Downloading zlib complete.")

        if os.path.isfile(archive_path):
            logging.debug('"%s" exists.', archive_path)
            return True
        return False

    def extract(self):
        """Extract zlib.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/zlib-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isdir(self.zlib_dir):
            logging.debug('"%s" exists, exiting early.', self.zlib_dir)
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract zlib because "{}" could '
                "not be found.".format(file_path)
            )
            return False

        logging.info("Extracting zlib.")

        extract.tar(file_path, self.src_dir)

        logging.debug(
            'Renaming "%s-%s" to "%s".', self.zlib_dir, self.version, self.zlib_dir
        )
        os.rename("{}-{}".format(self.zlib_dir, self.version), self.zlib_dir)

    def build(self, cores=None, cflags=None):
        """Compiles zlib.

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

        bin32_loc = self.zlib_dir + "/minigzip"
        bin64_loc = self.zlib_dir + "/minigzip64"
        shell_env = os.environ.copy()

        shell_env["CFLAGS"] = cflags

        logging.debug("CFLAGS: %s", shell_env["CFLAGS"])

        if os.path.isfile(bin32_loc) or os.path.isfile(bin64_loc):
            return True

        if not os.path.isdir(self.zlib_dir):
            prettify.error_message(
                'Cannot compile zlib because "{}" could '
                "not be found.".format(self.zlib_dir)
            )
            return False

        logging.info(
            'Compiling zlib with %d Make threads, and "%s" CFLAGS.', cores, cflags
        )

        cmd = "./configure && make -j " + str(cores)

        self.commands.append("Build: CFLAGS = " + cflags)
        self.commands.append("Build: " + cmd)

        execute.output(cmd, self.zlib_dir, environment=shell_env)

        if not os.path.isfile(bin32_loc) or not os.path.isfile(bin64_loc):
            return False
        return True

    def run(self):
        """Run zlib compression (level 6) and decompression three times.

        Returns:
            If success, a dict containing (unit, run1, run2, run3, average,
            median).

                unit (str): Score units.
                run1 (list): A list of (compress, decompress).
                    compress (float): The compression score for the first run.
                    decompress (float): The decompression score for the first
                        run.
                run2 (list): A list of (compress, decompress).
                    compress (float): The compression score for the second run.
                    decompress (float): The decompression score for the second
                        run.
                run3 (list): A list of (compress, decompress).
                    compress (float): The compression score for the third run.
                    decompress (float): The decompression score for the third
                        run.
                average (list): A list of (compress, decompress).
                    compress (float): The compression average of run1, run2,
                        and run3.
                    decompress (float): The decompression average of run1,
                        run2, and run3.
                median (list): A list of (compress, decompress).
                    compress (float): The compression median of run1, run2, and
                        run3.
                    decompress (float): The decompression median of run1, run2,
                        and run3.

            Else, a dict containing (error).

                error (str): Error message.
        """
        bin32_loc = self.zlib_dir + "/minigzip"
        bin64_loc = self.zlib_dir + "/minigzip64"
        level = 6
        corpus_file = self.corpus_dir + "/corpus.txt"
        corpus_archive = corpus_file + ".zlib"
        results = {"unit": "s"}
        compress_times = []
        decompress_times = []

        if not os.path.isfile(bin32_loc) or not os.path.isfile(bin64_loc):
            text = (
                'Cannot run zlib because neither "{}" or "{}" could not be'
                " found.".format(bin32_loc, bin64_loc)
            )
            prettify.error_message(text)
            return {"error": text}

        if not os.path.isfile(corpus_file):
            text = 'Cannot run zlib because "{}" could not be found.'.format(
                corpus_file
            )
            prettify.error_message(text)
            return {"error": text}

        logging.info("Running zlib.")

        used_bin = bin64_loc

        if not os.path.isfile(bin64_loc):
            used_bin = bin32_loc

        os.makedirs(self.results_dir, exist_ok=True)

        compress_warmup = "{} -1 < {} > /dev/null".format(used_bin, corpus_file)
        compress_cmd = "{} -{} < {} > {}".format(
            used_bin, level, corpus_file, corpus_archive
        )
        decompress_warmup = "{} -d < {} > /dev/null".format(used_bin, corpus_archive)
        decompress_cmd = "{} -d < {} > /dev/null".format(used_bin, corpus_archive)

        self.commands.append("Run - Warmup: " + compress_warmup)
        self.commands.append("Run: " + compress_cmd)
        self.commands.append("Run - Warmup: " + decompress_warmup)
        self.commands.append("Run: " + decompress_cmd)

        for count in range(1, 4):
            run_num = "run" + str(count)
            result_file = "{}/zlib_{}.txt".format(self.results_dir, run_num)

            optimize.prerun()
            time.sleep(10)

            # warm up
            execute.output(compress_warmup, self.corpus_dir)

            compress_time = execute.timed(compress_cmd, self.corpus_dir)

            optimize.prerun()
            time.sleep(10)

            # warm up
            execute.output(decompress_warmup, self.corpus_dir)

            decompress_time = execute.timed(decompress_cmd, self.corpus_dir)

            file.write(
                result_file,
                "Compress Time (Level {}):  {}\n"
                "Decompress Time:          {}\n".format(
                    level, compress_time, decompress_time
                ),
            )

            compress_times.append(compress_time)
            decompress_times.append(decompress_time)

            results[run_num] = {}
            results[run_num]["compress"] = compress_time
            results[run_num]["decompress"] = decompress_time

        os.remove(corpus_archive)

        results["average"] = {}
        results["average"]["compress"] = statistics.mean(compress_times)
        results["average"]["decompress"] = statistics.mean(decompress_times)
        results["median"] = {}
        results["median"]["compress"] = statistics.median(compress_times)
        results["median"]["decompress"] = statistics.median(decompress_times)
        results["variance"] = {}
        results["variance"]["compress"] = statistics.variance(compress_times)
        results["variance"]["decompress"] = statistics.variance(decompress_times)
        results["range"] = {}
        sorted_compress_times = sorted(compress_times)
        sorted_decompress_times = sorted(decompress_times)
        results["range"]["compress"] = (
            sorted_compress_times[-1] - sorted_compress_times[0]
        )
        results["range"]["decompress"] = (
            sorted_decompress_times[-1] - sorted_decompress_times[0]
        )

        logging.info("zlib results: %s", str(results))

        return results
