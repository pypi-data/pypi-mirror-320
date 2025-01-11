from libc.stdint cimport uint32_t

cdef class Parameter:
    cdef public uint32_t byte
    cdef public uint32_t bit
    cdef public uint32_t group
    cdef public uint32_t block_size
    cdef public uint32_t counter
    cdef public uint32_t length
    cdef public double maximum
    cdef public str name
    cdef public str type
