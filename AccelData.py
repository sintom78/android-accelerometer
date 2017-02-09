#!/usr/bin/python

import xml.etree.ElementTree as ElementTree
import numpy

def getFloat(num):
    return float(num.replace(',','.'))

class AccelPoint(object):
    """Represent acceleration in 3-D with timestamp"""

    deltaT = 0

    def __init__(self,x,y,z,timestamp):
        self.x = x
        self.y = y
        self.z = z
        self.timestamp = timestamp

    def calcModule(self):
        m = self.x**2 + self.y**2 + self.z**2
        self.mod = numpy.sqrt(m)

    def calcDeltaT(self, prevAccelPoint):
        self.deltaT = self.timestamp - prevAccelPoint.timestamp / 1000.0

class AccelData():
    """Collection of accelerometer points (AccelPoint classes)"""
    accelData = []
    duration = 0

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


