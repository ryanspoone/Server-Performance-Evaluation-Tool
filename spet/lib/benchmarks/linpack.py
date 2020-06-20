# -*- coding: utf-8 -*-
"""Intel LINPACK and High-Performance Linpack benchmarking.

This module handles the downloading, extracting, setting up, building,
and running HPL.
"""

import collections
import filecmp
import logging
import math
import os
import shutil
import time

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import file
from spet.lib.utilities import grep
from spet.lib.utilities import optimize
from spet.lib.utilities import prettify


class Linpack:
    """High-Performance Linpack (HPL) benchmarking.

    Notes:
        * Requires `gcc` to be installed.
        * Requires OpenMPI to be installed in the `src_dir` prior to compiling.
        * Requires OpenBLAS to be installed in the `src_dir` prior to
            compiling.

    Args:
        version (str): Version number for HPL.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for HPL.
        src_dir (str): The source directory for installing packages.
        hpl_dir (str): The source directory for the HPL.
        results_dir (str): The results directory for the HPL results.
        mathlib (str): The math library used.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.hpl_dir = self.src_dir + "/hpl"
        self.results_dir = results_dir + "/hpl"
        self.mathlib = "openblas"
        self.commands = []

    def download(self):
        """Download High-Performance Linpack (HPL).

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        archive_name = "hpl-{}.tar.gz".format(self.version)
        archive_path = "{}/{}".format(self.src_dir, archive_name)

        if os.path.isfile(archive_path):
            return True

        url = "http://www.netlib.org/benchmark/hpl/" + archive_name

        logging.info("Downloading High-Performance Linpack.")
        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract High-Performance Linpack (HPL).

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}-{}.tar.gz".format(self.hpl_dir, self.version)

        if os.path.exists(self.hpl_dir):
            return True

        if not os.path.isfile(file_path):
            text = 'Cannot extract HPL because "{}" could not be ' "found.".format(
                file_path
            )
            prettify.error_message(text)
            logging.error(text)
            return False

        logging.info("Extracting High-Performance Linpack.")
        extract.tar(file_path, self.src_dir)
        os.rename("{}-{}".format(self.hpl_dir, self.version), self.hpl_dir)

        if os.path.exists(self.hpl_dir):
            return True
        return False

    def edit_makefile(self, processor, arch=None, cflags=None, avx512=None):
        """Edits the provided HPL Makefile with values for this system.

        Args:
            processor (str): The processor name for the system.
            arch (str, optional): The architecture type of the system.
            cflags (str, optional): The CFLAGS for GCC.
            avx512 (bool, optional): If AVX-512 instructions should be added to
                                     the CFLAGS.

        Returns:
            Boolean: True if edit was successful otherwise False.
        """
        if arch is None:
            arch = "x86_64"
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if avx512 is True:
            cflags += (
                " -mavx512f -mavx512cd -mavx512bw -mavx512dq -mavx512vl"
                " -mavx512ifma -mavx512vbmi "
            )

        blis_dir = "{}/blis".format(self.src_dir)
        mkl_dir = "/opt/intel/mkl"

        if "intel" in processor.lower() and os.path.isdir(mkl_dir):
            makefile = "Make.intel"
            self.mathlib = "mkl"
            mathlib_path = mkl_dir
        elif "amd" in processor.lower() and os.path.isdir(blis_dir):
            makefile = "Make.amd"
            self.mathlib = "blis"
            mathlib_path = blis_dir
        else:
            makefile = "Make.generic"
            self.mathlib = "openblas"
            mathlib_path = "{}/openblas".format(self.src_dir)

        orig_make = self.src_dir + "/provided/" + makefile
        dest_make = "{}/Make.{}".format(self.hpl_dir, arch)

        if os.path.exists(dest_make):
            return True

        if not os.path.isfile(orig_make):
            text = (
                "Cannot edit HPL's Makefile because '{}' could "
                "not be found.".format(orig_make)
            )
            prettify.error_message(text)
            logging.error(text)
            return False

        if not os.path.isdir(self.hpl_dir):
            text = (
                "Cannot edit HPL's Makefile because '{}' could "
                "not be found.".format(self.hpl_dir)
            )
            prettify.error_message(text)
            logging.error(text)
            return False

        logging.info(
            "Editing the High-Performance Linpack Makefile using "
            '"%s" arch and "%s" CFLAGS.',
            arch,
            cflags,
        )

        file.touch(dest_make)
        shutil.copyfile(orig_make, dest_make)

        file.replace_line(
            dest_make, "ARCH         = x86_64", "ARCH         = {}".format(arch)
        )

        file.replace_line(
            dest_make, "TOPdir       =", "TOPdir       = {}".format(self.hpl_dir)
        )

        file.replace_line(dest_make, "LAdir        =", "LAdir        = " + mathlib_path)

        file.replace_line(
            dest_make,
            "CC           =",
            "CC           = {}"
            "/openmpi/build/bin/mpicc {} -lgomp -fopenmp".format(self.src_dir, cflags),
        )

        if os.path.isfile(dest_make):
            return True
        return False

    def build(self, threads, arch=None, cores=None, cflags=None, avx512=None):
        """Compiles High-Performance Linpack (HPL).

        Args:
            threads (int): The number of threads on the system.
            arch (str, optional): The architecture type of the system.
            cores (int, optional): The number of cores on the system.
            cflags (str, optional): The CFLAGS for GCC.
            avx512 (bool, optional): If AVX-512 instructions should be added to
                                     the CFLAGS.

        Returns:
            Boolean: True if compilation was successful otherwise False.
        """
        if arch is None:
            arch = "x86_64"
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if avx512 is True:
            cflags += (
                " -mavx512f -mavx512cd -mavx512bw -mavx512dq -mavx512vl"
                " -mavx512ifma -mavx512vbmi "
            )
        if "-O" not in cflags:
            cflags += " -O3 "

        shell_env = os.environ.copy()
        shell_env["CFLAGS"] = cflags
        shell_env["OMP_NUM_THREADS"] = str(threads)
        bin_file = "{}/bin/{}/xhpl".format(self.hpl_dir, arch)
        mpicc_bin = self.src_dir + "/openmpi/build/bin/mpicc"
        makefile = self.hpl_dir + "/Make." + arch

        if os.path.isfile(bin_file):
            return True

        if not os.path.isdir(self.hpl_dir):
            text = 'Cannot compile LINPACK because "{}" could not ' "be found.".format(
                self.hpl_dir
            )
            prettify.error_message(text)
            logging.error(text)
            return False

        if not os.path.isfile(makefile):
            text = 'Cannot compile LINPACK because "{}" could not ' "be found.".format(
                makefile
            )
            prettify.error_message(text)
            logging.error(text)
            return False

        if not os.path.isfile(mpicc_bin):
            text = 'Cannot compile LINPACK because "{}" could not ' "be found.".format(
                mpicc_bin
            )
            prettify.error_message(text)
            logging.error(text)
            return False

        logging.info(
            'Compiling LINPACK using %s OMP threads, "%s" arch,'
            ' %d Make threads, and "%s" CFLAGS.',
            shell_env["OMP_NUM_THREADS"],
            arch,
            cores,
            shell_env["CFLAGS"],
        )

        # Sometimes building has an issue on the first run and doesn't build
        # but the second go-round is perfectly fine
        build_cmd = (
            "make -s -j {0} all arch={1} || make -s -j {0} all "
            "arch={1}".format(cores, arch)
        )
        install_cmd = "make -s -j {} install arch={}".format(cores, arch)

        self.commands.append("Build: CFLAGS = " + cflags)
        self.commands.append("Build: OMP_NUM_THREADS = " + str(threads))
        self.commands.append("Build: " + build_cmd)
        self.commands.append("Install: " + install_cmd)

        execute.output(build_cmd, working_dir=self.hpl_dir, environment=shell_env)

        execute.output(install_cmd, working_dir=self.hpl_dir, environment=shell_env)

        if os.path.isfile(bin_file):
            return True
        return False

    @staticmethod
    def __calculate_n(memory_gb, nb_size):
        """Calculate the problem size for LINPACK.

        Args:
            memory_gb (int): The total memory in GB of the system.
            nb_size (int): Block size.

        Returns:
            Integer: Problem size for LINPACK.
        """
        if memory_gb < 1:
            memory_gb = 1
        utilization = 0.8
        memory_alignment = 8
        memory_b = memory_gb * 1024 * 1024 * 1024
        tmp = int(math.sqrt((utilization * memory_b) / memory_alignment))
        # for precision by nb_size
        tmp = int(tmp / nb_size)
        tmp = int(tmp * nb_size)
        return tmp

    @staticmethod
    def __scale_n(n_size, nb_size):
        """Scale the n_size to avoid memory allocation issues.

        Args:
            n_size (int): The problem size for LINPACK.
            nb_size (int): Block size.

        Example:
            >>> __scale_n(137706, 389)
            [137, 1377, 13770, 137706]

        Returns:
            List: All integer N sizes to scale.
        """
        n_sizes = [n_size]
        current = n_size
        while current > 1000:
            current = int(current / 1.25)
            current = int(current / nb_size)
            current = int(current * nb_size)
            n_sizes.append(int(current))
        n_sizes = sorted(n_sizes)
        # HPL won't allow > 20 N sizes
        if len(n_sizes) > 20:
            n_sizes = n_sizes[-20:]
        return n_sizes

    @staticmethod
    def __grid(mpi_threads):
        """Calculate the PxQ grid for LINPACK.

        Args:
            mpi_threads (int): The number of MPI threads on the system.

        Example:
            >>> __grid(112)
            grid(P=8, Q=14)

        Returns:
            NamedTuple: P and Q.
        """
        i = 1
        divisors = []
        grid = collections.namedtuple("grid", ["P", "Q"])
        if mpi_threads < i:
            return None
        while i <= mpi_threads:
            if mpi_threads % i == 0:
                divisors.append(i)
            i = i + 1
        half = len(divisors) / 2.0
        middle = int(half)
        if half % 1 == 0:
            return grid(P=divisors[middle - 1], Q=divisors[-middle])
        return grid(P=divisors[middle], Q=divisors[middle])

    @staticmethod
    def __nb_size(threads):
        if threads >= 64:
            nb_size = 384
        elif threads >= 32:
            nb_size = 256
        else:
            nb_size = 192
        return nb_size

    def edit_datfile(self, memory_gb, mpi_threads, threads, arch=None):
        """Optimizes DAT file values.

        Args:
            memory_gb (int): The total memory in GB of the system.
            mpi_threads (int): The number of MPI threads used by LINPACK. This
                number is usually the number of physical cores on the system.
            threads (int): The total number of logical threads on the system.
            arch (str, optional): The architecture type of the system.

        Returns:
            Boolean: True if edit was successful otherwise False.
        """
        if arch is None:
            arch = "x86_64"

        orig_dat = self.src_dir + "/provided/HPL.dat"
        bin_dir = "{}/bin/{}".format(self.hpl_dir, arch)
        dest_dat = bin_dir + "/HPL.dat"

        nb_size = self.__nb_size(threads)

        if filecmp.cmp(orig_dat, dest_dat):
            return True

        if not os.path.isfile(dest_dat):
            text = 'Could not find the HPL DAT file at "{}".'.format(dest_dat)
            prettify.error_message(text)
            return False

        n_size = self.__calculate_n(memory_gb, nb_size)
        n_sizes = self.__scale_n(n_size, nb_size)
        file.replace_line(
            orig_dat,
            r"\d+\s+# of problems sizes \(N\)",
            str(len(n_sizes)) + "      # of problems sizes (N)",
        )
        file.replace_line(
            orig_dat,
            r"(\d+\s)+\s*Ns",
            " ".join(str(size) for size in n_sizes) + "   Ns",
        )
        file.replace_line(orig_dat, r"(\d+\s)+\s*NBs", str(nb_size) + "    NBs")

        grid = self.__grid(mpi_threads)
        file.replace_line(
            orig_dat,
            r"\d+\s+# of process grids \(P x Q\)",
            "1  # of process grids (P x Q)",
        )
        file.replace_line(orig_dat, r"([0-9]+\s+)+Ps", "{}  Ps".format(grid.P))
        file.replace_line(orig_dat, r"([0-9]+\s+)+Qs", "{}  Qs".format(grid.Q))

        logging.info("Replacing High-Performance Linpack DAT file.")
        shutil.copyfile(orig_dat, dest_dat)

        if filecmp.cmp(orig_dat, dest_dat):
            return True
        return False

    def run(self, mpi_threads, threads, arch=None):
        """Run High-Performance Linpack three times.

        Args:
            mpi_threads (int): The number of MPI threads used by LINPACK. This
                number is usually the number of physical cores on the system.
            threads (int): The total number of logical threads on the system.
            arch (str, optional): The architecture type of the system.

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
        if arch is None:
            arch = "x86_64"

        shell_env = os.environ.copy()
        openmpi_dir = "{}/openmpi/build/bin".format(self.src_dir)
        bin_dir = "{}/bin/{}".format(self.hpl_dir, arch)
        bin_loc = bin_dir + "/xhpl"
        results = {"unit": "GFLOPS", "mathlib": self.mathlib}
        tmp_results = []

        if not os.path.isfile(bin_loc):
            text = 'Could not find HPL binaries at "{}".'.format(bin_loc)
            prettify.error_message(text)
            logging.error(text)
            return {"error": text}

        if not os.path.isdir(openmpi_dir):
            text = 'Could not find OpenMPI directory at "{}".'.format(openmpi_dir)
            prettify.error_message(text)
            logging.error(text)
            return {"error": text}

        grid = self.__grid(mpi_threads)
        nb_size = self.__nb_size(threads)

        mpi_cmd = "{}/mpirun -n {} --allow-run-as-root --mca mpi_paffinity_alone 1".format(
            openmpi_dir, mpi_threads
        )

        if threads == mpi_threads:
            mpi_cmd = "{}/mpirun -n {} --allow-run-as-root".format(
                openmpi_dir, mpi_threads
            )

        logging.info('Running LINPACK using "%s" arch.', arch)

        os.makedirs(self.results_dir, exist_ok=True)
        shutil.copyfile(self.hpl_dir + "/Make." + arch, self.results_dir)
        shutil.copyfile(self.hpl_dir + "/bin/{}/HPL.dat".format(arch), self.results_dir)

        cmd = mpi_cmd + " ./xhpl"

        self.commands.append("Run: " + cmd)

        optimize.prerun()
        time.sleep(10)

        output = execute.output(cmd, working_dir=bin_dir, environment=shell_env)

        file.write(self.results_dir + "/linpack_output.txt", output)

        result = grep.text(
            output, r"\s+{}\s+{}\s+{}\s+".format(nb_size, grid.P, grid.Q)
        )

        for line in result:
            # 7th word
            tmp = float(line.split()[6])
            tmp_results.append(tmp)

        if tmp_results:
            sorted_results = sorted(tmp_results)
            results["score"] = sorted_results[-1]

        logging.info("LINPACK results: %s", str(results))

        return results
