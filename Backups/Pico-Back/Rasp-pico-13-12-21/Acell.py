# -*- coding: utf-8 -*-
"""
Python driver for the QMC5883L 3-Axis Magnetic Sensor.

Usage example:

  import py_qmc5883l
  sensor = py_qmc5883l.QMC5883L()
  m = sensor.get_magnet()
  print(m)

you will get three 16 bit signed integers, representing the values
of the magnetic sensor on axis X, Y and Z, e.g. [-1257, 940, -4970].
"""

import machine
import math
import time

__author__ = "Niccolo Rigacci"
__copyright__ = "Copyright 2018 Niccolo Rigacci <niccolo@rigacci.org>"
__license__ = "GPLv3-or-later"
__email__ = "niccolo@rigacci.org"
__version__ = "0.1.4"

def andbytes(a_byte, b_byte):
    if type(a_byte) == int: a_byte = bytes([a_byte])
    if type(b_byte) == int: b_byte = bytes([b_byte])
    return True if ord(bytes([a & b for a, b in zip(a_byte[:], b_byte[:])][:]).decode()) else False 

DFLT_BUS = 1
DFLT_ADDRESS = 0x0D

REG_XOUT_LSB = 0x00     # Output Data Registers for magnetic sensor.
REG_XOUT_MSB = 0x01
REG_YOUT_LSB = 0x02
REG_YOUT_MSB = 0x03
REG_ZOUT_LSB = 0x04
REG_ZOUT_MSB = 0x05
REG_STATUS_1 = 0x06     # Status Register.
REG_TOUT_LSB = 0x07     # Output Data Registers for temperature.
REG_TOUT_MSB = 0x08
REG_CONTROL_1 = 0x09    # Control Register #1.
REG_CONTROL_2 = 0x0a    # Control Register #2.
REG_RST_PERIOD = 0x0b   # SET/RESET Period Register.
REG_CHIP_ID = 0x0d      # Chip ID register.

# Flags for Status Register #1.
STAT_DRDY = 0b00000001  # Data Ready.
STAT_OVL = 0b00000010   # Overflow flag.
STAT_DOR = 0b00000100   # Data skipped for reading.

# Flags for Status Register #2.
INT_ENB = 0b00000001    # Interrupt Pin Enabling.
POL_PNT = 0b01000000    # Pointer Roll-over.
SOFT_RST = 0b10000000   # Soft Reset.

# Flags for Control Register 1.
MODE_STBY = 0b00000000  # Standby mode.
MODE_CONT = 0b00000001  # Continuous read mode.

ODR_10HZ  = 0b00000000   # Output Data Rate Hz.
ODR_50HZ  = 0b00000100
ODR_100HZ = 0b00001000
ODR_200HZ = 0b00001100

RNG_2G = 0b00000000     # Range 2 Gauss: for magnetic-clean environments.
RNG_8G = 0b00010000     # Range 8 Gauss: for strong magnetic fields.

OSR_512 = 0b00000000    # Over Sample Rate 512: less noise, more power.
OSR_256 = 0b01000000
OSR_128 = 0b10000000
OSR_64  = 0b11000000     # Over Sample Rate 64: more noise, less power.


