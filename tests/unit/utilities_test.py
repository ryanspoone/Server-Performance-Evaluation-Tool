# -*- coding: utf-8 -*-
"""Tests for lib/utilities"""

from spet.lib.utilities import execute
from spet.lib.utilities import prettify


def test_execute():
    """execute should run echo command correctly"""
    result = execute.output('echo "hi"')
    assert result == "hi\n"


## TODO
# def test_timed():
#    """timed: should time the sleep command correctly"""
#    result = execute.timed("sleep 2")
#    assert result == 2


def test_error_message(capsys):
    """error_message: should generate an error mesage"""
    prettify.error_message("my error mesage")
    captured = capsys.readouterr()
    assert captured.out == "\x1b[31mError\x1b[0m: my error mesage\n"
    assert captured.err == ""


def test_byte_size():
    """byte_size: should convert bytes to a human readable format"""
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
