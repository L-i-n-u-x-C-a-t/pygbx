import struct
from pygbx.bytereader import ByteReader

class LZO(object):
    """
    Partial implementation of the Lempel-Ziv-Oberhumer data compression algorithm.

    This implements the lzo1x_decompress_safe algorithm
    """

    def __init__(self):
        pass


    @staticmethod
    def lzo1x_decompress_safe(compressed_data, output_length):
        ip = ByteReader(compressed_data)

        out_len = output_length
        op = ByteReader(bytearray(out_len))

        op_len = op.size

        out = 0

        ip_end = ip.size
        op_end = op.size

        t = 0
        m_pos = 0

        print(op_len)

"""
int __cdecl lzo1x_decompress_safe(const unsigned char* in, unsigned long in_len,
    unsigned char* out, unsigned long* out_len) {
    unsigned char* op;
    const unsigned char* ip;
    unsigned long t;
    const unsigned char* m_pos;

    const unsigned char* const ip_end = in + in_len;
    unsigned char* const op_end = out + *out_len;

    bool needs_first_literal_run = false;
    bool needs_match_done = false;
    bool needs_match = false;

    *out_len = 0;

    op = out;
    ip = in;

    if (*ip > 17)
    {
        t = *ip++ - 17;
        if (t < 4) {
            if ((unsigned long)(op_end - op) < (unsigned long)(t)) {
                *out_len = op - out;
                return -5;
            }

            if ((unsigned long)(ip_end - ip) < (unsigned long)(t + 1)) {
                *out_len = op - out;
                return -4;
            }

            *op++ = *ip++;

            if (t > 1) {
                *op++ = *ip++;
                if (t > 2) {
                    *op++ = *ip++;
                }
            }

            t = *ip++;

            if (ip >= ip_end) {
                *out_len = op - out;
                return -7;
            }
        }
        else {
            if ((unsigned long)(op_end - op) < (unsigned long)(t)) {
                *out_len = op - out;
                return -5;
            }
            if ((unsigned long)(ip_end - ip) < (unsigned long)(t + 1)) {
                *out_len = op - out; return -4;
            }
            do *op++ = *ip++; while (--t > 0);
            needs_first_literal_run = true;
        }
    }

    while (ip < ip_end || needs_first_literal_run)
    {
        if (needs_match == false) {
            if (needs_first_literal_run == false) {
                t = *ip++;
                if (t >= 16) {
                    needs_match = true;
                    continue;
                }
                if (t == 0)
                {
                    if ((unsigned long)(ip_end - ip) < (unsigned long)(1)) {
                        *out_len = op - out;
                        return -4;
                    }
                    while (*ip == 0)
                    {
                        t += 255;
                        ip++;
                        if ((unsigned long)(ip_end - ip) < (unsigned long)(1)) {
                            *out_len = op - out;
                            return -4;
                        }
                    }
                    t += 15 + *ip++;
                }
                if ((unsigned long)(op_end - op) < (unsigned long)(t + 3)) {
                    *out_len = op - out;
                    return -5;
                }
                if ((unsigned long)(ip_end - ip) < (unsigned long)(t + 4)) {
                    *out_len = op - out;
                    return -4;
                }

                *(unsigned int*)(op) = *(const unsigned int*)(ip);
                op += 4; ip += 4;
                if (--t > 0)
                {
                    if (t >= 4)
                    {
                        do {
                            *(unsigned int*)(op) = *(const unsigned int*)(ip);
                            op += 4; ip += 4; t -= 4;
                        } while (t >= 4);
                        if (t > 0) do *op++ = *ip++; while (--t > 0);
                    }
                    else {
                        do *op++ = *ip++; while (--t > 0);
                    }
                }
            }
            else {
                needs_first_literal_run = false;
            }

            t = *ip++;
            if (t < 16) {
                m_pos = op - (1 + 0x0800);
                m_pos -= t >> 2;
                m_pos -= *ip++ << 2;
                if (m_pos < out || m_pos >= op) {
                    *out_len = op - out;
                    return -6;
                }
                if ((unsigned long)(op_end - op) < (unsigned long)(3)) {
                    *out_len = op - out;
                    return -5;
                }
                *op++ = *m_pos++; *op++ = *m_pos++; *op++ = *m_pos;
                needs_match_done = true;
            }
        }
        else {
            needs_match = false;
        }

        do {
            if (needs_match_done == false) {
                if (t >= 64)
                {
                    m_pos = op - 1;
                    m_pos -= (t >> 2) & 7;
                    m_pos -= *ip++ << 3;
                    t = (t >> 5) - 1;

                    if (m_pos < out || m_pos >= op) {
                        *out_len = op - out;
                        return -6;
                    }
                    if ((unsigned long)(op_end - op) < (unsigned long)(t + 3 - 1)) {
                        *out_len = op - out;
                        return -5;
                    }
                    goto copy_match;
                }
                else if (t >= 32)
                {
                    t &= 31;
                    if (t == 0)
                    {
                        if ((unsigned long)(ip_end - ip) < (unsigned long)(1)) {
                            *out_len = op - out;
                            return -4;
                        }
                        while (*ip == 0)
                        {
                            t += 255;
                            ip++;
                            if ((unsigned long)(ip_end - ip) < (unsigned long)(1)) {
                                *out_len = op - out;
                                return -4;
                            }
                        }
                        t += 31 + *ip++;
                    }
                    ip += 2;
                }
                else if (t >= 16)
                {
                    m_pos = op;
                    m_pos -= (t & 8) << 11;
                    t &= 7;
                    if (t == 0)
                    {
                        if ((unsigned long)(ip_end - ip) < (unsigned long)(1)) {
                            *out_len = op - out;
                            return -4;
                        }
                        while (*ip == 0)
                        {
                            t += 255;
                            ip++;
                            if ((unsigned long)(ip_end - ip) < (unsigned long)(1)) {
                                *out_len = op - out;
                                return -4;
                            }
                        }
                        t += 7 + *ip++;
                    }

                    m_pos -= (*(const unsigned short*)ip) >> 2;

                    ip += 2;
                    if (m_pos == op) {
                        *out_len = op - out;
                        return (ip == ip_end ? 0 :
                            (ip < ip_end ? -8 : -4));
                    }
                    m_pos -= 0x4000;
                }
                else
                {
                    m_pos = op - 1;
                    m_pos -= t >> 2;
                    m_pos -= *ip++ << 2;

                    if (m_pos < out || m_pos >= op) {
                        *out_len = op - out;
                        return -6;
                    }
                    if ((unsigned long)(op_end - op) < (unsigned long)(2)) {
                        *out_len = op - out;
                        return -5;
                    }
                    *op++ = *m_pos++; *op++ = *m_pos;

                    needs_match_done = true;
                }

                if (needs_match_done == false) {
                    if (m_pos < out || m_pos >= op) {
                        *out_len = op - out;
                        return -6;
                    }
                    if ((unsigned long)(op_end - op) < (unsigned long)(t + 3 - 1)) {
                        *out_len = op - out;
                        return -5;
                    }

                    if (t >= 2 * 4 - (3 - 1) && (op - m_pos) >= 4)
                    {
                        *(unsigned int*)(op) = *(const unsigned int*)(m_pos);
                        op += 4; m_pos += 4; t -= 4 - (3 - 1);
                        do {
                            *(unsigned int*)(op) = *(const unsigned int*)(m_pos);
                            op += 4; m_pos += 4; t -= 4;
                        } while (t >= 4);
                        if (t > 0) do *op++ = *m_pos++; while (--t > 0);
                    }
                    else
                    {
                    copy_match:
                        *op++ = *m_pos++; *op++ = *m_pos++;
                        do *op++ = *m_pos++; while (--t > 0);
                    }
                }
                else {
                    needs_match_done = false;
                }
            }
            else {
                needs_match_done = false;
            }

            t = ip[-2] & 3;

            if (t == 0) {
                break;
            }

            if ((unsigned long)(op_end - op) < (unsigned long)(t)) {
                *out_len = op - out;
                return -5;
            }

            if ((unsigned long)(ip_end - ip) < (unsigned long)(t + 1)) {
                *out_len = op - out;
                return -4;
            }

            *op++ = *ip++;

            if (t > 1) {
                *op++ = *ip++;
                if (t > 2) {
                    *op++ = *ip++;
                }
            }

            t = *ip++;

            if (ip >= ip_end) {
                *out_len = op - out;
                return -7;
            }
        } while (ip < ip_end);
    }

    *out_len = op - out;
    return -7;
}
"""