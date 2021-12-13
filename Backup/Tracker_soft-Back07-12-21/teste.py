from utils.cliente_TCP import Socket_NodeRed

mysock = Socket_NodeRed() 

mysock.connect( host = '127.0.0.1', port = 2411 )

from random import randint 
from math import cos, radians

from time import sleep 

count = 1 
while True: 
    
    Azimute = mysock.receive() 

    
    rec = ''
    while rec  == '':   
        rec = mysock.receive( ) 

        print('Recebendo : ', rec )

    print('Enviando {}'.format( TemperaturaDaCasa ) )
    
    sleep(1)