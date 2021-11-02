from dearpygui.dearpygui import *
import os 

PATH      = os.path.dirname( __file__ )
PATH_IMG  = PATH + '\\utils\\img\\'

def add_image_loaded( img_path ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )

def hover_buttons_IN ( sender, data, user ):
    if   user == "Visualização geral"  :
        configure_item( 1_3_1, default_value = user )
    elif user == "Posição do sol"      :
        configure_item( 1_3_1, default_value = user )
    elif user == "Atuadores"           :
        configure_item( 1_3_1, default_value = user )
    elif user == "Atuação da base"     :
        configure_item( 1_3_1, default_value = user )
    elif user == "Atuação da elevação" :
        configure_item( 1_3_1, default_value = user )
    elif user == "Configurações"       :
        configure_item( 1_3_1, default_value = user )

def resize_inicio():
    w , h = get_item_width( 1_0 ), get_item_height( 1_0 )
    
    configure_item( 1_1 , width = w-15     , height = h*3/10    , pos = [ 10       , 25             ] )
    configure_item( 1_2 , width = w/3      , height = h*6.60/10 , pos = [ 10       , (h//10)*3 + 30 ] )
    configure_item( 1_3 , width = w*2/3-20 , height = h*6.60/10 , pos = [ w//3 + 15, (h//10)*3 + 30 ] )

    w_header , h_header  = get_item_width( 1_1 ), get_item_height( 1_1 )
    w_lateral, h_lateral = get_item_width( 1_2 ), get_item_height( 1_2 )

    configure_item( 1_1_1_0 , width = w_header-16 , height = h_header-16 ) # HEADER 
    
    configure_item( 1_1_1_1 , pmin  = (-30,-30), pmax = ( w, round( h*3/10)*2 ))
    configure_item( 1_1_1_2 , pmin  = (10,10)  , pmax = (350,200) )

    v_spacing = h_lateral // 9  # LATERAL 
    configure_item( 1_2_1, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_2, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_3, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_4, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_5, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_6, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_7, width = w//3 - 15, height = v_spacing ) 
    configure_item( 1_2_8, width = w//3 - 15, height = v_spacing )  

def render_inicio    ( ):
    pass 

def init_inicio      ( windows :dict, callback ): 
    with theme( id = 'no_win_border'):
        add_theme_style( mvStyleVar_WindowBorderSize, 0 , category = mvThemeCat_Core )

    with window( label = 'Header' , id = 1_1, pos = [10, 25], no_move  = True , no_close    = True, no_title_bar= True, no_resize= True ) as Header_IN:    
        windows['Inicio'].append( Header_IN )
        
        img_fundo = add_image_loaded( PATH_IMG + 'fundo.jpg' )
        img_logo  = add_image_loaded( PATH_IMG + 'JetTowers-Logo.png' )
        add_drawlist( id = 1_1_1_0 )
        draw_image  ( parent = 1_1_1_0, id = 1_1_1_1, label = 'imgFundo', texture_id = img_fundo, pmin = (0,0), pmax = (1,1) ) 
        draw_image  ( parent = 1_1_1_0, id = 1_1_1_2, label = 'imgLogo' , texture_id = img_logo , pmin = (0,0), pmax = (1,1) )
    

    with window( label = 'Lateral', id = 1_2, no_move= True , no_close = True , no_title_bar= True, no_resize= True ) as Lateral_IN:
        windows['Inicio'].append( Lateral_IN )
        
        add_spacing( count = 4 )
        add_button(  label = "Visualização geral" , id = 1_2_1, arrow  = False, callback = callback, user_data   = 'Visualização geral'  )
        add_button(  label = "Posição do sol"     , id = 1_2_2, arrow  = False, callback = callback, user_data   = 'Posição do sol'      )
        add_button(  label = "Atuadores"          , id = 1_2_3, arrow  = False, callback = callback, user_data   = "Atuadores"           )
        add_button(  label = "Atuação da base"    , id = 1_2_4, arrow  = False, callback = callback, user_data   = "Atuação da base"     )
        add_button(  label = "Atuação da elevação", id = 1_2_5, arrow  = False, callback = callback, user_data   = "Atuação da elevação" )
        add_button(  label = "Sensores"           , id = 1_2_6, arrow  = False, callback = callback, user_data   = 'Sensores'            )
        add_button(  label = "RedNode Comunicaçaõ", id = 1_2_7, arrow  = False, callback = callback, user_data   = 'RedNode Comunicação' )
        add_button(  label = "Configurações"      , id = 1_2_8, arrow  = False, callback = callback, user_data   = 'Configurações'       )
    

    with window( label = 'Main'   , id = 1_3, no_move= True , no_close = True , no_title_bar= True, no_resize= True) as Main_IN:
        windows['Inicio'].append( Main_IN )
        
        add_text( 'HOVER SOME ITEM AT THE LEFT SIDE...', id = 1_3_1)
        add_hover_handler( parent = 1_2_1, callback = hover_buttons_IN, user_data = "Visualização geral"  )
        add_hover_handler( parent = 1_2_2, callback = hover_buttons_IN, user_data = "Posição do sol"      )
        add_hover_handler( parent = 1_2_3, callback = hover_buttons_IN, user_data = "Atuadores"           )
        add_hover_handler( parent = 1_2_4, callback = hover_buttons_IN, user_data = "Atuação da base"     )
        add_hover_handler( parent = 1_2_5, callback = hover_buttons_IN, user_data = "Atuação da elevação" )
        add_hover_handler( parent = 1_2_6, callback = hover_buttons_IN, user_data = "Sensores"            )
        add_hover_handler( parent = 1_2_7, callback = hover_buttons_IN, user_data = "RedNode Comunicação" )
        add_hover_handler( parent = 1_2_8, callback = hover_buttons_IN, user_data = "Configurações"       )

    set_item_theme(1_1, 'no_win_border')
    set_item_theme(1_2, 'no_win_border')
    set_item_theme(1_3, 'no_win_border')

