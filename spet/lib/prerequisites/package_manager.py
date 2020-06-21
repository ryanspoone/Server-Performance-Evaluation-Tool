# -*- coding: utf-8 -*-
"""Prerequisites from the system's package manager."""

import logging
import shutil

from spet.lib.utilities import execute
from spet.lib.utilities import prettify


def zypper(packages):
    """Install zypper packages.

    Args:
        packages (list): Zypper packages to install.
    """
    try:
        if not shutil.which("zypper"):
            return False

        logging.info('Installing prerequisites using "zypper".')

        for package in packages:
            cmd = "sudo -E zypper install -l -y --force-resolution " + package
            logging.debug("Zypper install: %s", cmd)
            output = execute.output(cmd)
            logging.debug("Zypper output: %s", output)
    except IOError as err:
        logging.debug(err)
    except ValueError as err:
        logging.debug(err)
    except TypeError as err:
        logging.debug(err)


def yum(packages):
    """Install yum packages.

    Args:
        packages (list): Yum packages to install.
    """
    try:
        if not shutil.which("yum"):
            return

        logging.info('Installing prerequisites using "yum".')

        devtools = "sudo -E yum groupinstall -y --skip-broken " '"Development Tools"'
        logging.debug("Yum install: %s", devtools)
        output = execute.output(devtools)
        logging.debug("Yum output: %s", output)

        for package in packages:
            cmd = "sudo -E yum install -y --skip-broken " + package
            logging.debug("Yum install: %s", cmd)
            output = execute.output(cmd)
            logging.debug("Yum output: %s", output)
    except IOError as err:
        logging.debug(err)
    except ValueError as err:
        logging.debug(err)
    except TypeError as err:
        logging.debug(err)


def apt_get(packages):
    """Install apt-get packages.

    Args:
        packages (list): Apt-get packages to install.
    """
    try:
        if not shutil.which("apt-get"):
            return

        logging.info('Installing prerequisites using "apt-get".')

        for package in packages:
            cmd = "sudo -E apt-get install -y --ignore-missing " + package
            logging.debug("Apt-get install: %s", cmd)
            output = execute.output(cmd)
            logging.debug("Apt-get output: %s", output)
    except IOError as err:
        logging.debug(err)
    except ValueError as err:
        logging.debug(err)
    except TypeError as err:
        logging.debug(err)


def aptitude(packages):
    """Install aptitude packages.

    Args:
        packages (list): Aptitude packages to install.
    """
    try:
        if not shutil.which("aptitude"):
            logging.error("The aptitude package manager could not be found.")
            return

        logging.info('Installing prerequisites using "aptitude".')

        for package in packages:
            cmd = "sudo -E aptitude install -y --ignore-missing " + package
            logging.debug("Aptitude install: %s", cmd)
            output = execute.output(cmd)
            logging.debug("Aptitude output: %s", output)
    except IOError as err:
        logging.debug(err)
    except ValueError as err:
        logging.debug(err)
    except TypeError as err:
        logging.debug(err)


def apt(packages):
    """Install apt packages.

    Args:
        packages (list): Apt packages to install.
    """
    try:
        if not shutil.which("apt"):
            logging.error("The apt package manager could not be found.")
            return

        logging.info('Installing prerequisites using "apt".')

        for package in packages:
            cmd = "sudo -E apt install -y --ignore-missing " + package
            logging.debug("Apt install: %s", cmd)
            output = execute.output(cmd)
            logging.debug("Apt output: %s", output)
    except IOError as err:
        logging.debug(err)
    except ValueError as err:
        logging.debug(err)
    except TypeError as err:
        logging.debug(err)


def unknown(packages):
    """Unknown package manager.

    Args:
        packages (list): Package names for user to install.
    """
    logging.warning("Unknown package manager.")
    prettify.error_message(
        "The appropriate package manager for your system could not be found")
    print(
        "Please try manually installing the following and rerun this program:")

    for package in packages:
        print(package)
