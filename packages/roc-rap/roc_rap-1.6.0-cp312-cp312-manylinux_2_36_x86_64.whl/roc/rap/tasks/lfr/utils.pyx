import numpy as np
cimport numpy as np

from poppy.core.logger import logger
from poppy.core.tools.exceptions import print_exception

from cpython cimport bool
from libc.stdint cimport uint16_t, uint32_t, uint64_t

from roc.rpl.time import Time
from roc.idb.converters.cdf_fill import fill_records, CDFToFill

from roc.rap.tasks.utils import sort_data

__all__ = ["group", "start_end_group", "fill_asm", "set_cwf", "set_swf"]


# Expected number of ASM bins per buffer for F0, F1 and F2
# A ASM buffer is formed by a set of 3 successive packets
ASM_NBINS = {"F0": [32, 32, 24],
             "F1": [36, 36, 32],
             "F2": [32, 32, 32]}

# ASM Bins offset
ASM_OFFSET = {"F0": 17,
              "F1": 6,
              "F2": 7}

cpdef tuple count_buff(np.ndarray[np.uint8_t, ndim=1] x):
    cdef:
        Py_ssize_t i
        Py_ssize_t nmax = x.shape[0]
        np.ndarray buff = np.zeros(nmax, dtype=np.uint32)
        uint32_t nbuff = 0

    # Get the number of buffers
    for i in range(1, nmax):
        if x[i] <= x[i - 1]:
            nbuff += 1
        buff[i] = nbuff

    return buff, nbuff + 1


cpdef tuple group(np.ndarray[np.uint8_t, ndim=1] x):
    cdef:
        Py_ssize_t i
        Py_ssize_t nmax = x.shape[0]
        np.ndarray result = np.zeros(nmax, dtype=np.uint64)
        Py_ssize_t counter = 0

    # Get the number of groups (i.e., buffer)
    for i in range(1, nmax):
        if x[i] <= x[i - 1]:
            counter += 1
        result[i] = counter

    return result, start_end_group(x, counter + 1)


cpdef np.ndarray[np.uint64_t, ndim = 2] start_end_group(
    np.ndarray[np.uint8_t, ndim=1] x,
    uint64_t ngroups,
):
    cdef:
        Py_ssize_t i
        Py_ssize_t nmax = x.shape[0]
        Py_ssize_t counter = 0
        np.ndarray[np.uint64_t, ndim = 2] result = np.zeros(
            (ngroups, 2),
            dtype=np.uint64,
        )
        Py_ssize_t start = 0

    for i in range(1, nmax):
        if x[i] <= x[i - 1]:
            # indicate the start and end of new group
            result[counter, 0] = start
            result[counter, 1] = i - 1

            # new group
            counter += 1

            # new start point
            start = i

    # treat the last group
    result[counter, 0] = start
    result[counter, 1] = nmax - 1

    return result


