from StepMotors     import Motors, Lever_control
from DS3231         import DS3231
from time           import sleep
from machine        import Pin
from SunPosition    import *
from FileStatements import *

import _thread   as thread
import  select
import  struct 
import  sys
import  gc

# MACRODEFINIÇÕES 
AUTOMATIC_TRACKING = 1
AUTOMATIC_BACKWARD = 2
AUTOMATIC_SLEEPING = 3
MANUAL_CONTROLING  = 0 

# VARIÁVEIS USADAS NAS GPIOs DO RASPICO 
STEP_GIR    = 0 
STEP_ELE    = 1 
STEP_GEN    = 2

DIR_GIR     = 3
DIR_ELE     = 4
DIR_GEN     = 5 

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
MOTORS.configure( MOTORS.GIR, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
MOTORS.configure( MOTORS.ELE, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
MOTORS.set_torque( True )

# BOTÕES / ALAVANCAS PARA MOVER OS MOTORES
LEVERS = Lever_control( lever_pins_A = [BUTTON_GP,BUTTON_GM], lever_pins_B = [BUTTON_EP,BUTTON_EM], LED = [LED1_RED, LED1_BLUE]  )

# Função de mover chamada via lambda para reduzir tamanho da chamada 
def move( gir, ele, tem = 2):
    MOTORS.move( gir, ele, tem )

def move_home( ):
    pass


# LEDS E LED BUILTIN DA PLACA PICO 
LED2_RED    = Pin(LED2_RED , Pin.OUT)
LED2_BLUE   = Pin(LED2_BLUE, Pin.OUT)
LED_BUILTIN = Pin( LED_BUILTIN, Pin.OUT ) 


# PINOS DO DS3231 
DS = DS3231( 0, Pin( SDA_DS ), Pin( SCL_DS ), addrs = [0x68, 0x57] )
#DS.set_time( 21, 7, 26, 13, 55, 15  )


# FILE CONFIGURATIONS 
FILE_PATH = 'mem_pico.txt'
FILE_OP   = 'rw' 


# Garbage Collector Enable 
gc.enable()


# CONFIGURAÇÕES DE RASTREAMENTO 
LATITUDE  = -29.16530765942215
LONGITUDE = -54.89831672609559 
TIME      = DS.now()
LOC       = [ LATITUDE, LONGITUDE, 298.5, 101.0 ] 


L_AZIMUTE , L_ALTITUDE = [ float(s2f) for s2f in file_readlines( FILE_PATH, 'r' ) ]
A_AZIMUTE , A_ALTITUDE = compute( LOC, TIME )
D_AZIMUTE , D_ALTITUDE = L_AZIMUTE - A_AZIMUTE, L_ALTITUDE - A_ALTITUDE


def calibrate_pos():
    MOTORS.set_torque( False )
    input()
    MOTORS.set_torque( True )


S_rise, S_set = get_twilights( LOC, TIME )
S_tot = (S_set[3]*3600 + S_set[4]*60 + S_set[5]) - (S_rise[3]*3600 + S_rise[4]*60 + S_rise[5])
S_tot /= 60*5
M =  S_tot // 60
S = (S_tot  % 60) // 1
NEW_TIME = S_rise
def up_fake_time( up = False ):
    global NEW_TIME
    global S_tot
    global S
    global M
    
    if up :
        S_rise, S_set = get_twilights( LOC, TIME )
        S_tot = (S_set[3]*3600 + S_set[4]*60 + S_set[5]) - (S_rise[3]*3600 + S_rise[4]*60 + S_rise[5])
        S_tot /= 60*5
        M =  S_tot // 60
        S = (S_tot  % 60) // 1
        NEW_TIME = S_rise

    NEW_TIME[5] += S
    NEW_TIME[4] += M
    if NEW_TIME[5] >= 60:
        NEW_TIME[4] += 1
        NEW_TIME[5] %= 60
    if NEW_TIME[4] >= 60:
        NEW_TIME[3] += 1
        NEW_TIME[4] %= 60
    NEW_TIME = [ int(d) for d in NEW_TIME ]
    return NEW_TIME 
    
    
# CONFIGURAÇÕES DE LOCK PARA TRABALHO COM MULTIPLAS THREADS 
baton_mot = thread.allocate_lock()
baton_in  = thread.allocate_lock()


AUTOMATIC_WAKE_UP  = 10
AUTOMATIC_BACKWARD = 20
AUTOMATIC_TRACKING = 30
AUTOMATIC_SLEEPING = 40

STATE = AUTOMATIC_WAKE_UP

'''
print( "Modo inicial de calibração: Torque desligado, pode mexer nos motores...")
print( "Azi = ", L_AZIMUTE )
print( "Alt = ", L_ALTITUDE )
print( "\nPressione enter para continuar.")
#calibrate_pos()
'''

#thread.start_new_thread( motors_control, () ) 

while True:
    if STATE == AUTOMATIC_WAKE_UP:
        
        print( "BOM DIA!!!") 
        TIME = DS.now() 
        #TIME = up_fake_time( up = True )
        
        A_AZIMUTE , A_ALTITUDE = compute( LOC, TIME )
        if A_ALTITUDE < 0:
            STATE = AUTOMATIC_SLEEPING
                
        L_AZIMUTE , L_ALTITUDE = [ float(s2f) for s2f in file_readlines( FILE_PATH, 'r' ) ]
        if L_AZIMUTE >= 180:     L_AZIMUTE -= 360
        
        D_AZIMUTE, D_ALTITUDE  = (A_AZIMUTE-L_AZIMUTE), (A_ALTITUDE-L_ALTITUDE)
        L_AZIMUTE, L_ALTITUDE  =  A_AZIMUTE           ,  A_ALTITUDE
        
        file_write( FILE_PATH, "%3.10f\n%3.10f"%(L_AZIMUTE, L_ALTITUDE), 0, 'wo')
        
        '''
        print( "Movendo para: Azi( {} ) e Alt( {} )".format(D_AZIMUTE, D_ALTITUDE) )
        '''
        
        move( D_AZIMUTE , -D_ALTITUDE , 10 )
        
        STATE = AUTOMATIC_TRACKING
        continue 
    
    
    elif STATE == AUTOMATIC_TRACKING:
        A_AZIMUTE, A_ALTITUDE = compute( LOC, TIME )
        
        TIME = DS.now() 
        #TIME = up_fake_time( )
        
        D_AZIMUTE_HO = abs(A_AZIMUTE-L_AZIMUTE) 
        D_AZIMUTE_AH = abs((360-A_AZIMUTE)+L_AZIMUTE)
       
        D_AZIMUTE    = D_AZIMUTE_HO  if D_AZIMUTE_HO < D_AZIMUTE_AH   else D_AZIMUTE_AH 
        D_ALTITUDE   = (A_ALTITUDE-L_ALTITUDE)
        
        L_AZIMUTE, L_ALTITUDE =  A_AZIMUTE , A_ALTITUDE
        file_write( FILE_PATH, "%3.10f\n%3.10f"%(L_AZIMUTE, L_ALTITUDE), 0, 'wo')
        
        move( -D_AZIMUTE, -D_ALTITUDE, 10 ) 
        #move( 0, -2*D_ALTITUDE, 10 ) 
        
        if L_ALTITUDE > 0:
            LED2_BLUE.high()
            LED2_RED.low()            
        else:
            LED2_BLUE.low()
            LED2_RED.high()
            STATE = AUTOMATIC_BACKWARD 
    
    elif STATE == AUTOMATIC_BACKWARD:
        TIME[2] += 1
        #TIME = DS.now()
        
        TIME = up_fake_time( up = True )
        
        A_AZIMUTE, A_ALTITUDE = compute( LOC, TIME )

        '''
        print( L_AZIMUTE, A_AZIMUTE ) 
        print( L_ALTITUDE, A_ALTITUDE )
        '''
        
        D_AZIMUTE  = (360-L_AZIMUTE)+A_AZIMUTE
        D_ALTITUDE = (A_ALTITUDE-L_ALTITUDE)
        
        L_AZIMUTE, L_ALTITUDE =  A_AZIMUTE , A_ALTITUDE
        file_write( FILE_PATH, "%3.10f\n%3.10f"%(L_AZIMUTE, L_ALTITUDE), 0, 'wo')
        
        FIRST_NIBBLE_AZI = D_AZIMUTE //2
        FIRST_NIBBLE_ALT = D_ALTITUDE + 15
        
        SECOND_NIBBLE_AZI = D_AZIMUTE //2
        SECOND_NIBBLE_ALT = D_ALTITUDE - 15
        
        '''
        print( FIRST_NIBBLE_AZI, SECOND_NIBBLE_AZI )
        print( FIRST_NIBBLE_ALT, SECOND_NIBBLE_ALT )
        '''
        
        move( FIRST_NIBBLE_AZI , -FIRST_NIBBLE_ALT , 10 ) 
        move( SECOND_NIBBLE_AZI, 0, 10 ) 
        move( 0, -SECOND_NIBBLE_ALT, 10 ) 
        #move( 0, -2*D_ALTITUDE, 10 )
        
        STATE = AUTOMATIC_SLEEPING
        continue 
    
    
    
    elif STATE == AUTOMATIC_SLEEPING:
        _ , A_ALTITUDE = compute( LOC, TIME )
        if A_ALTITUDE > 0:
            STATE = AUTOMATIC_WAKE_UP
        sleep( 60 ) 
    
    
    # SALVAR A DATA NA EEPROM DO RASP
    # FAZER O PINO DE INTERRUPÇÃO CASO FALTE LUZ

    def send_bytes( AZIMUTE, ALTITUDE, TIME ) :
        INIT = struct.pack('BBBB', ord('I'),ord('N'),ord('I'),ord('T') ) 
        CALC = struct.pack('B', struct.calcsize('BffBBBBBBB') )
        DATA = struct.pack('ff', AZIMUTE, ALTITUDE )
        TIME = struct.pack('BBBBBB', TIME[0], TIME[1], TIME[2], TIME[3], TIME[4], TIME[5] )
        NEWL = struct.pack('B', 255 )
                
        #print( INIT, CALC, DATA, TIME )
        
        sys.stdout.write( INIT )
        sys.stdout.write( CALC )
        sys.stdout.write( DATA )
        sys.stdout.write( NEWL )
        sys.stdout.write( TIME )
        sys.stdout.write( NEWL )
        
    '''
    print( "\n" )
    print( "AZIMUTE (A\D):\t{:2.4f}\t\t{:2.4f}".format( A_AZIMUTE , D_AZIMUTE ) ) 
    print( "ALTITUDE (A\D):\t{:2.4f}\t\t{:2.4f}".format( A_ALTITUDE, D_ALTITUDE) )
    print( "Data:\t\t{}/{}/{}\t\tHora:\t\t{}:{}:{}".format(TIME[0],TIME[1],TIME[2],TIME[3],TIME[4],TIME[5]) )
    print( "Azimute:\t{:2.3f}\t\tAltitude:\t{:2.3f}".format(L_AZIMUTE, L_ALTITUDE), end='\n\n' )
    '''
    
    send_bytes( L_AZIMUTE, L_ALTITUDE, TIME ) 
    sleep(0.1)
    
    # GARBAGE COLLECTOR 
    gc.collect()
