#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Union

from poppy.core.test import CommandTestCase

from roc.idb.constants import IDB_CACHE_DIR


def get_idb_install_dir(idb_source: str, idb_version: str, make: bool = True) -> str:
    """
    Generate local installation directory path for a given IDB source and version.

    :param idb_source: Source of IDB (MIB or PALISADE)
    :param idb_version: version of IDB
    :param make: If True, then create the IDB installation directory
    :return: path of the IDB installation directory
    """
    install_dir = os.path.join(IDB_CACHE_DIR, f"idb-{idb_source}-{idb_version}")
    if make:
        os.makedirs(install_dir, exist_ok=True)

    return install_dir


def reset_db(command_test_case: CommandTestCase, log_level: str = "INFO"):
    # Clear database
    clear_db_cmd = ["pop", "-ll", log_level, "db", "downgrade", "base"]
    command_test_case.run_command(clear_db_cmd)

    # Run database migrations
    create_db_cmd = ["pop", "-ll", log_level, "db", "upgrade", "heads"]
    command_test_case.run_command(create_db_cmd)


def load_idb(
    command_test_case: CommandTestCase,
    idb_source: str,
    idb_version: str,
    install_dir: Union[str, None] = None,
    log_level="INFO",
) -> str:
    if install_dir is None:
        install_dir = get_idb_install_dir(idb_source, idb_version, make=True)

    # IDB loading
    load_idb_cmd = [
        "pop",
        "-ll",
        log_level,
        "idb",
        "install",
        "--force",
        "--install-dir",
        install_dir,
        "-s",
        idb_source,
        "-v",
        idb_version,
        "--load",
    ]
    command_test_case.run_command(load_idb_cmd)

    return install_dir
