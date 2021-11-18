import dearpygui.dearpygui as dpg 

from views.menuInicio            import *
from views.menuVisualizacaoGeral import *
from views.menuPosicaoDoSol      import *
from views.menuAtuadores         import * 
from views.menuSensores          import * 
from views.menuRedNodeComm       import * 
from views.menuConfigurações     import * 

from themes                      import * 
from registry                    import * 
from time                        import sleep, time 


class Tracker: 
    window_opened : str         = ''
    sun_data      : SunPosition = 0 
    time_acum     : float       = 0 

    def __init__( self ):
        with window( label = 'Main Window', id = 1_0, autosize = True ) as main_window:
            self.main_window = main_window 
            with menu_bar(label = "MenuBar"):
                add_menu_item( label="Inicio"             , callback = self.change_menu, user_data = "Inicio"              )
                add_menu_item( label="Visualização geral" , callback = self.change_menu, user_data = "Visualizacao geral"  )
                add_menu_item( label="Posição do sol"     , callback = self.change_menu, user_data = "Posicao do sol"      )
                add_menu_item( label="Atuadores"          , callback = self.change_menu, user_data = "Atuadores"           )
                add_menu_item( label="Sensores"           , callback = self.change_menu, user_data = "Sensores"            )
                add_menu_item( label="RedNode Comunicacao", callback = self.change_menu, user_data = "Rednode comunicacao" )
                add_menu_item( label="Configurações"      , callback = self.change_menu, user_data = "Configuracoes"       )
                add_menu_item( label='Sair'               , callback = self.closing_dpg                                    )

        self.sun_data = sun_data 
        self.sun_data.update_date()
        dpg.set_primary_window ( main_window, True    )
        self.INICIO = ViewInicio( main_window = self.main_window, callback_change_menu = self.change_menu )
       
        with dpg.handler_registry():
            dpg.add_resize_handler( self.main_window, callback = self.resize ) 

    def build(self):
        self.INICIO.build ( )
        init_visualizacaoGeral( windows              ) 
        init_posicaoDoSol     ( windows              )
        init_atuador          ( windows              ) 
        init_sensores         ( windows              ) 
        init_rednodecom       ( windows              ) 
        init_configuracoes    ( windows              )
        self.change_menu  ( None, None, 'Inicio' )

    def resize ( self ):
        new_w = get_item_width ( self.main_window )
        new_h = get_item_height( self.main_window ) 
        if   self.window_opened == 'Inicio'             : self.INICIO.resize( new_w, new_h ) 
        elif self.window_opened == 'Visualizacao geral' : resize_visualizacaoGeral(  ) 
        elif self.window_opened == 'Posicao do sol'     : resize_posicaoDoSol     (  )
        elif self.window_opened == 'Atuadores'          : resize_atuador          (  )     
        elif self.window_opened == 'Sensores'           : resize_sensores         (  )  
        elif self.window_opened == 'Rednode comunicacao': resize_rednodecom       ( new_w, new_h )  
        elif self.window_opened == 'Configuracoes'      : resize_configuracoes    (  )  

    def render( self ):   
        self.time_acum = 0 
        while dpg.is_dearpygui_running():
            if not dpg.get_frame_count() % 25: 
                if   self.window_opened == 'Inicio'             : self.INICIO.render()            # ID = 1_0     
                elif self.window_opened == 'Visualizacao geral' : render_visualizacaoGeral() # ID = 2_0                 
                elif self.window_opened == 'Posicao do sol'     : render_posicaoDoSol()      # ID = 3_0         
                elif self.window_opened == 'Atuadores'          : render_atuador()           # ID = 4_0         
                elif self.window_opened == 'Sensores'           : render_sensores()          # ID = 5_0         
                elif self.window_opened == 'Rednode comunicacao': render_rednodecom()        # ID = 6_0         
                elif self.window_opened == 'Configuracoes'      : render_configuracao()      # ID = 9_0         
            self.time_acum += dpg.get_delta_time()
            if self.time_acum > 1 and dpg.get_value(hora_manual) == False:
                self.sun_data.update_date()
                dpg.set_value ( day          , self.sun_data.day               )
                dpg.set_value ( month        , self.sun_data.month             )
                dpg.set_value ( year         , self.sun_data.year              )
                dpg.set_value ( second       , self.sun_data.second            )
                dpg.set_value ( minute       , self.sun_data.minute            )
                dpg.set_value ( hour         , self.sun_data.hour              )
                dpg.set_value ( total_seconds, self.sun_data.total_seconds     )
                dpg.set_value ( dia_juliano  , self.sun_data.dia_juliano       )

                dpg.set_value ( azi          , self.sun_data.azi               )
                dpg.set_value ( alt          , self.sun_data.alt               )  

                dpg.set_value ( sunrise_azi  , self.sun_data.azimute_sunrise   )  
                dpg.set_value ( sunset_azi   , self.sun_data.azimute_sunset    )  
                dpg.set_value ( culminant_alt, self.sun_data.elevation_transit )  
                
                # Se estiver conectado, pega os valores de azi do motor e alt 
                if dpg.get_value( CONNECTED) == True: 
                    dpg.set_value ( MG_Angle , self.sun_data.azi               )                 
                    dpg.set_value ( ME_Angle , self.sun_data.alt               )
                
                time_acum = 0 

                refresh_TCP_connection( None, None, None )
            dpg.render_dearpygui_frame() 

    def change_menu(self, sender, app_data, user_data ):
        self.window_opened = user_data 
        # CLOSE ALL WINDOWS 
        for k in windows.keys():
            for i in windows[k]:
                dpg.hide_item(i)
        # OPEN THE RIGHT TAB WINDOW 
        to_open = windows[user_data]
        for i in to_open:
            dpg.show_item(i)
        self.resize() 

    def closing_dpg( self, sender, data, user ): 
        with dpg.window( pos = [ dpg.get_item_width(10)/2.5, dpg.get_item_height(10)/2.5]): 
            dpg.add_text( 'Obrigado por usar nosso programa\nEle irá encerrar em instantes' )
        sleep(2)
        dpg.stop_dearpygui() 


dpg.setup_viewport ( )
dpg.set_viewport_large_icon( PATH + 'ico\\large_ico.ico'              )
dpg.set_viewport_small_icon( PATH + 'ico\\small_ico.ico'              ) 
dpg.set_viewport_min_height( height = 900                             ) 
dpg.set_viewport_min_width ( width  = 1000                            ) 
dpg.set_viewport_title     ( title  = 'JetTracker - Controle do sol'  )
dpg.maximize_viewport() 

tracker = Tracker() 
tracker.build() 
tracker.render() 

print('Volte Sempre')