import Tracker.Sun.mySunposition as sun 
import Tracker.Motor.myStepmotor as stp
import Tracker.Time.myDatetime   as dt
import Tracker.Sensor.myAS5600   as sn
import Tracker.Serial.myUART     as sr
import Tracker.Controle.myPID    as mp
from thread_main import * 
from pinout      import * 

from machine import Pin, SoftI2C, UART, Timer, I2C
from time    import sleep, ticks_ms
from struct  import pack, unpack


isc0   = I2C ( 0, freq = 100000, sda = Pin( SDA_DS  ), scl = Pin( SCL_DS  ) ) 
isc1   = I2C ( 1, freq = 100000, sda = Pin( SDA_AS  ), scl = Pin( SCL_AS  ) )

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


TIME, TIME_STATUS = Time.get_time()    
AZIMUTE, ALTITUDE = sun.compute( LOCALIZATION,  TIME )


PID_GIR = mp.PID( PV = AZIMUTE, Kp = 0.75, Kd = 0.275, Ki = 0.5 )
PID_ELE = mp.PID( PV = ALTITUDE, Kp = 0.75, Kd = 0.275, Ki = 0.5 )

PID_GIR.att( ASGIR.degAngle )
PID_ELE.att( ASELE.degAngle ) 


POWER = Pin( POWER, Pin.OUT )


tim = Timer() 
raise_timer = True
def print_func( timer_obj ):
    global AZIMUTE, ALTITUDE
    global Time, ASGIR, ASELE, PID_GIR
    global raise_timer
        
    print("\nDatetime:\t", TIME, TIME_STATUS )
    print("Azimute:\t", AZIMUTE )
    print("Altitude:\t", ALTITUDE )
    
    print("\nGiro:\t\t", ASGIR.degAngle )
    print("PV(GIR):\t", PID_GIR.PV )
    print("Error:\t\t", PID_GIR.Error_real )
    print("Kd Ki Kp:\t", PID_GIR.Kd, PID_GIR.Ki, PID_GIR.Kp )
    
    print("\nElevação:\t", ASELE.degAngle )
    print("PV(ELE):\t", PID_ELE.PV )
    print("Error:\t\t", PID_ELE.Error_real )
    print("Kd Ki Kp:\t", PID_ELE.Kd, PID_ELE.Ki, PID_ELE.Kp )
    
    raise_timer = True


while True:
    if raise_timer == 23:
       tim.init( period = 1000, mode = Timer.ONE_SHOT, callback = print_func )
       raise_timer = False
    
    TIME, TIME_STATUS = Time.get_time()
    AZIMUTE, ALTITUDE = sun.compute( LOCALIZATION,  TIME )

    # Medição da posição dos sensores
    measure_gir = ASGIR.degAngle
    measure_ele = ASELE.degAngle
    
    posG = PID_GIR.compute( measure_gir )*0.05
    posE = PID_ELE.compute( measure_ele )*0.05
    
    Motors.move( posE, posG )
    
    Uart.response( initg = measure_gir, inite = measure_ele)
    
    
    # VERIFICA SE RECEBEU ALGO DA SERIAL 
    BYTE_ID = Uart.recv_from()
    print( BYTE_ID ) 
    
    if BYTE_ID: 
        if BYTE_ID == b'H':
            pass
        if BYTE_ID == b'S':
            pass
        if BYTE_ID == b'C':
            M = Uart.read(1)
            if M == b'G':
                if   FC == b'D':  PID_GIR.Kd = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'I':  PID_GIR.Ki = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'P':  PID_GIR.Kp = (unpack( 'f', Uart.read(4) )[0])
            elif M == b'E':
                if   FC == b'D':  PID_ELE.Kd = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'I':  PID_ELE.Ki = (unpack( 'f', Uart.read(4) )[0])
                elif FC == b'P':  PID_ELE.Kp = (unpack( 'f', Uart.read(4) )[0])

        if BYTE_ID == b'W':
            FC = Uart.read(1)
            if   FC == b'O':  POWER.high() 
            elif FC == b'F':  POWER.low()  

        
    # O Looping esta no delay
    sleep( 0.025 ) 