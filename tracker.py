from dearpygui.simple import *
from dearpygui.core import * 

from utils.serial_reader import serialPorts

from Model import SunPosition
from Model import Motors

import numpy as np 

import datetime
import serial 
import ephem
import math


# Definições de exibição 
X, Y = get_main_window_size()
set_main_window_pos( 100,0 )
set_main_window_size( X, Y )
set_main_window_title('Supervisorio Tracker - Teste')

# Definição das cores e alfa 
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
    'orange'  : lambda alfa : [ 255,  69,   0, alfa ],
}


# FUNÇÕES 
map_val = lambda value, in_min, in_max, out_min, out_max : ((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min ) 

cos = lambda x : math.cos( x )
sin = lambda x : math.sin( x )
tg  = lambda x : math.tan( x )


# MACRO 
PADDING   = 25 
LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 425

# GLOBAIS
sun_angle_elevation   = 1 
sun_angle_azimute     = 2 

motor_angle_base      = 3
motor_angle_elevation = 4 

window_opened = ''

#port_list = serialPorts(11)
port_list = serialPorts(15)

# Configurações padrão 
w, h = 350, 225 
center = [w//2, h//2]
r = 75 

sun_data = SunPosition( LATITUDE, LONGITUDE, ALTITUDE )
sun_data.update_date()



# Janelas 
windows = {
    'Visualização geral'  : ['solar-pos', 'Atuação', 'AtuaçãoBase', 'AtuaçãoElevação', 'log' ], 
    'Configurações'       : [ ],
    'Sair'                : [ ],
    'Posição do sol'      : [ "Posição do sol - Visualização","Posição do sol - Altura","Posição do sol - Azimute", "Posição do sol - log" ],
    "Atuadores"           : [ "Controle##AT", 'Definição dos horários##AT', 'Data log das posições##AT', 'Retornos##AT', 'Azimute##AT', 'Altitude##AT' ], 
    "Atuação da base"     : [ ], 
    "Atuação da elevação" : [ ],
    'Clima'               : [ ],
    'Alerta'              : [ ],
    'GPS'                 : [ ],
    'Geração'             : [ ],
    }


# CALLBACKS 
def mouse_update(sender, data): 
    pos = get_mouse_pos( local = True )
    print(pos)

def render_update(sender, data):

    sunlight = sun_data.get_sunlight_hours()
    now = datetime.datetime.utcnow() 

    if window_opened == 'Visualização geral':
        # Definição da Latitude/Longitude 
        sun_data.latitude  = str( get_value('Latitude')  )
        sun_data.longitude = str( get_value('Longitude') )
        sun_data.update_coordenates()

        # Horário automático 
        if ( get_value('Hora manual') is False ):
            # Definição do dia local e hora local
            sun_data.update_date()
            set_value('Dia automatico', [ sun_data.year, sun_data.month, sun_data.day ] ) 
            set_value('Hora automatica', [ sun_data.hour, sun_data.minute, sun_data.second ] )
            set_value('Total segundos', sun_data.total_seconds )
            # Total de segundos no dia convertido entre 0 e 1
            total_seconds_converted = map_val(sun_data.total_seconds, 0, 24*3600, 0, 1)
            set_value('progressive', total_seconds_converted)
            # Dias Julianos 
            set_value( "Dia Juliano", sun_data.dia_juliano)

        else:
            # Pegando a data e hora passadas pelo usuário
            year, month, day     = get_value('Dia arbitrario')
            hour, minute, second = get_value('Hora arbitraria') 
            # Montar a data setada pelo usuário
            data = datetime.datetime( int(year), int(month), int(day), int(hour), int(minute), int(second) )
            sun_data.set_date( data )
            # Total de segundos no dia
            set_value('Total segundos##', sun_data.total_seconds)
            # Total de segundos no dia convertidos entre 0 e 1
            total_seconds_converted = map_val(sun_data.total_seconds, 0, 24*3600, 0, 1)
            set_value('progressive', total_seconds_converted)
            # Calculo do dia Juliano 
            set_value( "Dia Juliano##", sun_data.dia_juliano)

        # Setar o Azimute, Altitude e Elevação
        set_value('Azimute', math.degrees( sun_data.azi) )
        set_value('Altitude', math.degrees( sun_data.alt) )
        set_value('Elevação (m)', sun_data.altitude)

        # Seta as horas do sol calculando as horas minutos e segundos de segundos totais 
        diff_sunlight = (sun_data.sunset - sun_data.rising).seconds
        set_value('Horas de sol', [diff_sunlight//3600, (diff_sunlight//60)%60 , diff_sunlight%60 ] )

        # Setar as informações de Nascer do sol, Culminante (ponto mais alto) e Por do sol
        set_value('Nascer do sol', [ sun_data.rising.hour+sun_data.utc_local, sun_data.rising.minute, sun_data.rising.second ]  )
        set_value('Culminante',    [ sun_data.transit.hour+sun_data.utc_local, sun_data.transit.minute, sun_data.transit.second ] )
        set_value('Por do sol',    [ sun_data.sunset.hour+sun_data.utc_local, sun_data.sunset.minute, sun_data.sunset.second ] )    

    elif window_opened == 'Posição do sol'     : 
        
        # Definição da Latitude/Longitude 
        sun_data.latitude  = str( get_value('Latitude (º)##PS' ) )
        sun_data.longitude = str( get_value('Longitude (º)##PS') )
        sun_data.altitude  = get_value('Altura (m)##PS')
        sun_data.update_coordenates()


        
        set_value ( 'Data atual##PS'     , value = [ now.year, now.month, now.day ] )
        set_value ( 'Data de calculo##PS', value = [ sun_data.year, sun_data.month, sun_data.day ] )
        
        set_value ( 'Nascer do sol##PS', value = [ sun_data.rising.hour + sun_data.utc_local, sun_data.rising.minute , sun_data.rising. second] )        
        set_value ( 'Transição##PS'  , value = [ sun_data.transit.hour+ sun_data.utc_local, sun_data.transit.minute, sun_data.transit. second] )        
        set_value ( 'Por do sol##PS'    , value = [ sun_data.sunset.hour + sun_data.utc_local, sun_data.sunset.minute , sun_data.sunset. second] ) 

        set_value ( 'Horas de luz##PS'  , value = [sunlight.seconds//3600, (sunlight.seconds//60)%60, sunlight.seconds%60] ) 

        set_value ( 'Altitude (º)##PS'  , value = math.degrees( sun_data.alt) ) 
        set_value ( 'Azimute (º)##PS'   , value = math.degrees( sun_data.azi) )

        #set_value ( 'Sombra (m)##PS'    , value = get_value('Altura Obj (m)##PS')/tg( sun_data.alt -math.pi/2 ) )  # Tg(teta)/altura = Projeção da sombra
       
        set_value ( 'Altura (m)##PS'    , value = sun_data.altitude )
        set_value ( 'Latitude (º)##PS'  , value = float( sun_data.latitude  ) )
        set_value ( 'Longitude (º)##PS' , value = float( sun_data.longitude ) )

        set_value ( 'UTM local (h)##PS'     , value = sun_data.utc_local )


        

    elif window_opened == "Atuadores"           :
        pass

    elif window_opened == "Atuação da base"     :
        pass

    elif window_opened == "Atuação da elevação" :
        pass

    elif window_opened == 'Clima'               :
        pass

    elif window_opened == 'Alerta'              :
        pass

    elif window_opened == 'GPS'                 :
        pass

    elif window_opened == 'Geração'             :
        pass


    global sun_angle_azimute, sun_angle_elevation, motor_angle_base, motor_angle_elevation 

    sun_angle_azimute   = math.radians(sun_data.azi)
    sun_angle_elevation = math.radians(sun_data.alt) 

    motor_angle_base = motor_angle_base + (sun_angle_azimute - motor_angle_base) * get_delta_time() if abs(sun_angle_azimute - motor_angle_base) > 0.005 else motor_angle_base
    motor_angle_elevation = motor_angle_elevation + ( sun_angle_elevation - motor_angle_elevation) * get_delta_time() if abs(sun_angle_elevation - motor_angle_elevation) > 0.005 else motor_angle_elevation
    
    modify_draw_command('MotorElevação', 'Sun', p1 = [(w//2)+r*math.cos( sun_angle_elevation ), h//2+r*math.sin( sun_angle_elevation )] )
    modify_draw_command('MotorBase',     'Sun', p1 = [(w//2)+r*math.cos( sun_angle_azimute ), h//2+r*math.sin( sun_angle_azimute )] )

    modify_draw_command('MotorElevação', 'Motor', p1 = [(w//2)+r*math.cos( motor_angle_elevation ),  h//2+r*math.sin( motor_angle_elevation )] )
    modify_draw_command('MotorBase',     'Motor', p1 = [(w//2)+r*math.cos( motor_angle_base ),       h//2+r*math.sin( motor_angle_base      )] )
    

def hora_manual(sender, data):
    # Verifica a condição do CheckBox
    status = get_value('Hora manual')
    # Configuração dos parametros automáticos
    configure_item('Dia automatico', enabled = not status )
    configure_item('Hora automatica', enabled = not status)
    configure_item('Total segundos', enabled = not status)
    configure_item('Dia Juliano', enabled = not status)
    # Configuração dos parametros manuais 
    configure_item( "Hora arbitraria", enabled = status )
    configure_item( "Dia arbitrario", enabled = status )
    configure_item('Total segundos##', enabled = status )
    configure_item('Dia Juliano##', enabled = status)

def change_menu(sender, data):
    global window_opened 
    window_opened = sender
    # CLOSE ALL WINDOWS 
    for k in windows.keys():
        for i in windows[k]:
            hide_item(i)
    # OPEN THE RIGHT TAB WINDOW 
    to_open = windows[sender]
    for i in to_open:
        show_item(i)


# FUNÇÕES
def draw_sun_trajetory( name_drawboard, width, height, all_day = False, extremes = False ):
    # Ponto central e Raio 
    center = [width//2, height//2]
    r = width//2 - 20 if width+20 <= height else height//2 - 20

    # Desenho estático 
    draw_line( name_drawboard, p1 = [center[0] - r, center[1]], p2 = [center[0] + r, center[1]], color = color['gray'](155), thickness= 1 )
    
    # DESENHO DA LINHA DE NASCER DO SOL E POR DO SOL 
    ang = sun_data.get_azi_from_date( sun_data.rising )[1]
    draw_line( name_drawboard, p1 = center, p2 = [center[0] + r*cos(ang-math.pi/2), center[1] + r*sin(ang-math.pi/2)], color = color['orange'](155), thickness= 2 )
    ang = sun_data.get_azi_from_date( sun_data.sunset )[1] # [ alt , azi ]
    draw_line( name_drawboard, p1 = center, p2 = [center[0] + r*cos(ang-math.pi/2), center[1] + r*sin(ang-math.pi/2)], color = color['gray'](200), thickness= 2 )

    # Desenhos estáticos 
    draw_circle( name_drawboard, center, r, color['white'](200), fill = color['white'](10 ), thickness = 3 )
    draw_circle( name_drawboard, center, 3, color['white'](200), fill = color['white'](255), thickness = 2 )
    draw_text( name_drawboard, pos= [center[0] - (r + 20), center[1] -10 ], text = 'W', color = color['white'](200), size=20 )
    draw_text( name_drawboard, pos= [center[0] + (r +  5), center[1] -10 ], text = 'E', color = color['white'](200), size=20 )
    draw_text( name_drawboard, pos= [center[0] - 10 , center[1] - (r + 25)  ], text = 'N', color = color['white'](255), size=20 )
    
    # PEGA OS ANGULOS NOS PONTOS DA TRAJETÓRIA DO SOL 
    dots = sun_data.trajetory(100, all_day )

    # PONTOS DE ACORDO COM Azimute - Altitude 
    dots = [ [ x - math.pi/2 ,  y ] for x, y in dots ]
    dots = [ [ center[0] + cos(x)*r, center[1] + sin(x)*cos(y)*r ] for x, y in dots ]

    # DESENHO DO TRACEJADO E OS PONTOS COLORIDOS DE NASCER A POR DO SOL  
    draw_polyline( name_drawboard, dots, color= color['red'](155), thickness= 2, closed= False )
    for n, p in enumerate(dots):
        draw_circle( name_drawboard, p, radius = 2, color = [n*4, 255-n*2, n*2, 255] )
    
    # DESENHO DO SOL NA SUA POSIÇÃO 
    sun = [  sun_data.azi - math.pi/2, sun_data.alt ] 
    sun = [ center[0] + cos(sun[0])*r, center[1] + sin(sun[0])*cos(sun[1])*r ]
    
    draw_line( name_drawboard, p1 = center, p2 = sun, color = color['yellow'](200), thickness = 2 )
    draw_circle(name_drawboard, center = sun, radius = 10, color = color['yellow'](155), fill = color['yellow'](255) )

    if extremes: 
        min_date = sun_data.winter_solstice 

        max_date = sun_data.summer_solstice        
        sun_data.set_date( min_date )

def draw_semi_circle( name_draw, center, radius, angle_i, angle_f, color, segments = 360, closed = False, thickness = 1 ):
    angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
    points = [ [ center[0] + radius*cos(ang), center[1] - radius*sin(ang) ] for ang in angles ]
    draw_polyline ( name_draw, points = points, color= color, closed = closed, thickness= thickness )




# MAIN WINDOW WITH MENU BAR 
with window('main-window', autosize = True ):
    with menu_bar("MenuBar"):
        add_menu_item("Visualização geral", callback = change_menu )
        add_menu_item("Posição do sol", callback = change_menu)
        with menu("Atuação##"):
            add_menu_item("Atuadores"          , callback = change_menu)
            add_menu_item("Atuação da base"    , callback = change_menu)
            add_menu_item("Atuação da elevação", callback = change_menu)
        add_menu_item('Clima'        , callback = change_menu )
        add_menu_item('Alerta'       , callback = change_menu )
        add_menu_item('GPS'          , callback = change_menu )
        add_menu_item('Geração'      , callback = change_menu )
        add_menu_item("Configurações", callback = change_menu)
        add_menu_item('Sair'         , callback = change_menu)


# JANELAS DA VIEW - VISUALIZAÇÃO GERAL 
with window('solar-pos', width = 800, height = 375, x_pos = 10, y_pos = 25, no_move= True, no_resize= True, no_collapse= True, no_close= True ):
    add_text('Area para a posição do sol')
    add_drawing('Solar', width=800, height=285)
    draw_sun_trajetory('Solar', 800, 250)

    add_progress_bar('progressive', width=800, height=30 )

with window('Atuação', width = 800, height = 340, x_pos = 10, y_pos = 410, no_move= True, no_resize= True, no_collapse= True, no_close= True ):
    add_text('Área para a atução da posição dos paineis solares')
    # Janela de desenho do motor da base

with window('AtuaçãoBase', width = 385, height = 270, x_pos = 10, y_pos = 470, no_move= True, no_resize= True, no_collapse= True, no_close= True ):
    
    # Área de desenho 
    add_drawing('MotorBase', width = w, height = h)
    draw_circle('MotorBase', center, 75, color['white'](255), thickness=2 )
    draw_arrow('MotorBase', tag='Sun',   p1 = [ 0, 0 ], p2 = center, color = color['green'](155), thickness= 5, size=10)
    draw_arrow('MotorBase', tag='Motor', p1 = [ 0, 0 ], p2 = center, color = color['red'](155),   thickness= 5, size=10)
    draw_circle('MotorBase', center, 5, [255,255,0,175], fill=True )

with window('AtuaçãoElevação', width = 385, height = 270, x_pos = 410, y_pos = 470, no_move= True, no_resize= True, no_collapse=True, no_close= True ):
    # Área de desenho 
    add_drawing('MotorElevação', width= w, height=h)
    draw_circle('MotorElevação', center, r, color['white'](255), thickness=2 )
    draw_arrow('MotorElevação', tag='Sun',   p1 = [ 0, 0 ], p2 = center, color = color['green'](150), thickness= 5, size=10)
    draw_arrow('MotorElevação', tag='Motor', p1 = [ 0, 0 ], p2 = center, color = color['red'](200),   thickness= 5, size=10)
    draw_circle('MotorElevação', center, 5, color['yellow'](155), fill=True)

with window('log', width = 430, height = 725, x_pos = 820, y_pos = 25, no_move= True, no_resize= True, no_collapse= True, no_close= True ):
    #Informações gerais do sistema - Automático 
    add_text('Informações gerais do sistema')
    add_drag_float3('Dia automatico',format='%4.0f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float3('Hora automatica',format='%4.0f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float('Total segundos',format='%4.0f', speed=0.1, min_value = 0, max_value = 23*3600, no_input= True)
    add_spacing(count=1)
    add_drag_float('Dia Juliano',format='%4.0f', speed=0.1, min_value = 0, no_input= True)
    add_spacing(count=5)

    # Informações gerais do sistema - Manual 
    add_checkbox("Hora manual", default_value = False, callback= hora_manual )
    add_spacing(count=1)
    add_input_float3('Dia arbitrario', default_value= [2020, 12, 25], format='%.0f', enabled = False )
    add_spacing(count=1)
    add_input_float3('Hora arbitraria', default_value= [20, 30, 10], format='%.0f', enabled = False )
    add_spacing(count=1)
    add_drag_float('Total segundos##',format='%4.0f', speed=0.1, min_value = 0, max_value = 24*3600, no_input= True, enabled= False)
    add_spacing(count=1)
    add_drag_float('Dia Juliano##',format='%4.0f', speed=0.1, min_value = 0, no_input= True, enabled = False)
    add_spacing(count=10)
    
    # Definições de longitude e latitude local
    add_text('Definições de longitude e latitude local')
    add_input_float('Latitude', default_value= -29.165307659422155, format='%3.10f')
    add_spacing(count=1)
    add_input_float('Longitude', default_value= -54.89831672609559, format='%3.10f')
    add_spacing(count=10)

    # Informações do sol 
    add_text('Informacoes do sol')
    add_drag_float('Azimute',format='%4.2f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float('Altitude',format='%4.2f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float('Elevação (m)',format='%4.0f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float3('Horas de sol', format='%.0f', no_input= True)
    add_spacing(count=10)
    
    # Posições de interesse
    add_text("Posicoes de interesse")
    add_drag_float3('Nascer do sol',format='%.0f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float3('Culminante',format='%.0f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float3('Por do sol', format='%.0f', speed=1, no_input= True)
    add_spacing(count=1)


# JANELAS DA VIEW POSIÇÃO DO SOL ## PS      
with window('Posição do sol - Visualização', width = 800, height = 450, x_pos = 10, y_pos = 25, no_move= True, no_resize= True, no_collapse= True, no_close= True ):
    add_drawing('Solar##full', width = 800, height = 410 )
    draw_sun_trajetory('Solar##full', 800, 410, extremes= True )

with window('Posição do sol - Altura', width = 395, height = 270, x_pos = 10, y_pos = 480, no_move = True,  no_resize= True, no_collapse= True, no_close= True ):
   #w, h = 390, 270
    raio = 220

    add_drawing('Altura##Solar', width = 380, height = 232)
    draw_polyline('Altura##Solar', [ [ 50, 10 ], [ 50, raio+10 ], [ raio+50, raio+10 ] ], color=color['white'](200), thickness= 2 )
    draw_semi_circle( 'Altura##Solar', [50, raio+10], raio, 0, math.radians(91), color['white'](200), segments= 90, thickness= 2)
    
    # RENDERIZAÇÃO 
    ang = sun_data.get_azi_from_date( sun_data.transit )[0] # [ alt , azi ]
    draw_line('Altura##Solar', [50, raio+10 ], [50 + raio*cos(ang), 230 - raio*sin(ang)], color = color['red'](200), thickness= 2 )
    
    ang = sun_data.alt
    draw_arrow("Altura##Solar", [ 50 + raio*cos(ang), 230 - raio*sin(ang)], [50, raio + 10], color= color['yellow'](200), thickness= 3, size= 10 ) 
    draw_text('Altura##Solar', [380-75, 10], "Altura:", color= color['white'](255), size=15 )
    draw_text('Altura##Solar', [380-75, 25], str( round(math.degrees(ang)) ) + 'º', color= color['white'](255), size=15 )
    
with window('Posição do sol - Azimute', width = 395, height = 270, x_pos = 415, y_pos = 480, no_move = True,  no_resize= True, no_collapse= True, no_close= True ):
    add_drawing('Azimute##Solar', width = 380, height = 230)
    draw_circle('Azimute##Solar', center = [ 380//2, 230//2], radius= 100, color= color['white'](200), thickness= 2 )
    draw_line('Azimute##Solar', p1= [380//2 -100, 230//2], p2=  [380//2 +100, 230//2], color = color['gray'](200), thickness=2 )
    draw_text("Azimute##Solar", pos= [380//2 - 120, 230//2 -7.5], text='W', color=color['white'](200), size=20 )
    draw_text("Azimute##Solar", pos= [380//2 + 110, 230//2 -7.5], text='E', color=color['white'](200), size=20 )
    draw_text("Azimute##Solar", pos= [380//2-5, 230//2 -80], text= 'N', color= color['white'](255), size=20 )
    
    # RENDERIZAÇÃO
    ang = sun_data.get_azi_from_date( sun_data.rising )[1] # [ alt , azi ]
    draw_line('Azimute##Solar', p1 = [ 380//2, 230//2], p2 = [380//2 + 100*cos(ang-math.pi/2), 230//2 + 100*sin(ang-math.pi/2)], color = color['yellow'](200), thickness= 2 )
    ang = sun_data.get_azi_from_date( sun_data.sunset )[1] # [ alt , azi ]
    draw_line('Azimute##Solar', p1 = [ 380//2, 230//2], p2 = [380//2 + 100*cos(ang-math.pi/2), 230//2 + 100*sin(ang-math.pi/2)], color = color['gray'](200), thickness= 2 )
    ang = sun_data.azi 
    draw_arrow('Azimute##Solar', p2 = [ 380//2, 230//2], p1 = [380//2 + 100*cos(ang-math.pi/2), 230//2 + 100*sin(ang-math.pi/2)], color = color['red'](200), thickness= 2, size=10 )
    draw_text('Azimute##Solar', pos= [380-75, 10], text= "Azimute:", color= color['white'](255), size=15 )
    draw_text('Azimute##Solar', pos= [380-75, 25], text= str( round(math.degrees(ang)) ) + 'º', color= color['white'](255), size=15 )
    
    # FIM DA RENDERIZAÇÃO
    draw_circle('Azimute##Solar', center= [380//2, 230//2], radius= 3, color= color['white'](200), thickness=2, fill= color['black'](255))

with window('Posição do sol - log', width= 440, height= 725, x_pos = 815, y_pos= 25, no_move= True, no_resize= True, no_collapse= True, no_close= True ):
    
    #Informações gerais do sistema - Automático 
    add_text('Informações de data e calculo')
    add_drag_float3('Data atual##PS'     ,format='%4.0f', speed=1, no_input= True)
    add_spacing(count=2)
    add_drag_float3('Data de calculo##PS',format='%4.0f', speed=1, no_input= True)
    add_spacing(count=5)

    add_text('Informações de configurações do sol')
    add_drag_float3('Nascer do sol##PS' ,format='%4.0f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float3('Transição##PS'     ,format='%4.0f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float3('Por do sol##PS'    ,format='%4.0f', speed=1, no_input= True)
    add_spacing(count=5)

    add_text('Informações gerais')
    add_drag_float3('Horas de luz##PS'   ,format='%4.0f', speed=1, no_input= True)
    add_spacing(count=1)
    add_drag_float('Altitude (º)##PS'    ,format='%4.0f', speed=0.1, min_value = 0, max_value = 23*3600, no_input= True)
    add_spacing(count=1)
    add_drag_float('Azimute (º)##PS'     ,format='%4.0f', speed=0.1, min_value = 0, no_input= True)
    add_spacing(count=5)

    # CORRIGIR A REGRA DA SOMBRA 
    add_text('Projeção de sombras')
    add_drag_float('Altura Obj (m)##PS'  ,format='%4.2f', default_value= 100, speed=0.1, max_value = 1205 )
    add_spacing(count=1)
    add_drag_float('Sombra (m)##PS'      ,format='%4.2f', speed=0.1, min_value = 0, no_input= True)
    add_spacing(count=5)

    add_text('Informações locais')
    add_input_float('Altura (m)##PS'       ,default_value= 425 , format='%4.0f', step = 5 )
    add_spacing(count=1)
    add_input_float('Latitude (º)##PS'     ,default_value= -29.165307659422155, format='%4.10f', step= 0.001 )
    add_spacing(count=1)
    add_input_float('Longitude (º)##PS'    ,default_value=  -54.89831672609559, format='%4.10f', step= 0.001 )
    add_spacing(count=1)
    add_drag_float('UTM local (h)##PS'     ,format='%4.0f', speed=0.1, min_value = 0, no_input= True)
    add_spacing(count=5)


CONNECTED = False
def initComport(sender, data):
    port     = get_value('PORT##AT')
    baudrate = get_value('BAUDRATE##AT')
    timeout  = get_value('TIMEOUT##AT')

    try:
        comport = serial.Serial( port= port, baudrate = int(baudrate), timeout= timeout )
        print("Comport conectada")
        CONNECTED = True 
    except: 
        print("Comport não esta disponível")
        CONNECTED = False


# JANELAS DE ATUAÇÃO ## AT
with window('Controle##AT', width= 400, height= 725, x_pos= 10, y_pos= 25, no_move= True, no_resize= True, no_collapse= True, no_close= True ):    

    # FAZER UMA THREAD PARA ESCUTAR NOVAS CONEXÕES SERIAIS 
    add_combo('PORT##AT', default_value='COM', items= port_list )

    add_spacing( count= 1 )
    add_combo('BAUDRATE##AT', default_value= '9600', items=[ '9600', '57600', '115200'])
    add_spacing( count= 1 )
    add_input_int('TIMEOUT##AT', default_value= 1)
    add_spacing( count= 5 )
    add_button('Iniciar conexão##AT', callback= initComport, width=260 )

    add_spacing(count= 15)
    add_text('Definições dos motores de passo')
    add_spacing(count= 5)

    add_text("Motor de Rotação da base - Motor 1")
    add_spacing(count=2)
    add_text('Resolução:')
    add_input_float('ResoluçãoM1##AT', default_value= 1.8, min_value= 0.01, max_value= 180, format= '%3.2f', callback= lambda sender, data : set_value('PassosM1##AT', value = ( 360 / get_value('ResoluçãoM1##AT') ) ), label='' )
    add_text('Passos por volta')
    add_drag_float('PassosM1##AT', default_value=  360 / 1.8, format='%5.2f', no_input= True, label='' )
    add_spacing(count= 2)
    #add_text('Passos da correia (mm)')
    #add_input_float('CorreiaM1##AT',label='', default_value= 2 )
    #add_spacing(count= 2)
    add_text('Micro Passos do motor')
    add_combo('MicroPassosM1##AT', label='', default_value = '1/16', items= ['1', '1/2', '1/4', '1/8', '1/16', '1/32'] )
    add_spacing(count=10)

    add_text("Motor de Rotação da base - Motor 2")
    add_spacing(count=2)
    add_text('Resolução:')
    add_input_float('ResoluçãoM2##AT', default_value= 1.8, min_value= 0.01, max_value= 180, format= '%3.2f', callback= lambda sender, data : set_value('PassosM2##AT', value = ( 360 / get_value('ResoluçãoM2##AT') ) ), label='' )
    add_text('Passos por volta')
    add_drag_float('PassosM2##AT', default_value=  360 / 1.8, format='%5.2f', no_input= True, label='' )
    add_spacing(count= 2)
    #add_text('Passos da correia (mm)')
    #add_input_float('CorreiaM2##AT',label='', default_value= 2 )
    #add_spacing(count= 2)
    add_text('Micro Passos do motor')
    add_combo('MicroPassosM2##AT', label='', default_value = '1/16', items= ['1', '1/2', '1/4', '1/8', '1/16', '1/32'] )


with window('Definição dos horários##AT', width= 835, height= 300, x_pos= 420, y_pos= 25, no_move= True, no_resize= True, no_collapse= True, no_close= True):
    pass

with window('Data log das posições##AT', width= 400, height= 300, x_pos= 420, y_pos= 335, no_move= True, no_resize= True, no_collapse= True, no_close= True):
    pass

with window('Retornos##AT', width= 835, height= 300, x_pos= 420, y_pos= 25, no_move= True, no_resize= True, no_collapse= True, no_close= True):
    pass

with window('Azimute##AT', width= 835, height= 300, x_pos= 420, y_pos= 25, no_move= True, no_resize= True, no_collapse= True, no_close= True):
    pass

with window('Altitude##AT', width= 835, height= 300, x_pos= 420, y_pos= 25, no_move= True, no_resize= True, no_collapse= True, no_close= True):
    pass


# Chamada de callbacks de rotina 
set_mouse_drag_callback(mouse_update, 10)
set_render_callback( render_update )
change_menu('Visualização geral', None )
change_menu('Posição do sol', None )
change_menu('Atuadores', None )


# Inicia o dearpygui com a janela principal 
start_dearpygui( primary_window = 'main-window' )

