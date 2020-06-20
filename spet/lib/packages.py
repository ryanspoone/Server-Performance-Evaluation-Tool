# -*- coding: utf-8 -*-
"""Packages to be installed by the system package manager."""

ZYPPER = (
    "gawk",
    "coreutils",
    "-t pattern devel_basis",
    "gcc",
    "gcc-fortran",
    "util-linux",
    "R-base",
    "bc",
    "lshw",
    "numactl",
    "java",
    "libaio",
    "python",
)

YUM = (
    "epel-release",
    "gawk",
    "coreutils",
    "gcc",
    "gcc-gfortran",
    "util-linux",
    "R",
    "R-littler",
    "bc",
    "lshw",
    "numactl",
    "java-sdk",
    "libaio",
    "python",
)

APT = (
    "coreutils",
    "build-essential",
    "gcc",
    "gfortran",
    "util-linux",
    "r-base",
    "littler",
    "bc",
    "lshw",
    "numactl",
    "default-jdk",
    "libaio1",
    "python",
)

UNKNOWN = (
    "coreutils",
    '"make" and other development tools for building packages',
    "gcc",
    "gfortran",
    "util-linux",
    '"littler" package for R',
    "bc",
    "lshw",
    "numactl",
    "java-jdk",
    "libaio",
    "python2",
)
