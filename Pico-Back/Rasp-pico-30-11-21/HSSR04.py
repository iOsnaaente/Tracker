import machine
import utime

# Bruno Gabriel Flores Sampaio 

class HCSR04:
    def __init__(self, TRIG : int = 18, ECHO : int = 0 ) -> None:
        self.TRIG = machine.Pin( TRIG, machine.Pin.OUT )
        self.ECHO = machine.Pin( ECHO, machine.Pin.IN  )
    
    def get_dist(self) -> float :            
        # Dispara o 'Trigger' # [ Alto, sleep(t), baixo ] = pulso quadrado de comprimento t  
        self.TRIG.high()
        utime.sleep(0.0001)
        self.TRIG.low()
        
        # Enquanto não pegar o sinal de retorno 
        while self.ECHO.value() == 0:
            start_t = utime.ticks_us()
        # Quando pega o retorno calcula os tempos de ida e volta 
        while self.ECHO.value() == 1:
            final_t = utime.ticks_us()
        
        dt  = final_t - start_t
        distancia = (dt * 0.0343) / 2
        return distancia
    
    def print_dist(self) -> None:
        print( "Distancia: ", self.get_dist() ,"cm" )


hc = HCSR04( TRIG = 18, ECHO = 0 )
ld = machine.Pin(25, machine.Pin.OUT )

while True:
    hc.print_dist()
    ld.toggle()
    



