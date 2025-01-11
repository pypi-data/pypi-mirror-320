from roc.rpl.rice cimport crice
import logging

from libc.stdint cimport uint8_t
from libc.stdint cimport uint16_t
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from libc.stdint cimport int32_t
from cpython.mem cimport PyMem_Malloc
from cpython.mem cimport PyMem_Free
from roc.rpl.packet_structure.data cimport Data

__all__ = ["compress", "uncompress"]

logger = logging.getLogger(__name__)


class RiceException(Exception):
    """
    Exceptions for the RICE library.
    """



cdef class Compressor:
    cdef uint32_t* int_buffer
    cdef uint16_t* short_buffer
    cdef uint8_t* byte_buffer
    cdef uint32_t _buffer_size

    def __cinit__(Compressor self, uint32_t buffer_size=0x4000):
        self.buffer_size = buffer_size

    cpdef Data uncompress(
        Compressor self,
        Data data,
        uint32_t output_size,
    ):
        cdef:
            int32_t decompressedSize
            int32_t postProcessedSize
            int32_t buffer_int_size

        # check valid sizes
        if output_size > self._buffer_size:
            raise RiceException("Internal buffer too small for input")

        # decompress the data and get the size
        decompressedSize = crice.uncompress(
            # self.byte_buffer,
            data.data,
            data.size,
            self.int_buffer,
            output_size // 2,
        )
        if decompressedSize == -1:
            raise RiceException("Error uncompressing data")

        # post process the data
        postProcessedSize = crice.postprocessor(
            self.int_buffer,
            decompressedSize,
            self.short_buffer,
            crice.ESTIMATE_1D_H,
        )
        if postProcessedSize == -1:
            raise RiceException("Error post processing decompressed data")

        # compute byte size
        postProcessedSize = postProcessedSize * sizeof(uint16_t)

        return Data(
            (<uint8_t*>self.short_buffer)[:postProcessedSize],
            postProcessedSize,
        )

    cpdef Data compress(
        Compressor self,
        Data data,
    ):
        cdef:
            uint8_t* compressed
            int32_t result
            Py_ssize_t i
            int32_t preProcessedSize
            uint16_t* tmp

        # check sizes are correct with the chosen buffers
        if data.size // 2 > self._buffer_size:
            raise RiceException("Internal buffers too small for compression")

        # pre-processed data generation
        preProcessedSize = crice.preprocess(
            <uint16_t*>data.data,
            data.size // 2,
            self.int_buffer,
            crice.ESTIMATE_1D_H,
        )
        if preProcessedSize == -1:
            raise RiceException("Error pre-processing data before compression.")

        # compress the data
        result = crice.compress(
            self.int_buffer,
            preProcessedSize,
            self.byte_buffer,
            self._buffer_size,
        )
        if result == -1:
            raise RiceException("Error occurred while compressing data")
        if <uint32_t>result > self._buffer_size:
            raise RiceException(
                "Byte buffer too small for compression.\n" +
                "Buffer size: {0} bytes, compressed size: {1} bytes".format(
                    self._buffer_size,
                    result,
                )
            )

        # copy the result
        return Data(self.byte_buffer[:result], result)

    property buffer_size:
        def __get__(self):
            return self._buffer_size

        def __set__(self, buffer_size):
            cdef:
                Py_ssize_t i
            # store the new buffer size
            self._buffer_size = buffer_size

            # if memory already allocated, deallocate
            if self.int_buffer != NULL:
                PyMem_Free(self.int_buffer)
            if self.short_buffer != NULL:
                PyMem_Free(self.short_buffer)
            if self.byte_buffer != NULL:
                PyMem_Free(self.byte_buffer)

            # allocate buffers with the new size
            self.int_buffer = <uint32_t*> PyMem_Malloc(
                buffer_size * sizeof(uint32_t)
            )
            self.short_buffer = <uint16_t*> PyMem_Malloc(
                buffer_size * sizeof(uint16_t)
            )
            self.byte_buffer = <uint8_t*> PyMem_Malloc(
                buffer_size * sizeof(uint8_t)
            )
            for i in range(buffer_size):
                self.byte_buffer[i] = 0
                self.short_buffer[i] = 0
                self.int_buffer[i] = 0

        def __del__(self):
            # if memory already allocated, deallocate
            if self.int_buffer != NULL:
                PyMem_Free(self.int_buffer)
            if self.short_buffer != NULL:
                PyMem_Free(self.short_buffer)
            if self.byte_buffer != NULL:
                PyMem_Free(self.byte_buffer)

    def __dealloc__(self):
        del self.buffer_size
