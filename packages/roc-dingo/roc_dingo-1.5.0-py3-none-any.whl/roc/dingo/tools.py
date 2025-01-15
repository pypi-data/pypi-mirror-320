#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
import argparse
import time
from datetime import datetime
import hashlib
import shutil

import h5py
import math
import numpy
from typing import Union, Type

import pandas as pd
import sqlalchemy
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import true
from sqlalchemy import and_

from poppy.core.logger import logger
from poppy.core.db.handlers import get_or_create_with_info

from spice_manager import SpiceManager

from roc.rpl.packet_parser import raw_to_eng
from roc.idb.models.idb import IdbRelease

from roc.dingo.constants import (
    TIME_DAILY_STRFORMAT,
    TIME_INPUT_STRFORMAT,
    SQL_LIMIT,
    TRYOUTS,
    TIME_WAIT_SEC,
    TF_CP_BIA_P011_SRDB_ID,
    IDB_SOURCE,
    NAIF_SOLO_ID,
)

from roc.dingo.exceptions import DingoException, DbQueryError

__all__ = [
    "cuc2utc",
    "hex_to_bytes",
    "insert_on_conflict_nothing",
    "insert_on_conflict_update",
    "valid_time",
    "valid_date",
    "valid_dir",
    "valid_data_version",
    "glob_paths",
    "get_packet_sha",
    "get_dict_sha",
    "get_current_idb",
    "compute_apid",
    "compute_pkt_seq_control",
    "load_spice",
    "insert_in_db",
    "safe_move",
    "get_or_create_in_db",
    "query_db",
    "delete_in_db",
    "actual_sql",
    "gen_sql_filters",
    "is_sclk_uptodate",
    "get_columns",
    "bulk_insert",
    "sbm_qf_eng",
    "raw_to_na",
    "compute_hfr_list_freq",
    "round_up",
]


def cuc2utc(
    spice_object: SpiceManager,
    cuc_time: Union[list, tuple, numpy.ndarray],
    naif_id: int = NAIF_SOLO_ID,
) -> str:
    """
    Convert input RPW CUC time into UTC time

    :param spice_object: SpiceManager class instance
    :param cuc_time: CUC time
    :param naif_id: NAIF SPICE ID
    :return: UTC time as returned by SpiceManager.obt2utc() method
    """
    obt_time = spice_object.cuc2obt(cuc_time)
    return spice_object.obt2utc(naif_id, obt_time)


def hex_to_bytes(string: str) -> bytearray:
    """
    Convert a hexadecimal string into a byte array.

    :param string: hexadecimal string to convert
    :return: input string as a byte array
    """
    # transform to an array of bytes
    return bytearray.fromhex(string)


def insert_on_conflict_nothing(
    table: Type[object],
    session: sqlalchemy.orm.Session,
    data_to_insert: list,
    commit: bool = True,
    index_elements: list = None,
    constraint: str = None,
) -> int:
    """
    Apply Insert.on_conflict_do_nothing() method in case of index conflict(s).

    :param table: name of the database table
    :type table: See sqlalchemy.dialects.postgresql.insert
    :param session: database session object
    :type session: sqlalchemy.orm.Session
    :param data_to_insert: data to be inserted as a list of dictionaries
    :type data_to_insert: list
    :param commit: whether to run session.commit() or not (default True)
    :type commit: bool
    :param index_elements: A sequence consisting of string column names,
    Column objects, or other column expression objects that will be used to infer a target index.
    :type index_elements: list
    :param constraint: The name of a unique or exclusion constraint on the table,
    or the constraint object itself if it has a .name attribute.
    :type constraint: str
    :return: number of data inserted
    """

    stmt = (
        insert(table)
        .values(data_to_insert)
        .on_conflict_do_nothing(index_elements=index_elements, constraint=constraint)
    )
    result = session.execute(stmt)
    if commit:
        session.commit()

    return result.rowcount


