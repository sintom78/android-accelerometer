import numpy
import scipy.signal as signal

def findCorrectionCoef(data):
    CORRECTION_WINDOW=15 #num of samples
    current = 0
    coefIdx = 0
    i = 0
    while i < (len(data)-CORRECTION_WINDOW):
        d = numpy.std(data[i:i+CORRECTION_WINDOW])
        i=i+1
        if current==0 or current>d:
            current = d
            coefIdx = i

    coef = numpy.mean(data[coefIdx:coefIdx+CORRECTION_WINDOW])
    return coef

def filter2(data):
    b, a = signal.iirfilter(8, Wn=0.2, btype="lowpass")
    result = signal.lfilter(b,a,data)
    return result

def filter(data, STEP=8):
    n = []
    result = []
    for d in data:
        n.append(d)
        if len(n) == STEP:
           m = numpy.mean(n)
           result.append(m)
           del n[0]

    return result

def addOffset(data,offset):
    i = 0
    while i < len(data):
        data[i] = data[i] + offset
        i=i+1

def avgWithStep(data, step):
    s = 0
    avg = 0
    current_avg = 0
    averaged = []
    deviation = []
    dev = []
    current_dev = 0
    for d in data:
        avg = avg + d
        s = s + 1
        averaged.append(current_avg)
        deviation.append(current_dev)
        dev.append(d)
        if (s == step):
            current_avg = avg/s
            current_dev = numpy.var(dev)
            dev = [] 
            #averaged.append(avg/s)
            avg = 0
            s = 0

    if (s > 0):
        averaged.append(avg/s)

    return averaged, deviation

def calcInteg(a,dt):
    i = 0
    v = []
    x = 0
    while(i<len(dt)):
        if i==0:
            v.append(0)
        else:
            v.append(v[i-1]+(a[i]*dt[i]))
        i=i+1

    return v


