#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
cimport numpy as np

from roc.rpl.time import Time
from roc.idb.converters.cdf_fill import fill_records as filler
from poppy.core.tools.exceptions import print_exception
from roc.rpl.packet_structure.data import Data
from roc.rpl.packet_structure.data cimport Data
from libc.stdint cimport uint64_t
from roc.rap.tasks.thr.science_tools import rpw_status
from roc.rap.tasks.thr.science_tools import temperatures_command
from roc.rap.tasks.thr.science_tools import input_setup
from roc.rap.tasks.thr.science_tools import do_analysis
from roc.rap.tasks.thr.science_tools import rpw_status_dtype
from roc.rap.tasks.thr.science_tools import temperatures_dtype
from roc.rap.tasks.thr.science_tools import input_setup_dtype
from roc.rap.tasks.thr.science_tools import do_analysis_dtype
from roc.rap.tasks.thr.science_tools import average_nr
from roc.rap.tasks.thr.tnr import delta_times
from roc.rap.tasks.thr.tnr import extract_band
from roc.rap.tasks.thr.tnr import tnr_setup
from roc.rap.tasks.thr.tnr import tnr_dtype
from roc.rap.tasks.thr.tnr import DURATION

# Max encoding value for uint32
UINT32_MAX_ENCODING = 2**32

# THR Tick value in nanosec
THR_TICK_NSEC = 15258

# List of TNR frequency values in Hz
TNR_FREQUENCY_LIST = 3991.785737 * np.power(4, 1./32)**np.arange(0, 128)

# List of TNR frequency for each band (0=A, 1=B, 2=C and 3=D)
# List is given as a dictionary with band index as keyword
TNR_BAND_FREQUENCY = {
             0:TNR_FREQUENCY_LIST[0:32],
             1:TNR_FREQUENCY_LIST[32:64],
             2:TNR_FREQUENCY_LIST[64:96],
             3:TNR_FREQUENCY_LIST[96:128],
            }


cpdef decommute_burst(group, task):
    return decommute(group, task, "PA_THR_B_BLOCK_CNT", "burst")


cpdef decommute_normal(group, task):
    return decommute(group, task, "PA_THR_N_BLOCK_CNT", "normal")


cdef decommute(group, task, cnt_param, message):
    cdef:
        Py_ssize_t i
        Py_ssize_t j
        Py_ssize_t counter
        unsigned long size
        unsigned long nblocks
        unsigned long offset

    # get the size for the number of blocks
    number = np.sum(group[cnt_param])

    # create the array containing the data
    array = np.zeros(number, dtype=create_dtype())

    # the number of packets
    packet_number = group[cnt_param].shape[0]

    # loop over packets
    counter = 0
    for i in range(packet_number):
        try:
            # size of the number of unsigned int
            size = group["PA_THR_TNR_DATA_CNT"][i]

            # number of blocks
            nblocks = group[cnt_param][i]

            # transform the data into byte array
            # store because of the garbage collector removing reference while
            # processing in Cython
            byte = group[
                "PA_THR_TNR_DATA"
            ][i][:size].byteswap().newbyteorder().tobytes()
            data = Data(byte, len(byte))

            # init offset
            offset = 0

            # loop over blocks
            for j in range(nblocks):
                # now extract the data
                array[counter], offset = extract_data(
                    data,
                    offset,
                    group["PA_THR_ACQUISITION_TIME"][i],
                )

                # increment counter
                counter += 1

            # check offset size
            if offset != size * 2:
                raise Exception(
                    "Bad decommutation for TNR " + message + " mode\n" +
                    "Expected {0} got {1} bytes".format(size * 2, offset)
                )
        except:
            # continue if something wrong with the packet
            message = print_exception()
            task.exception(message)

    # get the number of records
    number, bands = band_record_number(array)

    # create an array of tnr records
    records = np.zeros(number, dtype=tnr_dtype())
    filler(records)

    # fill the array with the records
    records = fill_records(array, records, message)

    return records


