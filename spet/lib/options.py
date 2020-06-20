# -*- coding: utf-8 -*-
"""Argument flag options for SPET."""

import logging
from argparse import ArgumentParser


class Options:
    """Argument flag options for SPET.

    Attributes:
        known (str): The source directory for installing packages.
        unknown (str): The source directory for the HPL.
    """

    def __init__(self):
        self._init_parser()
        self.known = []
        self.unknown = []

    def _init_parser(self):
        """Overrides usage that is by default."""
        usage = "spet"
        self.parser = ArgumentParser(usage=usage)
        self.parser.add_argument(
            "-v",
            "--verbose",
            help="Show additional output for SPET progress.",
            action="store_const",
            dest="loglevel",
            const=logging.INFO,
            default=logging.WARNING,
        )
        self.parser.add_argument(
            "-d",
            "--debug",
            help="Show debugging statements.",
            action="store_const",
            dest="loglevel",
            const=logging.DEBUG,
        )
        self.parser.add_argument(
            "-e",
            "--exclude",
            dest="excludes",
            nargs="+",
            action="store",
            type=str,
            help="Exclude the listed benchmark(s) from this run.",
        )
        self.parser.add_argument(
            "-avx512",
            "--avx512",
            help="Enable AVX-512 for LINPACK.",
            action="store_true",
        )

    def parse(self, args=None):
        """Parse known and unknown `args`.

        Args:
            args (list): All arguments to parse.

        Returns:
            Namespace object: All known argument values.
        """
        self.known, self.unknown = self.parser.parse_known_args(args)[:]

        if self.unknown:
            logging.info("WARNING: Unknown args received: %s", str(self.unknown))

        return self.known
