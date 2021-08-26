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

from views.menuInicio            import *
from views.menuVisualizaçãoGeral import *
from views.menuAtuadores         import * 
from views.menuConfigurações     import * 


COMP : Serial = Serial() 
PATH      = os.path.dirname( __file__ )
PATH_IMG  = PATH + '\\utils\\img\\'

map_val   = lambda value, in_min, in_max, out_min, out_max : ((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min ) 
cos       = lambda x : math.cos( x )
sin       = lambda x : math.sin( x )
tg        = lambda x : math.tan( x )

DOM       = [ 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro' ]
LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 425
UTC_HOUR  = -3

sun_data  = SunPosition( LATITUDE, LONGITUDE, ALTITUDE )
sun_data.update_date()

CONNECTED     = False

DAY_2Compute  = 0.0 

MG_Resolucao  = MG_Steps   = MG_uStep = 0.0 
ME_Resolucao  = ME_Steps   = ME_uStep = 0.0 
MG_Angle      = ME_Angle   =            0.0  
MGSR_Angle    = MESR_Angle =            0.0 

SERIAL_INFO   = [ ]
buff_in       = [ ]
buff_bytes    = b''
BUFF_MAX      = 30 
buff_count    = 0

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

with theme( default_theme = True ) as theme_id:
    add_theme_color( mvThemeCol_Button       , (255, 140, 23), category = mvThemeCat_Core )
    add_theme_style( mvStyleVar_FrameRounding,        5      , category = mvThemeCat_Core )
    # um azul bem bonito -> 52, 140, 215 

screen_dimension = [ GetSystemMetrics(0), GetSystemMetrics(1) ] 

setup_viewport ( )
set_viewport_title ( title = 'Inicio' )
set_viewport_pos ( [55, 0] )
set_viewport_width (screen_dimension[0])
set_viewport_height (screen_dimension[1])
set_primary_window ( main_window, True )
 
init_inicio (windows, change_menu )
init_visualizacaoGeral(windows ) 
init_atuador (windows ) 
init_configuracoes (windows ) 

change_menu(None, None, 'Inicio' )

while is_dearpygui_running():
    w, h = get_item_width( 1_0 ), get_item_height( 1_0 )
    render_dearpygui_frame() 
    
    if   window_opened == 'Inicio'            : render_inicio () 
    elif window_opened == 'Visualização geral': render_visualizacaoGeral() 
    elif window_opened == 'Atuadores'         : render_atuador()     
    elif window_opened == 'Configurações'     : render_configuracao() 
