from machine import Pin, PWM
from time import sleep

LED_BUILTIN = Pin( 25, Pin.OUT )

FADE = PWM( LED_BUILTIN )
FADE.freq( 1000 )           # 1000 ciclos por segundou ou 1kHz 


while True:
    for i in range( 0, 2**16, 100 ):
        FADE.duty_u16( i )
        sleep( 0.005 ) 