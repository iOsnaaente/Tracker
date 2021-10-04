from StepMotors import * 
from _thread    import allocate_lock 
from struct     import unpack, pack
from time       import sleep
from machine    import Pin
import select 
import sys

MOTORS = Motors( gir_stp = 0, gir_dir = 3  , ele_stp = 1  , ele_dir    = 4 , enb_motors = 14 )
MOTORS.configure( MOTORS.GIR, pos     = 0.0, step    = 1.8, micro_step = 16, ratio      = 1  )
MOTORS.configure( MOTORS.ELE, pos     = 0.0, step    = 1.8, micro_step = 16, ratio      = 1  )
MOTORS.set_torque( True )


UNAVAILABLE = 0
AVAILABLE   = 1

LED_BUILTIN = Pin( 25, Pin.OUT )

data_rec    = bytearray(16)
byte_init   = b'init'  
byte_len    = int(0)
byte_id     = chr(0) 
read_state  = UNAVAILABLE

unpacked = lambda n_bytes, byte_type = 'B' : unpack( byte_type, sys.stdin.buffer.read( n_bytes ))[0]

while True:    
    LED_BUILTIN.toggle()
    count = 0 
    while sys.stdin in select.select( [sys.stdin], [sys.stdout], [sys.stderr], 0 )[0]:
        if read_state == UNAVAILABLE:
            cmd = sys.stdin.read(1)
            
            if cmd == byte_init[count]:  count += 1
            else:                        count  = 0
            
            if count == 4:  read_state = AVAILABLE
            else:           read_state = UNAVAILABLE
            
        if read_state == AVAILABLE:
                byte_len = unpacked(1)
                byte_id  = unpacked(1)
                
                if   byte_id == b'H':
                        call_set_hour()
                elif byte_id == 'M':
                        call_motor_control()
                    
                read_state = UNAVAILABLE
                count      = 0
    sleep( 0.1 ) 
        
def call_set_hour( lenght ):
    if lenght != 6:
        return 0
    
    get_time = sys.stdin.buffer.read( lenght  ) 
    print( get_time, len(get_time), type( get_time )   )
    #DS.set_time( get_time[0], get_time[1], get_time[2], 1, get_time[3], get_time[4], get_time[5] )
    #TIME     = DS.now()

def call_motor_control( lenght ):
    if lenght != 8:
        return 0 
    
    gir_mot = unpacked( 4, 'h' )
    ele_mot = unpacked( 4, 'h' )
    
    print( gir_mot, ele_mot )
    
    MOTORS.move( gir_mot, ele_mot, 10 )
    
    
    
    


