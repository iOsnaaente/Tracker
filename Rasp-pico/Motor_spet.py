
from time import sleep_ms
from machine import Pin

class Motor: 
    
    direction = True
    position  = 0.0 
    torque    = False

    ratio     = 0.0 
    step      = 0.0 
    u_step    = 1

    def __init__(self, step : int, dir : int, enable : int ) -> None:
        self.pin_step       = Pin( step, Pin.OUT ) 
        self.pin_direction  = Pin( dir, Pin.OUT )
        self.pin_enable     = Pin( enable, Pin.OUT )
    
    def enable_torque( self, torque : bool ) -> None: 
        self.pin_enable.value( not torque )
        self.torque = torque 
   
    def _pulse(self, time_spend : int ) -> None :
        self.pin_step.high()
        sleep_ms ( time_spend//2 )
        self.pin_step.low()
        sleep_ms ( time_spend//2 )
    
    def direction( self, direction : bool ) -> None :
        self.pin_direction.value( direction )
        self.direction = direction 
    
    def set_direction( self, name : str ) -> None:
        if name == 'FORWARD':
            self.pin_direction.value( True ) 
            self.direction = True 
        elif name == 'BACKWARD':
            self.pin_direction.value( False )
            self.direction = False
        else:
            print("Parametro de direção inválido")

    def move( self, num_pulses : int, vel : int = 1) -> None:
        if not self.torque: 
            for i in range( num_pulses ):
                self.pin_enable.value( False )
                self._pulse( vel )
                self.pin_enable.value( True )
        else:
            for i in range( num_pulses ):
                self._pulse( vel )
        
        if self.direction: self.position += self.step / (self.u_step * self.ratio)  
        else:              self.position -= self.step / (self.u_step * self.ratio)
            
        if   self.position > 360.0: self.position -= 360.0
        elif self.position < 0:     self.position = 360 - self.position 


class Motors:
    GIR_POS = 0 
    GIR_VEL = 0
    ELE_POS = 0 
    ELE_VEL = 0 

    def __init__(self, gir_stp : Pin, gir_dir : Pin, gir_enb : Pin, ele_stp : Pin, ele_dir : Pin, ele_enb : Pin ):
        self.GIR = Motor( gir_stp, gir_dir, gir_enb )
        self.ELE = Motor( ele_stp, ele_dir, ele_enb )
    
    def configure(self, MOTOR : Motor, pos : float, step : float, micro_step : int, ratio : float ) -> None:
        MOTOR.pos    = pos 
        MOTOR.step   = step 
        MOTOR.u_step = micro_step 
        MOTOR.ratio  = ratio

    def move(self, gir_num : int, gir_dir : bool, ele_num : int, ele_dir : bool ) :
        self.GIR.set_direction( gir_dir )
        self.ELE.set_direction( ele_dir )
        for i in range( gir_num if gir_num > ele_num else ele_num ):
            if ( gir_num > 0 ) :
                self.GIR.move( 1 )
                gir_num -= 1
            if ( ele_num > 0 ) :
                self.ELE.move( 1 )
                ele_num -= 1

    def enable_torque(self, name : str, state : bool ) -> None :
        if name == 'GIR': 
            self.GIR.enable_torque( state )
        elif name == 'ELE':
            self.ELE.enable_torque( state )
        else:
            print( 'torque_enable: Name not found ( use "Gir" or "ELE" )') 
        
    


