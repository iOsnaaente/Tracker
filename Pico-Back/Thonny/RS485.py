from machine import Pin
from machine import UART
from time    import sleep

import select 

RX = 22
TX = 21

rs485 = UART( 0, 19200, bits = 8, parity = None, stop = 2 )

while True:
    print( rs485.read(1) )
    rs485.write('201720094') 
    sleep(1) 