cpdef np.ndarray fill_asm(dict fdata, str freq, list asm_dtype, np.ndarray asm_blks):

    cdef:
        Py_ssize_t i
        Py_ssize_t j
        Py_ssize_t k
        Py_ssize_t l
        list nbins
        int bin_offset
        int ibuff_len
        np.ndarray ibuff
        np.ndarray[np.uint8_t, ndim = 1] nblk
        uint32_t nbuff
        np.ndarray[np.uint8_t, ndim = 1] nr_asm
        np.ndarray[np.uint32_t, ndim = 1] buff
        np.ndarray data
        np.ndarray[np.float32_t, ndim = 2] asm_buff

    # Make sure that the input packets are sorted by ascending acquisition time
    # and ASM buffer packet index
    fdata, __ = sort_data(fdata, (
        fdata["PA_LFR_PKT_NR_ASM"][:],
        fdata["PA_LFR_ACQUISITION_TIME"][:, 1],
        fdata["PA_LFR_ACQUISITION_TIME"][:, 0],
    ))

    # Packet index for a given ASM buffer
    # In nominal, 1 ASM data buffer is stored into 3 successive packets
    nr_asm = fdata["PA_LFR_PKT_NR_ASM"]

    # Actual number of blocks per packet
    nblk = fdata["PA_LFR_ASM_{0}_BLK_NR".format(freq)].astype(np.uint8)

    # Expected number of bins per buffer
    nbins = ASM_NBINS[freq]

    # Get bin offset for current freq
    bin_offset = ASM_OFFSET[freq]

    # Number of buffers present in the data
    buff, nbuff = count_buff(nr_asm)

    # Create the data container from the number of buffers
    data = np.zeros(nbuff, dtype=asm_dtype)
    fill_records(data)

    # Initalize ASM buffer data array
    asm_buff = np.full([128, 25], -1.0e31, dtype=np.float32)

    # Loop on each buffer
    i = 0
    while i < nbuff:

        # Get indices for the current ASM buffer
        # (should have 3 elements
        # corresponding to the 3 successive packets of data)
        ibuff = np.where(buff == i)[0]

        # Get number of packets
        ibuff_len = len(ibuff)
        if ibuff_len != 3:
            logger.warning('Current LFR ASM buffer is not complete!')

        # get the acquisition time and synchro of
        # the first packet available of the buffer
        data["acquisition_time"][i] = fdata[
            "PA_LFR_ACQUISITION_TIME"][ibuff[0], :2]
        data["synchro_flag"][i] = fdata[
            "PA_LFR_ACQUISITION_TIME"][ibuff[0], 2]

        # Compute the corresponding TT2000 epoch times
        data["epoch"][i] = Time().obt_to_utc(fdata[
            "PA_LFR_ACQUISITION_TIME"][ibuff[0], :2], to_tt2000=True)

        data["scet"][i] = Time.cuc_to_scet(fdata[
            "PA_LFR_ACQUISITION_TIME"][ibuff[0], :2])

        # Fill parameters related to LFR config (e.g., Bias)
        data["bias_mode_mux_set"][i] = fdata["PA_BIA_MODE_MUX_SET"][ibuff[0]]
        data["bias_mode_hv_enabled"][i] = fdata[
            "PA_BIA_MODE_HV_ENABLED"][ibuff[0]]
        data["bias_mode_bias1_enabled"][i] = fdata[
            "PA_BIA_MODE_BIAS1_ENABLED"][ibuff[0]]
        data["bias_mode_bias2_enabled"][i] = fdata[
            "PA_BIA_MODE_BIAS2_ENABLED"][ibuff[0]]
        data["bias_mode_bias3_enabled"][i] = fdata[
            "PA_BIA_MODE_BIAS3_ENABLED"][ibuff[0]]
        data["bias_on_off"][i] = fdata["PA_BIA_ON_OFF"][ibuff[0]]
        data["bw"][i] = fdata["SY_LFR_BW"][ibuff[0]]
        data["sp0"][i] = fdata["SY_LFR_SP0"][ibuff[0]]
        data["sp1"][i] = fdata["SY_LFR_SP1"][ibuff[0]]
        data["r0"][i] = fdata["SY_LFR_R0"][ibuff[0]]
        data["r1"][i] = fdata["SY_LFR_R1"][ibuff[0]]
        data["r2"][i] = fdata["SY_LFR_R2"][ibuff[0]]

        # Filling ASM over the 3 successive packets of the buffer
        asm_buff[:] = -1.0e31

        # Define initial offset for the current buffer
        k = bin_offset
        l = 0
        # Loop on ASM expected packets for current buffer (i.e., 3)
        for j in range(len(nbins)):

            if j + 1 != nr_asm[ibuff[l]]:
                logger.warning(f"Packet #{j} is missing!")
                continue
            else:
                # If the number of blocks in the packet is not
                # equal to the expected number of bins
                # thus the current packet is not complete
                if nbins[j] != nblk[ibuff[l]]:
                    logger.warning("Incomplete LFR ASM packet!")

                # Fill asm_buff array with ASM blocks for the l-th packet in
                # the current buffer
                asm_buff[k:k + nblk[ibuff[l]],
                         :] = asm_blks[ibuff[l], :nblk[ibuff[l]], :]

                # Increment local ibuff indice
                l += 1
                if l >= ibuff_len:
                    break

            # Increment by bins length
            k += nbins[j]

        # Fill output data array with current ASM buffer data
        data["asm"][i, :, :] = asm_buff[:, :]

        # Increment buffer index
        i += 1

    data["asm_cnt"][:] = np.sum(nbins)

    return data


# LFR CWF SAMPLING RATES IN Hz
CWF_SAMPLING_RATE = {"F1": 4096,
                     "F2": 256.0,
                     "F3": 16.0}

