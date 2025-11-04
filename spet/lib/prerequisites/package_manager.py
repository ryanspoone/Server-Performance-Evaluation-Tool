# -*- coding: utf-8 -*-
"""Prerequisites from the system's package manager."""

import logging
import re
import shutil

from spet.lib.utilities import execute
from spet.lib.utilities import prettify


def _validate_package_name(package):
    """Validate package name is safe.

    Args:
        package (str): Package name to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    # Allow alphanumeric, dash, underscore, dot, plus
    # Reject anything with shell metacharacters
    if not package or not isinstance(package, str):
        return False

    # Check for dangerous characters
    dangerous_chars = [';', '&', '|', '$', '`', '\\', '\n', '\r']
    if any(char in package for char in dangerous_chars):
        logging.error("Package name contains dangerous characters: %s", package)
        return False

    # Package names should be reasonable length
    if len(package) > 200:
        logging.error("Package name too long: %s", package[:50])
        return False

    return True


def zypper(packages):
    """Install zypper packages safely.

    Args:
        packages (tuple or list): Zypper packages to install.

    Returns:
        bool: True if all packages installed successfully, False otherwise.
    """
    if not shutil.which("zypper"):
        logging.error("zypper package manager not found")
        return False

    logging.info('Installing %d prerequisites using "zypper".', len(packages))

    success_count = 0
    fail_count = 0

    for package in packages:
        # Special handling for zypper options like "-t pattern devel_basis"
        if package.startswith("-"):
            # Split options and package name
            parts = package.split()
            cmd_list = ["zypper", "install", "-l", "-y", "--force-resolution"] + parts
        else:
            # Validate package name
            if not _validate_package_name(package):
                logging.error("Invalid package name: %s", package)
                fail_count += 1
                continue

            cmd_list = ["zypper", "install", "-l", "-y", "--force-resolution", package]

        try:
            logging.debug("Installing: %s", package)
            output = execute.output(cmd_list, timeout=300)
            logging.debug("Installed %s successfully", package)
            success_count += 1
        except Exception as err:
            logging.error("Failed to install %s: %s", package, err)
            fail_count += 1

    logging.info("zypper: %d succeeded, %d failed", success_count, fail_count)
    return fail_count == 0


def yum(packages):
    """Install yum packages safely.

    Args:
        packages (tuple or list): Yum packages to install.

    Returns:
        bool: True if all packages installed successfully, False otherwise.
    """
    if not shutil.which("yum"):
        logging.error("yum package manager not found")
        return False

    logging.info('Installing prerequisites using "yum".')

    # Install Development Tools group first
    try:
        logging.info("Installing Development Tools group")
        cmd_list = ["yum", "groupinstall", "-y", "--skip-broken", "Development Tools"]
        execute.output(cmd_list, timeout=600)
    except Exception as err:
        logging.warning("Failed to install Development Tools: %s", err)

    success_count = 0
    fail_count = 0

    for package in packages:
        # Validate package name
        if not _validate_package_name(package):
            logging.error("Invalid package name: %s", package)
            fail_count += 1
            continue

        try:
            logging.debug("Installing: %s", package)
            cmd_list = ["yum", "install", "-y", "--skip-broken", package]
            output = execute.output(cmd_list, timeout=300)
            logging.debug("Installed %s successfully", package)
            success_count += 1
        except Exception as err:
            logging.error("Failed to install %s: %s", package, err)
            fail_count += 1

    logging.info("yum: %d succeeded, %d failed", success_count, fail_count)
    return fail_count == 0


def apt_get(packages):
    """Install apt-get packages safely.

    Args:
        packages (tuple or list): Apt-get packages to install.

    Returns:
        bool: True if all packages installed successfully, False otherwise.
    """
    if not shutil.which("apt-get"):
        logging.error("apt-get package manager not found")
        return False

    logging.info('Installing %d prerequisites using "apt-get".', len(packages))

    # Update package list first
    try:
        logging.info("Updating package list")
        execute.output(["apt-get", "update"], timeout=300)
    except Exception as err:
        logging.warning("apt-get update failed: %s", err)

    success_count = 0
    fail_count = 0

    for package in packages:
        # Validate package name
        if not _validate_package_name(package):
            logging.error("Invalid package name: %s", package)
            fail_count += 1
            continue

        try:
            logging.debug("Installing: %s", package)
            cmd_list = ["apt-get", "install", "-y", "--ignore-missing", package]
            output = execute.output(cmd_list, timeout=300)
            logging.debug("Installed %s successfully", package)
            success_count += 1
        except Exception as err:
            logging.error("Failed to install %s: %s", package, err)
            fail_count += 1

    logging.info("apt-get: %d succeeded, %d failed", success_count, fail_count)
    return fail_count == 0


def aptitude(packages):
    """Install aptitude packages safely.

    Args:
        packages (tuple or list): Aptitude packages to install.

    Returns:
        bool: True if all packages installed successfully, False otherwise.
    """
    if not shutil.which("aptitude"):
        logging.error("The aptitude package manager could not be found.")
        return False

    logging.info('Installing %d prerequisites using "aptitude".', len(packages))

    # Update package list first
    try:
        logging.info("Updating package list")
        execute.output(["aptitude", "update"], timeout=300)
    except Exception as err:
        logging.warning("aptitude update failed: %s", err)

    success_count = 0
    fail_count = 0

    for package in packages:
        # Validate package name
        if not _validate_package_name(package):
            logging.error("Invalid package name: %s", package)
            fail_count += 1
            continue

        try:
            logging.debug("Installing: %s", package)
            cmd_list = ["aptitude", "install", "-y", "--ignore-missing", package]
            output = execute.output(cmd_list, timeout=300)
            logging.debug("Installed %s successfully", package)
            success_count += 1
        except Exception as err:
            logging.error("Failed to install %s: %s", package, err)
            fail_count += 1

    logging.info("aptitude: %d succeeded, %d failed", success_count, fail_count)
    return fail_count == 0


def apt(packages):
    """Install apt packages safely.

    Args:
        packages (tuple or list): Apt packages to install.

    Returns:
        bool: True if all packages installed successfully, False otherwise.
    """
    if not shutil.which("apt"):
        logging.error("The apt package manager could not be found.")
        return False

    logging.info('Installing %d prerequisites using "apt".', len(packages))

    # Update package list first
    try:
        logging.info("Updating package list")
        execute.output(["apt", "update"], timeout=300)
    except Exception as err:
        logging.warning("apt update failed: %s", err)

    success_count = 0
    fail_count = 0

    for package in packages:
        # Validate package name
        if not _validate_package_name(package):
            logging.error("Invalid package name: %s", package)
            fail_count += 1
            continue

        try:
            logging.debug("Installing: %s", package)
            cmd_list = ["apt", "install", "-y", "--ignore-missing", package]
            output = execute.output(cmd_list, timeout=300)
            logging.debug("Installed %s successfully", package)
            success_count += 1
        except Exception as err:
            logging.error("Failed to install %s: %s", package, err)
            fail_count += 1

    logging.info("apt: %d succeeded, %d failed", success_count, fail_count)
    return fail_count == 0


def unknown(packages):
    """Unknown package manager.

    Args:
        packages (tuple or list): Package names for user to install.

    Returns:
        bool: Always False since we can't install packages.
    """
    logging.error("Unknown package manager.")
    prettify.error_message(
        "The appropriate package manager for your system could not be found")
    print(
        "Please manually install the following packages and rerun this program:")
    print()

    for package in packages:
        print(f"  - {package}")

    print()
    return False
