from machine import Pin, Timer
import sys, uselect, time

led_builtin = Pin( 25, Pin.OUT )
spoll = uselect.poll()
spoll.register( sys.stdin, uselect.POLLIN )

command = bytes()
validcommand = False

def ReadSerial():
    global command, validcommand, commandlist
    #   This a non-blocking read of the stdin (REPL port)
    got = spoll.poll( 1) 
    if got:
        print ( sys.stdin.read(1), got )
    else:
        print( time.ticks_ms() ) 
        
        
#while True: 
print ("Listening for commands >>")
while True:
    ReadSerial()
    if validcommand:
        command = bytes()
        validcommand = False
