import numpy as np
cimport numpy as np

from libc.stdint cimport uint8_t
from libc.stdint cimport uint16_t
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

from poppy.core.logger import logger

from roc.rpl.time import Time
from roc.idb.converters.cdf_fill import fill_records

from roc.rap.tasks.tds.utils import group

from roc.rap.tasks.utils import sort_data

__all__ = ["HIST2D", "set_hist2d"]

# Numpy array dtype for TDS histo2D L1 survey data
# Name convention is lower case

HIST2D = [
    ("epoch", "uint64"),
    ("scet", "float64"),
    ("acquisition_time", ("uint32", 2)),
    ("synchro_flag", "uint8"),
    ("quality_flag", "uint8"),
    ("quality_bitmask", "uint16"),
    ("survey_mode", "uint8"),
    ("bia_status_info", ("uint8", 6)),
    ("channel_status_info", ("uint8", 4)),
    ("sampling_rate", "float32"),
    ("input_config", "uint32"),
    ("snapshot_len", "uint8"),
    ("hist2d_id", "uint8"),
    ("hist2d_params", "uint8"),
    ("hist2d_axis1", "uint8"),
    ("hist2d_axis2", "uint8"),
    ("hist2d_col_time", "uint16"),
    ("hist2d_bins1", "uint8"),
    ("hist2d_bins2", "uint8"),
    ("hist2d_tot_pts", "uint16"),
    ("hist2d_counts", ("uint16", (128, 128))),
]

# TDS HIST2D sampling rate in Hz
SAMPLING_RATE_HZ = [65534.375, 131068.75, 262137.5, 524275., 2097100.]

