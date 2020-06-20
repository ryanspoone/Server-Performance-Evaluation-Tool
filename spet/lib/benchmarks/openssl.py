# -*- coding: utf-8 -*-
"""OpenSSL AES-128-GCM speed benchmarking.

This module handles the downloading, extracting, setting up, building,
and running OpenSSL.
"""

import logging
import os
import re
import statistics
import time

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import file
from spet.lib.utilities import optimize
from spet.lib.utilities import prettify


class OpenSSL:
    """Benchmark OpenSSL.

    Notes:
        * Requires `gcc` to be installed.
        * Requires glibc to be installed in the `/usr/local/glibc` prior to
            compiling.

    Args:
        version (str): Version number for OpenSSL.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for OpenSSL.
        src_dir (str): The source directory for installing packages.
        openssl_dir (str): The source directory for OpenSSL.
        results_dir (str): The results directory for OpenSSL results.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.openssl_dir = self.src_dir + "/openssl"
        self.results_dir = results_dir + "/openssl"
        self.commands = []

    def download(self):
        """Download OpenSSL.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        archive_path = "{}/openssl-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            return True

        url = "https://www.openssl.org/source/openssl-{}.tar.gz".format(self.version)

        logging.info("Downloading OpenSSL.")
        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract OpenSSL.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/openssl-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.exists(self.openssl_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract OpenSSL because "{}" could not be found.'.format(
                    file_path
                )
            )
            return False

        logging.info("Extracting OpenSSL.")
        extract.tar(file_path, self.src_dir)
        os.rename("{}-{}".format(self.openssl_dir, self.version), self.openssl_dir)

        if os.path.exists(self.openssl_dir):
            return True
        return False

    def build(self, glibc_ver, cores=None, cflags=None):
        """Compiles OpenSSL.

        Notes:
            * Requires glibc to be built in `/usr/local/glibc`

        Args:
            glibc_ver (str): The glibc version installed in the source
                directory.
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

        bin_loc = self.openssl_dir + "/apps/openssl"
        shell_env = os.environ.copy()

        shell_env["CFLAGS"] = cflags

        if os.path.isfile(bin_loc):
            return True

        if not os.path.isdir(self.openssl_dir):
            prettify.error_message(
                'Cannot compile OpenSSL because "{}" could not be found.'.format(
                    bin_loc
                )
            )
            return False

        logging.info(
            "Compiling OpenSSL with glibc version %s, %d Make threads"
            ', and "%s" CFLAGS.',
            glibc_ver,
            cores,
            str(shell_env["CFLAGS"]),
        )

        os.makedirs(self.openssl_dir + "/build", exist_ok=True)

        config_cmd = (
            "./config -Wl,--rpath=/usr/local/glibc/lib "
            "-Wl,--dynamic-linker=/usr/local/glibc/lib/ld-{0}.so "
            "-Wl,-rpath,{1} --prefix={1}/build".format(glibc_ver, self.openssl_dir)
        )
        make_cmd = "make -s -j {}".format(cores)
        install_cmd = "make -s -j {} install".format(cores)

        self.commands.append("Build: CFLAGS = " + cflags)
        self.commands.append("Config: " + config_cmd)
        self.commands.append("Compile: " + make_cmd)
        self.commands.append("Install: " + install_cmd)

        logging.debug("Config command:\n%s\n", config_cmd)

        execute.output(config_cmd, self.openssl_dir, environment=shell_env)

        compile_output = execute.output(
            "make -s -j {}".format(cores), self.openssl_dir, environment=shell_env
        )

        logging.debug("Compilation warnings/errors:\n%s", compile_output)

        install_output = execute.output(install_cmd, self.openssl_dir)
        logging.debug("Installation warnings/errors:\n%s", install_output)

        if os.path.isfile(bin_loc):
            return True
        return False

    @staticmethod
    def __taskset_ids(threads):
        """Numerical list of processor ids for `taskset -c`.

        Args:
            threads (int): The total number of threads on the system.

        Return:
            Str: Numberical list of processor ids not including the first core.
        """
        thread_siblings_list = file.read(
            "/sys/devices/system/cpu/cpu1/topology/thread_siblings_list"
        )
        core_list = thread_siblings_list.split(",")

        if len(core_list) <= 1:
            return "1-{}".format(threads - 1)

        core0_thread0 = core_list[0]
        core0_thread1 = core_list[1]

        return "{}-{},{}-{}".format(
            int(core0_thread0),
            int(threads / 2 - 1),
            int(core0_thread1),
            int(threads - 1),
        )

    @staticmethod
    def __multi_num(threads, taskset_ids):
        """The OpenSSL `-multi` flag based off of `taskset -c` processors.

        Args:
            threads (int): The total number of threads on the system.
            taskset_ids (str): Numerical list of processor ids for
                `taskset -c`.

        Return:
            Int: The number of threads actually being used.
        """

        if "," in taskset_ids:
            return threads - 2

        return threads - 1

    def run(self, threads):
        """Run OpenSSL three times.

        Args:
            threads (int): The total number of threads on the system.

        Returns:
            If success, a dict containing (unit, run1, run2, run3, average,
            median).

                unit (str): Score units.
                run1 (list): A list of (encrypt, decrypt).
                    encrypt (float): The encryption score for the first run.
                    decrypt (float): The decryption score for the first run.
                run2 (list): A list of (encrypt, decrypt).
                    encrypt (float): The encryption score for the second run.
                    decrypt (float): The decryption score for the second run.
                run3 (list): A list of (encrypt, decrypt).
                    encrypt (float): The encryption score for the third run.
                    decrypt (float): The decryption score for the third run.
                average (list): A list of (encrypt, decrypt).
                    encrypt (float): The encryption average of run1, run2, and
                        run3.
                    decrypt (float): The decryption average of run1, run2, and
                        run3.
                median (list): A list of (encrypt, decrypt).
                    encrypt (float): The encryption median of run1, run2, and
                        run3.
                    decrypt (float): The decryption median of run1, run2, and
                        run3.

            Else, a dict containing (error).

                error (str): Error message.
        """
        taskset_ids = self.__taskset_ids(threads)
        multi_num = self.__multi_num(threads, taskset_ids)
        bin_loc = self.openssl_dir + "/apps/openssl"
        results = {
            "aes-128-gcm": {
                "unit": "B/s",
                "score_size": 8192,
                "score_size_unit": "B",
                "test_bit_size": 128,
                "test": "AES-GCM",
            },
            "aes-256-gcm": {
                "unit": "B/s",
                "score_size": 8192,
                "score_size_unit": "B",
                "test_bit_size": 256,
                "test": "AES-GCM",
            },
        }

        shell_env = os.environ.copy()
        if "LD_LIBRARY_PATH" in shell_env:
            shell_env["LD_LIBRARY_PATH"] = "{}:{}".format(
                shell_env["LD_LIBRARY_PATH"], self.openssl_dir
            )
        else:
            shell_env["LD_LIBRARY_PATH"] = self.openssl_dir

        if not os.path.isfile(bin_loc):
            text = 'Could not find OpenSSL binaries at "{}".'.format(bin_loc)
            prettify.error_message(text)
            return {"error": text}

        logging.info(
            "Running OpenSSL on ids %s using a total of %d threads.",
            taskset_ids,
            multi_num,
        )

        os.makedirs(self.results_dir, exist_ok=True)

        for test in results:
            encrypt_results = []
            decrypt_results = []

            cmd_base = "taskset -c {} {} speed -multi {} -evp {}".format(
                taskset_ids, bin_loc, multi_num, test
            )
            cmd_decrypt = cmd_base + " -decrypt"

            self.commands.append("Run: " + cmd_base)
            self.commands.append("Run: " + cmd_decrypt)

            for count in range(1, 4):
                run_num = "run" + str(count)

                encrypt_result_file = "{}/openssl_{}_encrypt_{}.txt".format(
                    self.results_dir, test, run_num
                )
                decrypt_result_file = "{}/openssl_{}_decrypt_{}.txt".format(
                    self.results_dir, test, run_num
                )
                cmd_decrypt = cmd_base + " -decrypt"

                logging.debug("Encrypt command: %s", cmd_base)
                logging.debug("LD_LIBRARY_PATH: %s", shell_env["LD_LIBRARY_PATH"])

                optimize.prerun()
                time.sleep(10)

                encrypt_output = execute.output(cmd_base, environment=shell_env)
                file.write(encrypt_result_file, encrypt_output)

                logging.debug("Decrypt command: %s", cmd_base)
                logging.debug("LD_LIBRARY_PATH: %s", shell_env["LD_LIBRARY_PATH"])

                optimize.prerun()
                time.sleep(10)

                decrypt_output = execute.output(cmd_decrypt, environment=shell_env)
                file.write(decrypt_result_file, decrypt_output)

                encrypt_scores = encrypt_output.rstrip().split("\n")
                decrypt_scores = decrypt_output.rstrip().split("\n")

                if not encrypt_scores:
                    continue
                if not decrypt_scores:
                    continue
                encrypt_score = encrypt_scores[-1].split()[6]
                decrypt_score = decrypt_scores[-1].split()[6]

                if "k" in encrypt_score:
                    encrypt_score = re.sub(r"[^0-9.]", "", encrypt_score)
                if "k" in decrypt_score:
                    decrypt_score = re.sub(r"[^0-9.]", "", decrypt_score)

                # The 'numbers' are in 1000s of bytes per second processed.
                encrypt_score = float(encrypt_score) * 1000.0
                decrypt_score = float(decrypt_score) * 1000.0

                encrypt_results.append(encrypt_score)
                decrypt_results.append(decrypt_score)

                results[test][run_num] = {}
                results[test][run_num]["encrypt"] = encrypt_score
                results[test][run_num]["decrypt"] = decrypt_score

            if encrypt_results and decrypt_results:
                results[test]["average"] = {}
                results[test]["average"]["encrypt"] = statistics.mean(encrypt_results)
                results[test]["average"]["decrypt"] = statistics.mean(decrypt_results)
                results[test]["median"] = {}
                results[test]["median"]["encrypt"] = statistics.median(encrypt_results)
                results[test]["median"]["decrypt"] = statistics.median(decrypt_results)
                results[test]["variance"] = {}
                results[test]["variance"]["encrypt"] = statistics.variance(
                    encrypt_results
                )
                results[test]["variance"]["decrypt"] = statistics.variance(
                    decrypt_results
                )
                results[test]["range"] = {}
                sorted_encrypt = sorted(encrypt_results)
                results[test]["range"]["encrypt"] = (
                    sorted_encrypt[-1] - sorted_encrypt[0]
                )
                sorted_decrypt = sorted(decrypt_results)
                results[test]["range"]["decrypt"] = (
                    sorted_decrypt[-1] - sorted_decrypt[0]
                )

        logging.info("OpenSSL results: %s", str(results))

        return results
