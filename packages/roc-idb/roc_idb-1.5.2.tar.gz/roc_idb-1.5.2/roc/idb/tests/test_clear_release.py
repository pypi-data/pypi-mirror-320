#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from poppy.core.logger import logger
from poppy.core.test import CommandTestCase

from roc.idb.models.idb import IdbRelease

from sqlalchemy.exc import NoResultFound

import pytest

from .idb_test_util import load_idb


class TestClearReleaseCommand(CommandTestCase):
    """
    Test the clear_release command of the roc.idb plugin.
    """

    # @pytest.mark.skip
    @pytest.mark.parametrize(
        "idb_source,idb_version",
        [("MIB", "20200131")],
    )
    def test_clear_release(self, idb_source, idb_version):
        # Initializing database
        logger.debug("Reset database ...")

        # Installing IDB
        logger.debug(f"Installing IDB [{idb_source}-{idb_version}] ...")
        self.install_dir = load_idb(self, idb_source, idb_version)

        # Command to test
        command_to_test = [
            "pop",
            "idb",
            "clear_release",
            idb_version,
            "-s",
            idb_source,
            "--force",
            "-ll",
            "ERROR",
        ]

        # Run command to test
        self.run_command(command_to_test)

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
            assert True
        else:
            assert False

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
