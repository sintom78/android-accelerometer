#!/usr/bin/python

import getopt
import sys
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as pyplot
import matplotlib.figure as figure
import matplotlib.cm as cm
import scipy.signal as signal
from mpl_toolkits.mplot3d import Axes3D
import numpy
from scipy import signal

STEP=8

def findCorrectionCoef(data):
    CORRECTION_WINDOW=10 #num of samples
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
            deltaT.append(timestamp-t)
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

def getFloat(num):
    return float(num.replace(',','.'))

def loadAccelData(fileName):
    doc = ElementTree.parse(fileName)
    accelItems=doc.findall("./AccelItem")
    data = []
    t=0
    total_time=0
    samples=0
    med_samples=0
    n=0
    for accItem in accelItems:
         item = {}
         item['x'] = getFloat(accItem.get("x"))
         item['y'] = getFloat(accItem.get("y"))
         item['z'] = getFloat(accItem.get("z"))
         item['timestamp'] = long(accItem.get("data"))
         data.append(item)
         n=n+1
         if t == 0:
             t = item['timestamp']
             total_time = t
         else:
             dt = (item['timestamp'] - t) / 1000.0
             if (dt >= 1):
                t = item['timestamp']
                if (med_samples == 0):
                    med_samples = med_samples + n
                else:
                    med_samples = med_samples + n
                    med_samples = med_samples / 2.0

                n=0
         
    if len(data) > 0:
        total_time = (data[len(data)-1]['timestamp'] - data[0]['timestamp']) / 1000.0
        print "Total time: " + str(total_time)
        print "Samples per second(medium): " + str(med_samples)

    return data


def getXYZMod(accelData):
    x = []
    z = []
    y = []
    mod = []
    t = []
    for accel in accelData:
        x.append(accel['x'])
        y.append(accel['y'])
        z.append(accel['z'])
        t.append(accel['timestamp'])
        m = accel['x']**2 + accel['y']**2 + accel['z']**2
        if (m==0):
            mod.append(0)
        else:
            mod.append(numpy.sqrt(m))

    return x,y,z,mod,t

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
            v.append(v[i-1]+(a[i-1]/dt[i-1]))
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

    accelData = loadAccelData(inputfile)
    x,y,z,mod,t = getXYZMod(accelData)
    f2x = filter2(x)
    fx = filter(x)
    fy = filter(y)
    fz = filter(z)
    fmod = filter(mod)
    f2mod = filter2(mod)
    dt = calcDeltaT(t)
    vx = calcInteg(fx,dt)
    sx = calcInteg(vx,dt)

    ax, devax = avgWithStep(x,8)
    fax, devfax = avgWithStep(fx,8)
    amod,devmod = avgWithStep(mod,8)
    afmod,devafmod = avgWithStep(fmod,8)

    corrX = findCorrectionCoef(x)
    print "Correctio  coefX:" + str(corrX)

#    plot3D(x,fx,y,fy,z,fz,mod,fmod)
#    plot2D([x,fx],[['x'],['fx']])

    dplot = [
        {'data': [ax,devax,x], 'legend': ['ax','devax','x']},
        {'data': [fax,devfax,fx], 'legend':  ['fax','devfax','fx']}
        ]

    plot2D(dplot,1)
    pyplot.show()
    dplot = [ {'data': [f2x,x,fx], 'legend': ['f2x','x','fx']},
              {'data': [f2mod,mod,fmod], 'legend': ['f2mod','mod','fmod']}
            ]
    plot2D(dplot,1)
    pyplot.show()
    
#    plot2D([fax,devfax,fx],['fax','devfax','fx'])
#    pyplot.show()

#    plot2D([devax,devfax],['devax','devfax'])
#    pyplot.show()

#    plot2D([[amod,devmod,mod]], [['amod','devmod','mod']],2)
  #  pyplot.show()

#    plot2D([[afmod,devafmod,fmod]],[['afmod','devafmod','fmod']],3)
#    pyplot.show()

#    plot2D([[devmod,devafmod]],[['devmod','devafmod']])
#    pyplot.show()
 #    plot2D([fx,vx],[['fx'],['vx']])
#    pyplot.show()

#    plot2D([vx,sx],[['vx'],['sx']])
#    pyplot.show()

#    dx = calcDelta(fx)
#    dy = calcDelta(fy)
#    dz = calcDelta(fz)
#    dmod = calcDelta(fmod)
#    plot2D(fx,dx,fy,dy,fz,dz,fmod,dmod) 

if __name__=="__main__":
    main(sys.argv[1:])
