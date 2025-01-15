import numpy as np

from poppy.core.tools.exceptions import print_exception
from roc.rpl.packet_structure.data import Data
from roc.rpl.packet_structure.data cimport Data

from roc.idb.converters.cdf_fill import fill_records as filler

# Size in bytes of one block in PA_THR_SP_DATA parameter of TM_THR_SCIENCE_SPECTRAL_POWER packet
BLOCK_SIZE = 8

cpdef decommute(group, task):
    cdef:
        Py_ssize_t i
    """ 
    Extract source_data blocks in TM_THR_SCIENCE_SPECTRAL_POWER packets
    """

    # get the number of TM_THR_SCIENCE_SPECTRAL_POWER packets
    packet_number = group["PA_THR_SP_DATA_CNT"].shape[0]

    # get the total number of records over all TM_THR_SCIENCE_SPECTRAL_POWER packets
    record_number = int(np.sum(group["PA_THR_SP_DATA_CNT"]) / 4.0)

    # create the array containing the data
    array = np.empty(record_number, dtype=create_dtype())

    # Initialize the array with excepted CDF FILLVAL values
    filler(array)

    # loop over TM_THR_SCIENCE_SPECTRAL_POWER packets
    counter = 0
    for i in range(packet_number):
        try:
            # Get acquisition time (CUC with coarse + fine + synchro flag)
            acquisition_time = group["PA_THR_ACQUISITION_TIME"][i]

            # Number of blocks of 16 bits for the current packet
            nblock = int(group["PA_THR_SP_DATA_CNT"][i])

            # transform the data into byte array
            # store because of the garbage collector removing reference while
            # processing in Cython
            byte = group[
                "PA_THR_SP_DATA"
            ][i][:nblock].byteswap().newbyteorder().tobytes()
            data = Data(byte, len(byte))

            # Number of blocks of 64 bits in the packet
            nblock_64 = int(nblock / 4.0)

            # init offset (in bytes)
            offset = 0

            # loop over blocks
            for j in range(nblock_64):
                # now extract the data
                array[counter], offset = extract_data(
                    data,
                    offset,
                )

                counter += 1

            # check offset size
            if offset != nblock_64 * BLOCK_SIZE:
                raise Exception("Analysis has failed for TM_THR_SCIENCE_SPECTRAL_POWER")

            # Add acquisition time fine part and synchro flag for the current packet
            array[counter-nblock_64]['fine'] = group["PA_THR_ACQUISITION_TIME"][i][1]
            array[counter-nblock_64]['synchro'] = group["PA_THR_ACQUISITION_TIME"][i][2]

        except:
            # continue if something wrong with the packet
            message = print_exception()
            task.exception(message)

    return array


cdef tuple extract_data(Data data, Py_ssize_t offset):
    """
    Extract the data and insert it into the data structure of the packet.
    """
    cdef:
        unsigned long coarse
        unsigned short agc
        unsigned short auto
        unsigned char index

    # read coarse time value
    coarse = data.u32(offset, 0, 32)

    # read agc value
    agc = data.u16(offset + 4, 0, 12)

    # read auto value
    auto = data.u16(offset + 5, 4, 12)

    # read index frequency
    index = data.u8(offset + 7, 0, 8)

    # compute the new offset in bytes for the block
    offset += BLOCK_SIZE

    # tuple of values to add them to the numpy array
    # Fine and synchro not provided (FILLVAL value)
    return (
        coarse, agc, auto, index, 65535, 255,
    ), offset


cpdef list create_dtype():
    """
    Create dtype of numpy for the special packet.
    """
    return [
        ("coarse", "uint32"),
        ("agc", "uint16"),
        ("auto", "uint16"),
        ("index", "uint8"),
        ("fine", "uint16"),
        ("synchro", "uint8"),
    ]
