# -*- coding: utf-8 -*-
"""Contains wrapper functions for extracting archives."""

import logging
import os
import tarfile


def _is_safe_path(base_dir, path):
    """Check if path is safe (doesn't escape base directory).

    Args:
        base_dir (str): The base directory where extraction should occur.
        path (str): The path to check.

    Returns:
        bool: True if path is safe, False if it tries to escape base_dir.
    """
    # Resolve both paths to absolute paths
    base = os.path.abspath(base_dir)
    target = os.path.abspath(os.path.join(base_dir, path))

    # Check if target is within base directory
    return target.startswith(base)


def _safe_extract(tar_file, output_dir="."):
    """Safely extract tar file with path traversal protection.

    Args:
        tar_file (tarfile.TarFile): Open tar file object.
        output_dir (str): Directory where files should be extracted.

    Raises:
        ValueError: If archive contains unsafe paths.
    """
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Validate all paths before extracting anything
    for member in tar_file.getmembers():
        # Check for absolute paths
        if member.name.startswith('/'):
            raise ValueError(f"Archive contains absolute path: {member.name}. "
                             f"This is a security risk.")

        # Check for parent directory references
        if '..' in member.name:
            raise ValueError(
                f"Archive contains parent directory reference: {member.name}. "
                f"This is a security risk.")

        # Check if resolved path would escape output directory
        if not _is_safe_path(output_dir, member.name):
            raise ValueError(
                f"Archive contains path that escapes output directory: {member.name}. "
                f"This is a security risk.")

        # Check for suspicious file types
        if member.issym() or member.islnk():
            # Verify symlink targets are also safe
            if member.linkname and not _is_safe_path(output_dir,
                                                     member.linkname):
                raise ValueError(
                    f"Archive contains unsafe symlink: {member.name} -> {member.linkname}"
                )

    # All paths validated, now extract
    total_members = len(tar_file.getmembers())
    logging.info("Extracting %d files to %s", total_members, output_dir)

    extracted = 0
    for member in tar_file.getmembers():
        tar_file.extract(member, output_dir)
        extracted += 1

        # Log progress every 100 files
        if extracted % 100 == 0 or extracted == total_members:
            logging.debug("Extracted %d/%d files", extracted, total_members)

    logging.info("Extraction complete: %d files", extracted)


def tar(archive, output_dir="."):
    """Extract recognized tar file types with security checks.

    Args:
        archive (str): The archive to extract.
        output_dir (str, optional): Where the archive is extracted.

    Returns:
        bool: True if extraction successful, False otherwise.

    Raises:
        FileNotFoundError: If archive file doesn't exist.
        ValueError: If archive contains unsafe paths.
        tarfile.TarError: If archive is corrupted or invalid.
    """
    # Validate inputs
    if not archive or not os.path.isfile(archive):
        logging.error("Archive file not found: %s", archive)
        raise FileNotFoundError(f"Archive file not found: {archive}")

    if not output_dir:
        output_dir = "."

    # Validate output directory doesn't contain parent references
    if '..' in output_dir:
        logging.error("Output directory contains parent reference: %s",
                      output_dir)
        raise ValueError(f"Invalid output directory: {output_dir}")

    try:
        # Determine archive type and open appropriately
        if archive.endswith(".tar.gz") or archive.endswith(".tgz"):
            logging.info("Extracting gzipped tar archive: %s", archive)
            mode = "r:gz"
        elif archive.endswith(".tar.bz2"):
            logging.info("Extracting bzipped tar archive: %s", archive)
            mode = "r:bz2"
        elif archive.endswith(".tar.xz"):
            logging.info("Extracting xz tar archive: %s", archive)
            mode = "r:xz"
        elif archive.endswith(".tar"):
            logging.info("Extracting tar archive: %s", archive)
            mode = "r:"
        else:
            logging.error("Unsupported archive format: %s", archive)
            raise ValueError(f"Unsupported archive format: {archive}")

        # Use context manager to ensure file is closed
        with tarfile.open(archive, mode) as tar_file:
            _safe_extract(tar_file, output_dir)

        return True

    except tarfile.TarError as err:
        logging.error("Tar extraction error for %s: %s", archive, err)
        raise
    except IOError as err:
        logging.error("IO error extracting %s: %s", archive, err)
        raise
    except Exception as err:
        logging.error("Unexpected error extracting %s: %s", archive, err)
        raise
