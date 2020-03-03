import sys
import time
import numpy as np
from maki_lib.mic.Mic import MicReceiver

def received_data(data):
    print(data)

host = 'localhost'
port1 = int(sys.argv[1])
port2 = int(sys.argv[2])

rx = MicReceiver(received_data)

rx.connect(host, port1, port2)
rx.listen()

input('Press enter to send results back to Speero')

rx.sync_post()
rx.disconnect()

print('Terminating mock server')

