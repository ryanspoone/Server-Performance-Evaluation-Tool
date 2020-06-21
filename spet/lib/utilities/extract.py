# -*- coding: utf-8 -*-
"""Contains wrapper functions for extracting archives."""

import logging
import tarfile


def tar(archive, output_dir="."):
    """Extract recognized tar file types.

    Args:
        archive (str): The archive to extract.
        output_dir (str, optional): Where the archive is extracted.
    """
    try:
        if archive.endswith("tar.gz"):
            logging.debug('File ends with "tar.gz".')
            file = tarfile.open(archive, "r:gz")
            file.extractall(output_dir)
            file.close()
        elif archive.endswith("tar"):
            logging.debug('File ends with "tar".')
            file = tarfile.open(archive, "r:")
            file.extractall(output_dir)
            file.close()
        elif archive.endswith("tgz"):
            logging.debug('File ends with "tgz".')
            file = tarfile.open(archive, "r")
            for item in file:
                file.extract(item, output_dir)
                if not item.name.find(".tgz") or not item.name.find(".tar"):
                    tar(item.name, "./" + item.name[:item.name.rfind("/")])
    except IOError as err:
        logging.error(err)
