from Tracker.Time.myDS3231 import DS3231
from pinout                import SDA_DS, SCL_DS

import machine 
import time


class RTC_Pico:
    RTC = 0 
    def __init__( self, yr : int = None, mt : int = None, dy : int = None, hr : int = None, mn : int = None, sc : int = None, wd : int = None ):  
        if all([yr, mt, dy, wd, hr, mn, sc]) is True:
            self.RTC = machine.RTC(  )
            self.RTC.datetime( (yr, mt, dy, wd, hr, mn, sc, 0) )
        else:
            self.RTC = machine.RTC()
    
    # To set the date, use .datetime() and to get the date too
    # A tuple with ( year, month, day, weekday, hours, minutes, seconds, subseconds)
    def set_datetime( self, yr : int = None, mt : int = None, dy : int = None, hr : int = None, mn : int = None, sc : int = None, wd : int = None ):
        try: 
            self.RTC.datetime( (yr, mt, dy, wd, hr, mn, sc) ) 
            return True
        except:
            return False

    @property
    def year ( self ) :
        return self.get_date()[0]
    @property
    def month ( self ) :
        return self.get_date()[1]
    @property
    def day ( self ) :
        return self.get_date()[2]

    @property
    def hours ( self ) :
        return self.get_hour()[0]
    @property
    def minutes ( self ) :
        return self.get_hour()[1]
    @property
    def seconds ( self ) :
        return self.get_hour()[2]
    
    
    def get_datetime( self ):
        return self.RTC.datetime()
    
    def get_date( self ):
        return self.get_datetime()[:3]

    def get_hour( self ):
        return self.get_datetime()[4:7]
    
    def get_day_of_week(self):
        return self.get_datetime()[3]
    

'''
isc = machine.I2C( 0, sda = machine.Pin( SDA_DS ), scl = machine.Pin( SCL_DS ), freq = 10000  ) 

rtc = RTC_pico(     )
DS  = DS3231  ( isc )

y, m, d = rtc.get_date()
h, n, s = rtc.get_hour() 


while True:
    print( '\n\n\n\n')
    print("Datetime pico:\t", rtc.get_datetime() )
    print("Datetime DS:\t", DS.now() )
    print( rtc.hours, rtc.minutes, rtc.seconds ) 
    
    time.sleep(1)
    
    
''' 
    
    
    
    
    
    
    
    
    
    
    