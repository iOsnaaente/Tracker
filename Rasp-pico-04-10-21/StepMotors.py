from time    import sleep_ms
from machine import Pin

BACKWARD = False
FORWARD  = True

DISABLE = 1 
ENABLE  = 0

class Motor: 
    
    direction = FORWARD
    torque    = ENABLE

    position  = 0.0 
    ratio     = 1.0 
    step      = 1.8
    u_step    = 16 
    nano_step = 0.0
    name = '' 

    # Para ter 30rpm durante 1 segundo
    rpm       = 0 
    pps       = 800  

    def __init__(self, STEP_PIN : int, DIRECTION_PIN : int, ENABLE_PIN : int, TORQUE : bool = False ) -> None:
        self.STEP_PIN       = Pin( STEP_PIN, Pin.OUT ) 
        self.DIRECTION_PIN  = Pin( DIRECTION_PIN, Pin.OUT )
        self.ENABLE_PIN     = Pin( ENABLE_PIN, Pin.OUT )

        self.direction      = FORWARD
        self.torque         = ENABLE if TORQUE else DISABLE 
        self.ENABLE_PIN.value( self.torque )
        
        self.step   = 1.8
        self.u_step = 8 
        self.ratio  = 1

    def configure(self, step : float = 1.8, u_step : int = 8, ratio : float = 1) -> None: 
        self.step   = step
        self.u_step = u_step 
        self.ratio  = ratio 

    def set_torque( self, torque : bool = ENABLE ) -> None:
        self.torque = ENABLE if torque else DISABLE 
        self.ENABLE_PIN.value( self.torque )
    
    def set_name(self, name):
        self.name = name 

    def set_velocity( self, rpm : int = 1 ) -> None:
        self.pps = int( ( rpm * 360 * ( self.u_step // self.step ) )/( 60 * self.step ))
        self.rpm = rpm 
    
    def set_direction( self, direction : bool ) -> None:
        self.direction = FORWARD if direction else BACKWARD
        self.DIRECTION_PIN.value( 1 if self.direction == FORWARD else 0 ) 
    
    def _pulse(self, time_spend : int = 2 ) -> None :
        self.STEP_PIN.high()
        sleep_ms ( time_spend//2 )
        self.STEP_PIN.low()
        sleep_ms ( time_spend//2 )
        
    def move( self, n_pulses : int, time_stemp : int = 10 ) -> None:  
        if self.torque == DISABLE: 
            self.ENABLE_PIN.low() 
            for _ in range( n_pulses ):
                self._pulse( time_stemp )
            self.ENABLE_PIN.high() 
        else:
            for i in range( n_pulses ):
                self._pulse( time_stemp )
        
        if self.direction: self.position += self.step / (self.u_step * self.ratio)  
        else:              self.position -= self.step / (self.u_step * self.ratio)

        if   self.position > 360.0: self.position -= 360.0
        elif self.position < 0:     self.position = 360 - self.position 

    def get_num_pulses(self, angle : int) -> int:
        n_pulso = ((angle*self.u_step)/self.step)*self.ratio
        self.nano_step += n_pulso % 1
        n_pulso = int( n_pulso // 1 )
        
        if self.nano_step > 1.0 :
            self.nano_step -= 1  
            n_pulso += 1
            
        print(self.name, "\tNumero de pulsos : ", n_pulso, "\tNano pulso: ", self.nano_step, "\tGraus: ", angle, "º" )
        return n_pulso

class Motors:
    GIR_POS = 0
    ELE_POS = 0 

    def __init__(self, gir_stp : Pin, gir_dir : Pin, ele_stp : Pin, ele_dir : Pin, enb_motors : Pin ):
        self.GIR = Motor ( gir_stp, gir_dir, enb_motors )
        self.GIR.set_name("Gir/Azimute")
        self.ELE = Motor ( ele_stp, ele_dir, enb_motors )
        self.ELE.set_name("Ele/Altitude" )
    
    def configure(self, MOTOR : Motor, pos : float, step : float, micro_step : int, ratio : float ) -> None:
        MOTOR.u_step = micro_step 
        MOTOR.ratio  = ratio
        MOTOR.step   = step 
        MOTOR.pos    = pos 

    def set_torque(self, state : bool ) -> None :  
        self.GIR.torque = ENABLE if state else DISABLE
        self.GIR.ENABLE_PIN.value( self.GIR.torque )
        self.ELE.torque = ENABLE if state else DISABLE
        self.ELE.ENABLE_PIN.value( self.GIR.torque )

    def get_positions(self):
        return [ self.GIR.position, self.ELE.position ]

    def move(self, g_ang : int, e_ang : int, time_stemp : int = 2 ) -> None :
        if   g_ang < 0:   self.GIR.set_direction( BACKWARD )
        elif g_ang > 0:   self.GIR.set_direction( FORWARD  )
        
        if   e_ang < 0:   self.ELE.set_direction( BACKWARD ) 
        elif e_ang > 0:   self.ELE.set_direction( FORWARD  )
        
        g_pulses = self.GIR.get_num_pulses( abs(g_ang) )
        e_pulses = self.ELE.get_num_pulses( abs(e_ang) )
        
        for i in range( g_pulses if g_pulses > e_pulses else e_pulses ):
            if g_pulses > 0: 
                self.GIR.move( 1, time_stemp )
                g_pulses -= 1
            if e_pulses > 0 : 
                self.ELE.move( 1, time_stemp )
                e_pulses -= 1
                
        self.GIR_POS, self.ELE_POS = self.get_positions()
