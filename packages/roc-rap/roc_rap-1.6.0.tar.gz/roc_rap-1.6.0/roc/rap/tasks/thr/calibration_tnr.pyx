import numpy as np
cimport numpy as np

from libc.stdint cimport uint64_t

from poppy.core.tools.exceptions import print_exception

from roc.rpl.time import Time
from roc.rpl.packet_structure.data cimport Data
from roc.rpl.packet_structure.data import Data

from roc.idb.converters.cdf_fill import fill_records as set_fillval

from roc.rap.tasks.thr.science_tools import input_setup
from roc.rap.tasks.thr.science_tools import voltages
from roc.rap.tasks.thr.science_tools import do_analysis
from roc.rap.tasks.thr.science_tools import voltages_dtype
from roc.rap.tasks.thr.science_tools import input_setup_dtype
from roc.rap.tasks.thr.science_tools import do_analysis_dtype
from roc.rap.tasks.thr.tnr import extract_calibration_band as extract_band
from roc.rap.tasks.thr.tnr import tnr_setup
from roc.rap.tasks.thr.tnr import tnr_dtype


class TNRCalibrationDecomError(Exception):
    """
    Error management for TNR calibration.
    """


cpdef decommute(group, task):
    cdef:
        Py_ssize_t i

    # get the size for the number of packets
    number = group["PA_THR_TNR_DATA_CNT"].shape[0]

    # create the array containing the data
    array = np.zeros(number, dtype=create_dtype())

    # loop over packets
    for i in range(number):
        try:
            # size for number of unsigned int
            size = group["PA_THR_TNR_DATA_CNT"][i]

            # transform the data into byte array
            # store because of the garbage collector removing reference while
            # processing in cython
            byte = group[
                "PA_THR_TNR_DATA"
            ][i][:size].byteswap().newbyteorder().tobytes()
            data = Data(byte, len(byte))

            # now extract the data
            result, offset = extract_data(
                data,
                0,
                group["PA_THR_ACQUISITION_TIME"][i],
            )

            # check offset
            if offset != size * 2:
                raise TNRCalibrationDecomError(
                    "Expected a size of {0} bytes but have {1}".format(
                        size * 2,
                        offset,
                    )
                )

            # store the data
            array[i] = result
        except:
            # do nothing with this packet and store the error in the database
            message = print_exception()
            task.exception(message)

    # get the number of records
    number, bands = band_record_number(array)

    # create an array of tnr records
    records = np.empty(number, dtype=tnr_dtype())
    set_fillval(records)

    # fill the array with the records
    records = fill_records(array, records)

    return records


cdef fill_records(array, records):
    cdef:
        Py_ssize_t i
        unsigned long nblocks
        unsigned long counter

    # get number of blocks
    nblocks = array.shape[0]

    # init the counter for placing data
    counter = 0

    # loop over fields
    for i in range(nblocks):
        if array["tnr_setup"]["a"][i] == 1:
            counter = set_record(records, array, counter, i, "a", 0)
        if array["tnr_setup"]["b"][i] == 1:
            counter = set_record(records, array, counter, i, "b", 1)
        if array["tnr_setup"]["c"][i] == 1:
            counter = set_record(records, array, counter, i, "c", 2)
        if array["tnr_setup"]["d"][i] == 1:
            counter = set_record(records, array, counter, i, "d", 3)

    return records


cdef unsigned long set_record(records, array, counter, i, band, index):
    cdef:
        double epoch
        Py_ssize_t j
        str level

    epoch = <double>Time().obt_to_utc(
                np.array([array["acquisition_time"][i][:2]]),
        to_tt2000=True)

    for j in range(9):
        level = str(j)
        records["epoch"][counter] = epoch
        records["acquisition_time"][counter] = array["acquisition_time"][i][:2]
        records["scet"][counter] = Time.cuc_to_scet(
            np.array([array["acquisition_time"][i][:2]]))
        records["synchro_flag"][counter] = array[
            "acquisition_time"
        ][i][2]
        records["survey_mode"][counter] = 2
        records["average_nr"][counter] = array["tnr_setup"]["av"][i]
        records["auto_cross_status"][counter] = (
            array["tnr_setup"]["au"][i],
            array["tnr_setup"]["cr"][i],
        )
        records["channel_status"][counter] = (
            array["do_analysis"]["ch1"][i],
            array["do_analysis"]["ch2"][i],
        )
        records["calibration_level"][counter] = j
        records["front_end"][counter] = array["input_setup"]["fe"][i]
        records["sensor_config"][counter] = (
            array["input_setup"]["sensor_tnr_1"][i],
            array["input_setup"]["sensor_tnr_2"][i],
        )

        # in calibration mode, no temperatures array, but just PCB temperture
        # and voltages
        records["temperature"][counter] = (
            array["temperature_pcb"][i],
            array["voltages"]["minus5"][i],
            array["voltages"]["plus5"][i],
            array["voltages"]["plus12"][i],
        )
        records["tnr_band"][counter] = index
        records["agc1"][counter] = array["data"][level][band]["ch1"]["agc"][i]
        records["agc2"][counter] = array["data"][level][band]["ch2"]["agc"][i]
        records["auto1"][counter][:8] = array["data"][
            level
        ][band]["ch1"]["autos"][i]
        records["auto2"][counter][:8] = array["data"][
            level
        ][band]["ch2"]["autos"][i]
        records["cross_r"][counter][:8] = array["data"][
            level
        ][band]["cross"][i][:, 0]
        records["cross_i"][counter][:8] = array["data"][
            level
        ][band]["cross"][i][:, 1]
        counter += 1

    return counter

