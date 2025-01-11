#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pytest

from poppy.core.logger import logger
from poppy.core.test import CommandTestCase

from roc.idb.models.idb import PacketHeader, ItemInfo, IdbRelease
from .idb_test_util import load_idb


class TestLoadIdbCommand(CommandTestCase):
    def setup_method(self, method):
        super().setup_method(method)

    @pytest.mark.parametrize(
        "idb_source,idb_version",
        [("PALISADE", "4.3.5_MEB_PFM"), ("MIB", "20200131")],
    )
    def test_install_and_load_idb(self, idb_source, idb_version):
        # First be sure that IDB is not loaded in the database
        clear_idb = [
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
        self.run_command(clear_idb)

        # Installing IDB
        logger.debug(f"Installing IDB [{idb_source}-{idb_version}] ...")
        self.install_dir = load_idb(self, idb_source, idb_version)

        logger.debug(f"Querying IDB [{idb_source}-{idb_version}] ...")
        packet_header = (
            self.session.query(PacketHeader)
            .join(ItemInfo)
            .join(IdbRelease)
            .filter(
                ItemInfo.srdb_id == "YIW00083",
                IdbRelease.idb_version == idb_version,
                IdbRelease.idb_source == idb_source,
            )
            .one()
        )

        # make assertions
        assert packet_header.cat == 7
        assert packet_header.sid == 42122

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