# Fill CDF data with CWF packet data
cpdef np.ndarray set_cwf(dict fdata, str freq, list cwf_dtype, bool magnetic, task):

    cdef:
        Py_ssize_t packet
        uint16_t nsamp
        uint64_t nsamps, size, i
        uint64_t epoch0
        float delta_t
        float samp_rate
        np.ndarray blk_nr
        np.ndarray data
        np.ndarray elec
        np.ndarray mag

    # Sort input packets by ascending acquisition times
    fdata, __ = sort_data(fdata, (
        fdata["PA_LFR_ACQUISITION_TIME"][:, 1],
        fdata["PA_LFR_ACQUISITION_TIME"][:, 0],
    ))

    # Get number of blocks
    if freq == "F3":
        blk_nr = fdata["PA_LFR_CWF3_BLK_NR"][:]
    elif freq == "LONG_F3":
        blk_nr = fdata["PA_LFR_CWFL3_BLK_NR"][:]
        freq = freq[-2:]
    else:
        blk_nr = fdata["PA_LFR_CWF_BLK_NR"][:]

    # Number of samples
    nsamps = np.sum(blk_nr)

    # Sampling rate
    samp_rate = CWF_SAMPLING_RATE[freq]

    # Cadence in nanoseconds
    delta_t = 1.0e9 / samp_rate

    # create a record array with the good dtype and good length
    data = np.zeros(nsamps, dtype=cwf_dtype)
    fill_records(data)

    # Get the number of packets
    size = fdata["PA_LFR_ACQUISITION_TIME"].shape[0]

    # Loop over packets
    i = 0
    for packet in range(size):

        # Get the number of samples for the current packet
        nsamp = blk_nr[packet]

        # get the acquisition time and time synch. flag
        data["acquisition_time"][i:i + nsamp, :] = \
            fdata["PA_LFR_ACQUISITION_TIME"][packet, :2]
        data["synchro_flag"][i:i + nsamp] = \
            fdata["PA_LFR_ACQUISITION_TIME"][packet, 2]

        # Compute corresponding Epoch time
        epoch0 = Time().obt_to_utc(
            fdata["PA_LFR_ACQUISITION_TIME"][packet, :2].reshape([1, 2]),
            to_tt2000=True)

        data["epoch"][i:i + nsamp] = epoch0 + \
            np.uint64(delta_t * np.arange(0, nsamp, 1))

        data["scet"][
            i:i + nsamp] = Time.cuc_to_scet(data["acquisition_time"][i:i + nsamp, :])

        data["sampling_rate"][i:i + nsamp] = samp_rate

        data["bias_mode_mux_set"][i:i + nsamp] = \
            fdata["PA_BIA_MODE_MUX_SET"][packet]
        data["bias_mode_hv_enabled"][i:i + nsamp] = \
            fdata["PA_BIA_MODE_HV_ENABLED"][packet]
        data["bias_mode_bias1_enabled"][i:i + nsamp] = \
            fdata["PA_BIA_MODE_BIAS1_ENABLED"][packet]
        data["bias_mode_bias2_enabled"][i:i + nsamp] = \
            fdata["PA_BIA_MODE_BIAS2_ENABLED"][packet]
        data["bias_mode_bias3_enabled"][i:i + nsamp] = \
            fdata["PA_BIA_MODE_BIAS3_ENABLED"][packet]
        data["bias_on_off"][i:i + nsamp] = fdata["PA_BIA_ON_OFF"][packet]
        data["bw"][i:i + nsamp] = fdata["SY_LFR_BW"][packet]
        data["sp0"][i:i + nsamp] = fdata["SY_LFR_SP0"][packet]
        data["sp1"][i:i + nsamp] = fdata["SY_LFR_SP1"][packet]
        data["r0"][i:i + nsamp] = fdata["SY_LFR_R0"][packet]
        data["r1"][i:i + nsamp] = fdata["SY_LFR_R1"][packet]
        data["r2"][i:i + nsamp] = fdata["SY_LFR_R2"][packet]

        # potential just need to be reshaped
        data["v"][i:i + nsamp] = fdata["PA_LFR_SC_V_" + freq][packet, :]

        # electrical and magnetic needs to have their components merged before
        # the reshaping
        elec = np.empty([nsamp, 2], dtype=np.int16)
        elec[:, 0] = fdata["PA_LFR_SC_E1_" + freq][packet, :]
        elec[:, 1] = fdata["PA_LFR_SC_E2_" + freq][packet, :]
        data["e"][i:i + nsamp, :] = elec

        # get magnetic only if present
        if magnetic:
            mag = np.empty([nsamp, 3], dtype=np.int16)
            mag[:, 0] = fdata["PA_LFR_SC_B1_" + freq][packet, :]
            mag[:, 1] = fdata["PA_LFR_SC_B2_" + freq][packet, :]
            mag[:, 2] = fdata["PA_LFR_SC_B3_" + freq][packet, :]
            data["b"][i:i + nsamp, :] = mag

        i += nsamp

    return data

# LFR SWF SAMPLING RATES IN Hz
SWF_SAMPLING_RATE = {"F0": 24576.0,
                     "F1": 4096.0,
                     "F2": 256.0}

