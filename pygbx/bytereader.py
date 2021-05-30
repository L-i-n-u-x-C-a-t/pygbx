import logging
import struct
from io import IOBase
from sys import float_info
from pygbx.headers import Vector3


class PositionCheckpoint(object):
    """Creates a simple object temporarily save a starting position in a buffer and its size. Position and size are
    set manually
    TODO: Find a way to automate the saving of position checkpoints better
    """

    def __init__(self, pos=None, size=None):
        """Constructs a new PositionInfo."""
        self.pos = pos
        self.size = size

    @property
    def valid(self):
        """Checks if the instance of the section is valid

        Returns:
            True if the position + size have sensible values
        """
        return self.pos is not None and self.size is not None and 0 <= self.pos <= self.size and self.size > 0


class ByteReaderBase(object):
    """The ByteReaderBase class provides convenience methods for reading raw types such as integers, strings
    from files/strings/bytearrays

    By default all methods inside this class have their endianness set to True (unlike ByteReader).

    Read operations always return the data read or False on errors/exceptions.
    Write operations always return the number of bytes written or False upon errors/exceptions.

    The readers position will always move forward when reading/writing data, unless an error/exception has occurred!
    """

    def __init__(self, data):
        """Constructs a new ByteReaderBase object that can be used to perform actions on the selected buffer.

        Args:
            data (str/IOBase/bytes/bytearray): The buffer to perform actions on.
        """
        if isinstance(data, str):
            self.data = bytearray(data.encode('utf-8'))
        elif isinstance(data, IOBase):
            self.data = bytearray(data.read())
        elif isinstance(data, bytes):
            self.data = bytearray(data)
        elif isinstance(data, bytearray):
            self.data = data
        else:
            raise Exception('Input data must be of type str / IOBase (filehandle of open()) / bytes / bytearray')

        self.pos = 0
        self.size = len(self.data)
        # initialize position_checkpoint but still keep it invalid
        self.position_checkpoint = PositionCheckpoint(None, None)

        # alias of skip method
        self.move = self.skip

    def push_position_checkpoint(self):
        """Begins a section that can be then retrieved with pop_position_checkpoint."""
        self.position_checkpoint.pos = self.pos

        # make the position_checkpoint of this class invalid because we just set a new starting point
        # and haven\'t ended it yet
        self.position_checkpoint.size = None

    def pop_position_checkpoint(self):
        """Ends the section began with push_position_checkpoint.

        Returns:
            The PositionCheckpoint of this class
        """
        self.position_checkpoint.size = self.pos - self.position_checkpoint.pos
        if self.position_checkpoint.size < 0:
            logging.warning(f'Returned PositionInfo has a size less than 0 ({self.position_checkpoint.size}). The '
                            f'readers position has moved more backwards than forwards since push_info was called.')
        # position_checkpoint can also be retrieved with self.position_checkpoint
        return self.position_checkpoint

    def __get_bytes(self, num_bytes):
        try:
            return self.data[self.pos:self.pos+num_bytes]  # This does not fail when reading more than available
        except Exception as e:
            # TODO: Add verbosity level options
            logging.error(e, exc_info=True, stack_info=True)
            return False

    def read(self, num_bytes, format_chars=None, little_endian=True):
        """Reads an arbitrary amount of bytes from the buffer.

        Args:
            num_bytes (int): the number of bytes to read from the buffer
            format_chars (str,None): the format character used by the struct module, passing None does not
                                unpack the bytes. for more information on format characters see:
                                # https://docs.python.org/3/library/struct.html#format-characters
            little_endian (bool): sets endianness when reading
        Returns:
            data of type format_chars (or bytearray if format_chars is None) or False upon errors/exceptions
        """
        val = self.__get_bytes(num_bytes)

        if val is False:
            return False

        bytes_read = len(val)
        self.pos += bytes_read

        if bytes_read > num_bytes:
            logging.error(f'Tried to read {num_bytes} byte(s), but only {bytes_read} byte(s) were left to be read')
        if bytes_read < num_bytes:
            logging.error(f'Tried to read {num_bytes} byte(s), but only {bytes_read} byte(s) were actually read')

        if format_chars is None:
            if little_endian:
                return val[-1::-1]
            else:
                return val

        try:
            if little_endian:
                format_chars = f'<{format_chars}'
            else:
                format_chars = f'>{format_chars}'
            return struct.unpack(format_chars, val)[0]
        except Exception as e:
            logging.error(e, exc_info=True, stack_info=True)
            return False

    def size(self):
        """Returns the size of the buffer in bytes"""
        return len(self.data)

    def skip(self, num_bytes):
        """Skips provided amount of bytes in the buffer. Accepts negative values too.

        Args:
            num_bytes (int): the number of bytes to skip
        """
        self.pos += num_bytes

    def read_string(self, num_bytes, little_endian=True):
        """Reads num_bytes amount of bytes from buffer and returns utf-8 decoded string.
        Note that you have to specify the amount of _bytes_ of the string, not the amount of characters!
        If you specify an invalid amount of bytes given the utf-8 encoding, you'll likely end up getting decoding errors

        Returns:
            the utf-8 string read from the buffer
        """
        val = self.read(num_bytes, str(num_bytes) + 's', little_endian)
        if val is False:
            return False
        try:
            val = val.decode('utf-8')
            if little_endian:
                return val[-1::-1]
            else:
                return val
        except UnicodeDecodeError as e:
            logging.error(f'Could not read string from buffer due to malformed unicode: {e}')
            return False
        except Exception as e:
            logging.error(f'Failed to read string from buffer: {e}')
            return False

    def read_int32(self, little_endian=True):
        """Reads a signed int32.

        Returns:
            the integer read from the buffer
        """
        return self.read(4, 'i', little_endian)

    def read_uint32(self, little_endian=True):
        """Reads an unsigned int32.

        Returns:
            the integer read from the buffer
        """
        return self.read(4, 'I', little_endian)

    def read_int16(self, little_endian=True):
        """Reads a signed int16.

        Returns:
            the integer read from the buffer
        """
        return self.read(2, 'h', little_endian)

    def read_uint16(self, little_endian=True):
        """Reads an unsigned int16.

        Returns:
            the integer read from the buffer
        """
        return self.read(2, 'H', little_endian)

    def read_uint8(self, little_endian=True):
        """Reads a signed int8.

        Returns:
            the integer read from the buffer
        """
        return self.read(1, 'B', little_endian)

    def read_int8(self, little_endian=True):
        """Reads a signed int8.

        Returns:
            the integer read from the buffer
        """
        return self.read(1, 'b', little_endian)

    def read_float(self, little_endian=True):
        """Reads a 32 bit float.

        Returns:
            the float read from the buffer
        """
        return self.read(4, 'f', little_endian)

    def __write_bytes(self, data, format_chars):
        try:
            data_packed = struct.pack(format_chars, data)
            data_length = len(data_packed)
            self.data[self.pos:self.pos+data_length] = data_packed
            return data_length
        except Exception as e:
            logging.error(e)
            return False

    def write(self, data, format_chars=None, little_endian=True):
        """Writes an arbitrary amount of bytes to the buffer. The readers position changes if when no errors/exceptions
        have occurred.

        Args:
            data (bytearray, any): the data to be written to the buffer
            format_chars (str, None): the format character specified as string used for writing. If format_chars
            is None, then data must be an bytearray. for more information on format characters see:
                # https://docs.python.org/3/library/struct.html#format-characters
            little_endian (bool): sets endianness when writing
        Returns:
            Number of bytes that were written, False upon errors/exceptions
        """
        if format_chars is None:
            if not isinstance(data, bytearray):
                logging.error(f'write accepts type bytearray for argument data if the format_chars argument is '
                              f'set to None. The type of data was {type(data)}.')
                return False
            else:
                # manually reverse here because struct.pack for some reason refuses to listen when specifying s/p
                if little_endian:
                    data = data[-1::-1]
                format_chars = f'{len(data)}s'
        else:
            format_chars = f'{"<" if little_endian else ">"}{format_chars}'

        bytes_written = self.__write_bytes(data, format_chars)

        if bytes_written:
            self.size = self.pos + bytes_written if self.pos + bytes_written > self.size else self.size
            self.pos += bytes_written
        return bytes_written

    # TODO: This still can fail for some inputs
    def write_string(self, data, little_endian=True):
        """Writes a string to the buffer.

        Returns:
            Number of bytes that were written, False on error/exception
        """
        if isinstance(data, str):
            if data == '':
                logging.warning(f'string passed to write_string was an empty string')
                return 0
            string_encoded = data.encode('utf-8')
            # struct.pack ignored the endianness for strings (format character s/p), so they are reversed here instead
            if little_endian:
                return self.write(bytearray(string_encoded[-1::-1]), f'{len(string_encoded)}s')
            else:
                return self.write(bytearray(string_encoded), f'{len(string_encoded)}s')
        else:
            logging.error(f'write_string accepts data type str. {type(data)} was given.')
            return False

    def write_uint32(self, data, little_endian=True):
        """Writes an uint32 to the buffer.

        Returns:
            Number of bytes that were written, False on error/exception
        """
        if isinstance(data, int) and 0 <= data <= 4294967295:
            return self.write(data, 'I', little_endian)
        else:
            # TODO: Fix error log message of what the incorrect datatype was. type() is insufficient. (for all w_(u)int)
            logging.error(f'write_uint32 accepts data type uint32. {type(data)} was given.')
            return False

    def write_int32(self, data, little_endian=True):
        """Writes an int32 to the buffer.

        Returns:
            Number of bytes that were written, False on error/exception
        """
        if isinstance(data, int) and -2147483648 <= data <= 2147483647:
            return self.write(data, 'i', little_endian)
        else:
            logging.error(f'write_int32 accepts data type int32. {type(data)} was given.')
            return False

    def write_uint16(self, data, little_endian=True):
        """Writes an uint16 to the buffer.

        Returns:
            Number of bytes that were written, False on error/exception
        """
        if isinstance(data, int) and 0 <= data <= 65536:
            return self.write(data, 'H', little_endian)
        else:
            logging.error(f'write_uint16 accepts data type uint16. {type(data)} was given.')
            return False

    def write_int16(self, data, little_endian=True):
        """Writes an int16 to the buffer.

        Returns:
            Number of bytes that were written, False on error/exception
        """
        if isinstance(data, int) and -32768 <= data <= 32767:
            return self.write(data, 'h', little_endian)
        else:
            logging.error(f'write_int16 accepts data type int16. {type(data)} was given.')
            return False

    def write_uint8(self, data, little_endian=True):
        """Writes an int8 to the buffer.

        Returns:
            Number of bytes that were written, False on error/exception
        """
        if isinstance(data, int) and 0 <= data <= 255:
            return self.write(data, 'B', little_endian)
        else:
            logging.error(f'write_uint8 accepts data type uint8. {type(data)} was given.')
            return False

    def write_int8(self, data, little_endian=True):
        """Writes an int8 to the buffer.

        Returns:
            Number of bytes that were written, False on error/exception
        """
        if isinstance(data, int) and -128 <= data <= 127:
            return self.write(data, 'b', little_endian)
        else:
            logging.error(f'write_int8 accepts data type int8. {type(data)} was given.')
            return False

    def write_float(self, data, little_endian=True):
        """Writes a float to the buffer.

        Returns:
            Number of bytes that were written, False on error/exception
        """
        if isinstance(data, float) and -float_info.max <= data <= float_info.max:
            return self.write(data, 'f', little_endian)
        else:
            logging.error(f'write_float accepts data type float. {type(data)} was given.')
            return False

