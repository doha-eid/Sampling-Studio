from tkinter import CENTER
from unicodedata import name

# import matplotlib.pyplot as plt
import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
from functions import *
from streamlit.components.v1 import html

# st. set_page_config(layout="wide")
#### Open css file to style ####
with open('style.css') as sc:
    st.markdown(f"<style>{sc.read()}</style>",unsafe_allow_html=True)

st.title("Sampling Studio")
################################################### plotting figure ###################################################################
mainSignal = px.line(height=500,width=1200, labels ={'x':'Time(s)','y':'Amplitude(mV)'})


mainSignal.update_layout(font=dict( family="Calibri", size=16, color="darkgray"),xaxis_title = 'Time(s)',yaxis_title ='Amplitude(mV)')




st.markdown("""
  <style>
    .css-hxt7ib{
      padding-top: 0px;
    }
  </style>
""", unsafe_allow_html=True) 


# Button to upload new file #
uploaded_file = st.file_uploader("Upload your file")

with st.sidebar:
    col1, col2, col3 = st.columns([4,1,1])

# Frequency slider to choose the frequency we need #  
    frequency = st.slider('Frequency',1,90)
# Amplitude slider to choose the amplitude we need #
    amplitude = st.slider('Amplitude', 1,20)
# Phase slider to choose the phase we need #
    phase = st.slider('Phase',0.0,2*np.pi,value=0.25*np.pi)
    # signalCheckBox = st.checkbox()
# Samplig frequency  slider to choose the frequncy we need #
    # sampe_freq=st.radio('options',options=('sampling fs','sampling f max'),key='sampling',horizontal=True)
    options=('Frequency','Fmax')
    selected_freq=st.selectbox('frequency scale',options,key='frequency_scale')
    Fmax_flag=0
    if st.session_state.frequency_scale=='Fmax':
        Fmax_flag=1

    if Fmax_flag:
        fsample = st.slider('Sampling Frequency', 1,10,step = 1,value=1,format='%dFmax',key='Fmax_scale')
        if maxFrequency() == 1:
            fsample = frequency*fsample
        else:
            fsample = maxFrequency()*fsample
        
    else:
        fsample = st.slider('Sampling Frequency', 1,200,step=1)





# Signal to noise ratio (snr) slider to choose the ratio we need we need # 
    
    col1, col2, col3= st.columns([5,6,3])
    addSignal=col2.button('Add Signal')
    noiseCheckBox = col1.checkbox("Add Noise")

    
# If we choose to upload file so read the csv pf this file and plot it  #

    if uploaded_file is not None:
        mainSignal = px.line(x=None,y=None,width= 1000,height= 500)
        TIME,AMPLITUDE,Interpolation_col= readCsv(uploaded_file)                  

# Interpolating function to drqw the interpolating between sampling points  #
        interpolatedSignal,sampleTimePoints,sampleAmpPoints,time_reconstructed = sinc_interp(fsample,time,Functions.UploadAmplitude)
        mainSignal.add_trace(go.Scatter(x=TIME,y=Functions.UploadAmplitude,
                                        name='Uploaded signal',
                                        line=dict(width=2,
                                        color='royalblue')
                                        ))
# Draw sampling points  #
        mainSignal.add_trace(go.Scatter(x=sampleTimePoints,
                                y=sampleAmpPoints, 
                                mode="markers", 
                                name ='Samples of uploaded signal without noise',
                                marker=dict(size=7, color ='lightyellow',
                                line=dict(width=2,
                                color='tan'))
                                ))
