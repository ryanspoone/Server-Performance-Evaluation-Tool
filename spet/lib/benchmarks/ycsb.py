# -*- coding: utf-8 -*-
"""YCSB NoSQL and SQL benchmarking.

This module handles the downloading, extracting, setting up, and running
MySQL and Cassandra.
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

# pylint disable=E1135


class NoSQL:
    """YCSB NoSQL benchmarking.

    Args:
        version (str): Version number for zlib.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for YCSB.
        src_dir (str): The source directory for installing packages.
        ycsb_dir (str): The source directory for the YCSB.
        results_dir (str): The results directory for the YCSB results.
    """

    def __init__(self, version, root_dir, results_dir):
        self.version = version
        self.src_dir = root_dir + "/src"
        self.ycsb_dir = self.src_dir + "/ycsb"
        self.results_dir = results_dir + "/ycsb_nosql"
        self.commands = []

    def download(self):
        """Download YCSB.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        url = (
            "https://github.com/brianfrankcooper/YCSB/releases/download/"
            "{0}/ycsb-{0}.tar.gz".format(self.version)
        )
        archive_path = "{}/ycsb-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isfile(archive_path):
            logging.debug('"%s" exists, exiting early.', archive_path)
            return True

        logging.info("Downloading YCSB.")
        download.file(url, archive_path)
        logging.debug("Downloading YCSB complete.")

        if os.path.isfile(archive_path):
            logging.debug('"%s" exists.', archive_path)
            return True
        return False

    def extract(self):
        """Extract YCSB.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        file_path = "{}/ycsb-{}.tar.gz".format(self.src_dir, self.version)

        if os.path.isdir(self.ycsb_dir):
            return True

        if not os.path.isfile(file_path):
            prettify.error_message(
                'Cannot extract YCSB because "{}" could not be found.'.format(file_path)
            )
            return False

        logging.info("Extracting YCSB")

        extract.tar(file_path, self.src_dir)
        os.rename("{}/ycsb-{}".format(self.src_dir, self.version), self.ycsb_dir)

        if os.path.isdir(self.ycsb_dir):
            return True
        return False

    def setup(self, threads):
        """Setup Cassandra's "ycsb" table and load basic records.

        Args:
            threads (int): The number of threads on the system.
        """
        pid = None
        shell_env = os.environ.copy()
        maven_dir = self.src_dir + "/maven"

        if os.path.isdir(maven_dir):
            shell_env["M2_HOME"] = maven_dir
            shell_env["M2"] = maven_dir + "/bin"
        else:
            return False

        cassandra_dir = self.src_dir + "/cassandra"

        if not os.path.isdir(cassandra_dir):
            prettify.error_message(
                'Cannot start Cassandra because "{}" could not be found.'.format(
                    cassandra_dir
                )
            )
            return False

        if os.path.exists(self.src_dir + "/cassandra/data/data/ycsb"):
            logging.debug(
                'Skipping Cassandra setup because the "ycsb" table ' "already exists."
            )
            return True

        # Start Cassandra service
        subprocess.Popen(
            "./bin/cassandra -R -p /tmp/cassandra.pid &",
            shell=True,
            cwd=cassandra_dir,
            env=shell_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(20)

        if os.path.isfile("/tmp/cassandra.pid"):
            pid = file.read("/tmp/cassandra.pid").strip()

        if not pid or not os.path.dirname("/proc/" + pid):
            text = "Cassandra failed to start."
            prettify.error_message(text)
            return False

        # Setup table schema
        execute.output(
            "./bin/cqlsh -f {}/provided/create-table.cql".format(self.src_dir),
            working_dir=cassandra_dir,
            environment=shell_env,
        )

        load_cmd = (
            "./bin/ycsb load cassandra-cql -s -P workloads/workloada "
            '-p hosts="localhost" -threads {} -p recordcount=10000000'.format(threads)
        )

        self.commands.append("Load: " + load_cmd)

        # Load YCSB records
        execute.output(load_cmd, working_dir=self.ycsb_dir, environment=shell_env)

        # Stop Cassandra service
        if pid:
            execute.kill(pid)
            execute.kill(pid)
            execute.kill(pid)

        return True

    def run(self, threads):
        """Run YCSB with Cassandra three times.

        Args:
            threads (int): The number of threads on the system.
        """
        pid = None
        shell_env = os.environ.copy()
        maven_dir = self.src_dir + "/maven"
        error = False
        results = {"unit": {"throughput": "ops/sec", "latency": "us"}}

        if os.path.isdir(maven_dir):
            shell_env["M2_HOME"] = maven_dir
            shell_env["M2"] = maven_dir + "/bin"
        else:
            prettify.error_message("Maven could not be found.")
            return False

        cassandra_dir = self.src_dir + "/cassandra"

        if not os.path.exists(cassandra_dir + "/data/data/ycsb"):
            text = 'Unable to find "ycsb" table in Cassandra.'
            prettify.error_message(text)
            return {"error": text}

        read_latency_results = []
        update_latency_results = []
        throughput_results = []

        os.makedirs(self.results_dir, exist_ok=True)

        # Start Cassandra service
        subprocess.Popen(
            "./bin/cassandra -R -p /tmp/cassandra.pid &",
            shell=True,
            cwd=cassandra_dir,
            env=shell_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(20)

        if os.path.isfile("/tmp/cassandra.pid"):
            pid = file.read("/tmp/cassandra.pid").strip()

        if not pid or not os.path.dirname("/proc/" + pid):
            text = "Cassandra failed to start."
            prettify.error_message(text)
            return {"error": text}

        run_cmd = (
            "./bin/ycsb run cassandra-cql -s -P workloads/workloada "
            '-p hosts="localhost" -threads {} '
            "-p operationcount=10000000".format(threads)
        )

        self.commands.append("Run: " + run_cmd)

        for count in range(1, 4):
            run_num = "run" + str(count)
            result_file = "{}/ycsb-nosql_{}.txt".format(self.results_dir, run_num)

            optimize.prerun()
            time.sleep(10)

            output = execute.output(
                run_cmd, working_dir=self.ycsb_dir, environment=shell_env
            )

            file.write(result_file, output)

            if "UPDATE-FAILED" in output or "READ-FAILED" in output:
                error = True
                break

            throughput_line = grep.text(output, r"\[OVERALL\], Throughput\(ops/sec\),")
            if throughput_line:
                throughput = float(throughput_line[-1].split(",")[2].strip())
                throughput_results.append(throughput)

            readlat_line = grep.text(output, r"\[READ\], 95thPercentileLatency\(us\),")
            if readlat_line:
                readlat = float(readlat_line[-1].split(",")[2].strip())
                read_latency_results.append(readlat)

            updatelat_line = grep.text(
                output, r"\[UPDATE\], 95thPercentileLatency\(us\),"
            )
            if updatelat_line:
                updatelat = float(updatelat_line[-1].split(",")[2].strip())
                update_latency_results.append(updatelat)

            if throughput_line and readlat_line and updatelat_line:
                results[run_num] = {
                    "throughput": throughput,
                    "read_latency": readlat,
                    "update_latency": updatelat,
                }

        # Stop Cassandra service
        if pid:
            execute.kill(pid)
            execute.kill(pid)
            execute.kill(pid)

        if error:
            return {"error": "YCSB failed to update and/or read database."}

        if "run1" in results:
            results["average"] = {}
            results["median"] = {}
            results["variance"] = {}
            results["range"] = {}

            results["average"]["throughput"] = statistics.mean(throughput_results)
            results["median"]["throughput"] = statistics.median(throughput_results)
            results["variance"]["throughput"] = statistics.variance(throughput_results)
            sorted_throughput = sorted(throughput_results)
            results["range"]["throughput"] = (
                sorted_throughput[-1] - sorted_throughput[0]
            )

            results["average"]["read_latency"] = statistics.mean(read_latency_results)
            results["median"]["read_latency"] = statistics.median(read_latency_results)
            results["variance"]["read_latency"] = statistics.variance(
                read_latency_results
            )
            sorted_read_latency = sorted(read_latency_results)
            results["range"]["read_latency"] = (
                sorted_read_latency[-1] - sorted_read_latency[0]
            )

            results["average"]["update_latency"] = statistics.mean(
                update_latency_results
            )
            results["median"]["update_latency"] = statistics.median(
                update_latency_results
            )
            results["variance"]["update_latency"] = statistics.variance(
                update_latency_results
            )
            sorted_update_latency = sorted(update_latency_results)
            results["range"]["update_latency"] = (
                sorted_update_latency[-1] - sorted_update_latency[0]
            )

        logging.info("YCSB Cassandra results: %s", str(results))

        return results


class SQL:
    """YCSB SQL benchmarking.

    Notes:
        * Requires `jconnect` to be installed.

    Args:
        version (str): Version number for zlib.
        jconnect_ver (str): Version number for jconnect.
        root_dir (str): The main directory for SPET.
        results_dir (str): The SPET run's result directory.

    Attributes:
        version (str): Version number for YCSB.
        jconnect_ver (str): Version number for jconnect.
        src_dir (str): The source directory for installing packages.
        ycsb_dir (str): The source directory for the YCSB.
        results_dir (str): The results directory for the YCSB results.
    """

    def __init__(self, version, jconnect_ver, root_dir, results_dir):
        self.version = version
        self.jconnect_ver = jconnect_ver
        self.src_dir = root_dir + "/src"
        self.ycsb_dir = self.src_dir + "/ycsb"
        self.results_dir = results_dir + "/ycsb_sql"
        self.commands = []

    def download(self):
        """Download YCSB.

        Returns:
            Boolean: True if download was successful otherwise False.
        """
        ycsb_url = (
            "https://github.com/brianfrankcooper/YCSB/releases/"
            "download/{0}/ycsb-{0}.tar.gz".format(self.version)
        )
        ycsb_archive_path = "{}/ycsb-{}.tar.gz".format(self.src_dir, self.version)

        jconnect_url = (
            "https://dev.mysql.com/get/Downloads/Connector-J/"
            "mysql-connector-java-{}.tar.gz".format(self.jconnect_ver)
        )
        jconnect_path = "{}/mysql-connector-java-{}.tar.gz".format(
            self.src_dir, self.jconnect_ver
        )
        if not os.path.isfile(ycsb_archive_path):
            logging.info("Downloading YCSB.")
            download.file(ycsb_url, ycsb_archive_path)
            logging.debug("Downloading YCSB complete.")

        if not os.path.isfile(jconnect_path):
            logging.info("Downloading J Connector.")
            download.file(jconnect_url, jconnect_path)
            logging.debug("Downloading J Connector complete.")

        if os.path.isfile(ycsb_archive_path) and os.path.isfile(jconnect_path):
            logging.debug('"%s" and "%s" exists.', ycsb_archive_path, jconnect_path)
            return True
        return False

    def extract(self):
        """Extract YCSB.

        Returns:
            Boolean: True if extraction was successful otherwise False.
        """
        ycsb_archive_path = "{}/ycsb-{}.tar.gz".format(self.src_dir, self.version)
        jconnect_dir = "{}/mysql-connector-java-{}".format(
            self.src_dir, self.jconnect_ver
        )
        jconnect_archive_path = jconnect_dir + ".tar.gz"
        jconn_final = self.src_dir + "/mysql-connector-java"

        if not os.path.isfile(ycsb_archive_path):
            prettify.error_message(
                'Cannot extract YCSB because "{}" could not be found.'.format(
                    ycsb_archive_path
                )
            )
            return False

        if not os.path.isfile(jconnect_archive_path):
            prettify.error_message(
                'Cannot extract MySQL J Connector because "{}" could not be'
                " found.".format(jconnect_archive_path)
            )
            return False

        if not os.path.isdir(self.ycsb_dir):
            logging.info("Extracting YCSB.")
            extract.tar(ycsb_archive_path, self.src_dir)
            os.rename("{}/ycsb-{}".format(self.src_dir, self.version), self.ycsb_dir)
            logging.info("Extracting YCSB Complete.")

        if not os.path.isdir(jconn_final):
            logging.info("Extracting MySQL J Connector.")
            extract.tar(jconnect_archive_path, self.src_dir)
            os.rename(jconnect_dir, jconn_final)
            logging.info("Extracting MySQL J Connector Complete.")

        if os.path.isdir(self.ycsb_dir) and os.path.isdir(jconn_final):
            return True
        return False

    def setup(self, threads):
        """Setup YCSB J Connector, MySQL's "ycsb" table, and load basic records.

        Args:
            threads (int): The number of threads on the system.
        """
        shell_env = os.environ.copy()
        maven_dir = self.src_dir + "/maven"

        if os.path.isdir(maven_dir):
            shell_env["M2_HOME"] = maven_dir
            shell_env["M2"] = maven_dir + "/bin"
        else:
            prettify.error_message("Maven could not be found.")
            return False

        mysql_dir = self.src_dir + "/mysql"
        mysql_data = mysql_dir + "/mysql-files"

        jconnect_jar = "mysql-connector-java-{}-bin.jar".format(self.jconnect_ver)
        jconnect_path = "{}/mysql-connector-java/{}".format(self.src_dir, jconnect_jar)
        jdbc_binding_path = "{}/jdbc-binding/lib/{}".format(self.ycsb_dir, jconnect_jar)

        if not os.path.isdir(mysql_dir):
            prettify.error_message(
                'Cannot start MySQL because "{}" could not be found.'.format(mysql_dir)
            )
            return False

        if os.path.exists(mysql_data + "/ycsb"):
            logging.debug(
                'Skipping MySQL setup because the "ycsb" table ' "already exists."
            )
            return True

        # Start MySQL service
        subprocess.Popen(
            "{0}/bin/mysqld_safe --user=root --basedir={0} --datadir={1} "
            "--plugin-dir={0}/lib/plugin --pid-file=/tmp/mysql.pid "
            "--log-error=ycsb.err &".format(mysql_dir, mysql_data),
            cwd=mysql_dir,
            shell=True,
            env=shell_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(20)

        # Setup ycsb database
        schema_output = execute.output(
            "./bin/mysql -uroot --skip-password < "
            "{}/provided/create-table.mysql".format(self.src_dir),
            working_dir=mysql_dir,
            environment=shell_env,
        )

        logging.debug(schema_output)
        if os.path.isfile(mysql_data + "/ycsb.err"):
            logging.debug(file.read(mysql_data + "/ycsb.err"))

        shutil.copyfile(jconnect_path, jdbc_binding_path)

        # Load YCSB records
        load_cmd = (
            "./bin/ycsb load jdbc -s -P workloads/workloada -p "
            "db.driver=com.mysql.jdbc.Driver -p "
            "db.url=jdbc:mysql://localhost:3306/ycsb?useSSL=false -p "
            'db.user=root -p db.passwd="" -threads {} '
            "-p recordcount=1000000".format(threads)
        )

        self.commands.append("Load: " + load_cmd)

        load_ycsb = execute.output(
            "./bin/ycsb load jdbc -s -P workloads/workloada -p "
            "db.driver=com.mysql.jdbc.Driver -p "
            "db.url=jdbc:mysql://localhost:3306/ycsb?useSSL=false -p "
            'db.user=root -p db.passwd="" -threads {} -p recordcount=1000000'.format(
                threads
            ),
            working_dir=self.ycsb_dir,
            environment=shell_env,
        )

        logging.debug(load_ycsb)
        if os.path.isfile(mysql_data + "/ycsb.err"):
            logging.debug(file.read(mysql_data + "/ycsb.err"))

        # Stop MySQL service
        if os.path.exists("/tmp/mysql.pid"):
            pid = file.read("/tmp/mysql.pid").strip()
            execute.kill(pid)
            execute.kill(pid)
            execute.kill(pid)

    def run(self, threads):
        """Run YCSB with MySQL three times.

        Args:
            threads (int): The number of threads on the system.
        """
        shell_env = os.environ.copy()
        maven_dir = self.src_dir + "/maven"
        error = False
        results = {"unit": {"throughput": "ops/sec", "latency": "us"}}

        if os.path.isdir(maven_dir):
            shell_env["M2_HOME"] = maven_dir
            shell_env["M2"] = maven_dir + "/bin"
        else:
            return {"error": "Maven not found."}

        mysql_dir = self.src_dir + "/mysql"
        mysql_data = mysql_dir + "/mysql-files"

        if not os.path.exists(mysql_data + "/ycsb"):
            text = 'Unable to find "ycsb" table in MySQL.'
            prettify.error_message(text)
            return {"error": text}

        os.makedirs(self.results_dir, exist_ok=True)

        # Start MySQL service
        subprocess.Popen(
            "{0}/bin/mysqld_safe --user=root --basedir={0} --datadir={1} "
            "--plugin-dir={0}/lib/plugin --pid-file=/tmp/mysql.pid "
            "--log-error=ycsb.err &".format(mysql_dir, mysql_data),
            cwd=mysql_dir,
            shell=True,
            env=shell_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(20)

        read_latency_results = []
        update_latency_results = []
        throughput_results = []

        run_cmd = (
            "./bin/ycsb run jdbc -s -P workloads/workloada -p "
            "db.driver=com.mysql.jdbc.Driver -p "
            "db.url=jdbc:mysql://localhost:3306/ycsb?useSSL=false -p "
            'db.user=root -p db.passwd="" -threads {} -p '
            "operationcount=1000000".format(threads)
        )

        self.commands.append("Run: " + run_cmd)

        for count in range(1, 4):
            run_num = "run" + str(count)
            result_file = "{}/ycsb-sql_{}.txt".format(self.results_dir, run_num)

            optimize.prerun()
            time.sleep(10)

            # Run YCSB
            output = execute.output(
                run_cmd, working_dir=self.ycsb_dir, environment=shell_env
            )

            file.write(result_file, output)

            if "UPDATE-FAILED" in output or "READ-FAILED" in output:
                error = True
                break

            throughput_line = grep.text(output, r"\[OVERALL\], Throughput\(ops/sec\),")
            if throughput_line:
                throughput = float(throughput_line[-1].split(",")[2].strip())
                throughput_results.append(throughput)

            readlat_line = grep.text(output, r"\[READ\], 95thPercentileLatency\(us\),")
            if readlat_line:
                readlat = float(readlat_line[-1].split(",")[2].strip())
                read_latency_results.append(readlat)

            updatelat_line = grep.text(
                output, r"\[UPDATE\], 95thPercentileLatency\(us\),"
            )
            if updatelat_line:
                updatelat = float(updatelat_line[-1].split(",")[2].strip())
                update_latency_results.append(updatelat)

            if throughput_line and readlat_line and updatelat_line:
                results[run_num] = {
                    "throughput": throughput,
                    "read_latency": readlat,
                    "update_latency": updatelat,
                }

        # Stop MySQL service
        if os.path.exists("/tmp/mysql.pid"):
            pid = file.read("/tmp/mysql.pid").strip()
            execute.kill(pid)
            execute.kill(pid)
            execute.kill(pid)

        if error:
            return {"error": "YCSB failed to update and/or read database."}

        if "run1" in results:
            results["average"] = {}
            results["median"] = {}
            results["variance"] = {}
            results["range"] = {}

            results["average"]["throughput"] = statistics.mean(throughput_results)
            results["median"]["throughput"] = statistics.median(throughput_results)
            results["variance"]["throughput"] = statistics.variance(throughput_results)
            sorted_throughput = sorted(throughput_results)
            results["range"]["throughput"] = (
                sorted_throughput[-1] - sorted_throughput[0]
            )

            results["average"]["read_latency"] = statistics.mean(read_latency_results)
            results["median"]["read_latency"] = statistics.median(read_latency_results)
            results["variance"]["read_latency"] = statistics.variance(
                read_latency_results
            )
            sorted_read_latency = sorted(read_latency_results)
            results["range"]["read_latency"] = (
                sorted_read_latency[-1] - sorted_read_latency[0]
            )

            results["average"]["update_latency"] = statistics.mean(
                update_latency_results
            )
            results["median"]["update_latency"] = statistics.median(
                update_latency_results
            )
            results["variance"]["update_latency"] = statistics.variance(
                update_latency_results
            )
            sorted_update_latency = sorted(update_latency_results)
            results["range"]["update_latency"] = (
                sorted_update_latency[-1] - sorted_update_latency[0]
            )

        logging.info("YCSB MySQL results: %s", str(results))

        return results
