from machine import Pin 

import select 
import sys 

HIGH = 1 
LOW  = 0  

PIN = Pin( 15, Pin.OUT )
LED = Pin( 25, Pin.OUT )

STATE = LOW  

PIN.value( STATE )
LED.value( HIGH  )


while True:     
    while sys.stdin in select.select( [sys.stdin], [sys.stdout], [sys.stderr], 1 )[0]: 
        const = sys.stdin.buffer.read(1) 
        if const == 10 or const == 32 :
            PIN.toggle() 
            if PIN.value() == HIGH: 
                print( 'Ligado' )
            else: 
                print( 'Desligado' )

    LED.toggle()
