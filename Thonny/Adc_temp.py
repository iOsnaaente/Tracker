from machine import Pin, ADC
from time import sleep 

LED_BUILTIN = Pin( 25, Pin.OUT )
TEMP        = ADC( 4 )

while True:
    LED_BUILTIN.toggle() 
    
    temp = TEMP.read_u16()*( 3.3 / (2**16) );
    temp = 27 - (temp - 0.706)/0.001721
    
    print( temp )
    
    sleep(0.5)
            