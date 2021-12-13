from machine import Pin 
from machine import RTC 
from time    import sleep
from DS3231  import DS3231
from Const   import *

rtc_pico = RTC()
DS       = DS3231( 0, Pin( SDA_DS ), Pin( SCL_DS ), addrs = [0x68, 0x57] )


# To set the date, use .datetime() and to get the date too
# A tuple with ( year, month, day, weekday, hours, minutes, seconds, subseconds)
#rtc.datetime( ( 2021,11, 18, 4, 11, 28, 0, 0  ) )

while True:
    print( '\n\n\n\n')
    print("Datetime pico:\t", rtc_pico.datetime() )
    print("Datetime DS:\t", DS.now() )
    
    sleep(1)