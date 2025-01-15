from libc.stdint cimport uint8_t
from libc.stdint cimport uint16_t

cimport numpy as np
import numpy as np

from poppy.core.logger import logger

from roc.idb.converters.cdf_fill import fill_records, CDFToFill
from roc.rpl.time import Time

from roc.rap.tasks.utils import sort_data

__all__ = ["SM", "set_sm"]

# Numpy array dtype for TDS LFM SM L1 survey data
# Name convention is lower case

SM = [
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
    ("sm_srclen", "uint8"),
    ("sm_type", "uint8"),
    ("sm_freq_nr", "uint16"),
    ("sm_freq_axis", "uint8"),
    ("cross_re", ("int8", (10, 200))),
    ("cross_im", ("int8", (10, 200))),
]


cpdef set_sm(l0, task):
    cdef:
        Py_ssize_t index
        Py_ssize_t size
        uint16_t number
        np.ndarray[np.uint16_t, ndim=1] block
        uint8_t coef

    # name of the packet
    name = "TM_TDS_SCIENCE_LFM_SM"
    logger.debug("Get data for " + name)

    # get the LFM SM packet data
    if name in l0["TM"]:
        tm = l0["TM"][name]["source_data"]
    else:
        # rest of the code inside the with statement will not be called
        return np.empty(
            0,
            dtype=SM,
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
    data = np.zeros(size, dtype=SM)
    fill_records(data)

    # survey mode to normal
    data["survey_mode"][:] = 0

    # Epoch
    data["epoch"][:] = Time().obt_to_utc(tm["PA_TDS_ACQUISITION_TIME"][:, :2], to_tt2000=True)

    # acquisition time
    data["acquisition_time"][:, :] = tm["PA_TDS_ACQUISITION_TIME"][:, :2]
    data["synchro_flag"][:] = tm["PA_TDS_ACQUISITION_TIME"][:, 2]

    # scet
    data["scet"][:] = Time.cuc_to_scet(data["acquisition_time"])

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
            tm["PA_TDS_LFM_SM_INPUT_CH1"],
            tm["PA_TDS_LFM_SM_INPUT_CH2"],
            tm["PA_TDS_LFM_SM_INPUT_CH3"],
            tm["PA_TDS_LFM_SM_INPUT_CH4"],
            tm["PA_TDS_LFM_SM_INPUT_CH5"],
            tm["PA_TDS_LFM_SM_INPUT_CH6"],
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

    # other SM data
    data["sm_srclen"][:] = tm["PA_TDS_LFM_SM_SRCLEN"]
    data["sm_freq_axis"][:] = tm["PA_TDS_LFM_SM_FREQ_AXIS"]
    data["sm_freq_nr"][:] = tm["PA_TDS_LFM_SM_NUM_FREQS"]
    data["sm_type"][:] = tm["PA_TDS_LFM_SM_TYPE"]

    # loop over the data to assign to the good channel
    with nogil:
        for index in range(size):
            with gil:
                # initialize the counter for channels
                counter = 0

                # number of freqs and combinations
                number = data["sm_freq_nr"][index]

                # coefficient for getting the number of data for a series of
                # combinations
                coef = 0
                if tm["PA_TDS_LFM_SM_TYPE"][index] == 1:
                    coef = 3
                elif tm["PA_TDS_LFM_SM_TYPE"][index] == 2:
                    coef = 10

                # copy only used data
                block = tm["PA_TDS_LFM_SM_DATA_BLK"][index, :number * coef]

                # real part
                data["cross_re"][index, :coef, :number] = (
                    block.view("int8")[::2].reshape((number, coef)).T
                )

                # real part
                data["cross_im"][index, :coef, :number] = (
                    block.view("int8")[1::2].reshape((number, coef)).T
                )

    return data
