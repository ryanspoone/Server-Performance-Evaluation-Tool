# -*- coding: utf-8 -*-
"""Wrapper module for gathering all system information."""

import collections
import logging
import os
import sys

from spet import overrides
from spet.lib.system import gcc
from spet.lib.system import java
from spet.lib.system import memory
from spet.lib.system import operating_system
from spet.lib.system import processor

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


def system_information():
    """Replaces incomplete override information with detected information.

    Returns:
        Named Tuple: All known system information.
            processorName (str): Processor name.
            osName (str): Operating system name.
            osVer (str): Operating system version.
            gccVer (str): GCC version.
            archBits (int): 32-bit or 64-bit architecture.
            archType (str): Machine architecture type.
            sockets (int): Total sockets.
            cores (int): Total cores.
            threads (int): Total threads.
            memory (int): Total RAM in GB.
            cflags (str): The CFLAGS for GCC.
            javaVer (str): The system default Java version.
            l1iCache (int): L1 instruction cache size in bytes.
            l1dCache (int): L1 data cache size in bytes.
            l2Cache (int): L2 cache size in bytes.
            l3Cache (int): L3 cache size in bytes.
            processorFrequency (int): Processor frequency in MHz.
            memoryFrequency (int): RAM frequency in MHz.
            streamArraySize (int): The override size for STREAM's array.
            numaNodes (int): Total NUMA nodes.
    """
    try:
        _overrides = overrides.OVERRIDES
        options = [
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
            "javaVer",
            "l1iCache",
            "l1dCache",
            "l2Cache",
            "l3Cache",
            "processorFrequency",
            "memoryFrequency",
            "streamArraySize",
            "numaNodes",
        ]

        named_info = collections.namedtuple("system_info", options)
        system_info = named_info(
            processorName=(_overrides.processorName or processor.name()),
            osName=_overrides.osName or operating_system.distribution()[0],
            osVer=_overrides.osVer or operating_system.distribution()[1],
            gccVer=_overrides.gccVer or gcc.version(),
            archBits=_overrides.archBits or operating_system.architecture()[0],
            archType=_overrides.archType or operating_system.architecture()[1],
            sockets=_overrides.sockets or processor.topology()[2],
            cores=_overrides.cores or processor.topology()[0],
            threads=_overrides.threads or processor.topology()[1],
            memory=_overrides.memory or memory.total(),
            cflags=_overrides.cflags or gcc.flags(),
            javaVer=java.version(),
            l1iCache=_overrides.l1iCache or processor.cache()[0],
            l1dCache=_overrides.l1dCache or processor.cache()[1],
            l2Cache=_overrides.l2Cache or processor.cache()[2],
            l3Cache=_overrides.l3Cache or processor.cache()[3],
            processorFrequency=(_overrides.processorFrequency or
                                processor.frequency()),
            memoryFrequency=(_overrides.memoryFrequency or memory.frequency()),
            streamArraySize=_overrides.streamArraySize,
            numaNodes=_overrides.numaNodes or processor.numa_nodes(),
        )

        return system_info
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)
