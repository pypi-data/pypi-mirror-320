
cdef class Parameter:
    def __cinit__(
        Parameter self,
        str name,
        uint32_t byte,
        uint32_t bit,
        uint32_t group,
        uint32_t block_size,
        uint32_t counter,
        uint32_t length,
        str type,
        double maximum,
    ):
        self.name = name
        self.byte = byte
        self.bit = bit
        self.group = group
        self.block_size = block_size
        self.length = length
        self.type = type
        self.maximum = maximum
        self.counter = counter

    def __repr__(Parameter self):
        return (
            "Parameter(" +
            "name={0},".format(self.name) +
            "byte={0},".format(self.byte) +
            "bit={0},".format(self.bit) +
            "length={0},".format(self.length) +
            "type={0},".format(self.type) +
            ")"
        )