cdef tuple band_record_number(array):
    """
    Get the number of records for each band.
    """
    cdef:
        tuple nnormal
        unsigned long number = 0

    nnormal = (
        int(array["tnr_setup"]["a"].sum()) * 9,
        int(array["tnr_setup"]["b"].sum()) * 9,
        int(array["tnr_setup"]["c"].sum()) * 9,
        int(array["tnr_setup"]["d"].sum()) * 9,
    )
    number += sum(nnormal)

    return number, nnormal



cdef tuple extract_data(Data data, Py_ssize_t offset, time):
    """
    Extract the data and insert it into the data structure of the packet.
    """
    cdef:
        unsigned short cmd_ctr
        unsigned short bit_count
        tuple voltages_cmd
        tuple tnr_setup_cmd
        tuple input_setup_cmd
        tuple do_analysis_cmd
        tuple res
        list banda, bandb, bandc, bandd
        Py_ssize_t i

    # read command control
    cmd_ctr = data.u8(offset, 0, 8)
    offset += 1

    # read temperatures
    voltages_cmd = voltages(data, offset)
    offset += 3

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

    # initialize bit count
    bit_count = 0

    # init structure for calibration levels
    banda, bandb, bandc, bandd = [], [], [], []

    # loop over the calibration levels
    for i in range(9):
        # extract bands
        res, bit_count = extract_band(
            tnr_setup_cmd[6],
            do_analysis_cmd[4],
            do_analysis_cmd[3],
            tnr_setup_cmd[2],
            tnr_setup_cmd[1],
            data,
            offset,
            bit_count,
        )
        banda.append(res)
        res, bit_count = extract_band(
            tnr_setup_cmd[5],
            do_analysis_cmd[4],
            do_analysis_cmd[3],
            tnr_setup_cmd[2],
            tnr_setup_cmd[1],
            data,
            offset,
            bit_count,
        )
        bandb.append(res)
        res, bit_count = extract_band(
            tnr_setup_cmd[4],
            do_analysis_cmd[4],
            do_analysis_cmd[3],
            tnr_setup_cmd[2],
            tnr_setup_cmd[1],
            data,
            offset,
            bit_count,
        )
        bandc.append(res)
        res, bit_count = extract_band(
            tnr_setup_cmd[3],
            do_analysis_cmd[4],
            do_analysis_cmd[3],
            tnr_setup_cmd[2],
            tnr_setup_cmd[1],
            data,
            offset,
            bit_count,
        )
        bandd.append(res)

    # compute the new offset for the block
    offset += bit_count // 8

    # align
    if offset % 2 != 0:
        offset += 1

    # tuple of values to add them to the numpy array
    return (
        cmd_ctr, voltages_cmd, tnr_setup_cmd,
        input_setup_cmd, do_analysis_cmd,
        tuple([(banda[i], bandb[i], bandc[i], bandd[i]) for i in range(9)]),
        time
    ), offset


cpdef list create_dtype():
    """
    Create dtype of numpy for the special packet.
    """
    return [
        ("temperature_pcb", "uint8"),
        ("voltages", voltages_dtype()),
        ("tnr_setup", tnr_setup_dtype()),
        ("input_setup", input_setup_dtype()),
        ("do_analysis", do_analysis_dtype()),
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


cpdef list channel_dtype():
    return [
        ("agc", "uint16"), ("autos", "uint16", 8),
    ]


cpdef list band_dtype():
    return [
        ("ch1", channel_dtype()),
        ("ch2", channel_dtype()),
        ("cross", "uint16", (8, 2)),
    ]


cpdef list block_data_dtype():
    return [
        (
            "{0}".format(i),
            [
                ("a", band_dtype()),
                ("b", band_dtype()),
                ("c", band_dtype()),
                ("d", band_dtype())
            ],
        ) for i in range(9)
    ]
