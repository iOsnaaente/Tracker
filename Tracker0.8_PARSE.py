from dearpygui.dearpygui import *
from utils.serial_reader import serialPorts 
from utils.Model         import SunPosition
from win32api            import GetSystemMetrics
from serial              import Serial
from struct              import unpack

import datetime as dt 
import ephem
import math 
import sys 
import os 

PATH = os.path.dirname( __file__ )
PATH_IMG = PATH + '\\utils\\img\\'

map_val = lambda value, in_min, in_max, out_min, out_max : ((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min ) 
cos     = lambda x : math.cos( x )
sin     = lambda x : math.sin( x )
tg      = lambda x : math.tan( x )


COMP : Serial = Serial() 
PATH = os.path.dirname( __file__ )


LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 425
UTC_HOUR  = -3
DOM       = [ 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro' ]


sun_data  = SunPosition( LATITUDE, LONGITUDE, ALTITUDE )
sun_data.update_date()


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

count = 0 

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

windows = {
            "Inicio"             : [  ],
            "Visualização geral" : [  ],
            "Posição do sol"     : [  ],
            "Atuadores"          : [  ],
            "Atuação da base"    : [  ],
            "Atuação da elevação": [  ],
            "Configurações"      : [  ],
            'Sair'               : [  ],
            }

window_opened = ''


def add_image_loaded( img_path ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )

def change_menu(sender, app_data, user_data ):
    global window_opened 
    window_opened = user_data 
    # CLOSE ALL WINDOWS 
    for k in windows.keys():
        for i in windows[k]:
            hide_item(i)
    # OPEN THE RIGHT TAB WINDOW 
    to_open = windows[user_data]
    for i in to_open:
        show_item(i)

def ajust_win( obj, o_wh : list, o_pos : list) -> list :    
    cw = get_item_width( main_window ) / 1474
    ch = get_item_height( main_window )/ 841 

    set_item_width(  obj, cw*o_wh[0] ) 
    set_item_height( obj, ch*o_wh[1] ) 
    set_item_pos(    obj, [ cw*o_pos[0], ch*o_pos[1] ] ) 

# Main Window 
with window( label = 'Main Window', id = 1_0, autosize = True ) as main_window:
    with menu_bar(label = "MenuBar"):
        add_menu_item( label="Inicio"             , callback = change_menu, user_data = "Inicio"              )
        add_menu_item( label="Visualização geral" , callback = change_menu, user_data = "Visualização geral"  )
        add_menu_item( label="Posição do sol"     , callback = change_menu, user_data = "Posição do sol"      )
        add_menu_item( label="Atuadores"          , callback = change_menu, user_data = "Atuadores"           )
        add_menu_item( label="Atuação da base"    , callback = change_menu, user_data = "Atuação da base"     )
        add_menu_item( label="Atuação da elevação", callback = change_menu, user_data = "Atuação da elevação" )
        add_menu_item( label="Configurações"      , callback = change_menu, user_data = "Configurações"       )
        add_menu_item( label='Sair'               , callback = change_menu, user_data = 'Sair'                )

# Themes e mudanças de estilo 
with theme( default_theme = True ) as theme_id:
    add_theme_color( mvThemeCol_Button       , (255, 140, 23), category = mvThemeCat_Core )
    add_theme_style( mvStyleVar_FrameRounding,        5      , category = mvThemeCat_Core )
    # um azul bem bonito -> 52, 140, 215 

with theme( id = 99_0_2  ):
    add_theme_color( mvThemeCol_Button       , (52, 140, 215 ), category = mvThemeCat_Core )
    # um azul bem bonito -> 52, 140, 215 


# RENDER 
def render_inicio():
    w_header , h_header  = get_item_width( 1_1 ), get_item_height( 1_1 )
    w_lateral, h_lateral = get_item_width( 1_2 ), get_item_height( 1_2 )

    configure_item( 1_1 , width = w-15     , height = h*3/10    , pos = [ 10       , 25             ] )
    configure_item( 1_2 , width = w/3      , height = h*6.60/10 , pos = [ 10       , (h//10)*3 + 30 ] )
    configure_item( 1_3 , width = w*2/3-20 , height = h*6.60/10 , pos = [ w//3 + 15, (h//10)*3 + 30 ] )

    configure_item( 1_1_1_0 , width = w_header-16 , height = h_header-16 ) # HEADER 

    configure_item( 1_1_1_1 , pmin  = (-30,-30), pmax = ( w, round( h*3/10)*2 ))
    configure_item( 1_1_1_2 , pmin  = (10,10)  , pmax = (350,200) )

    v_spacing = h_lateral // 7  # LATERAL 
    configure_item( 1_2_1, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_2, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_3, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_4, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_5, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_6, width = w//3 - 15, height = v_spacing )  

def render_visualizacao():
    w, h = get_item_width(1_0), get_item_height(1_0)

    configure_item( 2_1_0    , width =  w*2/3        , height =  h*3/5      , pos = [10 , 25 ]               ) # DESENHO 
    configure_item( 2_1_1_0  , width = (w*2/3)*0.9   , height = (h*3/5)*0.95, pos = [ (w*1/6)  ,  10 ]       ) # DRAWLIST
    configure_item( 2_1_2    , width = (w*2/3)-20    , height =  25         , pos = [ 10       , (h*3/5)-50] ) # PROGRESSIVE BAR 

    configure_item( 2_2_0    , width =  w*2/3         , height =  (h*2/5)-35 , pos = [10 , (h*3/5)+30 ]       ) # ATUADORES 
    configure_item( 2_2_1_0  , width =  (w*2/3)//2-15 , height = (h*2/5)*0.9 , pos = [ 5            , 20 ] )                           # GIRO
    configure_item( 2_2_2_0  , width =  (w*2/3)//2-15 , height = (h*2/5)*0.9 , pos = [ (w*2/3)//2 +5, 20 ] )                           # ELEVAÇÃO 

    configure_item( 2_3_0    , width =  w/3 -20      , height =  h - 30     , pos = [ w*2/3 +15, 25 ]        ) # LOG 

    #clear_drawing('Solar')
    #draw_sun_trajetory('Solar',  get_item_width('Solar_pos##VG')-20,  get_item_height('Solar_pos##VG')-75 )

    # Definição da Latitude/Longitude 
    sun_data.latitude  = str( get_value(2_3_10) ) # LATITUDE
    sun_data.longitude = str( get_value(2_3_11) ) # LONGITUDE 
    sun_data.update_coordenates()

    # Horário automático 
    if ( get_value( 2_3_5 ) is False ):           # HORA MANUAL 
        sun_data.update_date()
        set_value( 2_3_1, value = [ sun_data.year, sun_data.month, sun_data.day ] )      # DIA ATUTOMÁTICO 
        set_value( 2_3_2, value = [ sun_data.hour, sun_data.minute, sun_data.second ] )  # HORA AUTOMÁTICA
        set_value( 2_3_3, value = sun_data.total_seconds )                               # TOTAL DE SEGUNDOS 

        # Total de segundos no dia convertido entre 0 e 1
        total_seconds_converted = map_val(sun_data.total_seconds, 0, 24*3600, 0, 1)
        set_value( 2_1_2, total_seconds_converted)                               # BARRA PROGRESSIVA 
        set_value( 2_3_9, sun_data.dia_juliano)                                  # DIA JULIANO 

    else:
        # Pegando a data e hora passadas pelo usuário
        year, month, day     = get_value( 2_3_6 )                               # DIA ARBITRÁRIO 
        hour, minute, second = get_value( 2_3_7 )                               # HORA ARBITRÁRIA

        # Montar a data setada pelo usuário
        data = dt.datetime( int(year), int(month), int(day), int(hour), int(minute), int(second) )
        sun_data.set_date( data )
        
        set_value( 2_3_3, sun_data.total_seconds)                               # TOTAL DE SEGUNDOS 
        
        # Total de segundos no dia convertidos entre 0 e 1
        total_seconds_converted = map_val(sun_data.total_seconds, 0, 24*3600, 0, 1)
        set_value( 2_1_2, total_seconds_converted)                              # BARRA PROGRESSIVA  
        set_value( 2_3_9, sun_data.dia_juliano)                                 # DIA JULIANO

    # Setar o Azimute, Altitude e Elevação
    set_value( 2_3_12, math.degrees( sun_data.azi) )                            #  AZIMUTE               
    set_value( 2_3_13, math.degrees( sun_data.alt) )                            #  ALTITUDE               
    set_value( 2_3_14, sun_data.altitude)                                       #  ELEVAÇÃO

    # Seta as horas do sol calculando as horas minutos e segundos de segundos totais 
    diff_sunlight = (sun_data.sunset - sun_data.rising).seconds
    set_value( 2_3_15, [diff_sunlight//3600, (diff_sunlight//60)%60 , diff_sunlight%60 ] )

    # Setar as informações de Nascer do sol, Culminante (ponto mais alto) e Por do sol
    set_value( 2_3_16, [ sun_data.rising.hour+sun_data.utc_local , sun_data.rising.minute , sun_data.rising.second  ] ) # 'Nascer do sol'
    set_value( 2_3_17, [ sun_data.transit.hour+sun_data.utc_local, sun_data.transit.minute, sun_data.transit.second ] ) # 'Culminante'   
    set_value( 2_3_18, [ sun_data.sunset.hour+sun_data.utc_local , sun_data.sunset.minute , sun_data.sunset.second  ] ) # 'Por do sol'      

def render_atuador():
    global count
    DAY_2Compute = get_value( 42_5_1 )
    MG_Resolucao = get_value( 43_1_1 ) 
    MG_Steps     = get_value( 43_1_2 ) 
    MG_uStep     = get_value( 43_1_3 ) 
    ME_Resolucao = get_value( 43_2_1 ) 
    ME_Step      = get_value( 43_2_2 ) 
    ME_uStep     = get_value( 43_2_3 ) 
    MG_Angle     = get_value( 44_1   ) 
    ME_Angle     = get_value( 45_1   )

    att_Serial_Pico( COMP )
    att_CMD_Pico( COMP )

    if count == 30:
        ajust_win( serial_AT        , [455, 330], [10 , 25 ] )
        ajust_win( config_AT        , [455, 480], [10 , 360] )
        ajust_win( azimute_config_AT, [495, 330], [470, 25 ] )
        ajust_win( zenite_config_AT , [495, 330], [970, 25 ] )
        ajust_win( draw_tracker_AT  , [995, 480], [470, 360] )
        count = 0
    else: 
        count += 1 

def render_configuracao():
    w, h = get_item_width( 1_0 ), get_item_height( 1_0 ) 
    configure_item( 7_1_0, pos = [ 10            , 25 ], width = (w*(1/3))//1, height = (h*0.965)//1 ) 
    configure_item( 7_2_0, pos = [ w*(1/3)   + 10, 25 ], width = (w*(7/15)-5 )//1, height = (h*0.965)//1 ) 
    configure_item( 7_3_0, pos = [ w*(12/15) + 5 , 25 ], width = (w*(3/15)-10)//1, height = (h*0.965)//1 ) 



# FUNÇÕES
def draw_sun_trajetory( id, width, height, all_day = False, extremes = False ):
    # Ponto central, dimensões da tela e Raio 
    center = [ width//2, height//2 ]
    w, h   = get_item_width(1_0), get_item_height(1_0)
    r      =   width//2 - 20 if width+20 <= height else height//2 - 20

    add_drawlist(       id = 2_1_1_0, width = w, height = h, label = 'Solar')

    # Desenho estático 
    draw_line( parent = id, p1 = [center[0] - r, center[1]], p2 = [center[0] + r, center[1]], color = color['gray'](155), thickness= 1 )
    
    # DESENHO DA LINHA DE NASCER DO SOL E POR DO SOL 
    ang = sun_data.get_azi_from_date( sun_data.rising )[1]
    draw_line( parent = id, p1 = center, p2 = [center[0] + r*cos(ang-math.pi/2), center[1] + r*sin(ang-math.pi/2)], color = color['orange'](155), thickness= 2 )
    
    ang = sun_data.get_azi_from_date( sun_data.sunset )[1] # [ alt , azi ]
    draw_line( parent = id, p1 = center, p2 = [center[0] + r*cos(ang-math.pi/2), center[1] + r*sin(ang-math.pi/2)], color = color['gray'](200), thickness= 2 )

    # Desenhos estáticos 
    draw_circle( parent = id, center = center, radius = r, color = color['white'](200), fill = color['white'](10 ), thickness = 3 )
    draw_circle( parent = id, center = center, radius = 3, color = color['white'](200), fill = color['white'](255), thickness = 2 )
    
    draw_text(   parent = id, pos= [center[0] - (r + 20), center[1] -10 ], text = 'W', color = color['white'](200), size=20 )
    draw_text(   parent = id, pos= [center[0] + (r +  5), center[1] -10 ], text = 'E', color = color['white'](200), size=20 )
    draw_text(   parent = id, pos= [center[0] - 10 , center[1] - (r + 25)  ], text = 'N', color = color['white'](255), size=20 )
    
    # PEGA OS ANGULOS NOS PONTOS DA TRAJETÓRIA DO SOL 
    dots = sun_data.trajetory(100, all_day )

    # PONTOS DE ACORDO COM Azimute - Altitude 
    dots = [ [ x - math.pi/2 ,  y ] for x, y in dots ]
    dots = [ [ center[0] + cos(x)*r, center[1] + sin(x)*cos(y)*r ] for x, y in dots ]

    # DESENHO DO TRACEJADO E OS PONTOS COLORIDOS DE NASCER A POR DO SOL  
    draw_polyline( parent = id, points = dots, color= color['red'](155), thickness= 2, closed= False )
    for n, p in enumerate(dots):
        draw_circle( parent = id, center = p, radius = 2, color = [n*4, 255-n*2, n*2, 255] )
    
    # DESENHO DO SOL NA SUA POSIÇÃO 
    sun = [  sun_data.azi - math.pi/2, sun_data.alt ] 
    sun = [ center[0] + cos(sun[0])*r, center[1] + sin(sun[0])*cos(sun[1])*r ]
    
    draw_line(   parent = id, p1 = center, p2 = sun, color = color['yellow'](200), thickness = 2 )
    draw_circle( parent = id, center = sun, radius = 10, color = color['yellow'](155), fill = color['yellow'](255) )

    if extremes: 
        min_date = sun_data.winter_solstice 
        max_date = sun_data.summer_solstice        
        sun_data.set_date( min_date )

def hover_buttons_IN( sender, data, user):
    if   user == "Visualização geral"  :
        configure_item( 1_3_1, default_value = user)
    elif user == "Posição do sol"      :
        configure_item( 1_3_1, default_value = user)
    elif user == "Atuadores"           :
        configure_item( 1_3_1, default_value = user)
    elif user == "Atuação da base"     :
        configure_item( 1_3_1, default_value = user)
    elif user == "Atuação da elevação" :
        configure_item( 1_3_1, default_value = user)
    elif user == "Configurações"       :
        configure_item( 1_3_1, default_value = user)

def get_nBytes( comp : Serial ): 
    if comp.isOpen():
        return comp.inWaiting()  
    else:
        print( 'COMP fechada ')

def send_msg( comp : Serial, msg : str ):
    for s in msg:
        comp.write( s.encode() ) 

def att_comData(comp : Serial ):
    DATA = receive_msg( comp )
    if DATA : 
        return DATA  

def add_image_loaded( img_path ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )

def change_menu(sender, app_data, user_data ):
    global window_opened 
    window_opened = user_data 
    # CLOSE ALL WINDOWS 
    for k in windows.keys():
        for i in windows[k]:
            hide_item(i)
    # OPEN THE RIGHT TAB WINDOW 
    to_open = windows[user_data]
    for i in to_open:
        show_item(i)

def ajust_win( obj, o_wh : list, o_pos : list) -> list :    
    cw = get_item_width( main_window ) / 1474
    ch = get_item_height( main_window )/ 841 

    set_item_width(  obj, cw*o_wh[0] ) 
    set_item_height( obj, ch*o_wh[1] ) 
    set_item_pos(    obj, [ cw*o_pos[0], ch*o_pos[1] ] ) 

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


# DRAW TABS 
def init_inicio(): 
    with window( label = 'Header' , id = 1_1, pos = [10, 25], no_move= True, no_close= True, no_title_bar= True, no_resize= True ) as Header_IN:    
        windows['Inicio'].append( Header_IN )
        img_fundo = add_image_loaded( PATH_IMG + 'fundo.jpg' )
        img_logo  = add_image_loaded( PATH_IMG + 'JetTowers-Logo.png' )

        add_drawlist( id = 1_1_1_0 )
        draw_image  ( parent = 1_1_1_0, id = 1_1_1_1, label = 'imgFundo', texture_id = img_fundo, pmin = (0,0), pmax = (1,1) ) 
        draw_image  ( parent = 1_1_1_0, id = 1_1_1_2, label = 'imgLogo' , texture_id = img_logo , pmin = (0,0), pmax = (1,1) )
    with window( label = 'Lateral', id = 1_2, no_move= True, no_close= True, no_title_bar= True, no_resize= True) as Lateral_IN:
        windows['Inicio'].append( Lateral_IN )
        add_spacing( count = 4 )
        add_button( label = "Visualização geral" , id = 1_2_1, arrow= False, callback = change_menu, user_data = 'Visualização geral'  )
        add_button( label = "Posição do sol"     , id = 1_2_2, arrow= False, callback = change_menu, user_data = 'Posição do sol'      )
        add_button( label = "Atuadores"          , id = 1_2_3, arrow= False, callback = change_menu, user_data = "Atuadores"           )
        add_button( label = "Atuação da base"    , id = 1_2_4, arrow= False, callback = change_menu, user_data = "Atuação da base"     )
        add_button( label = "Atuação da elevação", id = 1_2_5, arrow= False, callback = change_menu, user_data = "Atuação da elevação" )
        add_button( label = "Configurações"      , id = 1_2_6, arrow= False, callback = change_menu, user_data = 'Configurações'       )
    with window( label = 'Main'   , id = 1_3, no_move= True, no_close= True, no_title_bar= True, no_resize= True) as Main_IN:
        windows['Inicio'].append( Main_IN )

        add_text( 'HOVER SOME ITEM AT THE LEFT SIDE...', id = 1_3_1)
        add_hover_handler( parent = 1_2_1, callback = hover_buttons_IN, user_data = "Visualização geral"  )
        add_hover_handler( parent = 1_2_2, callback = hover_buttons_IN, user_data = "Posição do sol"      )
        add_hover_handler( parent = 1_2_3, callback = hover_buttons_IN, user_data = "Atuadores"           )
        add_hover_handler( parent = 1_2_4, callback = hover_buttons_IN, user_data = "Atuação da base"     )
        add_hover_handler( parent = 1_2_5, callback = hover_buttons_IN, user_data = "Atuação da elevação" )
        add_hover_handler( parent = 1_2_6, callback = hover_buttons_IN, user_data = "Configurações"       )

def init_visualizacao():
    with window( label = 'Posição solar'      , id = 2_1_0, pos = [50,50], width = 500, height = 500, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as Posicao_sol_VG:
        windows["Visualização geral"].append( Posicao_sol_VG )

        w, h = get_item_width(2_1_0), get_item_height(2_1_0)
        draw_sun_trajetory( id = 2_1_1_0, width = w-20, height = h-50 )
        add_progress_bar(   id = 2_1_2,   width = w   , height = 30   )


    with window( label = 'Atuação'           , id = 2_2_0, no_move = True, no_resize = True, no_collapse = True, no_close = True ) as Atuacao_VG:
        windows["Visualização geral"].append( Atuacao_VG )

        add_text('Área para a atução da posição dos paineis solares')
        center = [ get_item_width(2_2_0)//2 , get_item_height(2_2_0)//2 ]
        r = 100 
        
        with child( label = 'AtuaçãoBase'   , id = 2_2_1_0 ):
            add_drawlist( id     = 2_2_1_1_0, width = w-10, height = h-10)
            draw_circle(  parent = 2_2_1_1_0, id = 2_2_1_1_1, center = center, radius = 75, color = color['white'](255), thickness=2 )
            draw_arrow(   parent = 2_2_1_1_0, id = 2_2_1_1_2, p1 = [ 0, 0 ]  , p2 = center, color = color['green'](155), thickness= 5, size=10)
            draw_arrow(   parent = 2_2_1_1_0, id = 2_2_1_1_3, p1 = [ 0, 0 ]  , p2 = center, color = color['red'](155),   thickness= 5, size=10)
            draw_circle(  parent = 2_2_1_1_0, id = 2_2_1_1_4, center = center, radius = 5 , color = [255,255,0,175], fill=True )

        with child(label = 'AtuaçãoElevação', id = 2_2_2_0 ):
            add_drawlist( id     = 2_2_2_1_0, width  = w-10 , height = h-10 )
            draw_circle(  parent = 2_2_2_1_0, id = 2_2_2_1_1, center = center, radius = r , color = color['white'](255), thickness=2 )
            draw_arrow(   parent = 2_2_2_1_0, id = 2_2_2_1_2, p1 = [ 0, 0 ]  , p2 = center, color = color['green'](150), thickness= 5, size=10)
            draw_arrow(   parent = 2_2_2_1_0, id = 2_2_2_1_3, p1 = [ 0, 0 ]  , p2 = center, color = color['red'](200),   thickness= 5, size=10)
            draw_circle(  parent = 2_2_2_1_0, id = 2_2_2_1_4, center = center, radius = 5 , color = color['yellow'](155), fill=True)

    with window( label = 'Painel de log'       , id = 2_3_0, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar = True ) as Painel_log_VG:
        windows["Visualização geral"].append( Painel_log_VG )
      
        #Informações gerais do sistema - Automático 
        add_text('Informações gerais do sistema')
        add_drag_floatx( label = 'Dia automatico'  , id = 2_3_1, size = 3, format='%4.0f', speed=1, no_input= True)
        add_spacing(count=1)
        add_drag_floatx( label = 'Hora automatica' , id = 2_3_2, size = 3, format='%4.0f', speed=1, no_input= True)
        add_spacing(count=1)
        add_drag_float( label = 'Total segundos'  , id = 2_3_3, format='%4.0f', speed=0.1, min_value = 0, max_value = 23*3600, no_input= True)
        add_spacing(count=1)
        add_drag_float( label = 'Dia Juliano'     , id = 2_3_4, format='%4.0f', speed=0.1, min_value = 0, no_input= True)
        add_spacing(count=5)

        def hora_manual_VG(sender, data, user):
            # Verifica a condição do CheckBox
            status = get_value(2_3_5)
            # Configuração dos parametros automáticos
            configure_item( 2_3_1, enabled = not status )
            configure_item( 2_3_2, enabled = not status)
            configure_item( 2_3_3, enabled = not status)
            configure_item( 2_3_4, enabled = not status)

            # Configuração dos parametros manuais 
            configure_item( 2_3_1, enabled = status )
            configure_item( 2_3_2, enabled = status )
            configure_item( 2_3_3, enabled = status )
            configure_item( 2_3_4, enabled = status)

        # Informações gerais do sistema - Manual 
        add_checkbox(     label = "Hora manual"    , id = 2_3_5, default_value = False, callback= hora_manual_VG )
        add_spacing(count = 1 )
        add_input_floatx( label = 'Dia arbitrario' , id = 2_3_6, size = 3, default_value = [2020, 12, 25], format='%.0f', enabled = False )
        add_spacing(count = 1 )
        add_input_floatx( label = 'Hora arbitraria', id = 2_3_7, size = 3, default_value = [20, 30, 10]  , format='%.0f', enabled = False )
        add_spacing(count = 1 )
        add_drag_float(  label = 'Total segundos'  , id = 2_3_8, format = '%4.0f', speed = 0.1 , min_value = 0, max_value = 24*3600, no_input= True, enabled= False)
        add_spacing(count = 1 )
        add_drag_float(  label = 'Dia Juliano'     , id = 2_3_9, format = '%4.0f', speed = 0.1 , min_value = 0, no_input= True, enabled = False)
        add_spacing(count = 10)
        
        # Definições de longitude e latitude local
        add_text('Definições de longitude e latitude local')
        add_input_float( label = 'Latitude' , id = 2_3_10, default_value = -29.165307659422155, format = '%3.5f')
        add_spacing(count = 1)
        add_input_float( label = 'Longitude', id = 2_3_11, default_value = -54.89831672609559 , format = '%3.5f')
        add_spacing(count=10)

        # Informações do sol 
        add_text('Informacoes do sol')
        add_drag_float( label = 'Azimute'     , id = 2_3_12, format='%4.2f', speed=1, no_input= True)
        add_spacing(count = 1)
        add_drag_float( label = 'Altitude'    , id = 2_3_13, format='%4.2f', speed=1, no_input= True)
        add_spacing(count = 1)
        add_drag_float( label = 'Elevação (m)', id = 2_3_14, format='%4.0f', speed=1, no_input= True)
        add_spacing(count = 1)
        add_drag_floatx( label = 'Horas de sol', id = 2_3_15, size = 3, format='%.0f', no_input= True)
        add_spacing(count=10)
        
        # Posições de interesse
        add_text("Posicoes de interesse")
        add_drag_floatx( label = 'Nascer do sol', id = 2_3_16, size = 3, format='%.0f', speed=1, no_input= True)
        add_spacing(count = 1)
        add_drag_floatx( label = 'Culminante'   , id = 2_3_17, size = 3, format='%.0f', speed=1, no_input= True)
        add_spacing(count = 1)
        add_drag_floatx( label = 'Por do sol'   , id = 2_3_18, size = 3, format='%.0f', speed=1, no_input= True)
        add_spacing(count = 1)
        add_spacing(count=1)

def init_configuracao(): 

    def att_theme_style( sender, data, user ):
        with theme( default_theme = True ) as theme_style_id: 
            # Windows 
            add_theme_style( mvStyleVar_WindowBorderSize   , get_value(7_1_1) )
            add_theme_style( mvStyleVar_WindowMinSize      , get_value(7_1_2) )
            add_theme_style( mvStyleVar_WindowPadding      , x = get_value(7_1_3)[0] , y = get_value(7_1_3)[1] )
            add_theme_style( mvStyleVar_WindowTitleAlign   , x = get_value(7_1_4)[0] , y = get_value(7_1_4)[1] )
            add_theme_style( mvStyleVar_WindowRounding     , x = get_value(7_1_5)[0] , y = get_value(7_1_5)[1] )

            # Childs    
            add_theme_style( mvStyleVar_ChildBorderSize    , get_value( 7_1_6 ) )
            add_theme_style( mvStyleVar_ChildRounding      , get_value( 7_1_7 ) )

            # PopUp
            add_theme_style( mvStyleVar_PopupBorderSize    , get_value( 7_1_8 ) )
            add_theme_style( mvStyleVar_PopupRounding      , get_value( 7_1_9 ) )

            # Frames 
            add_theme_style( mvStyleVar_FrameBorderSize    , get_value( 7_1_10 ) )
            add_theme_style( mvStyleVar_FramePadding       , x = get_value(7_1_11)[0] , y = get_value(7_1_11)[1] )
            add_theme_style( mvStyleVar_FrameRounding      , get_value( 7_1_12 ) )

            # Items 
            add_theme_style( mvStyleVar_ItemSpacing        , x = get_value(7_1_13)[0] , y = get_value(7_1_13)[1] )
            add_theme_style( mvStyleVar_ItemInnerSpacing   , x = get_value(7_1_14)[0] , y = get_value(7_1_14)[1] )

            # Scroll
            add_theme_style( mvStyleVar_ScrollbarSize      , get_value( 7_1_15 ) )
            add_theme_style( mvStyleVar_ScrollbarRounding  , get_value( 7_1_16 ) )

            # Cell \ Indent \ Grab \ Button 
            add_theme_style( mvStyleVar_CellPadding        , x = get_value(7_1_17)[0] , y = get_value(7_1_17)[1] )
            add_theme_style( mvStyleVar_IndentSpacing      , get_value( 7_1_18 ) )
            add_theme_style( mvStyleVar_GrabMinSize        , get_value( 7_1_19 ) )
            add_theme_style( mvStyleVar_GrabRounding       , get_value( 7_1_20 ) )
            add_theme_style( mvStyleVar_ButtonTextAlign    , x = get_value(7_1_21)[0] , y = get_value(7_1_21)[1] )
            add_theme_style( mvStyleVar_SelectableTextAlign, x = get_value(7_1_22)[0] , y = get_value(7_1_22)[1] )
        
    def att_theme_color():
        with theme( default_theme = True ) as theme_color_id:
            
            add_theme_color( mvThemeCol_Text                   , get_value( 7_2_22 ) ) 
            add_theme_color( mvThemeCol_TextDisabled           , get_value( 7_2_23 ) ) 
            add_theme_color( mvThemeCol_WindowBg               , get_value( 7_2_24 ) ) 
            add_theme_color( mvThemeCol_ChildBg                , get_value( 7_2_25 ) ) 
            add_theme_color( mvThemeCol_PopupBg                , get_value( 7_2_26 ) ) 
            add_theme_color( mvThemeCol_Border                 , get_value( 7_2_27 ) ) 
            add_theme_color( mvThemeCol_BorderShadow           , get_value( 7_2_28 ) ) 
            add_theme_color( mvThemeCol_FrameBg                , get_value( 7_2_29 ) ) 
            add_theme_color( mvThemeCol_FrameBgHovered         , get_value( 7_2_30 ) ) 
            add_theme_color( mvThemeCol_FrameBgActive          , get_value( 7_2_31 ) ) 
            add_theme_color( mvThemeCol_TitleBg                , get_value(77_2_32 ) ) 
            add_theme_color( mvThemeCol_TitleBgActive          , get_value(77_2_33 ) ) 
            add_theme_color( mvThemeCol_TitleBgCollapsed       , get_value(77_2_34 ) ) 
            add_theme_color( mvThemeCol_MenuBarBg              , get_value(77_2_35 ) ) 
            add_theme_color( mvThemeCol_ScrollbarBg            , get_value(77_2_36 ) ) 
            add_theme_color( mvThemeCol_ScrollbarGrab          , get_value(77_2_37 ) ) 
            add_theme_color( mvThemeCol_ScrollbarGrabHovered   , get_value(77_2_38 ) ) 
            add_theme_color( mvThemeCol_ScrollbarGrabActive    , get_value(77_2_39 ) ) 
            add_theme_color( mvThemeCol_CheckMark              , get_value(77_2_40 ) ) 
            add_theme_color( mvThemeCol_SliderGrab             , get_value(77_2_41 ) ) 
            add_theme_color( mvThemeCol_SliderGrabActive       , get_value(77_2_42 ) ) 
            add_theme_color( mvThemeCol_Button                 , get_value(77_2_43 ) ) 
            add_theme_color( mvThemeCol_ButtonHovered          , get_value(77_2_44 ) ) 
            add_theme_color( mvThemeCol_ButtonActive           , get_value(77_2_45 ) ) 
            add_theme_color( mvThemeCol_Header                 , get_value(77_2_46 ) ) 
            add_theme_color( mvThemeCol_HeaderHovered          , get_value(77_2_47 ) ) 
            add_theme_color( mvThemeCol_HeaderActive           , get_value(77_2_48 ) ) 
            add_theme_color( mvThemeCol_Separator              , get_value(77_2_49 ) ) 
            add_theme_color( mvThemeCol_SeparatorHovered       , get_value(77_2_50 ) ) 
            add_theme_color( mvThemeCol_SeparatorActive        , get_value(77_2_51 ) ) 
            add_theme_color( mvThemeCol_ResizeGrip             , get_value(77_2_52 ) ) 
            add_theme_color( mvThemeCol_ResizeGripHovered      , get_value(77_2_53 ) ) 
            add_theme_color( mvThemeCol_ResizeGripActive       , get_value(77_2_54 ) ) 
            add_theme_color( mvThemeCol_Tab                    , get_value(77_2_55 ) ) 
            add_theme_color( mvThemeCol_TabHovered             , get_value(77_2_56 ) ) 
            add_theme_color( mvThemeCol_TabActive              , get_value(77_2_57 ) ) 
            add_theme_color( mvThemeCol_TabUnfocused           , get_value(77_2_58 ) ) 
            add_theme_color( mvThemeCol_TabUnfocusedActive     , get_value(77_2_59 ) ) 
            add_theme_color( mvThemeCol_DockingPreview         , get_value(77_2_60 ) ) 
            add_theme_color( mvThemeCol_DockingEmptyBg         , get_value(77_2_61 ) ) 
            add_theme_color( mvThemeCol_PlotLines              , get_value(77_2_62 ) ) 
            add_theme_color( mvThemeCol_PlotLinesHovered       , get_value(77_2_63 ) ) 
            add_theme_color( mvThemeCol_PlotHistogram          , get_value(77_2_64 ) ) 
            add_theme_color( mvThemeCol_PlotHistogramHovered   , get_value(77_2_65 ) ) 
            add_theme_color( mvThemeCol_TableHeaderBg          , get_value(77_2_66 ) ) 
            add_theme_color( mvThemeCol_TableBorderStrong      , get_value(77_2_67 ) ) 
            add_theme_color( mvThemeCol_TableBorderLight       , get_value(77_2_68 ) ) 
            add_theme_color( mvThemeCol_TableRowBg             , get_value(77_2_69 ) ) 
            add_theme_color( mvThemeCol_TableRowBgAlt          , get_value(77_2_70 ) ) 
            add_theme_color( mvThemeCol_TextSelectedBg         , get_value(77_2_71 ) ) 
            add_theme_color( mvThemeCol_DragDropTarget         , get_value(77_2_72 ) ) 
            add_theme_color( mvThemeCol_NavHighlight           , get_value(77_2_73 ) ) 
            add_theme_color( mvThemeCol_NavWindowingHighlight  , get_value(77_2_74 ) ) 
            add_theme_color( mvThemeCol_NavWindowingDimBg      , get_value(77_2_75 ) ) 
            add_theme_color( mvThemeCol_ModalWindowDimBg       , get_value(77_2_76 ) ) 
        return theme_id

    with window( label = 'Configurações_Estilo'  , id = 7_1_0, pos = [50,50], width = 500, height = 500, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as style_CONFG:
        windows['Configurações'].append( style_CONFG )

        add_text( 'Configurações de janela' )
        add_checkbox     ( label = 'WindowBorderSize'   , id = 7_1_1 , callback = att_theme_style, default_value = True                                                  )
        add_slider_int   ( label = 'WindowMinSize   '   , id = 7_1_2 , callback = att_theme_style, default_value = 0                  , min_value = 0 , max_value = 1400 )
        add_slider_intx  ( label = 'WindowPadding'      , id = 7_1_3 , callback = att_theme_style, default_value = [5,5]    , size = 2, min_value = 0 , max_value = 25   )
        add_slider_floatx( label = 'WindowTitleAlign'   , id = 7_1_4 , callback = att_theme_style, default_value = [0.5,0.5], size = 2, min_value = 0 , max_value = 2    )
        add_slider_floatx( label = 'WindowRouding'      , id = 7_1_5 , callback = att_theme_style, default_value = [1,1]    , size = 2, min_value = 0 , max_value = 1    )
        
        add_spacing() 
        add_text( 'Configurações de Childs')
        add_checkbox     ( label = 'ChildBorderSize'    , id = 7_1_6 , callback = att_theme_style, default_value = True)        
        add_slider_int   ( label = 'ChildRounding'      , id = 7_1_7 , callback = att_theme_style, default_value = 5 , min_value = 0  , max_value = 10   )    
        
        add_spacing() 
        add_text( 'Configurações de PopUp')
        add_checkbox     ( label = 'PopupBorderSize'    , id = 7_1_8 , callback = att_theme_style, default_value = False )        
        add_slider_int   ( label = 'PopupRounding'      , id = 7_1_9 , callback = att_theme_style, default_value = 5 , min_value = 0  , max_value = 10    )    
        
        add_spacing() 
        add_text( 'Configurações de Frames')
        add_checkbox     ( label = 'FrameBorderSize'    , id = 7_1_10, callback = att_theme_style, default_value = False )        
        add_slider_floatx( label = 'FramePadding'       , id = 7_1_11, callback = att_theme_style, default_value = [5,4], size = 2, min_value=0, max_value = 10 )    
        add_slider_float ( label = 'FrameRounding'      , id = 7_1_12, callback = att_theme_style, default_value = 5    , min_value = 0, max_value = 10   )   

        add_spacing() 
        add_text( 'Configurações de Itens')
        add_slider_intx  ( label = 'ItemSpacing'        , id = 7_1_13, callback = att_theme_style, default_value = [10,4], size = 2,  min_value = 5, max_value = 25, enabled = False )    
        add_slider_intx  ( label = 'ItemInnerSpacing'   , id = 7_1_14, callback = att_theme_style, default_value = [5,5] , size = 2,  min_value = 0, max_value = 10, enabled = False )        
        
        add_spacing() 
        add_text( 'Configurações de Scroll')
        add_slider_int   ( label = 'ScrollbarSize'      , id = 7_1_15, callback = att_theme_style, default_value = 15 , min_value = 0, max_value = 20 )    
        add_slider_int   ( label = 'ScrollbarRounding'  , id = 7_1_16, callback = att_theme_style, default_value = 2  , min_value = 0, max_value = 20 )        

        add_spacing() 
        add_text( 'Outras configurações')
        add_slider_intx  ( label = 'CellPadding'        , id = 7_1_17, callback = att_theme_style, default_value = [5,5]     , size = 2, min_value = 0, max_value = 20 )    
        add_slider_int   ( label = 'IndentSpacing'      , id = 7_1_18, callback = att_theme_style, default_value = 5                                                   )    
        add_slider_int   ( label = 'GrabMinSize'        , id = 7_1_19, callback = att_theme_style, default_value = 20                                                  )    
        add_slider_int   ( label = 'GrabRounding'       , id = 7_1_20, callback = att_theme_style, default_value = 3                   , min_value = 0, max_value = 10 )    
        add_slider_floatx( label = 'ButtonAling'        , id = 7_1_21, callback = att_theme_style, default_value = [0.5, 0.5], size = 2, min_value = 0, max_value = 1  )    
        add_slider_floatx( label = 'SelectableTextAlign', id = 7_1_22, callback = att_theme_style, default_value = [0.5, 0.5], size = 2, min_value = 0, max_value = 1  )

    with window( label = 'Configurações_Colors'  , id = 7_2_0, pos = [50,50], width = 700, height = 500, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as colors_CONFG:
        windows['Configurações'].append( colors_CONFG )
        add_color_edit( label = 'mvThemeCol_Text                 ', id = 7_2_22_1, default_value = (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), callback = att_theme_color ) 
        add_color_edit( label = 'mvThemeCol_TextDisabled         ', id = 7_2_23  , default_value = (0.50 * 255, 0.50 * 255, 0.50 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_WindowBg             ', id = 7_2_24  , default_value = (0.06 * 255, 0.06 * 255, 0.06 * 255, 0.94 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ChildBg              ', id = 7_2_25  , default_value = (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_PopupBg              ', id = 7_2_26  , default_value = (0.08 * 255, 0.08 * 255, 0.08 * 255, 0.94 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_Border               ', id = 7_2_27  , default_value = (0.43 * 255, 0.43 * 255, 0.50 * 255, 0.50 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_BorderShadow         ', id = 7_2_28  , default_value = (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_FrameBg              ', id = 7_2_29  , default_value = (0.16 * 255, 0.29 * 255, 0.48 * 255, 0.54 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_FrameBgHovered       ', id = 7_2_30  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.40 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_FrameBgActive        ', id = 7_2_31  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.67 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TitleBg              ', id = 7_2_32  , default_value = (0.04 * 255, 0.04 * 255, 0.04 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TitleBgActive        ', id = 7_2_33  , default_value = (0.16 * 255, 0.29 * 255, 0.48 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TitleBgCollapsed     ', id = 7_2_34  , default_value = (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.51 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_MenuBarBg            ', id = 7_2_35  , default_value = (0.14 * 255, 0.14 * 255, 0.14 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ScrollbarBg          ', id = 7_2_36  , default_value = (0.02 * 255, 0.02 * 255, 0.02 * 255, 0.53 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ScrollbarGrab        ', id = 7_2_37  , default_value = (0.31 * 255, 0.31 * 255, 0.31 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ScrollbarGrabHovered ', id = 7_2_38  , default_value = (0.41 * 255, 0.41 * 255, 0.41 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ScrollbarGrabActive  ', id = 7_2_39  , default_value = (0.51 * 255, 0.51 * 255, 0.51 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_CheckMark            ', id = 7_2_40  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_SliderGrab           ', id = 7_2_41  , default_value = (0.24 * 255, 0.52 * 255, 0.88 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_SliderGrabActive     ', id = 7_2_42  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_Button               ', id = 7_2_43  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.40 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ButtonHovered        ', id = 7_2_44  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ButtonActive         ', id = 7_2_45  , default_value = (0.06 * 255, 0.53 * 255, 0.98 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_Header               ', id = 7_2_46  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.31 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_HeaderHovered        ', id = 7_2_47  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.80 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_HeaderActive         ', id = 7_2_48  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_Separator            ', id = 7_2_49  , default_value = (0.43 * 255, 0.43 * 255, 0.50 * 255, 0.50 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_SeparatorHovered     ', id = 7_2_50  , default_value = (0.10 * 255, 0.40 * 255, 0.75 * 255, 0.78 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_SeparatorActive      ', id = 7_2_51  , default_value = (0.10 * 255, 0.40 * 255, 0.75 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ResizeGrip           ', id = 7_2_52  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.20 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ResizeGripHovered    ', id = 7_2_53  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.67 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ResizeGripActive     ', id = 7_2_54  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.95 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_Tab                  ', id = 7_2_55  , default_value = (0.18 * 255, 0.35 * 255, 0.58 * 255, 0.86 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TabHovered           ', id = 7_2_56  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.80 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TabActive            ', id = 7_2_57  , default_value = (0.20 * 255, 0.41 * 255, 0.68 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TabUnfocused         ', id = 7_2_58  , default_value = (0.07 * 255, 0.10 * 255, 0.15 * 255, 0.97 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TabUnfocusedActive   ', id = 7_2_59  , default_value = (0.14 * 255, 0.26 * 255, 0.42 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_DockingPreview       ', id = 7_2_60  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.70 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_DockingEmptyBg       ', id = 7_2_61  , default_value = (0.20 * 255, 0.20 * 255, 0.20 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_PlotLines            ', id = 7_2_62  , default_value = (0.61 * 255, 0.61 * 255, 0.61 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_PlotLinesHovered     ', id = 7_2_63  , default_value = (1.00 * 255, 0.43 * 255, 0.35 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_PlotHistogram        ', id = 7_2_64  , default_value = (0.90 * 255, 0.70 * 255, 0.00 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_PlotHistogramHovered ', id = 7_2_65  , default_value = (1.00 * 255, 0.60 * 255, 0.00 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TableHeaderBg        ', id = 7_2_66  , default_value = (0.19 * 255, 0.19 * 255, 0.20 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TableBorderStrong    ', id = 7_2_67  , default_value = (0.31 * 255, 0.31 * 255, 0.35 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TableBorderLight     ', id = 7_2_68  , default_value = (0.23 * 255, 0.23 * 255, 0.25 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TableRowBg           ', id = 7_2_69  , default_value = (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TableRowBgAlt        ', id = 7_2_70  , default_value = (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.06 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_TextSelectedBg       ', id = 7_2_71  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.35 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_DragDropTarget       ', id = 7_2_72  , default_value = (1.00 * 255, 1.00 * 255, 0.00 * 255, 0.90 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_NavHighlight         ', id = 7_2_73  , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_NavWindowingHighlight', id = 7_2_74  , default_value = (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.70 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_NavWindowingDimBg    ', id = 7_2_75  , default_value = (0.80 * 255, 0.80 * 255, 0.80 * 255, 0.20 * 255), callback = att_theme_color )
        add_color_edit( label = 'mvThemeCol_ModalWindowDimBg     ', id = 7_2_76  , default_value = (0.80 * 255, 0.80 * 255, 0.80 * 255, 0.35 * 255), callback = att_theme_color )

    with window( label = 'Configurações_Diversos', id = 7_3_0, pos = [50,50], width = 300, height = 500, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as others_CONFG:
        windows['Configurações'].append( others_CONFG ) 
        w, h = get_item_width(7_3_0), get_item_height(7_3_0)
        add_text( 'Área de visualização das configurações', bullet = True ) 
        add_button(       label = 'Isto é um botão '        , width = w*0.9 , height = 50 )
        add_button(       label = 'E isso é um botão '      , width = w*0.44, height = 50 )
        add_same_line()
        add_button(       label= 'lado a lado '             , width = w*0.44, height = 50 )
        add_color_button( label = 'Isto é um botão colorido', width = w*0.9 , height = 50 , default_value = (55,102, 231,200) )
        add_spacing()
        add_radio_button( label = 'Radio button', items=['Isto', 'é', 'um', 'Radio', 'button'], horizontal = True )
        add_spacing()
        add_checkbox(     label = 'CheckBox 1')
        add_same_line()
        add_checkbox(     label = 'CheckBox 2')
        add_same_line()
        add_checkbox(     label = 'CheckBox 3')
        add_spacing() 
        with child( width = w*0.9, height = 100, label = 'Isto é um Child', border = True  ):
            add_text( 'Isto é uma Child')
            add_drawlist( label = 'Isto é um Draw_list', width=200, height = 400  , id = 7_3_1 )
            draw_text( parent = 731, text = 'Isto é um Draw_List' , pos = [10,0]  , size = 15  )
            draw_text( parent = 731, text = 'Super longo'         , pos = [10,20] , size = 15  )
            draw_text( parent = 731, text = 'Viu só'              , pos = [10,380], size = 15  )
        
        add_text('Clique aqui para abrir um ... ', id = 7_3_2 )
        with popup( parent = 7_3_2, mousebutton = mvMouseButton_Left):
            add_text( 'POPUP')
            add_button( label = 'Popup Com Botão também')
        
        add_spacing() 
        add_text( 'Um exemplo de color picker', bullet = True  ) 
        add_color_picker() 

def init_atuador():
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
        add_spacing(count= 3)

        with child( id=42_5_0, autosize_x= True, autosize_y= True, no_scrollbar=True, border= True ):
            add_text( 'Data Calculada:' )
            add_text( id = 42_5_1, default_value='No data')
            add_button(label="Atualizar", width=100, id = 42_5_2, callback= lambda : set_value( 42_5_1, str(dt.datetime.now().strftime('%A %d/%m/%Y - %H:%M:%S')) ) if sun_data.update_date() == None else 1 )
            add_same_line()
            add_button(label="Limpar", width=100, id = 42_5_3, callback= lambda : set_value( 42_5_1, 'No data' ) )

    # Step Motors Config 
    with window( label = 'Motores'    , id = 43_0, width= 455, height= 480, pos = [10,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as config_AT:
        windows['Atuadores'].append( config_AT )
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

        add_slider_float( id = 45_2, pos=[w*0.025,h-50], width= w*0.95, min_value= 0, max_value= math.pi/2, indent = 0.01, callback= move_alt )
        move_item_up(45_2)

    # General Draw 
    with window( label = 'Draw_Window', id = 46_0, width= 995, height= 480, pos = [470,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as draw_tracker_AT:
        windows['Atuadores'].append( draw_tracker_AT )  
    
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



screen_dimension = [ GetSystemMetrics(0), GetSystemMetrics(1) ] 

setup_viewport()
set_viewport_title ( title = 'Inicio'    )
set_viewport_pos   (    [55, 0]          )
set_viewport_width ( screen_dimension[0] )
set_viewport_height( screen_dimension[1] )
set_primary_window ( main_window, True   )

init_inicio()
init_visualizacao() 
init_atuador() 
init_configuracao() 

change_menu(None, None, 'Inicio' )


count = 0
while is_dearpygui_running():
    w, h = get_item_width( 1_0 ), get_item_height( 1_0 )
    render_dearpygui_frame()
    count += 1  

    if window_opened == 'Inicio':
        render_inicio()

    elif window_opened == 'Visualização geral':
        render_visualizacao() 

    elif window_opened == 'Atuadores':
        render_atuador()     
        
    elif window_opened == 'Configurações':
        render_configuracao() 
    
