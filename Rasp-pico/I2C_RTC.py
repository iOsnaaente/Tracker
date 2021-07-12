from machine import Pin, I2C 
from time import sleep, sleep_ms

class DS3231: 
    DoW      = ["Domingo","Segunda-feira","Terça-Feira","Quarta-Feira","Quinta-Feira" ,"Sexta-Feira","Sábado"]
    temp     = 0.0
     
    def __init__(self, NUM : int, SDA : Pin, SCL : Pin, addrs : bytes(2) = [0x68, 0x57], pages : int = 128, len_pages : int = 32 ):
        self.DS_I2C    = I2C( NUM, sda = SDA, scl = SCL ) 
        self.ADDR_DS   = addrs[0]
        self.ADDR_EE   = addrs[1]
        self.len_pages = len_pages 
        self.num_pages = pages
        
    def set_time(self, y : bytes, m : bytes, d : bytes, dow : bytes, hh : bytes, mm : bytes, ss : bytes ):
        buff = bytearray( [ self.dec2bcd(t) for t in [ss, mm, hh, dow, d, m, y] ] )
        self.DS_I2C.writeto_mem( self.ADDR, 0x00, buff )  
        sleep_ms(5)
        
    def now( self ) -> list:
        time = self.DS_I2C.readfrom_mem( self.ADDR_DS, 0x00, 7)
        time = [ self.bcd2dec( time[i] ) for i in range(len(time)-1,-1,-1) if i != 3 ]
        time.append( 3 )
        return time
    
    def get_day_of_week(self, day : bytes ) -> bytes:
        return self.DoW[ day ]
    
    def get_temperature( self ) -> float:
        temp3231 = bytearray(2)
        try:
            temp3231 = self.DS_I2C.readfrom_mem( self.ADDR_DS, 0x11, 2, addrsize = 16)
            tMSB = temp3231[1] 
            tLSB = temp3231[0]
            self.temp = ( float( ( tMSB << 8 | (tLSB & 0xC0) ) )/256.0 )
        except:
            self.temp = -9999
        
        return self.temp 
    
    def bcd2dec(self, bcd : bytes ) -> bytes: 
        return (bcd>>4)*10 + ( bcd & 0b1111 )  

    def dec2bcd(self, dec : bytes ) -> bytes:
        return ((dec//10)<<4) + (dec % 10)
    
    def scan( self, dec : bool = True ) -> list:
        if dec :
            return self.DS_I2C.scan()
        else:
            return [ hex(add) for add in self.DS_I2C.scan() ] 
        
    def get_parameters(self) -> list:
        return self.DS

    def read( self, addr : int, nbytes : int ) -> bytearray:
        return self.DS_I2C.readfrom_mem( self.ADDR_EE, addr, nbytes, addrsize = 16 ) 
 
    def write( self, addr : int, buff : bytearray) -> None:
        offset = addr % self.len_pages
        nibble = 0 
        if offset > 0 :
            nibble = self.len_page - offset
            self.DS_I2C.writeto_mem( self.ADDR_EE, addr, buff[0: nibble], addrsize = 16 )
            sleep_ms(5)
            addr += nibble
        for i in range( nibble, len(buff), self.len_pages ) :
            self.DS_I2C.writeto_mem( self.ADDR_EE, addr-nibble+i, buff[i:i+self.len_pages], addrsize=16)
            sleep_ms(5)



