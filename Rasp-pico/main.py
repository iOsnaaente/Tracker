from Motor_step import Motors
DIR_MOTOR1    = 0 
STEP_MOTOR1   = 1
ENABLE_MOTOR1 = 2
DIR_MOTOR2    = 3 
STEP_MOTOR2   = 4
ENABLE_MOTOR2 = 5

MOTORS = Motors( STEP_MOTOR1, DIR_MOTOR1, ENABLE_MOTOR1, STEP_MOTOR2, DIR_MOTOR2, ENABLE_MOTOR2 )
MOTORS.configure( MOTORS.GIR, pos = 0.0, step = 1.8, micro_step = 16, ratio = 1000 )
MOTORS.configure( MOTORS.ELE, pos = 0.0, step = 1.8, micro_step = 16, ratio = 1000 )


from machine import Pin
LED1_RED   = Pin(10, Pin.OUT)
LED1_BLUE  = Pin(11, Pin.OUT)
LED2_RED   = Pin(12, Pin.OUT)
LED2_BLUE  = Pin(13, Pin.OUT)

# AVISO QUE ESTA LIGADO 
LED1_BLUE.high()
LED1_RED.low()
LED2_BLUE.low()
LED2_RED.low()


from I2C_RTC import DS3231
ADDR_DS = [0x68, 0x57] 
SDA_DS = Pin( 16 ) 
SCL_DS = Pin( 17 )
DS = DS3231( 0, SDA_DS, SCL_DS, addrs = ADDR_DS )
#DS.set_time( 21, 6, 24, 5, 11, 56, 3  )


from SunPosition import * 
LATITUDE  = -29.16530765942215
LONGITUDE = -54.89831672609559 
TIME      = [ 2021, 6, 23, 18, 6, 0, 3 ]
LOC       = [ LATITUDE, LONGITUDE, 298.5, 101.0 ]

azimute = 0.0
altitude = 0.0

from time import sleep
import select
import struct 
import sys
import gc

gc.enable()

debug = False 

while True:
    TIME = DS.now()
     
    sys.stdout.write( struct.pack('b', 99 ) )
    sys.stdout.write( struct.pack('B', struct.calcsize('ffBBBBBBbB') ) )
    sys.stdout.write( struct.pack('ff', azimute, altitude ) )
    sys.stdout.write( struct.pack('BBBBBB', TIME[0], TIME[1], TIME[2], TIME[3], TIME[4], TIME[5] ) )
    
    while sys.stdin in select.select( [sys.stdin], [], [], 0 )[0]:        
        cmd = sys.stdin.read(1)
        if (cmd == 'h'): 
            get_time = struct.unpack( 'BBBBBB', sys.stdin.read(6) )
            DS.set_time( get_time[0], get_time[1], get_time[2], 1, get_time[3], get_time[4], get_time[5] )
            if debug:
                TIME = DS.now() 
                sys.stdout.write( 'Input = h : Correção da Hora' )
                sys.stdout.write( 'Nova data/hora = %i/%i/%i - %i:%i:%i ' %(TIME[0],TIME[1],TIME[2],TIME[3],TIME[4],TIME[5]) ) 
        
    # LED TOGGLE INDICATOR 
    LED1_RED.toggle()
    sleep(0.1)
    LED1_RED.toggle()
    sleep(0.9)
    
    azimute, altitude = compute( LOC, TIME )
    
    LED2_BLUE.value ( 1 if altitude > 0 else 0 )
    LED2_RED.value  ( 0 if altitude > 0 else 1 )
    
    # SALVAR A DATA NA EEPROM DO RASP
    # FAZER O PINO DE INTERRUPÇÃO CASO FALTE LUZ 
    
    # GARBAGE COLLECTOR 
    gc.collect()



