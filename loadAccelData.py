#!/usr/bin/python

import getopt
import sys
from AccelData import AccelData
from AccelData import AccelPoint
import matplotlib.pyplot as pyplot
import matplotlib.figure as figure
import matplotlib.cm as cm
import scipy.signal as signal
from mpl_toolkits.mplot3d import Axes3D
import numpy
from scipy import signal

STEP=8

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

def filter(data):
    n = []
    result = []
    for d in data:
        n.append(d)
        if len(n) == STEP:
           m = numpy.mean(n)
           result.append(m)
           del n[0]

    return result

def calcDeltaT(timestamps):
    d = 0
    deltaT = []
    for timestamp in timestamps:
        d = d + 1
        if d == 1:
            t=timestamp
        elif d >= STEP:
            deltaT.append((timestamp-t) / 1000.0)
            t = timestamp

    return deltaT

def plotAccel(accelData):
    pyplot.plot(accelData)
    pyplot.grid()
    pyplot.show()

def calcDelta(data):
    delta = []
    for d in data:
        if len(delta) == 0:
            delta.append(d)
        else:
            delta.append(d - delta[len(delta)-1])

    return delta

def getXYZMod(accelData):
    x = []
    z = []
    y = []
    mod = []
    t = []
    for accel in accelData:
        x.append(accel.x)
        y.append(accel.y)
        z.append(accel.z)
        t.append(accel.timestamp)
        m = accel.x**2 + accel.y**2 + accel.z**2
        if (m==0):
            mod.append(0)
        else:
            mod.append(numpy.sqrt(m))

    return x,y,z,mod,t

def addOffset(data,offset):
    i = 0
    while i < len(data):
        data[i] = data[i] + offset
        i=i+1

def plot2D(data,figure=1):
    pyplot.figure(figure)
    n = 0
    if (len(data) == 2):
        sb = 211
    elif (len(data)>2 and len(data)<4):
        sb = 221
    else:
        sb = 111
    for d in data:
        pyplot.subplot(sb)
        for dd in d['data']:
            pyplot.plot(dd)

        pyplot.legend(d['legend'])
        n=n+1
        sb=sb+1


def plot3D(x,fx,y,fy,z,fz,mod,fmod):
    fig = pyplot.figure()
    ax = Axes3D(fig)
    ax.plot(xs=fx,ys=fy,zs=fz) #,rstride=1,cstride=1,cmap=cm.jet)
    pyplot.show()


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

def main(argv):
    inputfile=''
    try:
        opts,args = getopt.getopt(argv,"hi:")
    except getopt.GetoptError: 
        sys.exit(2)

    if len(opts) == 0:
        print "no input file"
        sys.exit(2)
    
    for opt,arg in opts:
        if opt == '-h':
            print '-i <inputfile.xml>'
            sys.exit(0)
        elif opt == '-i':
           inputfile = arg
        else:
           print 'no input file'
           sys.exit(2)

    accelData = AccelData()
    accelData.loadAccelData(inputfile)
    accelData.calcDeltasT()
    x,y,z,mod,t = getXYZMod(accelData.accelData)
    f2x = filter2(x)
    fx = filter(x)
    fy = filter(y)
    fz = filter(z)
    fmod = filter(mod)
    f2mod = filter2(mod)

    ax, devax = avgWithStep(x,8)
    fax, devfax = avgWithStep(fx,8)
    amod,devmod = avgWithStep(mod,8)
    afmod,devafmod = avgWithStep(fmod,8)

#CALCULATE CORRECTION
    corrX = findCorrectionCoef(x)
    print "Correction  coefX:" + str(corrX)
    corrMod = findCorrectionCoef(mod)
    print "Correction coefMod: " + str(corrMod)
    offx = x[0:]
    addOffset(offx,-corrX)
    offy = y[0:]
    corrY=findCorrectionCoef(y)
    addOffset(offy,-corrY)
    offMod = mod[0:]
    addOffset(offMod,-corrMod)
    corrOffMod = findCorrectionCoef(offMod)
    print "Correction for offMod: " + str(corrOffMod)
#    plot3D(x,fx,y,fy,z,fz,mod,fmod)
#    plot2D([x,fx],[['x'],['fx']])

#CALCULATE Velocity,distance
    dt = calcDeltaT(t)
#    dts = dt[0:] / 1000.0f
    voffx = calcInteg(offx,dt)
    sx = calcInteg(voffx,dt)
    voffy = calcInteg(offy,dt)
    sy = calcInteg(voffy,dt)
    vmod = calcInteg(offMod,dt)
    smod = calcInteg(vmod,dt)
    dplot = [
                {'data': [offMod,vmod,smod], 'legend': ['offMod','vmod','smod']},
                {'data': [mod], 'legend': ['mod'] }
            ]
    plot2D(dplot,1)
    pyplot.show()
#
#   dplot = [
#               {'data': [offx,voffx,sx], 'legend': ['offx','voffx','sx']},
#               {'data': [x], 'legend':['x']}
#           ]
#   plot2D(dplot,1)
#   pyplot.show()
#
#   dplot = [
#               {'data': [offy,voffy,sy], 'legend': ['offy','voffy','sy']},
#               {'data': [y], 'legend':['y']}
#           ]
#   plot2D(dplot,1)
#   pyplot.show()
 
#MAKE PLOTS
#   dplot = [
#       {'data': [ax,devax,x], 'legend': ['ax','devax','x']},
#       {'data': [fax,devfax,fx], 'legend':  ['fax','devfax','fx']}
#       ]
#
#   plot2D(dplot,1)
#   pyplot.show()
#   dplot = [ {'data': [f2x,x,fx], 'legend': ['f2x','x','fx']},
#             {'data': [f2mod,mod,fmod], 'legend': ['f2mod','mod','fmod']}
#           ]
#   plot2D(dplot,1)
#   pyplot.show()
    
if __name__=="__main__":
    main(sys.argv[1:])