class ByteReader(ByteReaderBase):
    """The ByteReader class provides convenience methods for reading raw types such as integers, strings
    from files/strings/bytearrays

    This class is slightly modified from the ByteReaderBase class. It is specifically made for GBX files.
    All methods in this class are made for easy use when working with GBX data. See method docstrings for detailed info.

    Read operations always return the data read or False on errors/exceptions.
    Write operations always return the number of bytes written or False upon errors/exceptions.

    The readers position will always move forward when reading/writing data, unless an error/exception has occurred!
    """

    def __init__(self, data):
        """Constructs a new ByteReader object that can be used to perform actions on the selected buffer on.

        If any errors encounter while trying to read/write/jump from the buffer, the operation in question will return
        False. It will not throw or return data upon errors.

        Args:
            data (str/IOBase/bytes/bytearray): The buffer to perform actions on.
        """
        super().__init__(data)

        self.seen_lookback = False
        self.stored_strings = []

    def read(self, num_bytes=None, format_chars=None, little_endian=False):
        """This 'low' level read operating can be simply used by only calling it with the amount of bytes you want to
        read to get back a bytearray in big endian format (human readable left to right). If you call this with
        num_bytes set to None, it will first read an uint32 from the buffer (changing the readers position by +4),
        and the value it has read will be the amount of bytes it will then read from the buffer and return that data.
        (same as read_string)

        If you want to read specific data types use the higher level methods below.

        Args:
            num_bytes (int, None): Number of bytes to read from the buffer, or None to read uint32 first and then use
                                   the uint32 value to read data for those uint32 bytes
            format_chars (str,None): the format character used by the struct module, passing None does not
                                     unpack the bytes. for more information on format characters see:
                                     # https://docs.python.org/3/library/struct.html#format-characters
            little_endian (bool): sets endianness when reading
        """
        return super().read(self.read_uint32() if num_bytes is None else num_bytes, format_chars, little_endian)

    def read_string(self, num_bytes=None, little_endian=False):
        """Reads string from buffer in human readable format (big endian). You can specify the num_bytes to read, but
        this can lead to unicode exceptions. If num_bytes is None, it will first read a uint32, and use the read value
        as the amount of bytes it will then read afterwards and return that data.

        Usually you would call this method without any arguments, because GBX data will have a uint32 before strings
        that indicate the size of the upcoming string.

        GBX data in almost all cases has big endian strings (human readable). There are exception(s?) like the string
        "SKIP" which appears backwards as "PIKS", but that doesn't have a uint32 in front of it anyway, its different.
        """
        return super().read_string(self.read_uint32() if num_bytes is None else num_bytes, little_endian)

    def write(self, data, format_chars=None, little_endian=False):
        """Writes an arbitrary amount of bytes to the buffer in big endian format (human readable left to right)

        If you want to write specific data types use the higher level methods below.

        Args:
            data (bytearray, any): the data to be written to the buffer
            format_chars (str, None): the format character specified as string used for writing. If format_chars
            is None, then data must be an bytearray. for more information on format characters see:
                # https://docs.python.org/3/library/struct.html#format-characters
            little_endian (bool): sets endianness when writing
        Returns:
            Number of bytes that were written, False upon errors/exceptions
        """
        return super().write(data, format_chars, little_endian)

    def write_string(self, data, little_endian=False):
        """Writes a string to the buffer in big endian (human readable left to right)

        Remember that len(str) is not the same the bytes it will actually write. This method however does return the
        amount of bytes it has written.

        Args:
            data (str): String to write (do not use .encode('utf-8') on it before passing it)
            little_endian (bool): sets endianness when writing
        Returns:
            Number of bytes that were written, False upon errors/exceptions
        """
        return super().write_string(data, little_endian)

    def read_string_lookback(self):
        """Reads a special string type in the GBX file format called the lookbackstring.

        Such type is used to reference already read strings, or introduce them if they were not
        read yet. A ByteReader instance keeps track of lookback strings previously read and
        returns an already existing string, if the data references it. For more information,
        see the lookbackstring type in the GBX file format: https://wiki.xaseco.org/wiki/GBX.

        Returns:
            the lookback string read from the buffer
        """
        if not self.seen_lookback:
            self.read_uint32()

        self.seen_lookback = True
        inp = self.read_uint32()
        if (inp & 0xc0000000) != 0 and (inp & 0x3fffffff) == 0:
            s = self.read_string()
            self.stored_strings.append(s)
            return s

        if inp == 0:
            s = self.read_string()
            self.stored_strings.append(s)
            return s

        if inp == -1:
            return ''

        if (inp & 0x3fffffff) == inp:
            if inp == 11:
                return 'Valley'
            elif inp == 12:
                return 'Canyon'
            elif inp == 13:
                return 'Lagoon'
            elif inp == 17:
                return 'TMCommon'
            elif inp == 202:
                return 'Storm'
            elif inp == 299:
                return 'SMCommon'
            elif inp == 10003:
                return 'Common'

        inp &= 0x3fffffff
        if inp - 1 >= len(self.stored_strings):
            return ''
        return self.stored_strings[inp - 1]

    # TODO: Same todo issue as with write_vec3
    def read_vec3(self, little_endian=False):
        # TODO: Are Vectors in big endian in GBX data? (x y z and not z y x)
        """Reads 12 bytes as 3 floats from the buffer and packs them into a Vector3.

        Returns:
            the vector read from the buffer
        """
        val = (self.read_float(), self.read_float(), self.read_float())
        if little_endian:
            val = val[-1::-1]
        return Vector3(val[0], val[1], val[2])

    # TODO: Is Vector3 actually supposed to consist of floats only? I saw non floats inside of Vector3 somewhere else
    def write_vec3(self, data, little_endian=False):
        """Writes a Vector3 with length 12 bytes to the buffer. Specifying little_endian here will only affect
        the arrangement of x,y and z, but each of these values individually will always end up being little endian

        Note that this can return bytes written but still have failed (e.g. only 2 out of 3 floats were written)

        Returns:
            Number of bytes written, or False on error/exception
        """
        if isinstance(data, Vector3):
            # Check integrity of Vector3 object
            if isinstance(data.x, float) and isinstance(data.y, float) and isinstance(data.z, float):
                bytes_written = 0
                if little_endian:
                    result = self.write(data.x, 'f')
                    bytes_written += result if result else 0
                    result = self.write(data.y, 'f')
                    bytes_written += result if result else 0
                    result = self.write(data.z, 'f')
                    bytes_written += result if result else 0
                else:
                    result = self.write(data.z, 'f')
                    bytes_written += result if result else 0
                    result = self.write(data.y, 'f')
                    bytes_written += result if result else 0
                    result = self.write(data.x, 'f')
                    bytes_written += result if result else 0
                return bytes_written
            else:
                logging.error(f'write_vec3 accepts data type Vector3, consisting of floats, but 1 or more values '
                              f'inside the Vector3 object are not floats.\n'
                              f'vec.x: {type(data.x)}, \nvec.y: {type(data.y)},\nvec.z: {type(data.z)}')
                return False
        else:
            logging.error(f'write_vec3 accepts data type Vector3. {type(data)} was given.')
            return False
