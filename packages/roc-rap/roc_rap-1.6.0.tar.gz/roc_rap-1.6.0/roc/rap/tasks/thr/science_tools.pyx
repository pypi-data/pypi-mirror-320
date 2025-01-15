import numpy as np
cimport numpy as np

from roc.rpl.packet_structure.data import Data
from roc.rpl.packet_structure.data cimport Data


cpdef tuple rpw_status(Data data, unsigned int start):
    """
    Return tuple of values from the RPW status command.
    """
    cdef:
        unsigned char bias_on_off
        unsigned char lfr_on_off
        unsigned char tds_on_off
        unsigned char thr_on_off
        unsigned char ant1_on_off
        unsigned char ant2_on_off
        unsigned char ant3_on_off
        unsigned char scm_on_off
        unsigned char bias3
        unsigned char bias2
        unsigned char bias1
        unsigned char hv
        unsigned char m_lfr
        unsigned char c_lfr
        unsigned char m_tds
        unsigned int tmp

    tmp = start + 1

    bias_on_off = data.u8(tmp, 7, 1)
    lfr_on_off = data.u8(tmp, 6, 1)
    tds_on_off = data.u8(tmp, 5, 1)
    thr_on_off = data.u8(tmp, 4, 1)
    ant1_on_off = data.u8(tmp, 3, 1)
    ant2_on_off = data.u8(tmp, 2, 1)
    ant3_on_off = data.u8(tmp, 1, 1)
    scm_on_off = data.u8(tmp, 0, 1)

    bias3 = data.u8(start, 7, 1)
    bias2 = data.u8(start, 6, 1)
    bias1 = data.u8(start, 5, 1)
    hv = data.u8(start, 4, 1)
    m_lfr = data.u8(start, 3, 1)
    c_lfr = data.u8(start, 2, 1)
    m_tds = data.u8(start, 1, 1)

    return (
        m_tds, c_lfr, m_lfr, hv, bias1, bias2, bias3, scm_on_off,
        ant3_on_off, ant2_on_off, ant1_on_off, thr_on_off, tds_on_off,
        lfr_on_off, bias_on_off
    )


cpdef tuple do_analysis(Data data, unsigned int start):
    """
    Return tuple of values from the DoAnalysis command.
    """
    cdef:
        unsigned char ch1
        unsigned char ch2
        unsigned char eos
        unsigned char mod
        unsigned char it

    # read parameters
    ch1 = data.u8(start, 7, 1)
    ch2 = data.u8(start, 6, 1)
    eos = data.u8(start, 5, 1)
    mod = data.u8(start, 4, 1)
    it = data.u8(start, 0, 4)

    return it, mod, eos, ch2, ch1


cpdef tuple input_setup(Data data, unsigned int start):
    """
    Return a tuple of values from the input setup command.
    """
    cdef:
        unsigned char sensor_tnr_1
        unsigned char sensor_tnr_2
        unsigned char fe
        unsigned int tmp

    tmp = start + 1

    # read parameters
    # N.B. Bit order of tnr1 and tnr2 sensors
    # are inverted w.r.t. the doc.
    # (RPW-SYS-MEB-THR-TN-000914-LES_Iss03_Rev04.pdf)
    sensor_tnr_2 = data.u8(tmp, 0, 4)
    sensor_tnr_1 = data.u8(tmp, 4, 4)
    fe = data.u16(start, 6, 2)

    return fe, sensor_tnr_2, sensor_tnr_1


cpdef tuple temperatures_command(Data data, unsigned int start):
    """
    Read temperatures command block from micro command.
    """
    cdef:
        unsigned char analog
        unsigned char ant1
        unsigned char ant2
        unsigned char ant3

    analog = data.u8(start, 0, 8)
    ant1 = data.u8(start + 1, 0, 8)
    ant2 = data.u8(start + 2, 0, 8)
    ant3 = data.u8(start + 3, 0, 8)

    return analog, ant1, ant2, ant3


cpdef tuple voltages(Data data, unsigned int start):
    """
    Read voltages from the command.
    """
    cdef:
        unsigned char minus5
        unsigned char plus5
        unsigned char plus12

    minus5 = data.u8(start, 0, 8)
    plus5 = data.u8(start + 1, 0, 8)
    plus12 = data.u8(start + 2, 0, 8)

    return minus5, plus5, plus12


cpdef list voltages_dtype():
    """
    Return voltages dtype.
    """
    return [
        ("minus5", "uint8"), ("plus5", "uint8"), ("plus12", "uint8")
    ]


cpdef list temperatures_dtype():
    """
    Return temperatures dtype.
    """
    return [
        ("analog", "uint8"),
        ("ant1", "uint8"),
        ("ant2", "uint8"),
        ("ant3", "uint8"),
    ]


cpdef list rpw_status_dtype():
    """
    Return the RPW status command dtype.
    """
    return [
        ("m_tds", "uint8"), ("c_lfr", "uint8"), ("m_lfr", "uint8"),
        ("hv", "uint8"), ("bias1", "uint8"), ("bias2", "uint8"),
        ("bias3", "uint8"), ("scm_on_off", "uint8"),
        ("ant3_on_off", "uint8"), ("ant2_on_off", "uint8"),
        ("ant1_on_off", "uint8"), ("thr_on_off", "uint8"),
        ("tds_on_off", "uint8"), ("lfr_on_off", "uint8"),
        ("bias_on_off", "uint8")
    ]


cpdef list input_setup_dtype():
    return [
        ("fe", "uint8"), ("sensor_tnr_2", "uint8"), ("sensor_tnr_1", "uint8")
    ]


cpdef list do_analysis_dtype():
    return [
        ("it", "uint8"), ("mod", "uint8"), ("eos", "uint8"),
        ("ch2", "uint8"), ("ch1", "uint8"),
    ]

cpdef unsigned int average_nr(unsigned int average_index):
    average_map = [16, 32, 64, 128]
    return average_map[average_index]


