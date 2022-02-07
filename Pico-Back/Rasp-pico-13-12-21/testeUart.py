from machine    import Pin, I2C, UART
import struct

uart = UART( 1, 19200, tx = Pin(20), rx = Pin(21) )

while True:
    
    while uart.any():
        val = uart.read(1) 
        print( val )