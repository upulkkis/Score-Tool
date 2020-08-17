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
import matplotlib.pyplot as plt
from scipy.signal import freqz
from scipy.signal import find_peaks
from scipy.signal import find_peaks_cwt

#Ongelmallisia: no.99 alttohuilu, no.1218 crotale(bow) 94

n=1298 #number of sample file to pick
path = constants.path #Read the location of samples from constants
folders = [f for f in glob.glob(path + "**/**/**/**")] #Get all the files from directory structure
file = folders[n]
fileParts = file.split('\\') #get directory names as list
fs= constants.fs
print(folders[n])
orchestra = dict() #Create empty dictionary for orchestra
#print(fileParts[-4]) #Instrument name
#print(fileParts[-2]) #dynamic



dynamics_list = np.loadtxt("orch_dynyt.txt", delimiter=' ', dtype='U20,int, int, int', unpack=True) #Read dynamics as string, int, int, int
dyn_db = assignDynamics.assign_dynamics(fileParts[-2], fileParts[-4], dynamics_list) #function parameters: dynamics, instrument name, dynamics list
# idx = np.where(dynamics_list[0][:] == fileParts[-4]) #Find the index of item in dynamics
#
# #Get the mesured sound pressure level from dynamics file
# if fileParts[-2] == 'p':
#     dyn_db=dynamics_list[1][idx[0][0]]
# elif fileParts[-2] == 'mf':
#     dyn_db = dynamics_list[2][idx[0][0]]
# elif fileParts[-2] == 'f':
#     dyn_db = dynamics_list[3][idx[0][0]]
# else:
#     dyn_db = 60


#file = 'c:\\samples\\double_bass\\normal\\f\\23.wav'
noteN=int(94)
data, rate = librosa.load(file, sr=44100)

# print(file)
# print(rate)
# print(data.shape)


def cutSample(data):
    #fs=44100
    # data=data[:, 0] #Signal to mono
    data = librosa.to_mono(data) #signal to mono
    window = np.hanning(fs)
    if len(data)<fs:
        data=np.concatenate((data, np.zeros(fs-len(data))), axis=None)
    else:
        data=data[0:fs]
    data=data * window
    return data

def add_to_database (parameters, noteNumber, data):
    noteNumber=int(noteNumber/6)
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
    masking_freq, masking_threshold = maskingCurve.maskingCurve(S, noteNumber) #Calculate the masking curve
    #print("masking calculated")
    mfcc_data, centroid = MFCC.custom_mfcc(data) #Calculate mfcc and spectral centroid
    #print("mfcc calculated")
    LpcLocs, LpcFreqs = lpc_coeffs.lpc_coeffs(data) #calculate LPC-frequency response
    #print("lpc calculated")
    #Add everything to database:
    orchestra.update({instrument:{tech:{dyn:{noteNumber:{"data":data, "fft":spectrum, "masking_curve":masking_threshold, "masking_locs":masking_freq, "lpc_curve":LpcFreqs, "lpc_locs":LpcLocs, "mfcc":mfcc_data, "centroid":centroid}}}}})


data = cutSample(data)
data = normalize_sound_file.normalize_audio_file(data, dyn_db)

add_to_database(fileParts, noteN, data)
#print(data.shape)
#print(data)
#sd.play(data, fs)
inst='alto_flute'
orchestra = {inst : {'data' : data}}

M=len(data)
spectrum = np.fft.fft(orchestra[inst]['data'], axis=0)[:M // 2 + 1:-1]
spectrum = np.abs(spectrum)
S = 20 * np.log10(spectrum)
frq=30

#mfcc_data=librosa.feature.mfcc(y=data,sr=rate,n_mfcc=12,n_fft=int(M),hop_length=int(M+2))[:,0]
mfcc_data, centroid = MFCC.custom_mfcc(data)
LpcLocs, LpcFreqs = lpc_coeffs.lpc_coeffs(data)

# LPC=librosa.lpc(data, lpc_coeffs)
# f,h=freqz(1,LPC, worN=lpc_coeffs, fs=fs)
# h=20 * np.log10(np.abs(h))

A=np.linspace(0,len(spectrum),101)
#print("mfccs:")
#print(mfcc_data.shape)
#print(mfcc_data)
#print(centroid)
#peaks, _ = findPeaks(S, distance=frq, prominence=20, height=-10)
idx,peaks = findPeaks.peaks(S, noteN)
frq,thr = maskingCurve.maskingCurve(S, noteN)
#peaks = find_peaks_cwt(S,np.arange(1,fs/2+1))

fig, ax = plt.subplots()
ax.plot(S)
ax.plot(idx, peaks, "x")
ax.plot(frq,thr)
ax.plot(LpcLocs,LpcFreqs)
ax.set_xscale('log')
ax.set_ylabel('Frequency [kHz]')
ax.set_xlabel('Time [s]');


#sd.play(data, rate)
#status = sd.wait()  # Wait until file is done playing
#print(LpcLocs)
plt.show()