from SunPosition import * 
from myNumpy import *

'''
compute_all_day gera uma lista de aproximação do azimute e altitude do dia::
    >>> Location : list -> substitui a classe Location onde estão as coordenadas de 
    latitude, longitude, temperatura e pressão atmosférica
    >>> Time : list -> substitui a classe Time onde estão as informações de data e hora.
    Para a computação da aproximação são necessárias somente as informações de dd/mm/yyyy
    >>> ratio : int -> proporção de dados para serem computados ( padrão == 5 : 20%) 
    >>> yield [ sunrise, sunset]
    >>> yield alt
    >>> yield azi 

'''
def compute_all_day( Location : list, Time : list, ratio : int = 5 ) -> list:
    # Zera hh:mm:ss para fazer a contagem da hora zero 
    Time[3:-1] = 0,0,0  
    
    azi = []
    alt = []
    dat = []
    
    rising = [] 
    sunset = []

    while True: 
        azi_alt  = compute( Location, Time, useNorthEqualsZero= False  )
        # verifica se a altitude é maior que zero ( se o sol esta acima do horizonte )
        if azi_alt[1] > 0 :
            dat.append( Time[3] + Time[4]/60 + Time[5]/3600 )
            azi.append( abs(azi_alt[0]) if azi_alt[0] < 0 else 360-azi_alt[0]   )
            alt.append( azi_alt[1] )

            # Verifica a primeira e a ultima medição de sol acima do horizonte do dia ( sunrise, sunset )
            if rising == []:
                rising = [ t for t in Time ]
            sunset = [ t for t in Time ] 

        Time[4] += 10
        if Time[4] >= 60: 
            Time[4] = 0
            Time[3] += 1 
            if Time[3] >= 24:
                break
       
    yield [ rising, sunset ]
    
    dat  = [ dat[i] for i in range(len(dat)) if i%ratio == 0 ]
    alt  = [ alt[i] for i in range(len(alt)) if i%ratio == 0 ]
    alt = get_aprox( dat, alt )
    yield alt
    
    azi  = [ azi[i] for i in range(len(azi)) if i%ratio == 0 ]
    azi = get_aprox( dat, azi )
    yield azi 
