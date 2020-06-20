# -*- coding: utf-8 -*-
"""Docker benchmarking.

This module handles the downloading, extracting, setting up, and running
Docker.
"""
import logging
import os
import shutil
import statistics
import subprocess
import time

from spet.lib.utilities import download
from spet.lib.utilities import execute
from spet.lib.utilities import extract
from spet.lib.utilities import file
from spet.lib.utilities import grep
from spet.lib.utilities import optimize
from spet.lib.utilities import prettify


class Docker:
    """Docker benchmarking.

    Notes:
        * Requires `ulimit` being optimized to achieve 1000 containers.

    Args:
        version (str): Version number for Docker.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for Docker.
        src_dir (str): The source directory for installing packages.
        docker_dir (str): The source directory for the Docker.
        docker_dir (str): The data directory for the Docker.
        results_dir (str): The results directory for the Docker results.
        commands (list): All major commands run for Docker.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.docker_dir = self.src_dir + "/docker"
        self.data_dir = self.docker_dir + "/data"
        self.results_dir = results_dir + "/docker"
        self.commands = []

    def download(self):
        """Download Docker.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        archive_name = "docker-{}-ce.tgz".format(self.version)
        archive_path = "{}/{}".format(self.src_dir, archive_name)

        if os.path.isfile(archive_path):
            return True

        url = "https://download.docker.com/linux/static/stable/x86_64/" + archive_name

        logging.info("Downloading Docker Community Edition.")
        download.file(url, archive_path)

        if os.path.isfile(archive_path):
            return True
        return False

    def extract(self):
        """Extract Docker.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/docker-{}-ce.tgz".format(self.src_dir, self.version)

        if os.path.isdir(self.docker_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract Docker because "{}" could not be found.'.format(
                    file_path
                )
            )
            return False

        logging.info("Extracting Docker.")

        extract.tar(file_path, self.src_dir)
        # No rename necessary

        if os.path.isdir(self.docker_dir):
            return True
        return False

    def __image_built(self, name, env=None):
        """Check if the named image is built.

        Notes:
            * Requires Docker daemon (`dockerd`) to be running.

        Args:
            name (str): The name of the image.
            env (dict): The shell environment exports.

        Returns:
            Boolean: True if image found otherwise False.
        """
        if env is None:
            env = os.environ.copy()
            env["PATH"] = self.docker_dir + ":" + env["PATH"]

        logging.debug("Checking if Docker image is built.")
        image_output = execute.output(
            "docker images", working_dir=self.docker_dir, environment=env
        )
        found_images = grep.text(image_output, name)

        if found_images:
            return True
        return False

    def build(self, linux_ver, cores=None, cflags=None):
        """Builds the image for Docker to compile the Linux kernel.

        Args:
            linux_ver (str): The Linux kernel version.
            cores (int, optional): The number of Make cores.
            cflags (str, optional): The CFLAGS for GCC.

        Returns:
            Boolean: True if build was successful otherwise False.
        """
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if "-O" not in cflags:
            cflags += " -O3 "

        built = False
        pid_file = "/tmp/docker.pid"
        build_name = "compile_kernel"
        dockerfile = self.docker_dir + "/Dockerfile"

        shell_env = os.environ.copy()
        shell_env["PATH"] = self.docker_dir + ":" + shell_env["PATH"]
        shell_env["CFLAGS"] = cflags

        major_version = linux_ver.split(".")[0]
        url = (
            "http://www.kernel.org/pub/linux/kernel/v{}.x/" "linux-{}.tar.gz"
        ).format(major_version, linux_ver)
        build_cmd = (
            'docker build --build-arg cores={} --build-arg cflags="{}" '
            "--ulimit nofile=1048576:1048576 --build-arg url={} "
            "--build-arg version={} -t {} {}".format(
                cores, cflags, url, linux_ver, build_name, self.docker_dir
            )
        )

        self.commands.append("Build: " + build_cmd)

        if not os.path.isfile(self.docker_dir + "/dockerd"):
            prettify.error_message("Cannot build. Docker directory not found.")
            return False

        os.makedirs(self.data_dir, exist_ok=True)

        # Start Docker daemon
        logging.debug("Starting Docker daemon.")
        subprocess.Popen(
            "{}/dockerd --pidfile {} --data-root {} &".format(
                self.docker_dir, pid_file, self.data_dir
            ),
            cwd=self.docker_dir,
            shell=True,
            env=shell_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(20)

        # Make sure Docker has enough IPs available to assign to containers
        if shutil.which("ifconfig"):
            execute.output("ifconfig docker0 down && ifconfig docker0 172.17.0.1/16 up")

        if not os.path.isfile(dockerfile):
            shutil.copyfile(self.src_dir + "/provided/Dockerfile", dockerfile)

        if not self.__image_built(build_name, env=shell_env):
            build_output = execute.output(
                build_cmd, working_dir=self.docker_dir, environment=shell_env
            )
            logging.debug(build_output)

        if self.__image_built(build_name, env=shell_env):
            logging.info("Docker image built.")
            built = True

        # Stop Docker daemon
        if os.path.exists(pid_file):
            logging.debug("Stopping Docker daemon.")
            pid = file.read(pid_file).strip()
            execute.kill(pid)
            execute.kill(pid)
            time.sleep(5)

        return built

    def run(self, cores=None, cflags=None):
        """Runs Docker containers to compile the Linux kernel.

        Returns:
            If success, a dict containing (unit, times, average, median,
                variance, range).

                unit (str): Score units.
                times (list): All compile times for the kernel.
                average (float): Average of the times.
                median (float): Median of the times.
                variance (float): Variance of the times.
                range (float): Range of the times.

            Else, a dict containing (error).

                error (str): Error message.
        """
        if cores is None:
            cores = 1
        if cflags is None:
            cflags = "-march=native -mtune=native"
        if "-O" not in cflags:
            cflags += " -O3 "
        shell_env = os.environ.copy()
        shell_env["CFLAGS"] = cflags
        shell_env["PATH"] = self.docker_dir + ":" + shell_env["PATH"]

        pid_file = "/tmp/docker.pid"
        build_name = "compile_kernel"
        result_file = self.results_dir + "/times.txt"
        results = {"unit": "s"}
        times = []
        procs = []

        os.makedirs(self.results_dir, exist_ok=True)
        shutil.copyfile(
            self.docker_dir + "/Dockerfile", self.results_dir + "/Dockerfile"
        )

        if not os.path.isfile(self.docker_dir + "/dockerd"):
            message = "Cannot build. Docker directory not found."
            prettify.error_message(message)
            return {"error": message}

        # Start Docker daemon
        subprocess.Popen(
            "{}/dockerd --pidfile {} --data-root {} &".format(
                self.docker_dir, pid_file, self.data_dir
            ),
            cwd=self.docker_dir,
            shell=True,
            env=shell_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logging.info("Docker daemon is running.")
        time.sleep(20)

        if not self.__image_built(build_name, env=shell_env):
            if os.path.exists(pid_file):
                pid = file.read(pid_file).strip()
                execute.kill(pid)
            message = "Cannot build. Docker image not found."
            prettify.error_message(message)
            return {"error": message}

        logging.info("Docker is about to run.")

        # Remove all previously ran containers
        try:
            containers = execute.output(
                "{}/docker ps -a -q".format(self.docker_dir),
                working_dir=self.docker_dir,
                environment=shell_env,
            )
            if containers:
                execute.output(
                    "{0}/docker rm $({0}/docker ps -a -q)".format(self.docker_dir),
                    working_dir=self.docker_dir,
                    environment=shell_env,
                )
        except subprocess.SubprocessError as err:
            logging.debug(err)

        optimize.prerun()
        time.sleep(10)

        for count in range(0, 100):
            test_name = build_name + "_test{}".format(count)
            # Note: We avoid using `-i -t` because it causes TTY issues
            #       with SSH connections.
            run_command = (
                "{}/docker run --ulimit nofile=1048576:1048576 "
                '-e "cores={}" -e "cflags={}" --name {} {}'.format(
                    self.docker_dir, cores, cflags, test_name, build_name
                )
            )
            if count == 0:
                self.commands.append("Run: " + run_command)

            proc = subprocess.Popen(
                run_command,
                shell=True,
                cwd=self.docker_dir,
                env=shell_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            procs.append(proc)

        for proc in procs:
            stdout = proc.communicate()[0]
            if isinstance(stdout, bytes):
                stdout = stdout.decode()
            stdout = stdout.strip()
            try:
                stdout = float(stdout)
                file.write(result_file, "{}\n".format(stdout), append=True)
                times.append(stdout)
            except ValueError:
                logging.debug("Container failed to finish.")
                logging.debug(stdout)

        # Remove all previously ran containers
        try:
            containers = execute.output(
                "{}/docker ps -a -q".format(self.docker_dir),
                working_dir=self.docker_dir,
                environment=shell_env,
            )
            if containers:
                execute.output(
                    "{0}/docker stop $({0}/docker ps -a -q)".format(self.docker_dir),
                    working_dir=self.docker_dir,
                    environment=shell_env,
                )
                execute.output(
                    "{0}/docker rm $({0}/docker ps -a -q)".format(self.docker_dir),
                    working_dir=self.docker_dir,
                    environment=shell_env,
                )
        except subprocess.SubprocessError as err:
            logging.debug(err)

        # Stop Docker daemon
        if os.path.exists(pid_file):
            logging.info("Docker daemon is turning off.")
            pid = file.read(pid_file).strip()
            execute.kill(pid)
            execute.kill(pid)
            time.sleep(5)

        if times:
            results["times"] = times
            results["median"] = statistics.median(times)
            results["average"] = statistics.mean(times)
            results["variance"] = statistics.variance(times)
            sorted_times = sorted(times)
            results["range"] = sorted_times[-1] - sorted_times[0]
        else:
            results["error"] = "No container times available."

        return results
