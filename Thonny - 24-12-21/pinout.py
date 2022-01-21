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

POWER       = 15

SDA_DS      = 16 
SCL_DS      = 17
 
SDA_AS      = 18
SCL_AS      = 19 

UART_TX     = 20 
UART_RX     = 21

LED_BUILTIN = 25

# DATA E HORA 
UTC = -3 
DOM = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ANB = lambda year : True if (year%100 != 0 and year%4 == 0) or (year%100 == 0 and year%400 == 0) else False

# CONFIGURAÇÕES DE RASTREAMENTO 
LATITUDE    = -29.16530765942215
LONGITUDE   = -54.89831672609559 
TEMPERATURE =  298.5
PRESSURE    =  101.0

LOCALIZATION = [ LATITUDE, LONGITUDE, TEMPERATURE, PRESSURE ]


# MACRODEFINIÇÕES 
AUTOMATIC_SLEEPING =  3   # Dormindo esperando um novo dia começar 
AUTOMATIC_BACKWARD =  2   # Retorna para a posição inicial do novo dia
AUTOMATIC_TRACKING =  1   # Rastreia o sol em um dia normal 
WAKE_UP            =  0   # Opção de inicio. É chamado quando o Rasp liga
MANUAL_CONTROLING  = -1   # Ativa o controle por Levers 
MANUAL_STOPING     = -2   # Para o rastreio do tracker
MANUAL_DEMO        = -3   # Segue o sol de forma acelerada ( Demonstração ) 
GET_DATA           =  99 

LOW = 0
HIGH = 1 