cpdef set_hist2d(l0, task):
    cdef:
        uint64_t size
        uint64_t index
        uint64_t packet
        uint64_t grp
        uint16_t data_space
        uint16_t data_space_current
        uint16_t matrix_size
        uint16_t nx, ny

    # name of the packet
    name = "TM_TDS_SCIENCE_NORMAL_HIST2D"
    logger.debug("Get data for " + name)

    # get the HIST2D packet data
    if name in l0["TM"]:
        tm = l0["TM"][name]["source_data"]
    else:
        # rest of the code inside the with statement will not be called
        return np.empty(
            0,
            dtype=HIST2D,
        )

    # Sort input packets by ascending acquisition times and hist2D group number
    tm, __ = sort_data(tm, (
        tm["PA_TDS_ACQUISITION_TIME"][:,1],
        tm["PA_TDS_ACQUISITION_TIME"][:,0],
                    ))

    # get the size of the data from the number of groups
    groups, size = group(tm["PA_TDS_HIST2D_PKT_NR"][:])

    # create the data array with good size
    data = np.zeros(size, dtype=HIST2D)
    fill_records(data)

    # get the number of packets
    size = tm["PA_TDS_ACQUISITION_TIME"].shape[0]

    # fake current group for start
    grp = -1

    # loop over packets
    with nogil:
        while (packet < size):
            with gil:
                # if the group as changed
                if groups[packet] != grp:
                    # change the current group
                    grp = groups[packet]

                    # make the initialization of the data

                    # Time variable
                    data["epoch"][grp] = Time().obt_to_utc(tm[
                        "PA_TDS_ACQUISITION_TIME"
                    ][packet, :2].reshape([1, 2]), to_tt2000=True)
                    data["acquisition_time"][grp, :] = tm[
                        "PA_TDS_ACQUISITION_TIME"
                    ][packet, :2]
                    data["synchro_flag"][grp] = tm["PA_TDS_ACQUISITION_TIME"][
                        packet,
                        2,
                    ]

                    # scet
                    data["scet"][grp] = Time.cuc_to_scet(data["acquisition_time"][grp, :])


                    # bias info
                    data["bia_status_info"][grp, :] = (
                        tm["PA_BIA_MODE_MUX_SET"][packet],
                        tm["PA_BIA_MODE_HV_ENABLED"][packet],
                        tm["PA_BIA_MODE_BIAS1_ENABLED"][packet],
                        tm["PA_BIA_MODE_BIAS2_ENABLED"][packet],
                        tm["PA_BIA_MODE_BIAS3_ENABLED"][packet],
                        tm["PA_BIA_ON_OFF"][packet],
                        )

                    data["channel_status_info"][grp, :] = (
                        tm["PA_TDS_STAT_ADC_CH1"][packet],
                        tm["PA_TDS_STAT_ADC_CH2"][packet],
                        tm["PA_TDS_STAT_ADC_CH3"][packet],
                        tm["PA_TDS_STAT_ADC_CH4"][packet],
                    )

                    # Survey mode (always normal here == 3)
                    data["survey_mode"][grp] = 3

                    # sampling rate
                    data["sampling_rate"][grp] = SAMPLING_RATE_HZ[tm["PA_TDS_STAT_SAMP_RATE"][packet]]

                    # input config
                    data["input_config"][grp] = tm["PA_TDS_SWF_HF_CH_CONF"][packet]

                    # hist parameters
                    data["snapshot_len"] = tm["PA_TDS_SNAPSHOT_LEN"][packet]
                    data["hist2d_id"][grp] = tm["PA_TDS_SC_HIST2D_ID"][packet]
                    data["hist2d_params"][grp] = tm["PA_TDS_SC_HIST2D_PARAMS"][packet]
                    data["hist2d_axis1"][grp] = tm["PA_TDS_SC_HIST2D_PAR1_AXIS"][packet]
                    data["hist2d_axis2"][grp] = tm["PA_TDS_SC_HIST2D_PAR2_AXIS"][packet]
                    data["hist2d_bins1"][grp] = tm["PA_TDS_SC_HIST2D_PAR1_BINS"][packet]
                    data["hist2d_bins2"][grp] = tm["PA_TDS_SC_HIST2D_PAR2_BINS"][packet]
                    data["hist2d_col_time"][grp] = tm[
                        "PA_TDS_SC_HIST2D_COLL_TIME"
                    ][packet]
                    data["hist2d_tot_pts"][grp] = tm[
                        "PA_TDS_SC_HIST2D_TOT_POINTS"
                    ][packet]

                    # size of the matrix for counts
                    nx = data["hist2d_bins1"][grp]
                    ny = data["hist2d_bins2"][grp]
                    matrix_size = nx * ny
                    logger.debug(
                        "Matrix size for packet {0} is {1}".format(
                            packet,
                            matrix_size,
                        )
                    )

                    # create the memory space for the count matrix
                    matrix = np.zeros(matrix_size, dtype="uint16")

                    # compute the space for the data
                    if (
                        tm["PA_TDS_HIST2D_PKT_NR"][packet] ==
                        (tm["PA_TDS_HIST2D_PKT_CNT"][packet] - 1)
                    ):
                        # this is the last packet, all other are missing so the size of
                        # the data space is the one of the matrix minius the size of
                        # the data of this packet
                        data_space = (
                            matrix_size - tm["PA_TDS_SC_HIST2D_DATA_NR"][packet]
                        ) // tm["PA_TDS_HIST2D_PKT_CNT"][packet]
                    else:
                        # the size can be read directly from the packet because all
                        # except the last one have the same size
                        data_space = tm["PA_TDS_SC_HIST2D_DATA_NR"][packet]
                    logger.debug(
                        "Data space from packet number {0} is {1}".format(
                            packet,
                            data_space,
                        )
                    )

                # for each packet add the data
                # get the index in the snapshot of the data
                index = tm["PA_TDS_HIST2D_PKT_NR"][packet] - 1

                # get the space taken on the matrix for this data
                data_space_current = tm["PA_TDS_SC_HIST2D_DATA_NR"][packet]
                logger.debug(
                    "Packet index in snapshot: {0} for packet {1} & chunk {2}".format(
                        index,
                        packet,
                        data_space,
                    )
                )

                # fill the matrix in part with the data
                matrix[
                    index * data_space: index * data_space + data_space_current
                ] = tm["PA_TDS_SC_HIST2D_DATA"][packet][:data_space_current]

                # if last packet, copy the data to the structure
                if index == (tm["PA_TDS_HIST2D_PKT_CNT"][packet] - 1):
                    data["hist2d_counts"][grp][:nx, :ny] = matrix.reshape(
                        (nx, ny)
                    )[:, :]

                # increment the packet
                packet += 1



    return data
