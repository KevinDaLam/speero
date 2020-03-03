#!/usr/bin/env python
import uart_driver
import time
import struct
import argparse

COMMAND_MOVE_HOME = b'\x01'
COMMAND_MOVE_HAPPY = b'\x02'
COMMAND_MOVE_EXCITED = b'\x03'
COMMAND_MOVE_IDLE = b'\x04'
COMMAND_MOVE_WAVE_HELLO = b'\x05'
COMMAND_MOVE_HUG = b'\x06'
COMMAND_MOVE_WOAH = b'\x07'
COMMAND_MOVE_FORTNITE_DANCE = b'\x08'
COMMAND_RESET_TORQUE_ENABLE = b'\xaa'

def main():
    '''
    If run as standalone script connected to Arduino Uno, messages will be sent and received sequentially.
    '''

    p = argparse.ArgumentParser()
    p.add_argument('-p', '--port', type=str, required=True, help="Serial port name")
    args = p.parse_args()

    uart = uart_driver.UARTDriver(args.port, 57600)

    time.sleep(10)

    try:
        while (1):
            value = input("Please enter command:\n")
            if (value == str(1)):
                print("MOVE HOME")
                uart.transmit(COMMAND_MOVE_HOME, [])
            elif (value == str(2)):
                print("MOVE_HAPPY")
                uart.transmit(COMMAND_MOVE_HAPPY, [])
            elif (value == str(3)):
                print("MOVE_EXCITED")
                uart.transmit(COMMAND_MOVE_EXCITED, [])
            elif (value == str(4)):
                print("MOVE_IDLE")
                uart.transmit(COMMAND_MOVE_IDLE, [])
            elif (value == str(5)):
                print("MOVE_WAVE_HELLO")
                uart.transmit(COMMAND_MOVE_WAVE_HELLO, [])
            elif (value == str(6)):
                print("MOVE_HUG")
                uart.transmit(COMMAND_MOVE_HUG, [])
            elif (value == str(7)):
                print("MOVE_WAVE_WOAH")
                uart.transmit(COMMAND_MOVE_WOAH, [])
            elif (value == str(8)):
                print("MOVE_FORTNITE_DANCE")
                uart.transmit(COMMAND_MOVE_FORTNITE_DANCE, [])
            elif (value == str(9)):
                print("RESET_TORQUE_ENABLE")
                uart.transmit(COMMAND_RESET_TORQUE_ENABLE, [])

    except KeyboardInterrupt:
        uart.shutdown()

if __name__ == "__main__":
    main()