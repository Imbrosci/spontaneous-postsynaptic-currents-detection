# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 10:42:02 2022.

@author: barbara
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy.signal import resample
from abf_files_loader import load_abf
from butter import lowpass
from get_data import get_format_data
from pscs_parameters_calculator import ParametersCalculator
from txt_files_loader import load_txt

root = os.getcwd() + '/'
results_path = 'results/results.xlsx'
recording_dir = 'recordings/'

check_excel = False
trials = 0

while not check_excel:
    # get file name and channel to proof-read
    recording_file = input('Enter the file name: ')
    channel = input('Enter the channel number: ')

    # define the sheet_name
    if ('.abf' in recording_file) or ('.txt' in recording_file):
        sheet_name = recording_file[:-4] + '_' + channel
    else:
        print('Please, provide the file name with extention')
        trials += 1
        continue
    # try to load the results
    try:
        results = pd.read_excel(root + results_path, sheet_name=sheet_name)
        check_excel = True
    except ValueError:
        print('''Either the recording file or the channel was not found in the results.xlsx file. Please, try again.''')
        trials += 1
        if trials >= 5:
            exit()

# try to load the summary results sheet
try:
    summary_results = pd.read_excel(root + results_path,
                                    sheet_name='Summary results')
except ValueError:
    print('There is a problem with the results.xlsx file. Make sure there is a summary_results sheet')

# the name of the recordings files should be speficied with extentions in the
# metadata.xlsx file. The format that can be used are either abf or txt.
if ('.abf' not in recording_file) and ('.txt' not in recording_file):
    print('The extention of the recording file (.abf or .txt) should be specified in the metadata.xlsx file')
    exit()

# try to load the recording_file
if '.abf' in recording_file:
    try:
        data = load_abf(root + recording_dir + recording_file)
    except FileNotFoundError:
        print('The recording file was not found')
        exit()
if '.txt' in recording_file:
    try:
        data = load_txt(root + recording_dir + recording_file)
    except FileNotFoundError:
        print('The recording file was not found')
        exit()    

# get metadata
start_sweep = summary_results.loc[(
    summary_results['Recording filename'] == recording_file) & (
        summary_results['Channel'] == int(channel)
        )]['Analysis start at sweep (number)']

start_at = summary_results.loc[(
    summary_results['Recording filename'] == recording_file) & (
        summary_results['Channel'] == int(channel)
        )]['Starting point at each sweep (ms)']

analysis_end = summary_results.loc[(
    summary_results['Recording filename'] == recording_file) & (
        summary_results['Channel'] == int(channel)
        )]['Analysis length (sec)']

fs = summary_results.loc[(
    summary_results['Recording filename'] == recording_file) & (
        summary_results['Channel'] == int(channel)
        )]['Sampling rate (Hz)']

start_sweep = int(start_sweep - 1)
fs = int(fs)
start_at = int(start_at * (fs / 1000))
analysis_end = int(analysis_end * fs)

# try to get the relevant channel
ch = ['Ch' + str(channel)]
data = get_format_data(data, ch, start_sweep, start_at)
if len(data) == 0:
    print('The channel was not found in the recording file.')
    exit()

# get the portion of the recording been analyzed
signal = data[int(channel)]
signal = signal[:analysis_end]

# resample the signal if fs != 20000
if fs != 20000:
    signal = resample(signal, int(signal.shape[0] * 20000 / fs))

# low pass filter the recording
signal_lp = lowpass(signal, 800, order=1)

# get x, y coordinates of detected events
x = np.array(results['x (ms)'])
y = np.array(results['y (pA)'])

# plot the results
time = np.linspace(0, round(signal_lp.shape[0]/(fs / 1000)) - 1,
                   signal_lp.shape[0])

x_dp = np.zeros((len(x)))
for i in range(len(x)):
    x_dp[i] = int(x[i] * (fs / 1000))
x_dp = x_dp.astype(int)

cutouts = []
for ev_dp in x_dp:
    fifty_ms = int(50 * (fs / 1000))
    if (ev_dp - fifty_ms >= 0) and ev_dp + fifty_ms * 2 < len(signal_lp):
        cutouts.append(signal_lp[ev_dp - fifty_ms:ev_dp + fifty_ms * 2])

cutout_time = np.linspace(-50, 100, 3000)
cutout_mean = np.mean(np.array(cutouts), axis=0)

# get the dp at 10-90% of the rise time and at 90-10% of the decay time
parameters = ParametersCalculator(signal_lp, x_dp, y, fs)
rise_10, rise_90 = parameters.rise_time()[1:]
decay_10, decay_90 = parameters.decay_time()[1:]

try:
    rise_10 = rise_10 + 600
    rise_10_ms = int(rise_10 / (fs / 1000)) - 50
except TypeError:
    pass
try:
    rise_90 = rise_90 + 600
    rise_90_ms = int(rise_90 / (fs / 1000)) - 50
except TypeError:
    pass
try:
    decay_10 = decay_10 + 1000
    decay_10_ms = int(decay_10 / (fs / 1000)) - 50
except TypeError:
    pass
try:
    decay_90 = decay_90 + 1000
    decay_90_ms = int(decay_90 / (fs / 1000)) - 50
except TypeError:
    pass

# plot the detected PSCs
plt.figure(figsize=(18, 8))
plt.plot(time, signal_lp, c='black')
plt.scatter(x, y, c='blue', marker='o', s=20, linewidths=5,
            label='detected events')
plt.xlabel('Time (ms)', fontsize=16)
plt.ylabel('Signal (pA)', fontsize=16)
plt.legend()
plt.show()

# plot the mean PSC and the curves fitting the rise and decay phase
plt.figure(figsize=(8, 5))
plt.plot(cutout_time, cutout_mean, c='black', label='mean signal')
if rise_10 and rise_90:
    plt.scatter([cutout_time[rise_10], cutout_time[rise_90]],
                [cutout_mean[rise_10], cutout_mean[rise_90]],
                c='cyan', label='rise time range (10-90%)')
if decay_10 and decay_90:
    plt.scatter([cutout_time[decay_10], cutout_time[decay_90]],
                [cutout_mean[decay_10], cutout_mean[decay_90]],
                c='magenta', label='decay time range (90-10%)')
plt.xlabel('Time (ms)', fontsize=16)
plt.ylabel('Signal (pA)', fontsize=16)
plt.legend()
plt.show()