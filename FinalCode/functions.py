from random import sample
import streamlit as st
import pandas as pd
import mpld3
import streamlit.components.v1 as components
import csv
from io import StringIO
import numpy as np
import plotly.graph_objects as go
import math
from scipy.signal import find_peaks

time = np.linspace(0,1,1500)
class Functions:
    
    numberSignalsAdded = -1
    ADDED_FREQUENCES=[]
    ADDED_AMPLITUDES=[]
    UploadAmplitude = np.zeros(1500)
    ADDED_SIGNALS=[]
    amplitude_SUM = np.zeros(1500)  # Sum of AMPLITUDE of signals
    Current_amplitude = np.zeros(1500)
    defaultcose =[]



#  Function that is used to add multiple signals by ucosg frequencies and amplitudes entered by users. 
# - Function parameters : Frequency - Amplitude of new signal that we need to add
# - Function Return : Time - Amplitude that we need to plot   
# - For loop to store the new amplitude that we need to plot in the array 
# - updating lists to add new frequncies and amplitudes in the lists 
# - Add the new amplitude to the previouse amplitudes
def ADD_SIGNAL(added_magnitude ,added_frequency, phase):
    ##Signal##
    new_y_amplitude = np.zeros(1500)  # Array for saving cos signals values
    for i in range(1500): 
        new_y_amplitude[i] = (added_magnitude * (math.cos(((2 * np.pi * added_frequency * time[i]) + phase)))) 
    #updating lists
    Functions.numberSignalsAdded+=1
    Functions.ADDED_FREQUENCES.append(added_frequency)
    Functions.ADDED_AMPLITUDES.append(added_magnitude)
    Functions.ADDED_SIGNALS.append(new_y_amplitude)
    Functions.Current_amplitude = np.add(Functions.Current_amplitude,new_y_amplitude)
    Functions.UploadAmplitude =np.add(Functions.UploadAmplitude,new_y_amplitude)
    return Functions.Current_amplitude,Functions.UploadAmplitude



# Function that return the maximum frequency this is done by entering the list of frequencies then, iterating on it and getting the max. value.
def maxFrequency():
    if len(Functions.ADDED_FREQUENCES) == 0:
        return 1
    return np.max(Functions.ADDED_FREQUENCES)




# Function clean the graph from gargbe to start from zero.
# - Function parameters: None 
# - Function Return : None
def Clean_intialize():
    #number of signals added
    Functions.numberSignalsAdded=-1
    #lists of added features of the signals
    Functions.ADDED_FREQUENCES=[]
    Functions.ADDED_AMPLITUDES=[]
    Functions.ADDED_PHASES=[]
    Functions.ADDED_SIGNALS=[]
    Functions.amplitude_SUM = np.zeros(1500)  # Sum of AMPLITUDE of signals
    Functions.Current_amplitude=np.zeros(1500)



# Function to delete signal from the list and plot the signals.
# - Function parameters : index of signal that we need to remove
# - Function Return : Time - New Amplitude after deleting 
# - Delete the signal by its index in the list 
# - Check if there is signals or not :
#  -> if there is no signals so intialize the graph 
#  -> if there is signals so  : 1) subtract the removed amplitude from the current amplitude
#                               2) pop freqency from its list
#                               3) pop amplitude from its list
#                               4) pop signal from its list
def DELETE_SIGNAL(index_todelete):
    if(Functions.numberSignalsAdded== -1):
            Clean_intialize()
    else:
        Functions.Current_amplitude=np.subtract(Functions.Current_amplitude,Functions.ADDED_SIGNALS[index_todelete])
        Functions.ADDED_FREQUENCES.pop(index_todelete)
        Functions.ADDED_AMPLITUDES.pop(index_todelete)
        Functions.ADDED_SIGNALS.pop(index_todelete)
        Functions.numberSignalsAdded -= 1
       


