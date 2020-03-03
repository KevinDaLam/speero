import Mic
import sys
import time

HOST='localhost'
PORT1=2000
PORT2=2001

def received_data(data):
    pass

mode = sys.argv[1]

if mode == 'rx':
    rx = Mic.MicReceiver(received_data)
    rx.connect(HOST, PORT1, PORT2)

    rx.listen()
    msg = rx.sync_wait()
    print('Transmission was stopped. Received msg=%d.' % msg)

    rx.disconnect()

if mode == 'tx':
    msg = 3
    tx = Mic.MicTransmitter()
    success = tx.connect(HOST, PORT1, PORT2)

    if success:
        tx.start()
        input('Press any key to stop.')
        tx.stop()

        print('Stopping transmission with msg=%d.' % msg)
        tx.sync_post(msg)
        tx.disconnect()