cdef fill_records(array, records, message):
    cdef:
        Py_ssize_t i
        long nblocks
        unsigned long counter
        np.ndarray[np.uint64_t, ndim=1] delta_offset

    # get number of blocks
    nblocks = array.shape[0]

    # select the mode
    if message == "normal":
        mode = 0
    else:
        mode = 1

    # init the counter for placing data
    counter = 0

    # Init delta time offset for band A, B, C and D
    # (Required of delta times exceed max 32 bits encoding value in packet)
    delta_offset = np.zeros(4, dtype=np.uint64)

    # loop over fields
    for i in range(nblocks):
        if array["tnr_setup"]["a"][i] == 1:
            delta_offset = set_record(records, array, mode,
                                      counter, i, "a", 0,
                                      delta_offset)
            counter += 1
        if array["tnr_setup"]["b"][i] == 1:
            delta_offset = set_record(records, array, mode,
                                      counter, i, "b", 1,
                                      delta_offset)
            counter += 1
        if array["tnr_setup"]["c"][i] == 1:
            delta_offset = set_record(records, array, mode,
                                      counter, i, "c", 2,
                                      delta_offset)
            counter += 1
        if array["tnr_setup"]["d"][i] == 1:
            delta_offset = set_record(records, array, mode,
                                      counter, i, "d", 3,
                                      delta_offset)
            counter += 1

    return records


cdef np.ndarray set_record(
    records,
    array,
    unsigned char mode,
    unsigned long counter,
    Py_ssize_t i,
    str band,
    unsigned char index,
    np.ndarray delta_offset
):
    cdef:
        long delta_time
        float measurement_duration

    #  # Check if UINT32_MAX_ENCODING is reached
    # TODO - This part does not work because of the
    #        issue https://gitlab.obspm.fr/ROC/RCS/THR_CALBAR/-/issues/45
    # is_true = (i > 0 and
    #         Time.cuc_to_scet(
    #         np.array(array["acquisition_time"][i-1][:2])) == Time.cuc_to_scet(
    #         np.array(array["acquisition_time"][i][:2])) and
    #         array["delta_times"][band][i-1] > array["delta_times"][band][i])
    #
    # if is_true:
    #     delta_offset[index] += UINT32_MAX_ENCODING

    delta_time = ((array["delta_times"][band][i] +
                  delta_offset[index]) * THR_TICK_NSEC) # in nanosec
    measurement_duration = DURATION[
        (array["tnr_setup"]["av"][i], index)
    ] * 100.0

    records["epoch"][counter] = (<long>Time().obt_to_utc(
        np.array([array["acquisition_time"][i][:2]]), to_tt2000=True) + # acquisition time
        delta_time + # delta time in nanoseconds
        0.5 * measurement_duration * 10000000.0) # Take the middle of the measurement duration

    records["scet"][counter] = (Time.cuc_to_scet(
        np.array([array["acquisition_time"][i][:2]])) + # acquisition time
        float(delta_time / 1000000000.) + # delta time in seconds
        float(0.5 * measurement_duration) # duration measure
    )
    records["sweep_num"][counter] = i
    records["acquisition_time"][counter] = array["acquisition_time"][i][:2]
    records["synchro_flag"][counter] = array[
        "acquisition_time"
    ][i][2]
    records["measurement_duration"][counter] = measurement_duration * 10000.
    records["ticks_nr"][counter] = array["delta_times"][band][i]

    records["delta_time"][counter] = delta_time / 1000. # in microseconds
    records["survey_mode"][counter] = mode
    records["average_nr"][counter] = average_nr(array["tnr_setup"]["av"][i])
    records["auto_cross_status"][counter] = (
        array["tnr_setup"]["au"][i],
        array["tnr_setup"]["cr"][i],
    )
    records["channel_status"][counter] = (
        array["do_analysis"]["ch1"][i],
        array["do_analysis"]["ch2"][i],
    )
    records["front_end"][counter] = array["input_setup"]["fe"][i]
    records["sensor_config"][counter] = (
        array["input_setup"]["sensor_tnr_1"][i],
        array["input_setup"]["sensor_tnr_2"][i],
    )
    records["rpw_status"][counter] = array["rpw_status"][i].tolist()
    records["temperature"][counter] = array["temperatures"][i].tolist()
    records["tnr_band"][counter] = index
    records["frequency"][counter] = TNR_BAND_FREQUENCY[index]
    records["agc1"][counter] = array["data"][band]["ch1"]["agc"][i]
    records["agc2"][counter] = array["data"][band]["ch2"]["agc"][i]
    records["auto1"][counter] = array["data"][band]["ch1"]["autos"][i]
    records["auto2"][counter] = array["data"][band]["ch2"]["autos"][i]
    records["cross_r"][counter] = array["data"][band]["cross"][i][:, 0]
    records["cross_i"][counter] = array["data"][band]["cross"][i][:, 1]

    return delta_offset

