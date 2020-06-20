#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup script for Server Performance Evaluation Tool.

Also installs included versions of third party libraries, if those libraries
are not already installed.
"""

import os
import sys

from setuptools import find_packages
from setuptools import setup

if sys.version_info < (3, 3):
    print("spet requires python3 version >= 3.3.", file=sys.stderr)
    sys.exit(1)

# Extra __version__ from VERSION instead of spet.version so pip doesn't
# import __init__.py and bump into dependencies that haven't been installed
# yet.
with open(os.path.join(os.path.dirname(__file__), "VERSION")) as VERSION:
    __version__ = VERSION.read().strip()

with open("README.rst", "rb") as f:
    LONG_DESC = f.read().decode("utf-8")

setup(
    name="spet",
    version=__version__,
    description="Server Performance Evaluation Tool",
    long_description=LONG_DESC,
    author="Ryan Spoone",
    url="https://www.github.com/ryanspoone/spet",
    install_requires=[],
    packages=find_packages("spet"),
    package_dir={"": "spet"},
    include_package_data=True,
    entry_points={"console_scripts": ["spet = spet.run:main"]},
    scripts=["run"],
    license="MIT",
    keywords=[
        "server performance evaluation tool",
        "spet",
        "test",
        "benchmark",
        "performance",
        "intel",
        "amd",
        "generic",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Benchmark",
    ],
)
