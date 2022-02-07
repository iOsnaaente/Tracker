import Tracker.Sun.mySunposition as sun 
import Tracker.Motor.myStepmotor as stp
import Tracker.Time.myDatetime   as dt
import Tracker.Sensor.myAS5600   as sn
import Tracker.Serial.myUART     as sr
import Tracker.Controle.myPID    as mp
from thread_main import * 
from pinout      import * 

from Timanager import FAKE_TIME

from machine import Pin, SoftI2C, UART, Timer, I2C
from time    import sleep, ticks_ms
from struct  import pack, unpack


isc0   = I2C ( 0, freq = 100000, sda = Pin( SDA_DS  ), scl = Pin( SCL_DS  ) ) 
isc1   = I2C ( 1, freq = 100000, sda = Pin( SDA_AS  ), scl = Pin( SCL_AS  ) )

if (54 not in isc0.scan()) or (104 not in isc0.scan()) or (54 not in isc1.scan()):
    print( isc0, isc0.scan() ) 
    print( isc1, isc1.scan() ) 


ASGIR  = sn.AS5600  ( isc0 )
ASELE  = sn.AS5600  ( isc1 )
    
Uart   = sr.UART_SUP( 1, 115200, tx  = Pin(UART_TX) , rx  = Pin(UART_RX) )
Time   = dt.Datetime( isc0, RTC_AUTO = True )


print( isc0, isc0.scan() ) 
print( isc1, isc1.scan() )
print( Uart.myUART )


