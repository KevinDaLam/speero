#!/usr/bin/env python

import serial
import time
import struct
import binascii
import sys
import ctypes

DEBUG_MESSAGES = True

NUM_MOTORS = 2

STATE_START = 0
STATE_PRE_DATA = 1
STATE_DATA = 2


class DataStruct(ctypes.Structure):
    '''
    CType Struct to load data from the UART buffer
    Used to load the different datatypes coming from C in the firmware
    '''
    _pack_ = 1
    _fields_ = [("motor_positions", ctypes.c_uint16 * NUM_MOTORS)]


class UARTDriver(object):

    def __init__(self, port, baud_rate):
        '''
        Initializes serial port with corresponding parameters

        Args:
            port (str): address of UART device
            baud_rate (int): baud rate of serial port
        '''

        self.ser = None
        self.start_bytes = b'\xff\xee\xdd'

        print("Opening serial port...")
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        self.ser.flush()
        self.ser.flushInput()
        print("Opened serial port")

    def transmit(self, command_code, data=None):
        '''
        Args:
            data (:obj:'list' of bytes / str: byte string literal / :obj:'bytearray'): 
                bytes to be sent through UART

        Returns:
            bool: True if successful, False otherwise
        '''

        ser = self.ser

        # 'H' indicates unsigned short (2 bytes)
        length_bytes = struct.pack('H', len(data))
        data_bytes = bytearray(data)

        crc_bytes = self.generate_crc(data_bytes)

        ser.write(self.start_bytes)
        ser.write(command_code)
        ser.write(length_bytes)
        ser.write(data_bytes)
        ser.write(crc_bytes)

        if DEBUG_MESSAGES:
            print("Transmitted: ")
            self.print_bytes(self.start_bytes + command_code +
                             length_bytes + data_bytes + crc_bytes)

    def shutdown(self):
        '''
        Closes active serial port.
        '''
        print("UART Driver - Shutting Down...")
        self.ser.close()

    def generate_crc(self, data):
        '''
        Computes CRC-32, 32-bit checksum of data and converts to byte string literal.
        AND Mask used to generate same numeric value across all Python versions and platforms
        Reference: https://docs.python.org/3.2/library/binascii.html

        Args:
            data (str): byte string literal of message data
        Returns:
            str: byte string literal of 32-bit crc

        '''

        crc = binascii.crc32(data) & 0xffffffff
        return struct.pack('I', crc)

    def print_bytes(self, message_bytes):
        '''
        Prints through ROS logger hexadecimal format of an array of values.
        Individual values must be no larger than 1 byte (Etc. Int - 0 to 255)

        Args:
            message_bytes (:obj:'list' or str: byte string literal): bytes to be printed
        '''

        msg = "".join('0x%x ' % b for b in bytearray(message_bytes))
        print(msg)