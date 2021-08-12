from struct import pack, unpack
from serial import Serial 
from time   import sleep 

import sys 


msg  = [ ord(b) for b in 'initm ']  

comp = Serial( 'COM15' )

raw = 50

while True:   
    msg[-1] = raw  
    print( msg )    

    for i in msg: 
        comp.write( chr(i).encode() ) 
    
    sleep(2)
    num = comp.inWaiting() 
    print( 'entrou na função com %s bytes para ler' %num )
    for i in range( num ):
        val = comp.read(1)
        print( val.decode(), end ='' ) 
    
    try:
        raw = int( input() )
    except:
        raw = 1