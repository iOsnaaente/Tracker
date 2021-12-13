from Const import *

import machine
import time 

''' MODOS DE OPERAÇÃO 
    Parameter           Slow Mode (Pin MODE = 0)  Fast Mode (Pin MODE = 1)
    Sampling rate       2.61 kHz (383μs)          10.42 kHz (95.9μs)
    Transition noise    ≤ 0.03° rms               ≤ 0.06° rms
    Propagation delay   384μs                     96μs
    Startup time        20ms                      80ms

    Pin Mode só pode ser setado antes de ser usado 
        >>> Aterrado(GND=0) / Alimentado(5V=1) diretamente na placa
'''

class AS5043A:

    # Máscara para obter os 10 primeiros bits contendo a Posição
    ANG_MASK    = 0B1111111111000000 

    # Máscara para obter os 6 ultimos bits contendo o Status 
    STATUS_MASK = 0B0000000000111111 

    OCF_MASK    = 0B100000 # Offset Compensation Finished 
    COF_MASK    = 0B010000 # CORDIC Overflow  
    LIN_MASK    = 0B001000 # Linearity Alarm    
    MagINC_MASK = 0B000100 # Magnitude Increase
    MagDEC_MASK = 0B000010 # Magnitude Decrease
    CHK_MASK    = 0B000001 # Checksum even_parity 
    
    OCF = False 
    ''' OCF (Offset Compensation Finished), logic high indicates that the 
        Offset Compensation Algorithm has finished and data is valid.
    '''

    COF = False             
    ''' COF (CORDIC Overflow), logic high indicates an out of range
        error in the CORDIC part. When this bit is set, the data at D9:D0
        is invalid. The absolute output maintains the last valid angular
        value. This alarm may be resolved by bringing the magnet
        within the X-Y-Z tolerance limits.
    '''
    
    LIN = False              
    ''' LIN (Linearity Alarm), logic high indicates that the input field
        generates a critical output linearity. When this bit is set, the data
        at D9:D0 may still be used, but may contain invalid data. This
        warning may be resolved by bringing the magnet within the
        X-Y-Z tolerance limits.
    '''

    MagINC = False
    ''' MagInc, (Magnitude Increase) becomes HIGH, when the magnet is 
        pushed towards the IC, thus the magnetic field strength is increasing.
    '''

    MagDEC = False 
    ''' MagDec, (Magnitude Decrease) becomes HIGH, when the magnet is pulled 
        away from the IC, thus the magnetic field strength is decreasing.
    '''
    
    ''' MagDec and MagInc: 
        Both signals HIGH indicate a magnetic field that is out of the
        allowed range. Pin 1 (MagRngn) is a combination of MagInc and
        MagDec. It is active low via an open drain output and requires
        an external pull-up resistor. If the magnetic field is in range, this
        output is turned OFF. (logic “high”).
        NOT USED YET 
    '''

    ''' Data D9:D0 is valid, when the status bits have the following
        configurations: OCF(1) COF(0) LIN(0) MagInc(x) MagDec(x) even_parity(x)
    '''

    # Angulo dos sensores de Giro e Elevação 
    angGir = 0.0 
    angEle = 0.0 

    def __init__ ( self ):
        self.CSGIR = machine.Pin( CSGIR_MAG, machine.Pin.OUT )  
        self.CSELE = machine.Pin( CSELE_MAG, machine.Pin.OUT ) 
        self.CLK   = machine.Pin( CLK_MAG  , machine.Pin.OUT ) 
        self.DOX   = machine.Pin( DOX_MAG  , machine.Pin.IN  )

    def _read( self, CSn : machine.Pin ) -> bytearray: 
        ret_bytes : int = 0
        CSn.high()              # CSn High para iniciar
        time.sleep(0.0005)      # 500ns
        CSn.low()               # CSn Low para iniciar a transferencia
        time.sleep(0.0005)      
        self.CLK.low()          # Clock Low para iniciar 
        
        # Clocking 
        for _ in range(16):
            self.CLK.high()     
            time.sleep(0.0005) 
            # Monta a sequência de 16 bits 
            ret_bytes = (ret_bytes<<1)+1 if self.DOX.value() else (ret_bytes<<1)+0 
            self.CLK.low()   
            time.sleep(0.0005)
        return ret_bytes 
    
    def _checksum(self, bits : int, parity_even : bool = True ) -> bool : 
        sum = 0 
        for bit in range(16): 
            sum += 1 if (1<<bit) & bits else 0 
        return True if sum%2 == (0 if parity_even else 1) else False  

    def _getStatus(self, status : int ):
        self.OCF    = 1 if (status & self.OCF_MASK)    is True else 0   
        self.COF    = 1 if (status & self.COF_MASK)    is True else 0   
        self.LIN    = 1 if (status & self.LIN_MASK)    is True else 0   
        self.MagINC = 1 if (status & self.MagINC_MASK) is True else 0   
        self.MagDEC = 1 if (status & self.MagDEC_MASK) is True else 0   
        self.CHK    = 1 if (status & self.CHK_MASK)    is True else 0   

    def _checkStatus(self):
        if self.OCF:
            if not self.COF:
                if not self.LIN: 
                    return True 
                else:               
                    print("Out of linear operation - Data may be wrong")
                    return True 
            else:                   
                print( "Magnet out of range - Data invalid" ) 
                return False 
        else:                       
            print( "Corrupted data")
            return False 

    def get_gir(self) -> float : 
        bits   = self._read( self.CSGIR )  
        if self._checksum(bits):
            angle_bits  = (bits & self.ANG_MASK)>>6  
            status = bits & self.STATUS_MASK 
            self._getStatus( status )
            if self._checkStatus():
                angle = angle_bits*360/2**10 
                return angle

    def get_ele(self) -> float : 
        bits = self._read( self.CSGIR )  
        if self._checksum(bits):
            angle_bits  = (bits & self.ANG_MASK)>>6  
            status = bits & self.STATUS_MASK 
            self._getStatus( status )
            if self._checkStatus():
                angle = angle_bits*360/2**10 
                return angle

    def get_angles(self) -> list : 
        gir = self.get_gir()
        ele = self.get_ele()
        return [gir, ele]


