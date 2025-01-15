import numpy as np
cimport numpy as np

from poppy.core.logger import logger

from roc.rpl.time import Time
from roc.idb.converters.cdf_fill import fill_records
from libc.stdint cimport uint8_t
from libc.stdint cimport uint16_t
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

from roc.rap.tasks.utils import sort_data

__all__ = ["CWF", "set_cwf"]

# Numpy array dtype for TDS LFM CWF L1 survey data
# Name convention is lower case

CWF = [
    ("epoch", "uint64"),
    ("scet", "float64"),
    ("acquisition_time", ("uint32", 2)),
    ("synchro_flag", "uint8"),
    ("quality_flag", "uint8"),
    ("quality_bitmask", "uint16"),
    ("survey_mode", "uint8"),
    ("bia_status_info", ("uint8", 6)),
    ("sampling_rate", "float32"),
    ("cwf_data_artefacts", ("uint8", 8)),
    ("input_config", ("uint8", 8)),
    ("channel_status_info", ("uint8", 8)),
    ("waveform_data", ("int16", 8)),
]

cpdef set_cwf(l0, task):
    cdef:
        Py_ssize_t packet
        Py_ssize_t size
        Py_ssize_t sample
        Py_ssize_t index
        np.ndarray data
        tuple acquisition_time
        uint8_t synchro_flag
        tuple channel_status
        tuple artefacts
        tuple bias_status
        tuple input_config
        float sampling_rate
        uint16_t snapshot_nr
        uint16_t samp_per_ch
        uint16_t current_snapshot
        uint32_t current_sample
        uint8_t filter_coefs
        uint8_t counter_ch
        uint8_t channel
        uint64_t samp_step
        uint64_t epoch

    # name of the packet
    name = "TM_TDS_SCIENCE_LFM_CWF"
    logger.debug("Get data for " + name)

    # get the LFM CWF packet data
    if name in l0["TM"]:
        tm = l0["TM"][name]["source_data"]
    else:
        # rest of the code inside the with statement will not be called
        return np.empty(
            0,
            dtype=CWF,
        )

    # Sort input packets by ascending acquisition times
    tm, __ = sort_data(tm, (
        tm["PA_TDS_ACQUISITION_TIME"][:,1],
        tm["PA_TDS_ACQUISITION_TIME"][:,0],
                    ))

    # suppose for now that we have the good size for the data
    size = np.sum(tm["PA_TDS_LFR_CWF_SAMPS_PER_CH"])
    logger.debug("Number of samples: {0}".format(size))

    # create the data array with good size
    data = np.zeros(size, dtype=CWF)
    fill_records(data)

    # get the number of packets
    size = tm["PA_TDS_ACQUISITION_TIME"].shape[0]
    logger.debug("Number of packets: {0}".format(size))

    # initiate the group number and the sample number
    current_snapshot = 0
    current_sample = 0

    # initialize the position in the data array
    index = 0

    # survey mode to normal
    data["survey_mode"][:] = 0

    # loop over packets
    with nogil:
        for packet in range(size):
            with gil:
                # acquisition time
                acquisition_time = (
                    tm["PA_TDS_ACQUISITION_TIME"][packet, 0],
                    tm["PA_TDS_ACQUISITION_TIME"][packet, 1],
                )

                # the flag for time synchronization
                synchro_flag = tm["PA_TDS_ACQUISITION_TIME"][packet, 2]

                # channel status info
                channel_status = (
                    tm["PA_TDS_LFM_CWF_CH1"][packet],
                    tm["PA_TDS_LFM_CWF_CH2"][packet],
                    tm["PA_TDS_LFM_CWF_CH3"][packet],
                    tm["PA_TDS_LFM_CWF_CH4"][packet],
                    tm["PA_TDS_LFM_CWF_CH5"][packet],
                    tm["PA_TDS_LFM_CWF_CH6"][packet],
                    tm["PA_TDS_LFM_CWF_CH7"][packet],
                    tm["PA_TDS_LFM_CWF_CH8"][packet],
                )

                # artefacts
                artefacts = (
                    tm["PA_TDS_CWF_ART_CH1_OR"][packet],
                    tm["PA_TDS_CWF_ART_CH2_OR"][packet],
                    tm["PA_TDS_CWF_ART_CH3_OR"][packet],
                    tm["PA_TDS_CWF_ART_CH4_OR"][packet],
                    tm["PA_TDS_CWF_ART_CH5_OR"][packet],
                    tm["PA_TDS_CWF_ART_CH6_OR"][packet],
                    tm["PA_TDS_CWF_ART_BUF_OVERFLOW"][packet],
                    tm["PA_TDS_CWF_ART_SCM_OFF"][packet],
                )

                # input config
                input_config = (
                    tm["PA_TDS_LFM_CWF_INPUT_CONF1"][packet],
                    tm["PA_TDS_LFM_CWF_INPUT_CONF2"][packet],
                    tm["PA_TDS_LFM_CWF_INPUT_CONF3"][packet],
                    tm["PA_TDS_LFM_CWF_INPUT_CONF4"][packet],
                    tm["PA_TDS_LFM_CWF_INPUT_CONF5"][packet],
                    tm["PA_TDS_LFM_CWF_INPUT_CONF6"][packet],
                    tm["PA_TDS_CWF_ART_MAG_HEATER"][packet],
                    tm["PA_TDS_CWF_ART_SCM_CALIB"][packet],
                )

                # bias status info
                bias_status =  (
                    tm["PA_BIA_ON_OFF"][packet],
                    tm["PA_BIA_MODE_BIAS3_ENABLED"][packet],
                    tm["PA_BIA_MODE_BIAS2_ENABLED"][packet],
                    tm["PA_BIA_MODE_BIAS1_ENABLED"][packet],
                    tm["PA_BIA_MODE_HV_ENABLED"][packet],
                    tm["PA_BIA_MODE_MUX_SET"][packet],
                )

                # snapshot number
                snapshot_nr = tm["PA_TDS_SNAPSHOT_NR"][packet]
                if snapshot_nr != current_snapshot:
                    current_snapshot = snapshot_nr
                    current_sample = 0

                # Samples per sec.
                # (Note f["PA_TDS_LFM_CWF_SAMP_RATE"] = log2(samp_rate))
                sampling_rate = 2 ** (tm["PA_TDS_LFM_CWF_SAMP_RATE"][packet])

                # Get TT2000 Epoch times
                epoch = Time().obt_to_utc(np.array([acquisition_time]), to_tt2000=True)

                # Sampling rate in nanoseconds
                samp_step = <unsigned long>(1.0e9 / sampling_rate)

                # sample per channel
                samp_per_ch = tm["PA_TDS_LFR_CWF_SAMPS_PER_CH"][packet]

                # loop over samples defined in the variable
                for sample in range(samp_per_ch):
                    # populate the data array
                    data["epoch"][index] = epoch + (sample * samp_step)
                    data["scet"][index] = Time.cuc_to_scet(np.array([acquisition_time]))
                    data["acquisition_time"][index, :] = acquisition_time
                    data["synchro_flag"][index] = synchro_flag

                    # channel status info
                    data["channel_status_info"][index] = channel_status

                    # data artefacts
                    data["cwf_data_artefacts"][index] = artefacts

                    # input config
                    data["input_config"][index] = input_config

                    # informations for bias
                    data["bia_status_info"][index] = bias_status

                    # sampling rate
                    data["sampling_rate"][index] = sampling_rate

                    # snapshot number
                    #data["SNAPSHOT_SEQ_NR"][index] = snapshot_nr

                    # number of the sample
                    #data["SAMP_SEQ_NR"][index] = current_sample
                    current_sample += 1

                    # initialization of the counter of activated channel to be able
                    # to place read data correctly inside the block
                    counter_ch = 0

                    # loop over channels and add data
                    for channel in range(8):
                        if channel_status[channel] == 1:
                            data["waveform_data"][index, channel] = tm[
                                "PA_TDS_LFM_CWF_DATA_BLK"
                            ][
                                packet,
                                sample + counter_ch * samp_per_ch,
                            ]
                            counter_ch += 1

                    # increment the index
                    index += 1

    return data
