from math import *

# Constants:
MPI    = 3.14159265358979323846e6  # One Megapi...
R2D    = 57.2957795130823208768    # Radians to degrees conversion factor
R2H    = 3.81971863420548805845    # Radians to hours conversion factor
TWO_PI = 6.28318530717958647693
PI     = 3.14159265358979323846


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


def inv( Matriz_A : list ) -> list:
    N = len(Matriz_A) if len(Matriz_A) == len(Matriz_A[0]) else 0
    identidade = [ [ 0 for _ in range(N)] for _ in range(N) ]
    for linha in range( N ):
        for coluna in range(N):
            if(linha == coluna):
                identidade[linha][coluna] = 1
            else:
                identidade[linha][coluna] = 0     
    for coluna in range(N):
        pivo = Matriz_A[coluna][coluna]
        for k in range(N):
            Matriz_A[coluna][k] = (Matriz_A[coluna][k])/(pivo)
            identidade[coluna][k] = (identidade[coluna][k])/(pivo)
        for linha in range(N):
            if(linha != coluna):
                m = Matriz_A[linha][coluna]
                for k in range(N):
                    Matriz_A[linha][k] = (Matriz_A[linha][k]) - (m*Matriz_A[coluna][k])
                    identidade[linha][k] = (identidade[linha][k]) - (m*identidade[coluna][k])
    return identidade 

def dot_mat_vec( mat_a : list, vector : list ) -> list: 
    if len(mat_a[0]) != len(vector):
        return 'Dismatch matricial'
    else:
        M = len(mat_a   )
        N = len(mat_a[0])
        P = 1
        doted = [ [ 0 ] for _ in range( M ) ]
    for i in range(M):
        for j in range(P):
            for k in range(N):
                doted[i][j] += mat_a[i][k] * vector[k]
    return doted 


def dot( mat_a : list , mat_b : list) -> list: 
    if len(mat_a[0]) != len(mat_b):
        return 'Dismatch matricial'
    else: 
        M = len(mat_a   )
        N = len(mat_a[0])
        P = len(mat_b[0])
        doted = [ [ 0 for _ in range(P) ] for _ in range( M ) ]
    for i in range(M):
        for j in range(P):
            for k in range(N):
                doted[i][j] += mat_a[i][k] * mat_b[k][j]
    return doted 


def pow_dot( mat_a : list, exp : int ) -> list : 
    if exp == 1 :
        return mat_a 
    elif exp == 0 :
        return 1
    else : 
        return dot(mat_a, pow_dot( mat_a, exp -1 )) 

def pow_vector( Min : list, exp : int ) -> list:
    return [ Min[i]**exp for i in range(len(Min)) ]


def transp( mat : list) -> list:
    return list(map(lambda *i: [j for j in i], *mat))


def linspace( pI : float, pF : float, qtd : int ) -> list:
    dI = (pF - pI)/(qtd-1)
    return [ dI*i + pI for i in range(qtd)]


def polyval( P : list, X : list ) -> float: 
    r_poly = [ 0 for i in range(len(X))] 
    N = len(P)
    T = len(X)
    for x in range( T ):
        for i in range(1,N+1):
            r_poly[x] += P[i-1]*X[x]**(N-i)
    return r_poly 


def get_aprox( Xin : list, Yin : list, num : int = 0 ) -> None:
    V = transp( [ pow_vector(Xin, 4), pow_vector(Xin, 3), pow_vector(Xin, 2), pow_vector(Xin, 1), pow_vector(Xin, 0) ] ) 
    a = transp( dot_mat_vec( dot( inv( dot( transp( V ), V) ), transp(V)), Yin ) )[0]    
    Xout = linspace( Xin[0], Xin[-1], len(Xin) if not num else num )
    Yout = polyval( a, Xout )
    return [ Xout, Yout ]


def compute_all_day( LOC : Location, TIME : Time  ) -> list:
    # Zera a hora para fazer a contagem
    TIME = Time( TIME.year, TIME.month, TIME.day, 0, 0, 0 )
    tomorrow = TIME.day 
    azi = []
    alt = []
    dat = []
    
    date = []

    while True: 
        second = TIME.second
        minute = TIME.minute
        hour   = TIME.hour -3
        day    = TIME.day 
        month  = TIME.month
        year   = TIME.year

        SUN  = Solar( LOC, TIME, Position, useNorthEqualsZero= 0  )
        SUN.compute( TIME )

        if SUN.get_altitude() > 0 :
            date.append( [ hour, minute ] )
            dat.append( hour + minute/60 + second/3600 )
            azi.append( abs(SUN.get_azimute()) if SUN.get_azimute() < 0 else 360-SUN.get_azimute()   )
            alt.append( SUN.get_altitude() )
        minute += 30 
        if minute == 60:
            minute = 0
            hour += 1 
            if hour == 24:
                hour = 0
                day += 1 
        TIME = Time( year, month, day, hour, minute, second)

        if TIME.day != tomorrow :
            break
    
    rat  = 5
    Xo   = [ dat[i] for i in range(len(dat)) if i%rat == 0 ]
    Alt  = [ alt[i] for i in range(len(alt)) if i%rat == 0 ]
    Azi  = [ azi[i] for i in range(len(azi)) if i%rat == 0]
    
    min_pos = date[  0 ]
    max_pos = date[ -1 ]
    delta_sun = (max_pos[0]-min_pos[0])*60 + (max_pos[1]-min_pos[1])
    
    dat, alt = get_aprox( Xo, Alt, delta_sun )
    dat, azi = get_aprox( Xo, Azi, delta_sun )
    
    return [ min_pos, dat, alt, azi, max_pos ]


    

