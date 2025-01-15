import numpy as np
cimport numpy as np
from libcpp cimport bool as bool_t

from roc.rpl.time import Time
from roc.idb.converters.cdf_fill import fill_records as filler
from poppy.core.tools.exceptions import print_exception
from roc.rpl.packet_structure.data cimport Data
from roc.rpl.packet_structure.data import Data
from libc.stdint cimport uint64_t

from roc.rap.tasks.thr.hfr_time_log import found_delta_time
from roc.rap.tasks.thr.science_tools import rpw_status
from roc.rap.tasks.thr.science_tools import temperatures_command
from roc.rap.tasks.thr.science_tools import input_setup
from roc.rap.tasks.thr.science_tools import do_analysis
from roc.rap.tasks.thr.science_tools import rpw_status_dtype
from roc.rap.tasks.thr.science_tools import temperatures_dtype
from roc.rap.tasks.thr.science_tools import input_setup_dtype
from roc.rap.tasks.thr.science_tools import do_analysis_dtype
from roc.rap.tasks.thr.science_tools import average_nr
from roc.rap.tasks.thr.hfr import extract_band
from roc.rap.tasks.thr.hfr import hfr_setup
from roc.rap.tasks.thr.hfr import hfr_sweep_setup
from roc.rap.tasks.thr.hfr import delta_times
from roc.rap.tasks.thr.hfr import hfr_dtype
from roc.rap.tasks.thr.hfr import compute_frequency
from roc.rap.tasks.thr.hfr import compute_tempo
from roc.rap.tasks.thr.hfr import hfr_band_index
from roc.rap.tasks.thr.hfr_list import HfrListMode
from roc.rap.constants import THR_TICK_NSEC, UINT64_MAX_VALUE
from roc.rap.tools import to_logger

cpdef decommute_burst(group, task, packet_times, delta_times, mode):
    return decommute(group, task, packet_times, delta_times, mode)


cpdef decommute_normal(group, task, packet_times, delta_times, mode):
    return decommute(group, task, packet_times, delta_times, mode)


cdef decommute(group, task, packet_times, delta_times, mode):
    cdef:
        Py_ssize_t i
        Py_ssize_t j
        long number
        long packet_number
        unsigned long size
        unsigned long nblocks
        unsigned long offset

    # Initialize failed flag
    has_failed = False

    # select the mode
    if mode == 0:
        message = "normal"
        cnt_param = "PA_THR_N_BLOCK_CNT"
    else:
        message = "burst"
        cnt_param = "PA_THR_B_BLOCK_CNT"

    # get the size for the number of packets
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
            size = group["PA_THR_HFR_DATA_CNT"][i]

            # number of blocks
            nblocks = group[cnt_param][i]

            # Get delta times values for current packet
            try:
                delta_time1, delta_time2 = found_delta_time(
                    group, delta_times, packet_times, i, message)
            except:
                raised_message = print_exception()
                task.exception(raised_message)
                has_failed = True
                break

            # transform the data into byte array
            # store because of the garbage collector removing reference while
            # processing in cython
            byte = group[
                "PA_THR_HFR_DATA"
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
                    delta_time1[j],
                    delta_time2[j],
                )

                # increment counter
                counter += 1

            # check offset size
            if offset != size * 2:
                raise Exception(
                    "Bad decommutation for HFR " + message + " mode\n" +
                    "Expected {0} got {1} bytes".format(2 * size, offset)
                )
        except:
            # if problem with a packet, continue the process
            raised_message = print_exception()
            task.exception(raised_message)

    if not has_failed:
        # get the number of records
        number = band_record_number(array)

        # create an array of hfr records
        records = np.zeros(number, dtype=hfr_dtype())
        filler(records)

        # fill the array with the records
        records = fill_records(array, records, mode)
    else:
        raise Exception(f'Processing HFR {message} has failed')

    return records


cdef fill_records(array, records, mode):
    cdef:
        Py_ssize_t i
        long nblocks
        unsigned long counter

    # get number of blocks
    nblocks = array.shape[0]

    # init the counter for placing data
    counter = 0

    # loop over blocks of data
    for i in range(nblocks):
        if array["hfr_setup"]["hf1"][i] == 1:

            # Fill output records with packet parameters values
            counter = set_record(
                records,
                array,
                mode,
                counter,
                i,
                "hf1",
                "hf1_step",
                "hf1_size",
            )
        if array["hfr_setup"]["hf2"][i] == 1:

            # Fill output records with packet parameters values
            counter = set_record(
                records,
                array,
                mode,
                counter,
                i,
                "hf2",
                "hf2_step",
                "hf2_size",
            )

    return records

