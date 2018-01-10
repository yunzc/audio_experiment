# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 21:12:15 2016

@author: Yun Chang

"""
import wave
import numpy as np
from scipy.fftpack import fft
import audioop


def solatimescale(waveobj,posstart,posend,scale):
    #SOLA Synchronous Overlap Add
    #returns string obj to be written into .wav file and new frame
    #scale works best btwn 0.5~1.5
    numframes=posend-posstart
    chuncksize=numframes/20
    overlap=(scale-1)*chuncksize
    remainder=numframes/chuncksize
    waveobj.setpos(posstart)
    new_aud=waveobj.readframes(chuncksize)
    datapos=posstart+chuncksize
    while datapos<posend-remainder-chuncksize:
        waveobj.setpos(datapos-overlap)
        new_aud+=waveobj.readframes(chuncksize+overlap)
        datapos+=chuncksize
        
    waveobj.setpos(datapos-overlap)
    new_aud+=waveobj.readframes(chuncksize+overlap+remainder)
    return new_aud
    
#I believe the way to do it is the look at the file, fine the segments with words, randomly tune the words to a pitch (stretch time scale and when we shift it back to the 
#lower )
       
def generatewave(fps,frequency,numframes):
    
#    remainder=numframes/fps
    wavdata=""
    for i in range(numframes*2):
        #2 bytes in
        wavdata+=chr(int(np.sin(i/((fps/frequency)/np.pi))*127+128))
#    for i in range(remainder):
#        wavdata+=chr(128)
    return wavdata 
    
def generateemptywave(fps,numframes):
    remainder=numframes/fps
    wavedata=""
    for i in range(numframes*2):
        wavedata+=chr(int(128))
#    for i in range(remainder):
#        wavedata+=chr(128)
    return wavedata

def findfreqofframe(waveframeobj,fps,numframes):
    #Do dfft to find the fundemental plus the make up freqs of a frame 
    #returns top five frequency in format dictionary -> freq:amplitude (relative)
    wavdata=np.fromstring(waveframeobj,'Int16')
    rdft=fft(wavdata)
    rdft=rdft[0:len(wavdata)/2]
    absrd=abs(rdft)
    topfivefreq={}
    for j in range(4):
        index=np.argmax(absrd)
        freq=index*fps/numframes
        amplit=np.amax(absrd)
        topfivefreq[freq]=amplit
        absrd[index]=0
    return topfivefreq

#Plan: Step 1: find the frequency and keep all the frequency content but add harmonics: formant 
#Plan: Step 2: alter original frequency content by shift up or down !!!need to keep the words 

def addharmonics(waveobj,harmonicfactor):
    numframes=waveobj.getnframes()
    #divide into segments to operate on 
    #harmonic factor is a tuple and *2 is an octave for example
    fps=waveobj.getframerate()
    width=waveobj.getsampwidth()
    wavedata=waveobj.readframes(numframes)
    chunck=int(fps*0.1)
    numpartitions=int(numframes/chunck)
    remainder=numframes%chunck
    datapos=0
    harmonicwave=""
    for i in range(numpartitions):
        waveobj.setpos(datapos*i)
        segment=waveobj.readframes(chunck)
        freqcont_dict=findfreqofframe(segment,fps,chunck)
        #at this part only care about fundamental 
        freqcont_list=freqcont_dict.keys()
        fundfreq=freqcont_list[0]
        #now to generate harmonic wave
        harmonicwave_seg=generateemptywave(fps,chunck)
        for j in harmonicfactor:
            layer=generatewave(fps,fundfreq*j,chunck)
            audioop.add(harmonicwave_seg,layer,width)
        harmonicwave+=harmonicwave_seg
        print len(harmonicwave)
    if remainder != 0:
        datapos=datapos*numpartitions
        waveobj.setpos(datapos)
        segment=waveobj.readframes(remainder)
        freqcont_dict=findfreqofframe(segment,fps,remainder)
        freqcont_list=freqcont_dict.keys()
        fundfreq=freqcont_list[0]
        harmonicwave_seg=generateemptywave(fps,remainder)
        for j in harmonicfactor:
            layer=generatewave(fps,fundfreq*j,remainder)
            audioop.add(harmonicwave_seg,layer,width)
        harmonicwave+=harmonicwave_seg
    print len(wavedata)
    print len(harmonicwave)
    new_aud=audioop.add(wavedata,harmonicwave,width)
    return new_aud
    

audio=wave.open('output.wav')
numbframes=audio.getnframes()
fps=audio.getframerate()
width=audio.getsampwidth()
#newauddata=generatewave(fps,440,numbframes)
print numbframes
newauddata=addharmonics(audio,(2,))
print len(newauddata)
print len(wavedata)
newaudio=wave.open('newoutput.wav','w')
newaudio.setparams((1,width,fps,numbframes,'NONE','Uncompressed'))
newaudio.writeframes(newauddata)
newaudio.close()
audio.close()

