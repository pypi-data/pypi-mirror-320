import numpy as np

from poppy.core.tools.exceptions import print_exception

from roc.rpl.time import Time
from roc.rpl.packet_structure.data cimport Data
from roc.rpl.packet_structure.data import Data

from roc.idb.converters.cdf_fill import fill_records as set_fillval

from roc.rap.tasks.thr.science_tools import voltages
from roc.rap.tasks.thr.science_tools import input_setup
from roc.rap.tasks.thr.science_tools import do_analysis
from roc.rap.tasks.thr.science_tools import voltages_dtype
from roc.rap.tasks.thr.science_tools import input_setup_dtype
from roc.rap.tasks.thr.science_tools import do_analysis_dtype
from roc.rap.tasks.thr.hfr import extract_band
from roc.rap.tasks.thr.hfr import hfr_setup
from roc.rap.tasks.thr.hfr import hfr_dtype
from roc.rap.tasks.thr.hfr import hfr_sweep_setup
from roc.rap.tasks.thr.hfr import compute_frequency


class HFRCalibrationDecomError(Exception):
    """
    Error management for HFR calibration.
    """


cpdef decommute(group, task):
    cdef:
        Py_ssize_t i

    # get the size for the number of packets
    number = group["PA_THR_HFR_DATA_CNT"].shape[0]

    # create the array containing the data
    array = np.zeros(number, dtype=create_dtype())

    # loop over packets
    for i in range(number):
        try:
            # size for number of unsigned int
            size = group["PA_THR_HFR_DATA_CNT"][i]

            # transform the data into byte array
            # store because of the garbage collector removing reference while
            # processing in cython
            byte = group[
                "PA_THR_HFR_DATA"
            ][i][:size].byteswap().newbyteorder().tobytes()
            data = Data(byte, len(byte))

            # now extract the data
            result, offset = extract_data(
                data,
                0,
                group["PA_THR_ACQUISITION_TIME"][i],
            )

            # check offset size
            if offset != size * 2:
                raise HFRCalibrationDecomError(
                    "Expected a size of {0} bytes but have {1}".format(
                        size * 2,
                        offset,
                    )
                )

            # store the data
            array[i] = result
        except:
            message = print_exception()
            task.exception(message)

    # get the number of records
    number = band_record_number(array)

    # create an array of tnr records
    records = np.empty(number, dtype=hfr_dtype())
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
        if array["hfr_setup"]["hf1"][i] == 1:
            counter = set_record(
                records,
                array,
                counter,
                i,
                "hf1",
                0,
                "hf1_step",
                "hf1_size",
            )
        if array["hfr_setup"]["hf2"][i] == 1:
            counter = set_record(
                records,
                array,
                counter,
                i,
                "hf2",
                1,
                "hf2_step",
                "hf2_size",
            )

    return records


cdef set_record(records, array, counter, i, band, index, step, size):
    cdef:
        double epoch
        unsigned long frequency
        unsigned char level
        double delta_time = 0
        Py_ssize_t j

    # TT2000 Epoch times
    epoch = <double>Time().obt_to_utc(
        np.array([array["acquisition_time"][i][:2]]), to_tt2000=True)

    for level in range(9):
        for j in range(array["hfr_sweep"][step][i]):
            records["epoch"][counter] = epoch
            records["acquisition_time"][counter] = array["acquisition_time"][i][:2]
            records["scet"][counter] = Time.cuc_to_scet(
            np.array([array["acquisition_time"][i][:2]]))
            records["synchro_flag"][counter] = array[
                "acquisition_time"
            ][i][2]
            frequency = compute_frequency(
                array["hfr_setup"]["initial_frequency"][i],
                j,
                array["hfr_sweep"]["hf1_size"][i],
                array["hfr_sweep"]["hf1_step"][i],
                array["hfr_sweep"]["hf2_size"][i],
                band,
            )
            records["frequency"][counter] = frequency
            records["calibration_level"][counter] = level
            records["survey_mode"][counter] = 2
            records["average_nr"][counter] = array["hfr_setup"]["av"][i]
            records["channel_status"][counter] = (
                array["do_analysis"]["ch1"][i],
                array["do_analysis"]["ch2"][i],
            )
            records["front_end"][counter] = array["input_setup"]["fe"][i]
            records["sensor_config"][counter] = (
                array["input_setup"]["sensor_tnr_1"][i],
                array["input_setup"]["sensor_tnr_2"][i],
             )

            records["temperature"][counter] = (
                array["temperature_pcb"][i],
                array["voltages"]["minus5"][i],
                array["voltages"]["plus5"][i],
                array["voltages"]["plus12"][i],
            )
            records["hfr_band"][counter] = index
            records["agc1"][counter] = array["data"][
                str(level)
            ]["ch1"][band][i][j]
            records["agc2"][counter] = array["data"][
                str(level)
            ]["ch2"][band][i][j]
            counter += 1

    return counter


