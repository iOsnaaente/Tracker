import Tracker.Serial.myRegisters as rg

INPUTS    = rg.Registers( float, 8 )
# |       0 |       1 |    2 |     3 |   4 |    5 |      6 |      7 | 
# | MAG_GIR | MAG_ELE | YEAR | MONTH | DAY | HOUR | MINUTE | SECOND | 

HOLDINGS  = rg.Registers( float, 11 )
# |        0 |    1 |    2 |    3 |       4  | 
# | POS_MGIR | G_Kp | G_Ki | G_Kd | AZIMUTE  |

# |        5 |    6 |    7 |    8 |        9 |
# | POS_MELE | E_Kp | E_Ki | E_Kd | ALTITUDE |  

# |       10 | 
# |    STATE |  


DISCRETES = rg.Registers( bool , 10 )
# STATUS DOS SENSORES E PLANTA 
# | 8Bits_SENS_GIR | 8Bits_SENS_ELE |


COILS     = rg.Registers( bool , 4 ) 
# CONFIGURAÇÕES + LEDS 
# |     0 |     1 |     2 |     3 |
# | LD_R1 | LD_B1 | LD_R2 | LD_B2 |



# DATA E HORA 
ANB = lambda year : True if (year%100 != 0 and year%4 == 0) or (year%100 == 0 and year%400 == 0) else False
DOM = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
UTC = -3 


# CONFIGURAÇÕES DE RASTREAMENTO 
LATITUDE    = -29.16530765942215
LONGITUDE   = -54.89831672609559 
TEMPERATURE =  298.5
PRESSURE    =  101.0


# LOCALIZATION LIST - GET_SUN_POSITION
LOCALIZATION = [ LATITUDE, LONGITUDE, TEMPERATURE, PRESSURE ]


# STATES 
FAIL_STATE = 0
AUTOMATIC  = 1
MANUAL     = 2
REMOTE     = 3
DEMO       = 4
IDLE       = 5


