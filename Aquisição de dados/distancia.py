import datetime as dt 
import pandas   as pd
import ephem    as ep 

import math


tg = lambda ang : math.tan( math.radians(ang ) )  

date = '' 

LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 5

observer = ep.Observer()

observer.lat       = LATITUDE 
observer.lon       = LONGITUDE 
observer.elevation = ALTITUDE  
math.at

def get_alt( observer : ep.Observer, num_samples : int ):
    date : dt   = dt.datetime( 2021, 12, 21, 0, 0, 0 )
    sun  : ep   = ep.Sun() 
    alt  : list = []
    dat  : list = [] 

    for _ in range( num_samples ):
        date += dt.timedelta( seconds = 60)
        observer.date = date 
        sun.compute( observer ) 
        if sun.alt >= 0: 
            alt.append( math.degrees( float(sun.alt)) )
            dat.append( date - dt.timedelta(hours=3) )
    
    return [dat, alt]

date, alt = get_alt( observer, 60*24 )

shadow : list = []
s_date : list = []

tg = lambda d : math.tan( math.radians( d ) )
y  = lambda t, x, h : -tg(t)*x + h

for deg, sd in zip(alt, date) : 
    cl = ALTITUDE/tg(deg)
    if abs(cl) < 30:
        shadow.append( cl )
        s_date.append( sd )

from matplotlib import pyplot as plt 

plt.plot( date, alt, 'b-' )
plt.plot( s_date, shadow, 'r-' )
plt.show()