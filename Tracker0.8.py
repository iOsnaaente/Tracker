from win32api import GetSystemMetrics
from dearpygui.dearpygui import *

import sys 
import os 

screen_dimension = [ GetSystemMetrics(0), GetSystemMetrics(1) ] 
print(screen_dimension)

load_init_file('dpg.ini')

setup_viewport()
set_viewport_title( title = 'Controle dos motores - Unic' )
set_viewport_pos( [0,0] )
set_viewport_width( screen_dimension[0] )
set_viewport_height( screen_dimension[1] )

show_metrics()


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

# MAIN WINDOW 
with window( id = 1_0, autosize = True ) as main_window:
    with menu_bar(label = "MenuBar"):
        add_menu_item( label="Inicio"             , callback = change_menu, user_data = "Inicio"              )
        add_menu_item( label="Visualização geral" , callback = change_menu, user_data = "Visualização geral"  )
        add_menu_item( label="Posição do sol"     , callback = change_menu, user_data = "Posição do sol"      )
        add_menu_item( label="Atuadores"          , callback = change_menu, user_data = "Atuadores"           )
        add_menu_item( label="Atuação da base"    , callback = change_menu, user_data = "Atuação da base"     )
        add_menu_item( label="Atuação da elevação", callback = change_menu, user_data = "Atuação da elevação" )
        add_menu_item( label="Configurações"      , callback = change_menu, user_data = "Configurações"       )
        add_menu_item( label='Sair'               , callback = change_menu, user_data = 'Sair'                )


with window( id = 42_0, width= 455, height= 330, pos = [10,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as serial_AT: 
    windows['Atuadores'].append( serial_AT )

    add_spacing(count=2)
    add_text('CONFIGURAÇÕES DE COMUNICAÇÃO')

    # FAZER UMA THREAD PARA ESCUTAR NOVAS CONEXÕES SERIAIS 
    add_text('Selecione a porta serial: ')
    add_combo(label='PORT##AT', id=42_1, default_value='COM15', items= ['COM1', 'COM4', 'COM15', 'COM16'] )
    add_spacing( count= 1 )

    add_text('Baudarate: ')
    add_combo(label='BAUDRATE##AT', id=42_2, default_value= '115200', items=[ '9600', '57600', '115200'] )
    add_spacing( count= 1 )

    add_text('Timeout: ')
    add_input_int(label='TIMEOUT##AT', id=42_3, default_value= 1)
    add_spacing( count= 5 )

    add_button(label='Iniciar conexão##AT',  id=42_4, )
    add_spacing(count= 5)


with window( id = 43_0, width= 455, height= 480, pos = [10,360],  no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True ) as config_AT:
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

with window( label='Azimute', id = 44_0, width= 495, height= 330, pos = [470,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as azimute_config_AT: 
    windows['Atuadores'].append( azimute_config_AT)
    add_knob_float( id = 44_1, width= get_item_width(azimute_config_AT), height= get_item_height(azimute_config_AT) )

with window(label = 'Zenite', id = 45_0, width= 495, height= 330, pos = [970,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as zenite_config_AT:
    windows['Atuadores'].append( zenite_config_AT )  
    add_knob_float( id = 45_1, width= get_item_width(zenite_config_AT), height= get_item_width(zenite_config_AT) )


with window( id = 46_0, width= 995, height= 480, pos = [470,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as draw_tracker_AT:
    windows['Atuadores'].append( draw_tracker_AT )  
    add_text('draw_tracker_AT')



set_primary_window( main_window, True )
count = 0 

show_documentation()
show_style_editor()
show_font_manager()
show_item_registry()




while is_dearpygui_running():

    render_dearpygui_frame()
    save_init_file('dpg.ini')

    count += 1     

    if window_opened == 'Atuadores':
        SR_Port      = get_value( 42_1   )
        SR_Baudrate  = get_value( 42_2   )
        SR_Timeout   = get_value( 42_3   )  
        SR_Connected = get_value( 42_4   )
        MG_Resolucao = get_value( 43_1_1 ) 
        MG_Steps     = get_value( 43_1_2 ) 
        MG_uStep     = get_value( 43_1_3 ) 
        ME_Resolucao = get_value( 43_2_1 ) 
        ME_Step      = get_value( 43_2_2 ) 
        ME_uStep     = get_value( 43_2_3 ) 
        MG_Angle     = get_value( 44_1   ) 
        ME_Angle     = get_value( 45_1   ) 
        print("Atuadores: ", SR_Port, SR_Baudrate, SR_Timeout, SR_Connected, MG_Resolucao, MG_Steps, MG_uStep, ME_Resolucao, ME_Step, ME_uStep, MG_Angle, ME_Angle )

    if count == 30:
        ajust_win( serial_AT        , [455, 330], [10 , 25 ] )
        ajust_win( config_AT        , [455, 480], [10 , 360] )
        ajust_win( azimute_config_AT, [495, 330], [470, 25 ] )
        ajust_win( zenite_config_AT , [495, 330], [970, 25 ] )
        ajust_win( draw_tracker_AT  , [995, 480], [470, 360] )
        count = 0
