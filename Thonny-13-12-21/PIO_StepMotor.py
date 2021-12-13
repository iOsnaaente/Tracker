from machine import Pin, ADC
import utime
import time

step_m1 = Pin( 10 )
step_m2 = Pin( 12 )

dir_m1 = Pin( 11, Pin.OUT)
dir_m2 = Pin( 13, Pin.OUT)

@rp2.asm_pio( set_init = rp2.PIO.OUT_LOW )
def move():
    label('init')
    pull( )
    mov( x, osr )
    
    label( 'step_m1' )
    set(pins, 1)           [ 31 ]
    nop()                  [ 31 ]
    set(pins, 0)           [ 31 ]
    jmp( x_dec, 'step_m1') [ 31 ]
    
    jmp( 'init' )

    
"""Instantiate a state machine with the move
program, at 100000Hz, with set base to step pin."""
motor1 = rp2.StateMachine(0, move, freq=2000, set_base= step_m1 )
motor2 = rp2.StateMachine(1, move, freq=2000, set_base= step_m2 )

# Set directions
dir_m1.value(0)
dir_m2.value(0)

# Start your motor!
motor1.active(1)
motor2.active(1)



while True:
    data =  [ int(data) for data in input('PM1 PM2 SD1 SD2: ').split(' ')]
    
    value  = 0
    value += ( data[0] << 10 )
    value += ( data[1] << 2  )
    value += ( data[2] << 1  )
    value += ( data[3] << 0  ) 
    
    motor1.put( data[0] )
    motor2.put( data[1] )
    
    for i in range( 4010 ):
        print( i )

