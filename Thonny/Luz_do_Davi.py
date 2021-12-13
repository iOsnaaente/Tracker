from   machine import Pin  , PWM 
from   time    import sleep
import random

red   = PWM( Pin( 18, Pin.OUT ) )
green = PWM( Pin( 17, Pin.OUT ) )
blue  = PWM( Pin( 16, Pin.OUT ) ) 


red.freq(1000)
green.freq(1000)
blue.freq(1000)



while True:
    value_red   = random.randint( 0, 2**16 )
    red.duty_u16( value_red ) 
    
    value_green = random.randint( 0, 2**16 )
    green.duty_u16( value_green ) 
    
    value_blue  = random.randint( 0, 2**16 )
    blue.duty_u16( value_blue ) 
    
    sleep( 1 ) 