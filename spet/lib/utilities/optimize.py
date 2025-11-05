# -*- coding: utf-8 -*-
"""Used for optimizing the system for performance tests with backup/restore capability."""

import atexit
import logging
import os
import re
import shutil

import resource

from spet.lib.utilities import execute
from spet.lib.utilities import grep
from spet.lib.utilities import file

# Global dictionary to store original system settings
_ORIGINAL_SETTINGS = {}
_RESTORE_REGISTERED = False


def _register_restore():
    """Register the restore function to run at exit."""
    global _RESTORE_REGISTERED
    if not _RESTORE_REGISTERED:
        atexit.register(restore_system_settings)
        _RESTORE_REGISTERED = True
        logging.info("Registered system settings restore on exit")


def performance_governor():
    """Sets the CPU scaling governor to performance with backup."""
    cpu_root = "/sys/devices/system/cpu/"

    try:
        if not os.path.isdir(cpu_root):
            logging.warning("CPU root directory not found: %s", cpu_root)
            return False

        _register_restore()

        pattern = r"cpu[0-9]+"
        changed_count = 0

        for cpu in next(os.walk(cpu_root))[1]:
            if not re.match(pattern, cpu):
                continue

            governor_path = os.path.join(cpu_root, cpu, "cpufreq",
                                         "scaling_governor")

            if os.path.isfile(governor_path):
                # Save original setting before changing
                if governor_path not in _ORIGINAL_SETTINGS:
                    try:
                        original = file.read(governor_path,
                                             max_size_mb=1).strip()
                        _ORIGINAL_SETTINGS[governor_path] = original
                        logging.debug("Saved original governor for %s: %s", cpu,
                                      original)
                    except Exception as e:
                        logging.warning(
                            "Failed to read original governor for %s: %s", cpu,
                            e)
                        continue

                # Set to performance
                try:
                    file.write(governor_path, "performance")
                    changed_count += 1
                    logging.debug("Set %s governor to performance", cpu)
                except Exception as e:
                    logging.error(
                        "Failed to set performance governor for %s: %s", cpu, e)

        if changed_count > 0:
            logging.info("Changed %d CPU governors to performance mode",
                         changed_count)
            return True
        else:
            logging.warning("No CPU governors were changed")
            return False

    except Exception as err:
        logging.error("Error setting performance governor: %s", err)
        return False


def disable_hugepages():
    """Disables transparent hugepages with backup."""
    transparent_hugepage = "/sys/kernel/mm/transparent_hugepage/enabled"

    try:
        if not os.path.isfile(transparent_hugepage):
            logging.warning("Transparent hugepages file not found")
            return False

        _register_restore()

        # Save original setting
        if transparent_hugepage not in _ORIGINAL_SETTINGS:
            try:
                original = file.read(transparent_hugepage,
                                     max_size_mb=1).strip()
                _ORIGINAL_SETTINGS[transparent_hugepage] = original
                logging.debug("Saved original hugepages setting: %s", original)
            except Exception as e:
                logging.warning("Failed to read original hugepages setting: %s",
                                e)
                return False

        # Disable hugepages
        try:
            file.write(transparent_hugepage, "never")
            logging.info("Disabled transparent hugepages")
            return True
        except Exception as e:
            logging.error("Failed to disable hugepages: %s", e)
            return False

    except Exception as err:
        logging.error("Error disabling hugepages: %s", err)
        return False


def disable_swap():
    """Disable swap with tracking for restore."""
    try:
        if not shutil.which("swapoff"):
            logging.warning("swapoff command not found")
            return False

        _register_restore()

        # Check if swap is currently enabled
        if "swap_disabled" not in _ORIGINAL_SETTINGS:
            try:
                # Check current swap status
                swap_info = execute.output(["swapon", "--show"])
                swap_was_enabled = bool(swap_info and swap_info.strip())
                _ORIGINAL_SETTINGS["swap_disabled"] = swap_was_enabled
                logging.debug("Swap was originally %s",
                              "enabled" if swap_was_enabled else "disabled")
            except Exception as e:
                logging.warning("Failed to check swap status: %s", e)
                # Assume it was enabled if we can't check
                _ORIGINAL_SETTINGS["swap_disabled"] = True

        # Disable swap (no sudo needed, already running as root)
        try:
            execute.output(["swapoff", "-a"])
            logging.info("Disabled swap")
            return True
        except Exception as e:
            logging.error("Failed to disable swap: %s", e)
            return False

    except Exception as err:
        logging.error("Error disabling swap: %s", err)
        return False


