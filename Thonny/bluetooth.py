from machine import UART

bluetooth = UART( 0, baudrate = 9600 ) 

while True:
    if uart.any():
        command = uart.readline()
        print(command)
        