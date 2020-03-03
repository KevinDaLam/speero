from MicIO import MicIO
import sys

micIO = MicIO()

try:
    again = 'y'
    while again == 'y':
        micIO.play(sys.argv[1], device_index=None)
        again = input('Play again? (y/n) ')
except KeyboardInterrupt:
    print('')

micIO.terminate()
