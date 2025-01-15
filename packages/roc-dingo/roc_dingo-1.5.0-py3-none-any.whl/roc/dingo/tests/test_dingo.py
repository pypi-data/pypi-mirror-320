#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Functions used in all DINGO tests
"""

import os
import copy
from pathlib import Path
import argparse
from typing import Union

import yaml

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.dialects import postgresql

from poppy.core.logger import logger
from poppy.core.test import CommandTestCase
from poppy.core.configuration import Configuration

from roc.dingo.models.file import FileLog
from roc.dingo.constants import TEST_DATABASE
from roc.dingo.constants import DINGO_CACHE_DIR


# Models to be adapted for each Dingo model
#
# from poppy.core.test import TaskTestCase, CommandTestCase
# class DingoTaskTestCase(TaskTestCase):
#
#     @classmethod
#     def setup_class(cls):
#         logger.debug('setup_class DingoLogFileTaskTestCase')
#         d = DingoTest()
#         d.get_test_data()
#
#    #     # --- database setup ---
#    #     session = DingoTestLogFile.setup_session()
#
#    # @classmethod
#    # def teardown_class(cls):
#    #     logger.debug('teardown_class DingoTaskTestCase')
#
#    #     # --- close session
#    #     session.close()
#
# class DingoCommandTestCase(CommandTestCase):
#
#     @classmethod
#     def setup_class(cls):
#         logger.debug('setup_class DingoCommandTestCase')
#         d = DingoTest()
#         d.get_test_data()


class DingoTest:
    # base_url = (
    #     "https://rpw.lesia.obspm.fr/roc/data/private/devtest/roc/test_data/rodp/dingo"  # noqa: E501
    # )
    # base_path = (
    #     "/volumes/plasma/rpw/roc/data/https/private/devtest/roc/test_data/rodp/dingo"  # noqa: E501
    # )
    #
    # # test credentials
    # host = "roc2-dev.obspm.fr"
    # username = os.environ.get("ROC_TEST_USER", "roctest")
    # password = None

    def __init__(self):
        logger.debug("DingoTest setup_class()")
        # logger.debug(f"base_url = {self.base_url}")
        # logger.debug(f"base_path = {self.base_path}")
        # try:
        #    self.password = os.environ["ROC_TEST_PASSWORD"]
        # except KeyError:
        #    raise KeyError(
        #        "You have to define the test user password using"
        #        'the "ROC_TEST_PASSWORD" environment variable'
        #    )

    @staticmethod
    def compare_data_to_expected(
        expected_data: dict, data: dict, ignore: Union[list, None] = None
    ):
        """
        Compare expected_data to the data array dictionary
            -> check if every expected item is in data
            -> check if every data item is in expected data

            :param expected_data: expected data
            :type expected_data: dict
            :param data: the data to be compared
            :type data: dict
            :param ignore: items keys to ignore
            :type ignore: list
        """
        if ignore is None:
            ignore = []

        # check length
        assert len(expected_data) == len(data)

        # check content
        for item in data:
            assert item in expected_data, "item {} is not in expected data".format(item)
            for key in ignore:
                data[item].pop(key, None)
                expected_data[item].pop(key, None)

        for item in expected_data:
            assert item in data, "item {} is not in result".format(item)
            assert data[item] == expected_data[item], (
                "item {} is not the one expected :expected {} / got {}".format(
                    item, expected_data[item], data[item]
                )
            )

    @staticmethod
    def read_data(file: str) -> list:
        """
        Read a file located in the data-tasks directory
        and returns file content as an array of strings

        :param file: file to open
        :type file: str
        :return: data inside file
        rtype: list
        """
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, "data-tasks", file)
        data = []
        with open(path, "r") as f:
            # read a line corresponding to a directory
            for line in f.readlines():
                # append the data
                data.append(line.strip())
        return data

    @staticmethod
    def get_test_data_path() -> str:
        """
        Read the config file and returns ROC_TEST_DATA_PATH
        which is the path where to store the test dataset locally

        :return: path to the test data directory
        :rtype: str
        """
        # Define default value
        data_test_path = DINGO_CACHE_DIR

        conf = DingoTest.load_configuration()

        # Check if ROC_TEST_DATA_PATH env. variable is defined
        # in: (1) config file, (2) shell env.
        for source in [conf["environment"], os.environ]:
            try:
                data_test_path = source["ROC_TEST_DATA_PATH"]
            except KeyError:
                # logger.debug('Env. variable ROC_TEST_DATA_PATH not set')
                pass
            else:
                break

        logger.debug(f"ROC_TEST_DATA_PATH = {data_test_path}")
        return data_test_path

    # def get_test_data(self):
    #     """
    #     Get the test dataset indicated by the environment variable
    #     ROC_TEST_DATA_PATH
    #
    #     Try to make a rsync with the roctest account
    #     A public kay has to be setup on the server to allow connexion
    #     If the command is not available (Windows),
    #     use the download_file() method
    #
    #     """
    #     data_test_path = DingoTest.get_test_data_path()
    #     os.makedirs(data_test_path, exist_ok=True)
    #
    #     try:
    #         logger.info("Starting rsync")
    #         ssh_option = "\"ssh -o 'StrictHostKeyChecking no'\""
    #         rsync_cmd = "rsync -e {} -irtzuv {}@{}:{}/ {}/".format(
    #             ssh_option, self.username, self.host, self.base_path, data_test_path
    #         )
    #         logger.info("Executing " + rsync_cmd)
    #         output = os.popen(rsync_cmd)
    #         rsync_output = output.read()
    #         if output.close() is not None:
    #             raise ValueError("Rsync failed : {}".format(rsync_output))
    #     except ValueError:
    #         logger.info("Rsync failed, using download_test_data()")
    #         self.download_test_data(data_test_path)

    # def download_test_data(self, data_test_path):
    #     """
    #     Download the manifest.txt file located at self.base_url
    #     And for each file, download it only if the file does not exist
    #     in data_test_path
    #     """
    #     logger.debug("download_test_data()")
    #     manifest_filepath = osp.join(data_test_path, "manifest.txt")
    #
    #     manifest_file_url = self.base_url + "/manifest.txt"
    #     auth = (self.username, self.password)
    #
    #     file_list = list(
    #         self.load_manifest_file(manifest_filepath, manifest_file_url, auth=auth)
    #     )
    #
    #     for relative_filepath in file_list:
    #         # skip empty strings
    #         if not relative_filepath:
    #             continue
    #
    #         # get the complete filepath
    #         filepath = osp.join(data_test_path, relative_filepath)
    #         os.makedirs(osp.dirname(filepath), exist_ok=True)
    #
    #         # download it only if it does not exist
    #         if not osp.isfile(filepath):
    #             logger.info("Downloading {}".format(filepath))
    #             download_file(
    #                 filepath, f"{self.base_url}/{relative_filepath}", auth=auth
    #             )
    #
    # @staticmethod
    # def load_manifest_file(manifest_filepath, manifest_file_url, auth=None):
    #     """
    #     Read the manifest.txt file located at manifest_file_url
    #     and returns the list composed by the file list
    #     """
    #
    #     download_file(manifest_filepath, manifest_file_url, auth=auth)
    #
    #     with open(manifest_filepath) as manifest_file:
    #         for line in manifest_file:
    #             yield line.strip("\n\r")
    #
    #     os.remove(manifest_filepath)

    @staticmethod
    def load_configuration(config_file: Path = None) -> Configuration:
        """
        Load pipeline configuration file in JSON format.

        :param config_file: Path of the configuration file.
        If not passed, try to retrieve file path from
        PIPELINE_CONFIG_FILE environment variable
        :type config_file: Path
        :return: pipeline configuration data
        :rtype: poppy.core.configuration.Configuration
        """
        if config_file:
            configuration = Configuration(str(config_file))
        else:
            configuration = Configuration(os.getenv("PIPELINE_CONFIG_FILE", None))
        configuration.read()

        return configuration

    @staticmethod
    def get_spice_kernel_dir():
        """
        Returns SPICE kernels directory

        :return: spice_kernels_dir
        """
        # Define default value
        spice_kernels_dir = os.path.join(Path.cwd(), "data", "spice_kernels")

        # Get pipeline configuration parameters
        conf = DingoTest.load_configuration()

        # Check if SPICE_KERNEL_PATH env. variable is defined
        # in: (1) config file, (2) shell env.
        for source in [conf["environment"], os.environ]:
            try:
                spice_kernels_dir = os.path.join(source["SPICE_KERNEL_PATH"])
            except Exception as e:
                logger.debug(e)
                # logger.debug('Env. variable SPICE_KERNEL_PATH not set')
                pass
            else:
                break

        return spice_kernels_dir

    @staticmethod
    def setup_session(config_file: Path = None) -> Session:
        """
        Set up database configuration.

        :param config_file: Pipeline/database configuration file path
        :type config_file: Path
        :return: database session
        :rtype: Session
        """
        # Read config file
        conf = DingoTest.load_configuration(config_file=config_file)

        database_info = list(
            filter(
                lambda db: db["identifier"] == TEST_DATABASE, conf["pipeline.databases"]
            )
        )[0]

        # Create an Engine, which the Session will use for connection resources
        engine = create_engine(
            "{}://{}@{}/{}".format(
                database_info["login_info"]["vendor"],
                database_info["login_info"]["user"],
                database_info["login_info"]["address"],
                database_info["login_info"]["database"],
            )
        )
        # create a configured "Session" class
        Session = sessionmaker(bind=engine, autocommit=False)
        # create a Session
        session = Session()

        return session

    @staticmethod
    def get_db_values(item):
        """
        returns a dict for any object in DB returned by session.query

        :param item: the object
        """

        return copy.copy(item.__dict__)

    @staticmethod
    def get_db_values_columns_only(item):
        """
        Convert an input item as returned by SQLAlchemy.query into dictionary.
        (Same than DingoTest.get_db_values(), but with columns only)
        See https://stackoverflow.com/questions/1958219/how-to-convert-sqlalchemy-row-object-to-a-python-dict

        :param item: SQLAlchemy table model class instance
        :return: dictionary with columns as keywords and entries as values
        """
        return {
            c.expression.name: getattr(item, c.key)
            for c in inspect(item).mapper.column_attrs
        }

    @staticmethod
    def clear_db(command_test_case: CommandTestCase, log_level: str = "INFO"):
        # Clear database
        clear_db_cmd = ["pop", "db", "downgrade", "base", "-ll", log_level]
        command_test_case.run_command(clear_db_cmd)

    @staticmethod
    def create_db(command_test_case: CommandTestCase, log_level: str = "INFO"):
        # Run database migrations
        create_db_cmd = ["pop", "db", "upgrade", "heads", "-ll", log_level]
        command_test_case.run_command(create_db_cmd)

    @staticmethod
    def load_idb(
        command_test_case: CommandTestCase,
        idb_source: str,
        idb_version: str,
        install_dir: str = None,
        log_level="INFO",
    ) -> str:
        if install_dir is None:
            install_dir = DINGO_CACHE_DIR
        idb_dir = os.path.join(install_dir, f"idb-{idb_source}-{idb_version}")
        os.makedirs(idb_dir, exist_ok=True)

        # IDB loading
        load_idb_cmd = [
            "pop",
            "idb",
            "install",
            "--force",
            "--install-dir",
            idb_dir,
            "-s",
            idb_source,
            "-v",
            idb_version,
            "--load",
            "-ll",
            log_level,
        ]
        command_test_case.run_command(load_idb_cmd)

        return idb_dir

    @staticmethod
    def filelog_to_yml(yml_outfile: Path, level: list = None, config_file: Path = None):
        """
        Export pipeline.file_log database table content
        into an output yaml format file.
        Can be used to quickly generated the "roc_data_files_all_dump.yml

        :param yml_outfile: Path and name of the output yaml format file
        :type yml_outfile: Path
        :param level: Filter rows by data processing level
        :type level: list
        :param config_file: Path to configuration file
        :type config_file: Path
        :return: None
        """
        if not level:
            level = ["L0", "L1", "HK", "L1R", "L2", "L3", "CAL", "BIA"]

        session = DingoTest.setup_session(config_file=config_file)
        query = session.query(FileLog).filter(FileLog.level.in_(level))
        try:
            results = query.all()
        except NoResultFound as e:
            logger.error(f"No entry found in pipeline.file_log with {level}:\n{e}")
            logger.debug(
                str(
                    query.statement.compile(
                        dialect=postgresql.dialect(),
                        compile_kwargs={"literal_binds": True},
                    )
                )
            )
        else:
            output_data = {}
            for i, row in enumerate(results):
                row_dict = row.as_dict()
                output_data[row_dict["basename"]] = {k: v for k, v in row_dict.items()}

            with open(str(yml_outfile), "w") as f:
                yaml.dump(output_data, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--yml_file", nargs=1, type=Path, help="Path and name of output yaml file"
    )
    parser.add_argument(
        "-l",
        "--level",
        nargs="+",
        type=str,
        help="Filter rows by data processing level",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        nargs=1,
        type=Path,
        help="Path and name of config JSON file",
    )
    args = parser.parse_args()

    DingoTest.filelog_to_yml(args.yml_file[0], level=args.level)
