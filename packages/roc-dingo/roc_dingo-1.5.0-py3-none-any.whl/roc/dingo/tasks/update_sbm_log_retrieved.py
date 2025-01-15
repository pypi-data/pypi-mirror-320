#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Contains dingo tasks to update pipeline.sbm_log.retrieved column
into the ROC database."""

import uuid
from typing import Tuple, List, Type

import pandas as pd
from sqlalchemy import and_, or_, update

from poppy.core.logger import logger
from poppy.core.db.connector import Connector
from poppy.core.task import Task

from roc.dingo.models.data import SbmLog
from roc.dingo.models.packet import TmLog
from roc.dingo.tools import query_db, valid_time, round_up, gen_sql_filters
from roc.dingo.constants import (
    PIPELINE_DATABASE,
    TIME_DAILY_STRFORMAT,
    TRYOUTS,
    TIME_WAIT_SEC,
    SQL_LIMIT,
    SBM_SCI_PKT_LIST,
    SBM_SCI_PKT_MAX_NB,
)

__all__ = ["UpdateSbmRetrieved"]


class UpdateSbmRetrieved(Task):
    """
    Update pipeline.sbm_log.retrieved column
    from information provided in the
    pipeline.tm_log table.
    """

    plugin_name = "roc.dingo"
    name = "update_sbm_retrieved"

    def add_targets(self):
        pass

    @Connector.if_connected(PIPELINE_DATABASE)
    def setup_inputs(self):
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

        # get a database session
        self.session = Connector.manager[PIPELINE_DATABASE].session

        # Get tryouts from pipeline properties
        self.tryouts = self.pipeline.get("tryouts", default=[TRYOUTS], create=True)[0]

        # Get wait from pipeline properties
        self.wait = self.pipeline.get("wait", default=[TIME_WAIT_SEC], create=True)[0]

        # Retrieve --limit keyword value
        self.limit = self.pipeline.get(
            "limit",
            default=[SQL_LIMIT],
        )[0]

    def run(self):
        # Define task job ID (long and short)
        self.job_uuid = str(uuid.uuid4())
        self.job_id = self.job_uuid[:8]
        logger.info(f"Job {self.job_id} is starting")
        try:
            self.setup_inputs()
        except Exception as e:
            logger.error(f"Initializing inputs has failed for {self.job_id}!")
            logger.debug(e)
            self.pipeline.exit()
            return

        # Query SBM events list from ROC database
        model = SbmLog

        filters = list()
        # Add start_time/end_time filters (if passed)
        if self.start_time:
            filters.append(model.utc_time >= str(self.start_time))
        if self.end_time:
            filters.append(model.utc_time <= str(self.end_time))

        results = query_db(
            self.session,
            model,
            filters=(and_(*filters) if filters else None),
            tryouts=self.tryouts,
            wait=self.wait,
            limit=self.limit,
            order_by=model.utc_time,
            to_dict="records",
        )

        n_rec = len(results)
        logger.info(f"{n_rec} SBM event(s) found in pipeline.sbm_log")
        if n_rec == 0:
            return

        # Define data buffer time range functions
        sbm_trange_func = {1: self.compute_sbm1_trange, 2: self.compute_sbm2_trange}

        # Loop on each SBM event
        for i, current_sbm in enumerate(results):
            current_sbm_type = current_sbm["sbm_type"]
            current_sbm_utc = current_sbm["utc_time"]

            # Compute data buffer time range
            # (returned the coarse part of the on-board time only)
            current_sbm_start, current_sbm_end = sbm_trange_func[current_sbm_type](
                current_sbm
            )

            # Extend time range by N seconds before/after
            # to make sure to retrieve all SBM event packets
            # For the current event
            N = 60
            current_sbm_start -= N
            current_sbm_end += N

            # Retrieve SBM event science packets from pipeline.TmLog table
            current_sbm_tm = self.query_sbm_tm_data(
                current_sbm_type, current_sbm_start, current_sbm_end
            )
            n_pkt = len(current_sbm_tm)
            logger.info(
                f"{n_pkt} SBM{current_sbm_type} packets "
                f"retrieved from pipeline.tm_log for event occurred at "
                f"{current_sbm_utc}\t [{n_rec - i - 1}]"
            )

            # Compute info from SBM science packet data
            # and update sbm_log.retrieved column
            _ = self.update_sbm_log(current_sbm_type, current_sbm_tm, current_sbm["id"])

    @staticmethod
    def compute_sbm1_trange(event_data: dict) -> Tuple[int, int]:
        """
        Compute time range of SBM1 event
        using event CUC time in input sbm_log data.
        Only coarse part is returned.

        :param event_data: dictionary containing SBM1 event data from sbm_log

        :return: tuple (start_time, end_time)
        """
        # sbm1_time = source_data['HK_RPW_S20_SBM1_TIME_D']
        utc_time = event_data["utc_time"]
        cuc_time = event_data["cuc_time"]
        cuc_coarse = int(cuc_time.split(":")[0])
        dt1 = event_data["sbm_algo_param"]["SY_DPU_SBM1_DT1_SBM1_D"]
        dt2 = event_data["sbm_algo_param"]["SY_DPU_SBM1_DT2_SBM1_D"]
        dt3 = event_data["sbm_algo_param"]["SY_DPU_SBM1_DT3_SBM1_D"]

        start_time = cuc_coarse - int(0.5 * dt2) - 1
        end_time = cuc_coarse + int(0.5 * dt2) + 1

        end_time_dt3 = cuc_coarse + round_up(dt1 + dt3)
        if end_time_dt3 > end_time:
            logger.debug(
                f"DT1_SBM1[{dt1}] + DT3_SBM1[{dt3}] > 0.5 * DT2_SBM1[{dt2}] for SBM1 event at {utc_time} [{cuc_time}]"
            )
            end_time = end_time_dt3

        return start_time, end_time

    @staticmethod
    def compute_sbm2_trange(event_data: dict) -> Tuple[int, int]:
        """
        Compute time range of SBM2 event
        using event on-board cuc time in input sbm_log data.
        Only coarse part is returned.

        :param event_data: dictionary containing SBM2 event data from sbm_log

        :return: start_time, end_time
        """
        dt = event_data["sbm_algo_param"]["HK_DPU_SBM2_DT_SBM2"]

        start_time = int(event_data["cuc_time"].split(":")[0])
        end_time = start_time + int(dt)
        # print('sbm2', utc, start_time, end_time, dt)

        return start_time, end_time

    def query_sbm_tm_data(
        self, sbm_type: int, sbm_obt_start: int, sbm_obt_end: int, model=TmLog
    ) -> Type[pd.DataFrame]:
        """
        Query SBM science packet data from pipeline.tm_log table
        providing the SBM type, start and end on-board times (coarse part)

        :param sbm_type: Type of SBM (1 or 2)
        :type sbm_type: int
        :param sbm_obt_start: SBM data buffer start on-board time (obt coarse part)
        :type sbm_obt_start: int
        :param sbm_obt_end: SBM data buffer end on-board time (obt coarse part)
        :type sbm_obt_end: int
        :param model: Database table model to use.
        :type model: SQLAlchemy model class
        :return: data returned by query_db() method
        :rtype: Type[pd.DataFrame]
        """
        # Build query filters
        filters = [
            model.palisade_id == current_tm for current_tm in SBM_SCI_PKT_LIST[sbm_type]
        ]
        filters = or_(*filters)
        filters = and_(
            filters,
            gen_sql_filters(
                TmLog,
                start_time=sbm_obt_start,
                end_time=sbm_obt_end,
                field="acq_coarse_time",
            ),
        )

        # Query database
        return query_db(
            self.session,
            model,
            filters=filters,
            tryouts=self.tryouts,
            wait=self.wait,
            limit=self.limit,
        )

    def update_sbm_log(
        self,
        sbm_type: int,
        sbm_tm_data: pd.DataFrame,
        sbm_log_id: int,
        model=SbmLog,
    ) -> dict:
        """
        Extract event size, number of packets and other info
        from input SBM event data then update sbm_log.retrieved column

        :param sbm_type: type of SBM (can be 1 or 2)
        :type sbm_type: int
        :param sbm_tm_data: data as returned by self.query_sbm_data()
        :type sbm_tm_data: Type[pd.DataFrame]
        :param sbm_log_id: sbm_log id for the current event
        :type sbm_log_id: int
        :param model: database table model instance
        :type model: SQLAlchemy model class
        :return: sbm data info as dictionary
        :rtype: dict
        """
        sbm_info = {}

        # For each SBM science packet type, compute
        # the size in bytes and packet counts
        total_size = 0
        total_count = 0
        total_percent = 0.0
        retrieved_time = []
        for current_packet in SBM_SCI_PKT_LIST[sbm_type]:
            # Initialize dict for current packet
            sbm_info[current_packet] = {"size": 0, "count": 0, "percent": 0.0}

            current_index = sbm_tm_data["palisade_id"] == current_packet
            current_length = sbm_tm_data["length"][current_index]

            sbm_info[current_packet]["count"] = int(current_length.count())
            if current_length.count() == 0:
                continue
            sbm_info[current_packet]["size"] = int(
                sum(current_length) + (7 * sbm_info[current_packet]["count"])
            )
            sbm_info[current_packet]["percent"] = 100.0 * (
                float(sbm_info[current_packet]["count"])
                / float(SBM_SCI_PKT_MAX_NB[sbm_type][current_packet])
            )

            # Compute total size, count and percent
            total_size += int(sbm_info[current_packet]["size"])
            total_count += int(sbm_info[current_packet]["count"])
            total_percent += sbm_info[current_packet]["percent"]

            # For retrieved_time, get the insertion time of the
            # latest SBM science packet in tm_log
            retrieved_time.append(max(sbm_tm_data["insert_time"][current_index]))

        # Get number of expected packets
        n_pkt = len(self.get_sbm_sci_pkt_names(sbm_type, no_comp=True))
        total_percent = total_percent / float(n_pkt)

        # Update retrieved column in pipeline.sbm_log table with
        # this information
        retrieved = {
            "size": total_size,
            "percent": total_percent,
            "info": sbm_info,
        }

        values = {"retrieved": retrieved}
        if retrieved_time:
            retrieved_time = max(retrieved_time)
            values["retrieved_time"] = retrieved_time

        stmt = update(model).values(**values).where(model.id == sbm_log_id)
        self.session.execute(stmt)

        return sbm_info

    @staticmethod
    def get_sbm_sci_pkt_names(sbm_type: int, no_comp: bool = False) -> List[str]:
        """
        Get list of names of
        SBM science packets

        :param sbm_type: Type of SBM (1 or 2)
        :type sbm_type: int
        :param no_comp: remove compressed packets from the list
        :type no_comp: bool
        :return: list of names
        :rtype: List[str]
        """
        if no_comp:
            pkt_list = list(
                set(
                    [
                        current_packet.replace("_C", "")
                        for current_packet in SBM_SCI_PKT_LIST[sbm_type]
                    ]
                )
            )
        else:
            pkt_list = SBM_SCI_PKT_LIST[sbm_type]

        return pkt_list