def insert_on_conflict_update(
    table: Type[object],
    session: sqlalchemy.orm.Session,
    data_to_insert: list,
    index_elements: list = None,
    constraint: str = None,
    set_: dict = None,
    set_from_excluded: bool = False,
    commit: bool = True,
) -> int:
    """
    Apply Insert.on_conflict_do_update() method in case of index conflict(s).
    See sqlalchemy.dialects.postgresql.Insert.on_conflict_do_update() documentation for details.

    :param table: name of the database table
    :type table: See sqlalchemy.dialects.postgresql.insert
    :param session: database session object
    :type session: sqlalchemy.orm.Session
    :param data_to_insert: data to be inserted as a list of dictionaries
    :type data_to_insert: list
    :param index_elements: A sequence consisting of string column names,
    Column objects, or other column expression objects that will be used to infer a target index.
    :type index_elements: list
    :param constraint: The name of a unique or exclusion constraint on the table,
    or the constraint object itself if it has a .name attribute.
    :type constraint: str
    :param set_: A dictionary or other mapping object where the keys are either
    names of columns in the target table, or Column objects or
    other ORM-mapped columns matching that of the target table,
    and expressions or literals as values, specifying the SET actions to take.
    :type set_: dict
    :param set_from_excluded: If True then fill set_ input automatically from stmt.excluded columns
    :type set_from_excluded: bool
    :param commit: whether to run session.commit() or not (default True)
    :type commit: bool
    :return: number of data inserted
    """

    stmt = insert(table).values(data_to_insert)

    if set_from_excluded:
        set_ = {col: getattr(stmt.excluded, col) for col in data_to_insert[0]}

    stmt = stmt.on_conflict_do_update(
        index_elements=index_elements, constraint=constraint, set_=set_
    )

    result = session.execute(stmt)
    if commit:
        session.commit()

    return result.rowcount


def valid_dir(str_dir: Union[str, list]) -> str:
    """
    Make sure to have a valid input directory.

    :param str_dir: 1-element list or string containing the path to the directory
    :type str_dir: Union[str, list]
    :return: input directory if valid
    :rtype: str
    """
    try:
        if isinstance(str_dir, list):
            str_dir = str_dir[0]
        if os.path.isdir(str_dir):
            return str_dir
        else:
            raise IsADirectoryError
    except IsADirectoryError:
        raise_error(
            f"Input directory not found! ({str_dir})", exception=IsADirectoryError
        )
    except ValueError:
        raise_error(f"Input directory is not valid! ({str_dir})", exception=ValueError)
    except Exception as e:
        raise_error(f"Problem with input directory! ({str_dir})", exception=e)


def glob_paths(paths: Union[str, list]) -> list:
    """
    Make sure input paths are expanded
    (can be used to avoid any path with wildcard pattern)

    :param paths: list of input paths to glob
    :type paths: Union[str, list]
    :return: list of paths after glob filtering
    :rtype: list
    """
    globbed_paths = []
    if not isinstance(paths, list):
        paths = [paths]

    for current_path in paths:
        globbed_paths.extend(glob.glob(current_path))

    return globbed_paths


def round_up(n: float, decimals: int = 0) -> float:
    """
    Compute round of input float

    :param n: input float
    :type n: float
    :param decimals: round precision
    :type decimals: int
    :return: rounded float
    :rtype: float
    """
    multiplier = 10**decimals
    return math.ceil(n * multiplier) / multiplier


def raise_error(message: str, exception: Type[Exception] = DingoException):
    """Add an error entry to the logger and raise an exception."""
    logger.error(message)
    raise exception(message)


def valid_time(t: str, str_format: str = TIME_INPUT_STRFORMAT) -> datetime:
    """
    Validate input datetime string format.

    :param t: input datetime string
    :type t: str
    :param str_format: expected datetime string format
    :type str_format: str
    :return: datetime object with input datetime info
    :rtype: datetime.datetime
    """
    if t and isinstance(t, str):
        try:
            t = datetime.strptime(t, str_format)
        except ValueError:
            logger.error(f"Not a valid time: '{t}'!")
            raise

    return t