cpdef unsigned long band_record_number(array):
    """
    Get the number of records for each band.
    """
    cdef:
        tuple nnormal
        unsigned long number = 0
    filter1 = array["hfr_setup"]["hf1"] == 1
    filter2 = array["hfr_setup"]["hf2"] == 1

    nnormal = (
        int(array["hfr_sweep"]["hf1_step"][filter1[:]].sum() * 9),
        int(array["hfr_sweep"]["hf2_step"][filter2[:]].sum() * 9),
    )
    number += sum(nnormal)

    return number



cdef tuple extract_data(Data data, Py_ssize_t offset, time):
    """
    Extract the data and insert it into the data structure of the packet.
    """
    cdef:
        unsigned short cmd_ctr
        unsigned short n1, n2
        unsigned int bit_count
        tuple voltages_cmd
        tuple hfr_setup_cmd
        tuple input_setup_cmd
        tuple hfr_sweep_cmd
        tuple do_analysis_cmd
        tuple res
        list ch1, ch2
        Py_ssize_t i

    # read command control
    cmd_ctr = data.u8(offset, 0, 8)
    offset += 1

    # read voltages
    voltages_cmd = voltages(data, offset)
    offset += 3

    # read tnr setup
    hfr_setup_cmd = hfr_setup(data, offset)
    offset += 2

    # read input setup
    input_setup_cmd = input_setup(data, offset)
    offset += 2

    # read hfr sweep setup
    hfr_sweep_cmd = hfr_sweep_setup(data, offset)
    n1 = hfr_sweep_cmd[2]
    n2 = hfr_sweep_cmd[0]
    offset += 4

    # read do analysis command
    offset += 1
    do_analysis_cmd = do_analysis(data, offset)
    offset += 1

    # initialize bit count
    bit_count = 0

    # init containers for values of the calibration
    ch1, ch2 = [], []

    # loop over calibration levels
    for i in range(9):
        # extract bands
        res, bit_count = extract_band(
            do_analysis_cmd[4],
            hfr_setup_cmd[3],
            hfr_setup_cmd[2],
            n1,
            n2,
            data,
            offset,
            bit_count,
        )
        ch1.append(res)
        res, bit_count = extract_band(
            do_analysis_cmd[3],
            hfr_setup_cmd[3],
            hfr_setup_cmd[2],
            n1,
            n2,
            data,
            offset,
            bit_count,
        )
        ch2.append(res)

    # compute the new offset for the block
    offset += bit_count // 8

    # align
    if offset % 2 != 0:
        offset += 1

    # tuple of values to add them to the numpy array
    return (
        cmd_ctr, voltages_cmd, hfr_setup_cmd,
        input_setup_cmd, hfr_sweep_cmd, do_analysis_cmd,
        tuple([(ch1[i], ch2[i]) for i in range(9)]), time
    ), offset


cpdef list create_dtype():
    """
    Create dtype of numpy for the special packet.
    """
    return [
        ("temperature_pcb", "uint8"),
        ("voltages", voltages_dtype()),
        ("hfr_setup", setup_dtype()),
        ("input_setup", input_setup_dtype()),
        ("hfr_sweep", hfr_sweep_setup_dtype()),
        ("do_analysis", do_analysis_dtype()),
        ("data", block_data_dtype()),
        ("acquisition_time", "uint32", 3),
    ]


cpdef list channel_dtype():
    return [
        ("hf1", "uint16", 512), ("hf2", "uint16", 512)
    ]


cpdef list block_data_dtype():
    return [
        (
            "{0}".format(i),
            [
                ("ch1", channel_dtype()),
                ("ch2", channel_dtype())
            ],
        ) for i in range(9)
    ]


cpdef list hfr_sweep_setup_dtype():
    return [
        ("hf2_step", "uint16"), ("hf2_size", "uint8"),
        ("hf1_step", "uint16"), ("hf1_size", "uint8"),
    ]


cpdef list setup_dtype():
    return [
        ("sw", "uint8"), ("initial_frequency", "uint16"),
        ("hf2", "uint8"), ("hf1", "uint8"), ("av", "uint8")
    ]
