from dearpygui.dearpygui import *

from math   import e , factorial, sqrt, pi 
from serial import Serial 

from .menuAtuadores import *


def resize_sensores(): 
    new_w, new_h = get_item_width(1_0), get_item_height(1_0)
    configure_item( 7_1_0, width=new_w*0.65   , height=new_h*0.4  , pos=[10, 25]            )
    configure_item( 7_2_0, width=new_w*0.65   , height=new_h*0.4  , pos=[10, new_h*0.4+30]  )
    configure_item( 7_3_0, width=new_w*0.65   , height=new_h*0.2-40, pos=[10, new_h*0.8+35] )
    configure_item( 7_4_0, width=new_w*0.35-20, height=new_h-30    , pos=[new_w*0.65+15,25] )

    configure_item( 7_1_1, width=new_w*0.639   , height=new_h*0.375 )
    configure_item( 7_2_1, width=new_w*0.639   , height=new_h*0.375 )


def att_CMD_Sensores( COMP : Serial ):
    global CONNECTED
    global buff_count
    global buff_bytes 
    global buff_in 

    if CONNECTED:    
        try:
            read = COMP.read( get_nBytes( COMP ) )
            if len(read) > 3: 
                buff_in.append( '[{}] '.format( buff_count ) + str(read.decode()) ) 
                buff_bytes  = read 
                buff_count += 1

                if len(buff_in) > 2: 
                    buff_in.pop(0)
        except:
            pass 
        aux = ''
        for i in buff_in:
            aux += i + '\n'  
        configure_item( 7_3_1, default_value = aux )
    else: 
        buff_count = 0 
        buff_in    = []
        configure_item( 7_3_1, default_value = 'DESCONECTADO...' )
    

def init_sensores( windows : dict ):       

    with window(id=7_1_0, no_title_bar=True, no_move=True, no_resize=True, no_close=True, no_collapse=True) as WinPltM1:
        windows['Sensores'].append(WinPltM1)
        with plot(id=7_1_1, label="Sensor do Motor 1 (Giro)", width=700, height=200, anti_aliased=True ) :
            add_plot_legend()
            add_plot_axis(mvXAxis, label="Tempo (h)", id='gx_axis')
            add_plot_axis(mvYAxis, label="Graus (º)", id="gy_axis")
            set_axis_limits("gx_axis", 0, 100)
            set_axis_limits('gy_axis', 0, 360)
            add_line_series([i for i in range(100)], [ (360)*(0.75**i)*(1-0.75)**(1-0.75) for i in range(1, 100+1) ], label="Bernoulli", id="GX_value", parent="gy_axis")
            add_line_series([i for i in range(100)], [ (3600)*((e**(-50))*50**i)/factorial(i)   for i in range(1, 100+1) ] , label="Poison" , id="GY_value", parent="gy_axis")



    with window(id=7_2_0,  no_title_bar=True, no_move=True, no_resize=True, no_close=True, no_collapse=True) as WinPltM2:
        windows['Sensores'].append(WinPltM2)
        with plot( id=7_2_1, label="Sensor do Motor 2 (Giro)", width=700, height=200, anti_aliased=True) :
            add_plot_legend()
            add_plot_axis(mvXAxis, label="Tempo (h)", id='ex_axis')
            add_plot_axis(mvYAxis, label="Graus (º)", id="ey_axis")
            set_axis_limits("ex_axis", 0, 100)
            set_axis_limits('ey_axis', 0, 370)
            add_line_series([i for i in range(100)], [ (360*20)*(1/(10*sqrt(2*pi)))*e**(-((i-50)**2)/(2*10**2)) for i in range(1, 100+1) ], label="Gauss", id="EX_value", parent="ey_axis")
            add_line_series([i for i in range(100)], [ 350/(1+e**(-i))   for i in range(1, 100+1) ]           , label="Sigmoidal" , id="EY_value", parent="ey_axis")


    with window(id=7_3_0, no_title_bar=True, no_move=True, no_resize=True, no_close=True, no_collapse=True) as WinPltMx:
        windows['Sensores'].append(WinPltMx)
        add_text('Log dos sensores (Rasp)')
        add_text( id = 7_3_1, default_value = 'DESCONECTADO!')



    with window(id=7_4_0, no_close=True, no_move=True, no_resize=True, no_title_bar=True, no_collapse=True ) as Comandos: 
        windows['Sensores'].append(Comandos)
        add_text('Configurações')

        



def render_sensores() : 
    pass 