def valid_date(
    t_in: str, str_tformat: str = TIME_DAILY_STRFORMAT
) -> Union[datetime, None]:
    """
    Validate input date string format.

    :param t_in: input date string
    :type t_in: str
    :param str_tformat: expected date string format
    :type str_tformat: str
    :return: date object with input date info
    :rtype: datetime.datetime
    """
    t_out = t_in
    if t_in and isinstance(t_in, str):
        try:
            t_out = datetime.strptime(t_in, str_tformat).date()
        except ValueError:
            argparse.ArgumentTypeError(f"Not a valid date: '{t_in}'!")
    return t_out


def valid_data_version(data_version: Union[str, int]) -> str:
    """
    Make sure to have a valid data version.

    :param data_version: integer or string containing the data version
    :type data_version: Union[str, int]
    :return: string containing valid data version (i.e., 2 digits string):
    :rtype: str
    """
    try:
        data_version = int(data_version)
        return f"{data_version:02d}"
    except ValueError:
        raise_error(
            f"Input value for --data-version is not valid! \
                     ({data_version})"
        )


def get_packet_sha(packet_data: Union[h5py.Group, dict]) -> str:
    """
    Compute the SHA256 of the input packet.
    TM sha is computed from binary
    TC sha is computed from packet name (SRDB ID), execution UTC time and status

    :param packet_data: data of the input packet
    :type packet_data: h5py.Group or dict
    :return: string containing SHA (hexdigest)
    :rtype: str
    """
    sha = None
    packet_name = packet_data["palisade_id"]
    if packet_name.startswith("TC"):
        raw_sha = hashlib.sha256()
        raw_sha.update(packet_data["srdb_id"].encode("utf-8"))
        raw_sha.update(packet_data["utc_time"].isoformat().encode("utf-8"))
        raw_sha.update(packet_data["tc_exe_state"].encode("utf-8"))
        sha = str(raw_sha.hexdigest())
    elif packet_name.startswith("TM"):
        raw_sha = hashlib.sha256()
        raw_sha.update(packet_data["binary"].encode("utf-8"))
        sha = str(raw_sha.hexdigest())
    else:
        logger.error(f"Unknown packet name: {packet_name}")

    return sha


def get_dict_sha(dict_to_hash: dict, include=None, exclude=None) -> str:
    """
    Compute a SHA256 from the values in an input dictionary

    :param dict_to_has: input dictionary to hash
    :type dict_to_hash: dict
    :param include: keywords to include.
    :type include: list
    :param exclude: keywords to ignore
    :type exclude: list
    :return: SHA as a hexa digest string
    """
    sha = hashlib.sha256()
    for key, val in dict_to_hash.items():
        if include and key not in include:
            continue
        if exclude and key in exclude:
            continue
        if isinstance(val, datetime):
            sha.update(val.isoformat().encode("utf-8"))
        else:
            sha.update(str(val).encode("utf-8"))

    return str(sha.hexdigest())


def compute_apid(
    process_id: Union[int, numpy.uint8], packet_category: Union[int, numpy.uint8]
) -> int:
    """
    Compute the APID using the process_id and the packet_category
    APID = |0000000|0000|
        process_id | packet_category

    :param process_id: process id
    :type process_id: Union[int, numpy.uint8]
    :param packet_category: packet category
    :type packet_category: Union[int, numpy.uint8]
    :return: APID
    :rtype: int
    """
    return int((process_id << 4) + packet_category)  # 4 bits shift


def compute_pkt_seq_control(segmentation_grouping_flag, sequence_cnt):
    """
    Compute Packet Sequence Control field for a given packet

    :param segmentation_grouping_flag: Integer storing the packet segmentation_grouping_flag
    :param sequence_cnt: Integer containing the packet sequence counter
    :return: Packet Sequence Control (16-bits)
    """
    return (segmentation_grouping_flag << 14) + sequence_cnt


def load_spice(spice_kernels=[]):
    """
    Load SpiceManager instance with input SOLO kernels

    :param spice_kernels: List of input kernels to load in SPICE
    :return: SpiceManager instance
    """
    from spice_manager import SpiceManager

    return SpiceManager(spice_kernels, logger=logger)