cdef tuple band_record_number(array):
    """
    Get the number of records for each band.
    """
    cdef:
        tuple nnormal
        unsigned long number = 0

    nnormal = (
        int(array["tnr_setup"]["a"].sum()),
        int(array["tnr_setup"]["b"].sum()),
        int(array["tnr_setup"]["c"].sum()),
        int(array["tnr_setup"]["d"].sum()),
    )
    number += sum(nnormal)

    return number, nnormal


cdef tuple extract_data(Data data, Py_ssize_t offset, time):
    """
    Extract the data and insert it into the data structure of the packet.
    """
    cdef:
        Py_ssize_t i
        unsigned short bit_count
        unsigned short cmd_ctr
        tuple rpw_status_cmd
        tuple temperatures
        tuple tnr_setup_cmd
        tuple input_setup_cmd
        tuple do_analysis_cmd
        tuple deltas
        tuple banda, bandb, bandc, bandd

    # read command control
    cmd_ctr = data.u16(offset, 0, 16)
    offset += 2

    # read rpw status
    rpw_status_cmd = rpw_status(data, offset)
    offset += 2

    # read temperatures
    temperatures = temperatures_command(data, offset)
    offset += 4

    # read tnr setup
    offset += 1
    tnr_setup_cmd = tnr_setup(data, offset)
    offset += 1


    # read input setup
    input_setup_cmd = input_setup(data, offset)
    offset += 2

    # read do analysis command
    offset += 1
    do_analysis_cmd = do_analysis(data, offset)
    offset += 1

    # read delta times
    deltas = delta_times(data, offset)
    offset += 16

    # initialize bit count
    bit_count = 0

    # extract bands
    banda, bit_count = extract_band(
        tnr_setup_cmd[6],
        do_analysis_cmd[4],
        do_analysis_cmd[3],
        tnr_setup_cmd[2],
        tnr_setup_cmd[1],
        data,
        offset,
        bit_count,
    )
    bandb, bit_count = extract_band(
        tnr_setup_cmd[5],
        do_analysis_cmd[4],
        do_analysis_cmd[3],
        tnr_setup_cmd[2],
        tnr_setup_cmd[1],
        data,
        offset,
        bit_count,
    )
    bandc, bit_count = extract_band(
        tnr_setup_cmd[4],
        do_analysis_cmd[4],
        do_analysis_cmd[3],
        tnr_setup_cmd[2],
        tnr_setup_cmd[1],
        data,
        offset,
        bit_count,
    )
    bandd, bit_count = extract_band(
        tnr_setup_cmd[3],
        do_analysis_cmd[4],
        do_analysis_cmd[3],
        tnr_setup_cmd[2],
        tnr_setup_cmd[1],
        data,
        offset,
        bit_count,
    )
    # compute the new offset for the block
    offset += bit_count // 8

    # align the address
    # I do not understand why this is a 32 bits alignment in the
    # documentation, surely I misunderstand something... but working !
    if offset % 2 != 0:
        offset += 1

    # tuple of values to add them to the numpy array
    return (
        cmd_ctr, rpw_status_cmd, temperatures, tnr_setup_cmd,
        input_setup_cmd, do_analysis_cmd, deltas,
        (banda, bandb, bandc, bandd), time
    ), offset


cpdef list create_dtype():
    """
    Create dtype of numpy for the special packet.
    """
    return [
        ("cmd_ctr", "uint8"),
        ("rpw_status", rpw_status_dtype()),
        ("temperatures", temperatures_dtype()),
        ("tnr_setup", tnr_setup_dtype()),
        ("input_setup", input_setup_dtype()),
        ("do_analysis", do_analysis_dtype()),
        ("delta_times", delta_times_dtype()),
        ("data", block_data_dtype()),
        ("acquisition_time", "uint32", 3),
    ]


cpdef list tnr_setup_dtype():
    """
    Return the TNR setup command dtype.
    """
    return [
        ("av", "uint8"), ("cr", "uint8"), ("au", "uint8"),
        ("d", "uint8"), ("c", "uint8"), ("b", "uint8"), ("a", "uint8"),
    ]


cpdef list delta_times_dtype():
    return [
        ("a", "uint32"), ("b", "uint32"), ("c", "uint32"), ("d", "uint32"),
    ]


cpdef list channel_dtype():
    return [
        ("agc", "uint16"), ("autos", "uint16", 32),
    ]


cpdef list band_dtype():
    return [
        ("ch1", channel_dtype()),
        ("ch2", channel_dtype()),
        ("cross", "uint16", (32, 2)),
    ]


cpdef list block_data_dtype():
    return [
        ("a", band_dtype()), ("b", band_dtype()),
        ("c", band_dtype()), ("d", band_dtype()),
    ]
