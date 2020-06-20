# -*- coding: utf-8 -*-
"""Intel Memory Latency Checker (MLC) benchmarking.

This module handles the extracting and running MLC.
"""

import logging
import os
import statistics

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import file
from spet.lib.utilities import grep
from spet.lib.utilities import prettify


class MemoryLatencyChecker:
    """Intel Memory Latency Checker (MLC) benchmarking.

    Args:
        version (str): Version number for HPL.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for MLC.
        src_dir (str): The source directory for installing packages.
        mlc_dir (str): The source directory for the MLC.
        results_dir (str): The results directory for the Linpack results.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.mlc_dir = self.src_dir + "/mlc"
        self.results_dir = results_dir + "/mlc"
        self.commands = []

    def download(self, url=None):
        """Download MLC.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        archive_path = "{}/mlc_v{}.tgz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        if url is None:
            prettify.error_message(
                "Unable to find an URL for MLC. Please visit "
                "https://software.intel.com/en-us/articles/intelr-memory-latency-checker"  # nopep8
                " to download MLC and place the archive in the {} directory.".format(
                    self.src_dir
                )
            )
            return False

        logging.info("Downloading MLC.")
        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract MLC.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/mlc_v{}.tgz".format(self.src_dir, self.version)

        if os.path.isdir(self.mlc_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract MLC because "{}" could not be found.'
                " Please download it from: \n\n"
                "https://software.intel.com/en-us/articles/intelr-memory-latency-checker".format(  # nopep8
                    file_path
                )
            )
            return False

        logging.info("Extracting MLC.")

        os.makedirs(self.mlc_dir, exist_ok=True)

        extract.tar(file_path, self.mlc_dir)

        if os.path.isdir(self.mlc_dir):
            return True
        return False

    @staticmethod
    def __node_latency_statistics(results):
        """Average and Median for each NUMA node.

        Args:
            results (dict): All results for a MLC run.

        Returns:
            Original results with the added |average| and |median| keys and
            values.
        """
        if "run1" not in results:
            prettify.error_message(
                "Cannot calculate the node statistics for MLC because the "
                "results list is empty."
            )
            return results

        averages = []
        medians = []
        variances = []
        ranges = []

        logging.debug("Computing node statistics.")

        for node in range(0, len(results["run1"])):
            latencies = []
            logging.debug("node: %s", repr(node))
            for run in results:
                logging.debug("run: %s", repr(run))
                if "run" not in run:
                    continue
                logging.debug("Appending: %s", repr(float(results[run][node])))
                latencies.append(float(results[run][node]))

            averages.append(statistics.mean(latencies))
            medians.append(statistics.median(latencies))
            variances.append(statistics.variance(latencies))
            sorted_latencies = sorted(latencies)
            ranges.append(sorted_latencies[-1] - sorted_latencies[0])

        logging.debug("Averages:\n%s", repr(averages))
        results["average"] = averages

        logging.debug("Medians:\n%s", repr(medians))
        results["median"] = medians

        logging.debug("Variances:\n%s", repr(variances))
        results["variance"] = variances

        logging.debug("Ranges:\n%s", repr(ranges))
        results["range"] = ranges

        return results

    def run(self):
        """Run MLC three times.

        Returns:
            If success: A dict containing (unit, run1, run2, run3, average,
            median).

                unit (str): Latency units.
                run1 (list): Latency for each NUMA node of the first run.
                run2 (list): Latency for each NUMA node of the second run.
                run3 (list): Latency for each NUMA node of the third run.
                average (list): Average for each NUMA node of run1, run2, and
                    run3.
                median (list): Median for each NUMA node of run1, run2, and
                    run3.

            If error: A dict containing (error).
                error (str): Error message.
        """
        bin_loc = self.mlc_dir + "/Linux/mlc_avx512"
        cmd = "modprobe msr; {} --latency_matrix".format(bin_loc)
        results = {"unit": "ns"}

        if not os.path.isfile(bin_loc):
            text = 'Cannot run MLC because "{}" could not be found.'.format(bin_loc)
            prettify.error_message(text)
            return {"error": text}

        os.makedirs(self.results_dir, exist_ok=True)
        self.commands.append("Run: " + cmd)

        output = execute.output(cmd, self.mlc_dir)

        file.write(self.results_dir + "/mlc_output.txt", output)

        found_lines = grep.text(output, r"^\s*0")

        if found_lines:
            node_latencies = found_lines[0].strip().split()
            node_latencies.pop(0)  # Remove leading '0' for first node
            for index, latency in enumerate(node_latencies):
                node_latencies[index] = float(latency)
            results["latencies"] = node_latencies

        logging.info("MLC results: %s", str(results))
        return results
