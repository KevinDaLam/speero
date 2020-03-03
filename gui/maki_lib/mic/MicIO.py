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

    def save(self, output_wav, data):
        wavfile.write(output_wav, MicIO.SamplingFrequency, data)

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

