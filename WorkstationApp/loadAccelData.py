#!/usr/bin/python

import getopt
import sys
from AccelData import AccelData
from AccelData import AccelPoint
import AccelCalculations as AccelCalc
from AccelPlot import plot2D
from AccelPlot import plot3D
import copy

#GLOBALS
inputfile=''

def plotSpeedVelocity(collection, getter, offset):
    D = getter(collection)
    offAccelData = collection.getCopyRange(offset)
    offAccelData.unBias()
    vAccelData = offAccelData.getIntegratedBydT()
    sAccelData = vAccelData.getIntegratedBydT()
 
    offD = getter(offAccelData)
    vD = getter(vAccelData)
    sD = getter(sAccelData)
    dplot = [
                {'data': [offD,vD,sD], 'legend': ['offset','V','S']},
                {'data': [D], 'legend': ['original'] }
            ]
    plot2D(dplot,1) 


def plotSpeedVelocityModule(accelData, offset):
    plotSpeedVelocity(accelData,lambda accD: accD.getModCollection(),offset)

def plotSpeedVelocityX(accelData, offset):
    plotSpeedVelocity(accelData,lambda accD: accD.getXCollection(),offset)

def plotSpeedVelocityY(accelData, offset):
    plotSpeedVelocity(accelData,lambda accD: accD.getYCollection(),offset)

def plotSpeedVelocityZ(accelData, offset):
    plotSpeedVelocity(accelData,lambda accD: accD.getZCollection(),offset)

def parseArgs(argv):
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
           globals()['inputfile'] = arg
        else:
           print 'no input file'
           sys.exit(2)


def main(argv):
    parseArgs(argv)

    accelData = AccelData()
    accelData.loadAccelData(globals()['inputfile'])
    accelData.calcDeltasT()
    OFFSET = 10
    x = accelData.getXCollection(OFFSET)
    y = accelData.getYCollection(OFFSET)
    z = accelData.getZCollection(OFFSET)
    mod = accelData.getModCollection(OFFSET)
    t = accelData.getTimestampCollection(OFFSET)
    f2x = AccelCalc.filter2(x)
    fx = AccelCalc.filter(x)
    fy = AccelCalc.filter(y)
    fz = AccelCalc.filter(z)
    fmod = AccelCalc.filter(mod)
    f2mod = AccelCalc.filter2(mod)

    ax, devax = AccelCalc.avgWithStep(x,8)
    fax, devfax = AccelCalc.avgWithStep(fx,8)
    amod,devmod = AccelCalc.avgWithStep(mod,8)
    afmod,devafmod = AccelCalc.avgWithStep(fmod,8)

    plotSpeedVelocityModule(accelData,OFFSET)
    plotSpeedVelocityX(accelData,OFFSET)
    plotSpeedVelocityY(accelData,OFFSET)
    plotSpeedVelocityZ(accelData,OFFSET)

#   dplot = [
#              {'data': [offx,voffx,sx], 'legend': ['offx','voffx','sx']},
#              {'data': [x], 'legend':['x']}
#          ]
#   plot2D(dplot,2)
#
#    dplot = [
#               {'data': [offy,voffy,sy], 'legend': ['offy','voffy','sy']},
#               {'data': [y], 'legend':['y']}
#           ]
#    plot2D(dplot,1)
 
#    dplot = [
#               {'data': [offz,voffz,sz], 'legend': ['offz','voffz','sz']},
#               {'data': [z], 'legend':['z']}
#           ]
#    plot2D(dplot,1)
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