def insert_in_db(
    session,
    model,
    data_to_insert,
    update_fields={},
    update_fields_kwargs={},
    tryouts=TRYOUTS,
    wait=TIME_WAIT_SEC,
):
    """
    Insert a data entry in the database

    :param session: open database session
    :param model: database model to use for input data
    :param data_to_insert: data to insert as an entry in the database
    :param update_fields: If entry already exists in the database,
                            then update only fields provided in this dictionary
    :param update_fields_kwargs: dictionary to pass to filter_by() method when query for updating
    :param tryouts: number of tries
    :param wait: seconds to wait between two tries
    :return: insertion status (0=OK, -1=NOK, 1=Already inserted, 2=Updated)
    """
    # if update_fields_kwargs not provided,
    # then use data_to_insert dictionary
    if not update_fields_kwargs:
        update_fields_kwargs = data_to_insert

    for i in range(tryouts):
        try:
            # Add current data as a new entry of the model table
            # in the database
            session.add(model(**data_to_insert))
            # Commit database change(s)
            session.commit()
        except IntegrityError:
            session.rollback()
            logger.debug(f"{data_to_insert} already inserted")
            # If entry already exists,
            # check if fields needs to be updated
            if update_fields:
                logger.debug(f"Updating {update_fields} in the database ...")
                instance = session.query(model).filter_by(**update_fields_kwargs).one()
                # update it
                for field in update_fields or {}:
                    if getattr(instance, field) != update_fields[field]:
                        setattr(instance, field, update_fields[field])
                session.commit()
                insert_status = 2
            else:
                insert_status = 1
            break
        except Exception as e:
            session.rollback()
            logger.error(f"Inserting {data_to_insert} has failed!")
            logger.debug(e)
            insert_status = -1
            time.sleep(wait)
        else:
            logger.debug(f"{data_to_insert} inserted")
            insert_status = 0
            break

    return insert_status


def safe_move(src, dst, ignore_patterns=[], copy=False):
    """
    Perform a safe move of a file or directory.

    :param src: string containing the path of the file/directory to move
    :param dst: string containing the path of the target file/directory
    :param ignore_patterns: string containing the file patterns to ignore (for copytree only)
    :param copy: if passed, copy files/dirs
    :return: True if the move has succeeded, False otherwise
    """

    # Initialize output
    is_copied = False

    # First do a copy...
    try:
        if os.path.isfile(src):
            shutil.copy(src, dst, follow_symlinks=True)
        elif os.path.isdir(src):
            shutil.copytree(
                src,
                dst,
                ignore=shutil.ignore_patterns(ignore_patterns),
                dirs_exist_ok=True,
            )
    except Exception as e:
        logger.exception(f"Cannot move {src} into {dst}!")
        raise e
    else:
        # then delete if the file has well copied
        if os.path.exists(dst):
            is_copied = True
            if os.path.isfile(src) and not copy:
                os.remove(src)
            elif os.path.isdir(src) and not copy:
                shutil.rmtree(src)

    return is_copied


def query_db(
    session,
    model,
    filters=None,
    limit=SQL_LIMIT,
    order_by=None,
    to_dict=None,
    is_one=False,
    tryouts=TRYOUTS,
    wait=TIME_WAIT_SEC,
    raise_exception=False,
):
    """
    Query entries from the ROC pipeline database.

    :param session: ROC database open session
    :param model: Table model class
    :param filters: query filters passed as a SQL expression object
    :param limit: Integer containing max. number of returned rows
    :param order_by: Sort returned rows by column value passed in order_by keyword
    :param to_dict: If passed with argument, apply the pandas.DataFrame.to_dict(orient=arg) method
    :param is_one: If True, only one entry is expected.
    :param tryouts: Number of query retries
    :param wait: number of seconds to wait between two retries
    :param raise_exception: If True, raise an exception
    :return: entries found in the database as returned by pandas.read_sql() method
    """
    # Initialize output
    table_entries = None
    # Run query
    has_failed = True
    for current_try in range(tryouts):
        try:
            if isinstance(model, list) or isinstance(model, tuple):
                query = session.query(*model)
            else:
                query = session.query(model)
            if filters is not None:
                query = query.filter(filters)
            if order_by is not None:
                query = query.order_by(order_by)
            query.limit(int(limit))
            logger.debug(f"Querying database: {actual_sql(query)} ...")
            table_entries = pd.read_sql(query.statement, session.bind)
            nrec = table_entries.shape[0]
            if nrec == 0:
                raise NoResultFound
            elif is_one and nrec != 1:
                raise MultipleResultsFound
        except MultipleResultsFound:
            logger.exception("Query has returned multiple results!")
            break
        except NoResultFound:
            logger.debug("No results found")
            has_failed = False
            break
        except Exception as e:
            logger.error("Query has failed!")
            logger.debug(e)
        else:
            # logger.debug(f'{query.count()} entries found in the {model} table for {filters}')
            # Convert returned entries into list of lists
            if to_dict:
                table_entries = table_entries.to_dict(orient=to_dict)

            has_failed = False
            break
        logger.debug(f"Retrying query ({current_try} on {tryouts})")
        time.sleep(wait)

    if has_failed and raise_exception:
        raise DbQueryError(f"Querying database with model {model} has failed!")

    return table_entries


