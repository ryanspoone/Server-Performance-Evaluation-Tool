# -*- coding: utf-8 -*-
"""Tests for lib/utilities"""

from spet.lib.utilities import execute
from spet.lib.utilities import prettify
from spet.lib.utilities import uglify


def TODO():
    """Tests that need to be completed."""
    pass


def NOT_IMPLEMENTING():
    """Tests not planned to be implemented. This is generally because it is a risky test."""
    pass


##########
# access
##########


def test_access__is_root():
    """access::is_root: should correctly tell if the program has root access or not"""
    TODO()


def test_access__make_executable():
    """access::make_executable: should make a file an executable"""
    TODO()


##########
# cleanup
##########


def test_cleanup__remove_color_codes():
    """cleanup::remove_color_codes: should remove ANSI escape color codes from the file"""
    TODO()


###########
# download
###########


def test_download__file():
    """download::file: should download a file"""
    TODO()


##########
# execute
##########


def test_execute__output():
    """execute::output: should run echo command correctly"""
    result = execute.output('echo "hi"')
    assert result == "hi\n"


def test_execute__timed():
    """timed: should time the sleep command correctly"""
    TODO()


def test_execute__pkill():
    """pkill: should kill all processes containing the name."""
    NOT_IMPLEMENTING()  # Deprecated in favor of `kill`


def test_execute__kill():
    """kill: should kill the process with the PID"""
    TODO()


##########
# extract
##########


def test_extract__tar():
    """extract::tar: should extract tar, tar.gz, and tgz files"""
    TODO()


#######
# file
#######


def test_file__read():
    """file::read: should read the contents of a file"""
    TODO()


def test_file__touch():
    """file::touch: should create an empty file"""
    TODO()


def test_file__write():
    """file::write: should write to a file"""
    TODO()


def test_file__replace_line():
    """file::replace_line: should replace a line in a file"""
    TODO()


#######
# grep
#######


def test_grep_file():
    """grep::file: should return all lines matching the pattern"""
    TODO()


def test_grep_text():
    """grep::text: should return all lines matching the pattern"""
    TODO()


############
# json_file
############


def test_json_file__write():
    """json_file::write: should write to a JSON file"""
    TODO()


def test_json_file__read():
    """json_file::read: should read the contents of a JSON file"""
    TODO()


###########
# optimize
###########


def test_optimize__performance_governor():
    """optimize::performance_governor"""
    NOT_IMPLEMENTING()


def test_optimize__disable_hugepages():
    """optimize::disable_hugepages"""
    NOT_IMPLEMENTING()


def test_optimize__disable_swap():
    """optimize::disable_swap"""
    NOT_IMPLEMENTING()


def test_optimize__prerun():
    """optimize::prerun"""
    NOT_IMPLEMENTING()


def test_optimize__ulimit():
    """optimize::ulimit"""
    NOT_IMPLEMENTING()


def test_optimize__nofiles():
    """optimize::nofiles"""
    NOT_IMPLEMENTING()


###########
# prettify
###########


def test_prettify__error_message(capsys):
    """prettify::error_message: should generate an error mesage"""
    prettify.error_message("my error mesage")
    captured = capsys.readouterr()
    assert captured.out == "\x1b[31mError\x1b[0m: my error mesage\n"
    assert captured.err == ""


def test_prettify__byte_size():
    """prettify::byte_size: should convert bytes to a human readable format"""
    result = prettify.byte_size(1)
    assert result == "1 B"
    result = prettify.byte_size(10000)
    assert result == "9.77 KB"
    result = prettify.byte_size(10000000)
    assert result == "9.54 MB"
    result = prettify.byte_size(10000000000)
    assert result == "9.31 GB"
    result = prettify.byte_size(1000000000000000)
    assert result == "909.49 TB"
    result = prettify.byte_size(10000000000000000000000)
    assert result == "8881784.2 PB"

    result = prettify.byte_size(10000, "KB")
    assert result == "9.77 MB"


def test_prettify__byte_per_second():
    """prettify::byte_per_second"""
    TODO()


def test_prettify__time_elapsed():
    """prettify::time_elapsed"""
    TODO()


def test_prettify__small_time():
    """prettify::small_time"""
    TODO()


def test_prettify__flops():
    """prettify::flops"""
    TODO()


def test_prettify__numbers():
    """prettify::numbers"""
    TODO()


def test_prettify__exponential():
    """prettify::exponential"""
    TODO()


##########
# run_num
##########


def test_run_num__write():
    """run_num::write"""
    TODO()


def test_run_num__read():
    """run_num::read"""
    TODO()


#########
# uglify
#########


def test_uglify__filename():
    """uglify::filename"""
    assert uglify.filename(
        'Intel Core(TM) i7-7700 CPU') == 'intel_core_i7-7700_cpu'
    assert uglify.filename('Intel(R) Xeon(R) Platinum 8180 CPU @ 2.50GHz'
                          ) == 'intel_xeon_platinum_8180_cpu_2.50ghz'
