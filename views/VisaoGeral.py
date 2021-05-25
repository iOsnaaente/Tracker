from dearpygui.simple import * 
from dearpygui.core import * 

# JANELAS DA VIEW - VISUALIZAÇÃO GERAL 
with window('Solar_pos##VG'      , no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ):
    add_text('Area para a posição do sol')
    add_drawing('Solar', width = get_item_width('Solar_pos##VG')-20, height = get_item_height('Solar_pos##VG')-50)
    draw_sun_trajetory('Solar',  get_item_width('Solar_pos##VG')-20,  get_item_height('Solar_pos##VG')-50 )
    add_progress_bar('progressive', width= get_item_width('Solar_pos##VG'), height=30 )
    
with window('Atuação##VG'        , no_move = True, no_resize = True, no_collapse = True, no_close = True ):
    add_text('Área para a atução da posição dos paineis solares')
    # Janela de desenho do motor da base
    
with window('AtuaçãoBase##VG'    , no_move = True, no_resize = True, no_collapse = True, no_close = True ):
    
    # Área de desenho 
    add_drawing('MotorBase', width = w-10, height = h-10)
    draw_circle('MotorBase', center, 75, color['white'](255), thickness=2 )
    draw_arrow('MotorBase', tag='Sun',   p1 = [ 0, 0 ], p2 = center, color = color['green'](155), thickness= 5, size=10)
    draw_arrow('MotorBase', tag='Motor', p1 = [ 0, 0 ], p2 = center, color = color['red'](155),   thickness= 5, size=10)
    draw_circle('MotorBase', center, 5, [255,255,0,175], fill=True )
    
with window('AtuaçãoElevação##VG', no_move = True, no_resize = True, no_collapse = True, no_close = True ):
    # Área de desenho 
    add_drawing('MotorElevação', width= w-10, height=h-10)
    draw_circle('MotorElevação', center, r, color['white'](255), thickness=2 )
    draw_arrow('MotorElevação', tag='Sun',   p1 = [ 0, 0 ], p2 = center, color = color['green'](150), thickness= 5, size=10)
    draw_arrow('MotorElevação', tag='Motor', p1 = [ 0, 0 ], p2 = center, color = color['red'](200),   thickness= 5, size=10)
    draw_circle('MotorElevação', center, 5, color['yellow'](155), fill=True)
    
with window('log##VG'            , no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar = True ):
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

