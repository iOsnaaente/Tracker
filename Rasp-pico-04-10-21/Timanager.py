from FileStatements import *
from StepMotors     import * 
from SunPosition    import *
from Const          import *
from DS3231         import *


class Timemanager: 
    # L = Last   
    L_AZIMUTE  = 0 
    L_ALTITUDE = 0
    # A = Atual 
    A_AZIMUTE  = 0 
    A_ALTITUDE = 0 
    # D = Differential 
    D_AZIMUTE  = 0 
    D_ALTITUDE = 0 
    
    DS     : DS3231 = 0  
    MOTORS : Motors = 0 
    TIME   : list   = 0 
    LOC    : list   = 0 


    '''
    FUNÇÃO MOVE
    '''
    def move (self, gir, ele, tem = 2 ):
        if abs(gir) > 0.001 or abs(ele) > 0.001 : 
            self.MOTORS.move( gir, ele, tem )
            #self.print() 

    '''
    MOVE TO
    '''
    def move_to( self, POS : list ) -> None : 
        self.L_AZIMUTE, self.L_ALTITUDE = [ float(s2f) for s2f in file_readlines( FILE_PATH, FILE_READ ) ] 
        self.A_AZIMUTE, self.A_ALTITUDE = POS 

        D_AZIMUTE_HO = abs( self.A_AZIMUTE - self.L_AZIMUTE) 
        D_AZIMUTE_AH = abs( (360-self.A_AZIMUTE) + self.L_AZIMUTE)
       
        self.D_AZIMUTE    = D_AZIMUTE_HO  if D_AZIMUTE_HO < D_AZIMUTE_AH   else D_AZIMUTE_AH 
        self.D_ALTITUDE   = (self.A_ALTITUDE-self.L_ALTITUDE)
        
        self.L_AZIMUTE, self.L_ALTITUDE =  self.A_AZIMUTE , self.A_ALTITUDE
        file_write( FILE_PATH, "%3.10f\n%3.10f"%(self.A_AZIMUTE, self.A_ALTITUDE), 0, FILE_WRITE )
        
        self.move( -self.D_AZIMUTE, -self.D_ALTITUDE, 10 )


    '''
    CONSTRUTOR
    '''
    def __init__(self, DS : DS3231, MOTORS : Motor ) -> None:
        
        self.DS     = DS 
        self.MOTORS = MOTORS 
        self.TIME   = self.DS.now()
        self.LOC    = [ LATITUDE, LONGITUDE, TEMPERATURE, PRESSURE ]
        
        self.S_rise, self.S_set = get_twilights( self.LOC, self.TIME )
        self.S_tot = (self.S_set[3]*3600 + self.S_set[4]*60 + self.S_set[5]) - (self.S_rise[3]*3600 + self.S_rise[4]*60 + self.S_rise[5])
        self.S_tot /= 60*5
        self.M =  self.S_tot // 60
        self.S = (self.S_tot  % 60) // 1
        self.NEW_TIME = self.S_rise
    
    '''
    PRIMEIRA CHAMADA DA CLASSE
    '''
    def start(self, TIME ) : 
        
        self.TIME = TIME 
        
        self.L_AZIMUTE , self.L_ALTITUDE = [ float(s2f) for s2f in file_readlines( FILE_PATH, FILE_READ ) ]
        
        D_AZIMUTE_HO = abs( self.A_AZIMUTE - self.L_AZIMUTE) 
        D_AZIMUTE_AH = abs( (360-self.A_AZIMUTE) + self.L_AZIMUTE)
       
        self.D_AZIMUTE    = D_AZIMUTE_HO  if D_AZIMUTE_HO < D_AZIMUTE_AH   else D_AZIMUTE_AH 
        self.D_ALTITUDE   = (self.A_ALTITUDE-self.L_ALTITUDE)

        self.A_AZIMUTE , self.A_ALTITUDE = compute( self.LOC, self.TIME )
        self.D_AZIMUTE , self.D_ALTITUDE = self.L_AZIMUTE - self.A_AZIMUTE, self.L_ALTITUDE - self.A_ALTITUDE
        self.L_AZIMUTE, self.L_ALTITUDE  =  self.A_AZIMUTE , self.A_ALTITUDE
        
        file_write( FILE_PATH, "%3.10f\n%3.10f"%(self.L_AZIMUTE, self.L_ALTITUDE), 0, FILE_WRITE )
        
        print( "Movendo: Azi( {} ) e Alt( {} )".format( self.D_AZIMUTE, self.D_ALTITUDE) )
        self.move( self.D_AZIMUTE , self.D_ALTITUDE , 10 )


    '''
    UPDATE
    '''
    def update( self, TIME ): 
        self.TIME = TIME 
        self.L_AZIMUTE, self.L_ALTITUDE = [ float(s2f) for s2f in file_readlines( FILE_PATH, FILE_READ ) ] 
        self.A_AZIMUTE, self.A_ALTITUDE = compute( self.LOC, self.TIME )
        
        D_AZIMUTE_HO = abs( self.A_AZIMUTE - self.L_AZIMUTE) 
        D_AZIMUTE_AH = abs( (360-self.A_AZIMUTE) + self.L_AZIMUTE)
       
        self.D_AZIMUTE    = D_AZIMUTE_HO  if D_AZIMUTE_HO < D_AZIMUTE_AH   else D_AZIMUTE_AH 
        self.D_ALTITUDE   = (self.A_ALTITUDE-self.L_ALTITUDE)
        
        self.L_AZIMUTE, self.L_ALTITUDE =  self.A_AZIMUTE , self.A_ALTITUDE
        file_write( FILE_PATH, "%3.10f\n%3.10f"%(self.A_AZIMUTE, self.A_ALTITUDE), 0, FILE_WRITE )
        
        self.move( -self.D_AZIMUTE, -self.D_ALTITUDE, 10 )


    def get_azimute(self):
        return self.L_AZIMUTE

    def get_altitude(self):
        return self.L_ALTITUDE


    '''
    PRINT
    '''
    def print(self):
        print( "\n" )
        print( "AZIMUTE (A\D):\t{:2.4f}\t\t{:2.4f}".format( self.A_AZIMUTE , self.D_AZIMUTE ) ) 
        print( "ALTITUDE (A\D):\t{:2.4f}\t\t{:2.4f}".format( self.A_ALTITUDE, self.D_ALTITUDE) )
        print( "Data:\t\t{}/{}/{}\t\tHora:\t\t{}:{}:{}".format(self.TIME[0],self.TIME[1],self.TIME[2],self.TIME[3],self.TIME[4],self.TIME[5]) )
        print( "Azimute:\t{:2.3f}\t\tAltitude:\t{:2.3f}".format(self.L_AZIMUTE, self.L_ALTITUDE), end='\n\n' )
        
        
    def up_fake_time(self, up = False ):
        global NEW_TIME
        global S_tot
        global S
        global M
        
        if up :
            S_rise, S_set = get_twilights( self.LOC, self.TIME )
            S_tot = (S_set[3]*3600 + S_set[4]*60 + S_set[5]) - (S_rise[3]*3600 + S_rise[4]*60 + S_rise[5])
            S_tot /= 60*5
            M =  S_tot // 60
            S = (S_tot  % 60) // 1
            NEW_TIME = S_rise

        NEW_TIME[5] += S
        NEW_TIME[4] += M
        if NEW_TIME[5] >= 60:
            NEW_TIME[5] %= 60
            NEW_TIME[4] += 1
        if NEW_TIME[4] >= 60:
            NEW_TIME[4] %= 60
            NEW_TIME[3] += 1
            if NEW_TIME[3] >= 24:
                NEW_TIME[3] = 0
                NEW_TIME[2] += 1
                if NEW_TIME[1] == 2: 
                    if ANB(NEW_TIME[0]) :  DOM[1] = 29 
                    else:                  DOM[1] = 28 
                if NEW_TIME[2] > DOM[NEW_TIME[1]]:
                    NEW_TIME[2] = 1 
                    NEW_TIME[1] += 1
                    if NEW_TIME[1] > 12: 
                        NEW_TIME[1] = 1
                        NEW_TIME[0] += 1
                        
        NEW_TIME = [ int(d) for d in NEW_TIME ]
        return NEW_TIME 

