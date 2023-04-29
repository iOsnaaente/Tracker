import minimalmodbus as mmb 

a, b, c = 0,0,0 
HOLDING = [] 

def att_holding( ):  
    global a, b, c, HOLDING  
    HOLDING = [ a, b, c]

def att_regs_holding( ): 
    global a, b, c, HOLDING
    a,b,c = HOLDING 


COM = mmb.Instrument( port = 'COM12', slaveaddress = 12, mode = mmb.MODE_RTU, debug = True )
#COM.write_bit( registeraddress = 1, value = True, functioncode = 5 ) 

import time

while True:
    try:
        COM.read_register( 2  )
    except:
        pass 

    time.sleep(0.1)
    #COM.write_bits( 2, [True,True, False] )
    #COM.write_bits( 2, False )




"""
def none():
    import machine
    import struct
    import time

    ## REGISTRADORES
    # Registradores Coil # Read from 1 to 2000
    LED1_RED    = machine.Pin( 10, machine.Pin.OUT)
    LED1_BLUE   = machine.Pin( 11, machine.Pin.OUT)
    LED2_RED    = machine.Pin( 12, machine.Pin.OUT)
    LED2_BLUE   = machine.Pin( 13, machine.Pin.OUT)

    #COIL_REGISTERS = { LED1_RED  : 0,
    #                   LED1_BLUE : 0,
    #                   LED2_RED  : 0,
    #                   LED2_BLUE : 0   }

    # Registradores Discrete 
    LEVER1_R = 0
    LEVER1_L = 0
    LEVER2_R = 0
    LEVER2_L = 0

    #DISCRETE_REGISTER = { LEVER1_R : 0,
    #                      LEVER1_L : 0,
    #                      LEVER2_R : 0,
    #                      LEVER2_L : 0   }


    # Registradores Holding
    POS_M1 = 10
    POS_M2 = 20

    #HOLDING_REGISTERS = {
    #                        POS_M1 : 0,
    #                        POS_M2 : 0   }

    # Registradores Input
    AZIMUTE = 10
    ZENITE  = 10

    #INPUT_REGISTERS = {
    #                    AZIMUTE : 10,
    #                    ZENITE  : 20   }



    ## ADDRS COIL
    ## ADDRS INPUT
    ## ADDRS HOLDING
    ## ADDRS DISCRETE INPUTS
    ADDR_AVAILABLE = []


    ## ESPECIAL ONES
    READ_AND_DELETE = 99
    DATA_REG_COIL = 6



    class myModbusCommunication:

    ## STATE MACHINE  
    #-------------
    #ADU
    SLAVE    = 100
    #-------------
    # PDU
    FC       = 101

    #----------------
    ADDR_REG_H = 102_1
    ADDR_REG_L = 102_2
    QNT_REG_H  = 103_1
    QNT_REG_L  = 103_2
    #----------------

    #-------------
    CHK      = 100_4 
    #-------------

    ## FUNCTIONS CODE 
    # DISCRETES
    READ_DISCRETE_INPUT       = 2

    # COILS 
    READ_COILS_REGISTER       = 1
    WRITE_COIL_REGISTER       = 5
    WRITE_COIL_REGISTERS      = 15

    # ANALOGS
    READ_INPUT_REGISTER       = 4

    # HOLDINGS
    READ_HOLDING_REGISTER     = 3
    WRITE_HOLDING_REGISTER    = 6
    WRITE_HOLDING_REGISTERS   = 16

    EXCEPTION_CODE            = -1 

    # Save the FC used 
    FUNCTION_CODE = 0
    ADDR_REG      = 0
    QTN_REG       = 0 
    DATA_REG      = 0 


    # PARAM. DE FUNC.
    FUNCTIONS_CODE_AVAILABLE = [ 1, 2, 3, 4, 5, 6, 15, 16 ]
    HOLDING_REGS_MAX = 10 
    INPUT_REGS_MAX = 10 
    DISCRETE_REGS_MAX = 10
    COIL_REGS_MAX = 10 

    # Para ler um registrador precisa de dois bytes, mas lemos um por vez, então::
    HIGH_REG = True
    LOW_REG  = False 

    def __init__( self, uart_num : int, baudrate : int, tx : int, rx : int, **kwargs ):
        if kwargs.keys():
            if 'parity' in kwargs.keys():
                self.parity = kwargs['parity']
                if type( self.parity ) == str :
                    if self.parity == 'even' : self.parity = 0
                    elif self.parity == 'odd': self.parity = 1
                    else                     : self.parity = None
                elif type( self.parity ) == int:
                    if self.parity > 1 or self.parity < 0:
                        self.parity = None
            else:
                self.parity = None 
            if 'stop_bits' in kwargs.keys():
                self.stop_bits = kwargs['stop_bits']
                if type( self.stop_bits ) is not int:
                    self.stop_bits = 1
            else:
                self.stop_bits = 1 
            if 'data_bits' in kwargs.keys():
                self.data_bits = kwargs['data_bits']
                if type( self.data_bits ) is not int:
                    self.data_bits = 8
            else:
                self.data_bits = 8 
            if 'timeout' in kwargs.keys():
                self.timeout =  kwargs['timeout']
                if type( self.timeout ) is not int:
                    self.timeout = 0
            else:
                self.timeout = 0.05
        else:
            self.parity = 1
            self.stop_bit = 1
            self.data_bits = 8
            self.timout = 0.05

        self.TX_PIN = rx
        self.TX_PIN.irq( handler = self.read, trigger = machine.Pin.IRQ_FALLING ) 
        
        self.STATE = self.SLAVE
        
        self.myUART = machine.UART( uart_num, baudrate, parity = self.parity, stop = self.stop_bits, bits = self.data_bits, rx = rx, tx = tx )


    def deactive_irq(self):
        pass

    def active_irq(self):
        pass

    def response(self, FC, DATA ):
        pass 


    def _set_high_reg(self):
        self.HIGH_REG = True
        self.LOW_REG  = False

    def _set_low_reg(self):
        self.HIGH_REG = False
        self.LOW_REG = True 

    def read(self, irq_obj ):
        
        while self.myUART.any():
            read = self.myUART.read(1) 
        
            # IDENTIFICA O SLAVE 
            if self.STATE == self.SLAVE:
                read = self.myUART.read(1)
                if read == self.ADDR_SLAVE:
                    if self.DEBUG: print( 'SLAVE {} FOUND'.format( self.ADDR_SLAVE) )
                    self.STATE = self.FC
                                        
            # IDENTIFICA AS FUNÇÕES DISPONÍVEIS 
            elif self.STATE == self.FC: 
                read = self.myUART.read(1)
                
                # DISCRETES
                if read == self.READ_DISCRETE_INPUT:
                    if DEBUG:  print( 'FC = 2: READ_DISCRETE_INPUT' )
                    self.FUNCTION_CODE = self.READ_DISCRETE_INPUT
                    self.STATE         = self.ADDR_REG_H
                
                # COILS 
                elif read == self.READ_COILS_REGISTER:
                    if DEBUG:  print( 'FC = 1 : READ_COILS_REGISTER' )
                    self.FUNCTION_CODE = self.READ_COILS_REGISTER
                    self.STATE         = self.ADDR_REG_H 
                    self._set_high_reg()
                elif read == self.WRITE_COIL_REGISTER:
                    if DEBUG:  print( 'FC = 5 : WRITE_COIL_REGISTER' )
                    self.FUNCTION_CODE = self.WRITE_COIL_REGISTER
                    self.STATE         = self.ADDR_REG_H 
                elif read == self.WRITE_COIL_REGISTERS:
                    if DEBUG:  print( 'FC = 15 : WRITE_COIL_REGISTERS' )
                    self.FUNCTION_CODE = self.WRITE_COIL_REGISTERS
                    self.STATE         = self.ADDR_REG_H 
                
                # ANALOGS
                elif read == self.READ_INPUT_REGISTER:
                    if DEBUG:  print( 'FC = 4 : READ_INPUT_REGISTER' )
                    self.FUNCTION_CODE = self.READ_INPUT_REGISTER
                    self.STATE         = self.ADDR_REG_H 
                
                # HOLDINGS
                elif read == self.READ_HOLDING_REGISTER:
                    if DEBUG:  print( 'FC = 3 : READ_HOLDING_REGISTER' )
                    self.FUNCTION_CODE = self.READ_HOLDING_REGISTER
                    self.STATE         = self.ADDR_REG_H 
                elif read == self.WRITE_HOLDING_REGISTER:
                    if DEBUG:  print( 'FC = 6 : WRITE_HOLDING_REGISTER' )
                    self.FUNCTION_CODE = self.WRITE_HOLDING_REGISTER
                    self.STATE         = self.ADDR_REG_H 
                elif read == self.WRITE_HOLDING_REGISTERS:
                    if DEBUG:  print( 'FC = 16 : WRITE_HOLDING_REGISTERS' )
                    self.FUNCTION_CODE = self.WRITE_HOLDING_REGISTERS  
                    self.STATE         = self.ADDR_REG_H 
                
                # EXCEPTION 
                else:
                    if DEBUG:  print( 'FUNCTION CODE NOT FOUND - EXCEPTION CODE' )
                    self.FUNCTION_CODE = EXCEPTION_CODE 
                    self.STATE = self.SLAVE
            
            elif self.STATE == self.ADDR_REG_H:
                self.ADDR_REG = self.myUART.read(1) << 8
                self.STATE = self.ADDR_REG_L
            elif self.STATE == self.ADDR_REG_L:
                self.ADDR_REG += self.myUART.read(1)
                if self.FUNCTION_CODE == SELF.READ_INPUT_REGISTER and self.ADDR_REG > self.INPUT_REGS_MAX:
                    if self.DEBUG: print('Registrador de input inválido. INPUT_REGS_MAX = {} GOT {}'.format(self.INPUT_REGS_MAX, self.ADDR_REG) )
                    self.STATE = SLAVE
                else:
                    if self.DEBUG: print('ADDR_REG: ', self.ADDR_REG )
                    self.STATE = QNT_REG_H
            
            elif self.STATE == QNT_REG_H:
                self.QNT_REG = self.myUART.read(1) << 8
                self.STATE = self.QNT_REG_L
            elif self.STATE == self.QNT_REG_L:
                self.QNT_REG += self.myUART.read(1)
                if self.FUNCTION_CODE == SELF.READ_INPUT_REGISTER and (self.QNT_REG > ( self.INPUT_REGS_MAX + self.QNT_REG)):
                    if self.DEBUG: print('Registrador de input inválido. INPUT_REGS_MAX = {} GOT {} + Offset of {}'.format(self.INPUT_REGS_MAX, self.ADDR_REG, self.QNT_REG) )
                    self.STATE = SLAVE
                else:
                    if self.DEBUG: print('QNT_REG: ', self.QNT_REG )
                    self.STATE = self.FUNCTION_CODE             
            
            
            elif self.STATE == self.READ_INPUT_REGISTER:
                AZIMUTE = 12
                ZENITE = 15 
                print( 'enviar o azimute afins' ) 


    def serial_main():
    com = myModbusCommunication( 1, 19200, tx = machine.Pin(20), rx = machine.Pin(21) ) 
    print( com.myUART )     


    while True:
        pass 



    while True:
        STATE = SLAVE 
        while com.myUART.any():
            # IDENTIFICA O SLAVE 
            if STATE == SLAVE:
                read = com.myUART.read(1)[0]
                if read == ADDR_SLAVE:
                    if DEBUG:
                        print( 'SLAVE {} FOUND'.format(ADDR_SLAVE) )
                    STATE = FC
                    
            # IDENTIFICA AS FUNÇÕES DISPONÍVEIS - NÃO IMPLEMENTADO O MÉTODO DE EXCEPTION CODE 
            elif STATE == FC: 
                read = com.myUART.read(1)[0]
                if read == WRITE_HOLDING_REGISTER:
                    if DEBUG:
                        print( 'FC = 16: WRITE_HOLDING_REGISTER' )
                    STATE = WRITE_HOLDING_REGISTER
                    
                elif read == FORCE_COIL:
                    if DEBUG:
                        print( 'FC = 5 : FORCE_COIL' )
                    STATE = FORCE_COIL
                else:
                    STATE =  READ_AND_DELETE
                
                
            # SE ESTAMOS LENDO UM FORCE_COIL
            # |ADDR_L| ADDR_H | TRUE_or_FALSE | 0x00 |  
            elif STATE == FORCE_COIL:
                read = com.myUART.read( 4 )  
                ADDR_COIL = struct.unpack('>h', read[0:2] )[0]
                DATA_COIL = 1 if read[2] == 0xff else 0
                print( ADDR_COIL, DATA_COIL )
                if ADDR_COIL == 0:
                    LED1_RED.value( DATA_COIL )
                if ADDR_COIL == 1:
                    LED1_BLUE.value( DATA_COIL )
                if ADDR_COIL == 2:
                    LED2_RED.value( DATA_COIL )
                if ADDR_COIL == 3:
                    LED2_BLUE.value( DATA_COIL )
                
                STATE = SLAVE 

        
        time.sleep( 0.01 )
        

    if __name__ == '__main__':
    serial_main()
        
"""        
        
        
        
        
