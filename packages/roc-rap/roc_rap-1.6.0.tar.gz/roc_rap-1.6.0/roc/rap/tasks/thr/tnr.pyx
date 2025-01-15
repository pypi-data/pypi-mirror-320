import numpy as np
cimport numpy as np

from roc.rpl.packet_structure.data import Data
from roc.rpl.packet_structure.data cimport Data


DURATION = {
    (0, 0): 0.35,
    (0, 1): 0.21,
    (0, 2): 0.17,
    (0, 3): 0.16,
    (1, 0): 0.63,
    (1, 1): 0.39,
    (1, 2): 0.33,
    (1, 3): 0.31,
    (2, 0): 1.16,
    (2, 1): 0.74,
    (2, 2): 0.63,
    (2, 3): 0.6,
    (3, 0): 2.14,
    (3, 1): 1.35,
    (3, 2): 1.25,
    (3, 3): 1.15,
}


cpdef list tnr_dtype():
    """
    Numpy array dtype for the TNR L1 survey data.
    """
    # Name convention is lower case
    return [
        ("epoch", "float64"),
        ("scet", "float64"),
        ("acquisition_time", "uint32", 2),
        ("synchro_flag", "uint8"),
        ("quality_flag", "uint8"),
        ("quality_bitmask", "uint16"),
        ("sweep_num", "uint32"),
        ("measurement_duration", "float64"),
        ("ticks_nr", "int64"),
        ("delta_time", "float64"),
        ("survey_mode", "uint8"),
        ("calibration_level", "uint8"),
        ("average_nr", "uint8"),
        ("auto_cross_status", "uint8", 2),
        ("channel_status", "uint8", 2),
        ("front_end", "uint8"),
        ("sensor_config", "uint8", 2),
        ("rpw_status", "uint8", 15),
        ("temperature", "uint8", 4),
        ("tnr_band", "uint8"),
        ("agc1", "uint16"),
        ("agc2", "uint16"),
        ("frequency", "uint32", 32),
        ("auto1", "uint16", 32),
        ("auto2", "uint16", 32),
        ("cross_r", "uint16", 32),
        ("cross_i", "uint16", 32),
    ]


cpdef tuple tnr_setup(Data data, unsigned int start):
    """
    Return tuple of values from the TNR setup command.
    """
    cdef:
        unsigned char A
        unsigned char B
        unsigned char C
        unsigned char D
        unsigned char au
        unsigned char cr
        unsigned char av

    # read parameters
    a = data.u8(start, 7, 1)
    b = data.u8(start, 6, 1)
    c = data.u8(start, 5, 1)
    d = data.u8(start, 4, 1)
    au = data.u8(start, 3, 1)
    cr = data.u8(start, 2, 1)
    av = data.u8(start, 0, 2)

    return av, cr, au, d, c, b, a


cpdef tuple delta_times(Data data, unsigned int start):
    """
    Read delta times command.
    """
    cdef:
        long long a
        long long b
        long long c
        long long d

    a = <long long>data.u32(start, 0, 32)
    b = <long long>data.u32(start + 4, 0, 32)
    c = <long long>data.u32(start + 8, 0, 32)
    d = <long long>data.u32(start + 12, 0, 32)

    return a, b, c, d


