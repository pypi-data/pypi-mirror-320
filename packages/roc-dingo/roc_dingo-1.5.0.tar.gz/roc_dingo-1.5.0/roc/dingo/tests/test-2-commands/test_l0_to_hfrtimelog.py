#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests module for the roc.dingo l0_to_hfrtimelog command and related tasks.
"""

import glob
import os
import shlex
import tarfile

import unittest.mock as mock
from pathlib import Path

from poppy.core.conf import Settings
from poppy.core.logger import logger
from poppy.core.generic.requests import download_file
from poppy.core.test import CommandTestCase

from roc.dingo.models.data import HfrTimeLog

# Tests on roc.dingo l0_to_hfrtimelog command
from roc.dingo.constants import DINGO_CACHE_DIR
from roc.dingo.tests.test_dingo import DingoTest


class TestDingoL0ToHfrtimelogCommand(CommandTestCase):
    def setup_method(self, method):
        super().setup_method(method)

        self.session.query(HfrTimeLog).delete()
        self.session.flush()

    def teardown_method(self, method):
        super().teardown_method(method)

    def test_l0_to_hfrtimelog(self):
        # Command name
        cmd = "l0_to_hfrtimelog"

        # First get test data to insert (i.e. L0 input file(s))
        test_data_tarball = "test_data.tar.gz"

        self.install_dir = os.environ.get("ROC_TEST_DATA_PATH", DINGO_CACHE_DIR)
        test_data_dir = os.path.join(self.install_dir, cmd)
        Path(test_data_dir).mkdir(exist_ok=True, parents=True)
        test_data_path = os.path.join(test_data_dir, test_data_tarball)
        if not os.path.isfile(test_data_path):
            # Build test data tarball URL
            test_data_url = "/".join([DingoTest.base_url, cmd, test_data_tarball])
            # Get username/password
            test_dingo = DingoTest()

            download_file(
                test_data_path,
                test_data_url,
                auth=(test_dingo.username, test_dingo.password),
            )

        # Extract tarball
        if tarfile.is_tarfile(test_data_path):
            logger.info(f"Extracting {test_data_path} ...")
            with tarfile.open(test_data_path, "r:*") as tarball:
                tarball.extractall(path=test_data_dir, filter="fully_trusted")
        else:
            raise tarfile.ReadError(f"{test_data_path} is not a valid tarball!")

        # Get list of input files
        input_dir = os.path.join(test_data_dir, "inputs")
        input_files = list(glob.glob(os.path.join(input_dir, "solo_L0_rpw*.h5")))
        if not input_files:
            raise FileNotFoundError(f"No input L0 file found in {input_dir}")

        # initialize the main command
        command_to_test = " ".join(
            ["pop", "dingo", cmd, "-l0", " ".join(input_files), "-ll", "INFO"]
        )

        # define the required plugins
        plugin_list = ["poppy.pop", "roc.dingo"]

        # run the command
        # force the value of the plugin list
        with mock.patch.object(
            Settings,
            "configure",
            autospec=True,
            side_effect=self.mock_configure_settings(
                dictionary={"PLUGINS": plugin_list}
            ),
        ):
            self.run_command(shlex.split(command_to_test))

        # Check that test data are in the database
        logger.debug("Querying hfr_time_log table in database ...")
        rows = self.session.query(HfrTimeLog).order_by(HfrTimeLog.acq_time).all()

        assert isinstance(rows, list)
        assert len(rows) == 5

        for row in rows:
            print(row.acq_time)

        # Convert first/last row objects to dictionaries (for debugging)
        # first_row = DingoTest.get_db_values_columns_only(rows[0])
        # last_row = DingoTest.get_db_values_columns_only(rows[-1])
        # print(first_row)
        # print(last_row)

        assert rows[0].coarse_time == 704635836
        assert rows[0].delta_time1["70467979131033"][0] == 2755222091
        assert rows[-1].coarse_time == 704722236
        assert rows[-1].delta_time1["70472414932248"][-1] == 122029054

        # assert False
