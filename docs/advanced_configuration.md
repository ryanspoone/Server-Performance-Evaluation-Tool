# Advanced Configuration

## Overriding Package Versions

You can override the default package versions in the
`spet/package_versions.py` file.

### Package Options

| Option                    | Description                                                                                                                                                                                                                                                           |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lmbench`                 | Cache latency performance test. Check [LMbench](http://www.bitmover.com/lmbench/get_lmbench.html) for the latest version.                                                                                                                                             |
| `mlc`                     | Memory latency performance test. Check [MLC](https://software.intel.com/en-us/articles/intelr-memory-latency-checker) for the latest version. NOTE: This package is provided, so you will need to add it manually to the `spet/src` directory.                        |
| `openmpi`                 | Prerequisite for LINPACK and STREAM. Check [Open MPI](http://www.open-mpi.org/software) for the latest version.                                                                                                                                                       |
| `glibc`                   | C library prerequisite for OpenSSL. Check [glibc](https://ftp.gnu.org/gnu/glibc/) for the latest version.                                                                                                                                                             |
| `openssl`                 | Cryptography performance test. Check [OpenSSL](https://www.openssl.org/source/) for the latest version.                                                                                                                                                               |
| `linpack`                 | Floating-point and math performance test. Check [HPL](http://www.netlib.org/benchmark/hpl/) for the latest version.                                                                                                                                                   |
| `stream`                  | Memory bandwidth performance test. Check [STREAM](https://www.cs.virginia.edu/stream/FTP/Code/stream.c) for the latest version.                                                                                                                                       |
| `openblas`                | Default math library for LINPACK. Check [OpenBLAS](http://www.openblas.net/) for the latest version.                                                                                                                                                                  |
| `linux`                   | Linux kernel source for compilation performance test. Check [Linux](http://www.kernel.org/pub/linux/kernel/) for the latest version.                                                                                                                                  |
| `zlib`                    | Compression library for the compression and decompression performance test. Check [zlib](https://zlib.net/) for the latest version.                                                                                                                                   |
| `cassandra`               | NoSQL database for the NoSQL performance test. Check [Cassandra](http://cassandra.apache.org/download/) for the latest version.                                                                                                                                       |
| `ycsb`                    | NoSQL and SQL performance tests. Check [YCSB](https://github.com/brianfrankcooper/YCSB/releases) for the latest version.                                                                                                                                              |
| `maven`                   | Prerequisite for YCSB. Check [Maven](https://maven.apache.org/download.cgi) for the latest version.                                                                                                                                                                   |
| `mysql` and `mysql_glibc` | SQL database for the SQL performance test. Check [MySQL](https://dev.mysql.com/downloads/mysql) for the latest version.                                                                                                                                               |
| `mkl` and `mkl_url`       | Intel processor math library for LINPACK. Check [MKL](https://software.intel.com/en-us/mkl) for the latest version. NOTE: This package is provided, so you will need to add it manually to the `spet/src` directory. In addtion, the `mkl_url` is currently not used. |
| `blis`                    | AMD processor math library for LINPACK. Check [AMD BLIS](http://developer.amd.com/amd-cpu-libraries/blas-library/) for the latest version. NOTE: This is provided, so you will need to add it manually to the `spet/src` directory.                                   |
| `jconnect`                | Connector for MySQL and YCSB. Check [Connector/J](https://dev.mysql.com/downloads/connector/j/) for the latest version.                                                                                                                                               |
| `docker`                  | Container software for the container performance test. Check [Docker](https://download.docker.com/linux/static/stable/x86_64/) for the latest version.                                                                                                                |

> \* Copyright (C) 2017, Advanced Micro Devices, Inc.
>
> \* Copyright (C) 2014, The University of Texas at Austin

## Overriding System Information

You can override the default package versions in the `spet/overrides.py`
file.

### System Options

| Option             | Description                                                                    | Type    |
| ------------------ | ------------------------------------------------------------------------------ | ------- |
| processorName      | Set the processor's name.                                                      | String  |
| osName             | Set the Operating System's distribution name.                                  | String  |
| osVer              | Set the Operating System's distribution version.                               | String  |
| gccVer             | Set the GNU Compiler version.                                                  | String  |
| archBits           | Set the system's architecture to 32- or 64-bit                                 | Integer |
| archType           | Set the system's architecture type.                                            | String  |
| sockets            | Set the system's total number of sockets.                                      | Integer |
| cores              | Set the system's total number of cores.                                        | Integer |
| threads            | Set the system's total number of threads.                                      | Integer |
| memory             | Set the system's total RAM in GB.                                              | Integer |
| cflags             | Set the CFLAGS to be used while compiling with GCC.                            | String  |
| l1iCache           | Set the L1 Instruction Cache size in bytes.                                    | Integer |
| l1dCache           | Set the L1 Data Cache size in bytes.                                           | Integer |
| l2Cache            | Set the L2-Cache size in bytes.                                                | Integer |
| l3Cache            | Set the L3-Cache size in bytes.                                                | Integer |
| processorFrequency | Set the processor frequency in MHz (this is currently not used).               | Integer |
| memoryFrequency    | Set the memory frequency in MHz                                                | Integer |
| streamArraySize    | Set the STREAM array size to be used by the memory bandwidth performance test. | Integer |
| numaNodes          | Set the number of NUMA nodes on the system.                                    | Integer |
