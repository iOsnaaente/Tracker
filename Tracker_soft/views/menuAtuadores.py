from typing import Counter
from dearpygui.dearpygui import *
from win32api import SendMessage
from utils.serial_reader import serialPorts 
from utils.Model         import SunPosition
from serial              import Serial
from struct              import unpack

import datetime as dt 
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

MG_Resolucao  = 0.0 
MG_Steps      = 0.0 
MG_uStep      = 0.0 
ME_Resolucao  = 0.0 
ME_Step       = 0.0 
ME_uStep      = 0.0 
MG_Angle      = 0.0 
ME_Angle      = 0.0  

MGSR_Angle    = 0.0 
MESR_Angle    = 0.0 

SERIAL_INFO   = [ ]
buff_in       = [ ]
buff_bytes    = b''
BUFF_MAX      = 30 
buff_count    = 0



def add_image_loaded( img_path ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )

def get_nBytes( comp : Serial ): 
    if comp.isOpen():
        return comp.inWaiting()  
    else:
        print( 'COMP fechada ')

def att_CMD_Pico( COMP : Serial ):
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
                    
                        w, h = get_item_width(45_0), get_item_height(45_0)
                        r    = w//1.3 if w < h else h//1.3
                        show_item( 45_1_7 )
                        configure_item( 45_1_7, p1 = [ 100 + r*cos(math.radians(MESR_Angle)), 10+r*(1-sin(math.radians(MESR_Angle)))])
                        
                    except:
                        configure_item( 46_1_1_1, default_value = 'Somente modo de Demonstração(Demo).' ) 
    else: 
        configure_item( 46_1_1_1, default_value = 'DESCONECTADO!' )
        hide_item( 45_1_7 )
        hide_item( 44_1_9)

def att_motors_data( sender, data, user ):
    global MG_Resolucao
    global MG_Steps
    global MG_uStep
    global ME_Resolucao
    global ME_Step
    global ME_uStep

    set_value( 43_1_2, value= (360 / get_value( 43_1_1 ) if get_value( 43_1_1 ) > 0 else 0 ) ) 
    set_value( 43_2_2, value= (360 / get_value( 43_2_1 ) if get_value( 43_2_1 ) > 0 else 0 ) ) 

    MG_Resolucao = get_value( 43_1_1 )     
    MG_Steps     = get_value( 43_1_2 ) 
    MG_uStep     = get_value( 43_1_3 ) 
    ME_Resolucao = get_value( 43_2_1 )     
    ME_Step      = get_value( 43_2_2 )
    ME_uStep     = get_value( 43_2_3 ) 

    # ENVIAR A MENSAGEM DE ADAPTAÇÃO PARA O RASPICO 

def write_message(sender, data, user ):
    msg = get_value( 46_2_2_2 )
    set_value( 46_2_2_2, '' )
    if CONNECTED: 
        try:
            COMP.write( msg.encode() )
            print( 'Enviando:', msg )
        except: 
            print("Erro serial.. ")

def write_message_buttons(sender, data, user ):
    if CONNECTED:
        msg = user if type(user) == str else str(user)
        try:
            COMP.write( msg.encode() )
            print( 'Enviando:', msg )
        except: 
            print("Erro serial.. ")
    else: 
        print("Não conectado")


