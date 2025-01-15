import numpy as np

from poppy.core.logger import logger

from roc.rpl.time import Time
from roc.idb.converters.cdf_fill import fill_records
from libc.stdint cimport uint8_t
from libc.stdint cimport uint16_t

from roc.rap.tasks.utils import sort_data

__all__ = ["PSD", "set_psd"]

# Numpy array dtype for TDS LFM PSD L1 survey data
# Name convention is lower case

PSD = [
    ("epoch", "uint64"),
    ("scet", "float64"),
    ("acquisition_time", ("uint32", 2)),
    ("synchro_flag", "uint8"),
    ("quality_flag", "uint8"),
    ("quality_bitmask", "uint16"),
    ("survey_mode", "uint8"),
    ("bia_status_info", ("uint8", 6)),
    ("lf_data_artefacts", ("uint8", 16)),
    ("input_config", ("uint8", 6)),
    ("channel_status_info", ("uint8", 6)),
    ("psd_srclen", "uint8"),
    ("psd_freq_nr", "uint16"),
    ("psd_freq_axis", "uint8"),
    ("psd_data", ("uint16", (6, 200))),
]


cpdef set_psd(l0, task):
    cdef:
        Py_ssize_t index
        Py_ssize_t channel
        Py_ssize_t size
        uint16_t number
        uint8_t counter

    # name of the packet
    name = "TM_TDS_SCIENCE_LFM_PSD"
    logger.debug("Get data for " + name)

    # get the LFM PDS packet data
    if name in l0["TM"]:
        tm = l0["TM"][name]["source_data"]
    else:
        # rest of the code inside the with statement will not be called
        return np.empty(
            0,
            dtype=PSD,
        )

    # Sort input packets by ascending acquisition times
    tm, __ = sort_data(tm, (
        tm["PA_TDS_ACQUISITION_TIME"][:,1],
        tm["PA_TDS_ACQUISITION_TIME"][:,0],
                    ))

    # get the number of packets
    size = tm["PA_TDS_ACQUISITION_TIME"].shape[0]
    logger.debug("Number of packets: {0}".format(size))

    # create the data array with good size
    data = np.zeros(size, dtype=PSD)
    fill_records(data)

    # survey mode to normal
    data["survey_mode"][:] = 0

    # TT2000 Epoch times
    data["epoch"][:] = Time().obt_to_utc(tm["PA_TDS_ACQUISITION_TIME"][:, :2], to_tt2000=True)

    # acquisition time
    data["acquisition_time"][:, :] = tm["PA_TDS_ACQUISITION_TIME"][:, :2]
    data["synchro_flag"][:] = tm["PA_TDS_ACQUISITION_TIME"][:, 2]

    # scet
    data["scet"][:] = Time.cuc_to_scet(data["acquisition_time"])

    # channel status info
    data["channel_status_info"][:, :] = np.vstack(
        (
            tm["PA_TDS_LFM_PSD_CH1"],
            tm["PA_TDS_LFM_PSD_CH2"],
            tm["PA_TDS_LFM_PSD_CH3"],
            tm["PA_TDS_LFM_PSD_CH4"],
            tm["PA_TDS_LFM_PSD_CH5"],
            tm["PA_TDS_LFM_PSD_CH6"],
        )
    ).T

    # artefacts
    data["lf_data_artefacts"][:, :] = np.vstack(
        (
            tm["PA_TDS_LF_ART_CH1_OR"],
            tm["PA_TDS_LF_ART_CH2_OR"],
            tm["PA_TDS_LF_ART_CH3_OR"],
            tm["PA_TDS_LF_ART_CH4_OR"],
            tm["PA_TDS_LF_ART_CH5_OR"],
            tm["PA_TDS_LF_ART_CH6_OR"],
            tm["PA_TDS_LF_ART_CH7_OR"],
            tm["PA_TDS_LF_ART_CH8_OR"],
            tm["PA_TDS_LF_ART_MAG_HEATER"],
            tm["PA_TDS_LF_ART_SCM_CALIB"],
            tm["PA_TDS_LF_ART_ANT3_OFF"],
            tm["PA_TDS_LF_ART_ANT2_OFF"],
            tm["PA_TDS_LF_ART_ANT1_OFF"],
            tm["PA_TDS_LF_ART_SCM_OFF"],
            tm["PA_TDS_LF_ART_THR_OFF"],
            tm["PA_TDS_LF_ART_LFR_OFF"],
        )
    ).T

    # input config
    data["input_config"][:, :] = np.vstack(
        (
            tm["PA_TDS_LFM_PSD_INPUT_CONF1"],
            tm["PA_TDS_LFM_PSD_INPUT_CONF2"],
            tm["PA_TDS_LFM_PSD_INPUT_CONF3"],
            tm["PA_TDS_LFM_PSD_INPUT_CONF4"],
            tm["PA_TDS_LFM_PSD_INPUT_CONF5"],
            tm["PA_TDS_LFM_PSD_INPUT_CONF6"],
        )
    ).T

    # bias status info
    data["bia_status_info"][:, :] = np.vstack(
        (
            tm["PA_BIA_ON_OFF"],
            tm["PA_BIA_MODE_BIAS3_ENABLED"],
            tm["PA_BIA_MODE_BIAS2_ENABLED"],
            tm["PA_BIA_MODE_BIAS1_ENABLED"],
            tm["PA_BIA_MODE_HV_ENABLED"],
            tm["PA_BIA_MODE_MUX_SET"],
        )
    ).T

    # other PSD data
    data["psd_srclen"][:] = tm["PA_TDS_LFM_PSD_SRCLEN"]
    data["psd_freq_axis"][:] = tm["PA_TDS_LFM_PSD_FREQ_AXIS"]
    data["psd_freq_nr"][:] = tm["PA_TDS_LFM_PSD_NUM_FREQS"]

    # loop over the data to assign to the good channel
    with nogil:
        for index in range(size):
            with gil:
                # initialize the counter for channels
                counter = 0

                # number of freqs
                number = data["psd_freq_nr"][index]

                # loop over channels to check which one is activated and set
                # the data according to this
                for channel in range(6):
                    # if the channel is activated
                    if data["channel_status_info"][index, channel] == 1:
                        # copy only used data
                        data["psd_data"][index, channel, :number] = tm[
                            "PA_TDS_LFM_PSD_DATA_BLK"
                        ][index, counter * number:(counter + 1) * number]

                        # increment the counter
                        counter += 1

    return data
