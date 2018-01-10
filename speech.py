#Embedded file name: /Users/Ryan/Desktop/speech.py
import mechanize
import random 
########Added by Yun################
import GLaDOSfunctions
import numpy as np 
import matplotlib.pyplot as plt 
import scipy.signal as filt
###Yun

def word2speech(text):
    url = 'http://www.wizzardspeech.com/att_demo.html'
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.open(url)
    br.select_form(nr=0)
    br['speaktext'] = text
    br['speaker'] = ['crystal16']
    submitlink = br.submit()
    html = submitlink.read()
    linkstart = html.find('MyFile=')
    linkend = html.find('.wav')
    filename = html[linkstart + 7:linkend + 4]
    data = br.open('http://www.wizzardspeech.com/php_tmp/' + filename).read()
    return data

def text2GLaDOS(text,savefile,fps):
    listofwords=text.split()
    totalmlen=0
    wordsaud=[]
    lappause=[]
    for i in listofwords:
        chardata=word2speech(i)
        arraydata=np.fromstring(chardata, 'Int16')
        newrd=GLaDOSfunctions.gladoseffect(arraydata,fps)[200:]
        indexi= GLaDOSfunctions.getstartend(newrd)
        newrd=newrd[indexi[0]:indexi[1]]
#        newrd=GLaDOSfunctions.solatimescale(newrd,1)
        newrd=GLaDOSfunctions.timestretch(newrd,512,0.5)
        totalmlen+=(len(newrd)+2400)
        wordsaud.append(newrd)
        lop=random.randint(-3,1)
        lappause.append(lop)
    GLaDOSvoice=np.int16([0]*totalmlen)
    GLaDOSvoice[0:len(wordsaud[0])]+=wordsaud[0]
    position=len(wordsaud[0])
    lappause[-1]=2
    print lappause
    for j in range(1,len(wordsaud)):
        overlap=lappause[j]*600
        print position
        position-=overlap
        GLaDOSvoice[position:position+len(wordsaud[j])]+=wordsaud[j]
        position+=len(wordsaud[j])
    final=GLaDOSfunctions.dictation(GLaDOSvoice,0.125)
    if savefile:
        GLaDOSfunctions.numarraytoaud(final,'output.wav',fps)
    return [GLaDOSvoice,final]
        



