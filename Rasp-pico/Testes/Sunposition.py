from math import *

# Constants:
MPI    = 3.14159265358979323846e6  # One Megapi...
R2D    = 57.2957795130823208768    # Radians to degrees conversion factor
R2H    = 3.81971863420548805845    # Radians to hours conversion factor
TWO_PI = 6.28318530717958647693
PI     = 3.14159265358979323846

def compute(Location : list, Time : list, useDegrees : bool = True, useNorthEqualsZero : bool = True, computeRefrEquatorial : bool = False, computeDistance : bool = False):
    # descompactação da lista Time 
    Tyear   = Time[0] + 2000 
    Tmonth  = Time[1]
    Tday    = Time[2]
    Thour   = Time[3] + Time[6]
    Tminute = Time[4]
    Tsecond = Time[5]

    # descompactação da lista Location
    Llatitude    = Location[0]
    Llongitude   = Location[1]
    Ltemperature = Location[2]
    Lpressure    = Location[3]   
    LsinLat      = sin( Llatitude ) 
    LcosLat      = sqrt( 1.0 - LsinLat**2 ) 

    if( useDegrees ): 
        Llongitude /= R2D
        Llatitude  /= R2D
    
    LsinLat = sin(  Llatitude)
    LcosLat = sqrt( 1.0 - LsinLat**2 )

    PjulianDay = computeJulianDay( Tyear, Tmonth, Tday,  Thour, Tminute, Tsecond)
    
    PUT   = Thour + float( Tminute/60.0 ) + float( Tsecond/3600.0 )
    PtJD  = PjulianDay
    PtJC  = PtJD / 36525.0
    PtJC2 = PtJC**2

    l0 = fmod(4.895063168 + 628.331966786 * PtJC  +  5.291838e-6  * PtJC2, TWO_PI)
    m  = fmod(6.240060141 + 628.301955152 * PtJC  -  2.682571e-6  * PtJC2, TWO_PI)

    c = fmod((3.34161088e-2 - 8.40725e-5*PtJC - 2.443e-7*PtJC2)*sin(m) + (3.489437e-4 - 1.76278e-6*PtJC)*sin(2*m), TWO_PI)   # Sun's equation of the centre
    odot = l0 + c

    omg  = fmod(2.1824390725 - 33.7570464271 * PtJC  + 3.622256e-5 * PtJC2, TWO_PI)
    dpsi = -8.338601e-5*sin(omg)
    dist = 1.0000010178

    if( computeDistance ):
        ecc = 0.016708634 - 0.000042037   * PtJC  -  0.0000001267 * PtJC2
        nu = m + c
        dist = dist*( 1.0 - ecc*ecc) / (1.0 + ecc*cos(nu) )
    
    aber = -9.93087e-5/dist

    eps0 = 0.409092804222 - (2.26965525e-4*PtJC + 2.86e-9*PtJC2)
    deps = 4.4615e-5*cos(omg)

    Plongitude    = fmod(odot + aber + dpsi, TWO_PI)
    Pdistance     = dist
    Pobliquity    = eps0 + deps
    PcosObliquity = cos(Pobliquity)
    PnutationLon  = dpsi

    #convertEclipticToEquatorial(Plongitude, PcosObliquity,  &PrightAscension, &Pdeclination)
    sinLon = sin(  Plongitude           )
    sinObl = sqrt( 1.0-PcosObliquity**2 )

    PrightAscension = atan2( PcosObliquity*sinLon, cos(Plongitude) )
    Pdeclination    = asin( sinObl * sinLon )

    #void convertEquatorialToHorizontal(struct STLocation location, struct STPosition *position) {   
    gmst  = 1.75336856 + fmod(0.017202791805*PtJD, TWO_PI) + 6.77e-6*PtJC2 + PUT/R2H
    Pagst = fmod(gmst + PnutationLon * PcosObliquity, TWO_PI)

    sinAlt=0.0

    #void eq2horiz(double sinLat, double cosLat, double longitude,  double rightAscension, double declination, double agst,   double *azimuth, double *sinAlt) {
    ha     = Pagst + Llongitude - PrightAscension
    sinHa  = sin(ha)
    cosHa  = cos(ha)
    sinDec = sin(Pdeclination)
    cosDec = sqrt(1.0 - sinDec * sinDec)
    tanDec = sinDec/cosDec
    PazimuthRefract = atan2( sinHa,  cosHa  * LsinLat - tanDec * LcosLat )
    sinAlt = LsinLat * sinDec + LcosLat * cosDec * cosHa

    alt    = asin( sinAlt )
    cosAlt = sqrt(1.0 - sinAlt * sinAlt)

    alt -= 4.2635e-5 * cosAlt
    Paltitude = alt

    dalt  = 2.967e-4 / tan(alt + 3.1376e-3/(alt + 8.92e-2))
    dalt *= Lpressure/101.0 * 283.0/Ltemperature
    alt  += dalt

    PaltitudeRefract = alt
    
    if(computeRefrEquatorial):
        cosAz  = cos(PazimuthRefract)
        sinAz  = sin(PazimuthRefract)
        sinAlt = sin(PaltitudeRefract)
        cosAlt = sqrt(1.0 - sinAlt * sinAlt)
        tanAlt = sinAlt/cosAlt
        LhourAngleRefract   = atan2( sinAz ,  cosAz  * LsinLat + tanAlt * LcosLat )
        LdeclinationRefract = asin(  LsinLat * sinAlt  -  LcosLat * cosAlt * cosAz  )

    if(useNorthEqualsZero):
        PazimuthRefract = PazimuthRefract + PI;                       
        if(PazimuthRefract > TWO_PI): 
            PazimuthRefract -= TWO_PI       
        if(computeRefrEquatorial):
            PhourAngleRefract = PhourAngleRefract + PI;                 
            if(PhourAngleRefract > TWO_PI):
                PhourAngleRefract -= TWO_PI

    if(useDegrees):
        Plongitude      *= R2D
        PrightAscension *= R2D
        Pdeclination    *= R2D

        Paltitude        *= R2D
        PazimuthRefract  *= R2D
        PaltitudeRefract *= R2D

        if(computeRefrEquatorial):
            PhourAngleRefract  *= R2D
    
    return [ PazimuthRefract, PaltitudeRefract ]


