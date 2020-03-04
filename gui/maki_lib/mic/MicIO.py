import pyaudio
import numpy as np
import wave
import scipy.signal
import scipy.io.wavfile as wavfile

class MicIO:
    NumberOfChannels = 1
    SamplingFrequency = 48000
    FramesPerBuffer = 1024

    def __init__(self):
        self.pyaudio_io = pyaudio.PyAudio()
        self.pyaudio_stream = None
        self.user_callback = None

    def terminate(self):
        self.pyaudio_io.terminate()

    def callback(self, in_data, frame_count, time_info, status):
        self.user_callback(in_data)
        return (None, pyaudio.paContinue)

    def listen(self, callback, device_index=None):
        self.user_callback = callback
        self.pyaudio_stream = self.pyaudio_io.open(format=pyaudio.paInt16,
                                                   channels=MicIO.NumberOfChannels, 
                                                   rate=MicIO.SamplingFrequency, 
                                                   input=True, 
                                                   input_device_index=device_index, 
                                                   frames_per_buffer=MicIO.FramesPerBuffer, 
                                                   stream_callback=self.callback)

    def stop(self):
        self.pyaudio_stream.stop_stream()
        self.pyaudio_stream.close()

    def save(self, output_wav, data, fs=None):
        if not fs:
            fs = MicIO.SamplingFrequency

        wavfile.write(output_wav, fs, data)

    def play(self, wavfile, device_index=None, volume_multiplier=1, resample_freq=None):
        wf = wave.open(wavfile, 'rb')
        data = wf.readframes(MicIO.FramesPerBuffer)
        
        if volume_multiplier != 1:
            data = bytes(np.frombuffer(data)*volume_multiplier)

        sample_freq = wf.getframerate()
        if resample_freq:
            data = bytes(scipy.signal.resample(np.frombuffer(data), resample_freq))
            sample_freq = resample_freq

        stream = self.pyaudio_io.open(format=self.pyaudio_io.get_format_from_width(wf.getsampwidth()), 
                                      channels=wf.getnchannels(), 
                                      rate=sample_freq,
                                      output=True, 
                                      output_device_index=device_index)

        while len(data):
            stream.write(data)
            data = wf.readframes(MicIO.FramesPerBuffer)

        stream.close()

    '''
    @ param trim_start_ms is the amount to trim from the beginning
    @ param trim_end_ms is the amount to trim from the end
    @ param fade_ms is the amount to fade out from the trimmed end
    '''
    def edit(self, wav, trim_start_ms=0, trim_end_ms=0, fade_ms=0):
        fs, data = wavfile.read(wav)
        
        data = data.tolist()

        trim_start = trim_start_ms * (fs // 1000)
        trim_end = len(data) - (trim_end_ms * (fs // 1000))
        fade = trim_end - (fade_ms * (fs // 1000))

        if trim_start > len(data) or trim_end < 0 or fade > trim_end:
            print('MicIO: Edit timestamp argument error')
            return None

        data = data[trim_start:trim_end]

        if fade_ms:
            fade = len(data) - (fade_ms * (fs // 1000))
            fade_multiplier = 1
            fade_multiplier_step = 1/(len(data) - fade)

            for i in range(fade, len(data)):
                data[i] = round(data[i]*fade_multiplier)
                fade_multiplier -= fade_multiplier_step

        edited_wav = wav.split('.')[0] + '-edit.wav'
        self.save(edited_wav, np.array(data, dtype=np.int16), fs=fs)

        return edited_wav

    def list_audio_devices(self):
        for i in range(self.pyaudio_io.get_device_count()):
            dev = self.pyaudio_io.get_device_info_by_index(i)
            print(dev)

    def search_audio_devices(self, device_name):
        for i in range(self.pyaudio_io.get_device_count()):
            dev = self.pyaudio_io.get_device_info_by_index(i)
            if (dev['name'] == device_name):
                return i
        return None

