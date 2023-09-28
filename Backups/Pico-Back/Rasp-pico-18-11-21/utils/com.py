from struct   import pack, unpack
from time     import sleep 

import serial 


def create_msg( id : str, len : int, data : bytearray ):
    send = ('init%s'%id).encode() 
    send += bytearray( pack('b', len) )
    for b in data:
        send += pack( 'b', b ) 
    return send

from datetime import datetime as dt 


with serial.Serial( 'COM16' ) as comp: 
    while True : 
        data = dt.now() 
        data = bytearray( [ data.year-2000, data.month, data.day, data.hour, data.minute, data.second ])     
        send = create_msg( 'h', 6, data )

        comp.write( send )
        sleep( 1 )
        if comp.inWaiting() > 0 : 
            n = comp.inWaiting() 
            r = comp.read( n )
            print( r )