cdef unsigned long set_record(records, array, mode, counter, i, band,
                              step, size) except 1:
    cdef:
        long long epoch
        unsigned long long tempo
        unsigned long long measure
        unsigned long frequency
        unsigned long long delta_time_nsec
        double sample_time
        double scet
        Py_ssize_t j

    # CAVEATS: HFR acquisition time (PA_THR_ACQUISITION_TIME)
    # behaviour is not fully compliant.
    # Acquisition times are supposed to increase every new TM packet
    # which is not the case for HFR science packets.
    # It is hence tried to fill Epoch times with delta_times values stored in the
    # hfr_time_log table. But it is not possible when the delta_times values
    # exceed the maximal value permitted by the data type (2**16).
    # In this case, data samples cannot be correctly time stamped and are removed from output data
    # (see https://gitlab.obspm.fr/ROC/RCS/THR_CALBAR/-/issues/76 for more details).

    # Get delta time for the current band and block in nanoseconds
    if array["deltas"][band][i] == UINT64_MAX_VALUE - 1:
        to_logger(f'Bad delta time value found, skip this sample ({i})!',
                  level='debug')
        return counter
    delta_time_nsec = <unsigned long long > ((array["deltas"][band][i]) * THR_TICK_NSEC)

    # Compute scet time in seconds
    scet = (Time.cuc_to_scet(
        np.array([array["acquisition_time"][i][:2]])) +  # acquisition time
        float(delta_time_nsec / 1000000000.)  # delta time in seconds
    )

    # Compute epoch time for the first sample of the sweep / block
    epoch = <long long > (Time().obt_to_utc(
        np.array([array["acquisition_time"][i][:2]]), to_tt2000=True) +  # acquisition time
        delta_time_nsec  # delta time in nanoseconds
    )

    # Process HFR MODE list (if found)
    if array["hfr_setup"]["sw"][i] == 1:
        try:
            #logger.debug("Getting HFR LIST mode frequency values")

            frequency_list = HfrListMode().get_freq(Time().obt_to_utc(
                np.array([array["acquisition_time"][i][:2]]),
                to_datetime=True)[0], band, mode)
            if not frequency_list:
                raise ValueError(
                    'No frequency list has been returned from pipeline.tc_log table')
            n_freq = len(frequency_list)

        except Exception as e:
            to_logger('Cannot retrieve frequencies for HFR LIST mode',
                level='exception')
            raise
    else:
        n_freq = array["hfr_sweep"][step][i]

    # Loop over list of frequencies
    tempo = 0
    for j in range(n_freq):
        if array["hfr_setup"]["sw"][i] == 1:
            frequency = frequency_list[j]
        else:
            # Get frequency value
            frequency = compute_frequency(
                array["hfr_setup"]["initial_frequency"][i],
                j,
                array["hfr_sweep"]["hf1_size"][i],
                array["hfr_sweep"]["hf1_step"][i],
                array["hfr_sweep"]["hf2_size"][i],
                band,
            )

        # Save acquisition time of the first sample in the packet
        records["acquisition_time"][counter] = array["acquisition_time"][i][:2]

        # Get the duration of the measurement
        # for the given HFR frequency in milliseconds
        measure = compute_tempo(frequency)
        # Get sample time for the given frequency in milliseconds
        sample_time = 0.5 * measure + tempo

        # Compute Epoch time for the current sample in nanoseconds
        records["epoch"][counter] = epoch + sample_time * 1000000
        records["scet"][counter] = scet + float(sample_time)

        tempo += measure
        records["sweep_num"][counter] = i
        records["frequency"][counter] = frequency
        records["sample_time"][counter] = sample_time * \
            1000.  # in microseconds
        records["synchro_flag"][counter] = array[
            "acquisition_time"
        ][i][2]

        records["ticks_nr"][counter] = array["delta_times"][band][i]
        records["delta_time"][counter] = < double > (delta_time_nsec) / 1000.  # in microseconds

        records["survey_mode"][counter] = mode
        records["sweep_mode"][counter] = array["hfr_setup"]["sw"][i]
        records["average_nr"][counter] = average_nr(
            array["hfr_setup"]["av"][i])
        records["channel_status"][counter] = (
            array["do_analysis"]["ch1"][i],
            array["do_analysis"]["ch2"][i],
        )
        records["front_end"][counter] = array["input_setup"]["fe"][i]
        records["sensor_config"][counter] = (
            array["input_setup"]["sensor_tnr_1"][i],
            array["input_setup"]["sensor_tnr_2"][i],
        )
        records["rpw_status"][counter][:] = array["rpw_status"][i].tolist()
        records["temperature"][counter] = array["temperatures"][i].tolist()
        records["hfr_band"][counter] = hfr_band_index(band)
        records["agc1"][counter] = array["data"]["ch1"][band][i][j]
        records["agc2"][counter] = array["data"]["ch2"][band][i][j]
        counter += 1

    return counter


