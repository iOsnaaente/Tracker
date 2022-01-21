from select import select 
import sys 

bufferSize      = 16                  # Size of circular buffer to allocate
buffer          = [' '] * bufferSize  # Circuolar incomming USB serial data buffer (pre fill)
bufferEcho      = False               # USB serial port echo incooming characters  (True/False) 
bufferNextIn    = 0                   # Pointer to next In caracter in circular buffer
bufferNextOut   = 0                   # pointer to next Out character in circualr buffer
terminateThread = False               # tell 'bufferSTDIN' function to terminate (True/False)

def getBytesSerial():
    global bufferSize, buffer, bufferEcho, bufferNextIn, bufferNextOut
    bufferNextIn = 0 
    while sys.stdin in select( [sys.stdin], [sys.stdout], [sys.stderr], 0 )[0]:  
        buffer[bufferNextIn] = sys.stdin.buffer.read(1)    # Wait for/store next byte from USB serial
        if bufferEcho:                                     # if echo is True ...
            print(buffer[bufferNextIn], end='')            #    ... output byte to USB serial
        bufferNextIn += 1                                  #  bump pointer
        if bufferNextIn == bufferSize:                     # ... and wrap, if necessary
            bufferNextIn = 0
    return buffer[:bufferNextIn] 