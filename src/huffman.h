// Huffman decoding for Sentinel-1 bits

#ifndef HUFFMAN_H_INCLUDED
#define HUFFMAN_H_INCLUDED

#include <stdint.h>

int huffman_brc0(int nbits, const uint8_t *bits, int nout, uint8_t *out);
int huffman_brc1(int nbits, const uint8_t *bits, int nout, uint8_t *out);
int huffman_brc2(int nbits, const uint8_t *bits, int nout, uint8_t *out);
int huffman_brc3(int nbits, const uint8_t *bits, int nout, uint8_t *out);
int huffman_brc4(int nbits, const uint8_t *bits, int nout, uint8_t *out);

#endif  // HUFFMAN_H_INCLUDED
