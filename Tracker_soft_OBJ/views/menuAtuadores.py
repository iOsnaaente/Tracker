from dearpygui.dearpygui import *

from utils.serial_reader import serialPorts 
from serial              import Serial

from registry            import * 
from themes              import * 

import datetime as dt
import struct 
import math 

SERIAL_INFO  = [ ]
buff_in      = [ ]
buff_bytes   = b''
BUFF_MAX     = 30 
buff_count   = 0

def get_nBytes(   comp   : Serial ): 
    if comp.isOpen():
        return comp.inWaiting()  
    else:
        print( 'COMP fechada ')
        set_value( CONNECTED, False )

def att_position( buffer : str    ):
    if type( buffer )  == bytes : 
        buffer = buffer.decode()
    try:
        buffer = buffer.split('\n')
        for line in buffer:
            if 'Azimute' in line:
                line.replace('Azimute:\\t', '').replace('\\r', '')
                azimute = line
            if 'Altitude' in line: 
                line.replace('Altitude:\\t', '').replace('\\r', '')
                altitude = line
    except:
        pass 
    print( azimute, altitude)
   
def att_CMD_Pico( COMP   : Serial ):
    global buff_count
    global buff_bytes 
    global buff_in 

    if get_value(CONNECTED) == True:    
        try:
            read = COMP.read( get_nBytes( COMP ) )
            if len(read) > 3: 
                buff_in.append( '[[{}] {}] '.format( buff_count, dt.datetime.now().strftime('%d/%m/%Y-%H:%M:%S') ) + str(read.decode()) ) 
                buff_bytes  = read 
                buff_count += 1
                if len(buff_in) > BUFF_MAX: 
                    buff_in.pop(0)
        except:
            pass

        aux = ''
        line = ''
        for i in buff_in:
            for l in i: 
                line += ' ' if ord(l) < 32 or ord(l) == 127 else l
            aux += line + '\n'
            line = ''  
        configure_item( 46_2_1_1, default_value = aux )
    else: 
        buff_count = 0 
        buff_in    = []
        configure_item( 46_2_1_1, default_value = 'DESCONECTADO...' )

def write_msg( msg : str ):
    global COMP
    if get_value(CONNECTED) == True:
        try:
            COMP.write( msg.encode() )
            print( 'Enviando:', msg )
        except: 
            print("Erro serial.. ")
    else: 
        print("Não conectado")

# CALLBACKS 
def att_motors_data( sender, data, user ):
    if get_value(43_1) == 'de Passo':
        msg = 'INITZO'
        if user == 'Gir':
            msg += 'g'
            uStep = get_value( 43_2_1_3 )  
            if   uStep == '1'   : uStep = float(1 )
            elif uStep == '1/2 ': uStep = float(2 )
            elif uStep == '1/4 ': uStep = float(4 )
            elif uStep == '1/8 ': uStep = float(8 )
            elif uStep == '1/16': uStep = float(16) 
            elif uStep == '1/32': uStep = float(32)
            else:                 uStep = float(1 )
            set_value( 43_2_1_2, value= (360 / get_value( 43_2_1_1 ) if get_value( 43_2_1_1 ) > 0 else 0 ) ) 
            set_value( MG_Resolucao ,  get_value( 43_2_1_1 )      )     
            set_value( MG_Steps     ,  get_value( 43_2_1_2 )      ) 
            set_value( MG_uStep     ,  uStep                      ) 
            msg_bytes  =  struct.pack( 'f', get_value( 43_2_1_1 ) )
            msg_bytes +=  struct.pack( 'f', get_value( 43_2_1_2 ) )
            msg_bytes +=  struct.pack( 'f', uStep                 )
            for n in range( struct.calcsize('fff')):
                msg += chr( msg_bytes[n] )
        else:
            msg += 'e'
            uStep = get_value( 43_2_1_3 )  
            if   uStep == '1'   : uStep = float(1 )
            elif uStep == '1/2 ': uStep = float(2 )
            elif uStep == '1/4 ': uStep = float(4 )
            elif uStep == '1/8 ': uStep = float(8 )
            elif uStep == '1/16': uStep = float(16) 
            elif uStep == '1/32': uStep = float(32)
            else:                 uStep = float(1 )
            set_value( 43_2_2_2, value= (360 / get_value( 43_2_2_1 ) if get_value( 43_2_2_1 ) > 0 else 0 ) ) 
            set_value( ME_Resolucao , get_value( 43_2_2_1 ) )     
            set_value( ME_Steps     , get_value( 43_2_2_2 ) )
            set_value( ME_uStep     , uStep                 ) 
            msg_bytes  =  struct.pack( 'f', get_value( 43_2_2_1 ) )
            msg_bytes +=  struct.pack( 'f', get_value( 43_2_2_2 ) )
            msg_bytes +=  struct.pack( 'f', uStep                 )
            for n in range( struct.calcsize('fff')):
                msg += chr( msg_bytes[n] )
        
    else: 
        msg = 'INITzOc'
        set_value(VelAng_M1 , get_value(43_3_1_2) ) 
        set_value(VelAng_M2 , get_value(43_3_2_2) )
        msg_bytes  =  struct.pack( 'f', get_value(43_3_1_2) )
        msg_bytes +=  struct.pack( 'f', get_value(43_3_2_2) )
        for n in range( struct.calcsize('ff')):
            msg += chr( msg_bytes[n] )
    
    write_msg( msg )

