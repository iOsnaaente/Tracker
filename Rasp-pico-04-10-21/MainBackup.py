#!/usr/bin/env python
# -*- coding: utf-8 -*-

from machine        import Pin, I2C

from Levers         import Lever_control
from Timanager      import Timemanager 
from StepMotors     import Motors
from DS3231         import DS3231
from Acell          import *
from SunPosition    import *
from FileStatements import *
from Const          import * 

import select 
import struct 
import time 
import sys
import gc

# INSTANCIAMENTO DOS PERIFÉRICOS 
MOTORS = Motors( STEP_GIR, DIR_GIR, STEP_ELE, DIR_ELE, ENABLE_MTS )
MOTORS.configure( MOTORS.GIR, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
MOTORS.configure( MOTORS.ELE, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
MOTORS.set_torque( True )

# Ativa os motores 
POWER_MOTORS_STATE = HIGH  
POWER_MOTORS = Pin( POWER, Pin.OUT )  
POWER_MOTORS.value( POWER_MOTORS_STATE ) 

LED_POWER = Pin(LED1_RED , Pin.OUT)

def turn_off_motors():
    POWER_MOTORS_STATE = LOW
    POWER_MOTORS.low( )
    LED_POWER.low( ) 
    
def turn_on_motors():
    POWER_MOTORS_STATE = HIGH
    POWER_MOTORS.high( )
    LED_POWER.high( ) 
    

# BOTÕES / ALAVANCAS PARA MOVER OS MOTORES
LEVERS = Lever_control( lever_pins_A = [BUTTON_GP,BUTTON_GM], lever_pins_B = [BUTTON_EP,BUTTON_EM], LED = [LED1_RED, LED1_BLUE]  )


# LEDS E LED BUILTIN DA PLACA PICO 
LED2_RED    = Pin(LED2_RED , Pin.OUT)
LED2_BLUE   = Pin(LED2_BLUE, Pin.OUT)
LED_BUILTIN = Pin( LED_BUILTIN, Pin.OUT ) 


# SERIAL CONFIGURAÇÕES 
BYTE_INIT = [b'I',b'N',b'I',b'T']  
count     = 0

# PINOS DO DS3231 
DS  = DS3231( 0, Pin( SDA_DS ), Pin( SCL_DS ), addrs = [0x68, 0x57] )

try:
    #MAG = QMC5883L( i2c_bus = I2C(1, Pin(18,Pin.OUT), Pin(19, Pin.OUT)), address=DFLT_ADDRESS, output_data_rate=ODR_200HZ, output_range=RNG_8G, oversampling_rate=OSR_512 ) 
    mag = I2C(1, sda=Pin(18,Pin.OUT), scl=Pin(19, Pin.OUT), freq = 100_000)
    print( mag, mag.scan() )
    a = mag.readfrom_mem( 13, 0x00, 2 )
    print( a ) 
    MAG = QMC5883L( mag ) 
except: 
    print("MAG not connected")

# CONTROLE DOS ANGULOS DO SOL 
timanager = Timemanager( DS, MOTORS )

# Garbage Collector Enable 
gc.enable()


# SETAR A HORA DO DS3231 
#DS.set_time( 21, 10, 21, 16, 47, 20  )


# ESTADO DE INICIALIZAÇÃO
STATE = WAKE_UP

autoEngine = True 
time_delay = 1 
count_mov  = 0 
last_time  = time.time() 

LIMIT = 50 
DATA_TRAIN = [] 

while True:
    # INICIALIZAÇÃO
    if STATE == WAKE_UP:
        print( "BOM DIA!!!") 
        
        #TIME = timanager.up_fake_time( up = True )
        TIME = DS.now() 
        
        timanager.start( TIME )
        
        STATE = AUTOMATIC_TRACKING
        
        if autoEngine: 
            turn_on_motors() 
        else:
            turn_off_motors()

    elif STATE == GET_DATA:
        LED_BUILTIN.toggle()
        levers_state = LEVERS.check_levers()
        if any(levers_state):
            if   levers_state[0]: timanager.move(  1,  0 )
            elif levers_state[1]: timanager.move( -1,  0 )
            if   levers_state[2]: timanager.move(  0,  1 )
            elif levers_state[3]: timanager.move(  0, -1 ) 
            count_mov += 1
            
            try:
                x,y,z = MAG.get_magnet_raw()
            except:
                print( 'Error. magnetico fora ')
                x,y,z = 0,0,0
                
            DATA = struct.pack('ffffff',count_mov,timanager.MOTORS.GIR_POS, timanager.MOTORS.ELE_POS, x, y, z) 
            DATA_TRAIN.append( DATA )
            
            if count_mov > 0:       
                with open('reg.txt', 'a') as f : 
                    f.write( b'{},\n'.format(DATA_TRAIN) )
                DATA_TRAIN = [] 


    # RASTREADOR 
    elif STATE == AUTOMATIC_TRACKING:
        #TIME = timanager.up_fake_time( )
        TIME = DS.now() 
        timanager.update( TIME )
        
        if timanager.get_altitude() > 0:
            LED2_BLUE.high()
            LED2_RED.low()            
        else:
            LED2_BLUE.low()
            LED2_RED.high()
            STATE = AUTOMATIC_BACKWARD 
    

    # RETORNO PARA O PONTO INICIAL DO DIA SEGUINTE 
    elif STATE == AUTOMATIC_BACKWARD:
        TIME[2] += 1
        if TIME[1] == 2: 
            if ANB(TIME[0]) :  DOM[1] = 29 
            else:              DOM[1] = 28 
        if TIME[2] > DOM[TIME[1]]:
            TIME[1] += 1
            TIME[2] = 1 
            if TIME[1] > 12: 
                TIME[0] += 1
                TIME[1] = 1 
            
        timanager.update( TIME )

        STATE = AUTOMATIC_SLEEPING
        continue 
    

    # ESPERA O NOVO DIA NASCER 
    elif STATE == AUTOMATIC_SLEEPING:
        TIME = DS.now() 
        if timanager.check_alt( TIME ):
            STATE = AUTOMATIC_TRACKING

    # INICIA O MODO DE OPEÇÃO ACELERADO ( DEMONSTRAÇÃO )
    elif STATE == MANUAL_DEMO:
        TIME = timanager.up_fake_time( up = True )
        timanager.update( TIME )
        timanager.print() 
    
    
    # CONTROLE MANUAL ATRAVÉS DOS LEVERS
    elif STATE == MANUAL_CONTROLING:
        levers_state = LEVERS.check_levers()
        if any(levers_state):
            if   levers_state[0]: timanager.move(  1,  0 )
            elif levers_state[1]: timanager.move( -1,  0 )
            if   levers_state[2]: timanager.move(  0,  1 )
            elif levers_state[3]: timanager.move(  0, -1 ) 
    

    # PARA O TRACKER
    elif STATE == MANUAL_STOPING:
        pass


    # VERIFICA SE RECEBEU ALGO DA SERIAL 
    while sys.stdin in select.select( [sys.stdin], [sys.stdout], [sys.stderr], 0 )[0]:  
        cmd = sys.stdin.buffer.read(1)
        if cmd == BYTE_INIT[count]:  count += 1
        else:                        count  = 0
 
        if count == 4:
            count = 0
            BYTE_ID  = sys.stdin.buffer.read(1)
            LED_BUILTIN.toggle()
            

            '''
            H -> Troca a hora
            M -> Move ambos motores
            m -> Move um dos motores
            S -> Para o tracker ( muda o estado )
            D -> Entra no modo Demo ( Demontração )
            C -> Para continuar o processo ( muda o estado ) 
            R -> Retorna para o inicio do dia
            O -> Muda para ativado os motores
            F -> Muda para desativado os motores 
            G -> Get data to conv net
            A -> Acelerometro medidas 
            '''
            
            
            if   BYTE_ID == b'H':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Recebido: {} para trocar a hora'.format(BYTE_ID))
                    year, month , day    = sys.stdin.buffer.read(3)
                    hour, minute, second = sys.stdin.buffer.read(3)
                    DS.set_time( year, month, day, hour, minute, second )
            
            
            elif BYTE_ID == b'M':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Recebido: {} para mover os dois motores'.format(BYTE_ID))
                    posG = struct.unpack( 'f', sys.stdin.buffer.read(4) )
                    posE = struct.unpack( 'f', sys.stdin.buffer.read(4) )
                    print(posG, posE, type(posG), type(posE))
                    timanager.move_to( POS = [ posG, posE ] )
                
                
            elif BYTE_ID == b'm':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Recebido: {} para mover somente um motor'.format(BYTE_ID))
                    motor_id = sys.stdin.buffer.read(1)
                    if motor_id == b'E':
                        posE = struct.unpack( 'f', sys.stdin.buffer.read(4) )
                        posG = [ float(s2f) for s2f in file_readlines( FILE_PATH, FILE_READ ) ][0]
                        timanager.move_to( POS = [ posG, posE ] )
                        print('POS E:', posE,' POS G:', posG, ' TYPE E:', type(posE),' TYPE G:',type(posG))

                    if motor_id == b'G':
                        posG = struct.unpack( 'f', sys.stdin.buffer.read(4) )
                        posE = [ float(s2f) for s2f in file_readlines( FILE_PATH, FILE_READ ) ][1]
                        timanager.move_to( POS = [ posG, posE ] )
                        print('POS E:', posE,' POS G:', posG, ' TYPE E:', type(posE),' TYPE G:',type(posG))
            
            
            elif BYTE_ID == b'S':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Recebido: {} para parar o processo'.format( BYTE_ID))
                    STATE = MANUAL_STOPING
            

            elif BYTE_ID == b'D':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Recebido: {} para iniciar o modo de demonstração do processo'.format( BYTE_ID))
                    STATE = MANUAL_DEMO
                    TIME = DS.now() 
                    timanager.update(TIME)
                    time_delay = 1 
            
            
            elif BYTE_ID == b'C':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Recebido: {} para continuar o processo'.format( BYTE_ID))
                    STATE = AUTOMATIC_TRACKING
                    timanager.update(TIME)
                    time_delay = 1 
                
                
            elif BYTE_ID == b'R':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Recebido: {} para retornar ao inicio do dia'.format( BYTE_ID))
                    TIME = DS.now()
                    TIME[3:6] = [0,0,0]
                    timanager.update(TIME)
            
            
            elif BYTE_ID == b'W':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Hello Tracker!!'.encode() )
            
            
            elif BYTE_ID == b'P':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    timanager.print()
            
            elif BYTE_ID == b'O':
                confirm = sys.stdin.buffer.read(1)
                if confirm ==  b'O':
                    sys.stdout.write("Turn on the power motors".encode())
                    turn_on_motors()
            
            elif BYTE_ID == b'F':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    sys.stdout.write("Turn off the power motors".encode())
                    turn_off_motors()
            
            elif BYTE_ID == b'G':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    print('Aquisição de dados')
                    STATE = GET_DATA 
                    time_delay = 0.001
                    last_time = time.time()
                    count_mov = 0
            
            elif BYTE_ID == b'A':
                confirm = sys.stdin.buffer.read(1)
                if confirm == b'O':
                    try: 
                        print( MAG.get_magnet_raw() )
                    except:
                        try:
                            print( 'Magnetic sensor error: {}'.format(MAG.scan() ) )  
                        except:
                            print("Magnetic sensor not conected")
    #timanager.print()
    time.sleep(time_delay)
    
    # GARBAGE COLLECTOR 
    #gc.collect()






