# -*- coding: utf-8 -*-
"""Overrides for system and benchmark information in SPET.

Attributes:
    OVERRIDES (namedtuple): Override values for system information.

Example:
    >>> OVERRIDES.processorName
    'Intel Core(TM) i7-7700'
"""

import collections

_overrides = collections.namedtuple(
    "OVERRIDES",
    [
        "processorName",
        "osName",
        "osVer",
        "gccVer",
        "archBits",
        "archType",
        "sockets",
        "cores",
        "threads",
        "memory",
        "cflags",
        "l1iCache",
        "l1dCache",
        "l2Cache",
        "l3Cache",
        "processorFrequency",
        "memoryFrequency",
        "streamArraySize",
        "numaNodes",
    ],
)

OVERRIDES = _overrides(
    # Set the processor's name
    # Type (String)
    # e.g., `"Intel Core(TM) i7-7700 CPU"`
    processorName=None,
    # Set the operating system's distribution name
    # Type (String)
    # e.g., `"openSUSE Leap"`
    osName=None,
    # Set the operating system's distribution version
    # Type (String)
    # e.g., `42.2`
    osVer=None,
    # Set the GNU Compiler version
    # Type (String)
    # e.g., `"5.2.0"`
    gccVer=None,
    # Set the system's architecture in 32 or 64-bit
    # Type (Integer)
    # e.g., `64`
    archBits=None,
    # Set the system's architecture type
    # Type (String)
    # e.g., `"x86_64"`
    archType=None,
    # Set the total number of sockets
    # Type (Integer)
    # e.g., `1`
    sockets=None,
    # Set the total number of cores
    # Type (Integer)
    # e.g., `4`
    cores=None,
    # Set the total number of threads
    # Type (Integer)
    # e.g., `4`
    threads=None,
    # Set the system's total RAM in GB
    # Type (Integer)
    # e.g., `64`
    memory=None,
    # Set used CFLAGS
    # NOTE: Include the whole flag
    # Type (String)
    # e.g., `"-Ofast -march=broadwell -mtune=generic"`
    cflags=None,
    # Set the level 1 instruction cache size in B
    # Type (Integer)
    # e.g., `32768`
    l1iCache=None,
    # Set the level 1 data cache size in B
    # Type (Integer)
    # e.g., `32768`
    l1dCache=None,
    # Set the level 2 cache size in B
    # Type (Integer)
    # e.g., `262144`
    l2Cache=None,
    # Set the level 3 cache size in B
    # Type (Integer)
    # e.g., `8388608`
    l3Cache=None,
    # Set the processor frequency in MHz
    # Type (Integer)
    # e.g., `3200` for 3.2 GHz
    processorFrequency=None,
    # Set the memory frequency in MHz
    # Type (Integer)
    # e.g., `1333`
    memoryFrequency=None,
    # Set the STREAM OMP array size
    # Type (Integer)
    # e.g., `15252014`
    streamArraySize=None,
    # Set the number of NUMA nodes
    # Type (Integer)
    # e.g., `8`
    numaNodes=None,
)
