from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

import numpy as np
cimport numpy as np

from poppy.core.logger import logger
from poppy.core.tools.exceptions import print_exception

from roc.rpl.time import Time
from roc.idb.converters.cdf_fill import fill_records, CDFToFill

from roc.rap.tasks.tds.utils import count_swf
from roc.rap.tasks.utils import sort_data

__all__ = ["RSWF", "set_rswf"]

NSAMP_MAX_PER_REC = 65536

# Numpy array dtype for TDS RSWF L1 survey data
# Name convention is lower case
RSWF = [
    ("epoch", "uint64"),
    ("scet", "float64"),
    ("acquisition_time", ("uint32", 2)),
    ("synchro_flag", "uint8"),
    ("quality_flag", "uint8"),
    ("quality_bitmask", "uint16"),
    ("survey_mode", "uint8"),
    ("bia_status_info", ("uint8", 6)),
    ("sampling_rate", "float32"),
    ("hf_data_artefacts", ("uint8", 5)),
    ("filter_coefs", "uint8"),
    ("rpw_status_info", ("uint8", 8)),
    ("input_config", "uint32"),
    ("snapshot_seq_nr", "uint16"),
    ("channel_status_info", ("uint8", 4)),
    ("samps_per_ch", "uint64"),
    ("waveform_data", ("int16", (4, NSAMP_MAX_PER_REC))),
]

# Enum CIWT0090TM of PA_TDS_HF_CH_SAMP_RATE {NIWD0348}
SAMP_RATE_ENUM = {
    "0": 65534.375,   # SR_64 [Hz]
    "1": 131068.75,  # SR_128 [Hz]
    "2": 262137.5,  # SR_256 [Hz]
    "3": 524275.0,  # SR_512 [Hz]
    "4": 2097100.0  # SR_FULL [Hz]
}

# Possible number of samples per snapshot (2**N with 9<N<18)
SAMP_PER_SNAPSHOT = 2**np.arange(9,18,1).astype(np.uint64)

# Max. Numer of WF samples in a packet
NSAMP_MAX_PER_PKT = 2032

# Number of channels
NCHANNEL = 4

