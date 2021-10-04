from Levers         import Lever_control
from Timanager      import Timemanager 
from StepMotors     import Motors
from DS3231         import DS3231
from SunPosition    import *
from FileStatements import *
from Const          import * 

from time           import sleep
from machine        import Pin

import  select
import  struct 
import  sys
import  gc

# INSTANCIAMENTO DOS PERIFÉRICOS 
MOTORS = Motors( STEP_GIR, DIR_GIR, STEP_ELE, DIR_ELE, ENABLE_MTS )
MOTORS.configure( MOTORS.GIR, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
MOTORS.configure( MOTORS.ELE, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
MOTORS.set_torque( True )

# BOTÕES / ALAVANCAS PARA MOVER OS MOTORES
LEVERS = Lever_control( lever_pins_A = [BUTTON_GP,BUTTON_GM], lever_pins_B = [BUTTON_EP,BUTTON_EM], LED = [LED1_RED, LED1_BLUE]  )
   
# LEDS E LED BUILTIN DA PLACA PICO 
LED2_RED    = Pin(LED2_RED , Pin.OUT)
LED2_BLUE   = Pin(LED2_BLUE, Pin.OUT)
LED_BUILTIN = Pin( LED_BUILTIN, Pin.OUT ) 

# SERIAL CONFIGURAÇÕES 
BYTE_INIT   = b'INIT'  
unpacked = lambda n_bytes, byte_type = 'B' : struct.unpack( byte_type, sys.stdin.buffer.read( n_bytes ))[0]

# PINOS DO DS3231 
DS = DS3231( 0, Pin( SDA_DS ), Pin( SCL_DS ), addrs = [0x68, 0x57] )

# CONTROLE DOS ANGULOS DO SOL 
timanager = Timemanager( DS, MOTORS )

# Garbage Collector Enable 
gc.enable()

# SETAR A HORA DO DS3231 
#DS.set_time( 21, 10, 4, 16, 29, 20  )

# ESTADO DE INICIALIZAÇÃO
STATE = AUTOMATIC_WAKE_UP

while True:
    # INICIALIZAÇÃO
    if STATE == AUTOMATIC_WAKE_UP:
        print( "BOM DIA!!!") 
        #TIME = timanager.up_fake_time( up = True )
        TIME = DS.now() 
        timanager.start( TIME )
        STATE = AUTOMATIC_TRACKING

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
        

    # VERIFICA SE RECEBEU ALGO DA SERIAL 
    while sys.stdin in select.select( [sys.stdin], [sys.stdout], [sys.stderr], 0 )[0]:  
        cmd = sys.stdin.read(1)        
        if cmd == BYTE_INIT[count]:  count += 1
        else:                        count  = 0
 
        if count == 4:
            count = 0
            BYTE_ID  = unpacked(1)
            if   BYTE_ID == b'H':
                print('Recebido: {}'.format(BYTE_ID))
            elif BYTE_ID == 'M':
                print('Recebido: {}'.format(BYTE_ID))
            


    # FAZER O PINO DE INTERRUPÇÃO CASO FALTE LUZ

    #sys.stdout.write( struct.pack('b', 99 ) )
    #sys.stdout.write( struct.pack('B', struct.calcsize('ffBBBBBBbB') ) )
    #sys.stdout.write( struct.pack('ff', AZIMUTE, ALTITUDE ) )
    #sys.stdout.write( struct.pack('BBBBBB', TIME[0], TIME[1], TIME[2], TIME[3], TIME[4], TIME[5] ) )
    
    #timanager.print()
    
    # GARBAGE COLLECTOR 
    gc.collect()
    sleep( 0.1 )
