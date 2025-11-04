# -*- coding: utf-8 -*-
"""Contains wrapper functions for executing shell processes."""

import logging
import os
import shlex
import subprocess
import timeit


def output(command, working_dir=None, environment=None, timeout=600):
    """Executes shell processes and returns output.

    Args:
        command (str or list): The shell command. If string, will be safely parsed.
                              If list, will be executed directly.
        working_dir (str, optional): The working directory of the shell command.
        environment (dict, optional): All environment variables for the shell.
        timeout (int, optional): Timeout in seconds. Default 600 (10 minutes).

    Example:
        >>> output('echo "hi"')
        'hi\n'
        >>> output(['echo', 'hi'])
        'hi\n'

    Returns:
        String: The stdout and stderr of the shell process called.

    Raises:
        ValueError: If command contains shell operators that cannot be safely executed.
        subprocess.TimeoutExpired: If command exceeds timeout.
    """
    try:
        shell_env = os.environ.copy()
        if environment:
            shell_env.update(environment)

        # Detect if we need shell features (pipes, redirects, etc)
        shell_operators = ['|', '>', '<', '>>', '<<', '&', '&&', '||', ';']
        needs_shell = False

        if isinstance(command, str):
            # Check if command uses shell features
            for op in shell_operators:
                if op in command:
                    needs_shell = True
                    break

            if needs_shell:
                # For commands that genuinely need shell, log warning
                logging.warning("Command uses shell operators, executing with shell=True: %s",
                              command[:100])
                cmd_args = command
                use_shell = True
            else:
                # Safe case - parse and execute without shell
                try:
                    cmd_args = shlex.split(command)
                    use_shell = False
                except ValueError as e:
                    logging.error("Failed to parse command: %s", e)
                    raise ValueError(f"Invalid command syntax: {e}")
        elif isinstance(command, list):
            cmd_args = command
            use_shell = False
        else:
            raise TypeError("command must be string or list")

        out = subprocess.check_output(
            cmd_args,
            stderr=subprocess.STDOUT,
            cwd=working_dir,
            shell=use_shell,
            universal_newlines=True,
            executable="/bin/bash" if use_shell else None,
            env=shell_env,
            timeout=timeout,
        )

        # Only log command, not full output (security - output may contain sensitive data)
        if isinstance(command, str):
            logging.debug("Command executed: %s", command[:200])
        else:
            logging.debug("Command executed: %s", ' '.join(command[:10]))

        if out is None:
            out = ""
        return out
    except subprocess.TimeoutExpired as err:
        logging.error("Command timed out after %d seconds: %s", timeout, command)
        raise
    except IOError as err:
        logging.error("IO error executing command: %s", err)
        raise
    except subprocess.CalledProcessError as err:
        logging.error("Execute error output: %s", err.output)
        logging.error("Execute error command: %s", err.cmd)
        logging.error("Execute error return code: %d", err.returncode)
        raise


def timed(command, working_dir=None, environment=None, timeout=3600):
    """Times the execution of the shell process.

    Args:
        command (str or list): The shell command.
        working_dir (str, optional): The working directory of the shell command.
        environment (dict, optional): All environment variables for the shell.
        timeout (int, optional): Timeout in seconds. Default 3600 (1 hour).

    Example:
        >>> timed('sleep 1')
        1.0

    Returns:
        Float: Wall clock time of command execution in seconds.
        None: If command fails.
    """
    import time

    try:
        shell_env = os.environ.copy()
        if environment:
            shell_env.update(environment)

        # Parse command safely
        shell_operators = ['|', '>', '<', '>>', '<<', '&', '&&', '||', ';']
        needs_shell = False

        if isinstance(command, str):
            for op in shell_operators:
                if op in command:
                    needs_shell = True
                    break

            if needs_shell:
                logging.warning("Timed command uses shell operators: %s", command[:100])
                cmd_args = command
                use_shell = True
            else:
                try:
                    cmd_args = shlex.split(command)
                    use_shell = False
                except ValueError as e:
                    logging.error("Failed to parse command: %s", e)
                    return None
        elif isinstance(command, list):
            cmd_args = command
            use_shell = False
        else:
            logging.error("Command must be string or list")
            return None

        # Time the execution
        start_time = time.time()
        try:
            subprocess.check_call(
                cmd_args,
                cwd=working_dir,
                shell=use_shell,
                universal_newlines=True,
                executable="/bin/bash" if use_shell else None,
                env=shell_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout,
            )
            elapsed_time = time.time() - start_time
            return float(elapsed_time)
        except subprocess.CalledProcessError:
            logging.error('Command failed to complete: %s', command)
            return None
        except subprocess.TimeoutExpired:
            logging.error('Command timed out after %d seconds: %s', timeout, command)
            return None
    except IOError as err:
        logging.error("IO error in timed execution: %s", err)
        return None


def pkill(process_name):
    """Kills all processes which contain the desired name.

    Deprecated. Prefer `kill` over this function.

    Args:
        process_name (str): The name to kill all processes with.
    """
    try:
        subprocess.check_call(["pkill", process_name],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.STDOUT)
    except IOError as err:
        logging.error(err)
    except subprocess.CalledProcessError as err:
        logging.debug("Execute error output: %s", err.output)
        logging.debug("Execute error command: %s", err.cmd)
        logging.debug("Execute error return code: %d", err.returncode)


def kill(pid, signal_num=15):
    """Kill process with desired PID.

    Args:
        pid (str or int): The process id to kill.
        signal_num (int): Signal number to send. Default 15 (SIGTERM).

    Returns:
        bool: True if process was killed, False otherwise.

    Raises:
        ValueError: If PID is invalid.
    """
    try:
        # Validate PID
        try:
            pid_int = int(pid)
            if pid_int <= 0:
                raise ValueError(f"Invalid PID: {pid}")
        except (ValueError, TypeError) as e:
            logging.error("Invalid PID value: %s", pid)
            raise ValueError(f"PID must be a positive integer: {e}")

        # Validate signal number
        if not (1 <= signal_num <= 31):
            logging.error("Invalid signal number: %d", signal_num)
            signal_num = 15  # Default to SIGTERM

        subprocess.check_call(
            ["kill", f"-{signal_num}", str(pid_int)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            timeout=5,
        )
        logging.info("Sent signal %d to process %d", signal_num, pid_int)
        return True
    except subprocess.TimeoutExpired:
        logging.error("Kill command timed out for PID %s", pid)
        return False
    except IOError as err:
        logging.error("IO error killing process: %s", err)
        return False
    except subprocess.CalledProcessError as err:
        logging.warning("Failed to kill process %s: %s", pid, err)
        return False
