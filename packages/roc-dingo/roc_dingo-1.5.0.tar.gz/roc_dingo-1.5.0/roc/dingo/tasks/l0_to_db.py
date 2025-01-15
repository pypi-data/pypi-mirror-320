#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Contains dingo tasks to insert RPW L0 data into the ROC database."""

from datetime import datetime, timedelta
import json
import concurrent.futures
import os
from typing import Union, List, Type

import pandas as pd
import scipy.sparse as sparse
import h5py
import uuid
from sqlalchemy import null

from poppy.core.logger import logger
from poppy.core.db.connector import Connector
from poppy.core.task import Task
from poppy.core.target import FileTarget

from roc.dingo.models.data import SbmLog, LfrKcoeffDump, BiaSweepLog
from roc.dingo.tools import (
    get_packet_sha,
    compute_apid,
    load_spice,
    is_sclk_uptodate,
    get_columns,
    get_current_idb,
    insert_on_conflict_nothing,
    glob_paths,
    valid_time,
)
from roc.dingo.exceptions import PacketInsertionError
from roc.dingo.constants import (
    PIPELINE_DATABASE,
    TIME_DAILY_STRFORMAT,
    TRYOUTS,
    TIME_WAIT_SEC,
    SQL_LIMIT,
    PIPELINE_TABLES,
    SBM_ALGO_PARAM_LIST,
    LFR_KCOEFF_PARAM_NR,
    SBM_LOG_PACKETS,
    LFR_KCOEFF_DUMP_PACKETS,
    TIME_ISO_STRFORMAT,
    PACKET_TYPE,
    TC_ACK_ALLOWED_STATUS,
    IDB_SOURCE,
    WORKERS,
    BIA_SWEEP_LOG_PACKETS,
    CIWT0130TM,
    CIWT0131TM,
    NAIF_SOLO_ID,
    PACKET_DATA_GROUP,
    EVENT_TM_APID,
    TC_ACK_APID,
    HK_TM_APID,
    ACQ_TIME_PNAMES,
)

__all__ = ["L0ToDb", "get_l0_files", "load_param"]


