import MicIO
import sys
import argparse

def main():
    custom_formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=100)
    p = argparse.ArgumentParser(formatter_class=custom_formatter)
    p.add_argument('-i', '--input', type=str, required=True)
    args = p.parse_args()

    input_wavfile = args.input
    micIO = MicIO.MicIO()

    try:
        while True:
            edit_settings = input('Edit settings? (START,END,FADE) ')
            edit_settings = list(map(int, edit_settings.split(',')))

            if len(edit_settings) is not 3:
                print('Must specify edit settings with START,END,FADE -- e.g. 10,10,1000')
                return

            trim_start_ms = edit_settings[0]
            trim_end_ms = edit_settings[1]
            fade_ms = edit_settings[2]

            edited_wavfile = micIO.edit(input_wavfile, trim_start_ms=trim_start_ms, trim_end_ms=trim_end_ms, fade_ms=fade_ms)
            if not edited_wavfile:
                return

            cmd = input('Play? (input/edited/no) ')

            while cmd == 'input' or cmd == 'i' or cmd == 'edited' or cmd == 'e':
                if cmd == 'input' or cmd == 'i':
                    micIO.play(input_wavfile)
                else:
                    micIO.play(edited_wavfile)
                cmd = input('Play? (input/edited/no) ')

    except KeyboardInterrupt:
        print('')
        micIO.terminate()
        pass

if __name__ == "__main__":
    main()

