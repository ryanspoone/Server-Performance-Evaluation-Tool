# -*- coding: utf-8 -*-
"""Used for optimizing the system for performance tests."""

import logging
import os
import re
import shutil

import resource

from . import execute
from . import grep
from . import file


def performance_governor():
    """Sets the CPU scaling governor to performance."""
    cpu_root = "/sys/devices/system/cpu/"

    try:
        if not os.path.isdir(cpu_root):
            return False
        pattern = r"cpu[0-9]"
        for cpu in next(os.walk(cpu_root))[1]:
            if not re.match(pattern, cpu):
                continue
            governor = cpu_root + cpu + "/cpufreq/scaling_governor"
            if os.path.isfile(governor):
                file.write(governor, "performance")
        return True
    except IOError as err:
        logging.debug(err)


def disable_hugepages():
    """Disables transparent hugepages."""
    transparent_hugepage = "/sys/kernel/mm/transparent_hugepage/enabled"

    try:
        if os.path.isfile(transparent_hugepage):
            file.write(transparent_hugepage, "never")
            return True
        return False
    except IOError as err:
        logging.debug(err)


def disable_swap():
    """Disable swap."""
    try:
        if shutil.which("swapoff"):
            execute.output("sudo swapoff -a")
            return True
        return False
    except IOError as err:
        logging.debug(err)


def prerun():
    """Clear up system resources before running a benchmark."""
    try:
        cleared = False
        if shutil.which("sync"):
            execute.output("sudo sync")
            cleared = True
        drop_caches = "/proc/sys/vm/drop_caches"
        if os.path.isfile(drop_caches):
            file.write(drop_caches, "3")
            cleared = True
        return cleared
    except ValueError as err:
        logging.debug(err)
    except IOError as err:
        logging.debug(err)


def ulimit():
    """Sets the `ulimit` values for this and child processes."""
    try:
        # The maximum size (in bytes) of the call stack for the current
        # process. This only affects the stack of the main thread in a
        # multi-threaded process.
        # `ulimit -s unlimited`
        resource.setrlimit(
            resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        )
        # The maximum number of open file descriptors for the current process.
        # `ulimit -n 1048576`
        resource.setrlimit(resource.RLIMIT_NOFILE, (1048576, 1048576))
        # The maximum number of user processes for the current process.
        # `ulimit -u unlimited`
        resource.setrlimit(
            resource.RLIMIT_NPROC, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        )
        return True
    except ValueError as err:
        logging.debug(err)


def nofiles():
    """Sets the number of files limit."""
    limits_conf = "/etc/security/limits.conf"
    sysctl_conf = "/etc/sysctl.conf"
    try:
        if os.path.isfile(limits_conf):
            lines = grep.file(limits_conf, "nofile 1048576")
            if not lines:
                file.write(limits_conf, "* - nofile 1048576", append=True)
        if os.path.isfile(sysctl_conf):
            lines = grep.file(sysctl_conf, "fs.file-max = 1048576")
            if not lines:
                file.write(sysctl_conf, "fs.file-max = 1048576", append=True)
            if shutil.which("sysctl"):
                execute.output("sudo sysctl -p")
        return True
    except ValueError as err:
        logging.debug(err)
    except IOError as err:
        logging.debug(err)
