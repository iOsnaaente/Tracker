import paho.mqtt.client as mqtt

from struct import pack
from random import randint
from time import sleep
 
IP   = "192.168.4.19"
PORT = 1883

AREA_ID   = 10
SENSOR_ID = 5000
 
# Topicos providos por este sensor
tt = "Bruno/fala/"
 
# Cria um identificador baseado no id do sensor
client = mqtt.Client( client_id = 'NODE:1', protocol = mqtt.MQTTv31 )

# Conecta no broker
client.connect( IP, PORT )
 
while True:
    # Gera um valor de temperartura aleatório
    t = 'Oi pessoa'
    
    # Codificando o payload como big endian, 2 bytes
    payload = t.encode() 
    
    # Envia a publicação
    client.publish( tt, payload, qos = 2 )
    print( tt + "/" + str( t ) )

    
    sleep(1)