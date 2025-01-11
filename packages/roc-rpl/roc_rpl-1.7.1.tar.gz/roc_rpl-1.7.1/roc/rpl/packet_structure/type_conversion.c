#include "type_conversion.h"
#include <string.h>

int8_t to_signed_char(uint8_t x)
{
    int8_t result;

    memcpy(&result, &x, sizeof(int8_t));
    return result;
}

int16_t to_signed_short(uint16_t x)
{
    int16_t result;

    memcpy(&result, &x, sizeof(int16_t));
    return result;
}

int32_t to_signed_long(uint32_t x)
{
    int32_t result;

    memcpy(&result, &x, sizeof(int32_t));
    return result;
}

float to_float(uint32_t x)
{
    float result;

    memcpy(&result, &x, sizeof(float));
    return result;
}
