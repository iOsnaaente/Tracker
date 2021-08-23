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

cos = lambda x : math.cos( x )
sin = lambda x : math.sin( x )
tg  = lambda x : math.tan( x )

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


with theme( default_theme = True ) as theme_id:
    add_theme_color( mvThemeCol_Button       , (255, 140, 23), category = mvThemeCat_Core )
    add_theme_style( mvStyleVar_FrameRounding,        5      , category = mvThemeCat_Core )
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


def inicio_render():
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



screen_dimension = [ GetSystemMetrics(0), GetSystemMetrics(1) ] 

setup_viewport()
set_viewport_title ( title = 'Inicio' )

init_inicio() 

set_viewport_pos   ( [55,0] )
set_viewport_width ( screen_dimension[0] )
set_viewport_height( screen_dimension[1] )

set_primary_window( main_window, True )
change_menu(None, None, 'Inicio' )

count = 0
while is_dearpygui_running():
    w, h = get_item_width( 1_0 ), get_item_height( 1_0 )

    render_dearpygui_frame()
    count += 1  

    if window_opened == 'Inicio':
        inicio_render()

    if count == 30:
        #ajust_win( draw_tracker_AT  , [995, 480], [470, 360] )
        count = 0
