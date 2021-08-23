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

with theme( default_theme = True ) as theme_id:
    add_theme_color( mvThemeCol_Button       , (255, 140, 23), category = mvThemeCat_Core )
    add_theme_style( mvStyleVar_FrameRounding,        5      , category = mvThemeCat_Core )
    # um azul bem bonito -> 52, 140, 215 

with theme( id = 99_0_2  ):
    add_theme_color( mvThemeCol_Button       , (52, 140, 215 ), category = mvThemeCat_Core )
    # um azul bem bonito -> 52, 140, 215 

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


def add_image_loaded( img_path ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )

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


setup_viewport()
screen_dimension = [ GetSystemMetrics(0), GetSystemMetrics(1) ] 

init_visualizacao() 

set_viewport_title( title = 'Visualização Geral' )
set_viewport_pos( [55,0] )
set_viewport_width(  screen_dimension[0] )
set_viewport_height( screen_dimension[1] )

set_primary_window( main_window, True )
change_menu(None, None, 'Visualização geral' )


count = 0
while is_dearpygui_running():
    render_dearpygui_frame()
    count += 1    

    if window_opened == 'Visualização geral':
        render_visualizacao() 
