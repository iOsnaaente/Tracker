from dearpygui.dearpygui         import *

from views.menuInicio            import *
from views.menuVisualizacaoGeral import *
from views.menuPosicaoDoSol      import *
from views.menuAtuadores         import * 
from views.menuSensores          import * 
from views.menuRedNodeComm       import * 
from views.menuConfigurações     import * 

from utils.Model                 import SunPosition
from serial                      import Serial
from time                        import sleep 

import os

COMP : Serial = Serial() 
PATH      = os.path.dirname( __file__ )
PATH_IMG  = PATH + '\\utils\\img\\'

DOM       = [ 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro' ]
LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 425
UTC_HOUR  = -3

sun_data  = SunPosition( LATITUDE, LONGITUDE, ALTITUDE )
sun_data.update_date()

CONNECTED    = False

DAY_2Compute = 0.0 

MG_Resolucao = MG_Steps   = MG_uStep = 0.0 
ME_Resolucao = ME_Steps   = ME_uStep = 0.0 
MG_Angle     = ME_Angle   =            0.0  
MGSR_Angle   = MESR_Angle =            0.0 

SERIAL_INFO  = [ ]
buff_in      = [ ]
buff_bytes   = b''
BUFF_MAX     = 30 
buff_count   = 0

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
            "Visualizacao geral" : [  ],
            "Posicao do sol"     : [  ],
            "Atuadores"          : [  ],
            "Atuacao da base"    : [  ],
            "Atuacao da elevacao": [  ],
            "Sensores"           : [  ],
            "Rednode comunicacao": [  ],
            "Configuracoes"      : [  ],
            'Sair'               : [  ],
            }

window_opened = ''

def add_image_loaded( img_path ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )

def configure_viewport():
    setup_viewport ( )
    set_viewport_large_icon( PATH + 'ico\\large_ico.ico'              )
    set_viewport_small_icon( PATH + 'ico\\small_ico.ico'              ) 
    set_viewport_min_height( height = 900                             ) 
    set_viewport_min_width ( width  = 1000                            ) 
    set_viewport_title     ( title  = 'JetTracker - Controle do sol'  )

    maximize_viewport() 

    set_primary_window    ( main_window, True    )

    init_inicio           ( windows, change_menu )
    init_visualizacaoGeral( windows              ) 
    init_posicaoDoSol     ( windows              )
    init_atuador          ( windows              ) 
    init_sensores         ( windows              ) 
    init_rednodecom       ( windows              ) 
    init_configuracoes    ( windows              ) 

def resize_mainwindow (): 
    if   window_opened == 'Inicio'            : resize_inicio () 
    elif window_opened == 'Visualizacao geral': resize_visualizacaoGeral() 
    elif window_opened == 'Posicao do sol'    : resize_posicaoDoSol()
    elif window_opened == 'Atuadores'         : resize_atuador()     
    elif window_opened == 'Sensores'          : resize_sensores()  
    elif window_opened == 'Rednode comunicacao': resize_rednodecom()  
    elif window_opened == 'Configuracoes'     : resize_configuracoes()  

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

    resize_mainwindow() 

def closing_dpg( sender, data, user ): 
    with window( pos = [ get_item_width(10)/2.5, get_item_height(10)/2.5]): 
        add_text( 'Obrigado por usar nosso programa\nEle irá encerrar em instantes' )
    sleep(2)
    stop_dearpygui() 

# Main Window 
with window( label = 'Main Window', id = 1_0, autosize = True ) as main_window:
    with menu_bar(label = "MenuBar"):
        add_menu_item( label="Inicio"             , callback = change_menu, user_data = "Inicio"              )
        add_menu_item( label="Visualização geral" , callback = change_menu, user_data = "Visualizacao geral"  )
        add_menu_item( label="Posição do sol"     , callback = change_menu, user_data = "Posicao do sol"      )
        add_menu_item( label="Atuadores"          , callback = change_menu, user_data = "Atuadores"           )
        add_menu_item( label="Atuação da base"    , callback = change_menu, user_data = "Atuacao da base"     )
        add_menu_item( label="Atuação da elevação", callback = change_menu, user_data = "Atuacao da elevacao" )
        add_menu_item( label="Sensores"           , callback = change_menu, user_data = "Sensores"            )
        add_menu_item( label="RedNode Comunicação", callback = change_menu, user_data = "Rednode comunicacao" )
        add_menu_item( label="Configurações"      , callback = change_menu, user_data = "Configuracoes"       )
        add_menu_item( label='Sair'               , callback = closing_dpg                                    )

with theme( default_theme = True ) as theme_id:
    add_theme_color( mvThemeCol_Button       , (52, 140, 215), category = mvThemeCat_Core )
    add_theme_style( mvStyleVar_FrameRounding,        5      , category = mvThemeCat_Core )
    # um azul bem bonito -> 52, 140, 215 
    # um laranja bem bonito -> 255, 140, 23 


configure_viewport()
add_resize_handler(main_window, callback=resize_mainwindow ) 
change_menu(None, None, 'Inicio' )

#show_debug()
#show_imgui_demo()
#show_implot_demo() 

while is_dearpygui_running():
    if not get_frame_count() % 25: 
        if   window_opened == 'Inicio'            : render_inicio () 
        elif window_opened == 'Visualizacao geral': render_visualizacaoGeral() 
        elif window_opened == 'Posicao do sol'    : render_posicaoDoSol()
        elif window_opened == 'Atuadores'         : render_atuador()     
        elif window_opened == 'Sensores'          : render_sensores()  
        elif window_opened == 'RednodeComunicacao': render_rednodecom()  
        elif window_opened == 'Configuracoes'     : render_configuracao()  

    render_dearpygui_frame() 
print('Volte Sempre')