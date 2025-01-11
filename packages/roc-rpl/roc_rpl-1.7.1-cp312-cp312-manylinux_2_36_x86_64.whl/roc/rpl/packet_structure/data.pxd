from libc.stdint cimport int8_t
from libc.stdint cimport uint8_t
from libc.stdint cimport int16_t
from libc.stdint cimport uint16_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint32_t
from .parameter cimport Parameter
from .header cimport TCHeader
from .header cimport TMHeader
from .header cimport Header

cdef extern from "type_conversion.h":
    int8_t to_signed_char(uint8_t x) nogil
    int16_t to_signed_short(uint16_t x) nogil
    int32_t to_signed_long(uint32_t x) nogil
    float to_float(uint32_t x) nogil


cdef class Data:
    cdef bytes ref
    cdef uint8_t* data
    cdef uint32_t size

    cpdef extract_parameter(self, Parameter parameter, uint32_t offset)
    cpdef Header extract_header(self)
    cpdef TMHeader extract_tm_header(self)
    cpdef TCHeader extract_tc_header(self)
    cpdef to_bytes(self)
    cdef int32_t i32(self, uint32_t start, uint32_t offset, uint32_t length) nogil
    cdef uint32_t u32(self, uint32_t start, uint32_t offset, uint32_t length) nogil
    cdef int16_t i16(self, uint32_t start, uint32_t offset, uint32_t length) nogil
    cdef uint16_t u16(self, uint32_t start, uint32_t offset, uint32_t length) nogil
    cdef int8_t i8(self, uint32_t start, uint32_t offset, uint32_t length) nogil
    cdef uint8_t u8(self, uint32_t start, uint32_t offset, uint32_t length) nogil
    cdef tuple time(self, uint32_t start, uint32_t offset, uint32_t length)
    cpdef tuple timep(self, uint32_t start, uint32_t offset, uint32_t length)
    cdef float f32(self, uint32_t start, uint32_t offset, uint32_t length) nogil
    cpdef int32_t i32p(self, uint32_t start, uint32_t offset, uint32_t length)
    cpdef uint32_t u32p(self, uint32_t start, uint32_t offset, uint32_t length)
    cpdef int16_t i16p(self, uint32_t start, uint32_t offset, uint32_t length)
    cpdef uint16_t u16p(self, uint32_t start, uint32_t offset, uint32_t length)
    cpdef int8_t i8p(self, uint32_t start, uint32_t offset, uint32_t length)
    cpdef uint8_t u8p(self, uint32_t start, uint32_t offset, uint32_t length)
    cpdef float f32p(self, uint32_t start, uint32_t offset, uint32_t length)
    cpdef tuple extract_parameters(self, Py_ssize_t offset, list parameters)
    cpdef tuple extract_block(self, Py_ssize_t offset, list parameters, uint32_t counter)
