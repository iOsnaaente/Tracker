# PROGRAMAÇÃO DO EEPROM 25Q32
WRITE_ENABLE      = 0x06 #Address Write Enable
WRITE_DISABLE     = 0x04 #Address Write Disable
CHIP_ERASE        = 0xc7 #Address Chip Erase
READ_STATUS       = 0x05 #Address Read Status
READ_DATA         = 0x03 #Address Read Data
PAGE_PROGRAM_STAT = 0x02 #Address Status Page Program
CHIP_COMMAND_ID   = 0x9F #Address Status Read Id 

from machine import Pin, SPI
from struct import pack 
from time import sleep 

class EEPROM_25Q80:
    
    buff_read   = bytearray(255)
    buff_write  = bytearray(255)
    
    command     = bytearray(2)
    address     = bytearray(2)

    id          = bytearray(1)
    memory_type = bytearray(1)
    capacity    = bytearray(1)
    
    def __init__(self, CSn : Pin, MOSI : Pin, MISO : Pin, SCK : Pin, baudrate = 1000000, bits = 8, phase = 0, polarity = 0 ):
        self.tx  = MOSI
        self.rx  = MISO
        self.sck = SCK 
        self.cs  = CSn 
        self.spi  = SPI( 0, sck= self.sck, mosi= self.tx, miso= self.rx, baudrate= baudrate, polarity= polarity, phase= phase, bits= bits, firstbit = SPI.MSB )
    
    
    def send_command( self, command : int ) -> None:
        self.cs.high()
        sleep(0.001)
        self.cs.low()
        buff = bytearray(1)
        self.spi.write_readinto( pack('B', command) , buff )
        
        
    def not_busy(self) -> None :
        self.send_command( READ_STATUS )
        readFromSPI = bytearray(1)
        readFromSPI = b'0'
        while ( readFromSPI is False ):
            self.spi.write_readinto( b'0', readFromSPI ) 
        self.cs.high() 
    
    
    def chip_information( self ):
        self.send_command( CHIP_COMMAND_ID )
        self.id          = self.spi.read( 1 )
        self.memory_tipe = self.spi.read( 1 )
        self.capacity    = self.spi.read( 1 )
        self.cs.high()
        self.not_busy()
    
    def erase(self):
        print("CHIP ERASE CALLED")
        self.send_command ( WRITE_ENABLE )
        self.send_command( CHIP_ERASE )
        self.cs.high()
        self.not_busy()
    
    def print_page(self, page : int ) -> None :
        buff = bytearray(256) 
        self.read_page( page, buff ) 
        for i in range(16):
            for j in range(16):
                print(buff[ i*j + j], end=' ' )
            print('\n')
    
    def read_page(self, page : int, page_buff : list = [] ):
        self.send_command( READ_DATA )
        buff = bytearray(3)
        buff[0] = page >> 8
        buff[1] = page & 0xff
        buff[2] = 0x00 
        self.spi.write( buff )
        if page_buff == []: 
            self.buff_read = self.spi.read(256)
        else:
            page_buff = self.spi.read(256)
        self.cs.high()
        self.not_busy()

    def write_page(self, page, data_buff):
        self.send_command( WRITE_ENABLE )
        self.send_command( PAGE_PROGRAM_STAT )
        buff    = bytearray(3)
        buff[0] = page >> 8
        buff[1] = page & 0xff
        buff[2] = 0x00 
        self.spi.write( buff )
        self.spi.write( data_buff )
        self.cs.high()
        self.not_busy()

    def write_one_byte(self, page, offset, data):
        self.read_page( page, self.buff_write )
        self.buff_write[offset] = data
        self.write_page( page, self.buff_write )

    def write_bytes( self, page, offset, data, len ):
        buff = bytearray(256)
        read_page( buff )
        for i in range( len ):
            buff[ offset + i] = data[i]
        write_page( page, buff )  
            
        
        
        
    
    


