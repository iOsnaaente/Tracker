from sys import stdin, exit
from _thread import start_new_thread
from utime import sleep

bufferSize      = 1024                # Size of circular buffer to allocate
buffer          = [' '] * bufferSize  # Circuolar incomming USB serial data buffer (pre fill)
bufferEcho      = True                # USB serial port echo incooming characters  (True/False) 
bufferNextIn    = 0                   # Pointer to next In caracter in circular buffer
bufferNextOut   = 0                   # pointer to next Out character in circualr buffer
terminateThread = False               # tell 'bufferSTDIN' function to terminate (True/False)

def bufferSTDIN():
    global buffer, bufferSize, bufferEcho, bufferNextIn, terminateThread
    while True:                                 # Endless loop
        if terminateThread:                     # if requested by main thread ...
            break                               #    ... exit loop

        buffer[bufferNextIn] = stdin.read(1)    # Wait for/store next byte from USB serial
        if bufferEcho:                          # if echo is True ...
            print(buffer[bufferNextIn], end='') #    ... output byte to USB serial

        bufferNextIn += 1                       # bump pointer
        if bufferNextIn == bufferSize:          # ... and wrap, if necessary
            bufferNextIn = 0

def getByteBuffer():
    global buffer, bufferSize, bufferNextOut, bufferNextIn
    
    if bufferNextOut == bufferNextIn:           # if no unclaimed byte in buffer ...
        return ''                               #    ... return a null string
    n = bufferNextOut                           # save current pointer
    bufferNextOut += 1                          # bump pointer
    if bufferNextOut == bufferSize:             #    ... wrap, if necessary
        bufferNextOut = 0
    return (buffer[n])                          # return byte from buffer


def getLineBuffer():
    global buffer, bufferSize, bufferNextOut, bufferNextIn

    if bufferNextOut == bufferNextIn:           # if no unclaimed byte in buffer ...
        return ''                               #    ... RETURN a null string

    n = bufferNextOut                           # search for a LF in unclaimed bytes
    while n != bufferNextIn:
        if buffer[n] == '\x0a':                 # if a LF found ... 
            break                               #    ... exit loop ('n' pointing to LF)
        n += 1                                  # bump pointer
        if n == bufferSize:                     #    ... wrap, if necessary
            n = 0
    if (n == bufferNextIn):                     # if no LF found ...
            return ''                           #    ... RETURN a null string

    line = ''                                   # LF found in unclaimed bytes at pointer 'n'
    n += 1                                      # bump pointer past LF
    if n == bufferSize:                         #    ... wrap, if necessary
        n = 0

    while bufferNextOut != n:                   # BUILD line to RETURN until LF pointer 'n' hit
        
        if buffer[bufferNextOut] == '\x0d':     # if byte is CR
            bufferNextOut += 1                  #    bump pointer
            if bufferNextOut == bufferSize:     #    ... wrap, if necessary
                bufferNextOut = 0
            continue                            #    ignore (strip) any CR (\x0d) bytes
        
        if buffer[bufferNextOut] == '\x0a':     # if current byte is LF ...
            bufferNextOut += 1                  #    bump pointer
            if bufferNextOut == bufferSize:     #    ... wrap, if necessary
                bufferNextOut = 0
            break                               #    and exit loop, ignoring (i.e. strip) LF byte
        line = line + buffer[bufferNextOut]     # add byte to line
        bufferNextOut += 1                      # bump pointer
        if bufferNextOut == bufferSize:         #    wrap, if necessary
            bufferNextOut = 0
    return line                                 # RETURN unclaimed line of input


# Incia a segunda Core
try: 
    bufferSTDINthread = start_new_thread(bufferSTDIN, ())
    print( 'Started the second core' ) 
except:
    print( 'Second core already started before' )