cpdef set_rswf(l0, task, is_sbm=False):
    cdef:
        Py_ssize_t i, j, k, l
        uint8_t counter_ch
        uint8_t nchannel
        uint32_t snapshot_size
        uint32_t samp_per_ch
        uint32_t samp_per_ch_max
        uint32_t samp_per_ch_miss
        uint32_t samp_per_snpht
        uint32_t snapshot_nsamp
        np.ndarray data
        np.ndarray index
        np.ndarray[np.uint32_t, ndim=1] snapshot_id
        np.ndarray[np.uint8_t, ndim=1] pkt_cnt
        np.ndarray[np.uint8_t, ndim=1] pkt_nr
        np.ndarray[np.uint32_t, ndim=1] snapshot_nr
        np.ndarray[np.uint32_t, ndim=1] snapshot_counter
        np.ndarray[np.uint32_t, ndim=1] snpht
        np.ndarray[np.uint32_t, ndim=1] samp_diff

    # Get name of the packet
    if is_sbm == False:
        name = "TM_TDS_SCIENCE_NORMAL_RSWF"
    else:
        name = "TM_TDS_SCIENCE_SBM1_RSWF"
    logger.debug("Get data for " + name)

    # get the RSWF packet data
    if name in l0["TM"]:
        tm = l0["TM"][name]["source_data"]
    else:
        # rest of the code inside the with statement will not be called
        return np.empty(
            0,
            dtype=RSWF,
        )

    # Sort input packets by ascending acquisition times and snapshot number
    tm, __ = sort_data(tm, (
        tm["PA_TDS_SNAPSHOT_NR"],
        tm["PA_TDS_ACQUISITION_TIME"][:,1],
        tm["PA_TDS_ACQUISITION_TIME"][:,0],
                    ))

    # Number of expected packets per snapshot
    pkt_cnt = tm["PA_TDS_SWF_PKT_CNT"][:]

    # sequence number of the packet in the snapshot (from 1 to PA_TDS_SWF_PKT_CNT)
    pkt_nr = tm["PA_TDS_SWF_PKT_NR"][:]

    # Index of the snapshot
    snapshot_nr = tm["PA_TDS_SNAPSHOT_NR"][:].astype(np.uint32)

    # Get number of snapshots
    snapshot_counter, snapshot_size = count_swf(snapshot_nr)

    # Get unique index of snapshots
    snapshot_id = np.unique(snapshot_counter).astype(np.uint32)

    # # create the data array with good size
    data = np.zeros(snapshot_size, dtype=RSWF)
    fill_records(data)

    # Loop over snapshots
    logger.debug("Number of snapshots: {0}".format(snapshot_size))
    with nogil:
        for i in range(snapshot_size):
            with gil:
                # Load indices for the snapshot_id[i]
                snpht = np.where(snapshot_counter == snapshot_id[i])[0].astype(np.uint32)

                # Sort snapshot packets by increasing PA_TDS_SWF_PKT_NR values
                snpht = snpht[np.argsort(pkt_nr[snpht[:]])]

                # Fill acquisition time
                data["acquisition_time"][i, :] = tm["PA_TDS_ACQUISITION_TIME"][snpht[0], :2]

                # Fill epoch in nanosec since RPW time base
                data["epoch"][i] = Time().obt_to_utc(data["acquisition_time"][i, :].reshape([1, 2]),
                                              to_tt2000=True)

                # Fill scet
                data["scet"][i] = Time.cuc_to_scet(data["acquisition_time"][i, :].reshape([1, 2]))

                # the flag for time synchronization
                data["synchro_flag"][i] = tm["PA_TDS_ACQUISITION_TIME"][snpht[0], 2]

                # survey mode to normal
                data["survey_mode"][i] = 0

                # sampling rate
                data["sampling_rate"][i] = SAMP_RATE_ENUM[str(tm["PA_TDS_HF_CH_SAMP_RATE"][snpht[0]])] # sampling rate in Hz

                data["bia_status_info"][i][:] = (
                            tm["PA_BIA_ON_OFF"][snpht[0]],
                            tm["PA_BIA_MODE_BIAS3_ENABLED"][snpht[0]],
                            tm["PA_BIA_MODE_BIAS2_ENABLED"][snpht[0]],
                            tm["PA_BIA_MODE_BIAS1_ENABLED"][snpht[0]],
                            tm["PA_BIA_MODE_HV_ENABLED"][snpht[0]],
                            tm["PA_BIA_MODE_MUX_SET"][snpht[0]],
                        )

                data["channel_status_info"][i][:] = (
                             tm["PA_TDS_HF_CH_ADC_CH1"][snpht[0]],
                             tm["PA_TDS_HF_CH_ADC_CH2"][snpht[0]],
                             tm["PA_TDS_HF_CH_ADC_CH3"][snpht[0]],
                             tm["PA_TDS_HF_CH_ADC_CH4"][snpht[0]],
                         )

                data["rpw_status_info"][i][:] = (
                            tm["PA_TDS_THR_OFF"][snpht[0]],
                            tm["PA_TDS_LFR_OFF"][snpht[0]],
                            tm["PA_TDS_ANT1_OFF"][snpht[0]],
                            tm["PA_TDS_ANT2_OFF"][snpht[0]],
                            tm["PA_TDS_ANT3_OFF"][snpht[0]],
                            tm["PA_TDS_SCM_OFF"][snpht[0]],
                            tm["PA_TDS_HF_ART_MAG_HEATER"][snpht[0]],
                            tm["PA_TDS_HF_ART_SCM_CALIB"][snpht[0]],
                        )

                data["hf_data_artefacts"][i][:] = (
                            tm["PA_TDS_HF_ART_BUF_OVERFLOW"][snpht[0]],
                            tm["PA_TDS_HF_ART_ADC1_OR"][snpht[0]],
                            tm["PA_TDS_HF_ART_ADC2_OR"][snpht[0]],
                            tm["PA_TDS_HF_ART_ADC3_OR"][snpht[0]],
                            tm["PA_TDS_HF_ART_ADC4_OR"][snpht[0]],
                        )

                data["input_config"][i] = tm["PA_TDS_SWF_HF_CH_CONF"][snpht[0]]

                data["filter_coefs"][i] = tm["PA_TDS_FILTER_COEFS"][snpht[0]]

                data["snapshot_seq_nr"][i] = tm["PA_TDS_SNAPSHOT_NR"][snpht[0]]

                # Max. number of data samples per channel
                samp_per_ch_max = np.uint32(NSAMP_MAX_PER_PKT / np.sum(data["channel_status_info"][i][:]))

                # Total number of samples per snapshot
                samp_diff = np.abs((samp_per_ch_max * np.uint32(pkt_cnt[snpht[0]]) - SAMP_PER_SNAPSHOT)).astype(np.uint32)
                samp_per_snpht = SAMP_PER_SNAPSHOT[samp_diff.argsort()[0]]

                # Loop on each packet of the snapshot
                snapshot_nsamp = 0
                j = 0
                k = 0
                while k < pkt_cnt[snpht[0]]:

                    if j >= len(snpht):
                        j = len(snpht) - 1

                    # Check that packet counter k value + 1
                    # is the same than the packet sequence
                    # number pkt_nr[snpht[j]] in the current snapshot
                    if k + 1 != pkt_nr[snpht[j]]:
                        # ... If not, then there is a missing packet.
                        logger.warning("Packet #{0} [{2}] is missing for snapshot #{1}!".format(k+1, i, pkt_cnt[snpht[0]]))

                        # If the missing packet is the last packet...
                        if k+1 == pkt_cnt[snpht[0]]:
                            # compute the number of sample
                            # in the last packet
                            samp_per_ch_miss = samp_per_snpht - np.uint32(samp_per_ch_max * (pkt_cnt[snpht[0]] - 1))

                        # If the missing packet is the first packet...
                        elif k+1 == 1:
                            # If there is only 2 packets for this snapshot
                            if pkt_cnt[snpht[0]] == 2:
                                # Compute the number of sample
                                # in the first packet
                                samp_per_ch_miss = samp_per_snpht - samp_per_ch_max
                            else:
                                # ... Get the number of samples from the next
                                # valid packet (which should be
                                # not the last one)
                                samp_per_ch_miss = samp_per_ch_max

                        # Increment total number of samples
                        # for the current snapshot
                        # assuming that the number of missing samples
                        # is the last samp_per_ch value
                        snapshot_nsamp += samp_per_ch_miss

                        # Increment packet counter k and continue
                        # in order to reach the next packet
                        # sequence number pkt_nr[snpht[j]] in the
                        # snapshot
                        k += 1
                        continue

                    # Fill TDS SWF sample data
                    samp_per_ch = np.uint32(tm["PA_TDS_SAMPS_PER_CH"][snpht[j]])

                    # Update the samp_per_ch_miss value
                    samp_per_ch_miss = samp_per_ch

                    index = np.arange(0, samp_per_ch, 1)

                    counter_ch = 0
                    for l in range(NCHANNEL):
                        if data["channel_status_info"][i][l] == 1:
                            data["waveform_data"][i, l, snapshot_nsamp : snapshot_nsamp + samp_per_ch] = tm[
                                     "PA_TDS_RSWF_DATA_BLK"
                                 ][snpht[j], index + (samp_per_ch * counter_ch)]
                            counter_ch += 1

                    # Increment total number of samples per channel
                    # for the current snapshot
                    snapshot_nsamp += samp_per_ch
                    k += 1
                    j += 1

                # Perform some verifications before saving the snapshot
                try:
                    # Check that total number of samples does not exceed the number of expected max. records in the output file
                    if snapshot_nsamp > NSAMP_MAX_PER_REC:
                        raise Exception("Total number of samples cannot exceed {1}, but {0} found in snapshot #{2}!".format(snapshot_nsamp, NSAMP_MAX_PER_REC, i))

                    # Check that the total number of samples is consistent
                    # with what it is expected
                    if samp_per_snpht != snapshot_nsamp:
                        raise Exception("Unexpected total number of samples in snapshot #{0}!".format(i))
                except:
                    message = print_exception()
                    task.exception(message)
                    data["waveform_data"][i, :, :] = CDFToFill()(data["waveform_data"].dtype.name)
                else:
                    data["samps_per_ch"][i] = snapshot_nsamp

    return data
