import numpy as np
cimport numpy as np

from roc.rpl.packet_structure.data import Data
from roc.rpl.packet_structure.data cimport Data

cpdef unsigned long compute_tempo(unsigned long frequency):
    """
    Return the time for measurement of the frequency in millisecond.
    """
    cdef:
        unsigned long tempo

    tempo = 11
    if frequency > 16000:
        tempo += 19
        return tempo
    if frequency > 12000:
        tempo += 11
        return tempo
    if frequency > 7000:
        tempo += 6
        return tempo
    return tempo

cpdef unsigned short hfr_band_index(str band):
    cdef:
        unsigned short band_index
    if band == "hf1":
        band_index = 1
    elif band == "hf2":
        band_index = 2
    else:
        raise Exception("Invalid HFR band name: {0}".format(band))

    return band_index

cpdef unsigned long compute_frequency(
    unsigned short init_frequency,
    unsigned short step,
    unsigned long hf1_step,
    unsigned long hf1_number,
    unsigned long hf2_step,
    str band,
):
    cdef:
        unsigned long number

    # compute the start frequency
    number = 436 + init_frequency

    # hf1 band
    if band == "hf1":
        number += step * hf1_step

    # hf2 band
    if band == "hf2":
        number += (hf1_number - 1) * hf1_step
        number += (step + 1) * hf2_step

    # compute the frequency in kHz from the formula given in the TNR/HFR
    # software user manual
    return 375 + 50 * (number - 436)


cpdef list hfr_dtype():
    """
    Numpy array dtype for the HFR L1 survey data.
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
        ("sample_time", "float64"),
        ("ticks_nr", "int64"),
        ("delta_time", "float64"),
        ("sweep_mode", "uint8"),
        ("survey_mode", "uint8"),
        ("channel_status", "uint8", 2),
        ("calibration_level", "uint8"),
        ("average_nr", "uint8"),
        ("front_end", "uint8"),
        ("sensor_config", "uint8", 2),
        ("rpw_status", "uint8", 15),
        ("temperature", "uint8", 4),
        ("hfr_band", "uint8"),
        ("frequency", "uint16"),
        ("agc1", "uint16"),
        ("agc2", "uint16"),
    ]


cpdef tuple delta_times(Data data, unsigned int start):
    """
    Read delta times command.
    """
    cdef:
        long long hf1
        long long hf2

    hf1 = <long long>data.u32(start, 0, 32)
    hf2 = <long long>data.u32(start + 4, 0, 32)

    return hf1, hf2


cpdef tuple hfr_sweep_setup (Data data, unsigned int start):
    """
    Return tuple of values from the HFR sweep setup command.
    """
    cdef:
        unsigned char hf1_size
        unsigned short hf1_number
        unsigned char hf2_size
        unsigned short hf2_number

    # read parameters
    hf1_size = data.u8(start + 3, 4, 4)
    hf1_number = data.u16(start + 2, 3, 9)
    hf2_size = data.u8(start + 1, 7, 4)
    hf2_number = data.u16(start, 6, 9)

    return hf2_number, hf2_size, hf1_number, hf1_size


cpdef tuple hfr_setup(Data data, unsigned int start):
    """
    Return tuple of values from the HFR setup command.
    """
    cdef:
        unsigned char av
        unsigned char hf1
        unsigned char hf2
        unsigned short initial_frequency
        unsigned char sw
        unsigned int tmp

    tmp = start + 1

    # read parameters
    av = data.u8(tmp, 6, 2)
    hf1 = data.u8(tmp, 5, 1)
    hf2 = data.u8(tmp, 4, 1)
    initial_frequency = data.u16(start, 3, 9)
    sw = data.u8(start, 2, 1)

    return sw, initial_frequency, hf2, hf1, av

cpdef tuple extract_band(
    unsigned char ch,
    unsigned char band1,
    unsigned char band2,
    unsigned short n1,
    unsigned short n2,
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
        np.ndarray[np.uint16_t, ndim=1] band1_value = np.zeros(512, dtype="uint16")
        np.ndarray[np.uint16_t, ndim=1] band2_value = np.zeros(512, dtype="uint16")

    # if channel is activated
    if ch == 1:
        # read the first band
        if band1 == 1:
            for i in range(n1):
                band1_value[i] = data.u16(
                    offset + bit_count // 8,
                    bit_count % 8,
                    12,
                )
                bit_count += 12

        # second band
        if band2 == 1:
            for i in range(n2):
                band2_value[i] = data.u16(
                    offset + bit_count // 8,
                    bit_count % 8,
                    12,
                )
                bit_count += 12

    return (
        (
            band1_value, band2_value
        ), bit_count
    )
