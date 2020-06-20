# -*- coding: utf-8 -*-
"""The detected processor information."""

import logging
import os
import re
import shutil

from ..utilities import execute
from ..utilities import file
from ..utilities import grep


def name():
    """The detected processor name.

    Example:
        >>> name()
        'Intel Core(TM) i7-7700 CPU'

    Returns:
        String: Processor name.
    """

    cpu_name = None

    try:
        if os.path.exists("/proc/cpuinfo"):
            cpu_name = grep.file("/proc/cpuinfo", r"^model name\s*:\s*")

        logging.debug("/proc/cpuinfo model name: %s", str(cpu_name))

        if cpu_name:
            cpu_name = " ".join(cpu_name[0].strip().split()[3:])
            return cpu_name

        if not shutil.which("lscpu"):
            return None

        lscpu_output = execute.output("lscpu")
        cpu_name = grep.text(lscpu_output, "Model name:")

        logging.debug("lscpu model name: %s", str(cpu_name))

        if not cpu_name:
            return None

        cpu_name = " ".join(cpu_name[0].strip().split()[2:])

        if cpu_name:
            return cpu_name

        cpu_name = grep.text(lscpu_output, "CPU:")
        cpu_name = " ".join(cpu_name[0].strip().split()[1:])
        return cpu_name
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def topology():
    """The processor topology.

    Examples:
        >>> topology()
        (4, 8, 1)

    Returns:
        A tuple of (cores, threads, sockets).

            cores (int): The number of physical processors.
            threads (int): The number of logical processors.
            sockets (int): The number of processor sockets.
    """

    cores = None
    sockets = None
    threads_per_core = None
    threads = None
    cores_per_processor = None

    try:
        if shutil.which("lscpu"):
            lscpu_output = execute.output("lscpu")
            sockets = grep.text(lscpu_output, "Socket")
            sockets = re.sub(r"Socket\(s\):\s*", "", sockets[0])
            sockets = int(sockets.strip())

            threads_per_core = grep.text(lscpu_output, r"Thread\(s\) per core:")
            threads_per_core = re.sub(
                r"Thread\(s\) per core:\s*", "", threads_per_core[0]
            )
            threads_per_core = int(threads_per_core.strip())

            cores_per_processor = grep.text(lscpu_output, r"Core\(s\) per socket:")
            cores_per_processor = re.sub(
                r"Core\(s\) per socket:\s*", "", cores_per_processor[0]
            )
            cores_per_processor = int(cores_per_processor.strip())

        if not sockets and shutil.which("dmidecode"):
            dmidecode_output = execute.output("dmidecode -t 4")

            sockets = len(grep.text(dmidecode_output, "Socket Designation"))

            total_threads = grep.text(dmidecode_output, r"Thread Count\:")
            total_threads = re.sub(r"Thread Count:", "", total_threads[0])
            total_threads = total_threads.strip().split()[0]
            total_threads = int(total_threads)

            cores_per_processor = grep.text(dmidecode_output, r"Core Count\:")
            cores_per_processor = re.sub(r"Core Count:\s*", "", cores_per_processor[0])
            cores_per_processor = cores_per_processor.strip().split()[0]
            cores_per_processor = int(cores_per_processor)

            threads_per_core = total_threads / cores_per_processor

        if not sockets:
            thread_siblings = (
                file.read("/sys/devices/system/cpu/cpu1/topology/thread_siblings_list")
                .strip()
                .split(",")
            )
            threads_per_core = 1

            if shutil.which("nproc"):
                total_threads = execute.output("nproc --all")
            elif os.path.isfile("/proc/cpuinfo"):
                total_threads = len(grep.file("/proc/cpuinfo", r"^processor"))
            else:
                total_threads = execute.output("getconf _NPROCESSORS_ONLN")

            total_threads = int(total_threads)

            if len(thread_siblings) > 1:
                threads_per_core = 2
            if total_threads:
                cores_per_processor = total_threads / threads_per_core

        if not sockets:
            raise Exception("The number of sockets was not found.")
        if not cores_per_processor:
            raise Exception("The number of cores per processor was not found.")
        if not threads_per_core:
            raise Exception("The number of threads per core was not found.")

        cores = sockets * cores_per_processor
        threads = threads_per_core * cores

        return cores, threads, sockets
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def numa_nodes():
    """The number of NUMA nodes.

    Example:
        >>> numa_nodes()
        1

    Returns:
        Integer: NUMA nodes.
    """

    nodes = None

    try:
        if shutil.which("numactl"):
            stdout = execute.output("numactl --hardware | grep -c cpus")
            if stdout:
                nodes = int(stdout.rstrip())
        if not nodes and shutil.which("dmesg"):
            stdout = execute.output(
                r'dmesg | grep -c "NUMA node\|No NUMA configuration found"'
            )
            if stdout:
                nodes = int(stdout.rstrip())
        return nodes
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def node_topology():
    """The arrangement of physical cores to logical cores.

    Example:
        >>> node_topology()
        ([0, 2], [1, 4])

    Returns:
        A tuple of (cores, threads, sockets).

            physical_cores (list): The physical core CPU IDs.
            logical_cores (list): The logical core CPU IDs.
    """
    physical_cores = None
    logical_cores = None

    try:
        stdout = execute.output("grep 'physical id' /proc/cpuinfo").strip()
        lines = stdout.split("\n")

        if not lines:
            return physical_cores, logical_cores

        physical_cores = []
        logical_cores = []

        for core_id, line in enumerate(lines, start=0):
            # e.g., "physical id\t: 0"
            core = line.split()[3]
            if int(core) % 2 == 0:
                physical_cores.append(str(core_id))
                continue
            logical_cores.append(str(core_id))

        return physical_cores, logical_cores
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def __cache_size_convert(size):
    """Helper function to convert cache size if necessary and typecast.

    Assumes that only 'K', 'M', or 'G' will be in the 'size' string.

    Example:
        >>>__cache_size_convert('32K')
        32
        >>>__cache_size_convert('8M')
        8192

    Args:
        size (str): The cache size output.

    Returns:
        Integer: The cache size in bytes.
    """
    try:
        if "K" in size:
            size = re.sub(r"[^0-9]", "", size)
            size = int(size)
            size = size * 1024
        elif "M" in size:
            size = re.sub(r"[^0-9]", "", size)
            size = int(size)
            size = size * 1024 * 1024
        elif "G" in size:
            size = re.sub(r"[^0-9]", "", size)
            size = int(size)
            size = size * 1024 * 1024 * 1024
        return int(size)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def cache():
    """Processor cache information.

    Example:
        >>> cache()
        (32768, 65536, 524288, 8388608)
        >>> # With no L3 cache
        >>> cache()
        (32768, 32768, 524288, None)

    Returns:
        A tuple of (level_one_instruction, level_one_data,
            level_two, level_three, cache_sum).

            level_one_instruction (int): L1 instruction cache in B.
            level_one_data (int): L1 data cache in B.
            level_two (int): L2 cache in B.
            level_three (int): L3 cache in B.
    """
    try:
        cache_loc = "/sys/devices/system/cpu/cpu0/cache"
        level_one_data_file = cache_loc + "/index0/size"
        level_one_instruction_file = cache_loc + "/index1/size"
        level_two_file = cache_loc + "/index2/size"
        level_three_file = cache_loc + "/index3/size"

        level_one_data = None
        level_one_instruction = None
        level_two = None
        level_three = None

        if shutil.which("lscpu"):
            lscpu_output = execute.output("lscpu")

            level_one_data_line = grep.text(lscpu_output, "L1d cache")
            if level_one_data_line:
                level_one_data = level_one_data_line[0].rstrip().split()[2]

            level_one_ins_line = grep.text(lscpu_output, "L1i cache")
            if level_one_ins_line:
                level_one_instruction = level_one_ins_line[0].rstrip()
                level_one_instruction = level_one_instruction.split()[2]

            level_two_line = grep.text(lscpu_output, "L2 cache")
            if level_two_line:
                level_two = level_two_line[0].rstrip().split()[2]

            level_three_line = grep.text(lscpu_output, "L3 cache")
            if level_three_line:
                level_three = level_three_line[0].rstrip().split()[2]

        if not level_one_data and os.path.isfile(level_one_data_file):
            if os.path.isfile(level_one_data_file):
                level_one_data = file.read(level_one_data_file)
            if os.path.isfile(level_one_instruction_file):
                level_one_instruction = file.read(level_one_instruction_file)
            if os.path.isfile(level_two_file):
                level_two = file.read(level_two_file)
            if os.path.isfile(level_three_file):
                level_three = file.read(level_three_file)

        level_one_data = __cache_size_convert(level_one_data)
        level_one_instruction = __cache_size_convert(level_one_instruction)
        level_two = __cache_size_convert(level_two)
        level_three = __cache_size_convert(level_three)

        return (level_one_instruction, level_one_data, level_two, level_three)
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)


