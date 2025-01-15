from libc.stdint cimport uint8_t
from libc.stdint cimport uint16_t
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

import numpy as np
cimport numpy as np

from roc.rap.tasks.utils import h5_group_to_dict

from roc.rpl.time import Time
from roc.idb.converters.cdf_fill import fill_records

__all__ = ["MAMP", "set_mamp"]

# Numpy array dtype for TDS MAMP L1 survey data
# Name convention is lower case
MAMP = [
    ("epoch", "uint64"),
    ("scet", "float64"),
    ("acquisition_time", ("uint32", 2)),
    ("synchro_flag", "uint8"),
    ("quality_flag", "uint8"),
    ("quality_bitmask", "uint16"),
    ("survey_mode", "uint8"),
    ("bia_status_info", ("uint8", 6)),
    ("dec_rate", "uint8"),
    ("hf_data_artefacts", ("uint8", 5)),
    ("rpw_status_info", ("uint8", 8)),
    ("input_config", "uint32"),
    ("snapshot_seq_nr", "uint16"),
    ("channel_status_info", ("uint8", 4)),
    ("waveform_data", ("int16", 4)),
]

cpdef np.ndarray set_mamp(object l0, object task):
    """
    Extract TM_TDS_SCIENCE_NORMAL_MAMP data

    :param l0: h5py.h5 object containing the RPW TM/TC packets
    :param task: POPPy task
    :return: numpy array with TDS mamp data
    """

    return Mamp().set_mamp(l0, task)

cdef class Mamp:

    cdef public np.ndarray data
    cdef public Py_ssize_t index

    def __init__(self):
        # Initialize mamp data array
        self.data = np.empty(
            0,
            dtype=MAMP,
        )

        # initialize the position in the data array
        self.index = 0

    cpdef np.ndarray set_mamp(self, object l0, object task):

        cdef:
            Py_ssize_t packet
            Py_ssize_t size
            Py_ssize_t sample
            list void_list
            str name
            object tm

        # name of the packet
        name = "TM_TDS_SCIENCE_NORMAL_MAMP"
        #logger.debug("Get data for " + name)

        # get the TDS MAMP packet data
        if name in l0["TM"]:
            tm = l0["TM"][name]["source_data"]
        else:
            # rest of the code inside the with statement will not be called
            return self.data

        # Make sure to use dictionary instead of H5 group
        # (Increase read speed)
        tm = h5_group_to_dict(tm)

        # suppose for now that we have the good size for the data
        size = np.sum(tm["PA_TDS_MAMP_SAMP_PER_CH"])
        #logger.debug("Number of samples: {0}".format(size))

        # create the data array with good size
        self.data = np.zeros(size, dtype=MAMP)
        fill_records(self.data)

        # get the number of packets
        size = tm["PA_TDS_ACQUISITION_TIME"].shape[0]
        #logger.debug("Number of packets: {0}".format(size))

        # survey mode to normal
        self.data["survey_mode"][:] = 0

        # loop over packets
        with nogil:
            for packet in range(size):
                with gil:
                    # loop over samples per channel
                    # defined in the variable PA_TDS_MAMP_SAMP_PER_CH
                    void_list = [
                        self._fill_mamp_data(tm, packet, sample)
                        for sample in range(tm["PA_TDS_MAMP_SAMP_PER_CH"][packet])
                    ]

        return self.data

    cdef _fill_mamp_data(self, object tm,
                         Py_ssize_t packet,
                         Py_ssize_t sample,
                         ):

        cdef:
            Py_ssize_t channel
            uint8_t counter_ch
            uint16_t snapshot_nr
        # populate the data array

        # Time variables
        self.data["acquisition_time"][self.index, :] = (
            tm["PA_TDS_ACQUISITION_TIME"][packet, 0],
            tm["PA_TDS_ACQUISITION_TIME"][packet, 1],
        )
        self.data["epoch"][self.index] = Time().obt_to_utc(
            np.array([self.data["acquisition_time"][self.index, :]]),
            to_tt2000=True)
        self.data["synchro_flag"][self.index] = tm[
            "PA_TDS_ACQUISITION_TIME"][packet, 2]
        self.data["scet"][self.index] = Time.cuc_to_scet(
            np.array([self.data["acquisition_time"][self.index, :]]))

        # dec rate
        self.data["dec_rate"][self.index] = tm[
            "PA_TDS_N_MAMP_DEC_RATE"][packet]

        # put the sampling rate
#        self.data["sampling_rate"][self.index] = tm[
#            "PA_TDS_MAMP_BASE_SAMP_RATE"][packet]

        # channel status info
        self.data["channel_status_info"][self.index] = (
            tm["PA_TDS_N_MAMP_ADC_CH1"][packet],
            tm["PA_TDS_N_MAMP_ADC_CH2"][packet],
            tm["PA_TDS_N_MAMP_ADC_CH3"][packet],
            tm["PA_TDS_N_MAMP_ADC_CH4"][packet],
        )

        # data artefacts
        self.data["hf_data_artefacts"][self.index] = (
            tm["PA_TDS_HF_ART_BUF_OVERFLOW"][packet],
            tm["PA_TDS_HF_ART_ADC1_OR"][packet],
            tm["PA_TDS_HF_ART_ADC2_OR"][packet],
            tm["PA_TDS_HF_ART_ADC3_OR"][packet],
            tm["PA_TDS_HF_ART_ADC4_OR"][packet],
        )

        # filter coefs
#        self.data["filter_coefs"][self.index] = tm[
#            "PA_TDS_FILTER_COEFS"][packet]

        # RPW status information
        self.data["rpw_status_info"][self.index] = (
            tm["PA_TDS_THR_OFF"][packet],
            tm["PA_TDS_LFR_OFF"][packet],
            tm["PA_TDS_ANT1_OFF"][packet],
            tm["PA_TDS_ANT2_OFF"][packet],
            tm["PA_TDS_ANT3_OFF"][packet],
            tm["PA_TDS_SCM_OFF"][packet],
            tm["PA_TDS_HF_ART_MAG_HEATER"][packet],
            tm["PA_TDS_HF_ART_SCM_CALIB"][packet],
        )

        # information for bias
        self.data["bia_status_info"][self.index] = (
            tm["PA_BIA_ON_OFF"][packet],
            tm["PA_BIA_MODE_BIAS3_ENABLED"][packet],
            tm["PA_BIA_MODE_BIAS2_ENABLED"][packet],
            tm["PA_BIA_MODE_BIAS1_ENABLED"][packet],
            tm["PA_BIA_MODE_HV_ENABLED"][packet],
            tm["PA_BIA_MODE_MUX_SET"][packet],
        )

        # snapshot number
        snapshot_nr = tm["PA_TDS_SNAPSHOT_NR"][packet]

        # snapshot number
        self.data["snapshot_seq_nr"][self.index] = snapshot_nr

        # input config
        self.data["input_config"][self.index] = tm[
            "PA_TDS_SWF_HF_CH_CONF"][packet]

        # # initialization of the counter of activated channel to be able
        # # to place read data correctly inside the block
        counter_ch = 0

        # # loop over channels and add data
        for channel in range(4):
            if self.data["channel_status_info"][self.index][channel] == 1:
                self.data["waveform_data"][self.index, channel] = tm[
                    "PA_TDS_MAMP_DATA_BLK"
                ][
                    packet,
                    sample + counter_ch *
                    tm["PA_TDS_MAMP_SAMP_PER_CH"][packet],
                ]
                counter_ch += 1

        # increment the self.index
        self.index += 1