def get_or_create_in_db(
    session, model, entry, kwargs=None, tryouts=TRYOUTS, wait=TIME_WAIT_SEC
):
    """
    Insert input entry to pipeline.data_queue table

    :param session: database session object
    :param model: Database table model class
    :param entry: A dictionary containing column:value to insert in the table
    :param kwargs: A dictionary containing the column:value to use to get data
    :param tryouts: number of tries to insert data
    :param wait: seconds to wait between two tries
    :return: (table entry created, database request status flag, creation status flag)
    """
    job = None
    created = None
    done = False
    if not kwargs:
        kwargs = entry
    for current_try in range(tryouts):
        try:
            job, created = get_or_create_with_info(
                session, model, **kwargs, create_method_kwargs=entry
            )
        except Exception as e:
            logger.error(
                f"Cannot query {model.__tablename__} [retry {tryouts - current_try}]"
            )
            logger.debug(e)
            time.sleep(wait)
        else:
            done = True
            break

    return job, done, created


def bulk_insert(
    session,
    model,
    data_to_insert,
    tryouts=TRYOUTS,
    wait=TIME_WAIT_SEC,
    exists_ok=False,
    raise_exception=True,
):
    """
    Run the bulk_insert_mappings() SQLAlchemy method
    to insert a bulk of data into the database.

    :param session: current database session
    :param model: database table model class
    :param data_to_insert: List of dictionaries to insert in the database
    :param tryouts: number of insertion attempts
    :param wait: seconds to wait between two attempts
    :param raise_exception: if true raise an exception
    :param exists_ok: If True then insertion is OK if entry is already found in the database
    :return: True if insertion has worked, False otherwise
    """
    has_worked = False
    raised_exc = Exception()
    for current_try in range(tryouts):
        try:
            session.bulk_insert_mappings(model, data_to_insert)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raised_exc = e
            if exists_ok:
                has_worked = True
            break
        except Exception as e:
            session.rollback()
            time.sleep(wait)
            raised_exc = e
        else:
            has_worked = True
            break

    if not has_worked and raise_exception:
        raise raised_exc

    return has_worked


def delete_in_db(session, model, filters=None, tryouts=TRYOUTS, wait=TIME_WAIT_SEC):
    """
    Delete row(s) of a table in the database

    :param session: database session
    :param model: Table model
    :param filters: list of filters
    :param tryouts: number of tries
    :param wait: seconds to wait between two tries
    :return: True if deletion has succeeded, False otherwise
    """
    is_deleted = False
    for current_try in range(tryouts):
        try:
            query = session.query(model)
            if filters:
                query.filter(filters)
            query.delete()
            session.commit()
        except NoResultFound:
            is_deleted = True
            break
        except Exception as e:
            logger.error(f"Deleting {model} with filters {filters} has failed!")
            logger.debug(e)
            time.sleep(wait)
        else:
            is_deleted = True
            break

    return is_deleted


def actual_sql(sqlalchemy_query):
    """
    convert input Sqlalchemy query into explicit SQL syntax query

    :param sqlalchemy_query: input Sqlalchemy query object
    :return: string with corresponding SQL syntax
    """
    return str(
        sqlalchemy_query.statement.compile(compile_kwargs={"literal_binds": True})
    )


