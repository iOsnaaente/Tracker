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

map_val = lambda value, in_min, in_max, out_min, out_max : ((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min ) 
cos     = lambda x : math.cos( x )
sin     = lambda x : math.sin( x )
tg      = lambda x : math.tan( x )

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

MG_Angle      = 30.0
ME_Angle      = 40.0  

AZI_Angle = 0.0 
ALT_Angle = 0.0 

LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 425
UTC_HOUR  = -3

sun_data  = SunPosition( LATITUDE, LONGITUDE, ALTITUDE )
sun_data.update_date()



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

def ajust_win( obj, o_wh : list, o_pos : list) -> list :    
    cw = get_item_width( main_window ) / 1474
    ch = get_item_height( main_window )/ 841 

    set_item_width(  obj, cw*o_wh[0] ) 
    set_item_height( obj, ch*o_wh[1] ) 
    set_item_pos(    obj, [ cw*o_pos[0], ch*o_pos[1] ] ) 

def add_image_loaded( img_path ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )



# FUNÇÕES
def draw_sun_trajetory( draw_id, parent_id, all_day = False, extremes = False ):
    # Ponto central, dimensões da tela e Raio 
    width, height = get_item_width( draw_id ), get_item_height( draw_id )
    w, h          = get_item_width(1_0)      , get_item_height(1_0)
    center        = [ width//2, height//2 ]
    r             =   width//2 - 20 if width+20 <= height else height//2 - 20
    id_link       = draw_id*100

    # DESENHO DA LINHA DE NASCER DO SOL E POR DO SOL 
    azi = sun_data.get_azi_from_date( sun_data.rising )[1]
    alt = sun_data.get_azi_from_date( sun_data.sunset )[1] # [ alt , azi ]

    # PEGA OS ANGULOS NOS PONTOS DA TRAJETÓRIA DO SOL 
    dots = sun_data.trajetory(100, all_day )
    # PONTOS DE ACORDO COM Azimute - Altitude 
    dots = [ [ x - math.pi/2 ,  y ] for x, y in dots ]
    dots = [ [ center[0] + cos(x)*r, center[1] + sin(x)*cos(y)*r ] for x, y in dots ]

    # DESENHO DO SOL NA SUA POSIÇÃO 
    sun = [  sun_data.azi - math.pi/2, sun_data.alt ] 
    sun = [ center[0] + cos(sun[0])*r, center[1] + sin(sun[0])*cos(sun[1])*r ]
    
    draw_line(     parent = draw_id, id = id_link+1 , p1     = [center[0] - r, center[1]]              , p2     = [center[0] + r, center[1]]                                          , color     = color['gray'](155)  , thickness = 1 )
    draw_line(     parent = draw_id, id = id_link+2 , p1     = center                                  , p2     = [center[0] + r*cos(azi-math.pi/2), center[1] + r*sin(azi-math.pi/2)], color     = color['orange'](155), thickness = 2 )
    draw_line(     parent = draw_id, id = id_link+3 , p1     = center                                  , p2     = [center[0] + r*cos(alt-math.pi/2), center[1] + r*sin(alt-math.pi/2)], color     = color['gray'](200)  , thickness = 2 )
    draw_circle(   parent = draw_id, id = id_link+4 , center = center                                  , radius = r                                                                   , color     = color['white'](200) , fill      = color['white'](10 ), thickness = 3 )
    draw_circle(   parent = draw_id, id = id_link+5 , center = center                                  , radius = 3                                                                   , color     = color['white'](200) , fill      = color['white'](255), thickness = 2 )
    draw_text(     parent = draw_id, id = id_link+6 , pos    = [center[0] -(r +20), center[1] -10 ]    , text   = 'W'                                                                 , color     = color['white'](200) , size      = 20 )
    draw_text(     parent = draw_id, id = id_link+7 , pos    = [center[0] +(r +5) , center[1] -10 ]    , text   = 'E'                                                                 , color     = color['white'](200) , size      = 20 )
    draw_text(     parent = draw_id, id = id_link+8 , pos    = [center[0] -10     , center[1] -(r +25)], text   = 'N'                                                                 , color     = color['white'](255) , size      = 20 )
    draw_polyline( parent = draw_id, id = id_link+9 , points = dots                                    , color  = color['red'](155)                                                    , thickness = 2                   , closed    = False )
    for n, p in enumerate(dots):
        draw_circle( parent = draw_id, id = id_link+(12+n) , center = p     , radius = 2  , color = [n*4, 255-n*2, n*2, 255]                              ) 
    draw_line(       parent = draw_id, id = id_link+10     , p1     = center, p2     = sun, color = color['yellow'](200)    , thickness = 2               )
    draw_circle(     parent = draw_id, id = id_link+11     , center = sun   , radius = 10 , color = color['yellow'](155)    , fill = color['yellow'](255) )

# CORRIGIR A GEOMETRIA DE DESENHO DA TRAJETÓRIA DO SOL 
def update_sun_trajetory( draw_id, parent_id, all_day = False ): 
    # Ponto central, dimensões da tela e Raio 
    width, height = get_item_width( draw_id ), get_item_height( draw_id )
    w, h          = get_item_width(1_0)      , get_item_height(1_0)
    center        = [ width//2, height//2 ]
    r             = width//2 - 20 if width+20 <= height else height//2 - 20
    id_link       = draw_id*100
    
    # DESENHO DA LINHA DE NASCER DO SOL E POR DO SOL 
    azi = sun_data.get_azi_from_date( sun_data.rising )[1]
    alt = sun_data.get_azi_from_date( sun_data.sunset )[1] # [ alt , azi ]
    
    # PEGA OS ANGULOS NOS PONTOS DA TRAJETÓRIA DO SOL 
    dots = sun_data.trajetory(100, all_day )
    dots = [ [ x - math.pi/2 ,  y ] for x, y in dots ]
    dots = [ [ center[0] + cos(x)*r, center[1] + sin(x)*cos(y)*r ] for x, y in dots ]
    
    # DESENHO DO SOL NA SUA POSIÇÃO 
    sun = [  sun_data.azi - math.pi/2, sun_data.alt ] 
    sun = [ center[0] + cos(sun[0])*r, center[1] + sin(sun[0])*cos(sun[1])*r ]
    
    # DESENHO ESTÁTICO
    configure_item( id_link+1 , p1     = [center[0] - r, center[1]], p2     = [center[0] + r, center[1]]                                           )
    configure_item( id_link+2 , p1     = center                    , p2     = [center[0] + r*cos(azi-math.pi/2), center[1] + r*sin(azi-math.pi/2)] )
    configure_item( id_link+3 , p1     = center                    , p2     = [center[0] + r*cos(alt-math.pi/2), center[1] + r*sin(alt-math.pi/2)] )
    configure_item( id_link+4 , center = center                    , radius = r      )
    configure_item( id_link+5 , center = center                    , radius = 3      )
    configure_item( id_link+6 , pos    = [center[0] - (r + 20), center[1] -10 ]      )
    configure_item( id_link+7 , pos    = [center[0] + (r +  5), center[1] -10 ]      )
    configure_item( id_link+8 , pos    = [center[0] - 10 , center[1] - (r + 25) ]    )
    configure_item( id_link+9 , points = dots                                        )
    configure_item( id_link+10, p1     = center                    , p2     = sun    )
    configure_item( id_link+11, center = sun                                         )
    for n, p in enumerate(dots):
        configure_item( id_link+(12+n) , center = p )

def get_semi_circle_points( center, radius, angle_i, angle_f, segments = 360, closed = False ):
    points_close = [[ center[0], center[1]-radius ] ,  center, [ center[0] + radius, center[1] ] ] 
    angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
    points =  [ [ center[0] + radius*cos(ang), center[1] - radius*sin(ang) ] for ang in angles ] 
    if closed: 
        points_close.extend( points )
        return points_close 
    else:      
        return points 

with window( label = 'Posição solar'    , id = 2_1_0, pos = [50,50], width = 500, height = 500, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as Posicao_sol_VG:
    windows["Visualização geral"].append( Posicao_sol_VG )
    w, h = get_item_width(2_1_0), get_item_height(2_1_0)
    add_drawlist( id = 2_1_1_0, width = w-20, height = h-50, label = 'Solar')
    draw_sun_trajetory( draw_id = 2_1_1_0, parent_id = 2_1_0 )
    add_progress_bar(  id = 2_1_2,   width = w   , height = 30  )

with window( label = 'Atuação'          , id = 2_2_0, no_move = True, no_resize = True, no_collapse = True, no_close = True ) as Atuacao_VG:
    windows["Visualização geral"].append( Atuacao_VG )
    add_text('Área para a atução da posição dos paineis solares')
    w, h   = get_item_width(2_2_0), get_item_height(2_2_0) 
    center = cw, ch =  w//2 , h//2 
    r = 100 

    # GIR 
    def att_draw_gir():
        global AZI_Angle
        global MG_Angle 
        w_gir, h_gir = [ get_item_width(2_2_1_1_0)//2, get_item_height(2_2_1_1_0)//2 ]
        r_gir        = w_gir*0.8 if w_gir<h_gir else h_gir*0.8 
        center_gir   = [ w_gir+r_gir, h_gir ]  
        configure_item( 2_2_1_1_0, width  = get_item_width(2_2_1_0)*0.9                                , height = get_item_height(2_2_1_0)*0.9 )
        configure_item( 2_2_1_1_1, center = center_gir                                                 , radius = r_gir                    ) 
        configure_item( 2_2_1_1_2, p1     = [ r_gir*cos(math.radians(MG_Angle )-math.pi/2)+center_gir[0], r_gir*sin(math.radians(MG_Angle )-math.pi/2) +h_gir ] , p2     = center_gir               ) 
        configure_item( 2_2_1_1_3, p1     = [ r_gir*cos(math.radians(AZI_Angle)-math.pi/2)+center_gir[0], r_gir*sin(math.radians(AZI_Angle)-math.pi/2)+h_gir ] , p2     = center_gir               ) 
        configure_item( 2_2_1_1_4, center = center_gir                                                 , radius = 5                       ) 
        configure_item( 2_2_1_1_5, size = r_gir/6.5, text   = 'Azimute:\n\nAzimute Medida:\n%.4f \nAzimute Motor:\n%.4f \n\nAzimute Minima:\nHora:  %s\nValor: %.4f\n\nAzimute Máxima:\nHora:  %s\nValor: %.4f ' %( AZI_Angle, MG_Angle, str(sun_data.rising).split(' ')[1], sun_data.azimute_sunrise ,str(sun_data.sunset).split(' ')[1], sun_data.azimute_sunset )  )

    with child( label = 'AtuaçãoGiro'   , id = 2_2_1_0, width = w*0.9, height = h*0.9 ):
        r_gir = w*0.9 if w < h else h*0.9 
        add_drawlist( id     = 2_2_1_1_0, width = cw*0.9, height = ch*0.9)
        draw_circle(  parent = 2_2_1_1_0, id = 2_2_1_1_1, center = center, radius = r_gir   , color = color['white'](255) , thickness =2                )
        draw_arrow(   parent = 2_2_1_1_0, id = 2_2_1_1_2, p1 = [ 0, 0 ]  , p2     = center  , color = color['green'](155) , thickness = 5, size = 5     )
        draw_arrow(   parent = 2_2_1_1_0, id = 2_2_1_1_3, p1 = [ 0, 0 ]  , p2     = center  , color = color['red'](155)   , thickness = 5, size = 5     )
        draw_circle(  parent = 2_2_1_1_0, id = 2_2_1_1_4, center = center, radius = 5       , color = color['yellow'](175), fill = color['yellow'](255) )
        draw_text(    parent = 2_2_1_1_0, id = 2_2_1_1_5, text = ''      , pos    = [10, 10]                                                             )
    
    # ELE 
    def att_draw_ele() :
        global ME_Angle
        global ALT_Angle
        w_ele, h_ele = [ get_item_width(2_2_2_1_0)//2, get_item_height(2_2_2_1_0)//2 ]
        r_ele        = w_ele*1.8 if w_ele < h_ele else h_ele*1.8
        center_ele   = [ w_ele - r_ele*0.1, r_ele+10]
        configure_item( 2_2_2_1_0, width  = get_item_width(2_2_2_0)*0.9  , height = get_item_height(2_2_2_0)*0.9 )
        configure_item( 2_2_2_1_1, points = get_semi_circle_points(        center = center_ele         , radius = r_ele, angle_i = 0, angle_f = math.radians(91), segments= 90, closed = True  )  )
        if ALT_Angle < 0 : configure_item( 2_2_2_1_3, p1 =  center_ele, p2 = center_ele )
        else:              configure_item( 2_2_2_1_3, p1 = [ r_ele*cos(math.radians(-ALT_Angle))+center_ele[0], r_ele*sin(math.radians(-ALT_Angle))+center_ele[1] ] , p2 = center_ele )
        configure_item( 2_2_2_1_2                   , p1 = [ r_ele*cos(math.radians(-ME_Angle ))+center_ele[0], r_ele*sin(math.radians(-ME_Angle )) +center_ele[1] ] , p2 = center_ele )
        configure_item( 2_2_2_1_4                   , center = center_ele                  , radius = 5 )
        configure_item( 2_2_2_1_5, text = 'Altitude:\n\nAltitude Medida:\n%.4f\nAltitude Motor:\n%.4f\n\nAltitude Máxima:\nData:  %s\nHora:  %s\nValor: %.4f ' %( ALT_Angle, ME_Angle, str(sun_data.transit).split(' ')[0], str(sun_data.transit).split(' ')[1], sun_data.elevation_transit) )
        configure_item( 2_2_2_1_5, size = r_ele/15 ) 

    with child(label = 'AtuaçãoElevação', id = 2_2_2_0, width = w*0.9, height = h*0.9 ):
        w, h = get_item_width( 2_2_2_0 ), get_item_height( 2_2_2_0 )
        r    = w//1.3 if w < h else h//1.3
        add_drawlist( id = 2_2_2_1_0, width  = cw*0.9 , height = ch*0.9 )
        points = get_semi_circle_points(center = [ 10, 100 + r], radius = r, angle_i = 0, angle_f = math.radians(91), closed = True, segments= 90 )  
        draw_polyline( parent = 2_2_2_1_0, id = 2_2_2_1_1, points = points, color = color['white'](200), thickness= 2 )
        draw_arrow(    parent = 2_2_2_1_0, id = 2_2_2_1_2, p1 = [ 0, 0 ]  , p2 = center, color = color['green'](150) , thickness= 5, size=10)
        draw_arrow(    parent = 2_2_2_1_0, id = 2_2_2_1_3, p1 = [ 0, 0 ]  , p2 = center, color = color['red'](200)   , thickness= 5, size=10)
        draw_circle(   parent = 2_2_2_1_0, id = 2_2_2_1_4, center = center, radius = 5 , color = color['yellow'](155), fill=color['yellow'](255))
        draw_text(     parent = 2_2_2_1_0, id = 2_2_2_1_5, text = "", pos = [10,10] )

with window( label = 'Painel de log'       , id = 2_3_0, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar = True ) as Painel_log_VG:
    windows["Visualização geral"].append( Painel_log_VG )
    
    #Informações gerais do sistema - Automático 
    add_text('Informações gerais do sistema')
    add_drag_floatx( label = 'Ano/Mes/Dia Auto'  , id = 2_3_1, size = 3, format = '%4.0f', min_value = 1, max_value = 3000, speed = 1, no_input= True, )
    add_spacing(count = 1)
    add_drag_floatx( label = 'Hora/Min/Sec Auto' , id = 2_3_2, size = 3, format = '%4.0f', speed = 1, no_input = True)
    add_spacing(count = 1)
    add_drag_float( label = 'Valor no dia'   , id = 2_3_3, format = '%4.0f', speed = 0.1, min_value = 0, max_value = 26*3600, no_input = True)
    add_spacing(count = 1)
    add_drag_float( label = 'Dia Juliano'      , id = 2_3_4, format = '%4.0f', speed = 0.1, min_value = 0, max_value = 366, no_input = True)
    add_spacing(count = 5)

    # Informações gerais do sistema - Manual 
    add_checkbox(     label = "Hora manual"    , id = 2_3_5, default_value = False )
    add_spacing(count = 1 )
    add_input_floatx( label = 'Ano/Mes/Dia Manual' , id = 2_3_6, size = 3, default_value = [2020, 12, 25], format='%.0f', min_value = 1, max_value = 3000, enabled = False )
    add_spacing(count = 1 )
    add_input_floatx( label = 'Hora/Min/Sec Manual', id = 2_3_7, size = 3, default_value = [20, 30, 10]  , format='%.0f', min_value = 1, max_value = 60, enabled = False )
    add_spacing(count = 1 )
    add_drag_float(  label = 'Valor no dia'  , id = 2_3_8, format = '%4.0f', speed = 0.1 , min_value = 0, max_value = 24*3600, no_input= True, enabled= False)
    add_spacing(count = 1 )
    add_drag_float(  label = 'Dia Juliano'     , id = 2_3_9, format = '%4.0f', speed = 0.1 , min_value = 0, max_value = 366, no_input= True, enabled = False)
    add_spacing(count = 10)
    
    # Definições de longitude e latitude local
    add_text('Definições de longitude e latitude local')
    add_input_float( label = 'Latitude' , id = 2_3_10, default_value = -29.165307659422155, min_value = -90, max_value = 90, format = '%3.5f', indent=0.01  )
    add_spacing(count = 1)
    add_input_float( label = 'Longitude', id = 2_3_11, default_value = -54.89831672609559 , min_value = -90, max_value = 90, format = '%3.5f', indent=0.01 )
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
    add_text("Posicoes de interesse", )
    add_text('Nascer do sol (hh/mm/ss)')
    add_drag_floatx( id = 2_3_16, size = 3, format='%.0f', speed=1, no_input= True)
    add_spacing(count = 1)
    add_text('Culminante (hh/mm/ss)'   )
    add_drag_floatx( id = 2_3_17, size = 3, format='%.0f', speed=1, no_input= True)
    add_spacing(count = 1)
    add_text('Por do sol (hh/mm/ss)'   )
    add_drag_floatx( id = 2_3_18, size = 3, format='%.0f', speed=1, no_input= True)
    add_spacing(count = 1)
    add_spacing(count=1)

def render_visualizacao():
    global MG_Angle 
    global ME_Angle 

    global AZI_Angle
    global ALT_Angle

    w , h  = get_item_width( 1_0   ), get_item_height( 1_0   ) # get the main_window dimension 
    w1, h1 = get_item_width( 2_1_0 ), get_item_height( 2_1_0 ) # get the child_window dimension 
    w2, h2 = get_item_width( 2_2_0 ), get_item_height( 2_2_0 ) 

    configure_item( 2_1_0    , width = w*2/3       , height    = h*3/5       , pos = [10 , 25 ]               ) # DESENHO 
    configure_item( 2_1_1_0  , width = w1-20       , height    = h1-50                                        ) # DRAWLIST
    update_sun_trajetory(     draw_id = 2_1_1_0    , parent_id = 2_1_0                                        ) # DRAWING 

    configure_item( 2_1_2    , width = (w*2/3)-20  , height    =  25         , pos = [ 10       , (h*3/5)-50] ) # PROGRESSIVE BAR 

    configure_item( 2_2_0    , width =  w*2/3      , height    = (h*2/5)-35  , pos = [10 , (h*3/5)+30 ]       ) # ATUADORES 
    configure_item( 2_2_1_0  , width = (w/3)-15    , height    = (h*2/5)*0.8 , pos = [ 5            , 20 ]    ) # GIRO
    configure_item( 2_2_2_0  , width = (w/3)-15    , height    = (h*2/5)*0.8 , pos = [ (w*2/3)//2 +5, 20 ]    ) # ELEVAÇÃO 

    configure_item( 2_3_0    , width =  w/3 -20     , height    =  h - 30     , pos = [ w*2/3 +15, 25 ]        ) # LOG 


    # Definição da Latitude/Longitude 
    sun_data.latitude  = str( get_value(2_3_10) ) # LATITUDE
    sun_data.longitude = str( get_value(2_3_11) ) # LONGITUDE 
    sun_data.update_coordenates()

    # Horário automático 
    if ( get_value( 2_3_5 ) == False ):           # HORA MANUAL 
        sun_data.update_date()
        set_value( 2_3_1, value = [ sun_data.year, sun_data.month, sun_data.day ] )      # DIA ATUTOMÁTICO 
        set_value( 2_3_2, value = [ sun_data.hour, sun_data.minute, sun_data.second ] )  # HORA AUTOMÁTICA
        set_value( 2_3_3, value = sun_data.total_seconds )                               # TOTAL DE SEGUNDOS 
        # Total de segundos no dia convertido entre 0 e 1
        total_seconds_converted = map_val(sun_data.total_seconds, 0, 24*3600, 0, 1)
        set_value( 2_1_2, total_seconds_converted)                               # BARRA PROGRESSIVA 
        set_value( 2_3_4, sun_data.dia_juliano%360)                                  # DIA JULIANO 

        disable_item(2_3_6) 
        disable_item(2_3_7) 

    else:
        enable_item( 2_3_6)
        enable_item( 2_3_7)

        # Pegando a data e hora passadas pelo usuário
        year, month, day     = get_value( 2_3_6 )[:3]                                # DIA ARBITRÁRIO 
        hour, minute, second = get_value( 2_3_7 )[:3]                                # HORA ARBITRÁRIA

        # Montar a data setada pelo usuário
        try: 
            data = dt.datetime( int(year), int(month), int(day), int(hour), int(minute), int(second) )
            sun_data.set_date( data )
        except:
            pass 

        set_value( 2_3_8, sun_data.total_seconds)                               # TOTAL DE SEGUNDOS 
        
        # Total de segundos no dia convertidos entre 0 e 1
        total_seconds_converted = map_val(sun_data.total_seconds, 0, 24*3600, 0, 1)
        set_value( 2_1_2, total_seconds_converted)                              # BARRA PROGRESSIVA  
        set_value( 2_3_9, sun_data.dia_juliano % 360)                                 # DIA JULIANO

    # Setar o Azimute, Altitude e Elevação
    set_value( 2_3_12, math.degrees( sun_data.azi) ) #  AZIMUTE               
    set_value( 2_3_13, math.degrees( sun_data.alt) ) #  ALTITUDE               
    set_value( 2_3_14, sun_data.altitude           ) #  ELEVAÇÃO
    
    AZI_Angle = get_value( 2_3_12 ) 
    ALT_Angle = get_value( 2_3_13 )

    att_draw_gir()
    att_draw_ele() 

    # Seta as horas do sol calculando as horas minutos e segundos de segundos totais 
    diff_sunlight = (sun_data.sunset - sun_data.rising).seconds
    set_value( 2_3_15, [diff_sunlight//3600, (diff_sunlight//60)%60 , diff_sunlight%60 ] )

    # Setar as informações de Nascer do sol, Culminante (ponto mais alto) e Por do sol
    set_value( 2_3_16, [ sun_data.rising.hour+sun_data.utc_local , sun_data.rising.minute , sun_data.rising.second  ] ) # 'Nascer do sol'
    set_value( 2_3_17, [ sun_data.transit.hour+sun_data.utc_local, sun_data.transit.minute, sun_data.transit.second ] ) # 'Culminante'   
    set_value( 2_3_18, [ sun_data.sunset.hour+sun_data.utc_local , sun_data.sunset.minute , sun_data.sunset.second  ] ) # 'Por do sol'      

setup_viewport()
screen_dimension = [ GetSystemMetrics(0), GetSystemMetrics(1) ] 

set_viewport_title( title = 'Visualização Geral' )
set_viewport_pos( [55,0] )
set_viewport_width(  screen_dimension[0] )
set_viewport_height( screen_dimension[1] )

set_primary_window( main_window, True )
change_menu(None, None, 'Visualização geral' )

while is_dearpygui_running():
    render_dearpygui_frame()
    if window_opened == 'Visualização geral':
        render_visualizacao() 
