from Tracker.Time.myDS3231 import DS3231
from Tracker.Time.myRTC    import RTC_Pico

import machine
import time

class Datetime:
    
    RTC_DATETIME = 0
    DS_DATETIME  = 0
    
    RTC_AUTO : bool = False
    SYNC : bool = False 
    
    def __init__( self, I2C, RTC_AUTO : bool = False ):
        self.ds3231   = DS3231( I2C )
        self.rtc_int  = RTC_Pico()
        self.RTC_AUTO = RTC_AUTO
        if self.RTC_AUTO:
            self.set_time() 

    def set_time(self,yr : int = None, mt : int = None, dy : int = None, hr : int = None, mn : int = None, sc : int = None, wd : int = None ):  
        try:
            if all([yr, mt, dy, wd, hr, mn, sc]) is True:
                self.ds3231.set_time( y-2000, m, d, h, n, s )
                return True
            else:
                if self.RTC_AUTO:
                    y, m, d = self.rtc_int.get_date()
                    h, n, s = self.rtc_int.get_hour() 
                    self.ds3231.set_time( y-2000, m, d, h, n, s )
                    return True
                else:
                    return False 
        except:
            return False 
            
    def get_JuliansDay(self, y, m, d):
        if m < 3:
            y = y -1 
            m = m +12 
        A = y // 100 
        B = A // 4 
        C = 2 -A +B
        # Funciona para datas posteriores de 04/10/1582
        D = int( 365.25 * ( y +4716 ) )
        E = int( 30.6001 * ( m +1 ) )
        DJ = D + E + d + 0.5 + C - 1524.5 
        return DJ 
    
    @property 
    def ds_str(self):
        y,m,d,h,n,s = self.ds3231.now()[:6]
        return ( str(y)+str(m)+str(d)+str(h)+str(n)+str(s) )
    
    @property 
    def rtc_str(self):
        y,m,d = self.rtc_int.get_date()
        h,n,s = self.rtc_int.get_hour()
        return ( str(y-2000)+str(m)+str(d)+str(h)+str(n)+str(s)  )
        
    @property 
    def SYNC(self):
        ds = int(self.ds_str)
        rt = int(self.rtc_str)
        
        diff = abs(ds - rt ) 
        if diff > 130:
            return False
        else:
            return True
    
    def update(self):
        try:
            self.RTC_DATETIME = self.rtc_int.get_datetime()
            self.DS_DATETIME  = self.ds3231.now()
            if self.SYNC: 
                return True
            else:
                return False
        except:
            return False 
        
    def get_time( self ):
        if self.update():
            return [self.DS_DATETIME, True ]
        else:
            return [self.DS_DATETIME, False ]



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