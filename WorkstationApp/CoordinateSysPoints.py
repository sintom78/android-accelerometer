import numpy

class EarthGeoParams(object):
    radius = 6371000 #meters
    b = 6356752.3142
    f = 1/298.257
    a = b/(1-f)
    e = (1 - (b**2/a**2))
    e2 = (a**2 - b**2)/a**2
    ep2 = (a**2 - b**2)/b**2

def getN(lat_rad):
    a = EarthGeoParams.a
    b = EarthGeoParams.b
    n = numpy.sqrt((a**2)*numpy.cos(lat_rad)**2+(b**2)*numpy.sin(lat_rad)**2)
    return (a**2)/n

class GeoPoint(object):
    def __init__(self):
        self.__init__(0,0,0)

    def __init__(self,longitude,latitude,altitude):
        self.alt = altitude    #meters
        self.lat = latitude    #degrees
        self.lon = longitude  #degrees
    def __str__(self):
        s = "lat: " + str(self.lat)
        s += " lon: " + str(self.lon)
        s += " alt: " + str(self.alt)
        return s

    def getXYZPoint(self):
        lat_rad = numpy.deg2rad(self.lat)
        lon_rad = numpy.deg2rad(self.lon)
        R = self.getN(lat_rad)
        a = EarthGeoParams.a
        b = EarthGeoParams.b
        x = (self.alt+R)*numpy.cos(lat_rad)*numpy.cos(lon_rad) #meters
        y = (self.alt+R)*numpy.cos(lat_rad)*numpy.sin(lon_rad) #meters
        z = (self.alt+R*(b**2)/(a**2))*numpy.sin(lat_rad) #meters        
        return XYZPoint(x,y,z)

    def getN(self, lat_rad):
        a = EarthGeoParams.a
        b = EarthGeoParams.b
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
        alt = self.calcAlt()
        lat = self.calcLat()
        lon = self.calcLon()
        return GeoPoint(lon,lat,alt)

    def calcLon(self):
        lon = numpy.arctan(self.y / self.x)
        return numpy.rad2deg(lon)

    def calcLat(self):
        e2a = EarthGeoParams.e2*EarthGeoParams.a
        p = numpy.sqrt(self.x**2 + self.y**2)
        r = numpy.sqrt(self.x**2 + self.y**2 + self.z**2)
        tu = (self.z / p) * ((1 - EarthGeoParams.f) + (e2a / r))
        u = numpy.arctan(tu)
        f1 = (self.z * (1 - EarthGeoParams.f)) + (e2a * (numpy.sin(u)**3))
        f2 = (1 - EarthGeoParams.f) * (p - (e2a * (numpy.cos(u)**3)))
        lat_rad = numpy.arctan(f1/f2)
        return numpy.rad2deg(lat_rad)

    def calcAlt(self):
        phi = numpy.deg2rad(self.calcLat())
        p = numpy.sqrt(self.x**2 + self.y**2)
        f1 = p * numpy.cos(phi) + self.z * numpy.sin(phi)
        f2 = EarthGeoParams.a * numpy.sqrt(1-EarthGeoParams.e2 * numpy.sin(phi)**2)
        return (f1 - f2)