class L0ToDb(Task):
    """
    Insert content of input L0 files into the
    in ROC database
    """

    plugin_name = "roc.dingo"
    name = "l0_to_db"

    def add_targets(self):
        self.add_input(
            identifier="rpw_l0_files",
            many=True,
            filepath=get_l0_files,
            target_class=FileTarget,
        )

    @Connector.if_connected(PIPELINE_DATABASE)
    def setup_inputs(self):
        # get the input l0 files
        self.l0_files = glob_paths(self.inputs["rpw_l0_files"].filepath)

        # Get start_time input value
        self.start_time = valid_time(
            self.pipeline.get("start_time", default=[None])[0],
            str_format=TIME_DAILY_STRFORMAT,
        )

        # Get end_time input value
        self.end_time = valid_time(
            self.pipeline.get("end_time", default=[None])[0],
            str_format=TIME_DAILY_STRFORMAT,
        )

        # Get include/exclude optional inputs
        self.include = self.pipeline.get("include", default=[], create=True)
        self.exclude = self.pipeline.get("exclude", default=[], create=True)

        # Retrieve --exclude-tm-apid, --exclude-tc-apid
        self.exclude_tm_apid = self.pipeline.get(
            "exclude_tm_apid", default=[], args=True
        )
        self.exclude_tc_apid = self.pipeline.get(
            "exclude_tc_apid", default=[], args=True
        )

        # Get or create failed_files list from pipeline properties
        self.failed_files = self.pipeline.get("failed_files", default=[], create=True)

        # Get or create processed_files list from pipeline properties
        self.processed_files = self.pipeline.get(
            "processed_files", default=[], create=True
        )

        # get a database session
        self.session = Connector.manager[PIPELINE_DATABASE].session

        # Get tryouts from pipeline properties
        self.tryouts = self.pipeline.get("tryouts", default=[TRYOUTS], create=True)[0]

        # Get wait from pipeline properties
        self.wait = self.pipeline.get("wait", default=[TIME_WAIT_SEC], create=True)[0]

        # Get number of workers to run in parallel
        self.workers = self.pipeline.get("workers", default=[WORKERS], create=True)[0]

        # Get idb_version/idb_source from pipeline properties
        self.idb_source = self.pipeline.get(
            "idb_source", default=[IDB_SOURCE], create=True
        )[0]

        self.idb_version = self.pipeline.get(
            "idb_version", default=[None], create=True
        )[0]

        # If idb_version not passed (is None),
        # then try to get current working version from the database
        if self.idb_version is None:
            self.idb_version = get_current_idb(
                self.idb_source,
                self.session,
                tryouts=self.tryouts,
                wait=self.wait,
            )
        if self.idb_version is None:
            raise ValueError("idb_version argument cannot be defined!")

        # Get SOLO SPICE kernels (SCLK and LSK)
        self.sclk_file = self.pipeline.get("sclk", default=[], create=True)[0]
        self.lsk_file = self.pipeline.get("lsk", default=[None], create=True)[0]
        if not self.sclk_file or not self.lsk_file:
            raise FileNotFoundError(
                "Both sclk_file and lsk_file must be passed as inputs to run L0ToDb!"
            )
        else:
            # Load SPICE with input kernels
            self.spice = load_spice(spice_kernels=[self.lsk_file, self.sclk_file])

        # Retrieve --limit keyword value
        self.limit = self.pipeline.get(
            "limit",
            default=[SQL_LIMIT],
        )[0]

        # Get --param-only optional keyword
        self.param_only = self.pipeline.get(
            "param_only",
            default=False,
        )
        if self.param_only:
            logger.warning("Disable data insertion in tm_log/tc_log table")

        # Initialize data insertion counters
        self.inserted_count = 0
        self.failed_count = 0
        self.total_count = 0
        self.tm_count = 0
        self.tc_count = 0

    def run(self):
        # Define task job ID (long and short)
        self.job_uuid = str(uuid.uuid4())
        self.job_id = f"{self.job_uuid[:8]}"
        logger.info(f"Task job {self.job_id} is starting")
        try:
            self.setup_inputs()
        except Exception as e:
            logger.error(
                f"Initializing inputs has failed!\t[{self.job_id}]{self.job_id}!"
            )
            logger.debug(e)
            self.pipeline.exit()
            return

        n_l0_files = len(self.l0_files)
        logger.info(f"{n_l0_files} RPW L0 files to process\t[{self.job_id}]")
        if n_l0_files == 0:
            return

        # Loop over each L0 file in the input list
        for i, current_l0_file in enumerate(self.l0_files):
            logger.info(
                f"Processing {current_l0_file} ({n_l0_files - i - 1} remaining)\t[{self.job_id}]"
            )
            self.current_l0_file = current_l0_file
            self.insert_time = datetime.today()
            # Open file
            try:
                with h5py.File(current_l0_file, "r") as l0:
                    # Check if the SCLK SPICE kernel used to compute TM utc times in the input L0 file
                    # is older or newer than the l0 file date (if kernel is older, then it means that utc times are computed
                    # with predictive time coefficients. In this case, the utc times are not stored in the database
                    # in order to avoid confusion)
                    current_l0_datetime = datetime.strptime(
                        l0.attrs["Datetime"][:8],
                        TIME_DAILY_STRFORMAT,
                    )
                    # Skip file if outside the [start_time, end_time] time range
                    # (if any)
                    if (
                        self.start_time
                        and self.start_time.date() > current_l0_datetime.date()
                    ):
                        logger.info(
                            f"Skipping {current_l0_file} (older than {self.start_time.date()})\t[{self.job_id}]"
                        )
                        continue
                    if (
                        self.end_time
                        and self.end_time.date() < current_l0_datetime.date()
                    ):
                        logger.info(
                            f"Skipping {current_l0_file} (newer than {self.end_time.date()})\t[{self.job_id}]"
                        )
                        continue
                    # Retrieving L0 start/end times
                    self.l0_start_time = datetime.strptime(
                        l0.attrs["TIME_MIN"], TIME_ISO_STRFORMAT
                    )
                    self.l0_end_time = datetime.strptime(
                        l0.attrs["TIME_MAX"], TIME_ISO_STRFORMAT
                    )
                    try:
                        self.is_predictive_time = not is_sclk_uptodate(
                            current_l0_datetime + timedelta(days=1),
                            l0.attrs["SPICE_KERNELS"],
                        )
                    except Exception as e:
                        logger.debug(e)
                        self.is_predictive_time = True

                        if self.is_predictive_time:
                            logger.info(
                                f"Predictive UTC times used in {current_l0_file}!\t[{self.job_id}]"
                            )

                    # Total number of TM/TC packets in current l0
                    l0_tm_count = int(l0["TM"].attrs["COUNT"])
                    l0_tc_count = int(l0["TC"].attrs["COUNT"])

                    # Insert input L0 data into database
                    inserted_count = 0
                    failed_count = 0
                    try:
                        inserted_count, failed_count = self.insert_l0(
                            l0, include=self.include, exclude=self.exclude
                        )

                        if failed_count > 0:
                            raise PacketInsertionError(
                                message="Database insertion has failed for "
                                f"{failed_count} packets in {self.current_l0_file}!\t[{self.job_id}]"
                            )
                    except PacketInsertionError:
                        self.failed_files.append(self.current_l0_file)
                        self.failed_count += failed_count
                    except Exception as e:
                        self.failed_files.append(self.current_l0_file)
                        self.failed_count += l0_tm_count + l0_tc_count
                        self.total_count += l0_tm_count + l0_tc_count
                        logger.error(
                            "Database insertion has failed for "
                            f"{self.current_l0_file}!\t[{self.job_id}]"
                        )
                        logger.debug(e)
                        break
                    else:
                        logger.info(
                            f"{inserted_count} new packets "
                            f"inserted from {self.current_l0_file}\t[{self.job_id}]"
                        )
                        self.inserted_count += inserted_count
                        self.processed_files.append(self.current_l0_file)
            except Exception as e:
                self.failed_files.append(self.current_l0_file)
                self.failed_count += l0_tm_count + l0_tc_count
                logger.error(f"Cannot open {self.current_l0_file}!\t[{self.job_id}")
                logger.debug(e)
                continue

        logger.info(
            f"{self.inserted_count}/{self.total_count} new packets inserted in the database"
            f" from {len(self.processed_files)} files\t[{self.job_id}]"
        )

        if len(self.failed_files) > 0:
            logger.error(
                f"Insertion has failed for {self.failed_count}/{self.total_count} packets "
                f"in {len(self.failed_files)} files\t[{self.job_id}]"
            )
            # Force the copy of failed files
            self.pipeline.properties["copy"] = True
            if "failed_files_dir" not in self.pipeline.properties:
                self.pipeline.properties["self.pipeline.properties"] = os.path.join(
                    self.pipeline.output, f"RODP_L0TODB_{self.job_id}", "failed"
                )

        logger.info(f"Task job {self.job_id} has ended correctly")

    def insert_l0(
        self,
        l0: Type[h5py._hl.files.File],
        packet_type: List[str] = PACKET_TYPE,
        include: Union[List[str], None] = None,
        exclude: Union[List[str], None] = None,
    ) -> tuple:
        """
        Insert L0 packet data into the database.
        Multiple packet insertions in parallel is possible.

        :param l0: h5.group object containing current L0 packet data
        :type l0: h5py._hl.files.File
        :param packet_type: Filter by type of packets (TM, TC)
        :type packet_type: list
        :param include: Packets to insert (all by default)
        :type include: list
        :param exclude: Packets to exclude from insertion (empty list by default)
        :type exclude: list
        :return: Numbers of inserted/failed packets
        :rtype: tuple
        """
        # Initialize counters
        inserted_count = 0
        failed_count = 0

        # Build list of packets to insert
        # (Filter if required using include/exclude keywords)
        packet_list = []
        packet_count = {"TM": 0, "TC": 0}
        for current_packet_type in packet_type:
            for current_packet_name in l0[current_packet_type].keys():
                if exclude and current_packet_name in exclude:
                    logger.debug(f"{current_packet_name} excluded")
                    continue
                if include and current_packet_name not in include:
                    logger.debug(f"{current_packet_name} not in {include}")
                    continue

                # Get APID of the current packet
                process_id = l0[current_packet_type][current_packet_name][
                    "packet_header"
                ]["process_id"][0]
                packet_category = l0[current_packet_type][current_packet_name][
                    "packet_header"
                ]["packet_category"][0]
                current_packet_apid = compute_apid(process_id, packet_category)

                if (
                    current_packet_type == "TM"
                    and self.exclude_tm_apid
                    and current_packet_apid in self.exclude_tm_apid
                ):
                    logger.debug(
                        f"{current_packet_name} ({current_packet_apid}) "
                        f"is in excluded apid list ({self.exclude_tm_apid})"
                    )
                    continue
                if (
                    current_packet_type == "TC"
                    and self.exclude_tc_apid
                    and current_packet_apid in self.exclude_tc_apid
                ):
                    logger.debug(
                        f"{current_packet_name} ({current_packet_apid}) "
                        f"is in excluded apid list ({self.exclude_tc_apid})"
                    )
                    continue

                current_packet_path = f"{current_packet_type}/{current_packet_name}"
                packet_list.append(current_packet_path)
                packet_count[current_packet_type] += int(
                    l0[current_packet_path].attrs["COUNT"]
                )

        logger.info(
            f"{packet_count['TM']}/{l0['TM'].attrs['COUNT']} TM and "
            f"{packet_count['TC']}/{l0['TC'].attrs['COUNT']} TC loaded "
            f"from {self.current_l0_file}\t[{self.job_id}]"
        )
        self.tm_count += packet_count["TM"]
        self.tc_count += packet_count["TC"]
        self.total_count = self.tm_count + self.tc_count

        # Loop over each TM/TC packet in L0
        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:
            # Start the load operations and mark each future with its file
            future_to_packet = {
                executor.submit(
                    self.insert_packet,
                    l0,
                    current_packet,
                ): current_packet
                for current_packet in packet_list
            }

            for i, future in enumerate(
                concurrent.futures.as_completed(future_to_packet)
            ):
                current_packet = future_to_packet[future]
                try:
                    n_pkt_to_insert, n_pkt_inserted = future.result()
                except AttributeError:
                    logger.exception(
                        f"Insertion has failed for {current_packet} in {self.current_l0_file}!\t[{self.job_id}]"
                    )
                    failed_count += int(l0[current_packet].attrs["COUNT"])
                else:
                    if n_pkt_inserted > 0:
                        logger.debug(
                            f"{n_pkt_to_insert}/{n_pkt_to_insert} {current_packet} packets inserted from {self.current_l0_file}\t[{self.job_id}]"
                        )
                    inserted_count += n_pkt_inserted

        return inserted_count, failed_count

    def insert_packet(self, l0: h5py._hl.files.File, packet_name: str) -> tuple:
        """
        Insert data for the input packet name found in L0 file

        :param l0: h5.group (root) in the L0 file
        :type l0: h5py._hl.files.File
        :param packet_name: Name of packet for which data must be inserted
        :type packet_name: string
        :return: (number of packets to insert, number of packets inserted)
        :rtype: tuple
        """
        # Initialize output
        n_pkt_inserted = 0

        # Get table class
        packet_type = packet_name[:2].upper()
        table_name = f"{packet_type.lower()}_log"
        table_model = PIPELINE_TABLES[table_name]

        # Convert input l0 packet data to pandas.DataFrame
        current_df = self.packet_to_dataframe(l0, packet_name)
        n_pkt_to_insert = current_df.shape[0]
        if n_pkt_to_insert == 0:
            logger.warning(f"No {packet_name} to insert from {self.current_l0_file}!")
            return 0, 0

        if not self.param_only:
            logger.debug(
                f"{n_pkt_to_insert} {packet_name} found in {self.current_l0_file}"
            )
            # Only keep tm_log/tc_log columns to insert
            if "data" not in current_df.columns:
                columns = get_columns(table_model, remove=["id", "binary", "data"])
            else:
                columns = get_columns(table_model, remove=["id", "binary"])

            # Database table constraint to use for DO NOTHING
            if table_name == "tm_log":
                constraint = "tm_log_sha_cuc_coarse_time_key"
            elif table_name == "tc_log":
                constraint = "tc_log_sha_key"
            else:
                constraint = None

            # convert to list of dictionaries
            data_to_insert = current_df[columns].to_dict("records")
            # Insert packet metadata
            n_pkt_inserted = insert_on_conflict_nothing(
                table_model,
                self.session,
                data_to_insert,
                constraint=constraint,
            )
        else:
            logger.debug(
                f"Inserting {packet_name} packet parameters from {self.current_l0_file}"
            )

        # Insert other tables data
        self._insert_packet_param(packet_name, current_df)

        return n_pkt_to_insert, n_pkt_inserted

    def packet_to_dataframe(
        self, l0: h5py._hl.files.File, packet_name: str
    ) -> pd.DataFrame:
        """
        Convert data of input l0 packet into pandas.DataFrame object.

        :param l0: l0 file packets data:
        :type l0: h5py._hl.files.File
        :param packet_name: name of the packet for which data must be converted
        :type packet_name: string
        :return: instance of pandas.DataFrame containing packet data
        :rtype: pandas.DataFrame
        """

        # Get packet type (TM or TC)
        packet_type = packet_name[:2]
        data_grp = PACKET_DATA_GROUP[packet_type]

        # Get number of packets
        packet_nsamp = l0[packet_name].attrs["COUNT"]

        # Get packet header
        packet_header = load_param(l0[packet_name]["packet_header"])
        # Get packet data field header
        data_field_header = load_param(l0[packet_name]["data_field_header"])

        # Compute APID of the packet
        packet_apid = compute_apid(
            packet_header.process_id[0], packet_header.packet_category[0]
        )

        # Get packet data
        packet_data = load_param(l0[packet_name][data_grp])

        # Concatenate packet headers and data dataframes
        packet_df = pd.concat([packet_header, data_field_header, packet_data], axis=1)

        # Use a dict first to store data (to avoid Pandas PerformanceWarning)
        packet_info = dict()

        # Add insertion time
        packet_info["insert_time"] = [self.insert_time] * packet_nsamp

        # Get packet_length
        packet_info["length"] = packet_df["packet_length"].to_list()

        # Add APID
        packet_info["apid"] = [packet_apid] * packet_nsamp

        # Store packet utc time values
        packet_info["utc_time"] = l0[packet_name]["utc_time"][()]

        # Store packet binary data (as hexa string)
        packet_info["binary"] = l0[packet_name]["binary"][()]

        packet_info["utc_time_is_predictive"] = [self.is_predictive_time] * packet_nsamp

        packet_info["palisade_id"] = [packet_name.split("/")[-1]] * packet_nsamp
        packet_info["srdb_id"] = [l0[packet_name].attrs["SRDB_ID"]] * packet_nsamp
        packet_info["category"] = [
            l0[packet_name].attrs["PACKET_CATEGORY"]
        ] * packet_nsamp

        # Add info to dataframe
        packet_df = pd.concat([packet_df, pd.DataFrame.from_dict(packet_info)], axis=1)

        # Convert utc_time byte strings into datetime objects
        packet_df["utc_time"] = packet_df["utc_time"].apply(
            lambda x: datetime.strptime(
                x.decode("UTF-8")[:-4] + "Z", TIME_ISO_STRFORMAT
            )
        )

        # Convert binary from bytes to string
        packet_df["binary"] = packet_df["binary"].apply(lambda x: x.decode("UTF-8"))

        # Case of compressed TM packets
        if "compressed" in l0[packet_name].keys():
            # Be sure that compressed TM have the right
            # PALISADE_ID, SDRB_ID and CATEGORY
            where_compressed = l0[packet_name]["compressed"][()] == 1
            packet_df.loc[where_compressed, "srdb_id"] = l0[packet_name].attrs[
                "SRDB_ID_C"
            ]
            packet_df.loc[where_compressed, "category"] = l0[packet_name].attrs[
                "PACKET_CATEGORY_C"
            ]
            packet_df.loc[where_compressed, "palisade_id"] = (
                packet_name.split("/")[-1] + "_C"
            )

        if packet_type == "TM":
            # Init dict (to avoid Pandas PerformanceWarning)
            packet_info = dict()

            # Get packet creation cuc_time
            packet_info["cuc_time"] = packet_df["time"].apply(
                lambda x: self.spice.cuc2str(x[0], x[1])
            )
            packet_info["cuc_coarse_time"] = packet_df["time"].apply(lambda x: x[0])
            packet_info["cuc_fine_time"] = packet_df["time"].apply(lambda x: x[1])

            # Compute obt_time from packet creation cuc_time
            packet_info["obt_time"] = packet_df["time"].apply(
                lambda x: self.spice.cuc2datetime(x[0], x[1])
            )

            # Get packet sync_flag
            packet_info["sync_flag"] = packet_df["time"].apply(lambda x: x[2] == 0)

            # Get TM source data
            # (Not inserted in the database)
            packet_info["data"] = [null()] * packet_nsamp

            # Add to packet_df dataframe
            packet_df = pd.concat(
                [packet_df, pd.DataFrame.from_dict(packet_info)], axis=1
            )

            try:
                # Only store data for event, HK and TC ack. TM packet types in the
                # database
                apid_to_store = EVENT_TM_APID + TC_ACK_APID + HK_TM_APID
                where_apid = packet_df["apid"].isin(apid_to_store)
                packet_df.loc[where_apid, ("data")] = packet_df.loc[
                    where_apid, l0[packet_name][data_grp].keys()
                ].to_dict("records")
            except Exception:
                # If failed, assume there is no parameter for this TM
                pass

            ## Store acquisition time (for science packets only)
            # Initialize acq_coarse_time and acq_coarse_time columns
            # with null values by default
            acq_time_info = {
                "acq_coarse_time": [None] * packet_nsamp,
                "acq_fine_time": [None] * packet_nsamp,
            }
            # then if TM packet contains one of
            # the valid acquisition time parameter
            for acq_time_pname in ACQ_TIME_PNAMES.keys():
                if acq_time_pname in packet_df:
                    # Store packet values
                    acq_time_info["acq_coarse_time"] = packet_df[acq_time_pname].apply(
                        lambda x: x[0]
                    )
                    acq_time_info["acq_fine_time"] = packet_df[acq_time_pname].apply(
                        lambda x: x[1]
                    )
                    break

            packet_df = pd.concat(
                [packet_df, pd.DataFrame.from_dict(acq_time_info)], axis=1
            )

        elif packet_type == "TC":
            # Init dict (to avoid Pandas PerformanceWarning)
            packet_info = dict()

            packet_info["unique_id"] = l0[packet_name]["unique_id"][()].astype(str)
            packet_info["sequence_name"] = l0[packet_name]["sequence_name"][()].astype(
                str
            )
            current_tc_state = l0[packet_name]["tc_ack_state"][()].astype(str)
            packet_info["tc_acc_state"] = current_tc_state[:, 0]
            packet_info["tc_exe_state"] = current_tc_state[:, 1]

            # Get TC application data
            try:
                packet_info["data"] = packet_df[
                    l0[packet_name][data_grp].keys()
                ].to_dict("records")
            except AttributeError:
                # If no application data, then just pass
                pass

            # Add to packet_df dataframe
            packet_df = pd.concat(
                [packet_df, pd.DataFrame.from_dict(packet_info)], axis=1
            )

            # Only store PASSED/FAILED TC in database
            packet_df = packet_df.loc[
                packet_df["tc_exe_state"].isin(TC_ACK_ALLOWED_STATUS)
            ]

        # If there is no packet anymore to insert, then return empty DataFrame
        if packet_df.shape[0] == 0:
            logger.debug(f"{packet_name} DataFrame is empty in {self.current_l0_file}!")
            return pd.DataFrame()

        # Compute SHA
        packet_info = {
            "sha": packet_df.apply(lambda x: get_packet_sha(x), axis=1).to_list()
        }

        # Add SHA to dataframe
        packet_df = pd.concat([packet_df, pd.DataFrame.from_dict(packet_info)], axis=1)

        # Make sure to have unique packets (unique SHA values)
        packet_df.drop_duplicates(subset=["sha"], inplace=True)

        return packet_df

    def _insert_packet_param(self, packet_name: str, packet_data: pd.DataFrame) -> int:
        """
        Insert following data for current packet:
             - sbm_log
             - bia_sweep_log
             - lfr_kcoeff_dump

        It is assumed that input data are not already stored in the
        database.

        :param packet_name: Name of the input packet
        :type packet_name: str
        :param packet_data: packet data as a pandas.DataFrame
        :type packet_data: pandas.DataFrame
        :return: number of packets inserted
        :rtype: int
        """
        constraint = None
        n_packet = packet_data.shape[0]
        packet_name = packet_name.split("/")[-1]
        # Set inputs corresponding to input packet
        if packet_name in SBM_LOG_PACKETS:
            model = SbmLog
            columns = get_columns(model, remove=["id", "retrieved_time", "sbm_subtype"])
            sbm_type = int(packet_name[-1])
            packet_data["sbm_type"] = [sbm_type] * n_packet
            packet_data["selected"] = [False] * n_packet
            packet_data["retrieved"] = [
                {"size": 0, "percent": 0, "stats": {}}
            ] * n_packet
            packet_data["status"] = [[]] * n_packet
            packet_data["sbm_qf"] = packet_data[
                f"HK_RPW_S20_SBM{sbm_type}_QF_D"
            ].astype(float)
            packet_data["sbm_algo"] = packet_data[f"SY_DPU_SBM{sbm_type}_ALGO"].astype(
                int
            )
            packet_data["sbm_algo_param"] = packet_data.apply(
                lambda x: self.extract_sbm_algo_param(x), axis=1
            )

            # Compute event occurred time
            occurred_time_key = f"HK_RPW_S20_SBM{sbm_type}_TIME_D"
            packet_data["cuc_time"] = packet_data[occurred_time_key].apply(
                lambda x: self.spice.cuc2str(x[0], x[1])
            )
            packet_data["obt_time"] = packet_data[occurred_time_key].apply(
                lambda x: self.spice.cuc2datetime(x[0], x[1])
            )
            packet_data["utc_time"] = packet_data[occurred_time_key].apply(self.cuc2utc)

            # Database table constraint to use for DO NOTHING
            constraint = "sbm_log_cuc_time_sbm_type_key"
        elif packet_name in BIA_SWEEP_LOG_PACKETS:
            model = BiaSweepLog
            columns = get_columns(model, remove=["id"])
            if packet_name == "TM_DPU_EVENT_ME_BIA_SWEEP":
                packet_data["sweep_step"] = packet_data.apply(
                    lambda x: CIWT0131TM[int(x["PA_DPU_BIA_SWEEP_ME_CODE"])],
                    axis=1,
                )
            else:
                packet_data["sweep_step"] = packet_data.apply(
                    lambda x: CIWT0130TM[int(x["PA_DPU_BIA_SWEEP_PR_CODE"])],
                    axis=1,
                )
                packet_data["utc_time"] = packet_data["PA_DPU_BIA_SWEEP_TIME"].apply(
                    self.cuc2utc
                )

            # Database table constraint to use for DO NOTHING
            constraint = "bia_sweep_log_sweep_step_utc_time_key"
        elif packet_name in LFR_KCOEFF_DUMP_PACKETS:
            model = LfrKcoeffDump
            columns = get_columns(model, remove=["id"])
            packet_data["kcoeff_pkt_cnt"] = packet_data["PA_LFR_KCOEFF_PKT_CNT"].astype(
                int
            )
            packet_data["kcoeff_pkt_nr"] = packet_data["PA_LFR_KCOEFF_PKT_NR"].astype(
                int
            )
            packet_data["kcoeff_blk_nr"] = packet_data["PA_LFR_KCOEFF_BLK_NR"].astype(
                int
            )
            packet_data["kcoeff_values"] = packet_data.apply(
                lambda x: self.extract_lfr_kcoeff(x), axis=1
            )

            # Database table constraint to use for DO NOTHING
            constraint = "lfr_kcoeff_dump_utc_time_kcoeff_pkt_nr_key"
        else:
            # Otherwise exit insertion normally
            # logger.debug(f'No extra data to insert for {packet_name}')
            return n_packet

        data_to_insert = packet_data[columns].to_dict("records")
        data_to_insert_len = len(data_to_insert)
        if data_to_insert_len > 0:
            logger.debug(
                f"Inserting {data_to_insert_len} {packet_name} data into table {model.__tablename__}"
            )
            try:
                n_packet = insert_on_conflict_nothing(
                    model,
                    self.session,
                    data_to_insert,
                    constraint=constraint,
                )
            except Exception as e:
                logger.error(
                    f"Insertion in table {model.__tablename__} has failed "
                    f"for {data_to_insert_len} {packet_name} from {self.current_l0_file}\t[{self.job_id}]"
                )
                logger.debug(e)
                n_packet = 0

            if n_packet > 0:
                logger.info(
                    f"{n_packet} entries inserted in table {model.__tablename__}\t[{self.job_id}]"
                )

        return n_packet

    def cuc2utc(self, cuc_time, naif_id=NAIF_SOLO_ID):
        """
        Convert input RPW CUC time into UTC time

        :param cuc_time:
        :return: UTC time as returned by SpiceManager.obt2utc() method
        """
        obt_time = self.spice.cuc2obt(cuc_time)
        return self.spice.obt2utc(naif_id, obt_time)

    def extract_sbm_algo_param(self, current_packet):
        """
        Extract SBM algo parameters from current packet

        :param current_packet: current packet data as a pandas.DataFrame
        :return: list of parameters returned as a JSON string
        """
        current_sbm_algo_param = {
            current_param: current_packet[current_param]
            for current_param in SBM_ALGO_PARAM_LIST[current_packet["sbm_type"]]
        }
        # Store SBM algo parameters as a JSON string
        return current_sbm_algo_param

    def extract_lfr_kcoeff(self, packet_data: pd.DataFrame) -> str:
        """
        Extract LFR Kcoeff parameters from current TM
        kcoeff data are returned in JSON format, where
        keyword is the frequency index and values are arrays of [LFR_KCOEFF_PARAM_NR, kcoeff_blk_nr] samples

        :param packet_data: current TM packet_data
        :type packet_data: pandas.DataFrame
        :return: Kcoeff parameters as a JSON string
        :rtype: str
        """
        kcoeffs = {}
        blk_nr = packet_data["kcoeff_blk_nr"]
        for current_freq in packet_data["SY_LFR_KCOEFF_FREQUENCY"]:
            kcoeffs[current_freq] = ",".join(
                [
                    str(packet_data[f"SY_LFR_KCOEFF_{j + 1}"][0:blk_nr])
                    for j in range(LFR_KCOEFF_PARAM_NR)
                ]
            )

        return json.dumps(kcoeffs)


def get_l0_files(pipeline):
    try:
        l0_files = pipeline.args.rpw_l0_files
        if not isinstance(l0_files, list):
            l0_files = [l0_files]
        return sorted(l0_files)
    except Exception as e:
        # If not defined as input argument, then assume that it is already
        # defined as target input
        logger.debug(e)
        pass


def load_param(current_group: h5py.Group) -> pd.DataFrame:
    """
    Sub-methods to save h5py.Data array in
    a pandas.DataFrame

    :param current_group: H5 group to convert
    :type current_group: h5py.Group
    :return: DataFrame with h5py.Data
    :rtype: pandas.DataFrame
    """
    # Input group must be a h5py.Group object
    if not isinstance(current_group, h5py.Group):
        return pd.DataFrame()

    current_df = dict()
    for key, val in current_group.items():
        current_val = val[()]
        if len(current_val.shape) > 1:
            arr = sparse.coo_matrix(current_val)
            current_df[key] = arr.toarray().tolist()
        else:
            current_df[key] = current_val

    return pd.DataFrame.from_dict(current_df)
