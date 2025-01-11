from libc.stdint cimport uint8_t
from libc.stdint cimport uint16_t

cdef class Header:
    cdef public uint8_t ccsds_version_number
    cdef public uint8_t packet_type
    cdef public uint8_t data_field_header_flag
    cdef public uint8_t process_id
    cdef public uint8_t packet_category
    cdef public uint8_t segmentation_grouping_flag
    cdef public uint16_t sequence_cnt
    cdef public uint16_t packet_length

    cpdef tuple to_tuple(Header self)
    cpdef dict to_dict(Header self)


cdef class TCHeader:
    cdef public uint8_t ccsds_secondary_header_flag
    cdef public uint8_t pus_version
    cdef public uint8_t ack_execution_completion
    cdef public uint8_t ack_execution_progress
    cdef public uint8_t ack_execution_start
    cdef public uint8_t ack_acceptance
    cdef public uint8_t service_type
    cdef public uint8_t service_subtype
    cdef public uint8_t source_id

    cpdef tuple to_tuple(TCHeader self)
    cpdef dict to_dict(TCHeader self)


cdef class TMHeader:
    cdef public uint8_t spare_1
    cdef public uint8_t pus_version
    cdef public uint8_t spare_2
    cdef public uint8_t service_type
    cdef public uint8_t service_subtype
    cdef public uint8_t destination_id
    cdef public tuple time

    cpdef tuple to_tuple(TMHeader self)
    cpdef dict to_dict(TMHeader self)