def init_atuador( windows : dict ): 
    # Serial Config 
    with window( label = 'Serial'     , id = 42_0, width= 455, height= 330, pos = [10,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as serial_AT: 
        windows['Atuadores'].append( serial_AT )

        add_spacing(count=2)
        add_text('CONFIGURAÇÕES DE COMUNICAÇÃO')

        # FAZER UMA THREAD PARA ESCUTAR NOVAS CONEXÕES SERIAIS 
        add_text('Selecione a porta serial: ')
        add_combo( id=42_1, default_value='COM15', items= ['COM1', 'COM4', 'COM15', 'COM16'] )
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
        add_spacing(count= 10)

        add_text( 'Data Calculada:' )
        add_same_line()

        add_text( id = 42_5_1, default_value='No data')
        add_button(label="Atualizar", width=100, id = 42_5_2, callback= lambda : set_value( 42_5_1, str(dt.datetime.now().strftime('%A %d/%m/%Y - %H:%M:%S')) ) if sun_data.update_date() == None else 1 )
        add_same_line()
        add_button(label="Limpar", width=100, id = 42_5_3, callback= lambda : set_value( 42_5_1, 'No data' ) )

    # Step Motors Config 
    with window( label = 'Motores'    , id = 43_0, width= 455, height= 480, pos = [10,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as config_AT:
        windows['Atuadores'].append( config_AT )
        # DEFNIÇÃO DOS MOTORES INDIVUDUAIS 
        add_text('DEFINIÇÃO DOS MOTORES DE PASSO')
        
        with child( id=43_1_0, label = 'MotorGiro', width= get_item_width( config_AT )-15, height= 200):
            add_text       ( "Motor de Rotação da base - Motor 1" )
            add_spacing    ( count = 2    )
            add_text       ( 'Resolução:' )
            add_input_float( id = 43_1_1, label = 'ResoluçãoM1', default_value = 1.8       , format = '%3.2f', callback = att_motors_data )
            add_spacing    ( count = 2    )
            add_text       ( 'Passos por volta:' )
            add_drag_float ( id = 43_1_2, label = 'PassosM1'   , default_value =  360 / 1.8, format = '%5.2f', no_input= True, callback= att_motors_data )
            add_spacing    ( count = 2    )
            add_text       ( 'Micro Passos do motor:' )
            add_combo      ( id=43_1_3, label = 'MicroPassosM1', default_value = '1/16'    , items  = ['1', '1/2', '1/4', '1/8', '1/16', '1/32'], callback= att_motors_data )
        add_spacing        ( count = 2    )

        with child( id = 43_2_0, label = 'MotorElevação',  width = get_item_width(config_AT)-15, height= 200 ):
            add_text       ( "Motor de Rotação da base - Motor 2")
            add_spacing    ( count = 2   )
            add_text       ( 'Resolução:')
            add_input_float( id = 43_2_1, label = 'ResoluçãoM2'  , default_value = 1.8      , format = '%3.2f', callback = att_motors_data )
            add_spacing    ( count = 2   )
            add_text       ( 'Passos por volta:')
            add_drag_float ( id = 43_2_2, label = 'PassosM2'     , default_value = 360 / 1.8, format ='%5.2f', no_input = True, callback = att_motors_data  )
            add_spacing    ( count = 2   )
            add_text       ( 'Micro Passos do motor:')
            add_combo      ( id = 43_2_3, label = 'MicroPassosM2', default_value = '1/16'   , items  = ['1', '1/2', '1/4', '1/8', '1/16', '1/32'], callback= att_motors_data ) 

    # Azimute Draw 
    with window( label ='Azimute'     , id = 44_0, width= 495, height= 330, pos = [470,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as azimute_config_AT: 
        windows['Atuadores'].append( azimute_config_AT)
        
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

        w,h = get_item_width(azimute_config_AT), get_item_height(azimute_config_AT)
        
        draw_arrow(  parent = 44_1_0, id = 44_1_8, p1 = [w//2 + r*cos(math.pi/2), h//2 + r*sin(math.pi/2)], p2 = [ w//2, h//2 ], color = color['yellow'](200), thickness = 2, size = 10  )
        draw_arrow(  parent = 44_1_0, id = 44_1_9, p1 = [w//2 + r*cos(math.pi/2), h//2 + r*sin(math.pi/2)], p2 = [ w//2, h//2 ], color = color['red'](200) , thickness = 2, size = 10  ) 
        hide_item( 44_1_9 )

        add_slider_float( id     = 44_2  , pos = [ w*0.025, h-50], width  = w*0.95, height = 50, min_value=0, max_value=360, indent=0.001, enabled=True, callback= move_azi )
        move_item_up(44_2)

    # Zenite / Altitude Draw 
    with window(label  = 'Zenite'     , id = 45_0, width= 495, height= 330, pos = [970,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as zenite_config_AT:
        windows['Atuadores'].append( zenite_config_AT )  

        def draw_semi_circle( parent, id, center, radius, angle_i, angle_f, color, segments = 360, closed = False, thickness = 1 ):
            angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
            points = [ [ center[0] + radius*cos(ang), center[1] - radius*sin(ang) ] for ang in angles ]
            draw_id = draw_polyline ( parent = parent, id = id, points = points, color= color, closed = closed, thickness= thickness )

        w, h = get_item_width(zenite_config_AT), get_item_height(zenite_config_AT)
        r    = w//1.3 if w < h else h//1.3
        pyi = 10*10/h
        pxi = 100*100/w 
        p   = 10*10/h

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

        add_slider_float( id = 45_2, pos=[w*0.025,h-50], width= w*0.95, min_value= 0, max_value= math.pi/2, indent = 0.01, callback= move_alt )
        move_item_up(45_2)

    # General Draw 
    with window( label = 'Draw_Window', id = 46_0, width= 995, height= 480, pos = [470,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as draw_tracker_AT:
        windows['Atuadores'].append( draw_tracker_AT )  
    
        with child(id = 46_1_0, width = (get_item_width(46_0)*0.3), border = False):
            add_text('Opções padrão de operação do sistema:')
            with child( id = 46_1_1_0, width = get_item_width(46_1_0), autosize_y=True, border = True ):
                add_button(label='send', callback = write_message_buttons, user_data='INITSO')
                add_same_line()
                add_text('S -> Parar o tracker')
                add_button(label='send', callback = write_message_buttons, user_data='INITDO')
                add_same_line()
                add_text('D -> Entra no modo Demo )')
                add_button(label='send', callback = write_message_buttons, user_data='INITCO')
                add_same_line()
                add_text('C -> Continuar processo')
                add_button(label='send', callback = write_message_buttons, user_data='INITRO')
                add_same_line()
                add_text('R -> Retornar inicio')
                add_button(label='send', callback = write_message_buttons, user_data='INITOO')
                add_same_line()
                add_text('O -> Ativar motores')
                add_button(label='send', callback = write_message_buttons, user_data='INITFO')
                add_same_line()
                add_text('F -> Desativar motores ')
                add_button(label='send', callback = write_message_buttons, user_data='INITGO')
                add_same_line()
                add_text('G -> Get data - Conv net')
                add_button(label='send', callback = write_message_buttons, user_data='INITAO')
                add_same_line()
                add_text('A -> Data acelerometro')                
                add_button(label='send', callback = write_message_buttons, user_data='INITPO')
                add_same_line()
                add_text('P -> Get data')
                
                add_spacing(count=3)
                add_button(label='send', callback = write_message_buttons, user_data='INITHO', enabled=False)
                add_same_line()
                add_text('H -> Trocar a hora')
                add_input_intx(id=46_1_1_1, size=3 )
                add_input_intx(id=46_1_1_2, size=3 ) 
                add_spacing(count=3)

                add_button(label='send', callback = write_message_buttons, user_data='INITMO', enabled=False)
                add_same_line()
                add_text('M -> Mover ambos motores')
                add_input_floatx(id=46_1_1_3, size=2 )
                add_spacing(count=3) 

                add_button(label='send', callback = write_message_buttons, user_data='INITmO', enabled=False)
                add_same_line()
                add_text('m -> Mover um motore')
                add_input_float(id=46_1_1_4 ) 
                add_spacing(count=3)



        add_same_line()
        with child( id = 46_2_0, width= (get_item_width(46_0)*0.7), autosize_y=True, border = False ):
            add_text( 'PICO_SM: RASPICO Serial Monitor')
            with child( id = 46_2_1_0, autosize_x= True, border= True):
                add_text( 'CMD:')       
                add_text( id = 46_2_1_1, default_value = 'DESCONECTADO!' )
            
            with child( id = 46_2_2_0, autosize_x= True, pos=[0, get_item_height(46_0)-54]):
                add_group(id = 46_2_2_1_0, horizontal=True)
                add_text( parent=46_2_2_1_0, id = 46_2_2_1, default_value="To send: ")
                add_input_text(parent=46_2_2_1_0, id = 46_2_2_2)
                add_button( parent=46_2_2_1_0, label = 'send', callback = write_message)

    hide_item( 42_0)
    hide_item( 43_0)
    hide_item( 44_0)
    hide_item( 45_0)
    hide_item( 46_0)

def resize_atuador(): 
    cw, ch = get_item_width( 1_0 ) / 1474, get_item_height( 1_0 )/ 841 
    # General Draw              46_0
    def general_att():
        configure_item( 46_0     , width  = cw*995, height = ch*480, pos = [cw*470, ch*360] ) #[995, 480] -> Draw 
        configure_item( 46_1_0   , width  = (cw*995)*0.3     ) 
        configure_item( 46_2_0   , width  = (cw*995)*0.675   )
        configure_item( 46_2_1_0 , height = (cw*480)-100     )
        configure_item( 46_2_2_0 , pos    = [0, (cw*480)-54] )
        configure_item( 46_2_2_2 , width  = (cw*995)*0.525   )
    general_att()

    # Zenite / Altitude Draw    45_0 
    def zenite_att():
        configure_item( 45_0, width = cw*495, height = ch*330, pos = [cw*970, ch*25 ] ) #[495, 330] -> Zenite 
        def draw_semi_circle( parent, id, center, radius, angle_i, angle_f, color, segments = 360, closed = False, thickness = 1 ):
            delete_item(id)
            angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
            points = [ [ center[0] + radius*cos(ang), center[1] - radius*sin(ang) ] for ang in angles ]
            draw_id = draw_polyline ( parent = parent, id = id, points = points, color= color, closed = closed, thickness= thickness )
        configure_item( 45_0, width = cw*495, height = ch*330, pos = [cw*970, ch*25 ] ) #[495, 330] -> Zenite 
        w, h        = cw*495, ch*330
        r           = w//1.3 if w < h else h//1.3
        pyi, pxi, p = h*10/495, w*50/330, h*10/495
        configure_item(   45_1_0 , width  = w*0.95 , height = h*0.95 , pos = [0,0] )
        configure_item(   45_1_1 , points = [ [ pxi, pyi ] , [ pxi, pyi+r ], [ pxi + r, pyi + r ] ], color = color['white'](200), thickness= 2               )
        draw_semi_circle( parent = 45_1_0, id = 45_1_2 , center = [ pxi, pyi + r], radius = r, angle_i = 0, angle_f = math.radians(91)  , color = color['white'](200), segments= 90, thickness= 2 )
        ang_transit = sun_data.get_azi_from_date( sun_data.transit )[0] # [ alt , azi ]
        ang_altitud = sun_data.alt
        configure_item( 45_1_3, p1  = [ pxi, pyi+r ], p2 = [pxi + r*cos(ang_transit), pyi+r*(1-sin(ang_transit))] )
        configure_item( 45_1_4, p1  = [ pxi + r*cos(ang_altitud), pyi+r*(1-sin(ang_altitud))], p2 = [pxi, pyi+r]  ) 
        configure_item( 45_1_5, pos = [ w-75, pyi] )
        configure_item( 45_1_6, pos = [ w-75, 25] )  
        configure_item( 45_1_7, p1  = [ pxi + r*cos(0), pyi+r*(1-sin(0))], p2 = [pxi, pyi+r] ) 
        hide_item( 45_1_7 )
        configure_item( 45_2, pos=[w*0.025,h-50], width= w*0.95 )
        move_item_up(45_2)
    zenite_att()

    # Azimute Draw              44_0
    def azimute_att(): 
        configure_item( 44_0, width = cw*495, height = ch*330, pos = [cw*470, ch*25 ] ) #[495, 330] -> Azimue
        configure_item( 44_1_0  , width = cw*495, height = ch*330, pos = [0,-25] )
        w, h = [ get_item_width(44_1_0)/2, get_item_height(44_1_0)/2] 
        r, p = (w/2)*1.25 if w < h else (h/2)*1.25 , 20
        configure_item( 44_1_1, center = [ w       , h     ] , radius =  r            )
        configure_item( 44_1_2, p1     = [ w - r   , h     ] , p2     = [ w + r, h ]  )
        configure_item( 44_1_3, pos    = [ w - r-p , h-7.5 ] )
        configure_item( 44_1_4, pos    = [ w + r+p , h-7.5 ] )
        configure_item( 44_1_5, pos    = [ w -6    , h-r-p ] )
        ## RENDERIZAÇÃO
        ang_ris = sun_data.get_azi_from_date( sun_data.rising )[1] # [ alt , azi ]
        ang_set = sun_data.get_azi_from_date( sun_data.sunset )[1] # [ alt , azi ]
        configure_item( 44_1_6, p1 = [ w, h], p2 = [w + r*cos(ang_ris-math.pi/2), h + r*sin(ang_ris-math.pi/2)] )
        configure_item( 44_1_7, p1 = [ w, h], p2 = [w + r*cos(ang_set-math.pi/2), h + r*sin(ang_set-math.pi/2)] )
        w,h = cw*495, ch*330    
        configure_item( 44_1_8, p1 = [w//2 + r*cos(math.pi/2), h//2 + r*sin(math.pi/2)], p2 = [ w//2, h//2 ] )
        hide_item( 44_1_9 )
        configure_item( 44_1_9, p1 = [w//2 + r*cos(math.pi/2), h//2 + r*sin(math.pi/2)], p2 = [ w//2, h//2 ] ) 
        configure_item( 44_2, pos = [ w*0.025, h-50], width  = w*0.95, height = 50  )
        move_item_up(44_2)
    azimute_att()

    # Step Motors Config        43_0 
    def step_motors_att():
        configure_item( 43_0, width = cw*455, height = ch*480, pos = [cw*10 , ch*360] ) #[455, 480] -> Motores
        configure_item( 43_1_0, width= (cw*455)-15, height= 200)
        configure_item( 43_2_0, width = (cw*455)-15, height= 200 )
    step_motors_att() 

    # Serial Config             42_0 
    def serial_config_att():
        configure_item( 42_0, width = cw*455, height = ch*330, pos = [cw*10 , ch*25 ] ) #[455, 330] -> Serial
    serial_config_att()

def render_atuador() : 
    #att_Serial_Pico( COMP )
    att_CMD_Pico( COMP )

    DAY_2Compute = get_value( 42_5_1 )
    MG_Resolucao = get_value( 43_1_1 ) 
    MG_Steps     = get_value( 43_1_2 ) 
    MG_uStep     = get_value( 43_1_3 ) 
    ME_Resolucao = get_value( 43_2_1 ) 
    ME_Step      = get_value( 43_2_2 ) 
    ME_uStep     = get_value( 43_2_3 ) 
    MG_Angle     = get_value( 44_1   ) 
    ME_Angle     = get_value( 45_1   )

    return [ DAY_2Compute, MG_Resolucao, MG_Steps , MG_uStep , ME_Resolucao, ME_Step , ME_uStep , MG_Angle , ME_Angle ]