def computeJulianDay( year, month, day, hour, minute, second ):
    if(month <= 2):
        year -= 1
        month += 12
    tmp1 = int( floor(year/100.0) )
    tmp2 = 2 - tmp1 + int( floor(tmp1/4.0) )
    dDay = day + hour/24.0 + minute/1440.0 + second/86400.0
    JD   = floor(365.250*(year-2000)) - 50.5 + floor(30.60010*(month+1)) + dDay + tmp2
    return JD 


'''
#  classs:
class RiseSet:
    def __init__(self):
        self.riseTime         = 0.0
        self.transitTime      = 0.0 
        self.setTime          = 0.0
        self.riseAzimuth      = 0.0
        self.transitAltitude  = 0.0    
        self.setAzimuth       = 0.0

class Position:
    def __init__(self):
        self.julianDay          = 0.0
        self.tJD                = 0.0 
        self.tJC                = 0.0 
        self.tJC2               = 0.0  
        self.UT                 = 0.0  
        self.longitude          = 0.0
        self.distance           = 0.0
        self.obliquity          = 0.0
        self.cosObliquity       = 0.0
        self.nutationLon        = 0.0
        self.rightAscension     = 0.0
        self.declination        = 0.0
        self.hourAngle          = 0.0
        self.agst               = 0.0
        self.altitude           = 0.0
        self.altitudeRefract    = 0.0
        self.azimuthRefract     = 0.0
        self.hourAngleRefract   = 0.0
        self.declinationRefract = 0.0

class Time:
    def __init__(self, year, month, day, hour, minute, second, utf = 3):
        self.year   = year + 2000 
        self.month  = month 
        self.day    = day   
        self.hour   = hour  + utf
        self.minute = minute
        self.second = second

class Location:
    def __init__(self, longitude, latitude, pressure = 101.0, temperature = 273.5 ):
        self.latitude    = latitude 
        self.longitude   = longitude 
        self.pressure    = pressure
        self.temperature = temperature    
        self.sinLat      = sin( latitude ) 
        self.cosLat      = sqrt( 1.0 - self.sinLat**2 ) 


class Solar: 
    def __init__(self, location : Location, time : Time, position : Position, useDegrees : bool = True, useNorthEqualsZero : bool = True, computeRefrEquatorial : bool = False, computeDistance : bool = False):
        self.location = location 
        self.position = position 
        self.time     = time

        self.useDegrees             = useDegrees
        self.useNorthEqualsZero     = useNorthEqualsZero 
        self.computeRefrEquatorial  = computeRefrEquatorial  
        self.computeDistance        = computeDistance 


    def compute( self, time : Time ) -> list:

        self.time = time

        if( self.useDegrees ): 
            self.location.longitude /= R2D
            self.location.latitude  /= R2D
        
        self.location.sinLat = sin(  self.location.latitude)
        self.location.cosLat = sqrt( 1.0 - self.location.sinLat**2 )

        self.position.julianDay = self.computeJulianDay( self.time.year, self.time.month, self.time.day,  self.time.hour, self.time.minute, self.time.second)
        
        self.position.UT   = self.time.hour + float( self.time.minute/60.0 ) + float( self.time.second/3600.0 )
        self.position.tJD  = self.position.julianDay
        self.position.tJC  = self.position.tJD / 36525.0
        self.position.tJC2 = self.position.tJC**2

        l0 = fmod(4.895063168 + 628.331966786 * self.position.tJC  +  5.291838e-6  * self.position.tJC2, TWO_PI)
        m  = fmod(6.240060141 + 628.301955152 * self.position.tJC  -  2.682571e-6  * self.position.tJC2, TWO_PI)

        c = fmod((3.34161088e-2 - 8.40725e-5*self.position.tJC - 2.443e-7*self.position.tJC2)*sin(m) + (3.489437e-4 - 1.76278e-6*self.position.tJC)*sin(2*m), TWO_PI)   # Sun's equation of the centre
        odot = l0 + c

        omg  = fmod(2.1824390725 - 33.7570464271 * self.position.tJC  + 3.622256e-5 * self.position.tJC2, TWO_PI)
        dpsi = -8.338601e-5*sin(omg)
        dist = 1.0000010178

        if( self.computeDistance ):
            ecc = 0.016708634 - 0.000042037   * self.position.tJC  -  0.0000001267 * self.position.tJC2
            nu = m + c
            dist = dist*( 1.0 - ecc*ecc) / (1.0 + ecc*cos(nu) )
        
        aber = -9.93087e-5/dist

        eps0 = 0.409092804222 - (2.26965525e-4*self.position.tJC + 2.86e-9*self.position.tJC2)
        deps = 4.4615e-5*cos(omg)

        self.position.longitude    = fmod(odot + aber + dpsi, TWO_PI)
        self.position.distance     = dist
        self.position.obliquity    = eps0 + deps
        self.position.cosObliquity = cos(self.position.obliquity)
        self.position.nutationLon  = dpsi

        #convertEclipticToEquatorial(self.position.longitude, self.position.cosObliquity,  &self.position.rightAscension, &self.position.declination)
        sinLon = sin(  self.position.longitude           )
        sinObl = sqrt( 1.0-self.position.cosObliquity**2 )

        self.position.rightAscension = atan2( self.position.cosObliquity*sinLon, cos(self.position.longitude) )
        self.position.declination    = asin( sinObl * sinLon )

        #void convertEquatorialToHorizontal(struct STLocation location, struct STPosition *position) {   
        gmst    = 1.75336856 + fmod(0.017202791805*self.position.tJD, TWO_PI) + 6.77e-6*self.position.tJC2 + self.position.UT/R2H
        self.position.agst = fmod(gmst + self.position.nutationLon * self.position.cosObliquity, TWO_PI)

        sinAlt=0.0

        #void eq2horiz(double sinLat, double cosLat, double longitude,  double rightAscension, double declination, double agst,   double *azimuth, double *sinAlt) {
        ha     = self.position.agst + self.location.longitude - self.position.rightAscension
        sinHa  = sin(ha)
        cosHa  = cos(ha)
        sinDec = sin(self.position.declination)
        cosDec = sqrt(1.0 - sinDec * sinDec)
        tanDec = sinDec/cosDec
        self.position.azimuthRefract = atan2( sinHa,  cosHa  * self.location.sinLat - tanDec * self.location.cosLat )
        sinAlt = self.location.sinLat * sinDec + self.location.cosLat * cosDec * cosHa

        alt = asin( sinAlt )
        cosAlt = sqrt(1.0 - sinAlt * sinAlt)

        alt -= 4.2635e-5 * cosAlt
        self.position.altitude = alt

        dalt = 2.967e-4 / tan(alt + 3.1376e-3/(alt + 8.92e-2))
        dalt *= self.location.pressure/101.0 * 283.0/self.location.temperature
        alt += dalt

        self.position.altitudeRefract = alt
        
        if(self.computeRefrEquatorial):
            cosAz  = cos(self.position.azimuthRefract)
            sinAz  = sin(self.position.azimuthRefract)
            sinAlt = sin(self.location.altitudeRefract)
            cosAlt = sqrt(1.0 - sinAlt * sinAlt)
            tanAlt = sinAlt/cosAlt
            self.location.hourAngleRefract   = atan2( sinAz ,  cosAz  * self.location.sinLat + tanAlt * self.location.cosLat )
            self.location.declinationRefract = asin(  self.location.sinLat * sinAlt  -  self.location.cosLat * cosAlt * cosAz  )

        if(self.useNorthEqualsZero):
            self.position.azimuthRefract = self.position.azimuthRefract + PI;                       
            if(self.position.azimuthRefract > TWO_PI): 
                self.position.azimuthRefract -= TWO_PI       
            if(self.computeRefrEquatorial):
                self.position.hourAngleRefract = self.position.hourAngleRefract + PI;                 
                if(self.position.hourAngleRefract > TWO_PI):
                    self.position.hourAngleRefract -= TWO_PI

        if(self.useDegrees):
            self.position.longitude      *= R2D
            self.position.rightAscension *= R2D
            self.position.declination    *= R2D

            self.position.altitude        *= R2D
            self.position.azimuthRefract  *= R2D
            self.position.altitudeRefract *= R2D

            if(self.computeRefrEquatorial):
                self.position.hourAngleRefract  *= R2D
                self.position.declinationRefract *= R2D
        
    def get_azimute(self):
        return self.position.azimuthRefract
        
    def get_altitude(self):
        return self.position.altitudeRefract 

    def computeJulianDay(self, year, month, day, hour, minute, second ):
        if(month <= 2):
            year -= 1
            month += 12
        tmp1 = int( floor(year/100.0) )
        tmp2 = 2 - tmp1 + int( floor(tmp1/4.0) )
        dDay = day + hour/24.0 + minute/1440.0 + second/86400.0
        JD   = floor(365.250*(year-2000)) - 50.5 + floor(30.60010*(month+1)) + dDay + tmp2
        return JD 
'''

