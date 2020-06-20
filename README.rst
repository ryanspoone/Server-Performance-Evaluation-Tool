==================================
Server Performance Evaluation Tool
==================================

Server Performance Evaluation Tool allows you to easily test the performance of
x86_64 processors on Linux.

.. contents::
   :depth: 3
   :backlinks: top
   :local:

********
Features
********

+ Automatically install system prerequisites using the operating system's
  package manager.
+ Automatic detection of system information.
+ Automatic downloading, setting up, and running of all performance tests.
+ Overriding available for general tuning of tests and changing test versions.
+ Results in JSON and text form.
+ All major commands documented in the results text file.

***************
Getting Started
***************

Requirements
============

1. x86_64 system
2. Linux (Ubuntu, Debian, CentOS, openSUSE) Operating System
      + Mostly tested on Ubuntu
3. Root access
4. Python 3

Setup
=====

.. code-block:: bash

    # Install `python3`
    apt-get install python3
    # or `yum install python3`
    # or `zypper install python3`

    # Change into the Server Performance Evaluation Tool root directory

    # You may need to allow `run` to be executable
    chmod +x run

Run
===

Once everything is set up, you can simply run Server Performance Evaluation
Tool by executing the ``run`` file:

**Note: You need root access to run Server Performance Evaluation Tool.**

.. code-block:: bash

    # In the Server Performance Evaluation Tool root directory
    sudo ./run

If for some reason, the run file does not work, you can call Server Performance
Evaluation Tool by doing the following within the same directory:

.. code-block:: bash

    python3 spet/
    # or `cd spet`
    # and `sudo python3 main.py`

Results
=======

Results will be outputted to the console (stdout) as they are gathered.
All result files will be located in ``$HOME/spet_results`` under your specific
run's directory.

If ``$HOME`` was not detected for whatever reason, the result files will be
located in the Server Performance Evaluation Tool's ``spet/spet_results``
directory.

Additional Options
==================

+-------------+--------------------+------------------------------------------+
| Option      | GNU long option    | Meaning                                  |
+=============+====================+==========================================+
| ``-v``      | ``--verbose``      | Show additional information on SPET      |
|             |                    | progress.                                |
+-------------+--------------------+------------------------------------------+
| ``-d``      | ``--debug``        | Show debugging information.              |
+-------------+--------------------+------------------------------------------+
| ``-e [..]`` | ``--exclude [..]`` | Exclude the desired benchmark(s).        |
|             |                    | Available options: ``lmbench``, ``mlc``, |
|             |                    | ``openssl``, ``compilation``, ``zlib``,  |
|             |                    | ``linpack``, ``stream``, ``nosql``,      |
|             |                    | ``sql``, and ``docker``.                 |
+-------------+--------------------+------------------------------------------+
| ``-avx512`` | ``--avx512``       | Enable AVX-512 for High-Performance      |
|             |                    | Linpack.                                 |
+-------------+--------------------+------------------------------------------+

*****************
Performance Tests
*****************

+-------------------+---------------------------------------------------------+
| Purpose           | Description                                             |
+===================+=========================================================+
| **Cryptography**  | Uses `OpenSSL's <https://www.openssl.org/>`_ built-in   |
|                   | ``speed`` command for testing encryption and decryption |
|                   | on 128- and 256-bit ``AES-GCM``.                        |
+-------------------+---------------------------------------------------------+
| **Cache           | Uses `LMbench <http://www.bitmover.com/lmbench/>`_  for |
| Latency**         | measuring L1-, L2-, and L3-cache latencies using        |
|                   | ``lat_mem_rd`` by measuring memory read latency for     |
|                   | varying memory sizes and strides.                       |
+-------------------+---------------------------------------------------------+
| **Memory          | Uses `Intel(R) Memory Latency Checker (MLC)             |
| Latency**         | <https://software.intel.com/en-us/articles/intelr-      |
|                   | memory-latency-checker>`_ for measuring node-to-node    |
|                   | latency.                                                |
+-------------------+---------------------------------------------------------+
| **Memory          | Uses `STREAM <https://www.cs.virginia.edu/stream/>`_    |
| Bandwidth**       | for measuring sustainable memory bandwidth  and the     |
|                   | corresponding computation rate for simple vector        |
|                   | kernels in parallel using Open MPI.                     |
+-------------------+---------------------------------------------------------+
| **Floating-point  | Uses `High-Performance Linpack                          |
| / Math**          | <http://www.netlib.org/benchmark/hpl/>`_ for measuring  |
|                   | the floating-point rate of execution of the system by   |
|                   | running a program that solves a system of linear        |
|                   | equations.                                              |
+-------------------+---------------------------------------------------------+
| **Compression /   | Uses `zlib <https://zlib.net/>`_ for testing the        |
| Decompression**   | performance of compression and decompression on a 2 GB  |
|                   | text file.                                              |
+-------------------+---------------------------------------------------------+
| **Software        | Uses the system's build utilities to compile the `Linux |
| Development /     | kernel <https://www.kernel.org/>`_.                     |
| Compute**         |                                                         |
+-------------------+---------------------------------------------------------+
| **Database SQL**  | Uses `Yahoo! Cloud Serving Benchmark (YCSB)             |
|                   | <https://github.com/brianfrankcooper/YCSB/wiki>`_ to    |
|                   | measure read and update performance on `MySQL           |
|                   | <https://www.mysql.com/products/community/>`_           |
|                   | databases.                                              |
+-------------------+---------------------------------------------------------+
| **Database        | Uses `Yahoo! Cloud Serving Benchmark (YCSB)             |
| NoSQL**           | <https://github.com/brianfrankcooper/YCSB/wiki>`_ to    |
|                   | measure read and update performance on `Cassandra       |
|                   | <http://cassandra.apache.org/>`_ databases.             |
+-------------------+---------------------------------------------------------+
| **Containers**    | Uses `Docker                                            |
|                   | <https://www.docker.com/community-edition>`_ to test    |
|                   | the performance of compiling the `Linux kernel          |
|                   | <https://www.kernel.org/>`_ (same test as the software  |
|                   | development/compute) on 100 concurrent containers.      |
+-------------------+---------------------------------------------------------+

*************
Documentation
*************

Visit the `docs/ <docs/index.rst>`_ directory for additional documentation.

*******
License
*******

This project is licensed under the MIT License - see the
`LICENSE <LICENSE>`_ file for details.