#Draw interploating # 
        mainSignal.add_trace(go.Scatter(x=time,
                        y=interpolatedSignal,
                        name='Interpolated Signal',
                        line=dict(width=2,
                        color='red')
                        ))
        if noiseCheckBox:
            snrRatio  = st.slider('SNR',1,260,1)
            noiseSignal=noise(Functions.UploadAmplitude,snrRatio)
            mainSignal.add_trace(go.Scatter(x=time,y=noiseSignal,
                                        name="Uploaded signal with noise",
                                        line=dict(width=2,
                                        color='green')
                                        ))
            interpolatedSignal,sampleTimePoints,sampleAmpPoints = sinc_interp(fsample,time,Functions.UploadAmplitude)
            mainSignal.add_trace(go.Scatter(x=time,y=interpolatedSignal,
                                            name='Sampling of the uploaded signal with noise',
                                            line=dict(width=2,
                                            color='black')
                                            ))
                

    else: 
        Functions.UploadAmplitude = np.zeros(1500)


    

    
    if len(Functions.ADDED_FREQUENCES)==0:
    
        defaultcose = amplitude * np.cos((2*np.pi*frequency*time)+ phase)

        mainSignal.add_trace(go.Scatter(x = time , y= amplitude * np.cos((2*np.pi*frequency*time) + phase),name="Signal to be added",line=dict(width=2,color='black')))

        interpolatedSignal,sampledTime,sampleAmplitude = sinc_interp(fsample, time , amplitude * np.cos((2*np.pi*frequency*time) + phase))

        mainSignal.add_trace(go.Scatter(x= time, y = interpolatedSignal, name = "Interpolation of signal to be added",line=dict(width=2,color='lightsalmon')))

        mainSignal.add_trace(go.Scatter(x=sampledTime,y=sampleAmplitude,mode="markers",name='Samples of the signal to be added',
                                    marker=dict(size=4, color ='yellow',
                                    line=dict(width=2,
                                    color='red'))
                                    ))

        if noiseCheckBox:
            snrRatio  = st.slider('SNR',1,260,1)
            noiseSignal = noise(amplitude * np.cos((2*np.pi*frequency*time)+ phase),snrRatio)
            mainSignal.add_trace(go.Scatter(x=time,y=noiseSignal,
                                        name="Signal to be added with noise",
                                        line=dict(width=2,
                                        color='green')
                                        ))
            interpolatedSignal,sampleTimePoints,sampleAmpPoints = sinc_interp(fsample,time,noiseSignal)
            mainSignal.add_trace(go.Scatter(x=time,y=interpolatedSignal,
                                            name='Sampling of the signal to be added with noise',
                                            line=dict(width=2,
                                            color='black')
                                            ))

    if addSignal:
        ADD_SIGNAL(amplitude, frequency, phase)


if len(Functions.ADDED_FREQUENCES) !=0:
            mainSignal = px.line(x=None,y=None)
            mainSignal.add_trace(go.Scatter(x=time,
                                            y=Functions.Current_amplitude,
                                            name='cosusoidal signals',
                                            line=dict(width=3,
                                            color='dodgerblue')))

            interpolatedSignal,sampleTimePoints,sampleAmpPoints = sinc_interp(fsample,time,Functions.Current_amplitude)
            mainSignal.add_trace(go.Scatter(x=time,
                                y=interpolatedSignal,
                                name='Interpolated Signal',
                                line=dict(width=2,
                                color='red')
                                ))
            mainSignal.add_trace(go.Scatter(x=sampleTimePoints,
            y=sampleAmpPoints,
            name='Interpolated Signal',
            mode ="markers"
            ))

            if noiseCheckBox:
                snrRatio  = st.slider('SNR',1,260,1)
                noiseSignal=noise(Functions.Current_amplitude ,snrRatio)
                # noiseDefault = noise(defaultcose,snrRatio)

                interpolatedSignal,sampleTimePoints,sampleAmpPoints = sinc_interp(fsample, time, noiseSignal)
                mainSignal.add_trace(go.Scatter(x=time,y=interpolatedSignal,
                                                name="interpolated signal with noise",
                                                line=dict(width=2,
                                                color='goldenrod')
                                                ))
                mainSignal.add_trace(go.Scatter(x= time ,y =noiseSignal,
                                                name = "Noised Signal",
                                                line=dict(width=2,
                                                color='green')
                                                ))
                mainSignal.add_trace(go.Scatter(x=sampleTimePoints,y=sampleAmpPoints,
                                    mode="markers",
                                    marker=dict(size=6, color ='brown',
                                    line=dict(width=2,
                                    color='red')),
                                    name='Samples With Noise'))


        # flag = 1
        # if addSignal:
        #     ADD_SIGNAL(amplitude, frequency, phase)


with st.sidebar:
    with st.form('Delete'):
        st.write("Delete Signal")

    
        deleteList = []
        
        
        for i in range(len(Functions.ADDED_FREQUENCES)):
            deleteList.append(f"amp = {Functions.ADDED_AMPLITUDES[i]} frequency ={Functions.ADDED_FREQUENCES[i]}")
        delList = st.multiselect("Signals to be deleted", deleteList)
        if st.form_submit_button("Delete Signal"):
            if len(Functions.ADDED_FREQUENCES) == 0:
                st.write('')
            else:
                for i in range(len(delList)):
                    if delList[i]:
                        DELETE_SIGNAL(i)
                        mainSignal.add_trace(go.Scatter(x=time,y=Functions.Current_amplitude))

                        


     
st.write(mainSignal)

save(Functions.Current_amplitude,interpolatedSignal)
            


            
    




st.markdown("""

<style>
.css-2ykyy6.egzxvld0{
    visibility:hidden;
}




<\style>



""", unsafe_allow_html=True)