#include "RiceWrapper.h"

namespace ricewrapper
{
    RiceWrapper::RiceWrapper(uint32_t buffer_size) {
        this->_buffer_size = buffer_size;
        this->byte_buffer = static_cast<uint8_t*>(malloc(this->_buffer_size));
        this->int_buffer = static_cast<uint32_t*>(malloc(this->_buffer_size * sizeof(uint32_t)));
        this->short_buffer = static_cast<uint16_t*>(malloc(this->_buffer_size * sizeof(uint16_t)));
    }

    RiceWrapper::~RiceWrapper() {
        if (this->byte_buffer != NULL) {
            free(this->byte_buffer);
        };
        if (this->int_buffer != NULL) {
            free(this->int_buffer);
        };
        if (this->short_buffer != NULL) {
            free(this->short_buffer);
        };
    }

    uint8_t* RiceWrapper::rice_compress(uint8_t* data, uint32_t size, int32_t& compressed_size) {
        int32_t preProcessedSize;
        int32_t result;
        uint8_t* buffer;

        // check sizes are correct with the chosen buffers
        if (size / 2 > this->_buffer_size) {
            throw std::invalid_argument("Internal buffers too small for compression");
        };

        // pre-processed data generation
        preProcessedSize = preprocess(
            reinterpret_cast<uint16_t*>(data),
            size / 2,
            this->int_buffer,
            ESTIMATE_1D_H
        );
        if (preProcessedSize == -1) {
            throw std::invalid_argument("Error pre-processing data before compression.");
        };

        // compress the data
        result = compress(
            this->int_buffer,
            preProcessedSize,
            this->byte_buffer,
            this->_buffer_size
        );
        if (result == -1) {
            throw std::invalid_argument("Problem rice");
        };

        // copy the result and return
        buffer = static_cast<uint8_t*>(malloc(result));
        std::memcpy(buffer, this->int_buffer, result);
        compressed_size = result;
        return buffer;
    }

    uint8_t* RiceWrapper::rice_uncompress(uint8_t* data, uint32_t size, uint32_t output_size) {
        int32_t decompressedSize;
        int32_t postProcessedSize;
        uint8_t* buffer;

        // check valid sizes
        if (output_size > this->_buffer_size) {
            throw std::invalid_argument("Internal buffer too small for input");
        };

        // decompress the data and get the size
        decompressedSize = uncompress(
            data,
            size,
            this->int_buffer,
            output_size / 2
        );
        if (decompressedSize == -1) {
            throw std::invalid_argument("Error uncompressing data");
        }

        // post process the data
        postProcessedSize = postprocessor(
            this->int_buffer,
            decompressedSize,
            this->short_buffer,
            ESTIMATE_1D_H
        );
        if (postProcessedSize == -1) {
            std::invalid_argument("Error post processing decompressed data");
        };

        // compute byte size
        postProcessedSize = postProcessedSize * sizeof(uint16_t);

        // return the copy of the data
        buffer = static_cast<uint8_t*>(malloc(postProcessedSize));
        std::memcpy(buffer, this->short_buffer, postProcessedSize);
        return buffer;
    }

} /* ricewrapper */
