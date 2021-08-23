from dearpygui.dearpygui import *
from utils.serial_reader import serialPorts 
from utils.Model         import SunPosition
from win32api            import GetSystemMetrics
from serial              import Serial
from struct              import unpack
from struct              import pack

import datetime as dt 
import ephem
import math 
import sys 
import os 

cos = lambda x : math.cos( x )
sin = lambda x : math.sin( x )
tg  = lambda x : math.tan( x )

COMP : Serial = Serial() 
PATH = os.path.dirname( __file__ )

LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 425
UTC_HOUR  = -3
DOM       = [ 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro' ]

sun_data  = SunPosition( LATITUDE, LONGITUDE, ALTITUDE )
sun_data.update_date()


color = {
    "black"   : lambda alfa : [   0,   0,   0, alfa ],
    "red"     : lambda alfa : [ 255,   0,   0, alfa ],
    "yellow"  : lambda alfa : [ 255, 255,   0, alfa ],
    "green"   : lambda alfa : [   0, 255,   0, alfa ],
    "ciano"   : lambda alfa : [   0, 255, 255, alfa ],
    "blue"    : lambda alfa : [   0,   0, 255, alfa ],
    "magenta" : lambda alfa : [ 255,   0, 255, alfa ],
    "white"   : lambda alfa : [ 255, 255, 255, alfa ],
    'gray'    : lambda alfa : [ 155, 155, 155, alfa ],
    'orange'  : lambda alfa : [ 255,  69,   0, alfa ],}


CONNECTED     = False

DAY_2Compute  = 0.0 

MGSR_Angle    = 0.0 
MESR_Angle    = 0.0 

SERIAL_INFO   = [ ]
buff_in       = [ ]
buff_bytes    = b''
BUFF_MAX      = 30 
buff_count    = 0

def get_nBytes( comp : Serial ): 
    if comp.isOpen():
        return comp.inWaiting()  
    else:
        print( 'COMP fechada ')

def send_msg( comp : Serial, msg : str ):
    for s in msg:
        comp.write( s ) 

def att_comData(comp : Serial ):
    DATA = receive_msg( comp )
    if DATA : 
        return DATA  

def att_CMD_Pico( COMP : Serial ):
    global CONNECTED
    global buff_count
    global buff_bytes 
    global buff_in 

    if CONNECTED:    
        try:
            read = COMP.read( get_nBytes( COMP ) )
            if len(read) > 3: 
                buff_in.append( '[{}] '.format( buff_count ) + str(read) ) 
                buff_bytes  = read 
                buff_count += 1

                if len(buff_in) > BUFF_MAX: 
                    buff_in.pop(0)
        except:
            pass 
        aux = ''
        for i in buff_in:
            aux += i + '\n'  
        configure_item( 46_2_1_1, default_value = aux )
    else: 
        buff_count = 0 
        buff_in    = []
        configure_item( 46_2_1_1, default_value = 'DESCONECTADO...' )
    
def att_Serial_Pico( COMP : Serial ):
    global MGSR_Angle 
    global MESR_Angle
    global SERIAL_INFO
    global CONNECTED
    global buff_count   
    global buff_bytes

    if CONNECTED:
        if b'INIT' in buff_bytes:
            DATA = buff_bytes.split(b'INIT')
            if len(DATA) == 2:
                DATA = DATA[1]
                if DATA != b'':
                    LENG = DATA[0]
                    if LENG == 27:
                        try:
                            AZI, ALT    = unpack( 'ff', DATA[1:9]   )
                            GIR, ELE    = unpack( 'ff', DATA[9:17]  )
                            TIME_D      = [ b for b  in DATA[18:21] ]
                            TIME_H      = [ b for b  in DATA[21:24] ]
                            SERIAL_INFO = [ [AZI, ALT], [GIR, ELE], TIME_D, TIME_H ]
                        except:
                            pass 
                    try: 
                        AUX = '%s de %s de %s\n\n' %( TIME_D[2], DOM[TIME_D[1]], TIME_D[0])
                        AUX += '%s/%s/%s' % ( TIME_D[2], TIME_D[1], TIME_D[0])
                        AUX += '  -  %s:%s:%s' % ( TIME_H[0], TIME_H[1], TIME_H[2] )
                        AUX += '\n\n\nPOSIÇÃO DO SOL CALCULADO:\n'
                        AUX += '\nAZIMUTE:  %.2fº' % AZI 
                        AUX += '\nALTITUDE: %.2fº' % ALT 
                        AUX += '\n\n\nPOSIÇÃO DOS MOTORES:\n'
                        AUX += '\nMOTOR DE GIRO:     %.2fº\n' % GIR 
                        AUX += 'MOTOR DE ELEVAÇÃO: %.2fº\n' % ELE

                        MGSR_Angle = GIR 
                        MESR_Angle = ELE 

                        configure_item( 46_1_1_1, default_value = AUX )

                        show_item( 44_1_9)        
                        w, h = [ get_item_width(44_1_0)/2, get_item_height(44_1_0)/2 ]     
                        r    = (w/2)*1.25 if w < h else (h/2)*1.25 
                        configure_item( 44_1_9, p1 =  [w + r*cos(math.radians(MGSR_Angle)+math.pi*3/2), h + r*sin( math.radians(MGSR_Angle)+math.pi*3/2)]  )
                    
                        w, h = get_item_width(zenite_config_AT), get_item_height(zenite_config_AT)
                        r    = w//1.3 if w < h else h//1.3
                        show_item( 45_1_7 )
                        configure_item( 45_1_7, p1 = [ 100 + r*cos(math.radians(MESR_Angle)), 10+r*(1-sin(math.radians(MESR_Angle)))])
                        

                    except:
                        pass 
    else: 
        configure_item( 46_1_1_1, default_value = 'DESCONECTADO...' )
        hide_item( 45_1_7 )
        hide_item( 44_1_9)


def send_serial():
    global MG_Angle 
    global ME_Angle 

    #msg = b'SENDM' + bytes(chr(8)) + 
    msg  = b'SENDM'
    msg += bytes( [0x08] )  
    msg += pack('ff', MG_Angle, ME_Angle )
    send_msg( COMP, msg )

# Main Window 
with window( label = 'Main Window', id = 1_0, autosize = True ) as main_window:
    pass 

# Serial Config 
with window( label = 'Serial'     , id = 42_0, width= 455, height= 330, pos = [10,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as serial_AT: 

    add_spacing(count=2)
    add_text('CONFIGURAÇÕES DE COMUNICAÇÃO')

    # FAZER UMA THREAD PARA ESCUTAR NOVAS CONEXÕES SERIAIS 
    add_text('Selecione a porta serial: ')
    add_combo( id=42_1, default_value='COM16', items= ['COM1', 'COM4', 'COM15', 'COM16'] )
    add_same_line( )

    def SR_refresh():
        seriais = serialPorts( lenght = 20 )
        configure_item( 42_1, items = seriais )

    add_button( label='Refresh', callback= SR_refresh )

    add_spacing( count= 1 )

    add_text('Baudarate: ')
    add_combo( id=42_2, default_value= '115200', items=[ '9600', '57600', '115200'] )
    add_spacing( count= 1 )

    add_text('Timeout: ')
    add_input_int( id=42_3, default_value= 1)
    add_spacing( count= 5 )


    def SR_try_connect( sender, data, user): 
        global CONNECTED
        global COMP 
        SR_Port      = get_value( 42_1   )
        SR_Baudrate  = get_value( 42_2   )
        SR_Timeout   = get_value( 42_3   )  

        # CORRIGIR PARA QUE NÃO FECHE A MESMA COMP
        if COMP.isOpen():
            COMP.close()
        try: 
            COMP = Serial( port = SR_Port, baudrate = SR_Baudrate, timeout = SR_Timeout )
            show_item( 42_6 )
            CONNECTED = True 
        except:
            hide_item( 42_6 )
            CONNECTED = False 

    add_button(label='Iniciar conexão##AT',  id=42_4, callback= SR_try_connect )
    add_same_line()
    add_button(label="DESCONECTAR ?", width=150, id = 42_6, callback= lambda : hide_item(42_6) if not COMP.close() else 1 )
    hide_item( 42_6) 
    add_spacing(count= 3)

    with child( id=42_5_0, autosize_x= True, autosize_y= True, no_scrollbar=True, border= True ):
        add_text( 'Data Calculada:' )
        add_text( id = 42_5_1, default_value='No data')
        add_button(label="Atualizar", width=100, id = 42_5_2, callback= lambda : set_value( 42_5_1, str(dt.datetime.now().strftime('%A %d/%m/%Y - %H:%M:%S')) ) if sun_data.update_date() == None else 1 )
        add_same_line()
        add_button(label="Limpar", width=100, id = 42_5_3, callback= lambda : set_value( 42_5_1, 'No data' ) )

# Step Motors Config 
with window( label = 'Motores'    , id = 43_0, width= 455, height= 480, pos = [10,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as config_AT:

    # DEFNIÇÃO DOS MOTORES INDIVUDUAIS 
    add_text('DEFINIÇÃO DOS MOTORES DE PASSO')
    
    with child( id=43_1_0, label = 'MotorGiro##AT', width= get_item_width( config_AT )-15, height= 200):
        add_text("Motor de Rotação da base - Motor 1")
        add_spacing(count=2)
        add_text('Resolução:')
        add_input_float( id=43_1_1, label='ResoluçãoM1##AT', default_value= 1.8, format= '%3.2f', callback= lambda sender, data : set_value('PassosM1##AT', value= (360/get_value('ResoluçãoM1##AT') if get_value('ResoluçãoM1##AT') > 0 else 0 ) ) )
        add_spacing(count=2)

        add_text('Passos por volta:')
        add_drag_float( id=43_1_2, label='PassosM1##AT', default_value=  360 / 1.8, format='%5.2f', no_input= True )
        add_spacing(count= 2)
        add_text('Micro Passos do motor:')
        add_combo( id=43_1_3, label='MicroPassosM1##AT', default_value = '1/16', items= ['1', '1/2', '1/4', '1/8', '1/16', '1/32'] )
    add_spacing(count= 2)

    with child(id=43_2_0,label = 'MotorElevação##AT',  width= get_item_width(config_AT)-15, height= 200 ):
        add_text("Motor de Rotação da base - Motor 2")
        add_spacing(count=2)
        add_text('Resolução:')
        add_input_float(id=43_2_1, label='ResoluçãoM2##AT', default_value= 1.8, format= '%3.2f', callback= lambda sender, data : set_value('PassosM2##AT', value= (360/get_value('ResoluçãoM2##AT') if get_value('ResoluçãoM2##AT') > 0 else 0 ) ) )
        add_spacing(count=2)
        add_text('Passos por volta:')
        add_drag_float(id=43_2_2, label='PassosM2##AT', default_value=  360 / 1.8, format='%5.2f', no_input= True )
        add_spacing(count= 2)
        add_text('Micro Passos do motor:')
        add_combo(id=43_2_3, label='MicroPassosM2##AT', default_value = '1/16', items= ['1', '1/2', '1/4', '1/8', '1/16', '1/32'] ) 

# Azimute Draw 
with window( label ='Azimute'     , id = 44_0, width= 495, height= 330, pos = [470,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as azimute_config_AT: 

    add_drawlist( id = 44_1_0  , width = 495, height = 330, pos = [0,-25] )
    
    w, h = [ get_item_width(44_1_0)/2, get_item_height(44_1_0)/2] 
    r    = (w/2)*1.25 if w < h else (h/2)*1.25 
    p    = 20

    draw_circle(parent = 44_1_0, id = 44_1_1, center = [ w       , h     ] , radius =  r            , color = color['white'](200), thickness = 2 )
    draw_line(  parent = 44_1_0, id = 44_1_2, p1     = [ w - r   , h     ] , p2     = [ w + r, h ]  , color = color['gray'](200) , thickness = 2 )
    draw_text(  parent = 44_1_0, id = 44_1_3, pos    = [ w - r-p , h-7.5 ] , text   = 'W'           , color = color['white'](200), size = 20     )
    draw_text(  parent = 44_1_0, id = 44_1_4, pos    = [ w + r+p , h-7.5 ] , text   = 'E'           , color = color['white'](200), size = 20     )
    draw_text(  parent = 44_1_0, id = 44_1_5, pos    = [ w -6    , h-r-p ] , text   = 'N'           , color = color['white'](255), size = 20     )

    ## RENDERIZAÇÃO
    ang_ris = sun_data.get_azi_from_date( sun_data.rising )[1] # [ alt , azi ]
    ang_set = sun_data.get_azi_from_date( sun_data.sunset )[1] # [ alt , azi ]
    draw_line(  parent = 44_1_0, id = 44_1_6, p1 = [ w, h], p2 = [w + r*cos(ang_ris-math.pi/2), h + r*sin(ang_ris-math.pi/2)], color = color['gray'](200), thickness= 2 )
    draw_line(  parent = 44_1_0, id = 44_1_7, p1 = [ w, h], p2 = [w + r*cos(ang_set-math.pi/2), h + r*sin(ang_set-math.pi/2)], color = color['gray'](200), thickness= 2 )
   
    def move_azi(sender, data, user): 
        global MG_Angle
        MG_Angle = get_value(44_2)
        w, h = [ get_item_width(44_1_0)/2, get_item_height(44_1_0)/2]     
        r    = (w/2)*1.25 if w < h else (h/2)*1.25 
        configure_item( 44_1_8, p1 = [w + r*cos(math.radians(MG_Angle)+math.pi*3/2), h + r*sin( math.radians(MG_Angle)+math.pi*3/2)] )
        send_serial()

    w,h = get_item_width(azimute_config_AT), get_item_height(azimute_config_AT)
    
    draw_arrow(  parent = 44_1_0, id = 44_1_8, p1 = [w//2 + r*cos(math.pi/2), h//2 + r*sin(math.pi/2)], p2 = [ w//2, h//2 ], color = color['yellow'](200), thickness = 2, size = 10  )
    draw_arrow(  parent = 44_1_0, id = 44_1_9, p1 = [w//2 + r*cos(math.pi/2), h//2 + r*sin(math.pi/2)], p2 = [ w//2, h//2 ], color = color['red'](200) , thickness = 2, size = 10  ) 
    hide_item( 44_1_9 )

    add_slider_float( id     = 44_2  , pos = [ w*0.025, h-50], width  = w*0.95, height = 50, min_value=0, max_value=360, indent=0.001, enabled=True, callback= move_azi )
    move_item_up(44_2)

# Zenite / Altitude Draw 
with window(label  = 'Zenite'     , id = 45_0, width= 495, height= 330, pos = [970,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as zenite_config_AT:

    def draw_semi_circle( parent, id, center, radius, angle_i, angle_f, color, segments = 360, closed = False, thickness = 1 ):
        angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
        points = [ [ center[0] + radius*cos(ang), center[1] - radius*sin(ang) ] for ang in angles ]
        draw_id = draw_polyline ( parent = parent, id = id, points = points, color= color, closed = closed, thickness= thickness )

    w, h = get_item_width(zenite_config_AT), get_item_height(zenite_config_AT)
    r    = w//1.3 if w < h else h//1.3
    pyi = 10
    pxi = 100 
    p   = 10 

    add_drawlist(     id     = 45_1_0, width  = w*0.95 , height = h*0.95         , pos = [0,0] )
    draw_polyline(    parent = 45_1_0, id     = 45_1_1 , points = [ [ pxi, pyi ] , [ pxi, pyi+r ], [ pxi + r, pyi + r ] ], color = color['white'](200), thickness= 2               )
    draw_semi_circle( parent = 45_1_0, id     = 45_1_2 , center = [ pxi, pyi + r], radius = r, angle_i = 0, angle_f = math.radians(91)  , color = color['white'](200), segments= 90, thickness= 2 )
    
    # RENDERIZAÇÃO 
    ang_transit = sun_data.get_azi_from_date( sun_data.transit )[0] # [ alt , azi ]
    ang_altitud = sun_data.alt

    draw_line( parent = 45_1_0, id = 45_1_3, p1  = [ pxi, pyi+r ], p2 = [pxi + r*cos(ang_transit), pyi+r*(1-sin(ang_transit))] , color = color['red'](200)   , thickness = 2             )
    draw_arrow(parent = 45_1_0, id = 45_1_4, p1  = [ pxi + r*cos(ang_altitud), pyi+r*(1-sin(ang_altitud))], p2 = [pxi, pyi+r]  , color = color['yellow'](200), thickness = 3, size = 10  ) 
    draw_text( parent = 45_1_0, id = 45_1_5, pos = [ w-75, pyi] , text = "Altura:"                                             , color = color['white'](255) , size = 15                 )
    draw_text( parent = 45_1_0, id = 45_1_6, pos = [ w-75, 25]  , text = str( round(math.degrees(ang_altitud)) )+'º'           , color = color['white'](255) , size = 15                 )  
    
    draw_arrow(parent = 45_1_0, id = 45_1_7, p1  = [ pxi + r*cos(0), pyi+r*(1-sin(0))], p2 = [pxi, pyi+r]  , color = color['red'](200), thickness = 3, size = 10  ) 
    hide_item( 45_1_7 )

    def move_alt( sender, data, user ):
        global ME_Angle
        ME_Angle = get_value(45_2)
        w, h = get_item_width( zenite_config_AT ), get_item_height( zenite_config_AT )
        r    = w//1.3 if w < h else h//1.3
        configure_item( 45_1_4, p1 = [ pxi + r*cos(ME_Angle), pyi+r*(1-sin(ME_Angle))] )
        configure_item( 45_1_6, text = str( round(math.degrees(ME_Angle)) )+'º' )
        send_serial( )

    add_slider_float( id = 45_2, pos=[w*0.025,h-50], width= w*0.95, min_value= 0, max_value= math.pi/2, indent = 0.01, callback= move_alt )
    move_item_up(45_2)

# General Draw 
with window( label = 'Draw_Window', id = 46_0, width= 995, height= 480, pos = [470,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as draw_tracker_AT:

    with child(id = 46_1_0, width = (get_item_width(46_0)*0.3) , autosize_y = True, border = False):
        add_text( 'Informações recebidas pela Serial: ')
        with child( id = 46_1_1_0, width = get_item_width(46_1_0), autosize_y = True, border = True ):
            add_text('Informações do sistema:')
            add_spacing()
            add_text( id = 46_1_1_1, default_value = 'DISCONNECTED...' )

    add_same_line()
    with child( id = 46_2_0, width= (get_item_width(46_0)*0.7), autosize_y = True, border = False ):
        add_text( 'PICO_SM: RASPICO Serial Monitor')
        with child( id = 46_2_1_0, autosize_x= True, autosize_y= True, border= True):
            add_text( 'CMD:')       
            add_text( id = 46_2_1_1, default_value = 'DISCONNECTED...' )


setup_viewport()
screen_dimension = [ GetSystemMetrics(0), GetSystemMetrics(1) ] 
set_viewport_title( title = 'Controle dos motores - Unic' )
set_viewport_pos( [55,0] )
set_viewport_width(  screen_dimension[0] )
set_viewport_height( screen_dimension[1] )

set_primary_window( main_window, True )

count = 0
while is_dearpygui_running():
    count += 1

    render_dearpygui_frame()

    DAY_2Compute = get_value( 42_5_1 )
    MG_Resolucao = get_value( 43_1_1 ) 
    MG_Steps     = get_value( 43_1_2 ) 
    MG_uStep     = get_value( 43_1_3 ) 
    ME_Resolucao = get_value( 43_2_1 ) 
    ME_Step      = get_value( 43_2_2 ) 
    ME_uStep     = get_value( 43_2_3 ) 
    MG_Angle     = get_value( 44_2   ) 
    ME_Angle     = get_value( 45_2   )

    att_Serial_Pico( COMP )
    att_CMD_Pico( COMP )


