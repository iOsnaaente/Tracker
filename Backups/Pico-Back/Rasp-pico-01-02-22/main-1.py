from   Tracker.Time.Timanager    import FAKE_TIME
import Tracker.Sun.mySunposition as sun 
import Tracker.Motor.myStepmotor as stp
import Tracker.Time.myDS3231     as ds
import Tracker.Sensor.myAS5600   as sn
import Tracker.Serial.myUART     as sr
import Tracker.Controle.myPID    as mp
import struct 

from machine import Pin  , SoftI2C , UART, Timer, I2C
from time    import sleep, ticks_ms
from struct  import pack , unpack
from pinout  import * 

Motors = stp.Motors( STEP_GIR, DIR_GIR, STEP_ELE, DIR_ELE, ENABLE_MTS, POWER )
Motors.configure( Motors.GIR, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
Motors.configure( Motors.ELE, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
Motors.set_torque( False )

isc0   = I2C ( 0, freq = 100000, sda = Pin( SDA_DS  ), scl = Pin( SCL_DS  ) ) 
isc1   = I2C ( 1, freq = 100000, sda = Pin( SDA_AS  ), scl = Pin( SCL_AS  ) )

print( isc0, isc0.scan(), '\n', isc1, isc1.scan() ) 

Time = ds.DS3231( isc0  )
#status = Time.set_time( 22, 1, 31, 10, 56, 50 )

try: 
    ASGIR  = sn.AS5600  ( isc0 )
    ASELE  = sn.AS5600  ( isc1 )
    ASELE.set_config() 
except:
    print( 'Breka AS5600')
    machine.soft_reset()


PID_GIR = mp.PID( PV = 100 , Kp = 0.5, Kd = 0.1, Ki = 0.5 )
PID_ELE = mp.PID( PV = 100, Kp = 0.5, Kd = 0.1, Ki = 0.5 )

PID_GIR.att( ASGIR.degAngle() )
PID_ELE.att( ASELE.degAngle() )
    
    
try:
    Uart   = sr.UART_SUP( 1, 115200, tx  = Pin(UART_TX) , rx  = Pin(UART_RX) )
    print( Uart.myUART )
except:
    print( 'Breka UART')
    machine.soft_reset()


MSG = ""
TIME, TIME_STATUS = Time.get_time() 
fake_time    = FAKE_TIME( LOCALIZATION, TIME )

STATE = AUTOMATIC

print_timmer  = Timer() 
raise_timmer  = True
wait_new_day  = False
send_datetime = False

def print_func( timmer_obj ):
    global raise_timmer
    global Uart 
    MSG = '{}\n'.format( Time.get_time()) 
    MSG += "Giro:\t\t{}\n".format( ASGIR.degAngle() ) 
    MSG += "PV(GIR):\t{}\n".format( PID_GIR.PV ) 
    MSG += "Error:\t\t{}\n".format( PID_GIR.Error_real )
    MSG += "Kd Ki Kp:\t{} {} {}\n".format( PID_GIR.Kd, PID_GIR.Ki, PID_GIR.Kp )
    MSG += "Elevação:\t{}\n".format( ASELE.degAngle() ) 
    MSG += "PV(ELE):\t{}\n".format( PID_ELE.PV )
    MSG += "Error:\t\t{}\n".format( PID_ELE.Error_real ) 
    MSG += "Kd Ki Kp:\t{} {} {}\n".format( PID_ELE.Kd, PID_ELE.Ki, PID_ELE.Kp )
    print( MSG, Time.get_raw_datetime() )
    Uart.response_msg( initH = Time.get_raw_datetime() )
    raise_timmer = True 
  
def move_new_day():
    diff = int(360-AZIMUTE)
    for ah in range( diff ):
        PID_GIR.set_PV( AZIMUTE + ah ) 
        measure_gir = ASGIR.degAngle()
        posG = PID_GIR.compute( measure_gir )
        Uart.response( initg = measure_gir, inite = ASELE.degAngle() )
        Motors.move( 0, posG*0.05 )
    for h in range( diff ):
        PID_GIR.set_PV( ah ) 
        measure_gir = ASGIR.degAngle()
        posG = PID_GIR.compute( measure_gir )
        Uart.response( initg = measure_gir, inite = ASELE.degAngle() )
        Motors.move( 0, posG*0.05 )
    
while True:
    if raise_timmer == True:
       print_timmer.init( period = 1000, mode = Timer.ONE_SHOT, callback = print_func )
       raise_timmer = False

    if STATE == AUTOMATIC: 
        
        TIME, TIME_STATUS = Time.get_time()
        AZIMUTE, ALTITUDE = sun.compute( LOCALIZATION,  TIME )        
        if ALTITUDE < 0:
            if wait_new_day == False: 
                move_new_day()
            wait_new_day = True 
            continue
        else:
            wait_new_day = False
        
        PID_GIR.set_PV( AZIMUTE  ) 
        PID_ELE.set_PV( ALTITUDE )        
        measure_gir = ASGIR.degAngle()
        measure_ele = ASELE.degAngle()
        posG = PID_GIR.compute( measure_gir )
        posE = PID_ELE.compute( measure_ele )
        Uart.response( initg = measure_gir, inite = measure_ele )
        Motors.move( posE*0.05, posG*0.05 )
        
        

    elif STATE == REMOTE:
        measure_gir = ASGIR.degAngle()
        measure_ele = ASELE.degAngle()
        posG = PID_GIR.compute( measure_gir )
        posE = PID_ELE.compute( measure_ele )
        Uart.response( initg = measure_gir, inite = measure_ele)
        Motors.move( posE*0.05, posG*0.05 )
    
    
    elif STATE == IDLE:
        pass
    
    
    elif STATE == MANUAL:
        pass
    
    
    elif STATE == DEMO:
        TIME = fake_time.compute( )
        AZIMUTE, ALTITUDE = sun.compute( LOCALIZATION,  TIME )
        if ALTITUDE < 0:
            fake_time.compute_new_day()
            move_new_day() 
    
        PID_GIR.set_PV( AZIMUTE  ) 
        PID_ELE.set_PV( ALTITUDE )
        measure_gir = ASGIR.degAngle()
        measure_ele = ASELE.degAngle()
        posG = PID_GIR.compute( measure_gir )
        posE = PID_ELE.compute( measure_ele )
        Uart.response( initg = measure_gir, inite = measure_ele)
        Motors.move( posE*0.05, posG*0.05 )
        
            
    # VERIFICA SE RECEBEU ALGO DA SERIAL 
    BYTE_ID = Uart.recv_from()
    
    if BYTE_ID:
        try:
            if BYTE_ID == b'W':
                FC = Uart.read(1)
                if   FC == b'O':  Motors.set_torque( True )
                elif FC == b'F':  Motors.set_torque( False )

            elif BYTE_ID == b'H':
                LEN = Uart.read(1)
                print( BYTE_ID, LEN ) 
                if LEN == chr(6).encode():
                    y, m, d, hh, mm, ss  = unpack( 'bbbbbb', Uart.read(6) )
                    if y < 50 and  m <= 12 and d <= 31:
                        if hh < 24 and mm < 60 and ss < 60:
                            Time.set_time( y, m, d, hh, mm, ss )
            
            elif BYTE_ID == b'S':
                FC = Uart.read(1)
                if FC == b'S': STATE = IDLE 
                if FC == b'C': STATE = AUTOMATIC
                if FC == b'D':
                    fake_time.compute_new_day() 
                    STATE = DEMO 
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
                MSG  = b'F' # 70 Bytes 
                MSG += struct.pack( 'f', ASGIR.degAngle() )
                MSG += struct.pack( 'f', PID_GIR.PV )
                MSG += struct.pack( 'f', PID_GIR.Error_real ) 
                MSG += ASGIR._read( 0, 11 )
                MSG += struct.pack( 'fff', PID_GIR.Kd, PID_GIR.Ki, PID_GIR.Kp )

                MSG += struct.pack( 'f', ASELE.degAngle() )
                MSG += struct.pack( 'f', PID_ELE.PV )
                MSG += struct.pack( 'f', PID_ELE.Error_real )
                MSG += ASELE._read( 0, 11 )
                MSG += struct.pack( 'fff', PID_ELE.Kd, PID_ELE.Ki, PID_ELE.Kp )
                MSG += '\\\\'.encode()
                
                print( MSG ) 
                Uart.response_msg( initD = MSG )
        except:
            print( 'Erro de struct.unpack() : BUFFER PROTOCOL REQUIRED' ) 
        
    # O Looping esta no delay
    sleep( 0.025 ) 



