# importações de repositórios locais
from   Tracker.Time.Timanager       import FAKE_TIME

import Tracker.Files.fileStatements as fs 
import Tracker.Sun.mySunposition    as sun 
import Tracker.Motor.myStepmotor    as stp
import Tracker.Time.myDS3231        as ds
import Tracker.Sensor.myAS5600      as sn
import Tracker.Serial.myUART        as sr
import Tracker.Serial.myRegisters   as rg
import Tracker.Serial.myModbus      as mmb
import Tracker.Controle.myPID       as mp
import Tracker.Manual.myLevers      as ml

from constants import * 
from pinout    import *


# importação de repositórios padrões do sistema PICO 
import machine 
import struct 
import time 


# Flags e variáveis globais
led_print     = machine.Pin( LED2_BLUE, machine.Pin.OUT)
STATE         = AUTOMATIC 
MSG           = ""
raise_timmer  = True
wait_new_day  = False
send_datetime = False
print_timmer  = machine.Timer() 


# Inicio da criação do objeto motores. Responsável pelo controle 
# de posição dos motores e controle automático quando os sensores
# falharem, por isso, as configurações de STEP, uSTEP e Ratio devem
# ser configuradas de acordo para evitar problemas de FAIL STATE 
Motors = stp.Motors( STEP_GIR, DIR_GIR, STEP_ELE, DIR_ELE, ENABLE_MTS, POWER )
Motors.configure( Motors.GIR, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
Motors.configure( Motors.ELE, pos = 0.0, step = 1.8, micro_step = 8, ratio = 1 )
Motors.set_torque( False )


# Criação dos barramentos i2c usados para os sensores AS5600 e DS3231 
isc0   = machine.I2C ( 0, freq = 100000, sda = machine.Pin( SDA_DS  ), scl = machine.Pin( SCL_DS  ) ) 
isc1   = machine.I2C ( 1, freq = 100000, sda = machine.Pin( SDA_AS  ), scl = machine.Pin( SCL_AS  ) )
print( isc0, isc0.scan(), '\n', isc1, isc1.scan() ) 


# Criação do objeto TIME que esta atrelado ao relógio RTC
# Responsável pela administração do tempo e temporizadores 
# de alarmes para Wake-up 
try: 
    Time = ds.DS3231( isc0  )
    TIME, TIME_STATUS = Time.get_time() 
    fake_time         = FAKE_TIME( LOCALIZATION, TIME )
    levers            = ml.Lever_control( [BUTTON_GP, BUTTON_GM], [BUTTON_EP, BUTTON_EM], [LED1_RED, LED1_BLUE] )

# Se o DS3231 não estiver de acordo, não tem como o Tracker
# entrar em operação e será obrigado a resetar 
except: 
    machine.soft_reset() 


# Tenta instanciar os sensores de posição DS5600 
# Caso os sensores estejam vivos, seta-se as configurações de 
# incialização ( escrita de 0 nos endereços [0:11] ) 
try: 
    ASGIR  = sn.AS5600  ( isc0 )
    ASELE  = sn.AS5600  ( isc1 )
    ASELE.set_config() 
    STATE = AUTOMATIC 

# Caso os sensores não estejam funcionando, deve-se colocar 
# o Tracker em modo FAIL-STATE 
except:
    print( 'Erro na inicialização do AS5600')
    STATE = FAIL_STATE 


# Tenta inicializar a comunicação via UART
# Geralmente essa parte não causa falhas, porém
# Se o UART não incializar ( Cabos desconectados )
# é interessante o sistema saber para não tentar enviar
# Frames via Serial, evitando erros inesperados.
MODBUS = True

if not MODBUS: 
    print( 'Utilizando modo de comunicação UART:  ')
    Uart   = sr.UART_SUP( 1, 115200, tx  = machine.Pin(UART_TX) , rx  = machine.Pin(UART_RX, machine.Pin.IN) )
    print( Uart.myUART, end = '\n\n' )

else:    
    print( 'Utilizando modo de comunicação Modbus:  ')
    Uart = mmb.myModbusCommunication( 1, 19200, 0x12, tx  = machine.Pin(UART_TX) , rx  = machine.Pin(UART_RX), parity = 'even' )
    
    Uart.set_registers( DISCRETES, COILS, INPUTS, HOLDINGS )
    
    status = Uart.HOLDINGS.set_regs( 0, [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    if status is not False:    print( 'Setado os registradores')
    else:                      print( 'Erro ao setar os registradores')
      

# Cada motor possui um PID para correção da posição
# Instanciamento dos PIDs de cada motor
PID_GIR = mp.PID( PV = 100, Kp = 0.75, Kd = 0.51, Ki = 0.5 )
PID_ELE = mp.PID( PV = 100, Kp = 0.75, Kd = 0.51, Ki = 0.5 )

# Atualizaão do angulo para calculo de correção. Há diferenças 
# entre a atualização e computação dos angulos de correção
PID_GIR.att( ASGIR.degAngle() )
PID_ELE.att( ASELE.degAngle() )
   
# QUANDO FOR ESCRITO EM ALGUMA VARIÁVEL DO REGISTRADOR
# SERA NECESSÁRIO SETAR ESSES VALORES NOS REGISTRADORES 
def set_regs():
    global PID_GIR, PID_ELE
    global Uart 
    Uart.HOLDINGS.set_regs( 0, [PID_GIR.PV, PID_GIR.Kp, PID_GIR.Ki, PID_GIR.Kd, PID_ELE.PV, PID_ELE.Kp, PID_ELE.Ki, PID_ELE.Kd, STATE ] )
    global TIME
    Uart.INPUTS.set_regs( 0, TIME[:-1])
    
# AO CONTRARIO, TODA VEZ QUE FOR PRECISO USAR OS VALORES
# DE REGISTRADORES, DEVE-SE PEGAR ESSES VALORES  
def get_regs():
    pass 



def print_func( timmer_obj ):
    global raise_timmer
    global Uart
    global led_print
    led_print(1)
    
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
    Uart.serial_write_data( initH = Time.get_raw_datetime() )
    raise_timmer = True
    
    led_print(0)
  
# Quando um novo dia é detectado ou pela troca de dias no TIME[2] ou pela 
# detecção da Altitude < 0º no quadrante OESTE. Dessa forma o Tracker deve 
# voltar para a posição de Sunrise do novo dia no quadrante LESTE 
def move_new_day():
    # Como o zero (0º) é definido sobre o Norte, para retornar de Leste -> Oeste 
    # O tracker deve percorrer um caminho antihoário L -> N (270º -> 0º ) e um 
    # caminho horário N -> O ( 0º -> 90º ). Por isso são necessárias duas etapas
    # para se fazer a correção da posição de forma correta 
    diff = int(360-AZIMUTE)

    #Gira no sentido antihorário para voltar meio dia 
    for ah in range( diff ):
        PID_GIR.set_PV( AZIMUTE + ah ) 
        measure_gir = ASGIR.degAngle()
        posG = PID_GIR.compute( measure_gir )
        Uart.response( initg = measure_gir, inite = ASELE.degAngle() )
        Motors.move( 0, posG*0.05 )
    
    # Gira no sentido horário para continar voltando mais meio dia 
    for h in range( diff ):
        PID_GIR.set_PV( ah ) 
        measure_gir = ASGIR.degAngle()
        posG = PID_GIR.compute( measure_gir )
        Uart.response( initg = measure_gir, inite = ASELE.degAngle() )
        Motors.move( 0, posG*0.05 )


def save_statements():
    bus0  = '{}{}\n'.format( isc0, isc0.scan() )
    bus1  = '{}{}\n'.format( isc1, isc1.scan() )
    uart  = '{}'.format( Uart.myUART ) 
    date  = 'DATE_TIME = {}'.format( Time.get_time() )
    state = 'STATE = {}'.format(STATE)
    MSG = bus0 + bus1 + uart + date + state
    

while True:
    if raise_timmer == True:
       print_timmer.init( period = 1000, mode = machine.Timer.ONE_SHOT, callback = print_func )
       raise_timmer = False
    
    set_regs()
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
        Uart.serial_write_data( initg = measure_gir, inite = measure_ele )
        Motors.move( posE*0.05, posG*0.05 )
        

    elif STATE == REMOTE:
        measure_gir = ASGIR.degAngle()
        measure_ele = ASELE.degAngle()
        posG = PID_GIR.compute( measure_gir )
        posE = PID_ELE.compute( measure_ele )
        Uart.serial_write_data( initg = measure_gir, inite = measure_ele)
        Motors.move( posE*0.05, posG*0.05 )
    
    
    elif STATE == IDLE:
        pass
    
    
    elif STATE == MANUAL:
        posG, posE  = levers.check( factor = 0.25 )
        measure_gir = ASGIR.degAngle()
        measure_ele = ASELE.degAngle()
        Uart.serial_write_data( initg = measure_gir, inite = measure_ele)
        Motors.move( posE, posG )
    
    
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
        Uart.serial_write_data( initg = measure_gir, inite = measure_ele)
        Motors.move( posE*0.05, posG*0.05 )
        
            
    # VERIFICA SE RECEBEU ALGO DA SERIAL 
    BYTE_ID = 0 # Uart.recv_from()
    
    # Se recebu um Byte_ID válido, verifica qual ação deve ser tomada 
    if BYTE_ID:
        try:
            # BYTE_ID == W -> Questões de Potencia 
            if BYTE_ID == b'W':
                FC = Uart.read(1)
                if   FC == b'O':  Motors.set_torque( True )
                elif FC == b'F':  Motors.set_torque( False )


            # BYTE_ID == M -> Questões de Motores ( posição e configuração ) 
            elif BYTE_ID == b'M':
                FC = Uart.read(1)
                if   FC == b'G':
                    Motors.configure( Motors.GIR, pos = AZIMUTE, step = struct.unpack( 'f', Uart.read(4))[0], micro_step = struct.unpack( 'f', Uart.read(4))[0], ratio = 1 )
                elif FC == b'E':
                    Motors.configure( Motors.ELE, pos = ALTITUDE, step = struct.unpack( 'f', Uart.read(4))[0], micro_step = struct.unpack( 'f', Uart.read(4))[0], ratio = 1 )


            # BYTE_ID == H -> Questões de Data e Hora  
            elif BYTE_ID == b'H':
                OP = Uart.read(1)
                if OP == b'C':
                    y, m, d, hh, mm, ss  = struct.unpack( 'bbbbbb', Uart.read(6) ) 
                    if y < 50 and  m <= 12 and d <= 31:
                        if hh < 24 and mm < 60 and ss < 60:
                            Y, M, D, H, N, S, DW = TIME
                            if y != Y:                  Time.wrong_datetime = True   
                            elif m != M:                Time.wrong_datetime = True 
                            elif d != D:                Time.wrong_datetime = True  
                            elif hh != H:               Time.wrong_datetime = True   
                            elif mm < N-5 or mm > N+5 : Time.wrong_datetime = True 
                            else:                       Time.wrong_datetime = True 
                            
                print( BYTE_ID, OP ) 
                if OP == chr(6).encode():
                    y, m, d, hh, mm, ss  = struct.unpack( 'bbbbbb', Uart.read(6) )
                    if y < 50 and  m <= 12 and d <= 31:
                        if hh < 24 and mm < 60 and ss < 60:
                            status = Time.set_time( y, m, d, hh, mm, ss )
                            if status == 1: Time.wrong_datetime = True
                            else:           Time.wrong_datetime = False  
            

            # BYTE_ID == S -> Questões de States  
            elif BYTE_ID == b'S':
                FC = Uart.read(1)
                if FC == b'S': STATE = IDLE 
                if FC == b'C': STATE = AUTOMATIC
                if FC == b'D':
                    fake_time.compute_new_day() 
                    STATE = DEMO 
                if FC == b'R': machine.soft_reset() 
                if FC == b'L': STATE = MANUAL 
            

            # BYTE_ID == C -> Questões de Controle ( Posições e PV) 
            elif BYTE_ID == b'C':
                FC = Uart.read(1)
                if FC == b'M':
                    PID_GIR.set_PV( struct.unpack( 'f', Uart.read(4) )[0] )
                    PID_ELE.set_PV( struct.unpack( 'f', Uart.read(4) )[0] )
                    STATE = REMOTE 
                
                elif FC == b'G':
                    FC = Uart.read(1)
                    if   FC == b'D':  PID_GIR.Kd = (struct.unpack( 'f', Uart.read(4) )[0])
                    elif FC == b'I':  PID_GIR.Ki = (struct.unpack( 'f', Uart.read(4) )[0])
                    elif FC == b'P':  PID_GIR.Kp = (struct.unpack( 'f', Uart.read(4) )[0])
                    elif FC == b'M':
                        PID_GIR.set_PV( struct.unpack( 'f', Uart.read(4) )[0] )
                        STATE = REMOTE
                        
                elif FC == b'E':
                    FC = Uart.read(1)
                    if   FC == b'D':  PID_ELE.Kd = (struct.unpack( 'f', Uart.read(4) )[0])
                    elif FC == b'I':  PID_ELE.Ki = (struct.unpack( 'f', Uart.read(4) )[0])
                    elif FC == b'P':  PID_ELE.Kp = (struct.unpack( 'f', Uart.read(4) )[0])
                    elif FC == b'M':
                        PID_ELE.set_PV( struct.unpack( 'f', Uart.read(4) )[0] )
                        STATE = REMOTE 
                

            # BYTE_ID == P -> Questões de Diagnostico e Prints  
            elif BYTE_ID == b'P':
                FC = Uart.read(1)
                if FC == b'A':
                    DATETIME, DT_ACK = Time.get_time() 
                    MG     = struct.pack( 'f', Motors.get_gir_position() ) 
                    ME     = struct.pack( 'f', Motors.get_ele_position() ) 
                    PID_G  = struct.pack( 'ffff', PID_ELE.Kd, PID_ELE.Ki, PID_ELE.Kp, PID_ELE.PV )
                    PID_E  = struct.pack( 'ffff', PID_GIR.Kd, PID_GIR.Ki, PID_GIR.Kp, PID_GIR.PV )
                    S_ACK  = struct.pack( 'b', ASELE.get_ack() + ASGIR.get_ack( ) )
                    SG     = struct.pack( 'f', ASGIR.degAngle() )
                    SE     = struct.pack( 'f', ASELE.degAngle() ) 
                    AZ     = struct.pack( 'f', AZIMUTE )
                    AT     = struct.pack( 'f', ALTITUDE ) 
                    ON_OFF = struct.pack( 'b', Motors.POWER.value() )
                    State  = struct.pack( 'b', STATE )
                    ACK    = b'\\\\'
                    MSG  = DATETIME + DT_ACK
                    MSG += MG + PID_G
                    MSG += ME + PID_E
                    MSG += S_ACK
                    MSG += SG + ASGIR._read( 0, 11 ) 
                    MSG += SE + ASELE._read( 0, 11 ) 
                    MSG += AZ + AT
                    MSG += ON_OFF + State + ACK
                    print( MSG ) 
                    Uart.response_msg( initD = MSG )   

                elif FC == b'S':
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
        
    # Tempo de looping do Pico
    # FAZER UM SINCRONIZADOR DE LOOP 
    time.sleep( 0.025 ) 
