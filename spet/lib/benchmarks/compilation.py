# -*- coding: utf-8 -*-
"""Timed Linux kernel compilation speeds."""

import logging
import os
import statistics
import time

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import file
from spet.lib.utilities import optimize
from spet.lib.utilities import prettify


class CompilationSpeed:
    """Timed Linux kernel compilation speeds.

    Args:
        version (str): Version number for the Linux kernel.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for the Linux kernel.
        src_dir (str): The source directory for installing packages.
        kernel_dir (str): The source directory for the Linux kernel.
        results_dir (str): The results directory for the speed results.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.kernel_dir = self.src_dir + "/linux"
        self.results_dir = results_dir + "/kernel"
        self.commands = []

    def download(self):
        """Download the Linux kernel.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        major_version = self.version.split(".")[0]
        url = (
            "http://www.kernel.org/pub/linux/kernel/v{}.x/" "linux-{}.tar.gz"
        ).format(major_version, self.version)
        archive_path = "{}/linux-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        logging.info("Downloading the Linux kernel.")

        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract the Linux kernel.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/linux-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isdir(self.kernel_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract the Linux kernel because "{}" could not be '
                "found.".format(file_path)
            )
            return False

        logging.info("Extracting the Linux kernel.")

        extract.tar(file_path, self.src_dir)
        os.rename("{}-{}".format(self.kernel_dir, self.version), self.kernel_dir)

        if os.path.isdir(self.kernel_dir):
            return True
        return False

    def setup(self, cores=None, cflags=None):
        """Setup the Linux kernel config file.

        Args:
            cores (int, optional): The number of cores on the system.
            cflags (str, optional): The CFLAGS for GCC.

        Returns:
            Boolean: True if setup was successful otherwise False.
        """
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = "-march=native -mtune=native"

        config_loc = self.kernel_dir + "/.config"
        shell_env = os.environ.copy()
        if "-O" not in cflags:
            cflags += " -O3 "
        shell_env["CFLAGS"] = cflags

        if os.path.isfile(config_loc):
            return True

        if not os.path.isdir(self.kernel_dir):
            prettify.error_message(
                'Cannot configure the Linux kernel because "{}" could not be'
                " found.".format(self.kernel_dir)
            )
            return False

        logging.info(
            "Setting up the Linux kernel with %d Make threads, " 'and "%s" CFLAGS.',
            cores,
            str(shell_env["CFLAGS"]),
        )

        cmd = "make -s -j {0} defconfig && make -s -j {0} clean".format(cores)

        output = execute.output(cmd, working_dir=self.kernel_dir, environment=shell_env)

        logging.debug("Build output:\n%s", output)

        self.commands.append("Setup: CFLAGS = " + cflags)
        self.commands.append("Setup: " + cmd)

        if os.path.isfile(config_loc):
            return True
        return False

    def run(self, cores=None, cflags=None):
        """Run three timed Linux kernel compilations.

        Args:
            cores (int, optional): The number of cores on the system.

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
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if "-O" not in cflags:
            cflags += " -O3 "
        shell_env = os.environ.copy()
        shell_env["CFLAGS"] = cflags

        results = {"unit": "s"}
        config_loc = self.kernel_dir + "/.config"
        tmp_results = []

        if not os.path.isfile(config_loc):
            text = (
                'Cannot run timed Linux kernel because "{}" could not '
                "be found.".format(config_loc)
            )
            prettify.error_message(text)
            return {"error": text}

        logging.info(
            "Running timed Linux kernel compilation using %d Make " "thread.", cores
        )

        os.makedirs(self.results_dir, exist_ok=True)

        clean_cmd = "make -s -j {} clean".format(cores)
        build_cmd = "make -s -j {}".format(cores)
        self.commands.append("Run: CFLAGS = " + cflags)
        self.commands.append("Prerun: " + clean_cmd)
        self.commands.append("Run: " + build_cmd)

        for count in range(1, 4):
            run_num = "run" + str(count)
            result_file = "{}/zlib_{}.txt".format(self.results_dir, run_num)

            execute.output(clean_cmd, self.kernel_dir, environment=shell_env)

            optimize.prerun()
            time.sleep(10)

            compile_speed = execute.timed(
                build_cmd, working_dir=self.kernel_dir, environment=shell_env
            )

            if (
                not os.path.isfile(self.kernel_dir + "/vmlinux")
                or compile_speed is None
            ):
                return {"error": "Linux Kernel failed to compile."}

            file.write(
                result_file,
                "{}\nLinux Kernel Compilation Speed:  {}\n".format(
                    build_cmd, compile_speed
                ),
            )

            results[run_num] = float(compile_speed)
            tmp_results.append(compile_speed)

        if tmp_results:
            results["average"] = statistics.mean(tmp_results)
            results["median"] = statistics.median(tmp_results)
            results["variance"] = statistics.variance(tmp_results)
            sorted_results = sorted(tmp_results)
            results["range"] = sorted_results[-1] - sorted_results[0]

        logging.info("Timed Linux kernel compilation results:\n%s", str(results))

        return results