def is_sclk_uptodate(current_datetime, sclk_basename):
    """
    Check if the input SOLO SCLK SPICE kernel is newer or older than a give datetime

    :param current_datetime: datetime.datetime object to compare with SOLO SCLK SPICE kernel date
    :param sclk_basename: string containing SOLO SCLK SPICE kernel basename
    :return: True if SCLK SPICE kernel is newer than current_datetime
            , False otherwise
    """
    # Get the date of the SCLK SPICE kernel
    sclk_date = datetime.strptime(
        sclk_basename.split("_")[3],
        TIME_DAILY_STRFORMAT,
    ).date()

    return sclk_date > current_datetime.date()


def get_columns(model, remove=[]):
    """
    Get list of table columns for input model class

    :param model: Table model class
    :param remove: list of columns to remove
    :return: list of table columns
    """
    # Get columns
    columns = model.__table__.columns.keys()
    for key in remove:
        columns.remove(key)
    return columns


def raw_to_na(raw_values, idb_source=IDB_SOURCE, idb_version=None):
    """
    Convert input raw values of bias current into physical units (nA)

    :param raw_values: numpy array with raw values of Bias current
    :param idb_version: string with idb version
    :param idb_source: string with idb_source
    :return: values in physical units (nA)
    """

    # Retrieve engineering values in uA and return them in nA
    return (
        raw_to_eng(
            raw_values,
            TF_CP_BIA_P011_SRDB_ID,
            idb_source=idb_source,
            idb_version=idb_version,
        )
        * 1000
    )


def sbm_qf_eng(raw_values, tf_srdb_id, idb_source="MIB", idb_version=None):
    """
    Retrieve engineering values of the SBM1/SBM2 event quality factor

    :param raw_values: SBM1 QF raw values
    :param tf_srdb_id: SBM1/SBM2 F Transfer function SRDB ID (i.e, TF_PA_DPU_0038 or =TF_PA_DPU_0039)
    :param idb_source:
    :param idb_version:
    :return: engineering values of SBM1 QF
    """
    return raw_to_eng(
        raw_values, tf_srdb_id, idb_source=idb_source, idb_version=idb_version
    )


def get_current_idb(idb_source, session, tryouts=TRYOUTS, wait=TIME_WAIT_SEC):
    """
    Get current idb release stored in the database

    :param idb_source: IDB source to use (MIB, SRDB or PALISADE).
    :param session: database session
    :param tryouts: number of tries
    :param wait: seconds to wait between two tries
    :return: version of the idb tagged as current, None if not found
    """
    idb_version = None

    filters = [IdbRelease.idb_source == idb_source, IdbRelease.current == true()]
    for i in range(tryouts):
        try:
            query = session.query(IdbRelease.idb_version).filter(and_(*filters))
            results = query.one()
        except MultipleResultsFound:
            logger.error(f"Multiple results found for {actual_sql(query)}!")
            break
        except NoResultFound:
            logger.info(f"No result found for {actual_sql(query)}")
            break
        except Exception as e:
            logger.error(
                f"Cannot run {actual_sql(query)} (trying again in {wait} seconds)"
            )
            logger.debug(e)
            time.sleep(wait)
        else:
            idb_version = results.idb_version
            break

    return idb_version


def gen_sql_filters(model, start_time=None, end_time=None, field="utc_time"):
    """
    Generate common filters for query.

    :param model: table class
    :start_time: query rows greater or equal than start_time only (datetime object)
    :end_time: query rows lesser than end_time only (datetime object)
    :param field: field to use for filters
    :return: list of filters
    """
    filters = []
    if start_time:
        filters.append(model.__dict__[field] >= start_time)
    if end_time:
        filters.append(model.__dict__[field] < end_time)

    return and_(*filters)


def compute_hfr_list_freq(freq_index):
    """
    In HFR LIST mode, return frequency value in kHz giving its
    index

    :param freq_index: index of the frequency
    :return: Value of the frequency in kHz
    """
    return 375 + 50 * (int(freq_index) - 436)