Motors = stp.Motors( STEP_GIR, DIR_GIR, STEP_ELE, DIR_ELE, ENABLE_MTS, POWER )
Motors.configure( Motors.GIR, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
Motors.configure( Motors.ELE, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
Motors.set_torque( True )


STATE = AUTOMATIC

TIME, TIME_STATUS = Time.get_time()    
AZIMUTE, ALTITUDE = sun.compute( LOCALIZATION,  TIME )

PID_GIR = mp.PID( PV = AZIMUTE, Kp = 0.75, Kd = 0.1, Ki = 0.5 )
PID_ELE = mp.PID( PV = ALTITUDE, Kp = 0.75, Kd = 0.1, Ki = 0.5 )

PID_GIR.att( ASGIR.degAngle )
PID_ELE.att( ASELE.degAngle ) 


POWER = Pin( POWER, Pin.OUT )
POWER(0) 
 


MSG = ''

tim = Timer() 
raise_timer = True

fake_time = FAKE_TIME( LOCALIZATION, TIME )

def print_func( timer_obj ):
    global AZIMUTE, ALTITUDE, STATE, MSG 
    global Time, ASGIR, ASELE, PID_GIR, PID_ELE
    global raise_timer
    
    MSG = ''
    
    if STATE == AUTOMATIC: 
        MSG += 'AUTOMATIC STATE\n' 
    elif STATE == MANUAL:
        MSG +='LEVERS STATE\n'
    elif STATE == REMOTE:
        MSG += 'REMOTE STATE\n'
    
    MSG += "Datetime:\t{} {}\n".format( TIME, TIME_STATUS ) 
    MSG += "Azimute:\t{}\n".format( AZIMUTE ) 
    MSG += "Altitude:\t{}\n".format( ALTITUDE ) 
    MSG += "Giro:\t\t{}\n".format( ASGIR.degAngle ) 
    MSG += "PV(GIR):\t{}\n".format( PID_GIR.PV ) 
    MSG += "Error:\t\t{}\n".format( PID_GIR.Error_real )
    MSG += "Kd Ki Kp:\t{} {} {}\n".format( PID_GIR.Kd, PID_GIR.Ki, PID_GIR.Kp )
    MSG += "Elevação:\t{}\n".format( ASELE.degAngle ) 
    MSG += "PV(ELE):\t{}\n".format( PID_ELE.PV )
    MSG += "Error:\t\t{}\n".format( PID_ELE.Error_real ) 
    MSG += "Kd Ki Kp:\t{} {} {}\n".format( PID_ELE.Kd, PID_ELE.Ki, PID_ELE.Kp )
    
    print( MSG ) 
    raise_timer = True



while True:
    if raise_timer == True:
       tim.init( period = 1000, mode = Timer.ONE_SHOT, callback = print_func )
       raise_timer = False
    

    if STATE == AUTOMATIC: 
        TIME, TIME_STATUS = Time.get_time()
        AZIMUTE, ALTITUDE = sun.compute( LOCALIZATION,  TIME )        
        PID_GIR.set_PV( AZIMUTE  ) 
        PID_ELE.set_PV( ALTITUDE )
        measure_gir = ASGIR.degAngle
        measure_ele = ASELE.degAngle
        posG = PID_GIR.compute( measure_gir )
        posE = PID_ELE.compute( measure_ele )
        Uart.response( initg = measure_gir, inite = measure_ele)
        Motors.move( posE*0.05, posG*0.05 )
    
    elif STATE == REMOTE:
        measure_gir = ASGIR.degAngle
        measure_ele = ASELE.degAngle
        posG = PID_GIR.compute( measure_gir )
        posE = PID_ELE.compute( measure_ele )
        Uart.response( initg = measure_gir, inite = measure_ele)
        Motors.move( posE*0.05, posG*0.05 )
    
    elif STATE == IDLE:
        pass
    
    elif STATE == MANUAL:
        pass
    
    elif STATE == DEMO:
        TIME, NEW_DAY = fake_time.compute( )
        
        if NEW_DAY :
            print( "girar_maior_caminho()" ) 
            
        AZIMUTE, ALTITUDE = sun.compute( LOCALIZATION,  TIME )        
        ###### MUDEI A ORDEM PARA TESTE 
        PID_ELE.set_PV( AZIMUTE  ) 
        PID_GIR.set_PV( abs(ALTITUDE) )
        measure_gir = ASGIR.degAngle
        measure_ele = ASELE.degAngle
        posG = PID_GIR.compute( measure_gir )
        posE = PID_ELE.compute( measure_ele )
        Uart.response( initg = measure_gir, inite = measure_ele)
        Motors.move( posE*0.05, posG*0.05 )
        
    
    # VERIFICA SE RECEBEU ALGO DA SERIAL 
    BYTE_ID = Uart.recv_from()
    
    if BYTE_ID:
        if BYTE_ID == b'W':
            FC = Uart.read(1)
            if   FC == b'O':  POWER.high() 
            elif FC == b'F':  POWER.low()  

        elif BYTE_ID == b'H':
            pass
        
        elif BYTE_ID == b'S':
            FC = Uart.read(1)
            if FC == b'S': STATE = IDLE 
            if FC == b'C': STATE = AUTOMATIC
            if FC == b'D': STATE = DEMO 
            if FC == b'R': machine.soft_reset() 
            if FC == b'L': STATE = MANUAL 
        
        elif BYTE_ID == b'C':
            FC = Uart.read(1)
            if FC == b'M':
                PID_GIR.set_PV( unpack( 'f', Uart.read(4) )[0] )
                PID_ELE.set_PV( unpack( 'f', Uart.read(4) )[0] )
                STATE = REMOTE 
            
            elif FC == b'G':
                FC = Uart.read(1)
                if   FC == b'D':  PID_GIR.Kd = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'I':  PID_GIR.Ki = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'P':  PID_GIR.Kp = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'M':
                    PID_GIR.set_PV( unpack( 'f', Uart.read(4) )[0] )
                    STATE = REMOTE
                    
            elif FC == b'E':
                FC = Uart.read(1)
                if   FC == b'D':  PID_ELE.Kd = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'I':  PID_ELE.Ki = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'P':  PID_ELE.Kp = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'M':
                    PID_ELE.set_PV( unpack( 'f', Uart.read(4) )[0] )
                    STATE = REMOTE 
            
        elif BYTE_ID == b'P':
            Uart.response_msg( DIAGNOSIS = MSG )
            print( "Enviou {}".format(MSG[:20])) 

        
    # O Looping esta no delay
    sleep( 0.025 ) 
