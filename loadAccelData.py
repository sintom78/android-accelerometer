#!/usr/bin/python

import getopt
import sys
from AccelData import AccelData
from AccelData import AccelPoint
import AccelCalculations as AccelCalc
from AccelPlot import plot2D
from AccelPlot import plot3D
import copy

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
    OFFSET = 10
    x = accelData.getXCollection()
    x = x[OFFSET:]
    y = accelData.getYCollection()
    y = y[OFFSET:]
    z = accelData.getZCollection()
    z = z[OFFSET:]
    mod = accelData.getModCollection()
    mod = mod[OFFSET:]
    t = accelData.getTimestampCollection()
    t = t[OFFSET:]
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

#CALCULATE CORRECTION
    corrX = AccelCalc.findCorrectionCoef(x)
    print "Correction  coefX:" + str(corrX)
    corrMod = AccelCalc.findCorrectionCoef(mod)
    print "Correction coefMod: " + str(corrMod)
    offx = x[0:]
    AccelCalc.addOffset(offx,-corrX)
    offy = y[0:]
    corrY=AccelCalc.findCorrectionCoef(y)
    AccelCalc.addOffset(offy,-corrY)
    offz = z[0:]
    corrZ=AccelCalc.findCorrectionCoef(z)
    AccelCalc.addOffset(offz,-corrZ)
    offMod = mod[0:]
    AccelCalc.addOffset(offMod,-corrMod)
    corrOffMod = AccelCalc.findCorrectionCoef(offMod)
    print "Correction for offMod: " + str(corrOffMod)
#    plot3D(x,fx,y,fy,z,fz,mod,fmod)

#CALCULATE Velocity,distance
#    dt = accelData.getDeltaTCollection() 
#    dt = dt[OFFSET:]
#    dts = dt[0:] / 1000.0f
#   voffx = AccelCalc.calcInteg(offx,dt)
#   sx = AccelCalc.calcInteg(voffx,dt)
#   voffy = AccelCalc.calcInteg(offy,dt)
#   sy = AccelCalc.calcInteg(voffy,dt)
#   voffz = AccelCalc.calcInteg(offz,dt)
#   sz = AccelCalc.calcInteg(voffz,dt)
#   vmod = AccelCalc.calcInteg(offMod,dt)
#   smod = AccelCalc.calcInteg(vmod,dt)
    offAccelData = copy.deepcopy(accelData)
    offAccelData.unBias()
    vAccelData = offAccelData.getIntegratedBydT()
    sAccelData = vAccelData.getIntegratedBydT()

    offMod = offAccelData.getModCollection()
    vmod = vAccelData.getModCollection()
    smod = sAccelData.getModCollection()

    dplot = [
                {'data': [offMod,vmod,smod], 'legend': ['offMod','vmod','smod']},
                {'data': [mod], 'legend': ['mod'] }
            ]
    plot2D(dplot,1) #,False)
#
    dplot = [
               {'data': [offx,voffx,sx], 'legend': ['offx','voffx','sx']},
               {'data': [x], 'legend':['x']}
           ]
    plot2D(dplot,2)
#
    dplot = [
               {'data': [offy,voffy,sy], 'legend': ['offy','voffy','sy']},
               {'data': [y], 'legend':['y']}
           ]
    plot2D(dplot,1)
 
    dplot = [
               {'data': [offz,voffz,sz], 'legend': ['offz','voffz','sz']},
               {'data': [z], 'legend':['z']}
           ]
    plot2D(dplot,1)
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