def frequency():
    """The detected processor frequency.

    Example:
        >>> frequency()
        3200

    Returns:
        Integer: The processor frequency in MHz.
    """
    try:
        mhz_freq = None
        freq = None

        if shutil.which("dmidecode"):
            dmidecode_output = execute.output("dmidecode -t processor")
            dmidecode_output = grep.text(dmidecode_output, "Max Speed")
            if dmidecode_output:
                mhz_freq = dmidecode_output[0].strip().split()[2]
        elif shutil.which("lscpu"):
            lscpu_output = execute.output("lscpu")
            lscpu_output = grep.text(lscpu_output, "CPU max MHz:")
            if lscpu_output:
                mhz_freq = lscpu_output[0].strip().split()[3]
        elif os.path.isfile("/proc/cpuinfo"):
            cpuinfo_output = grep.file("/proc/cpuinfo", "cpu MHz")
            if cpuinfo_output:
                mhz_freq = cpuinfo_output[0].strip().split()[3]

        if "." in mhz_freq:
            freq = int(float(mhz_freq))
        elif mhz_freq and mhz_freq.isdigit():
            freq = int(mhz_freq)

        return freq
    except IOError as err:
        logging.error(err)
    except ValueError as err:
        logging.error(err)
    except TypeError as err:
        logging.error(err)
