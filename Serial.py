from struct import pack, unpack
from serial import Serial 
from time   import sleep 

import sys 
 
comp = Serial( 'COM16' )

def get_nBytes( comp : Serial ): 
    return comp.inWaiting() 

def send_msg( comp : Serial, msg : str ):
    for s in msg:
        comp.write( s.encode() ) 

def receive_msg( comp : Serial ):
    num = get_nBytes( comp )
    msg = comp.read( num ).split(b'INIT')
    for line in msg:
        if line:
            LENG = line[0]
            if LENG == 19:
                try:
                    DATA = unpack( 'ff'    , line[1:9]  )
                    TIME_D = [ b for b in line[10:13] ]
                    TIME_H = [ b for b in line[14:17] ]  
                    return DATA, TIME_D, TIME_H 
                except:
                    print( line )
                    return None 

while True:   
    sleep( 0.1 )
    DATA = receive_msg( comp )  
    if DATA:
        [azi, alt], [y,m,d], [h, mi, s]  = DATA   
        print( azi, alt )