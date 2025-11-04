# -*- coding: utf-8 -*-
"""Contains wrapper functions for downloading items."""

import hashlib
import logging
import os
import shutil
import ssl
import urllib.request
import urllib.error


def file(url, dest, expected_sha256=None, max_size_mb=1024, timeout=300):
    """Download file with security checks.

    Args:
        url (str): URL where the file is located.
        dest (str): Where to download the file to on this system.
        expected_sha256 (str, optional): Expected SHA256 hash of the file.
        max_size_mb (int, optional): Maximum file size in MB. Default 1024 MB.
        timeout (int, optional): Timeout in seconds. Default 300 (5 minutes).

    Returns:
        bool: True if download successful, False otherwise.

    Raises:
        ValueError: If URL is invalid or file exceeds size limit.
        urllib.error.URLError: If download fails.
    """
    # Validate URL
    if not url or not url.startswith(('http://', 'https://')):
        logging.error("Invalid URL: %s", url)
        raise ValueError(f"URL must start with http:// or https://: {url}")

    # Warn about HTTP (non-encrypted)
    if url.startswith('http://'):
        logging.warning("Downloading over insecure HTTP: %s", url)

    # Validate destination path
    if not dest:
        logging.error("Invalid destination path: empty")
        raise ValueError("Invalid destination path: empty")

    # Prevent path traversal
    if '..' in dest:
        logging.error("Invalid destination path contains ..: %s", dest)
        raise ValueError(f"Invalid destination path: {dest}")

    # Block writes to sensitive system directories
    sensitive_dirs = ['/etc/passwd', '/etc/shadow', '/etc/sudoers', '/boot', '/sys', '/proc']
    dest_normalized = os.path.normpath(os.path.abspath(dest))
    for sensitive in sensitive_dirs:
        if dest_normalized.startswith(sensitive):
            logging.error("Blocked write to sensitive path: %s", dest)
            raise ValueError(f"Cannot write to sensitive system path: {dest}")

    # Warn if using absolute path outside typical SPET directories
    if os.path.isabs(dest) and not any(dest.startswith(d) for d in ['/tmp', '/opt', '/home', '/root', '/usr/local']):
        logging.warning("Download to unusual absolute path: %s", dest)

    # Create parent directory if needed
    dest_dir = os.path.dirname(dest)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    agent = "SPET/1.0 (Server Performance Evaluation Tool)"
    max_size_bytes = max_size_mb * 1024 * 1024

    try:
        # Create SSL context with certificate verification
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        request = urllib.request.Request(url, headers={"User-Agent": agent})

        logging.info("Downloading: %s", url)

        with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as resp:
            # Check content length if provided
            content_length = resp.getheader('Content-Length')
            if content_length:
                size = int(content_length)
                if size > max_size_bytes:
                    raise ValueError(
                        f"File too large: {size} bytes "
                        f"(max {max_size_bytes} bytes)"
                    )
                logging.info("Download size: %.2f MB", size / (1024 * 1024))

            # Download with size checking
            hasher = hashlib.sha256()
            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks

            with open(dest, "wb") as out:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break

                    downloaded += len(chunk)
                    if downloaded > max_size_bytes:
                        # Clean up partial download
                        out.close()
                        if os.path.exists(dest):
                            os.remove(dest)
                        raise ValueError(
                            f"Downloaded data exceeds maximum size "
                            f"({max_size_mb} MB)"
                        )

                    out.write(chunk)
                    hasher.update(chunk)

                    # Log progress every 100 MB
                    if downloaded % (100 * 1024 * 1024) < chunk_size:
                        logging.info("Downloaded: %.2f MB", downloaded / (1024 * 1024))

        actual_sha256 = hasher.hexdigest()
        logging.info("Download complete: %s (%.2f MB)", dest, downloaded / (1024 * 1024))
        logging.info("SHA256: %s", actual_sha256)

        # Verify checksum if provided
        if expected_sha256:
            if actual_sha256.lower() != expected_sha256.lower():
                # Remove file with wrong checksum
                if os.path.exists(dest):
                    os.remove(dest)
                logging.error("Checksum mismatch!")
                logging.error("Expected: %s", expected_sha256.lower())
                logging.error("Actual:   %s", actual_sha256.lower())
                raise ValueError(
                    f"Checksum verification failed for {url}. "
                    f"Expected {expected_sha256}, got {actual_sha256}"
                )
            logging.info("Checksum verified successfully")

        return True

    except urllib.error.URLError as err:
        logging.error("Download failed for %s: %s", url, err)
        # Clean up partial download
        if os.path.exists(dest):
            try:
                os.remove(dest)
            except OSError:
                pass
        raise
    except IOError as err:
        logging.error("IO error during download: %s", err)
        # Clean up partial download
        if os.path.exists(dest):
            try:
                os.remove(dest)
            except OSError:
                pass
        raise
    except Exception as err:
        logging.error("Unexpected error during download: %s", err)
        # Clean up partial download
        if os.path.exists(dest):
            try:
                os.remove(dest)
            except OSError:
                pass
        raise
