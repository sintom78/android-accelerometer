import numpy

EARTH_RADIUS = 6371000 #meters
EARTH_B = 6353000
EARTH_A = 6384000

class GeoPoint(object):
    def __init__(self):
        self.__init__(0,0,0)

    def __init__(self,longitude,latitude,altitude):
        self.alt = altitude    #meters
        self.lat = latitude    #degrees
        self.lon = longitude  #degrees

    def getXYZPoint(self):
        lat_rad = numpy.deg2rad(self.lat)
        lon_rad = numpy.deg2rad(self.lon)
        R = self.getN(lat_rad)
        a = EARTH_A
        b = EARTH_B
        x = (self.alt+R)*numpy.cos(lat_rad)*numpy.cos(lon_rad) #meters
        y = (self.alt+R)*numpy.cos(lat_rad)*numpy.sin(lon_rad) #meters
        z = (self.alt+R*(b**2)/(a**2))*numpy.sin(lat_rad) #meters
        return XYZPoint(x,y,z)

    def getN(self, lat_rad):
        a = EARTH_A 
        b = EARTH_B
        n = numpy.sqrt((a**2)*numpy.cos(lat_rad)**2+(b**2)*numpy.sin(lat_rad)**2)
        return (a**2)/n

class XYZPoint(object):
    def __init__(self):
        self.__init(0,0,0)

    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def getGeoPoint(self):
        #TODO: calculate latitude, longitude and altitude
        lat = 0
        lon = 0
        alt = 0
        return GeoPoint(lon,lat,alt)
