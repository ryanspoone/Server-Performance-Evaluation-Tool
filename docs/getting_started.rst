===============
Getting Started
===============

.. contents::
   :depth: 3
   :backlinks: top
   :local:

************
Requirements
************

1. x86_64 system
2. Linux (Ubuntu, Debian, CentOS, openSUSE) Operating System
      + Most stable on Ubuntu
3. Root access
4. Python3

*****
Setup
*****

.. code-block:: bash

    pip3 install .
    python3 setup install


***
Run
***

Once everything is set up, you can simply run Server Performance Evaluation
Tool by executing the ``spet`` command:

**Note: You need root access to run Server Performance Evaluation Tool.**

.. code-block:: bash

    spet

If for some reason, the CLI does not work, you can call Server Performance
Evaluation Tool module with the following:

.. code-block:: bash

    python3 -m spet

*******
Results
*******

Results will be outputted to the console (stdout) as they are gathered.
All result files will be located in ``$HOME/spet_results`` under your specific
run's directory.

If ``$HOME`` was not detected for whatever reason, the result files will be
located in the Server Performance Evaluation Tool's ``spet/spet_results``
directory.

******************
Additional Options
******************

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


*************
Usage Example
*************

.. code-block:: bash

    # Do not run linpack and docker for a Skylake server
    sudo ./run --exclude linpack docker --avx512
