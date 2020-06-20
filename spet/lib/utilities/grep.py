# -*- coding: utf-8 -*-
"""Lines matching a pattern."""

import logging
import re


def file(file_path, pattern):
    """All lines of file matching the pattern.

    Args:
        file_path (str): The file to search.
        pattern (str): The search pattern.

    Returns:
        List: All lines containing the pattern.
    """
    try:
        lines = []
        with open(file_path) as origin_file:
            for line in origin_file:
                found = re.findall(pattern, line)
                if found:
                    lines.append(line)
        logging.debug("lines: %s", str(lines))
        return lines
    except IOError as err:
        logging.error(err)


def text(body, pattern):
    """All lines of text matching the pattern.

    Args:
        body (str): The body of text to search.
        pattern (str): The search pattern.

    Returns:
        List: All lines containing the pattern.

    """
    try:
        findings = []
        if not body:
            return []
        lines = body.rstrip().split("\n")
        for line in lines:
            found = re.findall(pattern, line)
            if found:
                findings.append(line)
        logging.debug("findings: %s", str(findings))
        return findings
    except IOError as err:
        logging.error(err)