def write_message(sender, data, user ):
    msg = get_value( 46_2_2_2 )
    set_value( 46_2_2_2, '' )
    write_msg ( msg )

def write_hour( sender, data, user ) : 
    # 'INITHO'
    msg  = user 
    date = get_value( 46_1_1_1 )
    hour = get_value( 46_1_1_2 ) 
    if date[0] > 31:    raise 'days out of range'
    if date[1] > 12:    raise 'months out of range'       
    if hour[0] > 60:    raise 'seconds out of range'
    if hour[1] > 60:    raise 'minutes out of range'
    if hour[2] > 23:    raise 'hours out of range'
    if date[2] > 2000:  date[2] -= 2000
    date = struct.pack( 'bbb', date[0], date[1], date[2] ) 
    msg += chr(date[0]) + chr(date[1]) + chr(date[2])
    hour = struct.pack( 'bbb', hour[0], hour[1], hour[2]) 
    msg += chr(hour[0]) + chr(hour[1]) + chr(hour[2])
    write_msg( msg )

def write_motors_pos(sender, data, user ) : 
    # 'INITMO' or 'INITmO' 
    msg = user
    if user == 'INITMO': 
        values = struct.pack('ff', get_value(46_1_1_3)[0], get_value(46_1_1_3)[1] ) 
        for i in range( struct.calcsize('ff')): 
            msg += chr(values[i])    

    elif user == 'INITmO':
        msg   += 'g' if get_value(46_1_1_4_1) == 'Gir' else 'e'
        values = struct.pack('f', get_value(46_1_1_4_2) )            
        for i in range( struct.calcsize('f')): 
            msg += chr(values[i])  

    write_msg( msg )

def write_message_buttons(sender, data, user ):
    global COMP
    if get_value(CONNECTED) == True:
        msg = user if type(user) == str else str(user)
        try:
            COMP.write( msg.encode() )
            print( 'Enviando:', msg )
        except: 
            print("Erro serial.. ")
    else: 
        print("Não conectado")

def change_motors_conf(sender, data, user):
    if data == 'de Passo':
        show_item(43_2_0)
        hide_item(43_3_0)
    elif data == 'Trifásicos': 
        show_item(43_3_0)
        hide_item(43_2_0)

def change_state_motor(sender, data, user ) : 
    msg = 'INITzOS'
    if user == 'm1':
        set_value( M1_ONorOFF, not get_value(M1_ONorOFF) ) 
        if get_value(M1_ONorOFF): 
            set_item_theme( sender, Motor_On  )
            msg += 'gO'
        else : 
            set_item_theme( sender, Motor_Off )
            msg += 'gF'
        configure_item(sender, label= 'Ligado' if get_value(M1_ONorOFF) == True else 'Desligado' )

    elif user == 'm2':
        set_value( M2_ONorOFF, not get_value(M2_ONorOFF) ) 
        if get_value(M2_ONorOFF): 
            set_item_theme( sender, Motor_On  )
            msg += 'eO'
        else : 
            set_item_theme( sender, Motor_Off )
            msg += 'eF'
        configure_item(sender, label= 'Ligado' if get_value(M2_ONorOFF) else 'Desligado' )

    write_msg( msg )

