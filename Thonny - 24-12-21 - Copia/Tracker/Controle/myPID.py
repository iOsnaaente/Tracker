from time import ticks_ms

class PID:
        
    ActualMeasure = 0
    LastMeasure   = 0
    
    Error_rounded = 0
    Error_real = 0
    
    PV = 0
    
    Kp = 0.75
    Ki = 0.55
    Kd = 0.00
    
    dto = 0
    dti = 0
    dt  = 0 

    def __init__( self, PV : float, Kp : float, Kd : float, Ki : float ):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.PV = PV 
    
    @property 
    def pid( self ):
        return (self.Kp*self.Error_rounded) + (self.Ki*((self.ActualMeasure-self.LastMeasure)*self.dt/2)) + (self.Kp*self.Kd*(self.Error_rounded/self.dt)*self.ActualMeasure)
    
    def att(self, measure : float ):
        self.LastMeasure = self.ActualMeasure
        self.ActualMeasure = measure
        self.dto = ticks_ms()
    
    def compute(self, measure, tol : float = 0.25 ):
        
        self.Error_real    = abs( self.PV - measure )
        self.Error_rounded = 0 if round( self.Error_real, 1 ) < tol else self.Error_real 
        self.LastMeasure   = self.ActualMeasure 
        
        self.dti = ticks_ms()
        self.dt  = self.dti - self.dto 
        self.dto = self.dti
        
        if self.PV < measure:
            op1 = 360 - measure + self.PV
            op2 = self.PV - measure 
        else: 
            op1 = measure + 360 - self.PV 
            op2 = measure - self.PV 
        
        return self.pid if op1 < op2 else -self.pid
        
