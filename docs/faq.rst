FAQ
===


What optimizations does SPET use?
---------------------------------

Server Performance Evaluation Tool optimizations in a few ways:

1.  Sets the CPU scaling governor to ``performance``.
2.  Disables transparent hugepages.
3.  Disables swap.
4.  Before each performance test, it writes buffered metadata and data to be
    written to the file system. It also frees pagecache, dentries, and inodes
    which will return page cache / buffer cache to "free".
5.  Sets the maximum call stack to unlimited.
6.  Sets the maximum number of file descriptors to 1048576.
7.  Sets the maximum number of user processes to unlimited.
8.  By default for compiled operations, it uses the appropriate ``-march=`` and
    ``-mtune=`` flags for the system. Some compilations also add ``-O3`` or
    ``-O2`` if an optimization flag is not already set.
9.  Add ``fs.file-max = 1048576`` to ``/etc/sysctl.conf``.
10. Add ``* - nofile 1048576'`` to ``/etc/security/limits.conf``.


Can I change the versions of packages used?
-------------------------------------------

Yes, you can override the package versions using by editing the
``spet/package_versions.py`` file. Please note that there is always a chance
that future versions are not setup the same as current versions, so it could
break some functionality in SPET.


Can I use custom C flags?
-------------------------

Yes, you can override Server Performance Evaluation Tool's optimizations by
editing the ``spet/overrides.py`` file.


What math library does SPET use for LINPACK?
--------------------------------------------

Server Performance Evaluation Tool uses one of three math libraries for
High-Performance Linpack.

1. If the processor name has Intel in it, SPET will use MKL.
2. If the processor name has AMD in it, SPET will use BLIS.
3. All other processor names will default to use OpenBLAS.
