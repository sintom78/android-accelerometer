#!/usr/bin/python

import xml.etree.ElementTree as ElementTree
import numpy
import copy
import AccelCalculations as AccelCalc

#WARN_DELTA_T: treshold for dletaT warning 
WARN_DELTA_T = 0.5

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
        self.pitch = 0    #rotation on Y (theta)
        self.yaw = 0      #rotation on Z (gamma)
        self.roll = 0     #rotation on X (phi)

    def __str__(self):
        string = "x: " + str(self.x) + " y: " + str(self.y) + " z: " + str(self.z)  
        string += " mod: " + str(self.mod) + " tstamp: " + str(self.timestamp) + " dT: " + str(self.deltaT)

        return string
 
    def calcSphereCoordinates(self):
        tan_phi_xyz = self.y / self.z
        tan_theta_xyz = -self.x / (numpy.sqrt(self.y**2 + self.z**2))
        self.roll = numpy.arctan(tan_phi_xyz)
        self.pitch = numpy.arctan(tan_theta_xyz)
        self.yaw = 0 #TODO

    def calcModule(self):
        m = self.x**2 + self.y**2 + self.z**2
        self.mod = numpy.sqrt(m)

    def calcDeltaT(self, prevAccelPoint):
        self.deltaT = (self.timestamp - prevAccelPoint.timestamp) / 1000.0

    def addOffset(self,x=0,y=0,z=0,mod=0):
        self.x += x
        self.y += y
        self.z += z
        self.mod += mod
        #self.mod = abs(self.mod)

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
        self.modOffset = 0
        self.maxDeltaT = 0

    def generateCollection(self,getter,start=0,end=-1):
        collection = self.accelData
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
        return self.generateCollection(lambda accP: accP.x,start,end)

    def getYCollection(self,start=0,end=-1):
        return self.generateCollection(lambda accP: accP.y,start,end)

    def getZCollection(self,start=0,end=-1):
        return self.generateCollection(lambda accP: accP.z,start,end)

    def getTimestampCollection(self,start=0,end=-1):
        return self.generateCollection(lambda accP: accP.timestamp,start,end)

    def getModCollection(self,start=0,end=-1):
        return self.generateCollection(lambda accP: accP.mod,start,end)

    def getDeltaTCollection(self,start=0,end=-1):
        return self.generateCollection(lambda accP: accP.deltaT,start,end)

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
            print "Duration: " + str(self.duration) + " [s]"

    def calcDeltasT(self):
        i = 1
        while i<len(self.accelData):
            self.accelData[i].calcDeltaT(self.accelData[i-1])
            deltaT = self.accelData[i].deltaT
            if self.maxDeltaT < deltaT:
                self.maxDeltaT = deltaT

            if deltaT > WARN_DELTA_T or deltaT <=0:
                print "Irrational deltaT: " + str(deltaT) + " at i="+str(i)
#                print "tstamp1=" + str(self.accelData[i-1].timestamp) 
#                print "tstamp2=" + str(self.accelData[i].timestamp)
            i=i+1
        print "Max DeltaT: " + str(self.maxDeltaT)

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

    def printBigDelta(self,collection=[]):
        i=1
        if len(collection)==0:
            collection = self.accelData

        cdelta = lambda x1,x2: x2-x1 
        gX = lambda n: collection[n].x
        gY = lambda n: collection[n].y
        gZ = lambda n: collection[n].z
        gMod = lambda n: collection[n].mod
        gDT = lambda n: collection[n].deltaT
        while (i<len(collection)):
           dMod = cdelta(gMod(i-1),gMod(i))
           #print dx
           if dMod>10:
               print "Huge dMod:" + str(dMod)
               print "x1=" + str(gX(i-1)) + " x2="  + str(gX(i))
               print "y1=" + str(gY(i-1)) + " y2="  + str(gY(i))
               print "z1=" + str(gZ(i-1)) + " x2="  + str(gZ(i))
               print "mod1=" + str(gMod(i-1)) + " mod2="  + str(gMod(i))
               print "dT1=" +str(gDT(i-1)) + " dT2=" + str(gDT(i))

           i += 1

    def getIntegratedBydT(self,recalcMod=True):
        newAccelData = AccelData()
        newAccelData.modOffset = self.modOffset
        deltaT = self.getDeltaTCollection()
        tstamps = self.getTimestampCollection()
        x = AccelCalc.calcInteg(self.getXCollection(), deltaT)
        y = AccelCalc.calcInteg(self.getYCollection(), deltaT)
        z = AccelCalc.calcInteg(self.getZCollection(), deltaT)
        if not recalcMod:
            mod = AccelCalc.calcInteg(self.getModCollection(), deltaT)

        i = 0
        while(i<len(x)):
            item = AccelPoint(x[i],y[i],z[i],tstamps[i])
            item.deltaT = deltaT[i]
            if recalcMod:
                item.calcModule()
            else:
                item.mod = mod[i]

            newAccelData.accelData.append(item)
            i += 1

        return newAccelData

    def unBiasMod(self):
        #print self.modOffset
        for item in self.accelData:
            item.addOffset(mod=-self.modOffset)
        

    def unBias(self, recalcMod=True):
        offX = AccelCalc.findCorrectionCoef(self.getXCollection())
        offY = AccelCalc.findCorrectionCoef(self.getYCollection())
        offZ = AccelCalc.findCorrectionCoef(self.getZCollection())
        self.modOffset = AccelCalc.findCorrectionCoef(self.getModCollection())
        #print self.modOffset

        for item in self.accelData:
            item.addOffset(-offX,-offY,-offZ,-self.modOffset)
            if recalcMod:
                item.calcModule()

    def applyFilter(self, filter):
        x = filter(self.getXCollection())
        y = filter(self.getYCollection())
        z = filter(self.getZCollection())
        i = 0
#        acclD = copy.deepcopy(self.accelData)
#        self.accelData = []
        while(i<len(x) and i<len(y) and i<len(z)):
            item = AccelPoint(x[i],y[i],z[i],self.accelData[i].timestamp)
            self.accelData[i].x = x[i]
            self.accelData[i].y = y[i]
            self.accelData[i].z = z[i]
            i += 1

        del self.accelData[i:len(self.accelData)]
        #TODO: what to do with timestamps? ho to "aligne them to new x,y,z collections
        for i in self.accelData:
            i.calcModule()
  
