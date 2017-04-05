import xml.etree.ElementTree as ElementTree
from datetime import datetime
from CoordinateSysPoints import GeoPoint, XYZPoint
import numpy

GARMIN_NS = {"garmin":"http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}
SEC_PER_DAY = 86400

class EndoPoint(object):
    def __init__(self):
        self.dattime = 0
        self.geoPoint = GeoPoint()
        self.endoDist = 0
        self.ddist = 0
        self.xyzPoint = XYZPoint()
        self.mod = 0
        self.deltaT = 0
        self.deltadistance = 0
        self.distance = 0
        self.distanceXY = 0
        self.deltaDistanceXY = 0

    def __init__(self, lat, lon, alt, dattime, endodist=0):
        self.dattime = dattime #datetime
        self.geoPoint = GeoPoint(lon,lat,alt)
        self.endoDist = endodist
        self.ddist = 0
        self.xyzPoint = self.geoPoint.getXYZPoint()
        self.mod = alt #meters
        self.deltaT = 0 #in seconds
        self.deltadistance = 0
        self.distance = 0
        self.distanceXY = 0
        self.deltaDistanceXY = 0

    def __str__(self):
        s= "----Endo Point----\n"
        s+= "time="+str(self.dattime)+"\n"
        s+= "lat="+str(self.geoPoint.lat)
        s+= ", lon="+str(self.geoPoint.lon)
        s+= ", alt="+str(self.geoPoint.alt)+"\n"
        s+= "deltaT="+str(self.deltaT)+"\n"
        s+= "distance="+str(self.distance)
        s+= ", deltadistance="+str(self.deltadistance)+"\n"
        s+= "endoDist="+str(self.endoDist)
        s+= ", endo ddist="+str(self.ddist)
        
        return s

    def calcDeltaT(self,prevEndoPoint):
        delta = self.dattime - prevEndoPoint.dattime
        self.deltaT = delta.days*SEC_PER_DAY+delta.seconds+delta.microseconds/1000000.0

    def calcDeltaDistance(self,prevEndoPoint):
        dx = self.xyzPoint.x - prevEndoPoint.xyzPoint.x
        dy = self.xyzPoint.y - prevEndoPoint.xyzPoint.y
        dz = self.xyzPoint.z - prevEndoPoint.xyzPoint.z
        self.deltadistance = numpy.sqrt(dz**2 + dy**2 + dx**2)
        self.deltaDistanceXY = numpy.sqrt(dx**2+dy**2)
        self.ddist = self.endoDist - prevEndoPoint.endoDist

    def calcDistance(self,prevEndoPoint):
         self.distance = prevEndoPoint.distance + self.deltadistance
         self.distanceXY = prevEndoPoint.distanceXY + self.deltaDistanceXY


class EndoData(object):
    def __init__(self):
        self.endoPoints = []
        self.duration = 0

    def loadEndoData(self, fileName):
        doc = ElementTree.parse(fileName)
        EndoItems=doc.findall(".//garmin:Track/garmin:Trackpoint[garmin:AltitudeMeters]",GARMIN_NS)
        print "Found EndoItems: " + str(len(EndoItems))
        t=0
        total_time=0
        samples=0
        med_samples=0
        n=0
        for eItem in EndoItems:
             item = self.createEndoPoint(eItem)
             self.endoPoints.append(item)
             n=n+1

    def calculateDeltasT(self):
        n=1
        while n<len(self.endoPoints):
            self.endoPoints[n].calcDeltaT(self.endoPoints[n-1])
            n += 1

    def createEndoPoint(self, endoItem):
        time = endoItem.find(".//garmin:Time",GARMIN_NS)
        lat = endoItem.find(".//garmin:LatitudeDegrees",GARMIN_NS)
        lon = endoItem.find(".//garmin:LongitudeDegrees",GARMIN_NS)
        alt = endoItem.find(".//garmin:AltitudeMeters",GARMIN_NS)
        dist = endoItem.find(".//garmin:DistanceMeters",GARMIN_NS)
        dt = datetime.strptime(time.text,"%Y-%m-%dT%H:%M:%SZ")
        tlat = lat.text
        tlon = lon.text
        talt = alt.text
        ndist = float(dist.text)*1000.0
        return EndoPoint(float(tlat),float(tlon),float(talt),dattime=dt,endodist=ndist)

    def generateCollection(self,getter,start=0,end=-1):
        collection = self.endoPoints
        c = []
        i = start;
        if (end == -1):
            end = len(collection)

        while ((i<end) and (i < len(collection))):
            c.append(getter(collection[i]))
            i += 1
        
        return c

    def getEndoDistanceCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.endoDist,start,end)
 
    def getEndoDeltaDistanceCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.ddist,start,end)

    def getDistanceCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.distance,start,end)

    def getDeltaDistanceXYCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.deltaDistanceXY,start,end)

    def getDistanceXYCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.distanceXY,start,end)

    def getDeltaDistanceCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.deltadistance,start,end)

    def getLatCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.geoPoint.lat,start,end)

    def getLonCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.geoPoint.lon,start,end)

    def getAltCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.geoPoint.alt,start,end)

    def getXCollection(self,start=0,end=-1):
#        x = fakeCollection(self.accelData, lambda accPoint: accPoint.x)
        return self.generateCollection(lambda endoP: endoP.xyzPoint.x,start,end)

    def getYCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.xyzPoint.y,start,end)

    def getZCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.xyzPoint.z,start,end)

    def getDatetimeCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.datTime,start,end)

    def getModCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.mod,start,end)

    def getDeltaTCollection(self,start=0,end=-1):
        return self.generateCollection(lambda endoP: endoP.deltaT,start,end)

    def getIntegratedBydT(self):
        newEndoData = EndoData()
        deltaT = self.getDeltaTCollection()
        datime = self.getDatetimeCollection()
        lon = AccelCalc.calcInteg(self.getLonCollection(), deltaT)
        lat = AccelCalc.calcInteg(self.getLatCollection(), deltaT)
        alt = AccelCalc.calcInteg(self.getAltCollection(), deltaT)

        i = 0
        while(i<len(lon)):
            item = EndoPoint(lon[i],lat[i],alt[i],tstamps[i])
            item.deltaT = deltaT[i]

            newEndoData.endoPoints.append(item)
            i += 1

        return newEndoData

    def calcDeltaDistances(self):
        i = 1;
        while(i<len(self.endoPoints)):
            self.endoPoints[i].calcDeltaDistance(self.endoPoints[i-1])
            i += 1

    def calcDistances(self):
        i = 1;
        while(i<len(self.endoPoints)):
            self.endoPoints[i].calcDistance(self.endoPoints[i-1])
            i += 1

#    def getVelocities(self):
#        self.calcDeltaDistances()
#        self.calcDistances()        
#        vel = []
#        i = 0;
        

    def getDerivatedByT(self):
        newEndoData = EndoData()
        deltaT = self.getDeltaTCollection()
        datime = self.getDatetimeCollection()
        lon = AccelCalc.calcDeriv(self.getLonCollection(), deltaT)
        lat = AccelCalc.calcDeriv(self.getLatCollection(), deltaT)
        alt = AccelCalc.calcDeriv(self.getAltCollection(), deltaT)

        i = 0
        while(i<len(lon)):
            item = EndoPoint(lon[i],lat[i],alt[i],tstamps[i])
            item.deltaT = deltaT[i]

            newEndoData.endoPoints.append(item)
            i += 1

        return newEndoData


