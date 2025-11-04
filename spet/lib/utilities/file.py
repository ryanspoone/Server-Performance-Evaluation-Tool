# -*- coding: utf-8 -*-
"""Contains miscellaneous functions to with common file tasks."""

import logging
import os
import re


def read(file_path, max_size_mb=100):
    """Reads contents of the file safely.

    Args:
        file_path (str): File to read.
        max_size_mb (int, optional): Maximum file size to read in MB. Default 100.

    Returns:
        String: File contents.

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If file is too large.
    """
    if not file_path or not os.path.isfile(file_path):
        logging.error("File not found: %s", file_path)
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size = os.path.getsize(file_path)
    if file_size > max_size_bytes:
        logging.error("File too large: %s (%.2f MB)", file_path, file_size / (1024 * 1024))
        raise ValueError(
            f"File too large: {file_path} ({file_size} bytes, "
            f"max {max_size_bytes} bytes)"
        )

    try:
        # Use context manager and specify encoding
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Only log that we read the file, not the contents (security)
        logging.debug("Read file: %s (%d bytes)", file_path, len(content))
        return content

    except UnicodeDecodeError:
        # If UTF-8 fails, try binary mode
        logging.warning("UTF-8 decode failed for %s, reading as binary", file_path)
        with open(file_path, 'rb') as f:
            content = f.read()
        return content.decode('utf-8', errors='replace')
    except IOError as err:
        logging.error("IO error reading file %s: %s", file_path, err)
        raise


def touch(file_path):
    """Creates empty file safely.

    Args:
        file_path (str): File to create.

    Returns:
        bool: True if successful, False otherwise.

    Raises:
        ValueError: If file path is invalid.
    """
    if not file_path:
        logging.error("Invalid file path: %s", file_path)
        raise ValueError("File path cannot be empty")

    # Prevent path traversal
    if '..' in file_path:
        logging.error("File path contains parent reference: %s", file_path)
        raise ValueError(f"Invalid file path: {file_path}")

    try:
        basedir = os.path.dirname(file_path)
        # Create directory tree if necessary
        if basedir and not os.path.exists(basedir):
            os.makedirs(basedir, mode=0o755)

        # Create an empty file using context manager
        with open(file_path, 'a', encoding='utf-8'):
            os.utime(file_path, None)

        logging.debug("Created file: %s", file_path)
        return True

    except IOError as err:
        logging.error("IO error creating file %s: %s", file_path, err)
        raise


def write(file_path, text, append=False, encoding='utf-8'):
    """Write text to file safely.

    Args:
        file_path (str): File to write.
        text (str): Text to write to file.
        append (bool, optional): Whether to append the text to the file or not.
        encoding (str, optional): File encoding. Default 'utf-8'.

    Returns:
        bool: True if successful.

    Raises:
        ValueError: If file path or text is invalid.
        IOError: If write fails.
    """
    if not file_path:
        logging.error("Invalid file path")
        raise ValueError("File path cannot be empty")

    # Prevent path traversal (reject .. in all paths)
    if '..' in file_path:
        logging.error("File path contains parent reference: %s", file_path)
        raise ValueError(f"Invalid file path: {file_path}")

    if text is None:
        logging.warning("Attempting to write None to %s, converting to empty string", file_path)
        text = ""

    try:
        write_type = "a" if append else "w"

        # Create parent directory if needed
        basedir = os.path.dirname(file_path)
        if basedir and not os.path.exists(basedir):
            os.makedirs(basedir, mode=0o755)

        # Use context manager
        with open(file_path, write_type, encoding=encoding) as f:
            f.write(text)

        logging.debug("Wrote %d bytes to %s (append=%s)", len(text), file_path, append)
        return True

    except IOError as err:
        logging.error("IO error writing to %s: %s", file_path, err)
        raise


def replace_line(file_path, pattern, subst):
    """Replace line in file safely.

    Args:
        file_path (str): The file to modify.
        pattern (str): Pattern in line to search for (regex).
        subst (str): What to substitute the pattern with.

    Returns:
        int: Number of lines modified.

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If pattern or subst is invalid.
    """
    if not file_path or not os.path.isfile(file_path):
        logging.error("File not found: %s", file_path)
        raise FileNotFoundError(f"File not found: {file_path}")

    if not pattern:
        logging.error("Pattern cannot be empty")
        raise ValueError("Pattern cannot be empty")

    if subst is None:
        logging.warning("Substitution is None, converting to empty string")
        subst = ""

    try:
        # Compile regex to validate it
        regex = re.compile(pattern)

        # Read all lines
        with open(file_path, "r", encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Replace lines
        modified_count = 0
        new_lines = []
        for line in lines:
            new_line = regex.sub(subst, line)
            if new_line != line:
                modified_count += 1
            new_lines.append(new_line)

        # Write back
        with open(file_path, "w", encoding='utf-8') as f:
            f.writelines(new_lines)

        logging.info("Modified %d lines in %s", modified_count, file_path)
        return modified_count

    except re.error as err:
        logging.error("Invalid regex pattern '%s': %s", pattern, err)
        raise ValueError(f"Invalid regex pattern: {err}")
    except IOError as err:
        logging.error("IO error modifying %s: %s", file_path, err)
        raise
