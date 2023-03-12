// Huffman decoding for Sentinel-1 bits

#include "huffman.h"

int huffman_brc0(int nbits, const uint8_t *bits, int nout, uint8_t *out)
{
    int idx = 0;
    int sample = 0;
    int sign;
    while ((idx < nbits) && (sample < nout))
    {
        sign = bits[idx++];
        if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 4 : 0);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 5 : 1);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 6 : 2);
        }
        else
        {
            out[sample] = (sign ? 7 : 3);
        }
        ++sample;
    }
    return (sample != nout) ? -idx : idx;
}  // huffman_brc0


int huffman_brc1(int nbits, const uint8_t *bits, int nout, uint8_t *out)
{
    int idx = 0;
    int sample = 0;
    int sign;
    while ((idx < nbits) && (sample < nout))
    {
        sign = bits[idx++];
        if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 5 : 0);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 6 : 1);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 7 : 2);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 8 : 3);
        }
        else
        {
            out[sample] = (sign ? 9 : 4);
        }
        ++sample;
    }
    return (sample != nout) ? -idx : idx;
}  // huffman_brc1


int huffman_brc2(int nbits, const uint8_t *bits, int nout, uint8_t *out)
{
    int idx = 0;
    int sample = 0;
    int sign;
    while ((idx < nbits) && (sample < nout))
    {
        sign = bits[idx++];
        if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 7 : 0);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 8 : 1);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 9 : 2);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 10 : 3);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 11 : 4);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 12 : 5);
        }
        else
        {
            out[sample] = (sign ? 13 : 6);
        }
        ++sample;
    }
    return (sample != nout) ? -idx : idx;
}  // huffman_brc2


int huffman_brc3(int nbits, const uint8_t *bits, int nout, uint8_t *out)
{
    int idx = 0;
    int sample = 0;
    int sign;
    while ((idx < nbits) && (sample < nout))
    {
        sign = bits[idx++];
        if (bits[idx++] == 0)
        {
            if (bits[idx++] == 0)
            {
                out[sample] = (sign ? 10 : 0);
            }
            else
            {
                out[sample] = (sign ? 11 : 1);
            }
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 12 : 2);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 13 : 3);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 14 : 4);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 15 : 5);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 16 : 6);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 17 : 7);
        }
        else if (bits[idx++] == 0)
        {
            out[sample] = (sign ? 18 : 8);
        }
        else
        {
            out[sample] = (sign ? 19 : 9);
        }
        ++sample;
    }
    return (sample != nout) ? -idx : idx;
}  // huffman_brc3


int huffman_brc4(int nbits, const uint8_t *bits, int nout, uint8_t *out)
{
    int idx = 0;
    int sample = 0;
    int sign;
    while ((idx < nbits) && (sample < nout))
    {
        sign = bits[idx++];
        if (bits[idx++] == 0)  // 0
        {
            if (bits[idx++] == 0)  // 00
            {
                out[sample] = (sign ? 16 : 0);  // 00
            }
            else if (bits[idx++] == 0)  // 010
            {
                out[sample] = (sign ? 17 : 1);  // 010
            }
            else
            {
                out[sample] = (sign ? 18 : 2);  // 011
            }
        }
        else if (bits[idx++] == 0)  // 10
        {
            if (bits[idx++] == 0)  // 100
            {
                out[sample] = (sign ? 19 : 3);  // 100
            }
            else  // 101
            {
                out[sample] = (sign ? 20 : 4);  // 101
            }
        }
        else if (bits[idx++] == 0)  // 110
        {
            if (bits[idx++] == 0)  // 1100
            {
                out[sample] = (sign ? 21 : 5);  // 1100
            }
            else  // 1101
            {
                out[sample] = (sign ? 22 : 6);  // 1101
            }
        }
        else if (bits[idx++] == 0)  // 1110
        {
            out[sample] = (sign ? 23 : 7);  // 1110
        }
        else if (bits[idx++] == 0)  // 11110
        {
            out[sample] = (sign ? 24 : 8);  // 11110
        }
        else if (bits[idx++] == 0)  // 111110
        {
            out[sample] = (sign ? 25 : 9);  // 111110
        }
        else if (bits[idx++] == 0)  // 1111110
        {
            if (bits[idx++] == 0)  // 11111100
            {
                out[sample] = (sign ? 26 : 10);  // 11111100
            }
            else  // 11111101
            {
                out[sample] = (sign ? 27 : 11);  // 11111101
            }
        }
        else if (bits[idx++] == 0) // 11111110
        {
            if (bits[idx++] == 0)  // 111111100
            {
                out[sample] = (sign ? 28 : 12);  // 111111100
            }
            else  // 111111101
            {
                out[sample] = (sign ? 29 : 13);  // 111111101
            }
        }
        else if (bits[idx++] == 0)  // 111111110
        {
            out[sample] = (sign ? 30 : 14);  // 111111110
        }
        else
        {
            out[sample] = (sign ? 31 : 15);  // 111111110
        }
        ++sample;
    }
    return (sample != nout) ? -idx : idx;
}  // huffman_brc4
