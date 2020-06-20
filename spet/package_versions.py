# -*- coding: utf-8 -*-
"""Package versions used by SPET.

Modify these values to update your tested versions.

Attributes:
    PACKAGE_VERSIONS (namedtuple): Package versions.

Example:
    >>> PACKAGE_VERSIONS.mlc
    '3.4'
"""

import collections

_packages = collections.namedtuple(
    "VERSIONS",
    [
        "lmbench",
        "mlc",
        "openmpi",
        "glibc",
        "openssl",
        "linpack",
        "stream",
        "openblas",
        "linux",
        "zlib",
        "cassandra",
        "ycsb",
        "mysql",
        "mysql_glibc",
        "maven",
        "mkl",
        "mkl_url",
        "blis",
        "jconnect",
        "docker",
    ],
)

PACKAGE_VERSIONS = _packages(
    # Check http://www.bitmover.com/lmbench/get_lmbench.html for the latest
    # LMbench version
    lmbench="3",
    # Check
    # https://software.intel.com/en-us/articles/intelr-memory-latency-checker
    # for the latest MLC version
    mlc="3.4",
    # Check http://www.open-mpi.org/software for the latest Open MPI version
    openmpi="3.0.0",
    # Check https://ftp.gnu.org/gnu/glibc/ for the latest glibc version
    glibc="2.26",
    # Check https://www.openssl.org/source/ for the latest OpenSSL version
    openssl="1.1.0g",
    # Check http://www.netlib.org/benchmark/hpl/ for the latest High-
    # Performance Linpack version
    linpack="2.2",
    # Check https://www.cs.virginia.edu/stream/FTP/Code/stream.c
    # for the latest STREAM OMP version
    stream="5.10",
    # Check http://www.openblas.net/ for the latest OpenBLAS version
    openblas="0.2.20",
    # Check http://www.kernel.org/pub/linux/kernel/ for the latest Linux kernel
    linux="4.14.4",
    # Check https://zlib.net/ for the latest zlib version
    zlib="1.2.11",
    # Check http://cassandra.apache.org/download/ for the latest Cassandra
    # version
    cassandra="3.11.1",
    # Check https://github.com/brianfrankcooper/YCSB/releases for the latest
    # YCSB version
    ycsb="0.12.0",
    # Check https://maven.apache.org/download.cgi for the latest Maven version
    maven="3.5.2",
    # Check https://dev.mysql.com/downloads/mysql/ for the latest MySQL version
    mysql="5.7.20",
    mysql_glibc="2.12",
    # Check https://software.intel.com/en-us/mkl for the latest MKL version
    mkl="2018.0.128",
    mkl_url="http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/12070/l_mkl_2018.0.128.tgz",
    # Check http://developer.amd.com/amd-cpu-libraries/blas-library/ for the
    # latest BLIS version
    blis="0.9-11-Beta",
    # Check https://dev.mysql.com/downloads/connector/j/ for the latest MySQL
    # J Connector version
    jconnect="5.1.44",
    # Check https://download.docker.com/linux/static/stable/x86_64/ for the
    # latest stable version of Docker
    docker="17.09.1",
)
