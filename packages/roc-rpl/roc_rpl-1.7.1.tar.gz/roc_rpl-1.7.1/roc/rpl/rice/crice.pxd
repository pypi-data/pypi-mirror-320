from libc.stdint cimport uint8_t
from libc.stdint cimport uint32_t
from libc.stdint cimport int32_t

cdef extern from "GsrPreprocessMode.h":
    ctypedef enum PreprocessMode:
        ESTIMATE_1D_H

cdef extern from "GsrRiceUncompress.h":
    # function to uncompress the data
    int uncompress(unsigned char* compressed, int compressedLen, unsigned int* data, int nbInput) except +

    # post process data
    int postprocessor(unsigned int* data, int nbInput, unsigned short* postProcessed, PreprocessMode mode) except +

cdef extern from "GsrRiceCompress.h":
    # function to compress the data
    int compress(unsigned int* data, int nbInput, unsigned char* compressed, int compressedLen) except +

    # preprocess the data
    int preprocess(unsigned short* data, int nbInput, unsigned int* preprocessed, PreprocessMode mode) except +
