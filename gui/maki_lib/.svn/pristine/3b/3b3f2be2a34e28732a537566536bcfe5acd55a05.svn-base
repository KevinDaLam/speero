from scipy.signal import butter, lfilter
from MicIO import MicIO
import numpy as np
import noisereduce as nr
import time

class MicFilter:
    def __init__(self):
        self.micIO = MicIO()
        self.noise_clip = None

    @staticmethod
    def bandpass(data, fs, lowf, highf, order):
        nyq = 0.5 * fs
        lowf /= nyq
        highf /= nyq
        num, den = butter(order, [lowf, highf], btype='band')
        filtered = lfilter(num, den, data)
        return filtered

    def record_noise(self, data):
        noise = np.frombuffer(data, dtype=np.int16)
        self.noise_clip = np.append(self.noise_clip, noise)

    def calibrate_noise(self, seconds, device_id=None):
        self.noise_clip = np.array([])
        self.micIO.listen(self.record_noise, device_index=device_id)
        time.sleep(seconds)
        self.micIO.stop()

    def remove_noise(self, audio_clip):
        if self.noise_clip.size == 0:
            print('Error: must calibrate noise levels before removing noise')
            return None
        return nr.reduce_noise(audio_clip=audio_clip, noise_clip=self.noise_clip)

    def trim_beginning_silence(self, audio_clip, fs=MicIO.SamplingFrequency, rms_window_ms=10):
        rms_window = rms_window_ms * (fs // 1000)
        if len(audio_clip) <= rms_window:
            print('Input audio should be longer than %d ms' % rms_window_ms)
            return None

        safety_factor = 1.5
        noise_rms = np.sqrt(np.mean(self.noise_clip**2)) * safety_factor

        audio_clip_squared = audio_clip ** 2

        index = 0
        current_sum = np.sum(audio_clip_squared[index:index+rms_window])
        rms = np.sqrt(current_sum/rms_window)
        index += 1

        while rms < noise_rms and index < audio_clip_squared.size:
            current_sum -= audio_clip_squared[index-1]
            current_sum += audio_clip_squared[index]
            rms = np.sqrt(current_sum/rms_window)
            index += 1

        if index == audio_clip_squared.size:
            print('Trim: did not find any beginning silence')
            return audio_clip

        return audio_clip[index:]