def restore_system_settings():
    """Restore all original system settings.

    This function is automatically called on program exit via atexit.
    """
    if not _ORIGINAL_SETTINGS:
        logging.debug("No system settings to restore")
        return

    logging.info("Restoring original system settings...")
    restored_count = 0
    failed_count = 0

    for setting_path, original_value in _ORIGINAL_SETTINGS.items():
        try:
            if setting_path == "swap_disabled":
                # Special handling for swap
                if original_value:  # If swap was originally enabled
                    logging.debug("Re-enabling swap")
                    try:
                        execute.output(["swapon", "-a"])
                        logging.info("Re-enabled swap")
                        restored_count += 1
                    except Exception as e:
                        logging.warning("Failed to re-enable swap: %s", e)
                        failed_count += 1
                continue

            # Restore file-based settings
            if os.path.isfile(setting_path):
                file.write(setting_path, original_value)
                logging.debug("Restored %s to: %s", setting_path,
                              original_value)
                restored_count += 1
            else:
                logging.warning("Setting path no longer exists: %s",
                                setting_path)
                failed_count += 1

        except Exception as e:
            logging.error("Failed to restore %s: %s", setting_path, e)
            failed_count += 1

    logging.info("Restored %d settings, %d failed", restored_count,
                 failed_count)


def prerun():
    """Clear up system resources before running a benchmark."""
    try:
        cleared = False

        # Sync filesystems (no sudo needed, already root)
        if shutil.which("sync"):
            try:
                execute.output(["sync"])
                logging.debug("Synced filesystems")
                cleared = True
            except Exception as e:
                logging.warning("Failed to sync filesystems: %s", e)

        # Drop caches
        drop_caches = "/proc/sys/vm/drop_caches"
        if os.path.isfile(drop_caches):
            try:
                file.write(drop_caches, "3")
                logging.debug("Dropped caches")
                cleared = True
            except Exception as e:
                logging.warning("Failed to drop caches: %s", e)

        return cleared

    except Exception as err:
        logging.error("Error in prerun: %s", err)
        return False


def ulimit():
    """Sets the `ulimit` values for this and child processes."""
    try:
        # The maximum size (in bytes) of the call stack for the current
        # process. This only affects the stack of the main thread in a
        # multi-threaded process.
        # `ulimit -s unlimited`
        resource.setrlimit(resource.RLIMIT_STACK,
                           (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

        # The maximum number of open file descriptors for the current process.
        # `ulimit -n 1048576`
        resource.setrlimit(resource.RLIMIT_NOFILE, (1048576, 1048576))

        # The maximum number of user processes for the current process.
        # `ulimit -u unlimited`
        resource.setrlimit(resource.RLIMIT_NPROC,
                           (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

        logging.info("Set ulimit values successfully")
        return True

    except (ValueError, OSError) as err:
        logging.error("Failed to set ulimit values: %s", err)
        return False


def nofiles():
    """Sets the number of files limit in system config files.

    WARNING: This modifies /etc/security/limits.conf and /etc/sysctl.conf
    These changes are NOT automatically reverted on exit.
    """
    limits_conf = "/etc/security/limits.conf"
    sysctl_conf = "/etc/sysctl.conf"

    try:
        modified = False

        if os.path.isfile(limits_conf):
            try:
                lines = grep.file(limits_conf, "nofile 1048576")
                if not lines:
                    logging.warning("Modifying %s (changes are permanent)",
                                    limits_conf)
                    file.write(limits_conf,
                               "\n* - nofile 1048576\n",
                               append=True)
                    modified = True
            except Exception as e:
                logging.error("Failed to modify %s: %s", limits_conf, e)

        if os.path.isfile(sysctl_conf):
            try:
                lines = grep.file(sysctl_conf, "fs.file-max = 1048576")
                if not lines:
                    logging.warning("Modifying %s (changes are permanent)",
                                    sysctl_conf)
                    file.write(sysctl_conf,
                               "\nfs.file-max = 1048576\n",
                               append=True)
                    modified = True

                if modified and shutil.which("sysctl"):
                    execute.output(["sysctl", "-p"])
                    logging.info("Reloaded sysctl configuration")
            except Exception as e:
                logging.error("Failed to modify %s: %s", sysctl_conf, e)

        return modified

    except Exception as err:
        logging.error("Error setting nofiles limit: %s", err)
        return False
