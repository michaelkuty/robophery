try:
    import smbus
except Exception:
    raise RuntimeError(
        "Cannot load smbus library. Please install the library.")

from robophery.interface.i2c import I2cInterface


class SMBusI2cInterface(I2cInterface):

    def __init__(self, *args, **kwargs):
        self._busnum = int(kwargs.get('busnum', 1))
        self._bus = smbus.SMBus(self._busnum)
        super(SMBusI2cInterface, self).__init__(*args, **kwargs)

    def writeRaw8(self, addr, value):
        """
        Write an 8-bit value on the bus (without register).
        """
        value = value & 0xFF
        self._log.debug(
            "Writing raw 8-bit value {0:#x} to address {1:#x}.".format(value, addr))
        self._bus.write_byte(addr, value)

    def write8(self, addr, register, value):
        """
        Write an 8-bit value to the specified register.
        """
        value = value & 0xFF
        self._bus.write_byte_data(addr, register, value)
        self._log.debug(
            "Writing 8-bit value {0:#x} to register {1:#x} at address {2:#x}.".format(value, register, addr))

    def write16(self, addr, register, value):
        """
        Write a 16-bit value to the specified register.
        """
        value = value & 0xFFFF
        self._log.debug(
            "Writing 16-bit value {0:#x} to register {1:#x} at address {2:#x}.".format(value, register, addr))
        self._bus.write_word_data(addr, register, value)

    def writeList(self, addr, register, data):
        """
        Write bytes to the specified register.
        """
        self._log.debug("Writing multiple values {0:#x} to register {1:#x} at address {2:#x}.".format(
            value, register, addr))
        self._bus.write_i2c_block_data(addr, register, data)

    def readRaw8(self, addr):
        """
        Read an 8-bit value on the bus (without register).
        """
        result = self._bus.read_byte(addr) & 0xFF
        self._log.debug(
            "Reading raw 8-bit value {0:#x} from address {1:#x}.".format(result, addr))
        return result

    def readU8(self, addr, register):
        """
        Read an unsigned byte from the specified register.
        """
        result = self._bus.read_byte_data(addr, register) & 0xFF
        self._log.debug(
            "Reading unsigned 8-bit value {0:#x} from register {1:#x} at address {2:#x}.".format(result, register, addr))
        return result

    def readS8(self, addr, register):
        """
        Read a signed byte from the specified register.
        """
        result = self.readU8(addr, register)
        if result > 127:
            result -= 256
        self._log.debug(
            "Reading signed 8-bit value {0:#x} from register {1:#x} at address {2:#x}.".format(result, register, addr))
        return result

    def readU16(self, addr, register, little_endian=True):
        """
        Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first).
        """
        result = self._bus.read_word_data(addr, register) & 0xFFFF
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        self._log.debug(
            "Reading unsigned 16-bit value {0:#x} from register {1:#x} at address {2:#x}.".format(result, register, addr))
        return result

    def readS16(self, addr, register, little_endian=True):
        """
        Read a signed 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first).
        """
        result = self.readU16(addr, register, little_endian)
        if result > 32767:
            result -= 65536
        self._log.debug(
            "Reading signed 16-bit value {0:#x} from register {1:#x} at address {2:#x}.".format(result, register, addr))
        return result

    def readList(self, addr, register, length):
        """
        Read a length number of bytes from the specified register. Results
        will be returned as a bytearray.
        """
        results = self._bus.read_i2c_block_data(addr, register, length)
        print_results = []
        for result in results:
            print_results.append("{0:#x}".format(result))
        self._log.debug("Reading {0} 8-bit values {1} from register {2:#x} at address {3:#x}.".format(
            length, ", ".join(print_results), register, addr))
        return results
