#!/usr/bin/python

import xml.etree.ElementTree as ElementTree
import numpy

def getFloat(num):
    return float(num.replace(',','.'))



class AccelPoint(object):
    """Represent acceleration in 3-D with timestamp"""

    deltaT = 0
    x = 0.0
    y = 0.0
    z = 0.0
    mod = 0.0
    deltaT = 0.0
    timestamp = 0.0

    def __init__(self,x,y,z,timestamp):
        self.x = x
        self.y = y
        self.z = z
        self.timestamp = timestamp

    def calcModule(self):
        m = self.x**2 + self.y**2 + self.z**2
        self.mod = numpy.sqrt(m)

    def calcDeltaT(self, prevAccelPoint):
        self.deltaT = (self.timestamp - prevAccelPoint.timestamp) / 1000.0


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
    accelData = []
    duration = 0

    def generateCollection(self,collection,getter):
        c = []
        for i in collection:
            c.append(getter(i))
        return c

    def getXCollection(self):
#        x = fakeCollection(self.accelData, lambda accPoint: accPoint.x)
        return self.generateCollection(self.accelData,lambda accP: accP.x)

    def getYCollection(self):
        return self.generateCollection(self.accelData,lambda accP: accP.y)

    def getZCollection(self):
        return self.generateCollection(self.accelData,lambda accP: accP.z)

    def getTimestampCollection(self):
        return self.generateCollection(self.accelData,lambda accP: accP.timestamp)

    def getModCollection(self):
        return self.generateCollection(self.accelData,lambda accP: accP.mod)

    def getDeltaTCollection(self):
        return self.generateCollection(self.accelData,lambda accP: accP.deltaT)

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


