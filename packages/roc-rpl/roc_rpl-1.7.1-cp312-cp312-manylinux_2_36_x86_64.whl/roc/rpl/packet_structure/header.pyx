cdef class Header:
    def __cinit__(
        Header self,
        uint8_t ccsds_version_number,
        uint8_t packet_type,
        uint8_t data_field_header_flag,
        uint8_t process_id,
        uint8_t packet_category,
        uint8_t segmentation_grouping_flag,
        uint16_t sequence_cnt,
        uint16_t packet_length,
    ):
        self.ccsds_version_number = ccsds_version_number
        self.packet_type = packet_type
        self.data_field_header_flag = data_field_header_flag
        self.process_id = process_id
        self.packet_category = packet_category
        self.segmentation_grouping_flag = segmentation_grouping_flag
        self.sequence_cnt = sequence_cnt
        self.packet_length = packet_length

    cpdef tuple to_tuple(Header self):
        """
        Return a tuple of the values of the header.
        """
        return (
            self.ccsds_version_number,
            self.packet_type,
            self.data_field_header_flag,
            self.process_id,
            self.packet_category,
            self.segmentation_grouping_flag,
            self.sequence_cnt,
            self.packet_length,
        )

    cpdef dict to_dict(Header self):
        """
        Return a dictionary of the values of the header.
        """
        return {
            'ccsds_version_number': self.ccsds_version_number,
            'packet_type': self.packet_type,
            'data_field_header_flag': self.data_field_header_flag,
            'process_id': self.process_id,
            'packet_category': self.packet_category,
            'segmentation_grouping_flag': self.segmentation_grouping_flag,
            'sequence_cnt': self.sequence_cnt,
            'packet_length': self.packet_length,
        }


    def __repr__(Header self):
        return (
            "Header(" +
            "ccsds_version_number={0}, ".format(self.ccsds_version_number) +
            "packet_type={0}, ".format(self.packet_type) +
            "data_field_header_flag={}, ".format(self.data_field_header_flag) +
            "process_id={0}, ".format(self.process_id) +
            "packet_category={0}, ".format(self.packet_category) +
            "segmentation_grouping_flag={0}, ".format(
                self.segmentation_grouping_flag
            ) +
            "sequence_cnt={0}, ".format(self.sequence_cnt) +
            "packet_length={0})".format(self.packet_length)
        )


cdef class TCHeader:
    def __cinit__(
        TCHeader self,
        uint8_t ccsds_secondary_header_flag,
        uint8_t pus_version,
        uint8_t ack_execution_completion,
        uint8_t ack_execution_progress,
        uint8_t ack_execution_start,
        uint8_t ack_acceptance,
        uint8_t service_type,
        uint8_t service_subtype,
        uint8_t source_id,
    ):
        self.ccsds_secondary_header_flag = ccsds_secondary_header_flag
        self.pus_version = pus_version
        self.ack_execution_completion = ack_execution_completion
        self.ack_execution_progress = ack_execution_progress
        self.ack_execution_start = ack_execution_start
        self.ack_acceptance = ack_acceptance
        self.service_type = service_type
        self.service_subtype = service_subtype
        self.source_id = source_id

    cpdef tuple to_tuple(TCHeader self):
        """
        Return the header with tuple.
        """
        return (
            self.ccsds_secondary_header_flag,
            self.pus_version,
            self.ack_execution_completion,
            self.ack_execution_progress,
            self.ack_execution_start,
            self.ack_acceptance,
            self.service_type,
            self.service_subtype,
            self.source_id,
        )

    cpdef dict to_dict(TCHeader self):
        """
        Return the header with dictionary.
        """
        return {
            'ccds_secondary_header_flag': self.ccsds_secondary_header_flag,
            'pus_version': self.pus_version,
            'ack_execution_completion': self.ack_execution_completion,
            'ack_execution_progress': self.ack_execution_progress,
            'ack_execution_start': self.ack_execution_start,
            'ack_acceptance': self.ack_acceptance,
            'service_type': self.service_type,
            'service_subtype': self.service_subtype,
            'source_id': self.source_id,
        }

    def __repr__(TCHeader self):
        return (
            "TCHeader(" +
            "ccsds_secondary_header_flag={0},".format(
                self.ccsds_secondary_header_flag
            ) +
            "pus_version={0},".format(self.pus_version) +
            "ack_execution_completion={0},".format(
                self.ack_execution_completion
            ) +
            "ack_execution_progress={0},".format(self.ack_execution_progress) +
            "ack_execution_start={0},".format(self.ack_execution_start) +
            "ack_acceptance={0},".format(self.ack_acceptance) +
            "service_type={0},".format(self.service_type) +
            "service_subtype={0},".format(self.service_subtype) +
            "source_id={0}".format(self.source_id) +
            ")"
        )


cdef class TMHeader:
    def __cinit__(
        TMHeader self,
        uint8_t spare_1,
        uint8_t pus_version,
        uint8_t spare_2,
        uint8_t service_type,
        uint8_t service_subtype,
        uint8_t destination_id,
        tuple time,
    ):
        self.spare_1 = spare_1
        self.pus_version = pus_version
        self.spare_2 = spare_2
        self.service_type = service_type
        self.service_subtype = service_subtype
        self.destination_id = destination_id
        self.time = time

    cpdef tuple to_tuple(TMHeader self):
        return (
            self.spare_1,
            self.pus_version,
            self.spare_2,
            self.service_type,
            self.service_subtype,
            self.destination_id,
            self.time,
        )

    cpdef dict to_dict(TMHeader self):
        return {
            'spare_1': self.spare_1,
            'pus_version': self.pus_version,
            'spare_2': self.spare_2,
            'service_type': self.service_type,
            'service_subtype': self.service_subtype,
            'destination_id': self.destination_id,
            'time': self.time,
        }

    def __repr__(TMHeader self):
        return (
            "TMHeader(" +
            "spare_1={0},".format(self.spare_1) +
            "pus_version={0},".format(self.pus_version) +
            "spare_2={0},".format(self.spare_2) +
            "service_type={0},".format(self.service_type) +
            "service_subtype={0},".format(self.service_subtype) +
            "destination_id={0},".format(self.destination_id) +
            "time={0}".format(self.time) +
            ")"
        )
