from Motor_step  import Motors
from I2C_RTC     import DS3231
from time        import sleep
from machine     import Pin
from SunPosition import *

import select
import struct 
import sys
import gc


# VARIÁVEIS USADAS NAS GPIOs DO RASPICO 
DIR_GIR     = 0
DIR_ELE     = 1
DIR_GEN     = 2 

STEP_GIR    = 3 
STEP_ELE    = 4 
STEP_GEN    = 5

BUTTON_GP   = 6 
BUTTON_GM   = 7

BUTTON_EP   = 8
BUTTON_EM   = 9

LED1_RED    = 10
LED1_BLUE   = 11
LED2_RED    = 12
LED2_BLUE   = 13

ENABLE_MTS  = 14

NOT_USED    = 15

SDA_DS      = 16 
SCL_DS      = 17

EE_SCK      = 18
EE_DOO      = 19
EE_DIO      = 20
EE_CS       = 21

LED_BUILTIN = 25

# INSTANCIAMENTO DOS PERIFÉRICOS 
MOTORS = Motors( STEP_GIR, DIR_GIR, STEP_ELE, DIR_ELE, ENABLE_MTS )
MOTORS.configure( MOTORS.GIR, pos = 0.0, step = 1.8, micro_step = 16, ratio = 1000 )
MOTORS.configure( MOTORS.ELE, pos = 0.0, step = 1.8, micro_step = 16, ratio = 1000 )
MOTORS.set_torque( True )

BUTTON_GP  = Pin( BUTTON_GP, Pin.IN, Pin.PULL_UP )
BUTTON_GM  = Pin( BUTTON_GM, Pin.IN, Pin.PULL_UP )
BUTTON_EP  = Pin( BUTTON_EP, Pin.IN, Pin.PULL_UP )
BUTTON_EM  = Pin( BUTTON_EM, Pin.IN, Pin.PULL_UP )

LED1_RED   = Pin(10, Pin.OUT)
LED1_BLUE  = Pin(11, Pin.OUT)
LED2_RED   = Pin(12, Pin.OUT)
LED2_BLUE  = Pin(13, Pin.OUT)

LED_BUILTIN = Pin( LED_BUILTIN, Pin.OUT ) 

ADDR_DS = [0x68, 0x57] 
SDA_DS = Pin( SDA_DS ) 
SCL_DS = Pin( SCL_DS )
DS = DS3231( 0, SDA_DS, SCL_DS, addrs = ADDR_DS )
#DS.set_time( 21, 7, 20, 5, 18, 6, 30  )


LATITUDE  = -29.16530765942215
LONGITUDE = -54.89831672609559 
TIME      = [ 2021, 6, 23, 18, 6, 0, 3 ]
LOC       = [ LATITUDE, LONGITUDE, 298.5, 101.0 ]

azimute = 0.0
altitude = 0.0

# AVISO QUE ESTA LIGADO 
LED1_BLUE.high()
LED1_RED.low()
LED2_BLUE.low()
LED2_RED.low()

gc.enable()

debug = False

import  _thread
baton = _thread.allocate_lock()

def pulse(pin):
    pin.high()
    sleep(0.001)
    pin.low()
    sleep(0.001)

def motors_control( ):
    while True:
        flag = '' 
        if BUTTON_GP.value() == 0:
            MOTORS.move( 1, 0 )
            LED1_BLUE.toggle()
            flag =  "GIRO P "
            
        elif BUTTON_GM.value() == 0:
            MOTORS.move(-1, 0 )
            LED1_RED.toggle()
            flag = "GIRO N "
        
        if BUTTON_EP.value() == 0:
            MOTORS.move( 0, 1 )
            LED2_BLUE.toggle()
            flag = "ELEVAÇÃO P "
        
        elif BUTTON_EM.value() == 0:
            MOTORS.move( 0,-1 )
            LED2_RED.toggle()
            flag = "ELEVAÇÃO N "
            
        if flag :
            baton.acquire()
            print( flag )
            baton.release() 

_thread.start_new_thread( motors_control, () ) 

while True:
    TIME = DS.now()
     
    #sys.stdout.write( struct.pack('b', 99 ) )
    #sys.stdout.write( struct.pack('B', struct.calcsize('ffBBBBBBbB') ) )
    #sys.stdout.write( struct.pack('ff', azimute, altitude ) )
    #sys.stdout.write( struct.pack('BBBBBB', TIME[0], TIME[1], TIME[2], TIME[3], TIME[4], TIME[5] ) )
    
    baton.acquire()
    print( TIME, azimute, altitude )
    baton.release() 
    
    while sys.stdin in select.select( [sys.stdin], [], [], 0 )[0]:        
        cmd = sys.stdin.read(1)
        if (cmd == 'h'): 
            get_time = struct.unpack( 'BBBBBB', sys.stdin.read(6) )
            DS.set_time( get_time[0], get_time[1], get_time[2], 1, get_time[3], get_time[4], get_time[5] )
            if debug:
                TIME = DS.now() 
                sys.stdout.write( 'Input = h : Correção da Hora' )
                sys.stdout.write( 'Nova data/hora = %i/%i/%i - %i:%i:%i ' %(TIME[0],TIME[1],TIME[2],TIME[3],TIME[4],TIME[5]) ) 
        
    azimute, altitude = compute( LOC, TIME )
    
    LED2_BLUE.value ( 1 if altitude > 0 else 0 )
    LED2_RED.value  ( 0 if altitude > 0 else 1 )
    
    # SALVAR A DATA NA EEPROM DO RASP
    # FAZER O PINO DE INTERRUPÇÃO CASO FALTE LUZ
    
    LED_BUILTIN.toggle() 
    sleep( 1 ) 
    # GARBAGE COLLECTOR 
    gc.collect()




