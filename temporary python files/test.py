import glob
import scipy.io.wavfile as readWav
import numpy as np
import sounddevice as sd
import librosa
import normalize_sound_file
from chord import maskingCurve
from helpers import assignDynamics, constants, findPeaks
import MFCC
import lpc_coeffs
import pickle
import matplotlib.pyplot as plt
from collections.abc import MutableMapping

path = 'c:\\samples\\'
dynamics_list = np.loadtxt("orch_dynyt.txt", delimiter=' ', dtype='U20,int, int, int', unpack=True) #Read dynamics as string, int, int, int
fs= constants.fs
folders = [f for f in glob.glob(path + "**/**/**/**")]
print(len(folders))
print(folders)
test_range_start=0
test_range_end=len(folders)-1
#orchestra = dict() #Create empty dictionary for orchestra
with open('orchestra.pickle', 'rb') as handle:
    orchestra = pickle.load(handle)
#print(orchestra)
#Cut data to 1 sec chunk and apply hanning-window

def cutSample(data):
    fs=44100
    # data=data[:, 0] #Signal to mono
    data = librosa.to_mono(data) #signal to mono
    window = np.hanning(fs)
    if len(data)<fs:
        data=np.concatenate((data, np.zeros(fs-len(data))), axis=None)
    else:
        data=data[0:fs]
    data=data * window
    return data

def nested_update(d, v):
    for key in v:
        if key in d and isinstance(d[key], MutableMapping) and isinstance(v[key], MutableMapping):
            nested_update(d[key], v[key])
        else:
            d[key] = v[key]

def add_to_database (parameters, noteNumber, data, orchestra):
    instrument = parameters[2]
    tech = parameters[3]
    dyn = parameters[4]
    #note = parameters[5]
    dyn_db = assignDynamics.assign_dynamics(dyn, instrument, dynamics_list)  # function parameters: dynamics, instrument name, dynamics list
    data = cutSample(data)
    data = normalize_sound_file.normalize_audio_file(data, dyn_db) #Set sound file level according to the loaded text file
    #print("data normalized")
    #mfcc_data=librosa.feature.mfcc(y=data,sr=fs,n_mfcc=12,win_length=fs)
    M = len(data) #Length of data (should be 44100)
    spectrum = np.fft.fft(data, axis=0)[:M // 2 + 1:-1] #Calculate the fft
    #print("spectrum calculated")
    S = np.abs(spectrum) #Get rid of complex numbers
    S = 20 * np.log10(S) #dB values of data
    try:
        masking_freq, masking_threshold = maskingCurve.maskingCurve(S, noteNumber) #Calculate the masking curve
    except:
        print("Masking calculation fail, using flat masking curve")
        masking_freq = constants.threshold[:, 0]
        masking_threshold = np.ones(106)
    #print("masking calculated")
    mfcc_data, centroid = MFCC.custom_mfcc(data) #Calculate mfcc and spectral centroid
    #print("mfcc calculated")
    LpcLocs, LpcFreqs = lpc_coeffs.lpc_coeffs(data) #calculate LPC-frequency response
    #print("lpc calculated")
    #Add everything to database (except fft spectrum):
    nested_update(orchestra, {instrument:{tech:{dyn:{noteNumber:{"data":data, "masking_curve":masking_threshold, "masking_locs":masking_freq, "lpc_curve":LpcFreqs, "lpc_locs":LpcLocs, "mfcc":mfcc_data, "centroid":centroid}}}}})
    return orchestra

number = 127

for f in range(test_range_start, test_range_end):

    previous=f
    nextOne=f
    if f>0:
        previous=f-1
    if f<len(folders):
        nextOne=f+1
    names = folders[f].split('\\')
    previous_names = folders[previous].split('\\')
    next_names = folders[nextOne].split('\\')
    instrument = names[-4]
    tech = names[-3]
    dyn = names[-2]
    note = names[-1]
    #oldNumber = number
    number = int(names[-1].split('.wav')[0])
    previous_number = int(previous_names[-1].split('.wav')[0])
    next_number = int(next_names[-1].split('.wav')[0])
    print(folders[f])
    print(f)
    print (number)
    data, rate = librosa.load(folders[f], sr=44100)
    if previous_number>number:
        for i in range(1,3): #Resample data three half steps down
            print("transposing down")
            orchestra = add_to_database(names, number, data, orchestra)
            resample_down_data = librosa.effects.pitch_shift(data, rate, n_steps=-i)
            new_number=number-i
            orchestra = add_to_database(names, new_number, resample_down_data, orchestra)
            del resample_down_data
            del new_number

    elif next_number>number+1 and next_number<number+7: #Check if there's gaps in chromatic scale
        for i in range(1,next_number-number):
            print("filling the gaps")
            orchestra = add_to_database(names, number, data, orchestra)
            fill_data = librosa.effects.pitch_shift(data, rate, n_steps=i)
            new_number=number+i
            orchestra = add_to_database(names, new_number, fill_data, orchestra)
            del fill_data
            del new_number

    elif next_number<number and number<95: #Resample data 5 steps up
        for i in range(1, 5):
            print("transposing up")
            orchestra = add_to_database(names, number, data, orchestra)
            resample_up_data = librosa.effects.pitch_shift(data, rate, n_steps=i)
            new_number=number+i
            orchestra = add_to_database(names, new_number, resample_up_data, orchestra)
            del resample_up_data
            del new_number

    else:
        orchestra = add_to_database(names, number, data, orchestra)

    # data, rate = librosa.load(f, sr=44100)
    #sd.play(data, rate)
    #status = sd.wait()  # Wait until file is done playing
    # print(len(data))
    del number
    del data
    if f % 500 == 0:
        file = "orchestra%s" % f
        with open(file, 'wb') as fil:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(orchestra, fil, pickle.HIGHEST_PROTOCOL)

file = "orchestra%s" % f
with open(file, 'wb') as fil:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(orchestra, fil, pickle.HIGHEST_PROTOCOL)