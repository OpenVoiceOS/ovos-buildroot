# smbus.py - cffi based python bindings for SMBus based on smbusmodule.c
# Copyright (C) 2013-2015 <david.schneider@bivab.de>
#
# smbusmodule.c - Python bindings for Linux SMBus access through i2c-dev
# Copyright (C) 2005-2007 Mark M. Hoffman <mhoffman@lightlink.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""This module defines an object type that allows SMBus transactions
on hosts running the Linux kernel.  The host kernel must have I2C
support, I2C device interface support, and a bus adapter driver.
All of these can be either built-in to the kernel, or loaded from
modules.

Because the I2C device interface is opened R/W, users of this
module usually must have root permissions."""

import os

from .util import validate
from .util import int2byte
from fcntl import ioctl

from ._smbus_cffi import ffi
from ._smbus_cffi import lib as SMBUS

MAXPATH = 16


class SMBus(object):
    """SMBus([bus]) -> SMBus
    Return a new SMBus object that is (optionally) connected to the
    specified I2C device interface.
    """

    _fd = -1
    _addr = -1
    _pec = 0
    # compat mode, enables some features that are not compatible with the
    # original smbusmodule.c
    _compat = False

    def __init__(self, bus=-1):
        if bus >= 0:
            self.open(bus)

    def close(self):
        """close()

        Disconnects the object from the bus.
        """
        os.close(self._fd)
        self._fd = -1
        self._addr = -1
        self._pec = 0

    def dealloc(self):
        self.close()

    def open(self, bus):
        """open(bus)

        Connects the object to the specified SMBus.
        """
        bus = int(bus)
        path = "/dev/i2c-%d" % (bus,)
        if len(path) >= MAXPATH:
                raise OverflowError("Bus number is invalid.")
        try:
            self._fd = os.open(path, os.O_RDWR, 0)
        except OSError as e:
            raise IOError(e.errno)

    def _set_addr(self, addr):
        """private helper method"""
        if self._addr != addr:
            ioctl(self._fd, SMBUS.I2C_SLAVE, addr)
            self._addr = addr

    @validate(addr=int)
    def write_quick(self, addr):
        """write_quick(addr)

        Perform SMBus Quick transaction.
        """
        self._set_addr(addr)
        if SMBUS.i2c_smbus_write_quick(self._fd, SMBUS.I2C_SMBUS_WRITE) != 0:
            raise IOError(ffi.errno)

    @validate(addr=int)
    def read_byte(self, addr):
        """read_byte(addr) -> result

        Perform SMBus Read Byte transaction.
        """
        self._set_addr(addr)
        result = SMBUS.i2c_smbus_read_byte(self._fd)
        if result == -1:
            raise IOError(ffi.errno)
        return result

    @validate(addr=int, val=int)
    def write_byte(self, addr, val):
        """write_byte(addr, val)

        Perform SMBus Write Byte transaction.
        """
        self._set_addr(addr)
        if SMBUS.i2c_smbus_write_byte(self._fd, ffi.cast("__u8", val)) == -1:
            raise IOError(ffi.errno)

    @validate(addr=int, cmd=int)
    def read_byte_data(self, addr, cmd):
        """read_byte_data(addr, cmd) -> result

        Perform SMBus Read Byte Data transaction.
        """
        self._set_addr(addr)
        res = SMBUS.i2c_smbus_read_byte_data(self._fd, ffi.cast("__u8", cmd))
        if res == -1:
            raise IOError(ffi.errno)
        return res

    @validate(addr=int, cmd=int, val=int)
    def write_byte_data(self, addr, cmd, val):
        """write_byte_data(addr, cmd, val)

        Perform SMBus Write Byte Data transaction.
        """
        self._set_addr(addr)
        if SMBUS.i2c_smbus_write_byte_data(self._fd,
                                           ffi.cast("__u8", cmd),
                                           ffi.cast("__u8", val)) == -1:
            raise IOError(ffi.errno)

    @validate(addr=int, cmd=int)
    def read_word_data(self, addr, cmd):
        """read_word_data(addr, cmd) -> result

        Perform SMBus Read Word Data transaction.
        """
        self._set_addr(addr)
        result = SMBUS.i2c_smbus_read_word_data(self._fd, ffi.cast("__u8", cmd))
        if result == -1:
            raise IOError(ffi.errno)
        return result

    @validate(addr=int, cmd=int, val=int)
    def write_word_data(self, addr, cmd, val):
        """write_word_data(addr, cmd, val)

        Perform SMBus Write Word Data transaction.
        """
        self._set_addr(addr)
        if SMBUS.i2c_smbus_write_word_data(self._fd,
                                           ffi.cast("__u8", cmd),
                                           ffi.cast("__u16", val)) == -1:
            raise IOError(ffi.errno)

    @validate(addr=int, cmd=int, val=int)
    def process_call(self, addr, cmd, val):
        """process_call(addr, cmd, val)

        Perform SMBus Process Call transaction.

        Note: although i2c_smbus_process_call returns a value, according to
        smbusmodule.c this method does not return a value by default.

        Set _compat = False on the SMBus instance to get a return value.
        """
        self._set_addr(addr)
        ret = SMBUS.i2c_smbus_process_call(self._fd,
                                           ffi.cast("__u8", cmd),
                                           ffi.cast("__u16", val))
        if ret == -1:
            raise IOError(ffi.errno)
        if self._compat:
            return ret

    @validate(addr=int, cmd=int)
    def read_block_data(self, addr, cmd):
        """read_block_data(addr, cmd) -> results

        Perform SMBus Read Block Data transaction.
        """
        # XXX untested, the raspberry pi i2c driver does not support this
        # command
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data *")
        if SMBUS.i2c_smbus_access(self._fd,
                                  int2byte(SMBUS.I2C_SMBUS_READ),
                                  ffi.cast("__u8", cmd),
                                  SMBUS.I2C_SMBUS_BLOCK_DATA,
                                  data):
            raise IOError(ffi.errno)
        return smbus_data_to_list(data)

    @validate(addr=int, cmd=int, vals=list)
    def write_block_data(self, addr, cmd, vals):
        """write_block_data(addr, cmd, vals)

        Perform SMBus Write Block Data transaction.
        """
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data *")
        list_to_smbus_data(data, vals)
        if SMBUS.i2c_smbus_access(self._fd,
                                  int2byte(SMBUS.I2C_SMBUS_WRITE),
                                  ffi.cast("__u8", cmd),
                                  SMBUS.I2C_SMBUS_BLOCK_DATA,
                                  data):
            raise IOError(ffi.errno)

    @validate(addr=int, cmd=int, vals=list)
    def block_process_call(self, addr, cmd, vals):
        """block_process_call(addr, cmd, vals) -> results

        Perform SMBus Block Process Call transaction.
        """
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data *")
        list_to_smbus_data(data, vals)
        if SMBUS.i2c_smbus_access(self._fd, SMBUS.I2C_SMBUS_WRITE,
                                  ffi.cast("__u8", cmd),
                                  SMBUS.I2C_SMBUS_BLOCK_PROC_CALL,
                                  data):
            raise IOError(ffi.errno)
        return smbus_data_to_list(data)

    @validate(addr=int, cmd=int, len=int)
    def read_i2c_block_data(self, addr, cmd, len=32):
        """read_i2c_block_data(addr, cmd, len=32) -> results

        Perform I2C Block Read transaction.
        """
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data *")
        data.block[0] = len
        if len == 32:
            arg = SMBUS.I2C_SMBUS_I2C_BLOCK_BROKEN
        else:
            arg = SMBUS.I2C_SMBUS_I2C_BLOCK_DATA
        if SMBUS.i2c_smbus_access(self._fd,
                                  int2byte(SMBUS.I2C_SMBUS_READ),
                                  ffi.cast("__u8", cmd),
                                  arg, data):
            raise IOError(ffi.errno)
        return smbus_data_to_list(data)

    @validate(addr=int, cmd=int, vals=list)
    def write_i2c_block_data(self, addr, cmd, vals):
        """write_i2c_block_data(addr, cmd, vals)

        Perform I2C Block Write transaction.
        """
        self._set_addr(addr)
        data = ffi.new("union i2c_smbus_data *")
        list_to_smbus_data(data, vals)
        if SMBUS.i2c_smbus_access(self._fd,
                                  int2byte(SMBUS.I2C_SMBUS_WRITE),
                                  ffi.cast("__u8", cmd),
                                  SMBUS.I2C_SMBUS_I2C_BLOCK_BROKEN,
                                  data):
            raise IOError(ffi.errno)

    @property
    def pec(self):
        return self._pec

    @pec.setter
    def pec(self, value):
        """True if Packet Error Codes (PEC) are enabled"""
        pec = bool(value)
        if pec != self._pec:
            if ioctl(self._fd, SMBUS.I2C_PEC, pec):
                raise IOError(ffi.errno)
            self._pec = pec


def smbus_data_to_list(data):
    block = data.block
    return [block[i + 1] for i in range(block[0])]


def list_to_smbus_data(data, vals):
    block_max = SMBUS.I2C_SMBUS_BLOCK_MAX
    if len(vals) > block_max or len(vals) == 0:
        raise OverflowError("Third argument must be a list of at least one, "
                            "but not more than %d integers" % block_max)
    data.block[0] = len(vals)
    for i, val in enumerate(vals):
        data.block[i + 1] = val
