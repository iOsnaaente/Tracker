import struct
import machine 
import select
import time 
import sys 

# Baseado nas informações do site abaixo:
# https://www.simplymodbus.ca/FC16.htm

MAX_READ_REGS      = 0x7D
MAX_WRITE_REGS     = 0x7B
MAX_BYTES_IN       = 256
MAX_READ_REGS      = 0x7D
MAX_WRITE_REGS     = 0x7B
MAX_MESSAGE_LENGTH = 256

ID     = 0
FC     = 1 
REG_H  = 2
REG_L  = 3
QNT_H  = 4
QNT_L  = 5
DATA_H = 4 
DATA_L = 5

class ModbusRTU: 

    FUNCTIONS_CODE = {          #  FC      EXECUTE WHEN RECEIVE             REPLY_AFTER_RECEIVED
        "FC_READ_SINGLE_REG"  : 0x04,  # Read single holding register 
        "FC_READ_MULT_REGS"   : 0x03,  # Read contiguous block of holding register  
        "FC_WRITE_SINGLE_REG" : 0x06,  # Write single holding register  
        "FC_WRITE_MULTI_REGS" : 0x10   # Write block of contiguous registers 
    }

    EXECPTIONS = {
        "ILLEGAL_FUNCTION"          : 0x01,
        "ILLEGAL_DATA_ADDRESS"      : 0x02,
        "ILLEGAL_DATA_VALUE"        : 0x03,
        "SERVER_DEVICE_FAILURE"     : 0x04,
        "ACKNOWLEDGE"               : 0x05,
        "SERVER_DEVICE_BUSY"        : 0x06,
        "MEMORY_PARITY_ERROR"       : 0x08,
        "GATEWAY_PATH_UNAVAILABLE"  : 0x0A,
        "DEVICE_FAILED_TO_RESPOND"  : 0x0B
    }

    # THE BAUDS PARITY AND TXPIN WILL NOT BE USED FOR USB CONNECTIONS
    def __init__(self, slave : int = 1, baudrate : int  = 19200, parity : int = 2, stopbit : int = 1, txenpin : machine.Pin = None, num_regs : int = 32  ): 
        self.baudrate = baudrate 
        self.parity   = parity
        self.stopbit  = stopbit 
        self.num_regs = num_regs 
        self.regs     = bytes( num_regs*2 )
        self.slave    = slave

        if txenpin is not None:
            self.Txenpin = txenpin
            self.Txenpin.low() 
        
        self.last_received  = 0 
        self.qnt_received   = 0 
        self.msg_received   = []
        self.msg_complete   = False
        self.T35            = 3.5*( (8 + stopbit + ( 1 if parity is not None else 0 ))/baudrate )*1000 # Para ms 

    # Função de recebimento
    def recv(self): 
        while True:
            self.last_received = time.ticks_ms()
            self.qnt_received = 0 
            while sys.stdin in select.select( [sys.stdin], [sys.stdout], [sys.stderr], 0 )[0]:  
                self.msg_received.append( sys.stdin.buffer.read(1) ) 
                self.qnt_received += 1
                self.last_received = time.ticks_ms()
                time.sleep(0.01)
                if self.qnt_received == MAX_BYTES_IN:
                    self.msg_complete = False 
                    self.qnt_received += 1
                    self.msg_received = [] 
                    return self.EXECPTIONS['ILLEGAL_DATA_VALUE']

            # Verifica o tempo entre o ultimo caracter para saber se a mensagem acabou 
            if time.ticks_diff( time.ticks_ms(), self.last_received ) > self.T35: 
                if self.qnt_received != 0:
                    self.msg_complete = True
                else:
                    self.msg_complete = False 
                self.qnt_received = 0 

            # Se a mensagem esta completa, verifica ela 
            if self.msg_complete: 
                self.validate_request( self.msg_received )
                self.msg_received = [] 
                self.msg_complete = False

    # Calcula o CRC
    def get_crc( self, buffer, lenght ):
        temp = 0xFFFF
        for i in range( lenght ):
            temp = temp ^ buffer[i]
        for _ in range(1, 9):
            flag = temp & 0x0001
            temp = temp >> 1
            if (flag):
                temp = temp ^ 0xA001
        temp2 = temp >> 8
        temp  = (temp << 8) | temp2
        temp &= 0xFFFF

        return temp


    # ADU -> SlaveID + PDU + CHK 
    def build_ADU(self, slave_ID, PDU: bytes):
        CRC = self.get_crc( PDU, len(PDU) )
        TO_SEND = bytearray() 
        TO_SEND.append( slave_ID )
        TO_SEND.extend( PDU )
        TO_SEND.append( CRC >> 8 ) 
        TO_SEND.append( CRC & 0x00ff )  
        self.send_reply( TO_SEND ) 

    # Envia o ADU serial como resposta a solicitação
    def send_reply( self, BUFFER_TO_SEND : bytes ): 
        for byte in BUFFER_TO_SEND:
            sys.stdout.buffer.write( byte )
        time.sleep_ms( self.T35 )

    
    def validate_request( self, BUFFER_IN : bytes ): 
        # Checagem do Slave ID 
        if BUFFER_IN[ID] != self.slave:
            return self.EXECPTIONS["ILLEGAL_FUNCTION"]

        # Checagem do FC 
        for function_code in self.FUNCTIONS_CODE.keys():
            if BUFFER_IN[FC] == function_code :
                fc_validated = 1 
                break 
        if not fc_validated:
            return self.EXECPTIONS["ILLEGAL_FUNCTION"]

        # IF READ SINGLE HOLDING REGISTER 
        if BUFFER_IN[FC] == self.FUNCTIONS_CODE['FC_WRITE_SINGLE_REG']:
            regs_num = (BUFFER_IN[ REG_H ]<<8) + BUFFER_IN[ REG_L ] 
            if regs_num >= MAX_WRITE_REGS:
                return self.EXECPTIONS['ILLEGAL_DATA_ADDRESS']
        
        # ELSE 
        regs_num =  (BUFFER_IN[QNT_H]<<8) + BUFFER_IN[QNT_L]

        # Checa a quantidade de registros 
        if BUFFER_IN[FC] == self.FUNCTIONS_CODE['FC_READ_MULT_REGS']:
            max_regs = MAX_READ_REGS
        elif BUFFER_IN[FC] == self.FUNCTIONS_CODE['FC_WRITE_MULTI_REGS']:
            max_regs = MAX_WRITE_REGS
        
        # Checa que não passou a quantidade máxima de registradores 
        if ((regs_num < 1) or (regs_num > max_regs )):
            return self.EXECPTIONS['ILLEGAL_DATA_ADDRESS']

        # Confere se o ADDR existe 
        start_addr = (BUFFER_IN[ REG_H] << 8) + BUFFER_IN[ REG_L] 
        if ((start_addr + regs_num) > self.num_registries):
            return self.EXECPTIONS['ILLEGAL_DATA_ADDRESS']

        # ELSE tudo OK 
        self.make_request( BUFFER_IN, BUFFER_IN[FC] ) 

        
    # Executa as ações de solicitação do mestre e responde 
    def make_request( self, BUFFER_IN : bytes, FC : int ):
        if FC == 0x03:      # FC = 3 
            self.read_holding_registers( BUFFER_IN )
        elif FC == 0x06:    # FC = 6 
            self.write_holding_registers( self, BUFFER_IN )   
        elif FC == 0x10:    # FC = 16 
            self.write_holding_registers( self, BUFFER_IN )


    # Read N Holding registers
    def read_holding_registers(self, BUFFER ):         
        starting_reg  = (BUFFER[REG_H]<<8) + BUFFER[REG_L]
        qnt_regs      = (BUFFER[QNT_H]<<8) + BUFFER[QNT_L]
        if not( 1 <= qnt_regs <= 125 ):
           return self.EXECPTIONS['ILLEGAL_DATA_VALUE'] 
        else:
            PDU = bytearray( )
            PDU.append( BUFFER[ID] )    # FUNCTION CODE 0x03
            PDU.append( qnt_regs*2 )    # NUMBER OF BYTES READ
            # REGISTERS TO READ  
            for i in range( qnt_regs ): 
                PDU.append( self.regs[ starting_reg+0 + i*2 ] ) 
                PDU.append( self.regs[ starting_reg+1 + i*2 ] )  
            self.build_ADU( self.slave, PDU )


    # Write a holding register 
    def write_holding_register( self, BUFFER ):
        self.regs[BUFFER[REG_H]] = BUFFER[DATA_H]
        self.regs[BUFFER[REG_L]] = BUFFER[DATA_L]
        # Resposta é a mesma de entrada 
        self.build_ADU( BUFFER[1:-2] )


    # Escreve multiplos registradores 
    def write_holding_registers(self, BUFFER ):
        ADDR_INIT = (BUFFER[REG_H]<<8)+BUFFER[REG_L]
        QNT_REGS  = (BUFFER[QNT_H]<<8)+BUFFER[QNT_L]
        for i in range( QNT_REGS ):
            self.regs[ADDR_INIT+0 + i*2] = BUFFER[ 6 + i*2 ] << 8
            self.regs[ADDR_INIT+1 + i*2] = BUFFER[ 7 + i*2 ]
            BYTES_WRITTEN = i 

        TO_SEND = bytearray()
        TO_SEND.append( BUFFER[ID])
        TO_SEND.append( BUFFER[REG_H] )
        TO_SEND.append( BUFFER[REG_L] )
        TO_SEND.append( BYTES_WRITTEN >> 8     )
        TO_SEND.append( BYTES_WRITTEN & 0x00ff )

        self.build_ADU( self.slave, TO_SEND )


mod = ModbusRTU( slave = 1, baudrate = 19200, parity = 2, stopbit = 1, num_regs = 8 )
mod.recv()
