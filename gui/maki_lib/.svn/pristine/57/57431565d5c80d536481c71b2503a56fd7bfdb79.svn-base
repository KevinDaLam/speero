from MicIO import MicIO
from MicFilter import MicFilter
import numpy as np
import argparse

PNP_MIC = 'USB PnP Audio Device'
PNP_MIC_MAX_INPUT_CHANNELS = 1
FILTER_SPECS = '100,12000,4'

recording = []
def record(data):
    global recording
    audio = np.frombuffer(data, dtype=np.int16).tolist()
    recording += audio

def main():
    custom_formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=100)
    p = argparse.ArgumentParser(formatter_class=custom_formatter)

    p.add_argument('--internal-mic', action='store_true', required=False)
    p.add_argument('--noise-cal', type=int, required=False)
    p.add_argument('--filter-specs', type=str, required=False)
    args = p.parse_args()

    device_id = None
    noise_cal_s = 1
    output_wav = 'MicLoopback.wav'
    output_wav_filtered = '%s-filtered.wav' % output_wav.split('.')[0]
    filter_specs = FILTER_SPECS

    if not args.internal_mic:
        micIO = MicIO()
        for i in range(micIO.pyaudio_io.get_device_count()):
            dev = micIO.pyaudio_io.get_device_info_by_index(i)
            if dev['name'] == PNP_MIC and dev['maxInputChannels'] == PNP_MIC_MAX_INPUT_CHANNELS:
                device_id = i
        if device_id:
            print('Using external mic: %s' % PNP_MIC)
        else:
            print('Could not find external mic: %s' % PNP_MIC)
            return

    if args.noise_cal:
        noise_calibration_s = args.noise_cal

    if args.filter_specs:
        filter_specs = args.filter_specs

    filter_specs = list(map(int, filter_specs.split(',')))
    if len(filter_specs) is not 3:
        print("Must specify filter specs with LOW,HIGH,ORDER -- e.g. -f 100,12000,3")
        return
    filter_lowf = filter_specs[0]
    filter_highf = filter_specs[1]
    filter_order = filter_specs[2]
    print('Filter specs: {0}hz-{1}hz, order={2}'.format(filter_lowf, filter_highf, filter_order))

    micIO = MicIO()
    micFilter = MicFilter()

    input('Press any key to begin calibrating noise levels for %d second(s)' % noise_cal_s)
    micFilter.calibrate_noise(seconds=noise_cal_s, device_id=device_id)
    print('Noise calibration finished')

    try:
        while True:
            recording.clear()

            input('Press any key to begin recording')
            micIO.listen(record, device_id)

            input('Recording... press any key to stop recording')
            micIO.stop()

            audio_unfiltered = np.array(recording)
            audio_unfiltered = audio_unfiltered.astype(np.int16)
            micIO.save(output_wav, audio_unfiltered)
            print('Saved raw recording to %s' % output_wav)

            audio_filtered = MicFilter.bandpass(recording, fs=MicIO.SamplingFrequency, lowf=filter_specs[0], highf=filter_specs[1], order=filter_specs[2])
            audio_filtered = micFilter.trim_beginning_silence(audio_clip=audio_filtered)
            audio_filtered = micFilter.remove_noise(audio_filtered)
            audio_filtered = audio_filtered.astype(np.int16)
            micIO.save(output_wav_filtered, audio_filtered)
            print('Saved filtered recording to %s' % output_wav_filtered)

            cmd = input('Playback? (raw/filtered/no) ')

            while cmd == 'raw' or cmd == 'r' or cmd == 'filtered' or cmd == 'f':
                if cmd == 'filtered' or cmd == 'f':
                    micIO.play(output_wav_filtered)
                else:
                    micIO.play(output_wav)
                cmd = input('Playback? (raw/filtered/no) ')

    except KeyboardInterrupt:
        print('\n')
        pass

if __name__ == "__main__":
    main()
