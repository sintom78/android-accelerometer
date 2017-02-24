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

def plotSpeedVelocity(title,collection, getter, offset=0,unbias=True):
    D = getter(collection)
    offAccelData = collection.getCopyRange() #ioffset)
    if unbias:
        offAccelData.unBias()
    offD = getter(offAccelData)
    vAccelData = offAccelData.getIntegratedBydT()
    vAccelData.printBigDelta()
#    vAccelData.unBiasMod()
    sAccelData = vAccelData.getIntegratedBydT()
#    sAccelData.unBiasMod()
    vD = getter(vAccelData)
    sD = getter(sAccelData)
    dplot = [
                {'data': [offD,vD,D], 'legend': ['offset','V','Orig']},
                {'data': [sD], 'legend': ['Distance'] }
            ]
    plot2D(dplot,1,title) 


def plotSpeedVelocityModule(accelData, offset):
    plotSpeedVelocity("SpeedVelocity Module",accelData,lambda accD: accD.getModCollection(),offset)

def plotSpeedVelocityX(accelData, offset):
    plotSpeedVelocity("Speed Velocity X",accelData,lambda accD: accD.getXCollection(),offset)

def plotSpeedVelocityY(accelData, offset):
    plotSpeedVelocity("Speed Velocity Y",accelData,lambda accD: accD.getYCollection(),offset)

def plotSpeedVelocityZ(accelData, offset):
    plotSpeedVelocity("Speed Velocity Z",accelData,lambda accD: accD.getZCollection(),offset)

def plotSVFilteredMod(accelData, OFFSET):
    accData = accelData.getCopyRange()
    accData.applyFilter(AccelCalc.filterH)
    #accData.applyFilter(AccelCalc.filterL)
    accData = accData.getCopyRange(60)
    plotSpeedVelocity("Filtered SV Mod",accData,lambda accD: accD.getModCollection(),0,False)


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

#    ax, devax = AccelCalc.avgWithStep(x,8)
#    fax, devfax = AccelCalc.avgWithStep(fx,8)
#    amod,devmod = AccelCalc.avgWithStep(mod,8)
#    afmod,devafmod = AccelCalc.avgWithStep(fmod,8)

    plotSpeedVelocityModule(accelData,OFFSET)
    plotSVFilteredMod(accelData, OFFSET)
#    plotSpeedVelocityX(accelData,OFFSET)
#    plotSpeedVelocityY(accelData,OFFSET)
#    plotSpeedVelocityZ(accelData,OFFSET)

    
if __name__=="__main__":
    main(sys.argv[1:])
