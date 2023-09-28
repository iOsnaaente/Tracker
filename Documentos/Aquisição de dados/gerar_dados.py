from dearpygui.dearpygui import *
from math                import degrees

import datetime as dt 
import pandas   as pd
import ephem    as ep 


azi  = 0.0 
alt = 0.0 

date = '' 

LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 425

observer = ep.Observer()

observer.lat       = LATITUDE 
observer.lon       = LONGITUDE 
observer.elevation = ALTITUDE  


def read_arq( file : str = 'data.csv' ):
    arq = []
    with open(file, 'r') as f: 
        lines = f.readlines() 
        for line in lines: 
            arq.append(line)
    return arq 

def compute_samples( observer : ep.Observer, num_samples : int = 2000 ):
    pos_M1 = 0.0 
    pos_M2 = 0.0 
    date = dt.datetime.utcnow()
    sun  = ep.Sun()

    samples = [] 
    for sample in range( num_samples ):
        date += dt.timedelta( seconds= 240 )
        observer.date = date 
        sun.compute( observer ) 
        
        pos_M1 += ( pos_M1 - float(sun.az)  )*2/60 
        pos_M2 += ( pos_M1 - float(sun.alt) )*2/60 
        pos_M1 = pos_M1 %360
        pos_M2 = pos_M2 %360

        samples.append( [date, float(sun.az), float(sun.alt),  pos_M1, pos_M2] )
    return samples 

def write_samples(samples : list , file : str = 'data.csv'):
    with open( file, 'w') as f:
        f.write('date,azimute,altitude,pos1,pos2\n')
        for sample in samples:
            f.write( str(sample[0]) + ',' + str(sample[1]) + ',' )
            f.write( str(sample[2]) + ',' + str(sample[3]) + ',' )
            f.write( str(sample[4]) + '\n' )

def transform( data : list ) -> list:
    return [ float(value) for value in data ]

def deg( data : list, func ) -> list:
    return [ func(value) for value in data ]

def plot_graph():
    read_from = pd.read_csv( 'data.csv')    
    date_data = [ num for num, value in enumerate( read_from['date']) ] 
    azi_data  = [ degrees(value) for value in read_from['azimute']    ]
    alt_data  = [ degrees(value) for value in read_from['altitude']   ]

    with window(label='main') as win:
        add_group(       label='unidosSomosMais', horizontal= False )
        add_plot(        label='plotAzi'        , width= 800    , height= 350  , id = 1 )
        add_line_series( label='plotAzi'        , x = date_data , y = azi_data , id = 2 )
        add_plot(        label='plotAlt'        , width= 800    , height= 350  , id = 3 )
        add_line_series( label='plotAlt'        , x = date_data , y = alt_data , id = 4 )
        
    start_dearpygui( primary_window= win)

if __name__ == '__main__':
    sample = compute_samples(observer)
    write_samples( sample )
    plot_graph()