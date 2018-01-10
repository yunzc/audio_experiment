# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 20:24:46 2016
GLaDOS project take 3
@author:Yun Chang
"""
from scipy.fftpack import fft, ifft
import numpy as np 
import wave
from scipy.io.wavfile import write
import random 


def averagelistabs(listofdata):
    #returns the average of the absolute value of the elements in the list
    abssum=0    
    for i in listofdata:
        abssum+=abs(i)
    return abssum/float(len(listofdata))
    

def wordsegment(speechaud):
    #speechaud is a wave object called by wave.open 
    #function takes the audio and return a list with segments of audio that contains a word 
    speechdata=speechaud.readframes(-1)
    auddata=np.fromstring(speechdata,'Int16')
    maxamp=np.amax(auddata)
#    plt.plot(auddata)
    threshold=maxamp/15#threshold can be tuned 
    start=[]
    stop=[]
    startyes=1
    for i in range(len(auddata)):
        avgamp=averagelistabs(auddata[i:i+300])
        if startyes==1:
            if avgamp>threshold:
                start.append(i+149)
                startyes=0 #start looking for the stop 
        elif startyes==0:
            if avgamp<threshold:
                stop.append(i+149)
                startyes=1
    if len(start)<len(stop):
        index=len(start)
    else:
        index=len(stop)
    
    listofframes=[]
    for j in range(index):
        listofframes.append(auddata[start[j]:stop[j]])
    return listofframes

def getstartend(wordarray):
    maxamp=np.amax(wordarray)
    threshold=maxamp/2
    startindex=0
    while wordarray[startindex]<threshold:
        startindex+=1
    stopindex=len(wordarray)-1
    while wordarray[stopindex]<threshold:
        stopindex-=1
    return (startindex,stopindex)
        
def numarraytoaud(numbarray,audfile,fps):
    write(audfile,fps,numbarray)
    
def findfreqofframe(wavearrayobj,fps,numframes):
    #Do dfft to find the fundemental plus the make up freqs of a frame 
    #returns top five frequency in format dictionary -> freq:amplitude (relative)
    #note that wavearrayobj is in int16
    rdft=fft(wavearrayobj)
    rdft=rdft[0:len(wavearrayobj)/2]
    absrd=abs(rdft)
    topfreq={}
    for j in range(10):
        index=np.argmax(absrd)
        freq=index*fps/numframes
        amplit=np.amax(absrd)
        topfreq[freq]=amplit
        absrd[index]=0
    topfreq.pop(0,None)
    return topfreq

def shiftpitchup1(segment,scale):
    orig_fourtrans=fft(segment)
    flip_orig=orig_fourtrans[::-1]
    new1=np.zeros(len(segment)/2,dtype=complex)
    for i in range(int(len(orig_fourtrans)/(2*scale))):
        new1[int(i*scale)]=orig_fourtrans[i]
    new2=np.zeros(len(segment)/2,dtype=complex)
    for i in range(int(len(flip_orig)/(2*scale))):
        new2[int(i*scale)]=orig_fourtrans[i]
    new2=new2[::-1]
    new=np.append(new1,new2)
    return ifft(new)

#test=wave.open('test.wav')
#tword=wordsegment(test)
#twordaud=np.int16(tword[3])
#numarraytoaud(twordaud,'test1.wav',16000)
#stest=shiftpitchup1(twordaud,1.2)
#numarraytoaud(np.int16(stest),'test2.wav',16000)  
  
def shiftpitchup(segment,fps,num):
    orig_fourtrans=fft(segment)
    newft=np.int16([0]*num)
    newft=np.append(newft,orig_fourtrans[0:len(orig_fourtrans)/2-num])
    newft=np.append(newft,orig_fourtrans[len(orig_fourtrans)/2+num:len(orig_fourtrans)])
    newft=np.append(newft,np.int16([0]*num))
    inv_fourier=ifft(newft)
    
    return np.int16(inv_fourier.real)

#stest2=shiftpitchup(twordaud,16000,80)
#numarraytoaud(stest2,'test3.wav',16000)

def shiftpitchdown(segment,fps,num):
    orig_fourtrans=fft(segment)
    newft=orig_fourtrans[num:len(orig_fourtrans)/2]
    newft=np.append(newft,np.int16([0]*num*2))
    newft=np.append(newft,orig_fourtrans[len(orig_fourtrans)/2:len(orig_fourtrans)-num])
    inv_fourier=ifft(newft)
    
    return np.int16(inv_fourier.real)

def dictation(wavearray,freq):
    # Cutoff frequency as a fraction of the sampling rate (in (0, 0.5)).
    fourt=fft(wavearray)
    lenindex=len(fourt)
    for i in range(int(freq*lenindex*0.5)):
        fourt[i]/=50
    for j in range(lenindex-int(freq*lenindex*0.5),lenindex):
        fourt[j]/=50
#    for k in range(int(freq*lenindex*0.5),lenindex-int(freq*lenindex*0.5)):
#        fourt[k]*=2
    newarray=ifft(fourt)
    return np.int16(newarray)
    
def timestretch(soundarray,chunck,factor):    
    hop=chunck/4    
    phase=np.zeros(chunck)
    hanning=np.hanning(chunck)
    result=np.zeros(len(soundarray)/factor+chunck,dtype=complex)
    for i in np.arange(0,len(soundarray)-(chunck+hop),hop*factor):
        a1=soundarray[i:i+chunck]
        a2=soundarray[i+hop:i+chunck+hop]
        s1=fft(hanning*a1)
        s2=fft(hanning*a2)
        phas=(phase+np.angle(s1/s2))%2*np.pi
        a2_rephased=ifft(np.abs(s2)*np.exp(1j*phase))
        
        i2=int(i/factor)
        result[i2:i2+chunck]+=hanning*a2_rephased
    result=((2**(16-4))*result/result.max())
    return np.int16(result)

def gladoseffect(wavarray,fps):
    shiftnum=random.randint(50,300)
    if shiftnum<=0:
        newrd=shiftpitchdown(wavarray,fps,abs(shiftnum))
    else:
        newrd=shiftpitchup(wavarray,fps,shiftnum)
    return newrd
    

#what we can do is to import the sentence word by word and then synthesize it 
#slowing it down definitely DOES NOT FRICKEN WORK 


#audio=wave.open('GLaDOS.wav')
#auddata=audio.readframes(-1)
#fps=audio.getframerate()
#audiodata=np.fromstring(auddata,'Int16')
#newaud=timestretch(audiodata,2048,1.5)
#numarraytoaud(newaud,'newoutput.wav',fps)
