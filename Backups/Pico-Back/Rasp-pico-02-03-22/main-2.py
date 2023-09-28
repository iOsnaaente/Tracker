from machine import Pin, ADC
import time
import struct 

pinSom = ADC( Pin( 28, Pin.IN ) )

while True:
    read = pinSom.read_u16()
    print( b'INIT' + struct.pack( 'f', read ) ) 
    time.sleep(0.001)
    

from machine import Pin, I2C, UART, ADC 
from time    import sleep
from sys     import stdout
from struct  import pack, unpack 

isc = I2C( 0, freq = 1_000_000, scl = Pin(17), sda = Pin(16)  )

as5600 = AS5600( isc, 54 )

read_sensor = ADC( 2 ) 

uart = UART( 0, 9600, tx=Pin(0), rx=Pin(1) )

#for i in range( 9 ):
#    as5600._write( i, chr(0) )

while 1:
    print(as5600.readAngle())
    
    sleep( 0.1 ) 