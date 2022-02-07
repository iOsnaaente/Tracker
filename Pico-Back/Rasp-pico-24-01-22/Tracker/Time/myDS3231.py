from machine import I2C, SoftI2C, Pin, soft_reset 
from time    import sleep_ms
from struct  import pack, unpack 

'''
DS3231 // Classe destinada para o uso do módulo DS3231, um RTC que utiliza o protocolo I2C de comunicação. 
O códulo DS3231 possui também, um EEPROM de 32kbi ( 4k Bytes ) anexa a placa, utilizando dos mesmos meios
de comunicação. Por padrão o endereço do DS3231 é 0x68 e o endereço do EEPROM anexo é 0x57. 
'''
class DS3231: 
    # Days of week - DoW  // Temperatura 
    DoW  = [ "Domingo", "Segunda-feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira" , "Sexta-Feira", "Sábado" ]
    temp = 0.0 

    '''
    Construtor da classe DS3231 ::
        >>> NUM : int -> (0 ou 1) depende qual dos dois I2C iremos usar ( Olhar o pinout do Rasp )
        >>> SDA : Pin -> Pino Serial DAta (SDA)  
        >>> SCL : Pin -> Pino Serial CLock ( SCL )
        >>> addrs : bytes(2) -> Endereços do DS3231 e AT24C32 ( Utilizar somente se forem alterados os valores em hardware)
        >>> pages : int -> Número de páginas do EEPROM ( O AT24C32 possui por padrão 128 páginas ) 
        >>> len_pages : int -> Número de bytes por página da EEPROM ( O AT24C32 possui por padrão 32 bytes por página )
    '''
    def __init__(self, i2c, addrs : bytes(2) = [0x68, 0x57], pages : int = 128, len_pages : int = 32 ):
        self.DS_I2C    = i2c
        self.ADDR_DS   = addrs[0]
        self.ADDR_EE   = addrs[1]
        self.len_pages = len_pages
        self.num_pages = pages
        self.time_not_sync = True 
        
        
    def _write( self, addr_mem : int, buffer : bytes ) -> None:
        if type( self.DS_I2C ) == I2C:
          self.DS_I2C.writeto_mem( self.ADDR_DS, addr_mem, buffer )
        elif type( self.DS_I2C ) == SoftI2C:
          self.DS_I2C.writeto( self.ADDR_DS, buffer, addr_mem )
            
            
    def _read( self, addr_mem : int, num_bytes : int = 2 ) -> list:
        try:
            if type( self.DS_I2C ) == I2C:
                return self.DS_I2C.readfrom_mem( self.ADDR_DS, addr_mem, num_bytes )
            
            elif type( self.DS_I2C ) == SoftI2C:
                return self.DS_I2C.readfrom( self.ADDR_DS, num_bytes, addr_mem )
        except:
            print( "DS3231 - Error -> _read line 31" ) 
            
            
            
    def set_time(self, y : bytes, m : bytes, d : bytes, hh : bytes, mm : bytes, ss : bytes ): 
        dow = self.get_DoW( y, m, d )
        buff = pack( 'bbbbbb', self.dec2bcd(ss), self.dec2bcd(mm), self.dec2bcd(hh), self.dec2bcd(dow), self.dec2bcd(d), self.dec2bcd(m), self.dec2bcd(y) )
        self._write( 0x00, buff )
        sleep_ms(1)
        
    def now( self ) -> list:
        time = self._read( 0x00, 7 )
        if time: 
            time = [ self.bcd2dec( time[i] ) for i in range(len(time)-1,-1,-1) if i != 3 ]
            time.append( 3 )
            return time
        else:
            print( 'Erro na leitura da data no DS3231')
            soft_reset() 

    def get_time(self):
        time = self.now()
        if self.time_not_sync: 
            return [time, False ]
        else:
            return [time, True ]
    
    def get_DoW(self, year : int, month : int, day : int) -> int :
        year  = year if year < 99 else year & 0x63 
        y_key = ((year//4 + year%7) % 7)-1 
        m_key = [ 1, 4, 4, 0, 2, 5, 0, 3, 6, 1, 4, 6 ] 
        DoW   = ( day + m_key[month-1] + y_key )
        DoW   = DoW if DoW < 7 else DoW // 7 
        return DoW if DoW >= 0 else 7 

    def get_day_of_week(self ) -> bytes:
        return self.DoW[ self.get_DoW ]
    
    def get_temperature( self ) -> float:
        temp3231 = b'' 
        try:
            temp = self._read( 0x11, 2)
            self.temp = temp[0] + ((temp[1] and 0xC0)>>6)/4
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


    '''
    Read é o método que irá ler um byte da EEPROM AT24C32 do DS3231 ::
        >>> addr : int -> Endereço de leitura da EEPROM 
        >>> nbytes : int ->  Quantidade de bytes para serem lidos 
    nbytes é número de bytes que queremos ler apartir do endereço passa como parâmetro.
    '''
    def read( self, addr : int, nbytes : int ) -> bytearray:
        return self.DS_I2C.readfrom_mem( self.ADDR_EE, addr, nbytes, addrsize = 16 ) 
    

    ''' 
    Write é o método de escrita na EEPROM AT24C32 do DS3231 ::
        >>> addr : int -> Endereço de escrita de 1 byte 
        >>> buff : bytearray -> dados a serem escritos na EEPROM
    O Buff começa a ser escrito a partir do primeiro endereço passado como parâmetro 
    na variável addr e vai sendo escrito na medida que é necessário.
    '''
    def write( self, addr : int, buff : bytearray) -> None:
        offset = addr % self.len_pages
        nibble = 0 
        if offset > 0 :
            nibble = self.len_page - offset
            self.DS_I2C.writeto_mem( self.ADDR_EE, addr, buff[0: nibble], addrsize = 16 )
            sleep_ms(1)
            addr += nibble
        for i in range( nibble, len(buff), self.len_pages ) :
            self.DS_I2C.writeto_mem( self.ADDR_EE, addr-nibble+i, buff[i:i+self.len_pages], addrsize=16)
            sleep_ms(1)

def main():
    from machine import Pin, I2C
    SDA_DS = 16 
    SCL_DS = 17
    isc0   = I2C ( 0,  sda = Pin( SDA_DS  ), scl = Pin( SCL_DS  ) )
    if 104 in isc0.scan():
        print( isc0.scan())
        Time   = DS3231( isc0  )
        #Time.set_time( 22, 1, 20, 15, 44, 50 )
        print( Time.get_time(), Time.get_temperature() ) 
    else:
        print( "I2C com erro ") 
        return 0 

if __name__ == "__main__":
    main() 
