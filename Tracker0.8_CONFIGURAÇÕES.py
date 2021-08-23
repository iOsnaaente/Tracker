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

PATH = os.path.dirname( __file__ )


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


# FUNÇÕES
def add_image_loaded( img_path ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )

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

def init_configuracoes(): 

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


def render_configuracao():
    w, h = get_item_width( 1_0 ), get_item_height( 1_0 ) 
    configure_item( 7_1_0, pos = [ 10            , 25 ], width = (w*(1/3))//1, height = (h*0.965)//1 ) 
    configure_item( 7_2_0, pos = [ w*(1/3)   + 10, 25 ], width = (w*(7/15)-5 )//1, height = (h*0.965)//1 ) 
    configure_item( 7_3_0, pos = [ w*(12/15) + 5 , 25 ], width = (w*(3/15)-10)//1, height = (h*0.965)//1 ) 


setup_viewport()
screen_dimension = [ GetSystemMetrics(0), GetSystemMetrics(1) ] 

show_style_editor()
show_documentation() 

set_viewport_title( title = 'Configurações' )
set_viewport_pos( [55,0] )
set_viewport_width(  screen_dimension[0] )
set_viewport_height( screen_dimension[1] )

set_primary_window( main_window, True )
change_menu(None, None, 'Configurações' )

count = 0
while is_dearpygui_running():
    render_dearpygui_frame()

    if window_opened == 'Configurações':
        render_configuracao() 
