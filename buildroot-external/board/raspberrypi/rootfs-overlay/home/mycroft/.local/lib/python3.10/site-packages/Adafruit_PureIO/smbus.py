# The MIT License (MIT)
#
# Copyright (c) 2016 Tony DiCola for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`Adafruit_PureIO.smbus`
================================================================================

Pure python (i.e. no native extensions) access to Linux IO I2C interface that mimics the
Python SMBus API.

* Author(s): Tony DiCola, Lady Ada, Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Software and Dependencies:**

* Linux and Python 3.5 or Higher

"""

from ctypes import c_uint8, c_uint16, c_uint32, cast, pointer, POINTER
from ctypes import create_string_buffer, Structure
from fcntl import ioctl
import struct

# I2C C API constants (from linux kernel headers)
I2C_M_TEN = 0x0010  # this is a ten bit chip address
I2C_M_RD = 0x0001  # read data, from slave to master
I2C_M_STOP = 0x8000  # if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_NOSTART = 0x4000  # if I2C_FUNC_NOSTART
I2C_M_REV_DIR_ADDR = 0x2000  # if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_IGNORE_NAK = 0x1000  # if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_NO_RD_ACK = 0x0800  # if I2C_FUNC_PROTOCOL_MANGLING
I2C_M_RECV_LEN = 0x0400  # length will be first received byte

I2C_SLAVE = 0x0703  # Use this slave address
I2C_SLAVE_FORCE = 0x0706  # Use this slave address, even if
# is already in use by a driver!
I2C_TENBIT = 0x0704  # 0 for 7 bit addrs, != 0 for 10 bit
I2C_FUNCS = 0x0705  # Get the adapter functionality mask
I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)
I2C_PEC = 0x0708  # != 0 to use PEC with SMBus
I2C_SMBUS = 0x0720  # SMBus transfer


# ctypes versions of I2C structs defined by kernel.
# Tone down pylint for the Python classes that mirror C structs.
# pylint: disable=invalid-name,too-few-public-methods
class i2c_msg(Structure):
    """Linux i2c_msg struct."""

    _fields_ = [
        ("addr", c_uint16),
        ("flags", c_uint16),
        ("len", c_uint16),
        ("buf", POINTER(c_uint8)),
    ]


class i2c_rdwr_ioctl_data(Structure):  # pylint: disable=invalid-name
    """Linux i2c data struct."""

    _fields_ = [("msgs", POINTER(i2c_msg)), ("nmsgs", c_uint32)]


# pylint: enable=invalid-name,too-few-public-methods


def make_i2c_rdwr_data(messages):
    """Utility function to create and return an i2c_rdwr_ioctl_data structure
    populated with a list of specified I2C messages.  The messages parameter
    should be a list of tuples which represent the individual I2C messages to
    send in this transaction.  Tuples should contain 4 elements: address value,
    flags value, buffer length, ctypes c_uint8 pointer to buffer.
    """
    # Create message array and populate with provided data.
    msg_data_type = i2c_msg * len(messages)
    msg_data = msg_data_type()
    for i, message in enumerate(messages):
        msg_data[i].addr = message[0] & 0x7F
        msg_data[i].flags = message[1]
        msg_data[i].len = message[2]
        msg_data[i].buf = message[3]
    # Now build the data structure.
    data = i2c_rdwr_ioctl_data()
    data.msgs = msg_data
    data.nmsgs = len(messages)
    return data


# Create an interface that mimics the Python SMBus API.
class SMBus:
    """I2C interface that mimics the Python SMBus API but is implemented with
    pure Python calls to ioctl and direct /dev/i2c device access.
    """

    def __init__(self, bus=None):
        """Create a new smbus instance.  Bus is an optional parameter that
        specifies the I2C bus number to use, for example 1 would use device
        /dev/i2c-1.  If bus is not specified then the open function should be
        called to open the bus.
        """
        self._device = None
        if bus is not None:
            self.open(bus)

    def __del__(self):
        """Clean up any resources used by the SMBus instance."""
        self.close()

    def __enter__(self):
        """Context manager enter function."""
        # Just return this object so it can be used in a with statement, like
        # with SMBus(1) as bus:
        #     # do stuff!
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit function, ensures resources are cleaned up."""
        self.close()
        return False  # Don't suppress exceptions.

    def open(self, bus):
        """Open the smbus interface on the specified bus."""
        # Close the device if it's already open.
        if self._device is not None:
            self.close()
        # Try to open the file for the specified bus.  Must turn off buffering
        # or else Python 3 fails (see: https://bugs.python.org/issue20074)
        # pylint: disable=consider-using-with
        self._device = open("/dev/i2c-{0}".format(bus), "r+b", buffering=0)
        # pylint: enable=consider-using-with
        # TODO: Catch IOError and throw a better error message that describes
        # what's wrong (i.e. I2C may not be enabled or the bus doesn't exist).

    def close(self):
        """Close the smbus connection.  You cannot make any other function
        calls on the bus unless open is called!"""
        if self._device is not None:
            self._device.close()
            self._device = None

    def _select_device(self, addr):
        """Set the address of the device to communicate with on the I2C bus."""
        ioctl(self._device.fileno(), I2C_SLAVE, addr & 0x7F)

    def read_byte(self, addr):
        """Read a single byte from the specified device."""
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        self._select_device(addr)
        return ord(self._device.read(1))

    def read_bytes(self, addr, number):
        """Read many bytes from the specified device."""
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        self._select_device(addr)
        return self._device.read(number)

    def read_byte_data(self, addr, cmd):
        """Read a single byte from the specified cmd register of the device."""
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        # Build ctypes values to marshall between ioctl and Python.
        reg = c_uint8(cmd)
        result = c_uint8()
        # Build ioctl request.
        request = make_i2c_rdwr_data(
            [
                (addr, 0, 1, pointer(reg)),  # Write cmd register.
                (addr, I2C_M_RD, 1, pointer(result)),  # Read 1 byte as result.
            ]
        )
        # Make ioctl call and return result data.
        ioctl(self._device.fileno(), I2C_RDWR, request)
        return result.value

    def read_word_data(self, addr, cmd):
        """Read a word (2 bytes) from the specified cmd register of the device.
        Note that this will interpret data using the endianness of the processor
        running Python (typically little endian)!
        """
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        # Build ctypes values to marshall between ioctl and Python.
        reg = c_uint8(cmd)
        result = c_uint16()
        # Build ioctl request.
        request = make_i2c_rdwr_data(
            [
                (addr, 0, 1, pointer(reg)),  # Write cmd register.
                (
                    addr,
                    I2C_M_RD,
                    2,
                    cast(pointer(result), POINTER(c_uint8)),
                ),  # Read word (2 bytes).
            ]
        )
        # Make ioctl call and return result data.
        ioctl(self._device.fileno(), I2C_RDWR, request)
        return result.value

    def read_block_data(self, addr, cmd):
        """Perform a block read from the specified cmd register of the device.
        The amount of data read is determined by the first byte send back by
        the device.  Data is returned as a bytearray.
        """
        # TODO: Unfortunately this will require calling the low level I2C
        # access ioctl to trigger a proper read_block_data.  The amount of data
        # returned isn't known until the device starts responding so an I2C_RDWR
        # ioctl won't work.
        raise NotImplementedError()

    def read_i2c_block_data(self, addr, cmd, length=32):
        """Perform a read from the specified cmd register of device.  Length number
        of bytes (default of 32) will be read and returned as a bytearray.
        """
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        # Build ctypes values to marshall between ioctl and Python.

        # convert register into bytearray
        if not isinstance(cmd, (bytes, bytearray)):
            reg = cmd  # backup
            cmd = bytearray(1)
            cmd[0] = reg

        cmdstring = create_string_buffer(len(cmd))
        for i, val in enumerate(cmd):
            cmdstring[i] = val

        result = create_string_buffer(length)

        # Build ioctl request.
        request = make_i2c_rdwr_data(
            [
                (
                    addr,
                    0,
                    len(cmd),
                    cast(cmdstring, POINTER(c_uint8)),
                ),  # Write cmd register.
                (addr, I2C_M_RD, length, cast(result, POINTER(c_uint8))),  # Read data.
            ]
        )

        # Make ioctl call and return result data.
        ioctl(self._device.fileno(), I2C_RDWR, request)
        return bytearray(
            result.raw
        )  # Use .raw instead of .value which will stop at a null byte!

    def write_quick(self, addr):
        """Write a single byte to the specified device."""
        # What a strange function, from the python-smbus source this appears to
        # just write a single byte that initiates a write to the specified device
        # address (but writes no data!).  The functionality is duplicated below
        # but the actual use case for this is unknown.
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        # Build ioctl request.
        request = make_i2c_rdwr_data(
            [
                (addr, 0, 0, None),
            ]
        )  # Write with no data.
        # Make ioctl call and return result data.
        ioctl(self._device.fileno(), I2C_RDWR, request)

    def write_byte(self, addr, val):
        """Write a single byte to the specified device."""
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        self._select_device(addr)
        data = bytearray(1)
        data[0] = val & 0xFF
        self._device.write(data)

    def write_bytes(self, addr, buf):
        """Write many bytes to the specified device. buf is a bytearray"""
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        self._select_device(addr)
        self._device.write(buf)

    def write_byte_data(self, addr, cmd, val):
        """Write a byte of data to the specified cmd register of the device."""
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        # Construct a string of data to send with the command register and byte value.
        data = bytearray(2)
        data[0] = cmd & 0xFF
        data[1] = val & 0xFF
        # Send the data to the device.
        self._select_device(addr)
        self._device.write(data)

    def write_word_data(self, addr, cmd, val):
        """Write a word (2 bytes) of data to the specified cmd register of the
        device.  Note that this will write the data in the endianness of the
        processor running Python (typically little endian)!
        """
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        # Construct a string of data to send with the command register and word value.
        data = struct.pack("=BH", cmd & 0xFF, val & 0xFFFF)
        # Send the data to the device.
        self._select_device(addr)
        self._device.write(data)

    def write_block_data(self, addr, cmd, vals):
        """Write a block of data to the specified cmd register of the device.
        The amount of data to write should be the first byte inside the vals
        string/bytearray and that count of bytes of data to write should follow
        it.
        """
        # Just use the I2C block data write to write the provided values and
        # their length as the first byte.
        data = bytearray(len(vals) + 1)
        data[0] = len(vals) & 0xFF
        data[1:] = vals[0:]
        self.write_i2c_block_data(addr, cmd, data)

    def write_i2c_block_data(self, addr, cmd, vals):
        """Write a buffer of data to the specified cmd register of the device."""
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        # Construct a string of data to send, including room for the command register.
        data = bytearray(len(vals) + 1)
        data[0] = cmd & 0xFF  # Command register at the start.
        data[1:] = vals[0:]  # Copy in the block data (ugly but necessary to ensure
        # the entire write happens in one transaction).
        # Send the data to the device.
        self._select_device(addr)
        self._device.write(data)

    def process_call(self, addr, cmd, val):
        """Perform a smbus process call by writing a word (2 byte) value to
        the specified register of the device, and then reading a word of response
        data (which is returned).
        """
        assert (
            self._device is not None
        ), "Bus must be opened before operations are made against it!"
        # Build ctypes values to marshall between ioctl and Python.
        data = create_string_buffer(struct.pack("=BH", cmd, val))
        result = c_uint16()
        # Build ioctl request.
        request = make_i2c_rdwr_data(
            [
                (addr, 0, 3, cast(pointer(data), POINTER(c_uint8))),  # Write data.
                (
                    addr,
                    I2C_M_RD,
                    2,
                    cast(pointer(result), POINTER(c_uint8)),
                ),  # Read word (2 bytes).
            ]
        )
        # Make ioctl call and return result data.
        ioctl(self._device.fileno(), I2C_RDWR, request)
        # Note the python-smbus code appears to have a rather serious bug and
        # does not return the result value!  This is fixed below by returning it.
        return result.value
