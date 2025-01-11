#ifndef RICEWRAPPER_H_4FKWVUKZ
#define RICEWRAPPER_H_4FKWVUKZ

#include <stdint.h>
#include <cstring>
#include <cstdlib>
#include <stdexcept>
#include "GsrRiceCompress.h"
#include "GsrRiceUncompress.h"
#include "GsrPreprocessMode.h"

namespace ricewrapper
{
    class RiceWrapper
    {
    public:
        RiceWrapper (uint32_t buffer_size);
        virtual ~RiceWrapper ();

        uint32_t* int_buffer;
        uint16_t* short_buffer;
        uint8_t* byte_buffer;
        uint32_t _buffer_size;

        uint8_t* rice_compress(uint8_t* data, uint32_t size, int32_t& compressed_size);
        uint8_t* rice_uncompress(uint8_t* data, uint32_t size, uint32_t output_size);

    private:

    };
} /* ricewrapper */

#endif /* end of include guard: RICEWRAPPER_H_4FKWVUKZ
#define RICEWRAPPER_H_4FKWVUKZ */
