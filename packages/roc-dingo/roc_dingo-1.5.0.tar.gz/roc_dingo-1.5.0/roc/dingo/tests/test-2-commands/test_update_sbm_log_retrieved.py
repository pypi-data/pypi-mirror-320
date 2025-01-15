#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests module for the roc.dingo update_sbm_retrieved command and related tasks.
"""

import glob
import os
import shlex
import tarfile

import unittest.mock as mock
from pathlib import Path

import pytest

from poppy.core.conf import Settings
from poppy.core.logger import logger
from poppy.core.generic.requests import download_file
from poppy.core.test import CommandTestCase

from roc.dingo.models.packet import TmLog
from roc.dingo.models.data import SbmLog

# Tests on roc.dingo update_sbm_retrieved command
from roc.dingo.tests.test_dingo import DingoTest
from roc.dingo.constants import DINGO_CACHE_DIR

EXPECTED_ROWS = (
    {
        "info": {
            "TM_TDS_SCIENCE_SBM1_RSWF": {"size": 2916, "count": 27, "percent": 1.25},
            "TM_LFR_SCIENCE_SBM1_BP1_F0": {
                "size": 777330,
                "count": 2879,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_BP2_F0": {
                "size": 495360,
                "count": 720,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1": {"size": 0, "count": 0, "percent": 0.0},
            "TM_TDS_SCIENCE_SBM1_RSWF_C": {
                "size": 2221930,
                "count": 2132,
                "percent": 98.70370370370371,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1_C": {
                "size": 13138060,
                "count": 8776,
                "percent": 99.97721576668945,
            },
        },
        "size": 16635596,
        "percent": 99.9827298675983,
    },
    {
        "info": {
            "TM_TDS_SCIENCE_SBM1_RSWF": {
                "size": 4644,
                "count": 43,
                "percent": 1.990740740740741,
            },
            "TM_LFR_SCIENCE_SBM1_BP1_F0": {
                "size": 777330,
                "count": 2879,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_BP2_F0": {
                "size": 495360,
                "count": 720,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1": {"size": 0, "count": 0, "percent": 0.0},
            "TM_TDS_SCIENCE_SBM1_RSWF_C": {
                "size": 2266296,
                "count": 2117,
                "percent": 98.00925925925927,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1_C": {
                "size": 13125590,
                "count": 8775,
                "percent": 99.96582365003418,
            },
        },
        "size": 16669220,
        "percent": 99.99145591250854,
    },
    {
        "info": {
            "TM_TDS_SCIENCE_SBM1_RSWF": {
                "size": 3672,
                "count": 34,
                "percent": 1.574074074074074,
            },
            "TM_LFR_SCIENCE_SBM1_BP1_F0": {
                "size": 777330,
                "count": 2879,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_BP2_F0": {
                "size": 495360,
                "count": 720,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1": {"size": 0, "count": 0, "percent": 0.0},
            "TM_TDS_SCIENCE_SBM1_RSWF_C": {
                "size": 2194002,
                "count": 2126,
                "percent": 98.42592592592592,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1_C": {
                "size": 13115610,
                "count": 8775,
                "percent": 99.96582365003418,
            },
        },
        "size": 16585974,
        "percent": 99.99145591250854,
    },
    {
        "info": {
            "TM_TDS_SCIENCE_SBM1_RSWF": {
                "size": 4212,
                "count": 39,
                "percent": 1.8055555555555554,
            },
            "TM_LFR_SCIENCE_SBM1_BP1_F0": {
                "size": 777330,
                "count": 2879,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_BP2_F0": {
                "size": 495360,
                "count": 720,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1": {"size": 0, "count": 0, "percent": 0.0},
            "TM_TDS_SCIENCE_SBM1_RSWF_C": {
                "size": 2259828,
                "count": 2121,
                "percent": 98.19444444444444,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1_C": {
                "size": 13196088,
                "count": 8775,
                "percent": 99.96582365003418,
            },
        },
        "size": 16732818,
        "percent": 99.99145591250854,
    },
    {
        "info": {
            "TM_TDS_SCIENCE_SBM1_RSWF": {
                "size": 1512,
                "count": 14,
                "percent": 0.6481481481481481,
            },
            "TM_LFR_SCIENCE_SBM1_BP1_F0": {
                "size": 777330,
                "count": 2879,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_BP2_F0": {
                "size": 495360,
                "count": 720,
                "percent": 100.0,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1": {"size": 0, "count": 0, "percent": 0.0},
            "TM_TDS_SCIENCE_SBM1_RSWF_C": {
                "size": 2124022,
                "count": 2146,
                "percent": 99.35185185185185,
            },
            "TM_LFR_SCIENCE_SBM1_CWF_F1_C": {
                "size": 13042384,
                "count": 8775,
                "percent": 99.96582365003418,
            },
        },
        "size": 16440608,
        "percent": 99.99145591250854,
    },
)


class TestDingoUpdateSbmRetrievedCommand(CommandTestCase):
    def setup_method(self, method):
        super().setup_method(method)

        # empty the database
        self.session.query(TmLog).delete()
        self.session.query(SbmLog).delete()
        self.session.flush()

    def teardown_method(self, method):
        super().teardown_method(method)

    @pytest.mark.parametrize(
        "idb_source,idb_version, exclude_tm_apid",
        [
            ("MIB", "20200131", "1212 1228 1244 1260 1204 1220 1236 1252 1269 1300"),
        ],
    )
    def test_update_sbm_retrieved(self, idb_source, idb_version, exclude_tm_apid):
        # Command name
        cmd = "update_sbm_retrieved"

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
        input_file = list(glob.glob(os.path.join(input_dir, "solo_L0_rpw*.h5")))
        if not input_file:
            raise FileNotFoundError(f"No input L0 file found in {input_dir}")
        elif len(input_file) > 1:
            raise ValueError("/inputs must contain only one L0 test file!")
        else:
            # Make sure to have only file
            input_file = input_file[0]

        # Check that SPICE kernels are present in ./data/spice_kernels folder
        spice_kernels_dir = DingoTest.get_spice_kernel_dir()
        if not os.path.isdir(spice_kernels_dir):
            raise FileNotFoundError(
                f"No SPICE kernel set found in {spice_kernels_dir}!"
            )
        else:
            # Get latest version of SCLK et LSK SPICE kernels
            sclk = max(
                (Path(spice_kernels_dir) / "sclk").glob("solo_ANC_soc-sclk_*.tsc"),
                key=os.path.getctime,
            )
            lsk = max(
                (Path(spice_kernels_dir) / "lsk").glob("naif*.tls"),
                key=os.path.getctime,
            )

        # First insert data into database
        command_to_run = " ".join(
            [
                "pop",
                "dingo",
                "--idb-source",
                idb_source,
                "--idb-version",
                idb_version,
                "--sclk",
                str(sclk),
                "--lsk",
                str(lsk),
                "l0_to_db",
                "-l0",
                input_file,
                "--exclude-tm-apid",
                exclude_tm_apid,
                "-ll",
                "INFO",
            ]
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
            self.run_command(shlex.split(command_to_run))

        # Command to test
        command_to_test = " ".join(["pop", "dingo", cmd, "-ll", "INFO"])
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
        logger.debug("Querying sbm_log table in database ...")
        rows = self.session.query(SbmLog).order_by(SbmLog.utc_time).all()

        for i, row in enumerate(rows):
            current_retrieved = row.retrieved
            current_expected = EXPECTED_ROWS[i]

            assert all(
                (current_expected.get(k) == v for k, v in current_retrieved.items())
            )
