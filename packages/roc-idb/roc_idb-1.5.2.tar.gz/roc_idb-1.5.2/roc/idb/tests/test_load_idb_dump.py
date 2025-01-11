#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test load_idb_dump command
"""

import os

from sqlalchemy.orm.exc import NoResultFound
import pytest

from poppy.core.logger import logger
from poppy.core.test import CommandTestCase

from roc.idb.constants import IDB_CACHE_DIR
from roc.idb.models.idb import IdbRelease
from .idb_test_util import reset_db


class TestLoadIdbDumpCommand(CommandTestCase):
    @pytest.mark.skip("Too long test: to be reworked")
    @pytest.mark.parametrize(
        "idb_source,idb_version,idb_dump_file,user,password",
        [
            (
                "MIB",
                "20200131",
                "https://rpw.lesia.obspm.fr/roc/data/private/devtest/roc/test_data/idb_dump/MIB_20200131/idb_dump.sql",
                os.environ.get("ROC_TEST_USERNAME", "roctest"),
                os.environ.get("ROC_TEST_PASSWORD", None),
            )
        ],
    )
    def test_load_idb_dump(
        self, idb_source, idb_version, idb_dump_file, user, password
    ):
        # Build idb_dump local path
        self.install_dir = os.path.join(
            IDB_CACHE_DIR, f"idb-{idb_source}-{idb_version}"
        )
        self.local_idb_dump = os.path.join(
            self.install_dir, os.path.basename(idb_dump_file)
        )
        os.makedirs(self.install_dir, exist_ok=True)

        if not password:
            logger.warning(f"Password is not defined for {user}!")

        # Reset database
        reset_db(self)

        # Loading IDB dump file
        command_to_test = [
            "pop",
            "-ll",
            "INFO",
            "idb",
            "--force",
            "load_idb_dump",
            "-i",
            self.install_dir,
            "-d",
            idb_dump_file,
            "-a",
            user,
            password,
        ]

        # Make sure the idb was not already loaded
        logger.debug(f"Running command: {' '.join(command_to_test)} ...")
        self.run_command(command_to_test)

        # Check idb sql dump file exits
        assert os.path.isfile(self.local_idb_dump)

        # Verify expected behaviour
        try:
            _ = (
                self.session.query(IdbRelease)
                .filter(
                    IdbRelease.idb_version == idb_version,
                    IdbRelease.idb_source == idb_source,
                )
                .one()
            )
        except NoResultFound:
            assert False
        else:
            assert True

    def teardown_method(self, method):
        """
        Method called immediately after the test method has been called and the result recorded.

        This is called even if the test method raised an exception.

        :param method: the test method
        :return:
        """

        # rollback the database
        super().teardown_method(method)

        # Remove IDB folder
        # shutil.rmtree(self.install_dir)
