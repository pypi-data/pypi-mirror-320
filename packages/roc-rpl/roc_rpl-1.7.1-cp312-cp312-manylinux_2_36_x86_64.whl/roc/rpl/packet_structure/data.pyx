import numpy as np
cimport numpy as np

from libc.stdint cimport int8_t
from libc.stdint cimport uint8_t
from libc.stdint cimport int16_t
from libc.stdint cimport uint16_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint32_t
from cpython cimport bool
from .data cimport to_float
from .data cimport to_signed_char
from .data cimport to_signed_short
from .data cimport to_signed_long
from .parameter cimport Parameter
from .header cimport TCHeader
from .header cimport TMHeader
from .header cimport Header

cpdef tuple header_foot_offset(uint8_t packet_type):
    """
    Get offset according to packet type.
    All packets have an offset of the application and source data at a
    different position according to the type of the packet, so the header
    offset take of this.
    Moreover, TC commands have a spare not defined as a parameter at the end
    of the packet called CRC, of 2 bytes size, so we had it for TC packets
    """
    cdef:
        Py_ssize_t header_offset
        Py_ssize_t foot_offset

    # If TC packet
    if packet_type == 1:
        header_offset = 10
        foot_offset = 2
    # If TM packet
    else:
        header_offset = 16
        foot_offset = 0

    return header_offset, foot_offset

