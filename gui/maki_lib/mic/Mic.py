from .MicIO import MicIO
import socket
import select
import threading
import numpy as np
import time
import sys

SyncMessageSize = sys.getsizeof(int())
SyncTimeout = 30

class MicTransmitter:
    def __init__(self):
        self.micIO = MicIO()
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sync_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sync_socket.settimeout(SyncTimeout)

    def connect(self, host, port1, port2):
        print('MicTransmitter: Connecting to %s on ports %d,%d ...' % (host, port1, port2))

        try:
            self.audio_socket.connect((host,port1))
            self.sync_socket.connect((host, port2))
        except:
            print('MicTransmitter: Connection refused')
            return False

        print('MicTransmitter: Mic connection established')
        return True

    def disconnect(self):
        self.audio_socket.close()
        self.sync_socket.close()

    def audio_callback(self, data):
        self.audio_socket.sendall(data)

    def start(self, device_index=None):
        self.micIO.listen(self.audio_callback, device_index)

    def stop(self):
        self.micIO.stop()
        self.sync_socket.sendall(bytes([0]))

    def sync_wait(self):
        msg = 0
        r, _, _ = select.select([self.sync_socket], [], [], SyncTimeout)

        if r:
            try:
                msg = self.sync_socket.recv(SyncMessageSize)
                msg = int.from_bytes(msg, 'little')
            except:
                pass
        else:
            print('MicTransmitter: Sync error timeout')

        return msg

    def sync_post(self, msg=0):
        msg = bytes([int(msg)])
        self.sync_socket.sendall(msg)

class MicReceiver:
    def __init__(self, callback):
        self.callback = callback

        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sync_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.audio_clientsocket = None
        self.sync_clientsocket = None

    def connect(self, host, port1, port2):
        self.audio_socket.bind((host, port1))
        self.sync_socket.bind((host, port2))

        self.audio_socket.listen(1)
        self.sync_socket.listen(1)

        print('MicReceiver: Waiting for connections to %s on ports %d,%d ...' % (host, port1, port2))

        (self.audio_clientsocket, _) = self.audio_socket.accept()
        (self.sync_clientsocket, _) = self.sync_socket.accept()

        self.sync_clientsocket.settimeout(SyncTimeout)

        print('MicReceiver: Mic connection established')

    def disconnect(self):
        self.audio_socket.close()
        self.sync_socket.close()

    def listen(self):
        self.sync_clientsocket.setblocking(False)

        while True:
            try:
                data = self.audio_clientsocket.recv(MicIO.FramesPerBuffer)
                if not data:
                    break
            except:
                break
            try:
                self.sync_clientsocket.recv(SyncMessageSize)
                break
            except:
                pass

            data = np.frombuffer(data, dtype=np.int16).tolist()
            if self.callback:
                self.callback(data)

        self.sync_clientsocket.settimeout(SyncTimeout)
        
    def sync_wait(self):
        msg = 0
        r, _, _ = select.select([self.sync_clientsocket], [], [], SyncTimeout)

        if r:
            try:
                msg = self.sync_clientsocket.recv(SyncMessageSize)
                msg = int.from_bytes(msg, 'little')
            except:
                pass
        else:
            print('MicReceiever: Sync error timeout')

        return msg

    def sync_post(self, msg=0):
        msg = bytes([int(msg)])
        self.sync_clientsocket.sendall(msg)