# Max. Number of WF samples in a packet
NSAMP_MAX_PER_PKT = 304

# Number of samples per snapshot
SAMP_PER_SNAPSHOT = 2048

# Number of packets per snapshot
PKT_PER_SNAPSHOT = 7

# Fill CDF data with SWF packet data
cpdef set_swf(dict fdata, str freq, list swf_dtype, task):
    cdef:
        Py_ssize_t i, j, k
        np.uint16_t samp_per_pkt
        np.uint16_t size
        np.uint16_t snapshot_nsamp
        np.uint16_t samp_per_pkt_miss
        np.uint16_t samp_per_pkt_max
        np.ndarray data
        np.ndarray[np.uint8_t, ndim = 1] pkt_nr
        np.ndarray[np.uint8_t, ndim = 1] pkt_cnt
        np.ndarray[np.uint32_t, ndim = 1] snapshot_id
        np.ndarray[np.uint32_t, ndim = 1] snpht
        np.ndarray[np.uint32_t, ndim = 1] snapshot_seq_nr

    # Sort input packets by ascending acquisition times and snapshot number
    fdata, __ = sort_data(fdata, (
        fdata["PA_LFR_PKT_NR"],
        fdata["PA_LFR_ACQUISITION_TIME"][:, 1],
        fdata["PA_LFR_ACQUISITION_TIME"][:, 0],
    ))

    # Get Total count of packets for the current snapshot.
    pkt_cnt = fdata["PA_LFR_PKT_CNT"]
    # Get Number of the packet for the current snapshot
    pkt_nr = fdata["PA_LFR_PKT_NR"]

    # Get Number of snapshots
    snapshot_seq_nr, size = count_buff(pkt_nr)
    snapshot_id = np.unique(snapshot_seq_nr).astype(np.uint32)

    # create the data array with good size
    data = np.zeros(size, dtype=swf_dtype)
    fill_records(data)

    # Max sample number per record for V, E and B
    nsamp_max_per_rec = data["e"].shape[-1]

    # Loop over snapshots
    logger.debug("Number of snapshots: {0}".format(size))
    with nogil:
        for i in range(size):
            with gil:
                snpht = np.where(snapshot_seq_nr == snapshot_id[i])[
                    0].astype(np.uint32)

                # Sort snapshot packets by increasing PA_LFR_PKT_NR values
                snpht = snpht[np.argsort(pkt_nr[snpht[:]])]

                # Fill acquisition time
                data["acquisition_time"][i, :] = fdata[
                    "PA_LFR_ACQUISITION_TIME"][snpht[0], :2]

                data["epoch"][i] = Time().obt_to_utc(data["acquisition_time"][i, :].reshape([1, 2]),
                                                     to_tt2000=True)

                data["scet"][i] = Time.cuc_to_scet(
                    data["acquisition_time"][i, :].reshape([1, 2]))

                # the flag for time synchronization
                data["synchro_flag"][i] = fdata[
                    "PA_LFR_ACQUISITION_TIME"][snpht[0], 2]

                # Sampling rate in Hz
                data["sampling_rate"][i] = float(SWF_SAMPLING_RATE[freq])

                data["bias_mode_mux_set"][i] = fdata[
                    "PA_BIA_MODE_MUX_SET"][snpht[0]]
                data["bias_mode_hv_enabled"][i] = fdata[
                    "PA_BIA_MODE_HV_ENABLED"
                ][snpht[0]]
                data["bias_mode_bias1_enabled"][i] = fdata[
                    "PA_BIA_MODE_BIAS1_ENABLED"
                ][snpht[0]]
                data["bias_mode_bias2_enabled"][i] = fdata[
                    "PA_BIA_MODE_BIAS2_ENABLED"
                ][snpht[0]]
                data["bias_mode_bias3_enabled"][i] = fdata[
                    "PA_BIA_MODE_BIAS3_ENABLED"
                ][snpht[0]]
                data["bias_on_off"][i] = fdata["PA_BIA_ON_OFF"][snpht[0]]
                data["bw"][i] = fdata["SY_LFR_BW"][snpht[0]]
                data["sp0"][i] = fdata["SY_LFR_SP0"][snpht[0]]
                data["sp1"][i] = fdata["SY_LFR_SP1"][snpht[0]]
                data["r0"][i] = fdata["SY_LFR_R0"][snpht[0]]
                data["r1"][i] = fdata["SY_LFR_R1"][snpht[0]]
                data["r2"][i] = fdata["SY_LFR_R2"][snpht[0]]

                # Max number of samples for this snapshot
                samp_per_pkt_max = NSAMP_MAX_PER_PKT
                samp_per_pkt_miss = samp_per_pkt_max

                # Loop on each packet of the current snapshot
                # Assuming there is no missing packet in the snapshot
                # (i.e., pkt_cnt = 7)
                snapshot_nsamp = 0
                j = 0
                k = 0
                while k < pkt_cnt[snpht[0]]:

                    if j >= len(snpht):
                        j = len(snpht) - 1

                    # Check that packet counter k value
                    # is the same as the packet sequence
                    # number pkt_nr[snpht[j]] in the current snapshot
                    if k + 1 != pkt_nr[snpht[j]]:
                        # ... If not, then there is a missing packet.
                        logger.warning("Packet #{0} [{2}] is missing for snapshot #{1}!".format(
                            k + 1, i, pkt_cnt[snpht[0]]))

                        # If the missing packet is the last packet...
                        if k + 1 == pkt_cnt[snpht[0]]:
                            # compute the number of sample
                            # in the last packet
                            samp_per_pkt_miss = SAMP_PER_SNAPSHOT - \
                                (samp_per_pkt_max * (pkt_cnt[snpht[0]] - 1))

                        # If the missing packet is the first packet...
                        elif k + 1 == 1:
                            # If there is only 2 packets for this snapshot
                            if pkt_cnt[snpht[0]] == 2:
                                # Compute the number of sample
                                # in the first packet
                                samp_per_pkt_miss = SAMP_PER_SNAPSHOT - samp_per_pkt_max
                            else:
                                # ... Get the number of samples from the next
                                # valid packet (which should be
                                # not the last one)
                                samp_per_pkt_miss = samp_per_pkt_max

                        # Increment total number of samples
                        # for the current snapshot
                        # assuming that samp_per_pkt_miss samples
                        # are missing
                        snapshot_nsamp += samp_per_pkt_miss

                        # Increment packet counter k and continue
                        # in order to reach the next packet
                        # sequence number pkt_nr[snpht[j]] in the
                        # snapshot
                        k += 1
                        continue

                    # Get number of LFR SWF sample data blocks
                    samp_per_pkt = fdata["PA_LFR_SWF_BLK_NR"][snpht[j]]

                    # Update the samp_per_pkt_miss value
                    samp_per_pkt_miss = samp_per_pkt

                    # Fill potential values
                    data["v"][i, snapshot_nsamp: snapshot_nsamp +
                              samp_per_pkt] = fdata["PA_LFR_SC_V_" + freq][snpht[j], :samp_per_pkt]

                    # Fill electric field values
                    data["e"][i, 0, snapshot_nsamp: snapshot_nsamp +
                              samp_per_pkt] = fdata["PA_LFR_SC_E1_" + freq][snpht[j], :samp_per_pkt]
                    data["e"][i, 1, snapshot_nsamp: snapshot_nsamp +
                              samp_per_pkt] = fdata["PA_LFR_SC_E2_" + freq][snpht[j], :samp_per_pkt]

                    # Fill magnetic field values
                    data["b"][i, 0, snapshot_nsamp: snapshot_nsamp +
                              samp_per_pkt] = fdata["PA_LFR_SC_B1_" + freq][snpht[j], :samp_per_pkt]
                    data["b"][i, 1, snapshot_nsamp: snapshot_nsamp +
                              samp_per_pkt] = fdata["PA_LFR_SC_B2_" + freq][snpht[j], :samp_per_pkt]
                    data["b"][i, 2, snapshot_nsamp: snapshot_nsamp +
                              samp_per_pkt] = fdata["PA_LFR_SC_B3_" + freq][snpht[j], :samp_per_pkt]

                    # Increment total number of samples per channel
                    # for the current snapshot
                    snapshot_nsamp += samp_per_pkt

                    k += 1
                    j += 1

                # Perform some verifications before saving the snapshot
                try:
                    if snapshot_nsamp > nsamp_max_per_rec:
                        raise Exception("Total number of samples cannot exceed {1}, but {0} is found!".format(
                            snapshot_nsamp, nsamp_max_per_rec))

                    if SAMP_PER_SNAPSHOT != snapshot_nsamp:
                        raise Exception(
                            "Unexpected total number of samples in snapshot #{0}!".format(snapshot_id[i]))
                except:
                    message = print_exception()
                    task.exception(message)
                    data["v"][i, ] = CDFToFill()(data["v"].dtype.name)
                    data["e"][i, ] = CDFToFill()(data["e"].dtype.name)
                    data["b"][i, ] = CDFToFill()(data["b"].dtype.name)

    return data
