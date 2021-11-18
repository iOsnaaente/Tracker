import dearpygui.dearpygui as dpg 
from registry              import * 
import os 

class ViewInicio: 
    windows             = { 'Inicio' : [] }
    Header              = 0   
    Lateral             = 0  
    Body                = 0   
    draw_list           = 0 
    img_bg              = 0 
    img_bg              = 0 
    img_logo            = 0 
    img_logo            = 0 
    visualização_geral  = 0 
    posicao_do_sol      = 0 
    atuadores           = 0 
    sensores            = 0 
    redNode_comunicacao = 0 
    configuracoes       = 0 
    text_body           = 0 

    def __init__( self, callback_change_menu, main_window ) -> None:
        self.PATH     = os.path.dirname( __file__ ).removesuffix( 'views' ) 
        self.PATH_IMG = self.PATH + 'img\\' 

        self.main_window = main_window 
        self.main_width  = dpg.get_item_width( main_window )  
        self.main_height = dpg.get_item_height( main_window )

        self.callback_change_menu = callback_change_menu 

        with dpg.window( label = 'Header', id = dpg.generate_uuid(), pos = [10, 25], no_move  = True , no_close    = True, no_title_bar= True, no_resize= True ) as Header:    
            self.windows['Inicio'].append( Header )
            self.Header = Header
        with dpg.window( label = 'Lateral', id = dpg.generate_uuid(), no_move= True , no_close = True , no_title_bar= True, no_resize= True ) as Lateral:
            windows['Inicio'].append( Lateral )
            self.Lateral = Lateral 
        with dpg.window( label = 'Main', id = dpg.generate_uuid(), no_move= True , no_close = True , no_title_bar= True, no_resize= True) as Body:
            windows['Inicio'].append( Body )
            self.Body = Body 

        self.num_buttons = 6 + 1 

    def exclude_itens(self) -> bool:
        for values in self.windows.values():
            childrens = dpg.get_item_children( values )
            dpg.delete_item(childrens)

    def build( self ) -> list: 
        dpg.configure_item( self.Header  , width = self.main_width-15     , height = self.main_height*3/10    , pos = [ 10                     , 25                            ] )
        dpg.configure_item( self.Lateral , width = self.main_width/3      , height = self.main_height*6.60/10 , pos = [ 10                     , (self.main_height//10)*3 + 20 ] )
        dpg.configure_item( self.Body    , width = self.main_width*2/3-20 , height = self.main_height*6.60/10 , pos = [ self.main_width//3 + 15, (self.main_height//10)*3 + 35 ] )
        
        self.draw_list = dpg.add_drawlist ( parent = self.Header, id = dpg.generate_uuid() )
        self.img_bg    = add_image_loaded ( self.PATH_IMG + 'fundo.jpg' )
        self.img_bg    = dpg.draw_image   ( parent = self.draw_list, id = dpg.generate_uuid(), label = 'imgFundo', texture_id = self.img_bg   , pmin = (0,0), pmax = (1,1) ) 
        self.img_logo  = add_image_loaded ( self.PATH_IMG + 'JetTowers-Logo.png' )
        self.img_logo  = dpg.draw_image   ( parent = self.draw_list, id = dpg.generate_uuid(), label = 'imgLogo' , texture_id = self.img_logo , pmin = (0,0), pmax = (1,1) )
    
        dpg.add_spacing( parent=self.Lateral, count = 4 )
        self.visualização_geral  = dpg.add_button( parent = self.Lateral,  label = "Visualização geral" , id = dpg.generate_uuid(), arrow  = False, callback = self.callback_change_menu, user_data   = "Visualizacao geral"  )
        self.posicao_do_sol      = dpg.add_button( parent = self.Lateral,  label = "Posição do sol"     , id = dpg.generate_uuid(), arrow  = False, callback = self.callback_change_menu, user_data   = "Posicao do sol"      )
        self.atuadores           = dpg.add_button( parent = self.Lateral,  label = "Atuadores"          , id = dpg.generate_uuid(), arrow  = False, callback = self.callback_change_menu, user_data   = "Atuadores"           )
        self.sensores            = dpg.add_button( parent = self.Lateral,  label = "Sensores"           , id = dpg.generate_uuid(), arrow  = False, callback = self.callback_change_menu, user_data   = "Sensores"            )
        self.redNode_comunicacao = dpg.add_button( parent = self.Lateral,  label = "RedNode Comunicaçaõ", id = dpg.generate_uuid(), arrow  = False, callback = self.callback_change_menu, user_data   = "Rednode comunicacao" )
        self.configuracoes       = dpg.add_button( parent = self.Lateral,  label = "Configurações"      , id = dpg.generate_uuid(), arrow  = False, callback = self.callback_change_menu, user_data   = "Configuracoes"       )
        
        dpg.add_text( 'HOVER SOME ITEM AT THE LEFT SIDE...'     , parent = self.Body, id = dpg.generate_uuid() )
        dpg.add_hover_handler( parent = self.visualização_geral , callback = self.hover_buttons, user_data = "Visualização geral"  )
        dpg.add_hover_handler( parent = self.posicao_do_sol     , callback = self.hover_buttons, user_data = "Posição do sol"      )
        dpg.add_hover_handler( parent = self.atuadores          , callback = self.hover_buttons, user_data = "Atuadores"           )
        dpg.add_hover_handler( parent = self.sensores           , callback = self.hover_buttons, user_data = "Sensores"            )
        dpg.add_hover_handler( parent = self.redNode_comunicacao, callback = self.hover_buttons, user_data = "RedNode Comunicação" )
        dpg.add_hover_handler( parent = self.configuracoes      , callback = self.hover_buttons, user_data = "Configurações"       )

        dpg.set_item_theme( self.Header , 'no_win_border')
        dpg.set_item_theme( self.Lateral, 'no_win_border')
        dpg.set_item_theme( self.Body   , 'no_win_border') 
    
    def hover_buttons( self, sender, data, user ) -> bool :
        if   user == "Visualização geral"  :
            dpg.configure_item( self.text_body, default_value = user )
        elif user == "Posição do sol"      :
            dpg.configure_item( self.text_body, default_value = user )
        elif user == "Atuadores"           :
            dpg.configure_item( self.text_body, default_value = user )
        elif user == "Atuação da base"     :
            dpg.configure_item( self.text_body, default_value = user )
        elif user == "Atuação da elevação" :
            dpg.configure_item( self.text_body, default_value = user )
        elif user == "Configurações"       :
            dpg.configure_item( self.text_body, default_value = user )
 
    def resize( self , main_width : int, main_height : int ) -> bool:
        self.main_width = main_width 
        self.main_height = main_height
        dpg.configure_item( self.Header  , width = self.main_width-15     , height = self.main_height*3/10    , pos = [ 10                     , 25                            ] )
        dpg.configure_item( self.Lateral , width = self.main_width/3      , height = self.main_height*6.60/10 , pos = [ 10                     , (self.main_height//10)*3 + 20 ] )
        dpg.configure_item( self.Body    , width = self.main_width*2/3-20 , height = self.main_height*6.60/10 , pos = [ self.main_width//3 + 15, (self.main_height//10)*3 + 35 ] )
        w_header , h_header  = dpg.get_item_width( self.Header  ), dpg.get_item_height( self.Header   )
        w_lateral, h_lateral = dpg.get_item_width( self.Lateral ), dpg.get_item_height( self.Lateral  )

        dpg.configure_item( self.draw_list , width = w_header-16 , height = h_header-16 )   
        dpg.configure_item( self.img_bg    , pmin  = (-30,-30), pmax = ( self.main_width, round( self.main_height*3/10)*2 ))
        dpg.configure_item( self.img_logo  , pmin  = (10,10)  , pmax = (350,200) )

        v_spacing = h_lateral // self.num_buttons
        dpg.configure_item( self.visualização_geral , width = self.main_width//3 - 15, height = v_spacing ) 
        dpg.configure_item( self.posicao_do_sol     , width = self.main_width//3 - 15, height = v_spacing ) 
        dpg.configure_item( self.atuadores          , width = self.main_width//3 - 15, height = v_spacing )
        dpg.configure_item( self.sensores           , width = self.main_width//3 - 15, height = v_spacing ) 
        dpg.configure_item( self.redNode_comunicacao, width = self.main_width//3 - 15, height = v_spacing ) 
        dpg.configure_item( self.configuracoes      , width = self.main_width//3 - 15, height = v_spacing )  
    
    def render(self) -> bool:
        return True 
