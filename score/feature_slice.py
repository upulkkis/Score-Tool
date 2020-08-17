from chord import maskingCurve_peakInput
import numpy as np

def get_feature_slice(inst, tch, dyna, note, orchestra, dummy_fft_size=22048):
    peaks = orchestra[inst][tch][dyna][note]['peaks']
    mfcc = orchestra[inst][tch][dyna][note]['mfcc']
    centroid = orchestra[inst][tch][dyna][note]['centroid']
    dummy_fft = np.ones(dummy_fft_size) + 70  # this is a dummy constant for masking calculation
    masking = maskingCurve_peakInput.maskingCurve(dummy_fft, peaks)
    return peaks, mfcc, centroid, masking