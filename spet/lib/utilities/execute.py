# -*- coding: utf-8 -*-
"""Contains wrapper functions for executing shell processes."""

import logging
import os
import subprocess
import timeit


def output(command, working_dir=None, environment=None):
    """Executes shell processes and returns output.

    Args:
        command (str): The shell command.
        working_dir (str, optional): The working directory of the shell
            command.
        environment (dict, optional): All environment variables for the shell.

    Example:
        >>> output('echo "hi"')
        'hi\n'

    Returns:
        String: The stdout and stderr of the shell process called.
    """
    try:
        shell_env = os.environ.copy()
        if environment:
            shell_env.update(environment)
        out = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            cwd=working_dir,
            shell=True,
            universal_newlines=True,
            executable="/bin/bash",
            env=shell_env,
        )
        logging.debug("%s:\n%s", command, out)
        if out is None:
            out = ""
        return out
    except IOError as err:
        logging.debug(err)
    except subprocess.CalledProcessError as err:
        logging.debug("Execute error output: %s", err.output)
        logging.debug("Execute error command: %s", err.cmd)
        logging.debug("Execute error return code: %d", err.returncode)


def timed(command, working_dir=None, environment=None):
    """Times the execution of the shell process.

    Args:
        command (str): The shell command.
        working_dir (str, optional): The working directory of the shell
            command.
        environment (dict, optional): All environment variables for the shell.

    Example:
        >>> timed('sleep 10')
        10

    Returns:
        Float: CPU time of command.
    """
    try:
        shell_env = os.environ.copy()
        if environment:
            shell_env.update(environment)

        command = command.replace("'", r"\'")

        statement = (
            "subprocess.check_call('{}', cwd='{}', shell=True, "
            "universal_newlines=True, executable='/bin/bash', env={}, "
            "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)".format(
                command, working_dir, repr(shell_env)))

        # This way of timing it allows us to easily replicate timing measures
        # from the command line with the same amount of precision.
        try:
            time = timeit.timeit(stmt=statement,
                                 setup="import subprocess",
                                 number=1)
            return float(time)
        except subprocess.CalledProcessError:
            logging.debug('"%s" failed to complete.', command)
            return None
    except IOError as err:
        logging.debug(err)


def pkill(process_name):
    """Kills all processes which contain the desired name.

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


def kill(pid):
    """Kill process with desired PID.

    Args:
        pid (str): The process id to kill.
    """
    try:
        subprocess.check_call(["kill", pid],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.STDOUT)
    except IOError as err:
        logging.debug(err)
    except subprocess.CalledProcessError as err:
        logging.debug("Execute error output: %s", err.output)
        logging.debug("Execute error command: %s", err.cmd)
        logging.debug("Execute error return code: %d", err.returncode)
