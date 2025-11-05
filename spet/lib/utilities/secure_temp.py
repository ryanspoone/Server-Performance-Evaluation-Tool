# -*- coding: utf-8 -*-
"""Secure temporary file and credential handling utilities."""

import logging
import os
import secrets
import string
import tempfile


class SecurePidFile:
    """Context manager for secure PID file handling.

    Creates a secure temporary file for PID storage that is automatically
    cleaned up on exit. Prevents symlink attacks by using secure temp files.

    Example:
        with SecurePidFile() as pid_file:
            # Start process with pid_file.name
            subprocess.Popen(..., args=["-p", pid_file.name])
            # PID file is automatically cleaned up on exit
    """

    def __init__(self, prefix="spet_", suffix=".pid"):
        """Initialize secure PID file.

        Args:
            prefix (str): Prefix for temp file name.
            suffix (str): Suffix for temp file name.
        """
        self.prefix = prefix
        self.suffix = suffix
        self.temp_file = None
        self.file_path = None

    def __enter__(self):
        """Create secure temporary file."""
        # Create in system temp directory with secure permissions (0600)
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            prefix=self.prefix,
            suffix=self.suffix,
            delete=False  # We'll delete manually for better control
        )
        self.file_path = self.temp_file.name

        # Ensure only owner can read/write
        os.chmod(self.file_path, 0o600)

        logging.debug("Created secure PID file: %s", self.file_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary file."""
        if self.temp_file:
            try:
                self.temp_file.close()
            except Exception as e:
                logging.warning("Failed to close PID file: %s", e)

        if self.file_path and os.path.exists(self.file_path):
            try:
                os.unlink(self.file_path)
                logging.debug("Removed secure PID file: %s", self.file_path)
            except Exception as e:
                logging.warning("Failed to remove PID file: %s", e)

        return False  # Don't suppress exceptions

    @property
    def name(self):
        """Get the path to the PID file."""
        return self.file_path

    def read_pid(self):
        """Read PID from file.

        Returns:
            str: The PID as a string, or None if not readable.
        """
        if not self.file_path or not os.path.exists(self.file_path):
            return None

        try:
            with open(self.file_path, 'r') as f:
                pid = f.read().strip()
                if pid:
                    return pid
        except Exception as e:
            logging.error("Failed to read PID from %s: %s", self.file_path, e)

        return None


def generate_secure_password(length=32):
    """Generate a cryptographically secure random password.

    Args:
        length (int): Length of password. Default 32 characters.

    Returns:
        str: Secure random password containing letters, digits, and punctuation.
    """
    if length < 16:
        logging.warning("Password length %d is too short, using 16", length)
        length = 16

    # Use all printable ASCII characters except space and quotes
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"

    # Use secrets module for cryptographically secure random generation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    logging.debug("Generated secure password of length %d", length)
    return password


def create_mysql_config(password, socket_path=None):
    """Create a secure MySQL configuration file.

    Args:
        password (str): MySQL root password.
        socket_path (str, optional): Path to MySQL socket file.

    Returns:
        str: Path to the created config file.
    """
    config_content = f"""[client]
user=root
password={password}
"""

    if socket_path:
        config_content += f"socket={socket_path}\n"

    # Create secure temp file with 0600 permissions
    fd, path = tempfile.mkstemp(suffix='.cnf', prefix='mysql_', text=True)

    try:
        with os.fdopen(fd, 'w') as f:
            f.write(config_content)

        # Ensure only owner can read (contains password)
        os.chmod(path, 0o600)

        logging.debug("Created MySQL config file: %s", path)
        return path
    except Exception as e:
        logging.error("Failed to create MySQL config: %s", e)
        # Clean up on failure
        try:
            os.unlink(path)
        except:
            pass
        raise


class SecureCredentials:
    """Secure credential management for database benchmarks.

    Generates and manages secure passwords for MySQL and Cassandra,
    cleaning up automatically on exit.
    """

    def __init__(self):
        """Initialize with secure random passwords."""
        self.mysql_password = generate_secure_password()
        self.cassandra_password = generate_secure_password()
        self.mysql_config_file = None

    def get_mysql_config_file(self, socket_path=None):
        """Get path to MySQL config file with credentials.

        Args:
            socket_path (str, optional): Path to MySQL socket.

        Returns:
            str: Path to config file.
        """
        if not self.mysql_config_file:
            self.mysql_config_file = create_mysql_config(
                self.mysql_password, socket_path)
        return self.mysql_config_file

    def cleanup(self):
        """Clean up credential files."""
        if self.mysql_config_file and os.path.exists(self.mysql_config_file):
            try:
                os.unlink(self.mysql_config_file)
                logging.debug("Removed MySQL config file")
            except Exception as e:
                logging.warning("Failed to remove MySQL config: %s", e)

    def __del__(self):
        """Cleanup on garbage collection."""
        self.cleanup()
