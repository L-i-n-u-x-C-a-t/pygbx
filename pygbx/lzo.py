from pygbx.bytereader import ByteReader

class lzo1x_decompress_safe(object):
    """
    Partial implementation of the Lempel-Ziv-Oberhumer data compression algorithm.

    This implements the lzo1x_decompress_safe algorithm
    """

    def __init__(self, input, output_length):
        """Decompresses data and returns bytearray

        Args:

        """


"""
int __cdecl lzo1x_decompress_safe(const unsigned char* in, unsigned long in_len, unsigned char* out, unsigned long* out_len) {
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

"""
