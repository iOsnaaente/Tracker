import paho.mqtt.client as mqtt

from struct import pack
from random import randint
from time import sleep
 
IP   = "192.168.4.19"
PORT = 1883

 
# Topicos providos por este sensor
tt = "Bruno/fala/"
 
# Cria um identificador baseado no id do sensor
client = mqtt.Client( client_id = 'NODE:120519', protocol = mqtt.MQTTv31 )

# Conecta no broker
client.connect( IP, PORT )
 
while True:
    # Gera um valor de temperartura aleatório
    t = 1205
    
    # Codificando o payload como big endian, 2 bytes
    payload = pack('i', t)
    
    # Envia a publicação
    client.publish( tt, payload, qos = 2 )
    print( tt + "/" + str( t ) )

    
    sleep(1)