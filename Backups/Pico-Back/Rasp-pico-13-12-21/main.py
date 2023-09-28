from machine    import Pin, I2C, UART
from time       import sleep, ticks_ms
from math       import sin

from myAS5600   import AS5600 
from StepMotors import Motors
from Const      import *

import struct
import select 
import sys


isc = I2C(1, scl = Pin(19, Pin.PULL_UP), sda = Pin(18, Pin.PULL_UP) )
uart = UART( 1, 19200, tx = Pin(UART_TX), rx = Pin(UART_RX) )

print ( isc.scan() ) 
print ( uart ) 


MOTORS = Motors( STEP_GIR, DIR_GIR, STEP_ELE, DIR_ELE, ENABLE_MTS )
MOTORS.configure( MOTORS.GIR, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
MOTORS.configure( MOTORS.ELE, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
MOTORS.set_torque( True )

p = Pin( POWER, Pin.OUT )
p(1) 

# SERIAL CONFIGURAÇÕES 
BYTE_INIT = [b'I',b'N',b'I',b'T']  
count     = 0

ActualMeasure = 0
LastMeasure = 0
Error = 0
Kp = 0.75
Ki = 0.5
Kd = 0.2
dt = 1

PID = lambda E, So, Si, dt : Kp*E + Ki*((So-Si)*dt/2) + Kp*Kd*(E/dt)*So 

PV = 180 

LastMeasure = struct.unpack( '>h', isc.readfrom_mem(0x36, 0xc,2))[0]
dto = ticks_ms() 
sleep( 0.5 )

while True:
    
    ActualMeasure = (struct.unpack( '>h', isc.readfrom_mem(0x36, 0xc,2))[0])
    Error = abs(PV - ActualMeasure*(360/0x0fff) )
    Error = 0 if round( Error ) == 0 else Error 
    LastMeasure = ActualMeasure 
    
    dti = ticks_ms()
    dt = dti - dto 
    dto = dti
    
    diff_pos = PID( Error, ActualMeasure, LastMeasure, dt  )
    
    direc = 1 if ActualMeasure*(360/0x0fff) < PV else -1 
    posE = (diff_pos*direc)*0.1
    posG = (diff_pos*direc)*0.1 
    
    read = struct.pack( 'f', ActualMeasure ) 
    uart.write( 'init'.encode() + read)
    
    # VERIFICA SE RECEBEU ALGO DA SERIAL 
    while uart.any(): 
        cmd = uart.read(1)
        if cmd == BYTE_INIT[count]:  count += 1
        else:                        count  = 0
 
        if count == 4:
            count = 0
            BYTE_ID  = uart.read(1)
            
            if BYTE_ID == b'F':
                confirm = uart.read(1)
                if confirm == b'O':
                    p.low()
                    
            if BYTE_ID == b'O':
                confirm = uart.read(1)
                if confirm == b'O':
                    p.high()
                    
            if BYTE_ID == b'P':
                confirm = uart.read(1)
                if confirm == b'V':
                    PV = (struct.unpack( 'f', uart.read(4) )[0])
                    print("\nPV: ", PV ) 
                    
                if confirm == b'D':
                    Kd = (struct.unpack( 'f', uart.read(4) )[0])
                    print("\nKd: ", Kd ) 
                    
                if confirm == b'I':
                    Ki = (struct.unpack( 'f', uart.read(4) )[0])
                    print("\nKi: ", Ki ) 
                    
                if confirm == b'P':
                    Kp = (struct.unpack( 'f', uart.read(4) )[0])
                    print( "\nKp: ", Kp ) 
                
                    
                    
    MOTORS.move( posG, posE )
            
    sleep(0.1)