# Function that read csv file when we upload the file.
#   - Function parameters : csv file 
#   - Function Return : Time - Added amplitudes   
#   1) Upload file 
#   2) Read file as bytes and store in (byte_data)
#   3) Convert bytes of file to string based on IO and store as string in (stringio)
#   4) Read the file as string in(string_data)
#   5) Read file as data fram (df)
#   6) First column at the csv  (Time)
#   7) Second column at csv (Amplitude)
#   😎 Add the amplitudes to each other 
def readCsv(uploaded_file):
    # if uploaded_file is not None:
    # To convert to a string based IO:
    df =  pd.read_csv(uploaded_file)
    Time = df.iloc[:,1]
    Amplitude = df.iloc[:,2]
    sample_interpolated=df.iloc[:,3]
    Functions.UploadAmplitude=np.add(Functions.UploadAmplitude,Amplitude)
    return Time,Functions.UploadAmplitude,sample_interpolated



# Function that sample the signal by entering different sampling frequencies.
# - Function parameters : Sampling Freqency(fsample) - Time (t) - Signal (cos)
# - Function Return : Sample Time - Sample Amplitude
# 1) Get timer range by subtract min time from max time 
# 2) Get the sample rate by its equation 
# 3) Get sample time and sample amplitude 
def sampling(fsample,t,cos):
    time_range=(max(t)-min(t))
    sampling_rate = int((len(t)/time_range)/fsample)
    sampling_time=t[::sampling_rate] 
    sampling_amplitude = cos[::sampling_rate]
    return sampling_time,sampling_amplitude




# Function used to make cosc interploation (recounstracting) on the signal from it’s sampling points.
# - Function parameters : Sampling Freqency(fsample) - Time (t) - Signal (cos)
# - Function Return : Reconstructed signal - Sampling time - Sampling ammplitude
# 1) First we make sample on the signal 
# 2) Store sampling time and sampling amplitude in numpy array 
# 3) Then we make resize to the time and store in matrix
def sinc_interp(fsample,t,cos ):
    samplingTime,samplingAmplitude=sampling(fsample,t,cos )
    samplingTime=np.array( samplingTime)
    samplingAmplitude=np.array(samplingAmplitude)
    time_matrix= np.resize(t,(len( samplingTime),len(t)))
    print(time_matrix.size)
    print( samplingTime)
    t=np.array(t)
    cos=np.array(cos)
    shiftingFactor = (time_matrix.T -  samplingTime)/( samplingTime[1]- samplingTime[0])
    resulted_matrix = samplingAmplitude* np.sinc(shiftingFactor)
    reconstucted_seg = np.sum(resulted_matrix, axis=1)
    return  reconstucted_seg, samplingTime,samplingAmplitude



# Function that generate noise on signal.
# - Function parameters : Siganl - SNR (Signal to Noise Ratio)
# - Function Return : Noised signal 
# 1) Get the signal power 2 
# 2) Use numpy mean function to get the mean of power array 
# 3) Substract signal to noise ratio from average power 
# 4) Use numpy random normal function to get the noise that we would add on the signal 
# 5) Add noise on the original signal
def noise(signal,snr_db):
    power = signal**2
    signal_avg_power=np.mean(power)
    signal_avg_power_db=10 * np.log10(signal_avg_power)
    noise_db=signal_avg_power_db - snr_db
    noise_watts=10 ** (noise_db/10)
    mean_noise=0
    noise=np.random.normal(mean_noise, np.sqrt(noise_watts),len(signal))
    noise_signal = signal+noise
    return noise_signal




# Function used to save the signal as csv file on yout PC.
#  - Function Parameters : Signal (cos)
# - Function Return : None
# 1) Get the x-axis (Time) and y-axis (Amplitude)
# 2) Use DataFrame to convert this signal to csv file 
def save(cos,interpolatedSignal,maxFrequency):
    signalAndInterpolation = {"x-axis":time, "y-axis":cos ,'sample-interpolated':interpolatedSignal,'maxFrequency':maxFrequency
                               }
    df= pd.DataFrame(signalAndInterpolation)

    st.session_state.sig = df
    
    @st.experimental_memo
    def convert_df(df):
        df.to_csv(index = False).encode('utf-8')
    col1, col2, col3= st.columns([1,1,1])
    col2.download_button(
    "Download",
    st.session_state.sig.to_csv(),
    "file.csv",
    "text/csv",
    key='download-csv'
    )