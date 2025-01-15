#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import datetime as dt
from datetime import timedelta

from poppy.core.logger import logger
from roc.rpl.time import Time

from roc.rap.tasks.thr.hfr_time_log import get_hfr_delta_times
from roc.rap.tasks.thr.normal_burst_tnr import decommute_normal as tnr_normal_decom
from roc.rap.tasks.thr.normal_burst_tnr import decommute_burst as tnr_burst_decom
from roc.rap.tasks.thr.normal_burst_hfr import decommute_normal as hfr_normal_decom
from roc.rap.tasks.thr.normal_burst_hfr import decommute_burst as hfr_burst_decom
from roc.rap.tasks.thr.calibration_tnr import decommute as tnr_calibration_decom
from roc.rap.tasks.thr.calibration_hfr import decommute as hfr_calibration_decom
from roc.rap.tasks.thr.science_spectral_power import decommute as spectral_power_decom

__all__ = [
    "extract_tnr_data",
    "extract_hfr_data",
    "extract_spectral_power_data",
]


# nanoseconds since POSIX epoch to J2000
POSIX_TO_J2000 = 946728000000000000


@np.vectorize
def convert_ns_to_datetime(value):
    return dt.datetime.utcfromtimestamp((value + POSIX_TO_J2000) / 1000000000)


def extract_tnr_data(l0, task):
    """
    Get the TNR data in a record array that can be easily exported into
    the CDF format.

    :param l0: h5py.h5 object containing RPW L0 packet data
    :param task: POPPy Task instance
    :return: TNR data array
    """
    # Extract source_data from the L0 file
    modes = tnr_decommutation(l0, task)

    # filter from None
    modes = [x for x in modes if x is not None]

    # check not empty
    if len(modes) == 0:
        return None

    return np.concatenate(modes)


def extract_hfr_data(l0, task):
    """
    Get the HFR data in a record array that can be easily exported into
    the CDF format.

    :param l0: h5py.h5 object containing RPW L0 packet data
    :param task: POPPy Task instance
    :return: HFR data array
    """
    # Extract source_data from the L0 file
    modes = hfr_decommutation(l0, task)

    # filter from None
    modes = [x for x in modes if x is not None]

    # check not empty
    if len(modes) == 0:
        return None

    return np.concatenate(modes)


def tnr_decommutation(l0, task):
    """
    Extract source_data from TNR SCIENCE TM packets.

    :param l0: h5py.h5 object containing RPW L0 packet data
    :param task: POPPy task
    :return: tuple of normal, burst and calibration TNR data
    """
    normal = None
    burst = None
    calibration = None

    # normal mode
    if "TM_THR_SCIENCE_NORMAL_TNR" in l0["TM"]:
        normal = tnr_normal_decom(
            l0["TM"]["TM_THR_SCIENCE_NORMAL_TNR"]["source_data"],
            task,
        )

    # burst mode
    if "TM_THR_SCIENCE_BURST_TNR" in l0["TM"]:
        burst = tnr_burst_decom(
            l0["TM"]["TM_THR_SCIENCE_BURST_TNR"]["source_data"],
            task,
        )

    # calibration mode
    if "TM_THR_SCIENCE_CALIBRATION_TNR" in l0["TM"]:
        calibration = tnr_calibration_decom(
            l0["TM"]["TM_THR_SCIENCE_CALIBRATION_TNR"]["source_data"],
            task,
        )

    return normal, burst, calibration


def hfr_decommutation(f, task):
    """
    Extract source_data from HFR SCIENCE TM packets.
    """
    normal = None
    burst = None
    calibration = None

    # normal mode
    packet_name = "TM_THR_SCIENCE_NORMAL_HFR"
    if packet_name in f["TM"]:
        # Define time range to query to retrieve hfr_time_log table data
        acq_time_max = f["TM"][packet_name]["source_data"]["PA_THR_ACQUISITION_TIME"][
            -1
        ][:2]
        end_time = Time.cuc_to_datetime(acq_time_max)[0] + timedelta(hours=24)
        start_time = end_time - timedelta(hours=72)
        # Define mode (0 == NORMAL)
        mode = 0
        # Query hfr_time_log table data
        delta_times = get_hfr_delta_times(mode, start_time, end_time)

        if len(delta_times) == 0:
            logger.warning(
                "No delta_times value found for NORMAL mode in the pipeline.hfr_time_log table!"
            )
        else:
            # Then get measurements in packets
            normal = hfr_normal_decom(
                f["TM"][packet_name]["source_data"],
                task,
                f["TM"][packet_name]["data_field_header"]["time"],
                delta_times,
                mode,
            )

    # burst mode
    packet_name = "TM_THR_SCIENCE_BURST_HFR"
    if packet_name in f["TM"]:
        # Define time range to query to retrieve hfr_time_log table data
        acq_time_max = f["TM"][packet_name]["source_data"]["PA_THR_ACQUISITION_TIME"][
            -1
        ][:2]
        end_time = Time.cuc_to_datetime(acq_time_max)[0] + timedelta(hours=24)
        start_time = end_time - timedelta(hours=72)
        # Define mode (1 == BURST)
        mode = 1
        # Query hfr_time_log table data
        delta_times = get_hfr_delta_times(mode, start_time, end_time)

        if len(delta_times) == 0:
            logger.warning(
                "No delta_times value found for BURST mode in the pipeline.hfr_time_log table!"
            )
        else:
            # Then get measurements in packets
            burst = hfr_burst_decom(
                f["TM"][packet_name]["source_data"],
                task,
                f["TM"][packet_name]["data_field_header"]["time"],
                delta_times,
                mode,
            )

    # calibration mode
    packet_name = "TM_THR_SCIENCE_CALIBRATION_HFR"
    if packet_name in f["TM"]:
        calibration = hfr_calibration_decom(
            f["TM"][packet_name]["source_data"],
            task,
        )

    return normal, burst, calibration


def extract_spectral_power_data(f, task):
    """
    Extract source_data from TM_THR_SCIENCE_SPECTRAL_POWER TM packets.
    """
    if "TM_THR_SCIENCE_SPECTRAL_POWER" in f["TM"]:
        return spectral_power_decom(
            f["TM"]["TM_THR_SCIENCE_SPECTRAL_POWER"]["source_data"],
            task,
        )
    return None