cdef class Data:
    """
    Wrapper class around bytes array to extract simple values, headers,
    parameters and block parameters.
    """
    def __cinit__(Data self, bytes data, uint32_t size):
        self.ref = data
        self.data = <uint8_t*> self.ref
        self.size = size

    def __str__(self):
        return (
                "Data(size=" + str(self.size) +
                ", buf=" + str(self.data[:self.size]) + ")"
        )

    property data_size:
        def __get__(self):
            return self.size

        def __set__(self, size):
            self.size = size

    property data_buffer:
        def __get__(self):
            return <bytes> self.data[:self.size]

    cpdef to_bytes(Data self):
        """
        Return the data into a bytearray that can be manipulated directly in
        Python without using C code.
        """
        return bytes(self.data[:self.size])

    cpdef extract_parameter(Data self, Parameter parameter, uint32_t offset):
        """
        Given a parameter, extract its value at the given offset.
        """
        # get the value of the parameter
        if parameter.type == "uint8":
            return self.u8(
                parameter.byte + offset,
                parameter.bit,
                parameter.length,
            )
        elif parameter.type == "uint16":
            return self.u16(
                parameter.byte + offset,
                parameter.bit,
                parameter.length,
            )
        elif parameter.type == "uint32":
            return self.u32(
                parameter.byte + offset,
                parameter.bit,
                parameter.length,
            )
        elif parameter.type == "int8":
            return self.i8(
                parameter.byte + offset,
                parameter.bit,
                parameter.length,
            )
        elif parameter.type == "int16":
            return self.i16(
                parameter.byte + offset,
                parameter.bit,
                parameter.length,
            )
        elif parameter.type == "int32":
            return self.i32(
                parameter.byte + offset,
                parameter.bit,
                parameter.length,
            )
        elif parameter.type == "float32":
            return self.f32(
                parameter.byte + offset,
                parameter.bit,
                parameter.length,
            )
        elif parameter.type == "time":
            return self.time(
                parameter.byte + offset,
                parameter.bit,
                parameter.length,
            )

    cpdef Header extract_header(Data self):
        """
        Extract header information from the packet data.
        """
        header = Header(
            ccsds_version_number=self.u8(0, 0, 3),
            packet_type=self.u8(0, 3, 1),
            data_field_header_flag=self.u8(0, 4, 1),
            process_id=self.u8(0, 5, 7),
            packet_category=self.u8(1, 4, 4),
            segmentation_grouping_flag=self.u8(2, 0, 2),
            sequence_cnt=self.u16(2, 2, 14),
            packet_length=self.u16(4, 0, 16),
        )
        return header

    cpdef TCHeader extract_tc_header(Data self):
        """
        Extract TC data field header.
        """
        header = TCHeader(
            ccsds_secondary_header_flag=self.u8(
                6, 0, 1
            ),
            pus_version=self.u8(6, 1, 3),
            ack_execution_completion=self.u8(6, 4, 1),
            ack_execution_progress=self.u8(6, 5, 1),
            ack_execution_start=self.u8(6, 6, 1),
            ack_acceptance=self.u8(6, 7, 1),
            service_type=self.u8(7, 0, 8),
            service_subtype=self.u8(8, 0, 8),
            source_id=self.u8(9, 0, 8),
        )
        return header

    cpdef TMHeader extract_tm_header(Data self):
        """
        Extract TM data field header.
        """
        header = TMHeader(
            spare_1=self.u8(6, 0, 1),
            pus_version=self.u8(6, 1, 3),
            spare_2=self.u8(6, 4, 4),
            service_type=self.u8(7, 0, 8),
            service_subtype=self.u8(8, 0, 8),
            destination_id=self.u8(9, 0, 8),
            time=self.time(10, 0, 48),
        )
        return header

    cpdef float f32p(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ):
        return self.f32(start, offset, length)

    cdef float f32(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ) nogil:
        cdef:
            float result
            uint32_t tmp

        # get the value with uint32_t
        tmp = self.u32(start, offset, length)

        result = to_float(tmp)
        return result

    cpdef uint32_t u32p(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ):
        return self.u32(
            start,
            offset,
            length,
        )

    cdef uint32_t u32(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ) nogil:
        """
        Extract an uint32_t from a byte array, with the starting byte in
        the array, the offset in bit from the left most position in the array
        and a bit length of length.
        """
        cdef:
            uint32_t byte1
            uint32_t byte2
            uint32_t byte3
            uint32_t result

        # compute the first two bytes from the offset
        byte1 = <uint32_t> self.u8(start + 3, offset, 8)
        byte2 = <uint32_t> self.u8(start + 2, offset, 8)
        byte3 = <uint32_t> self.u8(start + 1, offset, 8)
        result = <uint32_t> self.u8(start, offset, 8)

        # compute the short integer
        result = result << 24
        byte3 = byte3 << 16
        byte2 = byte2 << 8
        result = byte1 | byte2 | byte3 | result

        # short it by the length
        result = result >> (32 - length)
        return result

    cpdef int32_t i32p(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ):
        cdef:
            int32_t result
        result = self.i32(start, offset, length)
        return result

    cdef int32_t i32(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ) nogil:
        cdef:
            uint32_t tmp
            int32_t result
        # get as unsigned
        tmp = self.u32(start, offset, length)

        # reinterpret as signed
        result = to_signed_long(tmp)
        return result

    cpdef uint16_t u16p(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ):
        return self.u16(
            start,
            offset,
            length,
        )

    cdef uint16_t u16(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ) nogil:
        cdef:
            uint16_t byte2
            uint16_t result

        # compute the first two bytes from the offset
        byte2 = <uint16_t> self.u8(start + 1, offset, 8)
        result = <uint16_t> self.u8(start, offset, 8)

        # compute the short integer
        result = result << 8
        result = byte2 | result

        # short it by the length
        result = result >> (16 - length)
        return result

    cpdef int16_t i16p(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ):
        return self.i16(start, offset, length)

    cdef int16_t i16(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ) nogil:
        cdef:
            uint16_t tmp
            int16_t result
        tmp = self.u16(start, offset, length)
        result = to_signed_short(tmp)
        return result

    cpdef uint8_t u8p(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length
    ):
        return self.u8(start, offset, length)

    cdef uint8_t u8(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length
    ) nogil:
        """
        We store the intermediate result of shifting the bits because cython is
        doing an implicit conversion to an 'higher' size integer if the shift
        is bigger than a byte.
        """
        cdef:
            uint8_t result
            uint8_t tmp

        # start by reading the entire byte
        with nogil:
            result = self.data[start] << offset
            tmp = self.data[start + 1] >> (8 - offset)
            result = result | tmp

            # and hide the last part
            result = result >> (8 - length)
        return result

    cpdef int8_t i8p(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length
    ):
        return self.i8(start, offset, length)

    cdef int8_t i8(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length
    ) nogil:
        """
        We store the intermediate result of shifting the bits because cython is
        doing an implicit conversion to an 'higher' size integer if the shift
        is bigger than a byte.

        Do not do a lot of smart things with the sign bit since if we want to
        read a signed value, we need to read 8 bit, so the length should be 8.
        So I think that it should be always used with the length equals to 8.
        """
        cdef:
            uint8_t tmp
            int8_t result

        tmp = self.u8(start, offset, length)
        result = to_signed_char(tmp)
        return result

    cdef tuple time(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length,
    ):
        cdef:
            uint32_t coarse
            uint16_t fine
            uint8_t flag

        # get the flag
        flag = self.u8(start, 0, 1)

        # read the coarse part
        coarse = self.u32(start, 1, 31)

        # read the fine part
        fine = self.u16(start + 4, 0, 16)

        return (coarse, fine, flag)


    cpdef tuple timep(
            Data self,
            uint32_t start,
            uint32_t offset,
            uint32_t length
    ):
        return self.time(start, offset, length)


    cpdef tuple extract_block(
            Data self,
            Py_ssize_t offset,
            list parameters,
            uint32_t counter
    ):
        cdef:
            Py_ssize_t j, k
            Py_ssize_t limit
            uint32_t group_size
            uint32_t block_size
            list buff
            list values

            Parameter block_parameter

        # init the list of parameters and their data
        values = []

        # size of the group
        group_size = parameters[0].group

        # empty list, a list of values for each parameter in the block, since
        # multiple values are present for a parameter
        buff = [[] for x in range(group_size)]

        # compute the block offset (the block size in bit, including the any spare
        # present in the block, but not present in the parameter list)
        block_size = parameters[0].block_size

        # loop over parameters for the block size
        for j in range(counter):
            # loop over parameters in group
            for k in range(group_size):
                # get the parameter
                block_parameter = parameters[k]

                # get the value of the parameter
                value = self.extract_parameter(block_parameter, offset)

                # add the value to the buffer
                buff[k].append(value)

            # add the block to the offset
            offset += block_size

        # since the byte position of parameters from the database already
        # take into account one block size for their definition, we need
        # to delete the last offset of the parameters to be correctly
        # aligned with the size provided by the packet himself
        offset -= block_size

        # add values to the result
        for k in range(group_size):
            # get current parameter
            block_parameter = parameters[k]

            # create data array with the good type
            results = np.empty(
                counter,
                dtype=block_parameter.type,
            )

            # load the buffer data in the result array
            results[:] = buff[k][:]

            # add data to values
            values.append(results)

        return values, offset, group_size

    cpdef tuple extract_parameters(
            Data self,
            Py_ssize_t offset,
            list parameters,
    ):
        """
        Given the parameters to extract, get them from byte data, and take into
        account the blocks.
        """
        cdef:
            Py_ssize_t i

            uint32_t nmax
            uint32_t group_size
            uint32_t counter_value
            uint32_t data_field_offset

            bool in_block

            list values
            list buff

            Parameter block_parameter
            Parameter last_param

        # init some variables
        values = []

        # loop on parameters
        i = 0
        nmax = len(parameters)
        while (i < nmax):
            # check we are in block
            in_block = parameters[i].group > 0

            # if not in a block, read the parameters with the given offset (header
            # and eventually blocks of data)
            if not in_block:
                # store the last parameter if not in block and the value
                counter_parameter = parameters[i]

                # get the value of the parameter
                value = self.extract_parameter(parameters[i], offset)

                # add the value to the result
                values.append(value)

                # next parameter
                i += 1

            else:
                # case where the counter is from a parameter, and is by definition
                # the last extracted value
                if parameters[i].counter == 0:
                    # the last stored value is the counter
                    counter_value = value

                    # compute the maximal value of the array, depending on the
                    # maximal value of the counter
                    maximum = counter_parameter.maximum
                # case where the value of the counter is hardcoded in the IDB, the
                # IDB database of the store this information in the counter field
                # of the parameter, and the counter and maximum are the same
                else:
                    counter_value = parameters[i].counter
                    maximum = parameters[i].counter

                # check the data size is compatible with expected limits from
                # the IDB definition
                if counter_value > maximum:
                    raise RPLDecommuteError(f"Bad value {counter_value} for counter parameter {counter_parameter.name} "
                                            f"with maximum {maximum}")

                # extract the block data from the information of parameters
                buff, offset, group_size = self.extract_block(
                    offset,
                    parameters[i:],
                    counter_value,
                )

                # add values for block into the values container
                values += buff

                # increment parameters
                i += group_size

        return tuple(values), offset


class RPLDecommuteError(Exception):
    pass
