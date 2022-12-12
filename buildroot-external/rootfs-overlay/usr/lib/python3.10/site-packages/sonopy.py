# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import numpy as np
from functools import lru_cache
from scipy.fftpack import dct


def safe_log(x):
    """Prevents error on log(0) or log(-1)"""
    return np.log(np.clip(x, np.finfo(float).eps, None))


@lru_cache()  # Prevents recalculating when calling with same parameters
def filterbanks(sample_rate, num_filt, fft_len):
    """Makes a set of triangle filters focused on {num_filter} mel-spaced frequencies"""
    def hertz_to_mels(f):
        return 1127. * np.log(1. + f / 700.)

    def mel_to_hertz(mel):
        return 700. * (np.exp(mel / 1127.) - 1.)

    def correct_grid(x):
        """Push forward duplicate points to prevent useless filters"""
        offset = 0
        for prev, i in zip([x[0] - 1] + x, x):
            offset = max(0, offset + prev + 1 - i)
            yield i + offset

    # Grid contains points for left center and right points of filter triangle
    # mels -> hertz -> fft indices
    grid_mels = np.linspace(hertz_to_mels(0), hertz_to_mels(sample_rate), num_filt + 2, True)
    grid_hertz = mel_to_hertz(grid_mels)
    grid_indices = (grid_hertz * fft_len / sample_rate).astype(int)
    grid_indices = list(correct_grid(grid_indices))

    banks = np.zeros([num_filt, fft_len])

    for i, (left, middle, right) in enumerate(chop_array(grid_indices, 3, 1)):
        banks[i, left:middle] = np.linspace(0., 1., middle - left, False)
        banks[i, middle:right] = np.linspace(1., 0., right - middle, False)

    return banks


def chop_array(arr, window_size, hop_size):
    """chop_array([1,2,3], 2, 1) -> [[1,2], [2,3]]"""
    return [arr[i - window_size:i] for i in range(window_size, len(arr) + 1, hop_size)]


def power_spec(audio: np.ndarray, window_stride=(160, 80), fft_size=512):
    """Calculates power spectrogram"""
    frames = chop_array(audio, *window_stride) or np.empty((0, window_stride[0]))
    fft = np.fft.rfft(frames, n=fft_size)
    return (fft.real ** 2 + fft.imag ** 2) / fft_size


def mel_spec(audio, sample_rate, window_stride=(160, 80), fft_size=512, num_filt=20):
    """Calculates mel spectrogram (condensed spectrogram)"""
    spec = power_spec(audio, window_stride, fft_size)
    return safe_log(np.dot(spec, filterbanks(sample_rate, num_filt, spec.shape[1]).T))


def mfcc_spec(audio, sample_rate, window_stride=(160, 80),
              fft_size=512, num_filt=20, num_coeffs=13, return_parts=False):
    """Calculates mel frequency cepstrum coefficient spectrogram"""
    powers = power_spec(audio, window_stride, fft_size)
    if powers.size == 0:
        return np.empty((0, min(num_filt, num_coeffs)))

    filters = filterbanks(sample_rate, num_filt, powers.shape[1])
    mels = safe_log(np.dot(powers, filters.T))  # Mel energies (condensed spectrogram)
    mfccs = dct(mels, norm='ortho')[:, :num_coeffs]  # machine readable spectrogram
    mfccs[:, 0] = safe_log(np.sum(powers, 1))  # Replace first band with log energies
    if return_parts:
        return powers, filters, mels, mfccs
    else:
        return mfccs
