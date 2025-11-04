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
from spet.lib.utilities import secure_temp


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
        data_dir (str): The data directory for the Docker.
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
        self.daemon_process = None

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
        try:
            download.file(url, archive_path)
            if os.path.isfile(archive_path):
                return True
        except Exception as e:
            logging.error("Failed to download Docker: %s", e)
            return False

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
            logging.error('Cannot extract Docker because "%s" could not be found.', file_path)
            prettify.error_message(
                'Cannot extract Docker because "{}" could not be found.'.format(
                    file_path))
            return False

        logging.info("Extracting Docker.")

        try:
            extract.tar(file_path, self.src_dir)
            # No rename necessary

            if os.path.isdir(self.docker_dir):
                return True
        except Exception as e:
            logging.error("Failed to extract Docker: %s", e)
            prettify.error_message(f"Failed to extract Docker: {e}")
            return False

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
        try:
            image_output = execute.output(
                ["docker", "images"],
                working_dir=self.docker_dir,
                environment=env
            )
            found_images = grep.text(image_output, name)

            if found_images:
                return True
        except Exception as e:
            logging.error("Failed to check Docker images: %s", e)

        return False

    def _start_docker_daemon(self, pid_file_path, shell_env):
        """Start Docker daemon with secure PID file.

        Args:
            pid_file_path (str): Path to PID file.
            shell_env (dict): Environment variables.

        Returns:
            subprocess.Popen: The daemon process, or None on failure.
        """
        dockerd_path = os.path.join(self.docker_dir, "dockerd")

        if not os.path.isfile(dockerd_path):
            logging.error("dockerd not found at %s", dockerd_path)
            return None

        # Start Docker daemon without shell=True
        logging.debug("Starting Docker daemon.")
        try:
            proc = subprocess.Popen(
                [dockerd_path, "--pidfile", pid_file_path, "--data-root", self.data_dir],
                cwd=self.docker_dir,
                env=shell_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Give daemon time to start
            time.sleep(20)

            # Verify daemon started
            if proc.poll() is not None:
                logging.error("Docker daemon failed to start (exit code %d)", proc.returncode)
                return None

            logging.info("Docker daemon started successfully")
            return proc
        except Exception as e:
            logging.error("Failed to start Docker daemon: %s", e)
            return None

    def _stop_docker_daemon(self, pid_file_path, daemon_process=None):
        """Stop Docker daemon safely.

        Args:
            pid_file_path (str): Path to PID file.
            daemon_process (subprocess.Popen, optional): The daemon process object.
        """
        logging.debug("Stopping Docker daemon.")

        # Try to read PID from file
        if os.path.exists(pid_file_path):
            try:
                pid = file.read(pid_file_path).strip()
                if pid:
                    execute.kill(pid, signal_num=15)  # SIGTERM
                    time.sleep(2)
                    # If still running, force kill
                    execute.kill(pid, signal_num=9)  # SIGKILL
            except Exception as e:
                logging.warning("Failed to kill daemon via PID file: %s", e)

        # Also try terminate via process object
        if daemon_process and daemon_process.poll() is None:
            try:
                daemon_process.terminate()
                daemon_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                daemon_process.kill()
                daemon_process.wait()
            except Exception as e:
                logging.warning("Failed to terminate daemon process: %s", e)

        time.sleep(5)

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

        # Validate inputs
        try:
            cores = int(cores)
            if cores < 1:
                cores = 1
        except (ValueError, TypeError):
            logging.error("Invalid cores value: %s", cores)
            return False

        if not isinstance(linux_ver, str) or not linux_ver:
            logging.error("Invalid Linux version: %s", linux_ver)
            return False

        built = False
        build_name = "compile_kernel"
        dockerfile = self.docker_dir + "/Dockerfile"

        shell_env = os.environ.copy()
        shell_env["PATH"] = self.docker_dir + ":" + shell_env["PATH"]
        shell_env["CFLAGS"] = cflags

        major_version = linux_ver.split(".")[0]
        url = ("http://www.kernel.org/pub/linux/kernel/v{}.x/"
               "linux-{}.tar.gz").format(major_version, linux_ver)

        if not os.path.isfile(self.docker_dir + "/dockerd"):
            prettify.error_message("Cannot build. Docker directory not found.")
            return False

        os.makedirs(self.data_dir, exist_ok=True)

        # Use secure temporary PID file
        with secure_temp.SecurePidFile(prefix="docker_", suffix=".pid") as pid_file:
            # Start Docker daemon
            daemon_proc = self._start_docker_daemon(pid_file.name, shell_env)
            if not daemon_proc:
                prettify.error_message("Failed to start Docker daemon.")
                return False

            self.daemon_process = daemon_proc

            try:
                # Make sure Docker has enough IPs available to assign to containers
                if shutil.which("ifconfig"):
                    try:
                        execute.output(["ifconfig", "docker0", "down"])
                        execute.output(["ifconfig", "docker0", "172.17.0.1/16", "up"])
                    except Exception as e:
                        logging.warning("Failed to configure docker0 interface: %s", e)

                if not os.path.isfile(dockerfile):
                    shutil.copyfile(self.src_dir + "/provided/Dockerfile", dockerfile)

                if not self.__image_built(build_name, env=shell_env):
                    # Build Docker image using list-based command
                    build_cmd = [
                        "docker", "build",
                        "--build-arg", f"cores={cores}",
                        "--build-arg", f"cflags={cflags}",
                        "--ulimit", "nofile=1048576:1048576",
                        "--build-arg", f"url={url}",
                        "--build-arg", f"version={linux_ver}",
                        "-t", build_name,
                        self.docker_dir
                    ]

                    build_cmd_str = " ".join(build_cmd)
                    self.commands.append("Build: " + build_cmd_str)

                    logging.info("Building Docker image...")
                    try:
                        build_output = execute.output(
                            build_cmd,
                            working_dir=self.docker_dir,
                            environment=shell_env,
                            timeout=3600  # 1 hour timeout for build
                        )
                        logging.debug(build_output)
                    except Exception as e:
                        logging.error("Docker build failed: %s", e)
                        prettify.error_message(f"Docker build failed: {e}")

                if self.__image_built(build_name, env=shell_env):
                    logging.info("Docker image built.")
                    built = True
                else:
                    logging.error("Docker image not found after build")

            finally:
                # Stop Docker daemon
                self._stop_docker_daemon(pid_file.name, daemon_proc)
                self.daemon_process = None

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

        # Validate inputs
        try:
            cores = int(cores)
            if cores < 1:
                cores = 1
        except (ValueError, TypeError):
            logging.error("Invalid cores value: %s", cores)
            return {"error": "Invalid cores value"}

        shell_env = os.environ.copy()
        shell_env["CFLAGS"] = cflags
        shell_env["PATH"] = self.docker_dir + ":" + shell_env["PATH"]

        build_name = "compile_kernel"
        result_file = self.results_dir + "/times.txt"
        results = {"unit": "s"}
        times = []
        procs = []

        os.makedirs(self.results_dir, exist_ok=True)
        shutil.copyfile(self.docker_dir + "/Dockerfile",
                        self.results_dir + "/Dockerfile")

        if not os.path.isfile(self.docker_dir + "/dockerd"):
            message = "Cannot run. Docker directory not found."
            prettify.error_message(message)
            return {"error": message}

        # Use secure temporary PID file
        with secure_temp.SecurePidFile(prefix="docker_", suffix=".pid") as pid_file:
            # Start Docker daemon
            daemon_proc = self._start_docker_daemon(pid_file.name, shell_env)
            if not daemon_proc:
                return {"error": "Failed to start Docker daemon"}

            self.daemon_process = daemon_proc

            try:
                if not self.__image_built(build_name, env=shell_env):
                    message = "Cannot run. Docker image not found."
                    prettify.error_message(message)
                    return {"error": message}

                logging.info("Docker is about to run.")

                # Remove all previously ran containers
                self._cleanup_containers(shell_env)

                optimize.prerun()
                time.sleep(10)

                for count in range(0, 100):
                    test_name = build_name + "_test{}".format(count)

                    # Use list-based command for docker run
                    run_cmd = [
                        os.path.join(self.docker_dir, "docker"),
                        "run",
                        "--ulimit", "nofile=1048576:1048576",
                        "-e", f"cores={cores}",
                        "-e", f"cflags={cflags}",
                        "--name", test_name,
                        build_name
                    ]

                    if count == 0:
                        self.commands.append("Run: " + " ".join(run_cmd))

                    try:
                        proc = subprocess.Popen(
                            run_cmd,
                            cwd=self.docker_dir,
                            env=shell_env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                        )
                        procs.append(proc)
                    except Exception as e:
                        logging.error("Failed to start container %s: %s", test_name, e)

                # Wait for all containers to finish
                for proc in procs:
                    try:
                        stdout, _ = proc.communicate(timeout=3600)  # 1 hour timeout per container
                        if isinstance(stdout, bytes):
                            stdout = stdout.decode()
                        stdout = stdout.strip()
                        try:
                            time_value = float(stdout)
                            file.write(result_file, "{}\n".format(time_value), append=True)
                            times.append(time_value)
                        except ValueError:
                            logging.debug("Container failed to finish or returned invalid output.")
                            logging.debug(stdout)
                    except subprocess.TimeoutExpired:
                        logging.error("Container timed out")
                        proc.kill()
                    except Exception as e:
                        logging.error("Error communicating with container: %s", e)

                # Remove all containers
                self._cleanup_containers(shell_env)

                if times:
                    results["times"] = times
                    results["median"] = statistics.median(times)
                    results["average"] = statistics.mean(times)
                    if len(times) > 1:
                        results["variance"] = statistics.variance(times)
                    else:
                        results["variance"] = 0
                    sorted_times = sorted(times)
                    results["range"] = sorted_times[-1] - sorted_times[0] if len(sorted_times) > 1 else 0
                else:
                    results["error"] = "No container times available."

            finally:
                # Stop Docker daemon
                self._stop_docker_daemon(pid_file.name, daemon_proc)
                self.daemon_process = None

        return results

    def _cleanup_containers(self, shell_env):
        """Remove all Docker containers.

        Args:
            shell_env (dict): Environment variables.
        """
        docker_bin = os.path.join(self.docker_dir, "docker")

        try:
            # Get list of all containers
            containers = execute.output(
                [docker_bin, "ps", "-a", "-q"],
                working_dir=self.docker_dir,
                environment=shell_env,
            )

            if containers and containers.strip():
                container_ids = containers.strip().split("\n")

                # Stop containers
                try:
                    stop_cmd = [docker_bin, "stop"] + container_ids
                    execute.output(
                        stop_cmd,
                        working_dir=self.docker_dir,
                        environment=shell_env,
                        timeout=300
                    )
                except Exception as e:
                    logging.warning("Failed to stop containers: %s", e)

                # Remove containers
                try:
                    rm_cmd = [docker_bin, "rm"] + container_ids
                    execute.output(
                        rm_cmd,
                        working_dir=self.docker_dir,
                        environment=shell_env,
                        timeout=300
                    )
                except Exception as e:
                    logging.warning("Failed to remove containers: %s", e)

        except Exception as e:
            logging.warning("Failed to cleanup containers: %s", e)