cpdef tuple extract_band(
    unsigned char band,
    unsigned char ch1,
    unsigned char ch2,
    unsigned char auto,
    unsigned char cross,
    Data data,
    unsigned int offset,
    unsigned int bit_count,
):
    """
    Extract the band, returning fake data if not selected.
    """
    cdef:
        Py_ssize_t i
        unsigned short ch1_agc_value
        unsigned short ch2_agc_value
        np.ndarray[np.uint16_t, ndim=1] ch1_auto_value = np.zeros(32, dtype="uint16")
        np.ndarray[np.uint16_t, ndim=1] ch2_auto_value = np.zeros(32, dtype="uint16")
        np.ndarray[np.uint16_t, ndim=2] cross_value = np.zeros((32, 2), dtype="uint16")

    # By default, fill values with FILLVAL (see CDF ISTP standards)
    ch1_auto_value[:] = 65535
    ch2_auto_value[:] = 65535
    cross_value[:,:] = 65535

    # if band is activated
    if band == 1:
        # read the channel #1 first
        if ch1 == 0:
            ch1_agc_value = data.u16(
                offset + bit_count // 8,
                bit_count % 8,
                12,
            )
            bit_count += 12
            if auto == 1:
                for i in range(32):
                    ch1_auto_value[i] = data.u16(
                        offset + bit_count // 8,
                        bit_count % 8,
                        12,
                    )
                    bit_count += 12
        else:
            ch1_agc_value = 65535

        # Then read channel #2
        if ch2 == 0:
            ch2_agc_value = data.u16(
                offset + bit_count // 8,
                bit_count % 8,
                12,
            )
            bit_count += 12
            if auto == 1:
                for i in range(32):
                    ch2_auto_value[i] = data.u16(
                        offset + bit_count // 8,
                        bit_count % 8,
                        12,
                    )
                    bit_count += 12
        else:
            ch2_agc_value = 65535

        # if cross and all channels
        if cross == 1 and ch1 == 0 and ch2 == 0:
            for i in range(32):
                cross_value[i, 0] = data.u16(
                    offset + bit_count // 8,
                    bit_count % 8,
                    12,
                )
                cross_value[i, 1] = data.u16(
                    offset + (bit_count + 384) // 8,
                    (bit_count + 384) % 8,
                    12,
                )
                bit_count += 12
            bit_count += 384

    return (
        (
            (ch1_agc_value, ch1_auto_value),
            (ch2_agc_value, ch2_auto_value),
            cross_value,
        ), bit_count
    )


cpdef tuple extract_calibration_band(
    unsigned char band,
    unsigned char ch1,
    unsigned char ch2,
    unsigned char auto,
    unsigned char cross,
    Data data,
    unsigned int offset,
    unsigned int bit_count,
):
    """
    Extract the band, returning fake data if not selected.
    """
    cdef:
        Py_ssize_t i
        unsigned short ch1_value
        unsigned short ch2_value
        np.ndarray[np.uint16_t, ndim=1] ch1_auto_value = np.zeros(8, dtype="uint16")
        np.ndarray[np.uint16_t, ndim=1] ch2_auto_value = np.zeros(8, dtype="uint16")
        np.ndarray[np.uint16_t, ndim=2] cross_value = np.zeros((8, 2), dtype="uint16")

    # if band is activated
    if band == 1:
        # read the first channel
        if ch1 == 0:
            ch1_value = data.u16(
                offset + bit_count // 8,
                bit_count % 8,
                12,
            )
            bit_count += 12
            if auto == 1:
                for i in range(8):
                    ch1_auto_value[i] = data.u16(
                        offset + bit_count // 8,
                        bit_count % 8,
                        12,
                    )
                    bit_count += 12
        else:
            ch1_value = 0

        # second channel
        if ch2 == 0:
            ch2_value = data.u16(
                offset + bit_count // 8,
                bit_count % 8,
                12,
            )
            bit_count += 12
            if auto == 1:
                for i in range(8):
                    ch2_auto_value[i] = data.u16(
                        offset + bit_count // 8,
                        bit_count % 8,
                        12,
                    )
                    bit_count += 12
        else:
            ch2_value = 0

        # if cross and all channels
        if cross == 1 and ch1 == 0 and ch2 == 0:
            for i in range(8):
                cross_value[i, 0] = data.u16(
                    offset + bit_count // 8,
                    bit_count % 8,
                    12,
                )
                cross_value[i, 1] = data.u16(
                    offset + (bit_count + 96) // 8,
                    (bit_count + 96) % 8,
                    12,
                )
                bit_count += 12
            bit_count += 96

    return (
        (
            (ch1_value, ch1_auto_value),
            (ch2_value, ch2_auto_value),
            cross_value,
        ), bit_count
    )