class QMC5883L:
    """Interface for the QMC5883l 3-Axis Magnetic Sensor."""
    def __init__(self, i2c_bus = DFLT_BUS, address = DFLT_ADDRESS, output_data_rate = ODR_50HZ, output_range = RNG_2G, oversampling_rate = OSR_512):
        if type(i2c_bus) == machine.I2C: self.bus = i2c_bus 
        elif type(i2c_bus) == int :      self.bus = machine.I2C(i2c_bus)

        self.address      = address
        self.output_range = output_range
        self._declination = 0.0
        self._calibration = [[1.0, 0.0, 0.0],
                             [0.0, 1.0, 0.0],
                             [0.0, 0.0, 1.0]]
                
        self.mode_cont = (MODE_CONT | output_data_rate | output_range | oversampling_rate)
        self.mode_stby = (MODE_STBY | ODR_10HZ | RNG_2G | OSR_64)
        self.buff      = REG_CHIP_ID
        self.mode_continuous()
        
        chip_id = self._read_byte( REG_CHIP_ID )
        if chip_id != 0xff: print("Chip ID returned 0x%x instead of 0xff; is the wrong chip?" %chip_id)        


    def __del__(self):
        """Once finished using the sensor, switch to standby mode."""
        self.mode_standby()

    def mode_continuous(self):
        """Set the device in continuous read mode."""
        self.buff = bytearray([SOFT_RST])
        self._write_byte(REG_CONTROL_2, self.buff)  # Soft reset
        self.buff = bytearray([INT_ENB])
        self._write_byte(REG_CONTROL_2, self.buff)  # Disable interrupt.
        self.buff = bytearray([0x01])
        self._write_byte(REG_RST_PERIOD, self.buff)  # Define SET/RESET period.
        self.buff = bytearray([self.mode_cont])
        self._write_byte(REG_CONTROL_1, self.buff)  # Set operation mode.

    def mode_standby(self):
        """Set the device in standby mode."""
        self.buff = bytearray([SOFT_RST])
        self._write_byte(REG_CONTROL_2, self.buff)
        self.buff = bytearray([INT_ENB])
        self._write_byte(REG_CONTROL_2, self.buff)
        self.buff = bytearray([0x01])
        self._write_byte(REG_RST_PERIOD, self.buff)
        self.buff = bytearray([self.mode_stby])
        self._write_byte(REG_CONTROL_1, self.buff)  # Set operation mode.


    def _write_byte(self, registry, value ):
        self.bus.writeto_mem(self.address, registry, value )
        
    def _read_byte(self, registry):
        return self.bus.readfrom_mem(self.address, registry, 1)[0]

    def _read_word(self, registry):
        """Read a two bytes value stored as LSB and MSB."""
        val = self.bus.readfrom_mem(self.address, registry, 2)
        return ((val[1]<<8) + val[0])


    def _read_word_2c(self, registry):
        """Calculate the 2's complement of a two bytes value."""
        val = self._read_word(registry)
        if val >= 0x8000:  # 32768
            return val - 0x10000  # 65536
        else:
            return val


    def get_data(self):
        """Read data from magnetic and temperature data registers."""
        i = 0
        [x, y, z, t] = [None, None, None, None]
        while i < 20:  # Timeout after about 0.20 seconds.
            status = self._read_byte(REG_STATUS_1)
            if andbytes( status, STAT_OVL ):
                # Some values have reached an overflow.
                msg = ("Magnetic sensor overflow.")
                if self.output_range == RNG_2G:
                    msg += " Consider switching to RNG_8G output range."
            if andbytes( status, STAT_DOR ):
                # Previous measure was read partially, sensor in Data Lock.
                x = self._read_word_2c(REG_XOUT_LSB)
                y = self._read_word_2c(REG_YOUT_LSB)
                z = self._read_word_2c(REG_ZOUT_LSB)
                continue

            if andbytes(status, STAT_DRDY ):
                # Data is ready to read.
                x = self._read_word_2c(REG_XOUT_LSB)
                y = self._read_word_2c(REG_YOUT_LSB)
                z = self._read_word_2c(REG_ZOUT_LSB)
                t = self._read_word_2c(REG_TOUT_LSB)
                break
            else:
                # Waiting for DRDY.
                time.sleep(0.01)
                i += 1
        return [x, y, z, t]
    

    def get_magnet_raw(self):
        """Get the 3 axis values from magnetic sensor."""
        [x, y, z, t] = self.get_data()
        return [x, y, z]
    

    def get_magnet(self):
        """Return the horizontal magnetic sensor vector with (x, y) calibration applied."""
        [x, y, z] = self.get_magnet_raw()
        if x is None or y is None:
            [x1, y1] = [x, y]
        else:
            c = self._calibration
            x1 = x * c[0][0] + y * c[0][1] + c[0][2]
            y1 = x * c[1][0] + y * c[1][1] + c[1][2]
        return [x1, y1]


    def get_bearing_raw(self):
        """Horizontal bearing (in degrees) from magnetic value X and Y."""
        [x, y, z] = self.get_magnet_raw()
        if x is None or y is None:
            return None
        else:
            b = math.degrees(math.atan2(y, x))
            if b < 0:
                b += 360.0
            return b


    def get_bearing(self):
        """Horizontal bearing, adjusted by calibration and declination."""
        [x, y] = self.get_magnet()
        if x is None or y is None:
            return None
        else:
            b = math.degrees(math.atan2(y, x))
            if b < 0:
                b += 360.0
            b += self._declination
            if b < 0.0:
                b += 360.0
            elif b >= 360.0:
                b -= 360.0
        return b


    def get_temp(self):
        """Raw (uncalibrated) data from temperature sensor."""
        [x, y, z, t] = self.get_data()
        return t


    def set_declination(self, value):
        """Set the magnetic declination, in degrees."""
        try:
            d = float(value)
            if d < -180.0 or d > 180.0:
                print(u'Declination must be >= -180 and <= 180.')
            else:
                self._declination = d
        except:
            print(u'Declination must be a float value.')


    def get_declination(self):
        """Return the current set value of magnetic declination."""
        return self._declination


    def set_calibration(self, value):
        """Set the 3x3 matrix for horizontal (x, y) magnetic vector calibration."""
        c = [[1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0]]
        try:
            for i in range(0, 3):
                for j in range(0, 3):
                    c[i][j] = float(value[i][j])
            self._calibration = c
        except:
            print(u'Calibration must be a 3x3 float matrix.')


    def get_calibration(self):
        """Return the current set value of the calibration matrix."""
        return self._calibration
    