def SR_refresh( sender, data, user ):
    configure_item( 42_1_1, label = 'Procurando' ) 
    seriais = serialPorts( lenght = 20 )
    configure_item( 42_1  , items = seriais )
    configure_item( 42_1_1, label = 'Refresh' )

def SR_try_connect( sender, data, user): 
    global COMP 
    SR_Port      = get_value( 42_1 )
    SR_Baudrate  = get_value( 42_2 )
    SR_Timeout   = get_value( 42_3 )  

    if not COMP.isOpen():
        try: 
            COMP = Serial( port = SR_Port, baudrate = SR_Baudrate, timeout = SR_Timeout )
            show_item( 42_6 )
            show_item( 42_7 )
            set_item_theme( 42_6, Motor_On  )
            set_item_theme( 42_7, Motor_Off )
            hide_item( 42_4 )
            set_value( CONNECTED, True)
        except:                
            hide_item( 42_6 )
            hide_item( 42_7 )
            show_item( 42_4 )
            set_value( CONNECTED, False)

def SR_close_connection(sender, data, user ): 
    try: 
        COMP.close() 
        hide_item( 42_6)         
        hide_item( 42_7) 
        show_item(42_4)
    except: 
        pass 

def init_atuador( windows : dict ): 

    # Serial Config 
    with window( label = 'Serial'     , id = 42_0, width= 455, height= 330, pos = [10,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as serial_AT: 
        windows['Atuadores'].append( serial_AT )

        add_spacing(count = 1)
        add_text('CONFIGURAÇÕES DE COMUNICAÇÃO')

        add_text('Selecione a porta serial: ')
        add_combo( id = 42_1, default_value='COM16', items= ['COM1', 'COM4', 'COM15', 'COM16'] )
        add_same_line( )
        add_button(  id = 42_1_1, label='Refresh', callback= SR_refresh )
        add_spacing( count= 1 )

        add_text('Baudarate: ')
        add_combo( id = 42_2, default_value= '9600', items=[ '9600', '57600', '115200'] )
        add_spacing( count = 1 )

        add_text('Timeout: ')
        add_input_int( id = 42_3, default_value= 1)
        add_spacing( count = 3 )

        add_button(label='Iniciar conexão',              id = 42_4 , callback= SR_try_connect      )
        add_button(label="CONECTADO"      , width = 150, id = 42_6                                 )
        add_same_line()
        add_button(label="DESCONECTAR"    , width = 150, id = 42_7, callback = SR_close_connection )
        add_spacing(count= 5)
        hide_item( 42_6)         
        hide_item( 42_7) 

        add_text( 'Data Calculada:' )
        add_same_line()
        add_text( id = 42_5_1, default_value='Click em atualizar')
        
        add_button(label="Atualizar", width=100, id = 42_5_2, callback= lambda : set_value( 42_5_1, str(dt.datetime.now().strftime('%d/%m/%Y - %H:%M:%S')) ) if sun_data.update_date() == None else 1 )
        add_same_line()
        add_button(label="Limpar", width=100, id = 42_5_3, callback= lambda : set_value( 42_5_1, 'No data' ) )

    # Step Motors Config 
    with window( label = 'Motores'    , id = 43_0, width= 455, height= 480, pos = [10,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as config_AT:
        windows['Atuadores'].append( config_AT )
        add_text( 'CONFIGURAÇÃO DE ACIONAMENTO DOS MOTORES')
        add_spacing()

        # DEFNIÇÃO DOS MOTORES INDIVUDUAIS
        add_text('Motores ')
        add_same_line() 
        add_radio_button( id = 43_1, items = ['Trifásicos', 'de Passo'], default_value = 'de Passo', horizontal=True, callback = change_motors_conf)
        
        # DE PASSO 
        with child( id = 43_2_0, autosize_x =True, autosize_y = True): 
            add_text('DEFINIÇÃO DOS MOTORES DE PASSO')
            add_spacing( )
            with child( id = 43_2_1_0, label = 'MotorGiro'    , autosize_x=True, height = 200 ):
                add_text       ( "Motor de Rotação da base - Motor 1" )
                add_spacing    ( )
                add_text       ( 'Resolução:' )
                add_input_float( id = 43_2_1_1, default_value = 1.8       , format = '%3.2f', callback = att_motors_data, user_data = 'Gir', on_enter = True )
                add_spacing    ( )
                add_text       ( 'Micro Passos do motor:' )
                add_combo      ( id=43_2_1_3, default_value = '1/16'    , items  = ['1', '1/2', '1/4', '1/8', '1/16', '1/32'], callback= att_motors_data, user_data = 'Gir' )
                add_spacing    ( )
                add_text       ( 'Passos por volta:' )
                add_drag_float ( id = 43_2_1_2, default_value =  360 / 1.8, format = '%5.2f', no_input= True, callback= att_motors_data, user_data = 'Gir' )
            add_spacing    ( )
            with child( id = 43_2_2_0, label = 'MotorElevação', autosize_x=True, height = 200 ):
                add_text       ( "Motor de Rotação da base - Motor 2")
                add_spacing    ( )
                add_text       ( 'Resolução:')
                add_input_float( id = 43_2_2_1, default_value = 1.8      , format = '%3.2f', callback = att_motors_data, user_data = 'Ele', on_enter = True )
                add_spacing    ( )
                add_text       ( 'Micro Passos do motor:')
                add_combo      ( id = 43_2_2_3, default_value = '1/16'   , items  = ['1', '1/2', '1/4', '1/8', '1/16', '1/32'], callback= att_motors_data, user_data = 'Ele' ) 
                add_spacing    ( )
                add_text       ( 'Passos por volta:')
                add_drag_float ( id = 43_2_2_2, default_value = 360 / 1.8, format ='%5.2f', no_input = True, callback = att_motors_data, user_data = 'Ele'  )
        
            set_item_theme(43_2_1_0, 'noborder')
            set_item_theme(43_2_2_0, 'noborder')

        # TRIFÁSICO 
        with child( id = 43_3_0, autosize_x=True, autosize_y=True ):
            add_text('DEFINIÇÃO DE ACIONAMENTO TRIFÁSICO')
            add_spacing( )
            with child( id = 43_3_1_0, label = 'MotorGiro'    ,autosize_x = True, height = 100 ):
                add_text       ( "Motor de Rotação da base - Motor 1" )
                add_spacing    ( )
                add_button     ( id = 43_3_1_1, label= 'Desligado'  ,  width = 250, callback = change_state_motor, user_data='m1')
                add_text       ( 'Velocidade angular M1:' )
                add_input_float( id = 43_3_1_2, label = 'Wo (rad/s)', default_value = get_value(VelAng_M1), format = '%3.2f', on_enter = True, callback = att_motors_data )
                # CORRIGIR A TROCA DE MENSAGEM PARA AJUSTAR AS VELOCIDADES

            add_spacing    ( )
            with child( id = 43_3_2_0, label = 'MotorElevação',autosize_x = True, height = 125 ):
                    add_text       ( "Motor de Rotação da base - Motor 2")
                    add_spacing    ( )
                    add_button     ( id = 43_3_2_1, label='Desligado', width=250, callback = change_state_motor, user_data='m2')
                    add_text       ( 'Velocidade angular M2:' )
                    add_input_float( id = 43_3_2_2, label = 'Wo (rad/s)', default_value = get_value(VelAng_M2), format = '%3.2f', on_enter = True, callback = att_motors_data )

                # CORRIGIR A TROCA DE MENSAGEM PARA AJUSTAR AS VELOCIDADES

            set_item_theme(43_3_1_0, 'noborder')
            set_item_theme(43_3_2_0, 'noborder')
            set_item_theme( 43_3_1_1, Motor_Off )
            set_item_theme( 43_3_2_1, Motor_Off )

        if get_value( 43_1 ) == 'de Passo':
            show_item(43_2_0)
            hide_item(43_3_0)
        else: 
            show_item(43_3_0)
            hide_item(43_2_0)
            
    # Azimute Draw 
    with window( label ='Azimute'     , id = 44_0, width= 495, height= 330, pos = [470,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as azimute_config_AT: 
        windows['Atuadores'].append( azimute_config_AT)
        
        with drawlist( id = 44_1_0  , width = 495, height = 330, pos = [0,-25] ):
            
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
            draw_line(  parent = 44_1_0, id = 44_1_6, p1 = [ w, h], p2 = [w + r*math.cos(ang_ris-math.pi/2), h + r*math.sin(ang_ris-math.pi/2)], color = color['gray'](200), thickness= 2 )
            draw_line(  parent = 44_1_0, id = 44_1_7, p1 = [ w, h], p2 = [w + r*math.cos(ang_set-math.pi/2), h + r*math.sin(ang_set-math.pi/2)], color = color['gray'](200), thickness= 2 )
        
            def move_azi(sender, data, user):
                w, h = [ get_item_width(44_1_0)/2, get_item_height(44_1_0)/2]     
                r    = (w/2)*1.25 if w < h else (h/2)*1.25 
                configure_item( 44_1_8, p1 = [w + r*math.cos(math.radians(get_value(MG_Angle))+math.pi*3/2), h + r*math.sin( math.radians(get_value(MG_Angle))+math.pi*3/2)] )

            w,h = get_item_width(azimute_config_AT), get_item_height(azimute_config_AT)
            
            draw_arrow(  parent = 44_1_0, id = 44_1_8, p1 = [w//2 + r*math.cos(math.pi/2), h//2 + r*math.sin(math.pi/2)], p2 = [ w//2, h//2 ], color = color['yellow'](200), thickness = 2, size = 10  )
            draw_arrow(  parent = 44_1_0, id = 44_1_9, p1 = [w//2 + r*math.cos(math.pi/2), h//2 + r*math.sin(math.pi/2)], p2 = [ w//2, h//2 ], color = color['red'](200) , thickness = 2, size = 10  ) 
            hide_item( 44_1_9 )

        add_slider_float( id     = 44_2  , pos = [ w*0.025, h-50], width  = w*0.95, height = 50, min_value=0, max_value=360, indent=0.001, enabled=True, callback= move_azi )
        move_item_up(44_2)

    # Zenite / Altitude Draw 
    with window(label  = 'Zenite'     , id = 45_0, width= 495, height= 330, pos = [970,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as zenite_config_AT:
        windows['Atuadores'].append( zenite_config_AT )  

        def draw_semi_circle( parent, id, center, radius, angle_i, angle_f, color, segments = 360, closed = False, thickness = 1 ):
            angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
            points = [ [ center[0] + radius*math.cos(ang), center[1] - radius*math.sin(ang) ] for ang in angles ]
            draw_id = draw_polyline ( parent = parent, id = id, points = points, color= color, closed = closed, thickness= thickness )

        w, h = get_item_width(zenite_config_AT), get_item_height(zenite_config_AT)
        r    = w//1.3 if w < h else h//1.3
        pyi = 10*10/h
        pxi = 100*100/w 
        p   = 10*10/h

        with drawlist(     id     = 45_1_0, width  = w*0.95 , height = h*0.95         , pos = [0,0] ):
            draw_polyline(    parent = 45_1_0, id     = 45_1_1 , points = [ [ pxi, pyi ] , [ pxi, pyi+r ], [ pxi + r, pyi + r ] ], color = color['white'](200), thickness= 2               )
            draw_semi_circle( parent = 45_1_0, id     = 45_1_2 , center = [ pxi, pyi + r], radius = r, angle_i = 0, angle_f = math.radians(91)  , color = color['white'](200), segments= 90, thickness= 2 )
            
            # RENDERIZAÇÃO 
            ang_transit = sun_data.get_azi_from_date( sun_data.transit )[0] # [ alt , azi ]
            ang_altitud = sun_data.alt

            draw_line( parent = 45_1_0, id = 45_1_3, p1  = [ pxi, pyi+r ], p2 = [pxi + r*math.cos(ang_transit), pyi+r*(1-math.sin(ang_transit))] , color = color['red'](200)   , thickness = 2             )
            draw_arrow(parent = 45_1_0, id = 45_1_4, p1  = [ pxi + r*math.cos(ang_altitud), pyi+r*(1-math.sin(ang_altitud))], p2 = [pxi, pyi+r]  , color = color['yellow'](200), thickness = 3, size = 10  ) 
            draw_text( parent = 45_1_0, id = 45_1_5, pos = [ w-75, pyi] , text = "Altura:"                                             , color = color['white'](255) , size = 15                 )
            draw_text( parent = 45_1_0, id = 45_1_6, pos = [ w-75, 25]  , text = str( round(math.degrees(ang_altitud)) )+'º'           , color = color['white'](255) , size = 15                 )  
            
            draw_arrow(parent = 45_1_0, id = 45_1_7, p1  = [ pxi + r*math.cos(0), pyi+r*(1-math.sin(0))], p2 = [pxi, pyi+r]  , color = color['red'](200), thickness = 3, size = 10  ) 
            hide_item( 45_1_7 )

            def move_alt( sender, data, user ):
                w, h = get_item_width( zenite_config_AT ), get_item_height( zenite_config_AT )
                r    = w//1.3 if w < h else h//1.3
                configure_item( 45_1_4, p1 = [ pxi + r*math.cos(math.radians(get_value(ME_Angle))), pyi+r*(1-math.sin(math.radians(get_value(ME_Angle))))] )
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
                add_button(label='send', callback = write_message_buttons, user_data='INITLO')
                add_same_line()
                add_text('L -> Levers')                
                add_button(label='send', callback = write_message_buttons, user_data = 'INITPO')
                add_same_line()
                add_text('P -> Get data')
                
                add_spacing(count=3)
                add_button(label='send', callback = write_hour, user_data = 'INITHO' )
                add_same_line()
                add_text('H -> Trocar a hora')
                add_input_intx(id=46_1_1_1, size=3, default_value=[ 12, 5, 2021 ], max_value = 99, callback = write_hour, user_data = 'INITHO', on_enter = True )
                add_same_line()
                add_text('dd/mm/yy')
                add_input_intx(id=46_1_1_2, size=3, default_value=[ 15, 35, 10  ], max_value = 60, callback = write_hour, user_data = 'INITHO', on_enter = True ) 
                add_same_line()
                add_text('hh:mm:ss')
                add_spacing(count=3)

                add_button(label='send', callback = write_motors_pos, user_data = 'INITMO' )
                add_same_line()
                add_text('M -> Mover ambos motores')
                add_input_floatx(id=46_1_1_3, size=2, default_value=[ 12.05, 19.99], on_enter = True, callback = write_motors_pos, user_data = 'INITMO')
                add_spacing(count=3) 

                add_button(label='send', callback = write_motors_pos, user_data = 'INITmO' )
                add_same_line()
                add_text('m -> Mover um motore')
                add_input_float ( id = 46_1_1_4_2, default_value = 12, on_enter = True, callback = write_motors_pos, user_data = 'INITmO' )
                add_radio_button( id = 46_1_1_4_1, items = ['Gir', 'Ele'], default_value = 'Gir', horizontal = True ) 

        add_same_line()
        with child( id = 46_2_0, width= (get_item_width(46_0)*0.7), autosize_y=True, border = False ):
            add_text( 'PICO_SM: RASPICO Serial Monitor')
            with child  ( id = 46_2_1_0, autosize_x = True, border = True):
                add_text( 'CMD:')       
                add_text( id = 46_2_1_1, default_value = 'DESCONECTADO!', tracked = True, track_offset = 1 )
            
            with child        ( id     = 46_2_2_0  , autosize_x = True , pos=[0, get_item_height(46_0)-54] ):
                add_group     ( id     = 46_2_2_1_0, horizontal = True )
                add_text      ( parent = 46_2_2_1_0, id = 46_2_2_1  , default_value =  "To send: "    )
                add_input_text( parent = 46_2_2_1_0, id = 46_2_2_2  , on_enter =  True , callback = write_message )
                add_button    ( parent = 46_2_2_1_0, label = 'send' , callback =  write_message )

    hide_item( 42_0)
    hide_item( 43_0)
    hide_item( 44_0)
    hide_item( 45_0)
    hide_item( 46_0)

def resize_atuador(): 
    cw = get_item_width( 1_0 ) / 1474
    ch = get_item_height( 1_0 )/ 841 

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
            points = [ [ center[0] + radius*math.cos(ang), center[1] - radius*math.sin(ang) ] for ang in angles ]
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
        configure_item( 45_1_3, p1  = [ pxi, pyi+r ], p2 = [pxi + r*math.cos(ang_transit), pyi+r*(1-math.sin(ang_transit))] )
        configure_item( 45_1_4, p1  = [ pxi + r*math.cos(ang_altitud), pyi+r*(1-math.sin(ang_altitud))], p2 = [pxi, pyi+r]  ) 
        configure_item( 45_1_5, pos = [ w-75, pyi] )
        configure_item( 45_1_6, pos = [ w-75, 25] )  
        configure_item( 45_1_7, p1  = [ pxi + r*math.cos(0), pyi+r*(1-math.sin(0))], p2 = [pxi, pyi+r] ) 
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
        configure_item( 44_1_6, p1 = [ w, h], p2 = [w + r*math.cos(ang_ris-math.pi/2), h + r*math.sin(ang_ris-math.pi/2)] )
        configure_item( 44_1_7, p1 = [ w, h], p2 = [w + r*math.cos(ang_set-math.pi/2), h + r*math.sin(ang_set-math.pi/2)] )
        w,h = cw*495, ch*330    
        configure_item( 44_1_8, p1 = [w//2 + r*math.cos(math.pi/2), h//2 + r*math.sin(math.pi/2)], p2 = [ w//2, h//2 ] )
        hide_item( 44_1_9 )
        configure_item( 44_1_9, p1 = [w//2 + r*math.cos(math.pi/2), h//2 + r*math.sin(math.pi/2)], p2 = [ w//2, h//2 ] ) 
        configure_item( 44_2, pos = [ w*0.025, h-50], width  = w*0.95, height = 50  )
        move_item_up(44_2)
    azimute_att()

    # Step Motors Config        43_0 
    def step_motors_att():
        configure_item( 43_0, width = cw*455, height = ch*520, pos = [cw*10 , ch*320] ) #[455, 480] -> Motores
    step_motors_att() 

    # Serial Config             42_0 
    def serial_config_att():
        configure_item( 42_0, width = cw*455, height = ch*290, pos = [cw*10 , ch*25 ] ) #[455, 330] -> Serial
    serial_config_att()
 
def render_atuador() : 
    
    att_CMD_Pico( COMP )

    cw   = get_item_width( 1_0 ) / 1474
    ch   = get_item_height( 1_0 )/ 841 
    w, h = cw*495, ch*330
    r    = w//1.3 if w < h else h//1.3
    pyi  = 10*10  /h
    pxi  = 100*100/w

    ang_cul = get_value( culminant_alt ) 
    ang_alt = get_value( ME_Angle      )     
    configure_item( 45_1_3, p2   = [ pxi + r*math.cos( ang_cul ), pyi+r*( 1-math.sin( ang_cul ))] )
    configure_item( 45_1_4, p1   = [ pxi + r*math.cos( ang_alt ), pyi+r*( 1-math.sin( ang_alt ))] )
    configure_item( 45_1_6, text = str( round(math.degrees(ang_alt), 2) )+'º' )

    w, h = [ get_item_width(44_1_0)/2, get_item_height(44_1_0)/2] 
    r    = (w/2)*1.25 if w < h else (h/2)*1.25
    ang_ris = get_value( sunrise_azi)
    ang_set = get_value( sunset_azi )
    ang_azi = get_value( MG_Angle   )
    configure_item( 44_1_6, p2 = [w + r*math.cos(ang_ris-math.pi/2)  , h + r*math.sin( ang_ris-math.pi/2  )] )
    configure_item( 44_1_7, p2 = [w + r*math.cos(ang_set-math.pi/2)  , h + r*math.sin( ang_set-math.pi/2  )] )
    configure_item( 44_1_8, p1 = [w + r*math.cos(ang_azi+math.pi*3/2), h + r*math.sin( ang_azi+math.pi*3/2)] )


import dearpygui.dearpygui as dpg 

class Azimute: 
    parent  = 0 
    center  = 0
    radius  = 0
    height  = 0 
    width   = 0
    p       = 0

    ang_min = 0 
    ang_max = 0 

    size    = 0 
    arrows  = []

    def __init__(self, parent ):
        self.parent = parent 
        self.width, self.height = dpg.get_item_width( parent ), dpg.get_item_height( parent ) 
        with dpg.drawlist( parent = self.parent, id = dpg.generate_uuid()  , width = self.width, height = self.height, pos = [0,-25] ) as azimute_drawlist:
            self.azimute_drawlist = azimute_drawlist 

    def build(self, size : int = 1):
        w, h = [ self.width/2, self.height/2] 
        r, p = w*1.25 if w < h else h*1.25, 20 
        self.center = [w, h ]
        self.radius = r 
        self.p      = p

        self.size = size

        self.draw_circle = dpg.draw_circle( parent = self.azimute_drawlist, id = dpg.generate_uuid(), center = self.center         , radius =  self.radius  , color = color['white'](200), thickness = 2 )
        self.draw_line   = dpg.draw_line  ( parent = self.azimute_drawlist, id = dpg.generate_uuid(), p1     = [ w - r   , h     ] , p2     = [ w + r, h ]  , color = color['gray'](200) , thickness = 2 )
        self.draw_west   = dpg.draw_text  ( parent = self.azimute_drawlist, id = dpg.generate_uuid(), pos    = [ w - r-p , h-7.5 ] , text   = 'W'           , color = color['white'](200), size = 20     )
        self.draw_east   = dpg.draw_text  ( parent = self.azimute_drawlist, id = dpg.generate_uuid(), pos    = [ w + r+p , h-7.5 ] , text   = 'E'           , color = color['white'](200), size = 20     )
        self.draw_north  = dpg.draw_text  ( parent = self.azimute_drawlist, id = dpg.generate_uuid(), pos    = [ w -6    , h-r-p ] , text   = 'N'           , color = color['white'](255), size = 20     )
        
        self.draw_lnMin  = dpg.draw_line  ( parent = self.azimute_drawlist, id = dpg.generate_uuid(), p1 = [ w, h], p2 = [w + r*math.cos(self.ang_min-math.pi/2), h + r*math.sin(self.ang_min-math.pi/2)], color = color['gray'](200), thickness= 2 )
        self.draw_lnMax  = dpg.draw_line  ( parent = self.azimute_drawlist, id = dpg.generate_uuid(), p1 = [ w, h], p2 = [w + r*math.cos(self.ang_max-math.pi/2), h + r*math.sin(self.ang_max-math.pi/2)], color = color['gray'](200), thickness= 2 )
        
        for arrow in range(size):
            self.arrows.append( dpg.draw_arrow ( parent = self.azimute_drawlist, id = dpg.generate_uuid(), p1 = [ w + self.radius*math.cos(math.pi/2), h + self.radius*math.sin(math.pi/2)], p2 = self.center, color = color['yellow'](200), thickness = 2, size = 10 ) ) 
            
        self.slider = dpg.add_slider_float( parent = self.parent , id = generate_uuid(), pos = [ self.width*0.025, self.height-50], width  = self.width*0.95, height = 50, min_value=0, max_value=360, indent=0.001, enabled=True, callback = self.move_slider )
        
    def move_slider( self, sender, data, user  ): 
        for i in self.arrows:
            configure_item( i , p1 = [ self.width/2 + self.radius*math.cos(data), self.height/2 + self.radius*math.sin(data)] ) 

    def resize(self, width, height ): 
        self.width  = width
        self.height = height 
        configure_item( self.parent          , width = self.width*495, height = self.height*330, pos = [self.width*470, self.height*25 ] ) 
        configure_item( self.azimute_drawlist, width = self.width*495, height = self.height*330, pos = [0,-25] )
        
        w, h = [self.width/2, self.height/2] 
        r, p = w*1.25 if self.width < self.height else h*1.25 , 20
        
        self.center = [ w, h ]
        self.radius = r 
        self.p      = p 

        configure_item( self.draw_circle , center = [ w       , h     ] , radius =  r            )
        configure_item( self.draw_line   , p1     = [ w - r   , h     ] , p2     = [ w + r, h ]  )
        configure_item( self.draw_west   , pos    = [ w - r-p , h-7.5 ] )
        configure_item( self.draw_east   , pos    = [ w + r+p , h-7.5 ] )
        configure_item( self.draw_north  , pos    = [ w -6    , h-r-p ] )


    def render( self, data : list = [ 0, 0, 0] ):
        self.ang_min = data[0]
        self.ang_max = data[1]
        configure_item( 44_1_6, p1 = self.center, p2 = [self.center[0] + self.radius*math.cos(self.ang_min-math.pi/2), self.center[1] + self.radius*math.sin(self.ang_min-math.pi/2)] )
        configure_item( 44_1_7, p1 = self.center, p2 = [self.center[0] + self.radius*math.cos(self.ang_max-math.pi/2), self.center[1] + self.radius*math.sin(self.ang_max-math.pi/2)] )

        configure_item( 44_1_6, p2 = [w + r*math.cos(ang_ris-math.pi/2)  , h + r*math.sin( ang_ris-math.pi/2  )] )
        configure_item( 44_1_7, p2 = [w + r*math.cos(ang_set-math.pi/2)  , h + r*math.sin( ang_set-math.pi/2  )] )
        configure_item( 44_1_8, p1 = [w + r*math.cos(ang_azi+math.pi*3/2), h + r*math.sin( ang_azi+math.pi*3/2)] )