cdef unsigned long band_record_number(array):
    """
    Get the number of records for each band.
    """
    cdef:
        tuple nnormal
        unsigned long number = 0

    filter1 = array["hfr_setup"]["hf1"] == 1
    filter2 = array["hfr_setup"]["hf2"] == 1

    nnormal = (
        int(array["hfr_sweep"]["hf1_step"][filter1[:]].sum()),
        int(array["hfr_sweep"]["hf2_step"][filter2[:]].sum()),
    )
    number += sum(nnormal)

    return number


cpdef tuple extract_data(Data data,
                         Py_ssize_t offset,
                         np.ndarray time,
                         unsigned long long delta1,
                         unsigned long long delta2):
    cdef:
        unsigned short cmd_ctr
        unsigned short bit_count
        unsigned short n1, n2
        tuple rpw_status_cmd
        tuple temperatures
        tuple hfr_setup_cmd
        tuple input_setup_cmd
        tuple hfr_sweep_cmd
        tuple do_analysis_cmd
        tuple deltas
        tuple ch1, ch2

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
    hfr_setup_cmd = hfr_setup(data, offset)
    offset += 2

    # get the value for the sweep mode
    sw = hfr_setup_cmd[0]

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

    # read delta times
    # (NOT USED. REPLACED BY delta1, delta2 VALUES GIVEN IN INPUTS.
    # See https://gitlab.obspm.fr/ROC/RCS/THR_CALBAR/-/issues/76 for details)
    deltas = delta_times(data, offset)
    offset += 8

    # initialize bit count
    bit_count = 0

    # extract bands
    ch1, bit_count = extract_band(
        do_analysis_cmd[4],
        hfr_setup_cmd[3],
        hfr_setup_cmd[2],
        n1,
        n2,
        data,
        offset,
        bit_count,
    )
    ch2, bit_count = extract_band(
        do_analysis_cmd[3],
        hfr_setup_cmd[3],
        hfr_setup_cmd[2],
        n1,
        n2,
        data,
        offset,
        bit_count,
    )

    # compute the new offset for the block
    offset += bit_count // 8

    # align
    if offset % 2 != 0:
        offset += 1

    # tuple of values to add them to the numpy array
    return (
        cmd_ctr, rpw_status_cmd, temperatures, hfr_setup_cmd,
        input_setup_cmd, hfr_sweep_cmd, do_analysis_cmd, deltas,
        (ch1, ch2), time, (delta1, delta2)
    ), offset


cpdef list create_dtype():
    """
    Create dtype of numpy for the special packet.
    """
    return [
        ("cmd_ctr", "uint8"),
        ("rpw_status", rpw_status_dtype()),
        ("temperatures", temperatures_dtype()),
        ("hfr_setup", setup_dtype()),
        ("input_setup", input_setup_dtype()),
        ("hfr_sweep", hfr_sweep_setup_dtype()),
        ("do_analysis", do_analysis_dtype()),
        ("delta_times", delta_times_dtype()),
        ("data", block_data_dtype()),
        ("acquisition_time", "uint32", 3),
        ("deltas", deltas_dtype())
    ]


cpdef list channel_dtype():
    return [
        ("hf1", "uint16", 512), ("hf2", "uint16", 512)
    ]


cpdef list block_data_dtype():
    return [
        ("ch1", channel_dtype()), ("ch2", channel_dtype()),
    ]


cpdef list delta_times_dtype():
    return [
        ("hf1", "int64"), ("hf2", "int64"),
    ]

cpdef list deltas_dtype():
    return [
        ("hf1", "uint64"), ("hf2", "uint64"),
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
