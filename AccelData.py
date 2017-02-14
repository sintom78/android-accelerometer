#!/usr/bin/python

import xml.etree.ElementTree as ElementTree
import numpy
import copy
import AccelCalculations as AccelCalc


def getFloat(num):
    return float(num.replace(',','.'))


class AccelPoint(object):
    """Represent acceleration in 3-D with timestamp"""

    def __init__(self,x,y,z,timestamp):
        self.x = x
        self.y = y
        self.z = z
        self.timestamp = timestamp
        self.deltaT = 0
        self.mod = 0

    def __str__(self):
        string = "x: " + str(self.x) + " y: " + str(self.y) + " z: " + str(self.z)  
        string += " mod: " + str(self.mod) + " tstamp: " + str(self.timestamp) + " dT: " + str(self.deltaT)

        return string
 
    def calcModule(self):
        m = self.x**2 + self.y**2 + self.z**2
        self.mod = numpy.sqrt(m)

    def calcDeltaT(self, prevAccelPoint):
        self.deltaT = (self.timestamp - prevAccelPoint.timestamp) / 1000.0

    def addOffset(self,x,y,z):
        self.x += x
        self.y += y
        self.z += z

class fakeCollection():
    items = []
    
    def __init__(self,collection, getFunction):
        self.items = collection
        self.getfunction = getFunction

    def __getitem__(self,i):
        return self.getfunction(self.items[i])
 
    def __len__(self):
        return len(items)


class AccelData():
    """Collection of accelerometer points (AccelPoint classes)"""

    def __init__(self):
        self.accelData = []
        self.duration = 0

    def generateCollection(self,collection,getter,start=0,end=-1):
        c = []
        i = start;
        if (end == -1):
            end = len(collection)

        while ((i<end) and (i < len(collection))):
            c.append(getter(collection[i]))
            i += 1
        
        return c

    def getXCollection(self,start=0,end=-1):
#        x = fakeCollection(self.accelData, lambda accPoint: accPoint.x)
        return self.generateCollection(self.accelData,lambda accP: accP.x,start,end)

    def getYCollection(self,start=0,end=-1):
        return self.generateCollection(self.accelData,lambda accP: accP.y,start,end)

    def getZCollection(self,start=0,end=-1):
        return self.generateCollection(self.accelData,lambda accP: accP.z,start,end)

    def getTimestampCollection(self,start=0,end=-1):
        return self.generateCollection(self.accelData,lambda accP: accP.timestamp,start,end)

    def getModCollection(self,start=0,end=-1):
        return self.generateCollection(self.accelData,lambda accP: accP.mod,start,end)

    def getDeltaTCollection(self,start=0,end=-1):
        return self.generateCollection(self.accelData,lambda accP: accP.deltaT,start,end)

    def loadAccelData(self,fileName):
        doc = ElementTree.parse(fileName)
        accelItems=doc.findall("./AccelItem")
        self.accelData = []
        t=0
        total_time=0
        samples=0
        med_samples=0
        n=0
        for accItem in accelItems:
             item = AccelPoint(getFloat(accItem.get("x")),
                 getFloat(accItem.get("y")),
                 getFloat(accItem.get("z")),
                 long(accItem.get("data")))
             item.calcModule()
             self.accelData.append(item)
             n=n+1

        if len(self.accelData) > 0:
            self.duration = (self.accelData[len(self.accelData)-1].timestamp - self.accelData[0].timestamp) / 1000.0
            print "Duration: " + str(self.duration)

    def calcDeltasT(self):
        i = 1
        while i<len(self.accelData):
            self.accelData[i].calcDeltaT(self.accelData[i-1])
            i=i+1

    def getCopyRange(self, start=0,end=-1):
        newAccelData = AccelData()
        i=start
        if (end<0):
            end = 0
        while (i<len(self.accelData)):
            item = copy.deepcopy(self.accelData[i])
            newAccelData.accelData.append(item)
            i += 1
        return newAccelData

    def getIntegratedBydT(self):
        newAccelData = AccelData()
        deltaT = self.getDeltaTCollection()
        tstamps = self.getTimestampCollection()
        x = AccelCalc.calcInteg(self.getXCollection(), deltaT)
        y = AccelCalc.calcInteg(self.getYCollection(), deltaT)
        z = AccelCalc.calcInteg(self.getZCollection(), deltaT)
        i = 0
        while(i<len(x)):
            item = AccelPoint(x[i],y[i],z[i],tstamps[i])
            item.deltaT = deltaT[i]
            item.calcModule()
            newAccelData.accelData.append(item)
            i += 1

        return newAccelData

    def unBias(self):
        offX = AccelCalc.findCorrectionCoef(self.getXCollection())
        offY = AccelCalc.findCorrectionCoef(self.getYCollection())
        offZ = AccelCalc.findCorrectionCoef(self.getZCollection())

        for item in self.accelData:
            item.addOffset(-offX,-offY,-offZ)
            item.calcModule()
