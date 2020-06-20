#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Server Performance Evaluation Tool.

Linux command-line application that simplifies building and running multiple
free to use benchmark tests. Results are stored in the `$HOME` directory.
"""

import logging
import logging.config
import os
import shutil
import sys
import signal

from . import version
from . import package_versions
from .lib import options
from .lib import packages
from .lib import result_file
from .lib.benchmarks import compilation
from .lib.benchmarks import docker
from .lib.benchmarks import linpack
from .lib.benchmarks import lmbench
from .lib.benchmarks import mlc
from .lib.benchmarks import openssl
from .lib.benchmarks import stream
from .lib.benchmarks import ycsb
from .lib.benchmarks import zlib
from .lib.prerequisites import blis
from .lib.prerequisites import cassandra
from .lib.prerequisites import glibc
from .lib.prerequisites import maven
from .lib.prerequisites import mkl
from .lib.prerequisites import mysql
from .lib.prerequisites import openblas
from .lib.prerequisites import openmpi
from .lib.prerequisites import package_manager
from .lib.system import complete
from .lib.system import processor
from .lib.tables import results as results_table
from .lib.tables import system
from .lib.tables import commands as commands_table
from .lib.tables import packages as packages_table
from .lib.utilities import access
from .lib.utilities import file
from .lib.utilities import json_file
from .lib.utilities import optimize
from .lib.utilities import prettify
from .lib.utilities import run_num
from .lib.utilities import uglify

__author__ = "ryanspoone@gmail.com (Ryan Spoone)"


def package_manger_installations():
    """Install all prerequisites from the system package manager."""
    if shutil.which("zypper"):
        package_manager.zypper(packages.ZYPPER)
    elif shutil.which("yum"):
        package_manager.yum(packages.YUM)
    elif shutil.which("apt-get"):
        package_manager.apt_get(packages.APT)
    elif shutil.which("aptitude"):
        package_manager.aptitude(packages.APT)
    elif shutil.which("apt"):
        package_manager.apt(packages.APT)
    else:
        package_manager.unknown(packages.UNKNOWN)


def install_prerequisites(root_dir, system_info, opts):
    """Install all from source prerequisites.

    Args:
        root_dir (str): The directory containing `src/`.
        system_info (dict): All known system information.
        opts (list): All flag options passed to this module.
    """
    versions = package_versions.PACKAGE_VERSIONS

    # OpenMPI
    mpi = openmpi.OpenMPI(versions.openmpi, root_dir)

    download_success = mpi.download()
    if not download_success:
        prettify.error_message("OpenMPI failed to download.")

    extract_success = mpi.extract()
    if not extract_success:
        prettify.error_message("OpenMPI failed to extract.")

    build_success = mpi.build(cores=system_info.cores, cflags=system_info.cflags)
    if not build_success:
        prettify.error_message("OpenMPI failed to compile.")

    install_success = mpi.install(cores=system_info.cores)
    if not install_success:
        prettify.error_message("OpenMPI failed to install.")

    # Math libraries
    if "intel" in system_info.processorName.lower():
        intel = mkl.MKL(versions.mkl, root_dir)

        download_success = intel.download()
        if not download_success:
            prettify.error_message("MKL failed to download.")

        extract_success = intel.extract()
        if not extract_success:
            prettify.error_message("MKL failed to extract.")

        install_success = intel.install()
        if not install_success:
            prettify.error_message("MKL failed to install.")
    elif "amd" in system_info.processorName.lower():
        amd = blis.BLIS(versions.blis, root_dir)

        download_success = amd.download()
        if not download_success:
            prettify.error_message("BLIS failed to download.")

        extract_success = amd.extract()
        if not extract_success:
            prettify.error_message("BLIS failed to extract.")
    else:
        blas = openblas.OpenBLAS(versions.openblas, root_dir)

        download_success = blas.download()
        if not download_success:
            prettify.error_message("OpenBLAS failed to download.")

        extract_success = blas.extract()
        if not extract_success:
            prettify.error_message("OpenBLAS failed to extract.")

        build_success = blas.build(
            system_info.threads,
            cores=system_info.cores,
            cflags=system_info.cflags,
            avx512=opts.avx512,
        )
        if not build_success:
            prettify.error_message("OpenBLAS failed to compile.")

    # Glibc
    libc = glibc.GLibC(versions.glibc, root_dir)

    download_success = libc.download()
    if not download_success:
        prettify.error_message("Glibc failed to download.")

    extract_success = libc.extract()
    if not extract_success:
        prettify.error_message("Glibc failed to extract.")

    build_success = libc.build(cores=system_info.cores, cflags=system_info.cflags)
    if not build_success:
        prettify.error_message("Glibc failed to compile.")

    install_success = libc.install(cores=system_info.cores)
    if not install_success:
        prettify.error_message("Glibc failed to install.")

    # Maven
    mvn = maven.Maven(versions.maven, root_dir)

    download_success = mvn.download()
    if not download_success:
        prettify.error_message("Maven failed to download.")

    extract_success = mvn.extract()
    if not extract_success:
        prettify.error_message("Maven failed to extract.")

    # MySQL
    sql = mysql.MySQL(versions.mysql, versions.mysql_glibc, root_dir)

    download_success = sql.download()
    if not download_success:
        prettify.error_message("MySQL failed to download.")

    extract_success = sql.extract()
    if not extract_success:
        prettify.error_message("MySQL failed to extract.")

    setup_success = sql.setup()
    if not setup_success:
        prettify.error_message("MySQL failed to setup.")

    # Cassandra
    nosql = cassandra.Cassandra(versions.cassandra, root_dir)

    download_success = nosql.download()
    if not download_success:
        prettify.error_message("Cassandra failed to download.")

    extract_success = nosql.extract()
    if not extract_success:
        prettify.error_message("Cassandra failed to extract.")


def benchmarks(root_dir, results_dir, system_info, opts):
    """Compile and setup all benchmarks.

    Args:
        root_dir (str): The directory containing `src/`.
        results_dir (str): The SPET run's result directory.
        system_info (dict): All known system information.
        opts (list): All flag options passed to this module.

    Returns:
        Dict: All results.
    """
    versions = package_versions.PACKAGE_VERSIONS
    results = {}
    commands = {}

    if system_info.l3Cache is not None:
        cache = system_info.l3Cache
    elif system_info.l2Cache is not None:
        cache = system_info.l2Cache
    else:
        cache = system_info.l1dCache

    mem_lat_rd = lmbench.LMbench(versions.lmbench, root_dir, results_dir)
    crypto = openssl.OpenSSL(versions.openssl, root_dir, results_dir)
    node_lat = mlc.MemoryLatencyChecker(versions.mlc, root_dir, results_dir)
    kernel = compilation.CompilationSpeed(versions.linux, root_dir, results_dir)
    compression = zlib.Zlib(versions.zlib, root_dir, results_dir)
    hpl = linpack.Linpack(versions.linpack, root_dir, results_dir)
    stream_omp = stream.STREAM(versions.stream, root_dir, results_dir)
    nosql = ycsb.NoSQL(versions.ycsb, root_dir, results_dir)
    sql = ycsb.SQL(versions.ycsb, versions.jconnect, root_dir, results_dir)
    containers = docker.Docker(versions.docker, root_dir, results_dir)

    # Setup
    logging.warning("Setting up and compiling benchmarks...")

    if opts.excludes is None or "lmbench" not in opts.excludes:
        mem_lat_rd.download()
        mem_lat_rd.extract()
        mem_lat_rd.build(
            arch=system_info.archType,
            cores=system_info.cores,
            cflags=system_info.cflags,
        )

    if opts.excludes is None or "mlc" not in opts.excludes:
        node_lat.extract()

    if opts.excludes is None or "openssl" not in opts.excludes:
        crypto.download()
        crypto.extract()
        crypto.build(versions.glibc, cores=system_info.cores, cflags=system_info.cflags)

    if opts.excludes is None or "compilation" not in opts.excludes:
        kernel.download()
        kernel.extract()
        kernel.setup(cores=system_info.cores, cflags=system_info.cflags)

    if opts.excludes is None or "zlib" not in opts.excludes:
        compression.download()
        compression.extract()
        compression.build(system_info.cores, cflags=system_info.cflags)

    if opts.excludes is None or "linpack" not in opts.excludes:
        hpl.download()
        hpl.extract()
        hpl.edit_makefile(
            system_info.processorName,
            arch=system_info.archType,
            cflags=system_info.cflags,
            avx512=opts.avx512,
        )
        hpl.build(
            system_info.threads,
            arch=system_info.archType,
            cores=system_info.cores,
            cflags=system_info.cflags,
            avx512=opts.avx512,
        )
        hpl.edit_datfile(
            system_info.memory,
            system_info.cores,
            system_info.threads,
            arch=system_info.archType,
        )

    if opts.excludes is None or "stream" not in opts.excludes:
        stream_omp.download()
        stream_omp.build(
            cache,
            sockets=system_info.sockets,
            cflags=system_info.cflags,
            stream_array_size=system_info.streamArraySize,
        )

    if opts.excludes is None or "nosql" not in opts.excludes:
        nosql.download()
        nosql.extract()
        nosql.setup(system_info.threads)

    if opts.excludes is None or "sql" not in opts.excludes:
        sql.download()
        sql.extract()
        sql.setup(system_info.threads)

    if opts.excludes is None or "docker" not in opts.excludes:
        containers.download()
        containers.extract()
        containers.build(
            versions.linux, cores=system_info.cores, cflags=system_info.cflags
        )

    logging.warning("Done setting up and compiling benchmarks.")

    # Running

    logging.warning("Running benchmarks...")

    if opts.excludes is None or "lmbench" not in opts.excludes:
        results["LMbench"] = mem_lat_rd.run(
            system_info.l1dCache,
            system_info.l2Cache,
            system_info.l3Cache,
            arch=system_info.archType,
            threads=system_info.threads,
        )
        commands["LMbench"] = mem_lat_rd.commands
    else:
        results["LMbench"] = {"skipped": True}

    logging.warning("\n")
    logging.warning("System Performance Results".center(79))
    logging.warning("==========================".center(79))
    logging.warning(results_table.lmbench(results["LMbench"]))

    if opts.excludes is None or "mlc" not in opts.excludes:
        results["MLC"] = node_lat.run()
        commands["MLC"] = node_lat.commands
    else:
        results["MLC"] = {"skipped": True}

    logging.warning(results_table.mlc(results["MLC"]))

    if opts.excludes is None or "openssl" not in opts.excludes:
        results["OpenSSL"] = crypto.run(system_info.threads)
        commands["OpenSSL"] = crypto.commands
    else:
        results["OpenSSL"] = {"skipped": True}

    logging.warning(results_table.openssl(results["OpenSSL"]))

    if opts.excludes is None or "compilation" not in opts.excludes:
        results["Timed Kernel Compilation"] = kernel.run(
            cores=system_info.cores, cflags=system_info.cflags
        )
        commands["Timed Kernel Compilation"] = kernel.commands
    else:
        results["Timed Kernel Compilation"] = {"skipped": True}

    logging.warning(results_table.compilation(results["Timed Kernel Compilation"]))

    if opts.excludes is None or "zlib" not in opts.excludes:
        results["zlib"] = compression.run()
        commands["zlib"] = compression.commands
    else:
        results["zlib"] = {"skipped": True}

    logging.warning(results_table.zlib(results["zlib"]))

    if opts.excludes is None or "linpack" not in opts.excludes:
        results["High-Performance Linpack"] = hpl.run(
            system_info.cores, system_info.threads, arch=system_info.archType
        )
        commands["High-Performance Linpack"] = hpl.commands
    else:
        results["High-Performance Linpack"] = {"skipped": True}

    logging.warning(results_table.linpack(results["High-Performance Linpack"]))

    if opts.excludes is None or "stream" not in opts.excludes:
        results["STREAM"] = stream_omp.run(system_info.threads)
        commands["STREAM"] = stream_omp.commands
    else:
        results["STREAM"] = {"skipped": True}

    logging.warning(results_table.stream(results["STREAM"]))

    if opts.excludes is None or "nosql" not in opts.excludes:
        results["YCSB NoSQL"] = nosql.run(system_info.threads)
        commands["YCSB NoSQL"] = nosql.commands
    else:
        results["YCSB NoSQL"] = {"skipped": True}

    logging.warning(results_table.nosql(results["YCSB NoSQL"]))

    if opts.excludes is None or "sql" not in opts.excludes:
        results["YCSB SQL"] = sql.run(system_info.threads)
        commands["YCSB SQL"] = sql.commands
    else:
        results["YCSB SQL"] = {"skipped": True}

    logging.warning(results_table.sql(results["YCSB SQL"]))

    if opts.excludes is None or "docker" not in opts.excludes:
        results["Docker"] = containers.run(
            cores=system_info.cores, cflags=system_info.cflags
        )
        commands["Docker"] = containers.commands
    else:
        results["Docker"] = {"skipped": True}

    logging.warning(results_table.docker(results["Docker"]))

    logging.warning("Done running benchmarks.")

    return results, commands


def main():
    """Main function for running SPET."""
    versions = package_versions.PACKAGE_VERSIONS
    flags = options.Options()
    opts = flags.parse(sys.argv[1:])
    spet_ver = version.VERSION
    processor_name = processor.name()
    root_dir = os.path.dirname(os.path.realpath(__file__))
    home_dir = os.path.expanduser("~")
    if not home_dir:
        home_dir = root_dir

    results_dir = home_dir + "/spet_results"
    os.makedirs(results_dir, exist_ok=True)

    # SPET run number
    run_file = results_dir + "/.SPET.lock"
    run_num.write(run_file)
    nrun = run_num.read(run_file)

    results_file_starter = "SPET.{}.{}".format(nrun, uglify.filename(processor_name))

    run_dir = "{}/{}".format(results_dir, results_file_starter)

    # SPET result files
    results_json = "{}/{}.results.json".format(run_dir, results_file_starter)
    results_file = "{}/{}.results.txt".format(run_dir, results_file_starter)
    debug_file = "{}/{}.debug.log".format(run_dir, results_file_starter)
    log_file = "{}/{}.log".format(run_dir, results_file_starter)

    os.makedirs(run_dir, exist_ok=True)

    # Setup logging
    debug_format = "%(lineno)d in %(filename)s at %(asctime)s: %(message)s"
    log_config = {
        "version": 1,
        "formatters": {
            "info": {"user": "%(message)s"},
            "debug": {"format": debug_format},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "info",
                "level": opts.loglevel or logging.WARNING,
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": debug_file,
                "formatter": "debug",
                "level": logging.DEBUG,
            },
            "consolefile": {
                "class": "logging.FileHandler",
                "filename": log_file,
                "formatter": "info",
                "level": opts.loglevel or logging.WARNING,
            },
        },
        "root": {"handlers": ("console", "file", "consolefile"), "level": "DEBUG"},
    }
    logging.config.dictConfig(log_config)

    logging.warning("Server Performance Evaluation Tool (%s)", spet_ver)

    logging.debug("SPET options: %s", opts)
    logging.debug("Root directory for SPET: %s", root_dir)
    logging.debug("Run number lock file: %s", run_file)
    logging.debug("Run number: %s", nrun)
    logging.debug("Results directory: %s", results_dir)
    logging.debug("Run directory: %s", run_dir)
    logging.debug("Results file beginning: %s", results_file_starter)

    if not access.is_root():
        sys.exit(
            prettify.error_message(
                "You do not have root access. Please restart SPET once "
                "you have the proper access. Exiting now."
            )
        )

    if opts.excludes:
        logging.debug("Benchmark exclusions: %s", str(opts.excludes))

    logging.warning("\nInstalling prerequisites from the system's package " "manager.")
    package_manger_installations()
    logging.warning(
        "Done installing prerequisites from the system's package " "manager.\n"
    )

    system_info = complete.system_information()
    logging.debug("system_info: %s", str(system_info))

    logging.warning("\n")
    logging.warning(system.table(system_info, avx512=opts.avx512))

    # Optimizations
    optimize.performance_governor()
    optimize.disable_hugepages()
    optimize.disable_swap()
    optimize.ulimit()
    optimize.nofiles()

    logging.warning("Setting up and compiling prerequisites...")
    install_prerequisites(root_dir, system_info, opts)
    logging.warning("Done setting up and compiling prerequisites.")

    results, commands = benchmarks(root_dir, run_dir, system_info, opts)
    logging.warning("\n")

    # Create results JSON
    json_file.write(results_json, results)

    # Create results file
    file.write(results_file, result_file.header(spet_ver))
    file.write(results_file, results_table.table(results), append=True)
    file.write(results_file, "\n", append=True)
    file.write(results_file, system.table(system_info), append=True)
    file.write(results_file, commands_table.formatted(commands), append=True)
    file.write(
        results_file, packages_table.table(versions, processor_name), append=True
    )
    file.write(results_file, result_file.footer(), append=True)

    # Output file locations for logs, json, and text file.
    print("File Locations".center(79))
    print("==============".center(79))
    print(results_file)
    print(results_json)
    print(log_file)
    print(debug_file)
    print("\n")


def keyboard_interrupt_handler():
    """Allow CTRL+C interrupts to exit gracefully."""

    print("KeyboardInterrupt has been caught. Exiting now...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    sys.exit(main())
