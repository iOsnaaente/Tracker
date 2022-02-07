# INICIO DO CONTEXTO DPG 
import dearpygui.dearpygui as dpg

# INICIO DO CONTEXTO 
dpg.create_context()
dpg.create_viewport( title = 'Jet Towers Tracker', min_width = 800, min_height = 600 )
dpg.setup_dearpygui()


# CONFIGURAÇÃO DA FONTE - INICIO DO COD. 
with dpg.font_registry():
    defont = dpg.add_font("utils\\fonts\\verdana.ttf", 14 )
dpg.bind_font( defont )


# HANDLER REGISTRIES - INICIO DO COD.
with dpg.handler_registry( tag = 'handler' ):
    #dpg.add_mouse_click_handler( button = dpg.mvMouseButton_Left, callback = lambda : print(dpg.get_mouse_pos()), user_data = 'draw_list' )
    pass 


from   serial.serialutil import PARITY_ODD  
from   serial            import SerialException, Serial 
from   typing            import Union
from   time              import *
import datetime          as     dt 
import datetime 
import struct
import random 
import serial
import socket
import ephem 
import math 
import time 
import glob
import sys 
import os 



# CLASSE DE POSIÇÃO DO SOL USANDO EPHEM  
class SunPosition:
    # SEGUNDOS DO DIA E DIAS JULIANOS TOTAIS 
    total_seconds = 0
    dia_juliano   = 0 

    # DEFINIÇÃO DE DATA E HORA 
    year   = 0
    month  = 0
    day    = 0
    hour   = 0
    minute = 0
    second = 0

    # DEFINIÃO DOS PARAMETROS DE LAT/LONG
    latitude = 0        #-29.165307659422155
    longitude = 0       #-54.89831672609559

    # ALTURA - AZIMUTE - SOL 
    alt = 0 
    azi = 0 

    # ALTURA - AZIMUTE - LUA
    m_alt = 0
    m_azi = 0 

    # NASCER DO SOL - TRANSIÇÃO - POR DO SOL 
    rising  = 0  
    transit = 0  
    sunset  = 0 

    elevation_transit = 0.0 
    azimute_sunrise   = 0.0 
    azimute_sunset    = 0.0 

    winter_solstice = 0 
    summer_solstice = 0 
    equinox         = 0 


    def __init__(self, latitude, longitude, altitude, utc_local = -3 ):
        # DEFINIÇÃO DOS PARAMETROS 
        if type( latitude  ) == float: latitude  = str( latitude  )
        if type( longitude ) == float: longitude = str( longitude )
        
        self.latitude  = latitude 
        self.longitude = longitude
        self.altitude  = altitude

        # CRIAÇÃO DO OBSERVADOR 
        self.me = ephem.Observer()

        # CRIAÇÃO DO ASTRO OBSERVADO
        self.sun = ephem.Sun()
        self.moon = ephem.Moon()

        # DEFINIÇÃO DO OBSERVADOR 
        self.me.lat       = self.latitude 
        self.me.lon       = self.longitude
        self.me.elevation = self.altitude

        # HORÁRIO LOCAL 
        self.utc_local = utc_local 

        # ATUALIZAÇÃO DA DATA E COMPUTAÇÃO DOS VALORES 
        self.date = 0
        self.update_date()

    # Para setar novos parametros 
    def set_parameters(self, latitude, longitude, altitude ):
        if type( latitude  ) == float: latitude  = str( latitude  )
        if type( longitude ) == float: longitude = str( longitude )

        # DEFINIÇÃO DOS NOVOS PARAMETROS 
        self.latitude  = latitude 
        self.longitude = longitude
        self.altitude  = altitude

        # ATUALIZAÇÃO DO OBSERVADOR 
        self.me.lat       = self.latitude 
        self.me.lon       = self.longitude
        self.me.elevation = self.altitude

        # ATUALIZAÇÃO DOS CALCULOS
        self.update()
    
    def set_latitude(self, latitude):
        if type( latitude  ) == float: latitude  = str( latitude  )
        self.latitude         = latitude 
        self.me.lat           = self.latitude 
        self.update()

    def set_longitude(self, longitude ): 
        if type( longitude ) == float: longitude = str( longitude )
        self.longitude        = longitude
        self.me.lon           = self.longitude
        self.update() 

    def set_altitude(self, altitude):
        self.altitude     = altitude
        self.me.elevation = self.altitude
        self.update() 

    def update_coordenates(self):
        self.me.lat       = self.latitude
        self.me.lon       = self.longitude
        self.me.elevation = self.altitude
        self.update()
    
    # Calculo das horas de sol do dia 
    def get_sunlight_hours(self):
        return (self.sunset - self.rising)

    # Setar a data manualmente
    def set_date(self, data):
        # OBRIGADO USAR DATA NO ESTILO DATETIME.DATETIME
        if type(data) is datetime.datetime:
            self.date = data
            self.update_date(True)

    # Atualiza a data 
    def update_date(self, manual = False):
        if not manual:
            # Pega a hora local
            self.date   = datetime.datetime.utcnow()
        self.year   = self.date.year   
        self.month  = self.date.month  
        self.day    = self.date.day    
        self.hour   = self.date.hour + self.utc_local 
        self.minute = self.date.minute 
        self.second = self.date.second 
        self.total_seconds = self.second + self.minute*60 + self.hour*3600
        self.dia_juliano   = self.DJ()

        # ATUALIZAÇÃO DOS DADOS PASSADOS 
        self.update()

    # calculo do Dia Juliano segundo - ghiorzi.org/diasjuli.html
    def DJ( self ):
        y = self.year
        m = self.month
        d = self.day 
        if m < 3:
            y = y -1 
            m = m +12 
        A = y // 100 
        B = A // 4 
        C = 2 -A +B

        # Funciona para datas posteriores de 04/10/1582
        D = int( 365.25 * ( y +4716 ) )
        E = int( 30.6001 * ( m +1 ) )
        DJ = D + E + d + 0.5 + C - 1524.5 
        return DJ 

    def update(self):
        # ATUALIZAÇÃO DO OBSERVADOR 
        self.me.lat = self.latitude 
        self.me.lon = self.longitude 
        self.me.date = self.date 
        
        # COMPUTAÇÃO DOS DADOS
        self.sun.compute( self.me )
        self.moon.compute( self.me )

        # Calculando a altitude e azimute - do sol 
        self.alt = float( self.sun.alt )  
        self.azi = float( self.sun.az  ) 

        # Calculando a altitude e azimute - da Lua 
        self.m_alt = float( self.sun.alt )  
        self.m_azi = float( self.sun.az  )  
        
        # Calculando o nascer e por do sol
        try:
            self.rising  = self.me.previous_rising( self.sun ).datetime()
            self.transit = self.me.next_transit( self.sun ).datetime()   
            self.sunset  = self.me.next_setting( self.sun ).datetime()    
        except:
            print( 'Fora dos limites aceitáveis de calculo para sunrising/sunrise devido ao circulo polar ') 

        self.me.date = self.rising 
        self.sun.compute( self.me )
        self.azimute_sunrise = float( self.sun.az )
        
        self.me.date = self.transit 
        self.sun.compute( self.me )
        self.elevation_transit = float( self.sun.alt )
        
        self.me.date = self.sunset 
        self.sun.compute( self.me )
        self.azimute_sunset = float( self.sun.az )

        self.winter_solstice = ephem.next_solstice( str(self.date.year)  )
        self.summer_solstice = ephem.next_solstice( self.winter_solstice )

    def get_pos_from_date(self, date):
        self.me.date = date 
        self.sun.compute( self.me )

        # Calculo do azimute e altitude 
        alt = self.sun.alt.norm   # Altitude above horizon  # -13:04:48.9
        azi = self.sun.az.norm    # Azimuth east of north   #  226:41:12.8
        
        # Retorna a data ao self.me.date 
        self.me.date = self.date 
        self.update() 
        
        return [ alt, azi ]

    def trajetory(self, resolution = 24, all_day = False ):
        # Hora do dia atual 
        self.update()
        
        if all_day: 
            # Total de segundos em um dia 
            delta_day_time = 24*3600 - 1
            diff = datetime.timedelta ( seconds = delta_day_time // resolution )
            today = datetime.datetime( self.date.year, self.date.month, self.date.day, 0, 0, 0)
        else:
            # Total de segundos do nascer do sol ao por do sol 
            delta_day_time = self.sunset - self.rising 
            diff = datetime.timedelta ( seconds = delta_day_time.seconds // resolution ) 
            today = datetime.datetime( self.date.year, self.date.month, self.date.day, self.rising.hour , self.rising.minute, self.rising.second)
 
        # Lista de pontos
        dots = []        
        for i in range( resolution ):
            # Atualização da data para configuração dos pontos 
            self.me.date = today + diff * i 
            self.sun.compute( self.me )

            # Calculo do azimute e altitude 
            alt = self.sun.alt.norm   # Altitude above horizon  # -13:04:48.9
            azi = self.sun.az.norm    # Azimuth east of north   #  226:41:12.8
            time = today + diff * i 
            dots.append( [ azi, alt, time ] )
        
        # Retorna a data ao self.me.date 
        self.me.date = self.date 
        self.update() 

        return dots

# GRAPHS 
MPE_LIST  = []
MDE_LIST  = [] 
SPE_LIST  = []
MPE_COUNT = 0
GPHE_ATT  = False 

MPG_LIST  = []
MDG_LIST  = [] 
SPG_LIST  = []
MPG_COUNT = 0
GPHG_ATT  = False

DOMINIO  = [] 

MS_GIRO  = [] 
PS_GIRO  = [] 
TM_GIRO  = [] 
CNT_GIRO = 0

MS_ELE   = [] 
PS_ELE   = [] 
TM_ELE   = []
CNT_ELE  = 0

MSG_INIT    = [ ord(i) for i in 'init' ]
MSG_COUNT   = 0 

DIAGNOSIS_LIST = [] 

DOM         = [ 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro' ]

PATH        = os.path.dirname( __file__ )
PATH_IMG    = PATH + '\\utils\\img\\'

COLOR = {
    "black"     : lambda alfa : [    0,    0,    0, alfa ],
    "red"       : lambda alfa : [  255,    0,    0, alfa ],
    "yellow"    : lambda alfa : [  255,  255,    0, alfa ],
    "green"     : lambda alfa : [    0,  255,    0, alfa ],
    "ciano"     : lambda alfa : [    0,  255,  255, alfa ],
    "blue"      : lambda alfa : [    0,    0,  255, alfa ],
    "magenta"   : lambda alfa : [  255,    0,  255, alfa ],
    "white"     : lambda alfa : [  255,  255,  255, alfa ],
    'gray'      : lambda alfa : [  155,  155,  155, alfa ],
    'orange'    : lambda alfa : [  255,   69,    0, alfa ],

    'on_color'  : lambda alfa : [ 0x3c, 0xb3, 0x71, alfa ],
    'on_hover'  : lambda alfa : [ 0x92, 0xe0, 0x92, alfa ],
    'on_click'  : lambda alfa : [ 0x20, 0xb2, 0xaa, alfa ],
    'off_color' : lambda alfa : [ 0xff, 0x45, 0x00, alfa ],
    'off_hover' : lambda alfa : [ 0xf0, 0x80, 0x80, alfa ],
    'off_click' : lambda alfa : [ 0x8b, 0x45, 0x13, alfa ],


    }

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


with dpg.value_registry( ) as registries:
    # POSIÇÃO GEOGRÁFICA CONSTANTE - PEGAR DE UM DOCUMENTO
    LATITUDE     = dpg.add_float_value ( parent = registries, default_value = -29.16530765942215      , tag = 99_99_1 ) 
    LONGITUDE    = dpg.add_float_value ( parent = registries, default_value = -54.89831672609559      , tag = 99_99_2 )
    ALTITUDE     = dpg.add_float_value ( parent = registries, default_value = 425                     , tag = 99_99_3 )
    UTC_HOUR     = dpg.add_int_value   ( parent = registries, default_value = -3                      , tag = 99_99_4 )
    
    # DADOS DOS MOTORES 
    #   GIRO 
    MPG              = dpg.add_float_value ( parent = registries, default_value = 425                 , tag = 99_99_5 )
    MG_VELANG        = dpg.add_float_value ( parent = registries, default_value = 1.0                 , tag = 99_99_6 )  
    MG_RESOLUCAO     = dpg.add_float_value ( parent = registries, default_value = 0.0                 , tag = 99_99_7 )
    MG_STEPS         = dpg.add_float_value ( parent = registries, default_value = 0.0                 , tag = 99_99_8 )
    MG_USTEP         = dpg.add_string_value( parent = registries, default_value = '1/16'              , tag = 99_99_9 )
    MG_ONOFF         = dpg.add_bool_value  ( parent = registries, default_value = False               , tag = 99_99_10 ) 
    #   ELEVAÇÃO
    MPE              = dpg.add_float_value ( parent = registries, default_value = 100                 , tag = 99_99_11 )
    ME_VELANG        = dpg.add_float_value ( parent = registries, default_value = 1.0                 , tag = 99_99_12 )  
    ME_RESOLUCAO     = dpg.add_float_value ( parent = registries, default_value = 0.0                 , tag = 99_99_13 )
    ME_STEPS         = dpg.add_float_value ( parent = registries, default_value = 0.0                 , tag = 99_99_14 )
    ME_USTEP         = dpg.add_string_value( parent = registries, default_value = '1/16'              , tag = 99_99_15 ) 
    ME_ONOFF         = dpg.add_bool_value  ( parent = registries, default_value = False               , tag = 99_99_16 ) 

    # DADOS DOS SENSORES 
    #   GIRO
    SPG              = dpg.add_float_value ( parent = registries, default_value = 180                 , tag = 99_99_17 )
    SDG              = dpg.add_int_value   ( parent = registries, default_value = 1                   , tag = 99_99_18 )
    #   ELEVAÇÃO
    SPE              = dpg.add_float_value ( parent = registries, default_value = 45                  , tag = 99_99_19 )
    SDE              = dpg.add_int_value   ( parent = registries, default_value = 1                   , tag = 99_99_20 )

    # DADOS TEMPORAIS 
    YEAR             = dpg.add_int_value    ( parent = registries, default_value = 1                  , tag = 99_99_21 )  
    MONTH            = dpg.add_int_value    ( parent = registries, default_value = 1                  , tag = 99_99_22 )  
    DAY              = dpg.add_int_value    ( parent = registries, default_value = 1                  , tag = 99_99_23 )  
    HOUR             = dpg.add_int_value    ( parent = registries, default_value = 1                  , tag = 99_99_24 )
    MINUTE           = dpg.add_int_value    ( parent = registries, default_value = 1                  , tag = 99_99_25 )  
    SECOND           = dpg.add_int_value    ( parent = registries, default_value = 1                  , tag = 99_99_26 )  
    TOT_SECONDS      = dpg.add_int_value    ( parent = registries, default_value = 1                  , tag = 99_99_27 )  
    JULIANSDAY       = dpg.add_int_value    ( parent = registries, default_value = 1                  , tag = 99_99_28 )  
    
    # DADOS DE MEDIÇÃO E MONITORAMENTO DO SOL 
    AZIMUTE          = dpg.add_float_value ( parent = registries, default_value = 0.0                 , tag = 99_99_29 )
    ZENITE           = dpg.add_float_value ( parent = registries, default_value = 0.0                 , tag = 99_99_30 )
    H_SUNRISE        = dpg.add_float4_value ( parent = registries, default_value = [0,0,0,0]          , tag = 99_99_31 )  
    H_CULMINANT      = dpg.add_float4_value ( parent = registries, default_value = [0,0,0,0]          , tag = 99_99_32 )  
    H_SUNSET         = dpg.add_float4_value ( parent = registries, default_value = [0,0,0,0]          , tag = 99_99_33 )  
    HT_DAYLIGHT      = dpg.add_float4_value ( parent = registries, default_value = [0,0,0,0]          , tag = 99_99_34 )  
    SR_AZIMUTE       = dpg.add_float_value  ( parent = registries, default_value = 0.0                , tag = 99_99_35 )  
    SS_AZIMUTE       = dpg.add_float_value  ( parent = registries, default_value = 0.0                , tag = 99_99_36 )  
    SC_ALTITUDE      = dpg.add_float_value  ( parent = registries, default_value = 0.0                , tag = 99_99_37 )  
    
    # SERIAL CONFIGURATIONS 
    SERIAL_CONNECTED = dpg.add_bool_value  ( parent = registries, default_value = False               , tag = 99_99_38 ) 
    SERIAL_PORT      = dpg.add_string_value( parent = registries, default_value = 'COM12'             , tag = 99_99_39 )
    SERIAL_BAUDRATE  = dpg.add_string_value( parent = registries, default_value = '115200'            , tag = 99_99_40 )
    SERIAL_TIMEOUT   = dpg.add_int_value   ( parent = registries, default_value = 1                   , tag = 99_99_41 )


    DAY2COMPUTE      = dpg.add_bool_value  ( parent = registries, default_value = False               , tag = 99_99_99_38 )
    TCP_CONNECTED    = dpg.add_bool_value  ( parent = registries, default_value = False               , tag = 99_99_99_39 ) 
    HORA_MANUAL      = dpg.add_bool_value  ( parent = registries, default_value = False               , tag = 99_99_99_41 )  
    
    # ATUADOR 
    WRONG_DATETIME   = dpg.add_bool_value  ( parent = registries, default_value = False               , tag = 99_99_99_42 ) 
    CMD_MODE         = dpg.add_string_value( parent = registries, default_value = 'ASCII'             , tag = 99_99_99_43 )
    STATE            = dpg.add_string_value( parent = registries, default_value = 'AUTO'              , tag = 99_99_99_44 )

SUN_DATA = SunPosition( dpg.get_value(LATITUDE), dpg.get_value(LONGITUDE), dpg.get_value(ALTITUDE) )
SUN_DATA.update() 

dpg.set_value( SPE, math.degrees(SUN_DATA.alt) ) 
dpg.set_value( SPG, math.degrees(SUN_DATA.azi) ) 

date   = dt.datetime.utcnow()
dpg.set_value( YEAR  ,date.year   ) 
dpg.set_value( MONTH ,date.month  )
dpg.set_value( DAY   ,date.day    )
dpg.set_value( HOUR  ,date.hour   )  
dpg.set_value( MINUTE,date.minute ) 
dpg.set_value( SECOND,date.second ) 

# THEMES
with dpg.theme( tag = 99_100_1 ) as global_theme:
    with dpg.theme_component( dpg.mvAll ):
        dpg.add_theme_color( dpg.mvThemeCol_Button      , (52, 140, 215), category = dpg.mvThemeCat_Core )
        dpg.add_theme_style( dpg.mvStyleVar_FrameRounding,        5      , category = dpg.mvThemeCat_Core )

with dpg.theme( tag = 99_100_2 ) as theme_button_on:
    with dpg.theme_component( dpg.mvButton ):
        dpg.add_theme_color( dpg.mvThemeCol_Button       , COLOR['on_color'](255), category =  dpg.mvThemeCat_Core)
        dpg.add_theme_color( dpg.mvThemeCol_ButtonHovered, COLOR['on_hover'](255), category =  dpg.mvThemeCat_Core)

with dpg.theme( tag = 99_100_3 ) as theme_button_off:
    with dpg.theme_component( dpg.mvButton ):
        dpg.add_theme_color( dpg.mvThemeCol_Button       , COLOR['off_color'](255), category = dpg.mvThemeCat_Core)
        dpg.add_theme_color( dpg.mvThemeCol_ButtonHovered, COLOR['off_hover'](255), category = dpg.mvThemeCat_Core)

with dpg.theme( tag = 99_100_4 ) as theme_no_border:
    with dpg.theme_component( dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category = dpg.mvThemeCat_Core)

with dpg.theme( tag = 99_100_5 ) as theme_no_win_border:
    with dpg.theme_component( dpg.mvAll):
        dpg.add_theme_style( dpg.mvStyleVar_WindowBorderSize, 0 , category = dpg.mvThemeCat_Core )

#   APPLY DEFAULT THEMES AND FONTS
dpg.bind_theme( global_theme )

#   FONTS 
with dpg.font_registry() as font_add: 
    default_font = dpg.add_font( PATH + '\\utils\\fonts\\verdana.ttf', 14, parent = font_add )
    dpg.bind_font( default_font )


# MENU INICIO 
def add_image_loaded( img_path ):
    w, h, c, d = dpg.load_image( img_path )
    with dpg.texture_registry() as reg_id : 
        return dpg.add_static_texture( w, h, d, parent = reg_id )

# REGISTRIES ESPECIFIC 
img_fundo = add_image_loaded( PATH_IMG + 'fundo.jpg' )
img_logo  = add_image_loaded( PATH_IMG + 'JetTowers-Logo.png' )
img_inic  = add_image_loaded( PATH_IMG + 'init_img\\' + 'inic.png')
img_posi  = add_image_loaded( PATH_IMG + 'init_img\\' + 'posi.jpg')
img_atua  = add_image_loaded( PATH_IMG + 'init_img\\' + 'atua.png')
img_sens  = add_image_loaded( PATH_IMG + 'init_img\\' + 'sens.png')
img_comu  = add_image_loaded( PATH_IMG + 'init_img\\' + 'comu.jpg') 
img_conf  = add_image_loaded( PATH_IMG + 'init_img\\' + 'conf.png') 

# CALLBACKS 
def hover_buttons ( handler , data, user ):    
    if   data == 1_2_11 : dpg.configure_item( 1_3_1_1, texture_tag = img_inic ) 
    elif data == 1_2_22 : dpg.configure_item( 1_3_1_1, texture_tag = img_posi ) 
    elif data == 1_2_33 : dpg.configure_item( 1_3_1_1, texture_tag = img_atua ) 
    elif data == 1_2_44 : dpg.configure_item( 1_3_1_1, texture_tag = img_sens ) 
    elif data == 1_2_55 : dpg.configure_item( 1_3_1_1, texture_tag = img_comu ) 
    elif data == 1_2_66 : dpg.configure_item( 1_3_1_1, texture_tag = img_conf ) 

def closing_dpg( sender, data, user ): 
    with dpg.window( pos = [ dpg.get_item_width('mainWindow')/2.5, dpg.get_item_height('mainWindow')/2.5]): 
        dpg.add_text( 'Obrigado por usar nosso programa\nEle irá encerrar em instantes' )
    time.sleep(2)
    dpg.stop_dearpygui() 

# HANDLER_REGISTERS / THEMES 
def handlers_and_themes_inicio(): 
    with dpg.item_handler_registry( ) as handler_hover:
        dpg.add_item_hover_handler( callback = hover_buttons )
    dpg.bind_item_handler_registry( item = 1_2_11, handler_registry = handler_hover )
    dpg.bind_item_handler_registry( item = 1_2_22, handler_registry = handler_hover )
    dpg.bind_item_handler_registry( item = 1_2_33, handler_registry = handler_hover )
    dpg.bind_item_handler_registry( item = 1_2_44, handler_registry = handler_hover )
    dpg.bind_item_handler_registry( item = 1_2_55, handler_registry = handler_hover )
    dpg.bind_item_handler_registry( item = 1_2_66, handler_registry = handler_hover )

    dpg.bind_item_theme( 1_1, theme_no_win_border)
    dpg.bind_item_theme( 1_2, theme_no_win_border)
    dpg.bind_item_theme( 1_3, theme_no_win_border)

# MAIN FUNCTIONS 
def resize_inicio( ):
    w, h = dpg.get_item_width( 'mainWindow'), dpg.get_item_height('mainWindow')
    dpg.configure_item( 1_1 , width = w-15     , height = h*3/10    , pos = [ 10       , 25             ] )
    dpg.configure_item( 1_2 , width = w/3      , height = h*6.60/10 , pos = [ 10       , (h//10)*3 + 20 ] )
    dpg.configure_item( 1_3 , width = w*2/3-20 , height = h*6.60/10 , pos = [ w//3 + 15, (h//10)*3 + 35 ] )

    w_header , h_header  = dpg.get_item_width( 1_1 ), dpg.get_item_height( 1_1 )
    dpg.configure_item( 1_1_1_0 , width = w_header-16 , height = h_header-16 ) # HEADER 
    dpg.configure_item( 1_1_1_1 , pmin  = (-30,-30)   , pmax   = ( w, round( h*3/10)*2 ))
    dpg.configure_item( 1_1_1_2 , pmin  = (10,10)     , pmax   = (350,200) )

    v_spacing = dpg.get_item_height( 1_2 ) // 7  # LATERAL 
    dpg.configure_item( 1_2_11, width = w//3 - 15, height = v_spacing ) 
    dpg.configure_item( 1_2_22, width = w//3 - 15, height = v_spacing ) 
    dpg.configure_item( 1_2_33, width = w//3 - 15, height = v_spacing ) 
    dpg.configure_item( 1_2_44, width = w//3 - 15, height = v_spacing ) 
    dpg.configure_item( 1_2_55, width = w//3 - 15, height = v_spacing ) 
    dpg.configure_item( 1_2_66, width = w//3 - 15, height = v_spacing )  

    dpg.configure_item( 1_3_1_0, width = (w*2/3-20)*0.99 , height = (h*6.60/10)*0.875 )
    dpg.configure_item( 1_3_1_1, pmax  = [ (w*2/3-20)*0.99 , (h*6.60/10)*0.8750 ]  )
    dpg.configure_item( 1_3_1_2, pos   = [ (w*2/3-20)*0.99//3 , 50 ])

def render_inicio( ):
    if dpg.get_frame_count() % 5 == 0: 
        resize_inicio()   

def init_inicio( windows :dict, callback ): 
    with dpg.window( label = 'Header' , tag = 1_1, pos = [10, 25], no_move  = True , no_close    = True, no_title_bar= True, no_resize= True ) as Header_IN:    
        windows['Inicio'].append( Header_IN )
        dpg.add_drawlist( tag = 1_1_1_0, width= dpg.get_item_width( 1_1 )-16, height= dpg.get_item_height( 1_1 ) - 16 )
        dpg.draw_image  ( parent = 1_1_1_0, tag = 1_1_1_1, label = 'imgFundo', texture_tag = img_fundo, pmin = (0,0), pmax = (1,1) ) 
        dpg.draw_image  ( parent = 1_1_1_0, tag = 1_1_1_2, label = 'imgLogo' , texture_tag = img_logo , pmin = (0,0), pmax = (1,1) )

    with dpg.window( label = 'Lateral', tag = 1_2, no_move= True , no_close = True , no_title_bar= True, no_resize= True ) as Lateral_IN:
        windows['Inicio'].append( Lateral_IN )
        dpg. add_spacer( )
        dpg.add_button(  label = "Visualização geral" , tag = 1_2_11, arrow  = False, callback = callback, user_data   = "Visualizacao geral"  )
        dpg.add_button(  label = "Atuadores"          , tag = 1_2_33, arrow  = False, callback = callback, user_data   = "Atuadores"           )
        dpg.add_button(  label = "Sensores"           , tag = 1_2_44, arrow  = False, callback = callback, user_data   = "Sensores"            )
        dpg.add_button(  label = "RedNode Comunicaçaõ", tag = 1_2_55, arrow  = False, callback = callback, user_data   = "Rednode comunicacao" )
        dpg.add_button(  label = "Configurações"      , tag = 1_2_66, arrow  = False, callback = callback, user_data   = "Configuracoes"       )
        dpg.add_button(  label = "Sair"               , tag = 1_2_22, arrow  = False, callback = closing_dpg                                   )

    with dpg.window( label = 'Main'   , tag = 1_3, no_move= True , no_close = True , no_title_bar= True, no_resize= True) as Main_IN:
        windows['Inicio'].append( Main_IN )
        dpg.add_drawlist( tag = 1_3_1_0, width = 1000, height = 1000 )
        dpg.draw_image  ( parent = 1_3_1_0, tag = 1_3_1_1, label = 'imgMain', texture_tag = img_inic, pmin = (0,0), pmax = (100,100) ) 
        dpg.draw_text( pos = [500/500], text = '', tag = 1_3_1_2, size = 20 )
    
    resize_inicio() 
    handlers_and_themes_inicio()


# VISUALIZAÇÃO GERAL 
SUN_DATA.update_date() 
# FUNCTIONS 
def get_semi_circle_points( center, radius, angle_i, angle_f, segments = 360, closed = False ):
    points_close = [[ center[0], center[1]-radius ] ,  center, [ center[0] + radius, center[1] ] ] 
    angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
    points =  [ [ center[0] + radius*math.cos(ang), center[1] - radius*math.sin(ang) ] for ang in angles ] 
    if closed: 
        points_close.extend( points )
        return points_close 
    else:      
        return points 

def draw_sun_trajetory( draw_id, parent_id, all_day = False, extremes = False ):
    # Ponto central, dimensões da tela e Raio 
    width, height = dpg.get_item_width( draw_id ), dpg.get_item_height( draw_id )
    center        = [ width//2, height//2 ]
    r             =   width//2 - 20 if width+20 <= height else height//2 - 20
    id_link       = draw_id*100

    # DESENHO DA LINHA DE NASCER DO SOL E POR DO SOL 
    azi = SUN_DATA.get_pos_from_date( SUN_DATA.rising )[1]
    alt = SUN_DATA.get_pos_from_date( SUN_DATA.sunset )[1] # [ alt , azi ]

    # PEGA OS ANGULOS NOS PONTOS DA TRAJETÓRIA DO SOL 
    dots = SUN_DATA.trajetory(100, all_day )
    # PONTOS DE ACORDO COM Azimute - Altitude 
    dots = [ [ x - math.pi/2 ,  y ] for x, y, _ in dots ]
    dots = [ [ center[0] + math.cos(x)*r, center[1] + math.sin(x)*math.cos(y)*r ] for x, y in dots ]

    # DESENHO DO SOL NA SUA POSIÇÃO 
    sun = [  SUN_DATA.azi - math.pi/2, SUN_DATA.alt ] 
    sun = [ center[0] + math.cos(sun[0])*r, center[1] + math.sin(sun[0])*math.cos(sun[1])*r ]
    
    dpg.draw_line(     parent = draw_id, tag = id_link+1 , p1     = [center[0] - r, center[1]]              , p2     = [center[0] + r, center[1]]                                          , color = COLOR['gray'](155)  , thickness = 1 )
    dpg.draw_line(     parent = draw_id, tag = id_link+2 , p1     = center                                  , p2     = [center[0] + r*math.cos(azi-math.pi/2), center[1] + r*math.sin(azi-math.pi/2)], color = COLOR['orange'](155), thickness = 2 )
    dpg.draw_line(     parent = draw_id, tag = id_link+3 , p1     = center                                  , p2     = [center[0] + r*math.cos(alt-math.pi/2), center[1] + r*math.sin(alt-math.pi/2)], color = COLOR['gray'](200)  , thickness = 2 )
    dpg.draw_circle(   parent = draw_id, tag = id_link+4 , center = center                                  , radius = r                                                                   , color = COLOR['white'](200) , fill      = COLOR['white'](10 ), thickness = 3 )
    dpg.draw_circle(   parent = draw_id, tag = id_link+5 , center = center                                  , radius = 3                                                                   , color = COLOR['white'](200) , fill      = COLOR['white'](255), thickness = 2 )
    dpg.draw_text(     parent = draw_id, tag = id_link+6 , pos    = [center[0] -(r +20), center[1] -10 ]    , text   = 'W'                                                                 , color = COLOR['white'](200) , size      = 20 )
    dpg.draw_text(     parent = draw_id, tag = id_link+7 , pos    = [center[0] +(r +5) , center[1] -10 ]    , text   = 'E'                                                                 , color = COLOR['white'](200) , size      = 20 )
    dpg.draw_text(     parent = draw_id, tag = id_link+8 , pos    = [center[0] -10     , center[1] -(r +25)], text   = 'N'                                                                 , color = COLOR['white'](255) , size      = 20 )
    dpg.draw_polyline( parent = draw_id, tag = id_link+9 , points = dots                                    , color  = COLOR['red'](155)                                                    , thickness = 2                   , closed    = False )
    for n, p in enumerate(dots):
        dpg.draw_circle( parent = draw_id, tag = id_link+(12+n) , center = p     , radius = 2  , color = [n*4, 255-n*2, n*2, 255]                              ) 
    dpg.draw_line(       parent = draw_id, tag = id_link+10     , p1     = center, p2     = sun, color = COLOR['yellow'](200)    , thickness = 2               )
    dpg.draw_circle(     parent = draw_id, tag = id_link+11     , center = sun   , radius = 10 , color = COLOR['yellow'](155)    , fill = COLOR['yellow'](255) )

def update_sun_trajetory( draw_id, parent_id, all_day = False ): 
    # Ponto central, dimensões da tela e Raio 
    width, height = dpg.get_item_width( draw_id ), dpg.get_item_height( draw_id )
    w, h          = dpg.get_item_width( 'mainWindow' ) , dpg.get_item_height('mainWindow' )
    center        = [ width//2, height//2 ]
    r             = width//2 - 20 if width+20 <= height else height//2 - 20
    id_link       = draw_id*100
    
    # DESENHO DA LINHA DE NASCER DO SOL E POR DO SOL 
    azi = SUN_DATA.get_pos_from_date( SUN_DATA.rising )[1]
    alt = SUN_DATA.get_pos_from_date( SUN_DATA.sunset )[1] # [ alt , azi ]
    
    # PEGA OS ANGULOS NOS PONTOS DA TRAJETÓRIA DO SOL 
    dots = SUN_DATA.trajetory(100, all_day )
    dots = [ [ x - math.pi/2 ,  y ] for x, y, _ in dots ]
    dots = [ [ center[0] + math.cos(x)*r, center[1] + math.sin(x)*math.cos(y)*r ] for x, y in dots ]
    
    # DESENHO DO SOL NA SUA POSIÇÃO 
    sun = [  SUN_DATA.azi - math.pi/2, SUN_DATA.alt ] 
    sun = [ center[0] + math.cos(sun[0])*r, center[1] + math.sin(sun[0])*math.cos(sun[1])*r ]
    
    # DESENHO ESTÁTICO
    dpg.configure_item( id_link+1 , p1     = [center[0] - r, center[1]], p2     = [center[0] + r, center[1]]                                           )
    dpg.configure_item( id_link+2 , p1     = center                    , p2     = [center[0] + r*math.cos(azi-math.pi/2), center[1] + r*math.sin(azi-math.pi/2)] )
    dpg.configure_item( id_link+3 , p1     = center                    , p2     = [center[0] + r*math.cos(alt-math.pi/2), center[1] + r*math.sin(alt-math.pi/2)] )
    dpg.configure_item( id_link+4 , center = center                    , radius = r      )
    dpg.configure_item( id_link+5 , center = center                    , radius = 3      )
    dpg.configure_item( id_link+6 , pos    = [center[0] - (r + 20), center[1] -10 ]      )
    dpg.configure_item( id_link+7 , pos    = [center[0] + (r +  5), center[1] -10 ]      )
    dpg.configure_item( id_link+8 , pos    = [center[0] - 10 , center[1] - (r + 25) ]    )
    dpg.configure_item( id_link+9 , points = dots                                        )
    dpg.configure_item( id_link+10, p1     = center                    , p2     = sun    )
    dpg.configure_item( id_link+11, center = sun                                         )
    for n, p in enumerate(dots):
        dpg.configure_item( id_link+(12+n) , center = p )

def att_sunpos_graphs( ):
    last_date = SUN_DATA.date
    if not dpg.get_value( HORA_MANUAL ): SUN_DATA.set_date( dt.datetime.utcnow() )  
    else:                                SUN_DATA.set_date( dt.datetime( dpg.get_value(YEAR), dpg.get_value(MONTH), dpg.get_value(DAY), dpg.get_value(HOUR), dpg.get_value(MINUTE), dpg.get_value(SECOND) ) )    
    
    azi_alt = SUN_DATA.trajetory( 50, all_day = False )
    SUN_DATA.set_date( last_date )

    AZI = [] 
    ALT = [] 
    PTI = [] 
    for azi, alt, tim in azi_alt: 
        AZI.append( math.degrees(azi - math.pi) if azi > math.pi else math.degrees(azi + math.pi) )
        ALT.append( math.degrees(alt) if alt < math.pi else 0  )
        PTI.append( int( dt.datetime.timestamp( tim )) ) 
    
    azi, alt  = [math.degrees(SUN_DATA.azi)], [math.degrees(SUN_DATA.alt)]
    time_scrt = [math.degrees(dt.datetime.timestamp( last_date ))]
    
    SUN_DATA.set_date( last_date )

    dpg.configure_item (2_2_1_3, x    = PTI      , y    = AZI     )
    dpg.configure_item (2_2_1_4, x    = time_scrt, y    = azi )
    dpg.set_axis_limits(2_2_1_1, ymin = PTI[0]   , ymax = PTI[-1] )
    dpg.configure_item (2_2_2_3, x    = PTI      , y    = ALT     )
    dpg.configure_item (2_2_2_4, x    = time_scrt, y    = alt )
    dpg.set_axis_limits(2_2_2_1, ymin = PTI[0]   , ymax = PTI[-1] )

# MAIN FUNCTIONS 
def init_visualizacaoGeral( windows : dict ):
    # POSIÇÂO DO SOL 
    with dpg.window( label = 'Posição solar' , tag = 21_0, pos      = [50,50], width    = 500  , height      = 500 , no_move  = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as Posicao_sol_VG:
        windows["Visualizacao geral"].append( Posicao_sol_VG )
        w, h = dpg.get_item_width(2_1_0), dpg.get_item_height(2_1_0)
        dpg.add_drawlist      ( tag      = 2_1_1_0, width     = w-20  , height = h-50, label = 'Solar')
        draw_sun_trajetory( draw_id = 2_1_1_0, parent_id = 2_1_0 )

    # VISOR DAS POSIÇÔES DO SOL - USAR GRÀFICOS - MESMO DO TOOLTIP 
    with dpg.window( label = 'Atuação'       , tag = 22_0, no_move  = True   , no_resize = True, no_collapse = True, no_close = True ) as Atuacao_VG:
        windows["Visualizacao geral"].append( Atuacao_VG )
        dpg.add_text('Área para a atução da posição dos paineis solares')
        with dpg.group( horizontal = True ): 
            with dpg.plot( tag = 2_2_1_0, label = 'Azimute do dia', height = 312, width = 478, anti_aliased = True ): 
                dpg.add_plot_legend()
                dpg.add_plot_axis( dpg.mvXAxis, label = 'Hora [h]'  , tag = 2_2_1_1, parent = 2_2_1_0, time = True ) # X
                dpg.add_plot_axis( dpg.mvYAxis, label = 'Angulo [º]', tag = 2_2_1_2, parent = 2_2_1_0 ) # Y 
                dpg.set_axis_limits_auto( 2_2_1_1 )
                dpg.set_axis_limits     ( 2_2_1_2, -5, 370 )
                dpg.add_line_series     ( [], [], tag = 2_2_1_3, label = 'Rota diária', parent = 2_2_1_2 )
                dpg.add_scatter_series  ( [], [], tag = 2_2_1_4, label = 'Ponto atual', parent = 2_2_1_2 ) 
       
            with dpg.plot( tag = 2_2_2_0, label = 'Altitude do dia', height = 312, width = 478, anti_aliased = True ): 
                dpg.add_plot_axis( dpg.mvXAxis, label = 'Hora [h]'  , tag = 2_2_2_1, parent = 2_2_2_0, time = True ) # X
                dpg.add_plot_axis( dpg.mvYAxis, label = 'Angulo [º]', tag = 2_2_2_2, parent = 2_2_2_0 ) # Y 
                dpg.set_axis_limits_auto( 2_2_2_1 )
                dpg.set_axis_limits     ( 2_2_2_2, -5, 100 )
                dpg.add_plot_legend()
                dpg.add_line_series     ( [], [], tag = 2_2_2_3, label = 'Rota diária', parent = 2_2_2_2 )
                dpg.add_scatter_series  ( [], [], tag = 2_2_2_4, label = 'Ponto atual', parent = 2_2_2_2 ) 
            
            att_sunpos_graphs( ) 
        
    # CONFIGURAÇÔES DE TEMPO - USAR WINDOW NO HOUR_MANUAL 
    with dpg.window( label = 'Painel de log' , tag = 23_0, no_move  = True   , no_resize = True, no_collapse = True, no_close = True, no_title_bar = True ) as Painel_log_VG:
        windows["Visualizacao geral"].append( Painel_log_VG )
        
        dpg.add_text('Informações gerais do sistema')
        with dpg.child_window( autosize_x = True, height = 170, menubar = True):
            with dpg.menu_bar( label = 'menubar para datetime',):
                dpg.add_menu_item( label = 'Hora automática', callback = lambda s, d, u : dpg.set_value(HORA_MANUAL, False), shortcut = 'A data e hora de calculo é definida automaticamente de acordo com a hora do controlador local')
                dpg.add_menu_item( label = 'Hora manual'    , callback = lambda s, d, u : dpg.set_value(HORA_MANUAL, True) , shortcut = 'A data e hora de calculo é definida pela entrada do operador no supervisório' )

            with dpg.child_window( tag = 2_3_1_0):
                #Informações gerais do sistema - Automático 
                dpg.add_text('Hora automática')
                dpg.add_drag_floatx( label = 'Ano/Mes/Dia Auto'  , tag = 2_3_1, size = 3, format = '%.0f', speed = 0.1 , min_value = 1   , max_value = 3000   , no_input = True )
                dpg.add_drag_floatx( label = 'Hora/Min/Sec Auto' , tag = 2_3_2, size = 3, format = '%.0f', speed = 0.1 , no_input  = True                                                                             )
                dpg.add_drag_int   ( label = 'Valor no dia'      , tag = 2_3_3, format = '%.0f'          , speed = 0.1 , min_value = 0   , max_value = 26*3600, no_input = True, source = TOT_SECONDS, enabled = False)
                dpg.add_drag_int   ( label = 'Dia Juliano'       , tag = 2_3_4, format = '%.0f'          , speed = 0.1 , min_value = 0   , max_value = 366    , no_input = True, source = JULIANSDAY , enabled = False)
           
            with dpg.child_window( tag = 2_3_2_0):
                # Informações gerais do sistema - Manual  
                dpg.add_text('Hora manual')
                dpg.add_input_floatx( label = 'Ano/Mes/Dia Manual' , tag = 2_3_6, size = 3, default_value = [2020, 12, 25], format='%.0f', min_value = 1, max_value = 3000 )
                dpg.add_input_floatx( label = 'Hora/Min/Sec Manual', tag = 2_3_7, size = 3, default_value = [20, 30, 10]  , format='%.0f', min_value = 1, max_value = 60   )
                dpg.add_drag_int    ( label = 'Valor no dia'       , tag = 2_3_8, format = '%.0f', speed = 0.1 , min_value = 0, max_value = 24*3600, no_input = True, source = TOT_SECONDS, enabled = False )
                dpg.add_drag_int    ( label = 'Dia Juliano'        , tag = 2_3_9, format = '%.0f', speed = 0.1 , min_value = 0, max_value = 366    , no_input = True, source = JULIANSDAY , enabled = False )

            dpg.hide_item( 2_3_2_0 ) if dpg.get_value(HORA_MANUAL) == False else dpg.hide_item( 2_3_1_0 )
        
        dpg.add_spacer( height = 5 )
        with dpg.child_window( tag = 2_3_3_0, autosize_x = True, autosize_y = True ): 
            # Definições de longitude e latitude local
            with dpg.child_window( height = 90 ):
                dpg.add_text('Definições de longitude e latitude local')
                dpg.add_input_float( label = 'Latitude' , tag = 2_3_10, min_value = -90, max_value = 90, format = '%3.8f', indent=0.01, source = LATITUDE , callback = lambda sender, data, user : SUN_DATA.set_latitude( data ) )
                dpg.add_spacer( )
                dpg.add_input_float( label = 'Longitude', tag = 2_3_11, min_value = -90, max_value = 90, format = '%3.8f', indent=0.01, source = LONGITUDE, callback = lambda sender, data, user : SUN_DATA.set_longitude( data ) )
            
            dpg.add_spacer( height = 5 )
            with dpg.child_window( height = 150 ): 
                # Informações do sol 
                dpg.add_text('Informacoes do sol')
                dpg.add_drag_float( label = 'Azimute'      , tag = 2_3_12, format='%4.2f', speed=1, no_input= True, source = AZIMUTE )
                dpg.add_spacer( )
                dpg.add_drag_float( label = 'Altitude'     , tag = 2_3_13, format='%4.2f', speed=1, no_input= True, source = ZENITE )
                dpg.add_spacer( )
                dpg.add_drag_float( label = 'Elevação (m)' , tag = 2_3_14, format='%4.0f', speed=1, no_input= True, source = ALTITUDE )
                dpg.add_spacer( )
                dpg.add_drag_floatx( label = 'Horas de sol', tag = 2_3_15, size = 3, format='%.0f', no_input= True )
            
            dpg.add_spacer( height = 5 )
            with dpg.child_window( height = 200 ):
                # Posições de interesse
                dpg.add_text("Posicoes de interesse", )
                dpg.add_text('Nascer do sol (hh/mm/ss)')
                dpg.add_drag_floatx( tag = 2_3_16, size = 3, format='%.0f', speed=1, no_input= True, callback = lambda sender, data, user : dpg.set_value( H_SUNRISE     , data.extend([0]))  )
                dpg.add_spacer( )
                dpg.add_text('Culminante (hh/mm/ss)'   )
                dpg.add_drag_floatx( tag = 2_3_17, size = 3, format='%.0f', speed=1, no_input= True, callback = lambda sender, data, user : dpg.set_value( H_SUNSET      , data.extend([0]))  )
                dpg.add_spacer( )
                dpg.add_text('Por do sol (hh/mm/ss)'   )
                dpg.add_drag_floatx( tag = 2_3_18, size = 3, format='%.0f', speed=1, no_input= True, callback = lambda sender, data, user : dpg.set_value( H_CULMINANT, data.extend([0]))  )

def resize_visualizacaoGeral( ):
    # get the main_window dimension 
    w , h  = dpg.get_item_width( 'mainWindow' ), dpg.get_item_height( 'mainWindow' ) 
    
    dpg.configure_item( 21_0    , width = w*2/3   , height    = h*3/5       , pos = [10 , 25 ]               ) # DRAWING 
    dpg.configure_item( 22_0    , width = w*2/3   , height    = (h*2/5)-35  , pos = [10 , (h*3/5)+30 ]       ) # SUNPATH
    dpg.configure_item( 23_0    , width = w/3 -20 , height    =  h - 30     , pos = [ w*2/3 +15, 25 ]        ) # LOG 
    
    # get the child_window_window dimension 
    w1, h1 = dpg.get_item_width( 2_1_0 ), dpg.get_item_height( 2_1_0 ) 
    dpg.configure_item( 2_1_1_0  , width = w1-20       , height    = h1-50                                        ) # DRAWLIST
    update_sun_trajetory(     draw_id = 2_1_1_0    , parent_id = 2_1_0                                        ) # DRAWING 

    # SUNPATH ATT CHILD_WINDOW 
    dpg.configure_item( 2_2_1_0  , width = (w/3)-15    , height    = (h*2/5)*0.8 , pos = [ 5            , 20 ]    ) # GIRO
    dpg.configure_item( 2_2_2_0  , width = (w/3)-15    , height    = (h*2/5)*0.8 , pos = [ (w*2/3)//2 +5, 20 ]    ) # ELEVAÇÃO 

def render_visualizacaoGeral( ):
    global TOT_SECONDS , JULIANSDAY, HORA_MANUAL
    global HOUR, MINUTE, SECOND
    global YEAR, MONTH , DAY

    # Horário automático 
    if dpg.get_value( HORA_MANUAL ) == False :
        SUN_DATA.update_date()
        dpg.set_value( 23_1, value = [ dpg.get_value(YEAR), dpg.get_value(MONTH) , dpg.get_value(DAY)   ] )  # DIA ATUTOMÁTICO 
        dpg.set_value( 23_2, value = [ dpg.get_value(HOUR), dpg.get_value(MINUTE), dpg.get_value(SECOND)] )  # HORA AUTOMÁTICA
        dpg.hide_item( 23_2_0 )
        dpg.show_item( 23_1_0 )

    # Horário manual 
    else:        
        yearm, monthm, daym     = dpg.get_value( 23_6 )[:-1]
        hourm, minutem, secondm = dpg.get_value( 23_7 )[:-1]
        try:
            data = dt.datetime( int(yearm), int(monthm), int(daym), int(hourm), int(minutem), int(secondm) )
            dt.datetime.timestamp( data )
            SUN_DATA.set_date( data )
            SUN_DATA.update()
            dpg.set_value(YEAR  , yearm  )
            dpg.set_value(MONTH , monthm )
            dpg.set_value(DAY   , daym   ) 
            dpg.set_value(HOUR  , hourm  )
            dpg.set_value(MINUTE, minutem)
            dpg.set_value(SECOND, secondm)
        except:
            pass 

        # Total de segundos no dia
        dpg.set_value( 23_9, SUN_DATA.dia_juliano   )                              # DIA JULIANO
        dpg.set_value( 23_8, SUN_DATA.total_seconds)                               # TOTAL DE SEGUNDOS 
        
        dpg.hide_item( 23_1_0 )
        dpg.show_item( 23_2_0 )
        
    # Setar o Azimute, Altitude e Elevação
    dpg.set_value( 23_12, math.degrees( SUN_DATA.azi) )                            #  AZIMUTE               
    dpg.set_value( 23_13, math.degrees( SUN_DATA.alt) )                            #  ALTITUDE               
    dpg.set_value( 23_14, SUN_DATA.altitude           )                            #  ELEVAÇÃO

    # Seta as horas do sol calculando as horas minutos e segundos de segundos totais 
    diff_sunlight = (SUN_DATA.sunset - SUN_DATA.rising).seconds
    dpg.set_value( 2_3_15, [diff_sunlight//3600, (diff_sunlight//60)%60 , diff_sunlight%60 ] )

    # Setar as informações de Nascer do sol, Culminante (ponto mais alto) e Por do sol
    dpg.set_value( 23_16, [ SUN_DATA.rising.hour+SUN_DATA.utc_local , SUN_DATA.rising.minute , SUN_DATA.rising.second  ] ) # 'Nascer do sol'
    dpg.set_value( 23_17, [ SUN_DATA.transit.hour+SUN_DATA.utc_local, SUN_DATA.transit.minute, SUN_DATA.transit.second ] ) # 'Culminante'   
    dpg.set_value( 23_18, [ SUN_DATA.sunset.hour+SUN_DATA.utc_local , SUN_DATA.sunset.minute , SUN_DATA.sunset.second  ] ) # 'Por do sol'      

    update_sun_trajetory( draw_id = 21_1_0 , parent_id = 21_0 )
    att_sunpos_graphs()


# ATUADORES SERIAL
class UART_COM( Serial ):
    seriais_available = [] 
    BUFFER_MAX = 30
    BUFFER_IN  = []
    BUFFER_OUT = [] 

    COUNTER_OUT = 0 
    COUNTER_IN  = 0 

    def __init__ ( self, COM : str, baudrate : int = 115200, timeout : int = 1, *args, **kwargs ):
        try: 
            super().__init__( COM, baudrate = baudrate, timeout = timeout, parity = PARITY_ODD)
            self.seriais_available.append( COM )  
            self.BAUDS     = baudrate
            self.TIMEOFF   = timeout
            self.COMPORT   = COM
        except:
            print( "Serial comport cant be opened" ) 
        
    def _write(self, data  : bytes ):
        return super().write(data)
    
    def _read(self, size : int = 1 ):
        return super().read( size = size )

    def write( self, msg : Union[str, bytes] ): 
        if self.connected: 
            if type( msg ) == str: 
                self.BUFFER_OUT.append( msg.encode() )
                self._write( self.BUFFER_OUT[-1] )
            elif type( msg ) == bytes:
                self.BUFFER_OUT.append( msg )
                self._write( self.BUFFER_OUT[-1] )
            else: 
                return -1 
            if len(self.BUFFER_OUT) > self.BUFFER_MAX:
                self.BUFFER_OUT.pop( 0 )
            self.COUNTER_OUT += 1 
            return True
        else: 
            return -1 

    def read( self, n_bytes : int = 0 ):
        if self.connected:
            if n_bytes == 0:
                n_bytes = self.in_waiting() 
                if n_bytes == 0:
                    return False 
            self.BUFFER_IN.append( self._read( n_bytes ) ) 
            if len(self.BUFFER_IN) > self.BUFFER_MAX: 
                self.BUFFER_IN.pop(0)
            self.COUNTER_IN += 1 
            return self.BUFFER_IN[-1]
        else:
            return False 
    
    def in_waiting(self):
        try: 
            if self.connected: 
                return super().in_waiting 
            else: 
                return -1 
        except: 
            print("Erro no In_Waiting")
            return -1 

    @property
    def connected( self ):
        return super().isOpen() 

    def close(self):
        try:
            super().close()
            self.BUFFER_IN   = []
            self.BUFFER_OUT  = []
            return  True
        except:
            return -1 

    def connect(self):
        if not self.connected: 
            try: 
                super().__init__( self.COMPORT, baudrate = self.BAUDS, timeout = self.TIMEOFF )
                return True
            except:
                return -1 

    def get_serial_ports( self, lenght : int = 25 ):
        if self.connected:
            portList = [ self.COMPORT ]
        else: 
            portList = [] 

        if sys.platform.startswith('win'):  
            ports = ['COM%s' % (i + 1) for i in range( lenght )]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        else:
            print("Sistema Operacional não suportado")
        for port in ports:
            try:
                s = Serial( port )
                s.close()
                portList.append(port)
            except (OSError, SerialException):
                pass
        self.seriais_available = portList
        return portList

COMP = UART_COM( "" )

D1 = time.time() 

def serial_capture_frames(): 
    global COMP, MSG_INIT, MSG_COUNT
    global MPE_LIST, MPE_COUNT, SPE_LIST
    global MPG_LIST, MPG_COUNT, SPG_LIST
    global MPE, MPG, ALTITUDE, AZIMUTE
    global MDE_LIST, MDG_LIST 
    global GPHG_ATT, GPHE_ATT
    global MS_GIRO, PS_GIRO, TM_GIRO, CNT_GIRO 
    global MS_ELE , PS_ELE , TM_ELE , CNT_ELE

    if COMP.is_open: 
        for ind, byte in enumerate(COMP.BUFFER_IN[-1][:-1]):
            if byte == MSG_INIT[MSG_COUNT]: 
                MSG_COUNT = MSG_COUNT +  1
            else:
                MSG_COUNT = 0 
            if MSG_COUNT == 4: 
                MSG_COUNT = 0
                OP = COMP.BUFFER_IN[-1][ind+1]

                if OP == ord('e'):
                    try:
                        value = COMP.BUFFER_IN[-1][ind+2:ind+6]
                        value = struct.unpack('f', value )[0]
                        dpg.set_value(MPE, value) 
                        MPE_LIST.append( dpg.get_value(MPE) )
                        SPE_LIST.append( dpg.get_value(ZENITE) )
                        #MDE_LIST.append( int ( dt.datetime.timestamp( dt.datetime.utcnow() - dt.timedelta(hours=3) ) ) )
                        MDE_LIST.append( MPE_COUNT ) 
                        MPE_COUNT += 1
                        
                        # ELEVAÇÂO
                        if value:
                            if len(MPE_LIST) > 1000:
                                MPE_LIST.pop(0)
                                SPE_LIST.pop(0)
                                MDE_LIST.pop(0)
                        
                            dpg.configure_item( 45_1_1, x = MDE_LIST, y = MPE_LIST )
                            dpg.configure_item( 45_1_2, x = MDE_LIST, y = SPE_LIST )
                            dpg.set_axis_limits( 'x_axis_alt', ymin = MDE_LIST[0], ymax = MDE_LIST[-1])
                            
                            CNT_ELE += 1 
                            if CNT_ELE == 500:
                                CNT_ELE = 0
                                TM_ELE.append( MDE_LIST.pop(-1) )
                                MS_ELE.append( MPE_LIST.pop(-1) )
                                PS_ELE.append( SPE_LIST.pop(-1) )
                                if len(MS_ELE) > 7_200:
                                    MS_ELE.pop(0)
                                    TM_ELE.pop(0)
                                    PS_ELE.pop(0)
                                dpg.set_axis_limits( 51_20, ymin = TM_ELE[0], ymax = TM_ELE[-1] )
                                dpg.configure_item ( 51_40, x    = TM_ELE   , y    = MS_ELE     )
                                dpg.configure_item ( 51_50, x    = TM_ELE   , y    = PS_ELE     ) 

                    except struct.error as e:
                        print( e )

                elif OP == ord('g'):
                    try: 
                        value = COMP.BUFFER_IN[-1][ind+2:ind+6]
                        value = struct.unpack('f', value )[0]
                        dpg.set_value(MPG, value) 
                        MPG_LIST.append( dpg.get_value(MPG) )
                        SPG_LIST.append( dpg.get_value(AZIMUTE) )
                        #MDG_LIST.append(dt.datetime.timestamp( dt.datetime.utcnow() - dt.timedelta( hours = 3 )) ) 
                        MDG_LIST.append( MPG_COUNT ) 
                        MPG_COUNT += 1
                        if value:
                            if len(MPG_LIST) > 1000:
                                MPG_LIST.pop(0)
                                SPG_LIST.pop(0)
                                MDG_LIST.pop(0)
                            
                            dpg.set_axis_limits( 'x_axis_azi', ymin = MDG_LIST[0], ymax = MDG_LIST[-1])
                            dpg.configure_item( 44_11, x = MDG_LIST, y = MPG_LIST )
                            dpg.configure_item( 44_12, x = MDG_LIST, y = SPG_LIST )

                            CNT_GIRO += 1 
                            if CNT_GIRO == 500: 
                                CNT_GIRO = 0 
                                MS_GIRO.append( MPG_LIST.pop(-1) )
                                PS_GIRO.append( SPG_LIST.pop(-1) )
                                TM_GIRO.append( MDG_LIST.pop(-1)  )
                                if len( MS_GIRO ) > 7_200:
                                    MS_GIRO.pop(0)
                                    PS_GIRO.pop(0)
                                    TM_GIRO.pop(0)
                                dpg.set_axis_limits( 52_20, ymin = TM_GIRO[0], ymax=TM_GIRO[-1])
                                dpg.configure_item ( 52_40, x = TM_GIRO, y = MS_GIRO)
                                dpg.configure_item ( 52_50, x = TM_GIRO, y = PS_GIRO)
                                
                    except struct.error as e:
                        print( e )

                elif OP == ord('H'):
                    value = COMP.BUFFER_IN[-1][ind+2:ind+8]
                    y, m, d, h, mn, s = struct.unpack( 'bbbbbb', value )
                    if y < 22 or y > 50 or m > 12 or d > 31:
                        if h >= 24 or mn >= 60 or s >= 60: 
                            dpg.set_value( WRONG_DATETIME, True ) 
                    else: 
                        date = dt.datetime.now()
                        if y != date.year-2000 or m != date.month or d != date.day :
                            dpg.set_value( WRONG_DATETIME, True ) 
                        elif h != date.hour or ( date.minute + 5 < mn < date.minute - 5 ):
                            dpg.set_value( WRONG_DATETIME, True ) 
                        dpg.set_value( WRONG_DATETIME, False )

                elif OP == ord('D'):
                    NBYTES = COMP.BUFFER_IN[-1][ind+2]
                    msg = COMP.BUFFER_IN[-1][ind+3:]
                    if NBYTES < 70:
                        COMP.read()
                        msg += COMP.BUFFER_IN[-1]
                        if '\\\\'.encode() not in msg: 
                            serial_write_message(None, None, 'INITP' )
                            break
                    if NBYTES == len(msg)-2:
                        #try:
                        dpg.set_value( 54300, struct.unpack( 'f', msg[  : 4] )[0]                          )
                        dpg.set_value( 54301, struct.unpack( 'f', msg[ 4: 8] )[0]                          )
                        dpg.set_value( 54302, struct.unpack( 'f', msg[ 8:12] )[0]                          )
                        dpg.set_value( 54303, float( int.from_bytes( msg[12:23], 'little', signed = False ) ) )
                        dpg.set_value( 54304, struct.unpack( 'f', msg[23:27] )[0]                          )
                        dpg.set_value( 54305, struct.unpack( 'f', msg[27:31] )[0]                          )
                        dpg.set_value( 54306, struct.unpack( 'f', msg[31:35] )[0]                          )
                        dpg.set_value( 54307, struct.unpack( 'f', msg[35:39] )[0]                          )
                        dpg.set_value( 54308, struct.unpack( 'f', msg[39:43] )[0]                          )
                        dpg.set_value( 54309, struct.unpack( 'f', msg[43:47] )[0]                          )
                        dpg.set_value( 54310, float( int.from_bytes( msg[47:58], 'little', signed = False ) ) )
                        dpg.set_value( 54311, struct.unpack( 'f', msg[58:62] )[0]                          )
                        dpg.set_value( 54312, struct.unpack( 'f', msg[62:66] )[0]                          )
                        dpg.set_value( 54313, struct.unpack( 'f', msg[66:70] )[0]                          )
     
def serial_verify_connection(): 
    global COMP
    if not COMP.is_open: 
        dpg.hide_item( 42_6 )
        dpg.hide_item( 42_7 )
        dpg.show_item( 42_4 )
        dpg.set_value( SERIAL_CONNECTED, False)
    else: 
        if COMP.BUFFER_IN == []:
            dpg.set_value( 46_2_1_1, "CONECTADO!" )

def serial_atualize_actuator_cmd( ): 
    global COMP 
    if COMP.is_open:    
        if COMP.read():
            serial_capture_frames() 
            MSG  = ''
            for n, row in enumerate( COMP.BUFFER_IN ):
                MSG += '[{}] '.format( COMP.COUNTER_IN + n - len(COMP.BUFFER_IN) )
                if dpg.get_value( CMD_MODE ) == 'ASCII': 
                    for collum in row: 
                        MSG += chr(168) if collum < 32 or collum == 127 else chr(collum)
                    MSG += '\n'
                elif dpg.get_value( CMD_MODE ) == 'HEX': 
                    for collum in row: 
                        if collum == 10: MSG += '\n'
                        else:            MSG += str(hex(168)) if collum < 32 or collum == 127 else str(hex(collum)) + ' '
                    MSG += '\n'
            dpg.set_value( 46_2_1_1, MSG )
            dpg.set_value( 53_1, MSG )
    else:
        dpg.set_value( 46_2_1_1, "DESCONECTADO" ) 

def serial_refresh( sender, data, user ): 
    global COMP 
    dpg.configure_item( 42_1_1, label = 'Procurando' ) 
    dpg.configure_item( 42_1  , items = COMP.get_serial_ports( 20 ) )
    dpg.configure_item( 42_1_1, label = 'Refresh' )

def serial_try_to_connect( sender, data, user ): 
    global COMP 
    COMP = UART_COM( dpg.get_value(SERIAL_PORT), baudrate = int(dpg.get_value(SERIAL_BAUDRATE)), timeout = dpg.get_value(SERIAL_TIMEOUT) )
    if COMP.is_open:
        dpg.show_item( 42_6 )
        dpg.show_item( 42_7 )
        dpg.bind_item_theme( item = 42_6, theme = theme_button_on  )
        dpg.bind_item_theme( item = 42_7, theme = theme_button_off )
        dpg.hide_item( 42_4 )
        dpg.set_value( SERIAL_CONNECTED, True)
    else:   
        dpg.hide_item( 42_6 )
        dpg.hide_item( 42_7 )
        dpg.show_item( 42_4 )
        dpg.set_value( SERIAL_CONNECTED, False)

def serial_write_message(sender, data, user ):
    global COMP
    ## Control Params 
    if user   == 'INITCM':
        user   = 'INITCM'.encode()
        user  += struct.pack('ff', dpg.get_value(46_1_1_4_3)[0], dpg.get_value(46_1_1_4_3)[1] )
    if user   == 'INITCP':
        user   = 'INITCM'.encode()
        user  += struct.pack('ff', dpg.get_value(AZIMUTE), dpg.get_value(ZENITE) )
        print(dpg.get_value(AZIMUTE), dpg.get_value(ZENITE))
        
    elif user == 'INITCm':
        user   = 'INITCm'.encode()
        user  += 'G'.encode() if dpg.get_value(46_1_1_4_5) == 'Gir' else 'E'.encode()
        user  += struct.pack('f', dpg.get_value(46_1_1_4_4))
    elif user == 'INITCp':
        user   =  'INITC'.encode()
        user  +=  'G'.encode() if dpg.get_value(46_1_1_4_21) == 'Gir' else 'E'.encode()
        user  +=  dpg.get_value(46_1_1_4_22)
        user  +=  struct.pack( 'f', dpg.get_value(46_1_1_4_1) )

    ## Datetime Params 
    elif user == "INITHA":
        user = b'INITH' 
        datetime = dt.datetime.now()
        year     = struct.pack( 'b', datetime.year if datetime.year < 2000 else datetime.year - 2000 ) 
        month    = struct.pack( 'b', datetime.month  )
        day      = struct.pack( 'b', datetime.day    )
        hour     = struct.pack( 'b', datetime.hour   )
        minute   = struct.pack( 'b', datetime.minute )
        second   = struct.pack( 'b', datetime.second )
        user += chr(6).encode() + year + month + day + hour + minute + second 

    elif user == 'INITH':
        user  = "INITH".encode() 
        date  = dpg.get_value( 46_1_1_1 )
        hour  = dpg.get_value( 46_1_1_2 ) 
        if date[0] > 31:    raise 'days out of range'
        if date[1] > 12:    raise 'months out of range'       
        if hour[0] > 60:    raise 'seconds out of range'
        if hour[1] > 60:    raise 'minutes out of range'
        if hour[2] > 23:    raise 'hours out of range'
        if date[2] > 2000:  date[2] -= 2000
        user += struct.pack( 'bbb', date[0], date[1], date[2])
        user += struct.pack( 'bbb', hour[0], hour[1], hour[2])

    if user == 'manual_send':
        user = dpg.get_value(46_2_2_2)

    try: 
        if type( user ) == bytes: COMP.write( user )
        elif type( user ) == str: COMP.write( user.encode() )
    except SerialException as e:
        print( e )

    print( "Dentro de connections.serial: Sender {}  data {}  user {}".format(sender, data, user ))

def serial_request_diagnosis( sender, data, user ):
    global COMP
    if COMP.is_open:
        COMP.write( 'INITP' )     
    else: 
        print( "COMP NOT OPEN ")

def serial_close_connection(sender, data, user): 
    global COMP
    COMP.close()
    serial_verify_connection() 

def serial_print_comp():
    print( 'serial: ', COMP )

def serial_comp_is_open():
    return COMP.is_open 

# FUNCTIONS 
def change_menubar_cmd( sender, data, user ):
    dpg.set_value( CMD_MODE, user )
    if COMP.connected:
        MSG  = ''
        for n, row in enumerate( COMP.BUFFER_IN ):
            MSG += '[{}] '.format( COMP.COUNTER_IN + n - len(COMP.BUFFER_IN) )
            if user == 'ASCII': 
                for collum in row: 
                    MSG += chr(168) if collum < 32 or collum == 127 else chr(collum)
                MSG += '\n'
            elif user == 'HEX': 
                for collum in row: 
                    MSG += str(hex(168)) if collum < 32 or collum == 127 else str(hex(collum)) + ' '
                MSG += '\n'
        dpg.set_value( 46_2_1_1, MSG )

# MAIN FUNCTIONS 
def handlers_and_themes_atuador():
    dpg.bind_item_theme( item = 43_2_0  , theme = theme_no_border  )
    dpg.bind_item_theme( item = 43_2_1_0, theme = theme_no_border )
    dpg.bind_item_theme( item = 43_2_2_0, theme = theme_no_border )
    dpg.bind_item_theme( item = 43_3_0  , theme = theme_no_border  )
    dpg.bind_item_theme( item = 43_3_1_0, theme = theme_no_border  )
    dpg.bind_item_theme( item = 43_3_2_0, theme = theme_no_border  )
    dpg.bind_item_theme( item = 43_3_1_1, theme = theme_button_off )
    dpg.bind_item_theme( item = 43_3_2_1, theme = theme_button_off )
    dpg.hide_item( 42_0)
    dpg.hide_item( 43_0)
    dpg.hide_item( 44_0)
    dpg.hide_item( 45_0)
    dpg.hide_item( 46_0)

def init_atuador( windows : dict ): 
    # Serial Config 
    with dpg.window( label = 'Serial' , tag = 42_0, width= 455, height= 330, pos = [10,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as serial_AT: 
        windows['Atuadores'].append( serial_AT )

        dpg.add_spacer( height = 1 )
        dpg.add_text('CONFIGURAÇÕES DE COMUNICAÇÃO')
        dpg.add_text('Selecione a porta serial: ')
        with dpg.group( horizontal = True ):
            dpg.add_combo( tag = 42_1, default_value = 'COM12', items = ['COM1', 'COM4', 'COM5', 'COM10', 'COM12', 'COM15', 'COM16'], source = SERIAL_PORT )
            dpg.add_button(  tag = 42_1_1, label = 'Refresh', callback = serial_refresh )
        dpg.add_spacer( height = 1 )

        dpg.add_text('Baudarate: ')
        dpg.add_combo( tag = 42_2, default_value = '115200', items=[ '9600', '19200', '57600', '115200', '1000000'], source = SERIAL_BAUDRATE )
        dpg.add_spacer( height = 1 )

        dpg.add_text('Timeout: ')
        dpg.add_input_int( tag = 42_3, default_value = 1, source = SERIAL_TIMEOUT)
        dpg.add_spacer( height = 3 )

        dpg.add_button(label ='Iniciar conexão',              tag = 42_4 , callback = serial_try_to_connect      )
        with dpg.group( horizontal = True ):
            dpg.add_button(label ="CONECTADO"      , width = 150, tag = 42_6                                 )
            dpg.add_button(label ="DESCONECTAR"    , width = 150, tag = 42_7, callback = serial_close_connection )
        dpg.add_spacer(height = 5)
        dpg.hide_item( 42_6)         
        dpg.hide_item( 42_7) 

    # Step Motors Config 
    with dpg.window( label = 'Motores'    , tag = 43_0, width= 455, height= 480, pos = [10,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as config_AT:
        windows['Atuadores'].append( config_AT )
        
        def change_menubar_motors(sender, data, user ): 
            if user == 'step':
                dpg.show_item(43_2_0)
                dpg.hide_item(43_3_0)
            elif user == 'trif': 
                dpg.show_item(43_3_0)
                dpg.hide_item(43_2_0)

        dpg.add_text( 'CONFIGURAÇÃO DE ACIONAMENTO DOS MOTORES')
        # MENUBAR DE DEFNIÇÃO DOS MOTORES
        with dpg.child_window( autosize_x =True, autosize_y = True, menubar = True ):
            with dpg.menu_bar(label = "menubar_motors"):
                dpg.add_menu_item( label = "Motor de passo"  , callback = change_menubar_motors, user_data = 'step' )
                dpg.add_menu_item( label = "Motor Trifásico" , callback = change_menubar_motors, user_data = 'trif' )

            # DE PASSO 
            with dpg.child_window( tag = 43_2_0, autosize_x =True, autosize_y = True): 
                dpg.add_text('DEFINIÇÃO DOS MOTORES DE PASSO')
                dpg.add_spacer(  height = 15 )
                with dpg.child_window( tag = 43_2_1_0, label = 'MotorGiro'    , autosize_x=True, height = 200 ):
                    dpg.add_text       ( "Motor de Rotação da base - Motor G" )
                    dpg.add_text       ( 'Resolução:' )
                    dpg.add_input_float( tag = 43_2_1_1, default_value = 1.8    , format = '%3.2f', source = MG_RESOLUCAO, callback = serial_write_message, user_data = 'Gir', on_enter = True )
                    dpg.add_text       ( 'Micro Passos do motor:' )
                    dpg.add_combo      ( id=43_2_1_3, default_value = '1/16'    , items  = ['1', '1/2', '1/4', '1/8', '1/16', '1/32'], source = MG_USTEP, callback= serial_write_message, user_data = 'Gir' )
                    dpg.add_text       ( 'Passos por volta:' )
                    dpg.add_drag_float ( tag = 43_2_1_2, default_value =  360 / 1.8, format = '%5.2f', source = MG_STEPS, no_input = True, callback= serial_write_message, user_data = 'Gir' )
            
                with dpg.child_window( tag = 43_2_2_0, label = 'MotorElevação', autosize_x=True, height = 200 ):
                    dpg.add_text       ( "Motor de Rotação da base - Motor 2")
                    dpg.add_text       ( 'Resolução:')
                    dpg.add_input_float( tag = 43_2_2_1, default_value = 1.8      , format = '%3.2f', source = ME_RESOLUCAO, callback = serial_write_message, user_data = 'Ele', on_enter = True )
                    dpg.add_text       ( 'Micro Passos do motor:')
                    dpg.add_combo      ( tag = 43_2_2_3, default_value = '1/16'   , items  = ['1', '1/2', '1/4', '1/8', '1/16', '1/32'], source = ME_USTEP, callback= serial_write_message, user_data = 'Ele' ) 
                    dpg.add_text       ( 'Passos por volta:')
                    dpg.add_drag_float ( tag = 43_2_2_2, default_value = 360 / 1.8, format ='%5.2f', source = ME_STEPS, no_input = True, callback = serial_write_message, user_data = 'Ele'  )
        
            # TRIFÁSICO 
            with dpg.child_window( tag = 43_3_0, autosize_x=True, autosize_y=True ):
                dpg.add_text('DEFINIÇÃO DE ACIONAMENTO TRIFÁSICO')
                
                dpg.add_spacer( height = 15 )
                with dpg.child_window( tag = 43_3_1_0, label = 'MotorGiro'    ,autosize_x = True, height = 100 ):
                    dpg.add_text       ( "Motor de Rotação da base - Motor 1" )
                    dpg.add_spacer     ( )
                    dpg.add_button     ( tag = 43_3_1_1, label= 'Desligado'  ,  width = 250, callback = serial_write_message, user_data='m1')
                    dpg.add_text       ( 'Velocidade angular MG:' )
                    dpg.add_input_float( tag = 43_3_1_2, label = 'Wo (rad/s)', default_value = dpg.get_value(MG_VELANG), source = MG_VELANG, format = '%3.2f', on_enter = True, callback = serial_write_message )
                    # CORRIGIR A TROCA DE MENSAGEM PARA AJUSTAR AS VELOCIDADES
                
                dpg.add_spacer    ( height = 15 )
                with dpg.child_window( tag = 43_3_2_0, label = 'MotorElevação',autosize_x = True, height = 125 ):
                        dpg.add_text       ( "Motor de Rotação da base - Motor 2")
                        dpg.add_spacer     ( )
                        dpg.add_button     ( tag = 43_3_2_1, label='Desligado', width=250, callback = serial_write_message, user_data='m2')
                        dpg.add_text       ( 'Velocidade angular ME:' )
                        dpg.add_input_float( tag = 43_3_2_2, label = 'Wo (rad/s)', default_value = dpg.get_value(ME_VELANG), source = ME_VELANG, format = '%3.2f', on_enter = True, callback = serial_write_message )

            change_menubar_motors( None, None, 'step')
            
    # Azimute Draw 
    with dpg.window( label ='Azimute'     , tag = 44_0, width= 495, height= 330, pos = [470,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as azimute_config_AT: 
        windows['Atuadores'].append( azimute_config_AT)
        
        with dpg.plot( tag = 44_1_0, parent = 44_0, label = 'Azimute e angulo de giro', height = 312, width = 478, anti_aliased = True ): 
            dpg.add_plot_legend( )
            dpg.add_plot_axis  ( dpg.mvXAxis, label = 'Medições [n]', tag = 'x_axis_azi', time = True, no_tick_labels = True )
            dpg.add_plot_axis  ( dpg.mvYAxis, label = 'Angulo [º]' , tag = 'y_axis_azi' )
            dpg.set_axis_limits( 'x_axis_azi',  0,   1 )
            dpg.set_axis_limits( 'y_axis_azi', -5, 375 )
            dpg.add_line_series( [], [], tag = 44_1_1, label = 'Sensor Giro', parent = 'y_axis_azi' )
            dpg.add_line_series( [], [], tag = 44_1_2, label = 'Azimute sol', parent = 'y_axis_azi' ) 
 
    # Zenite / Altitude Draw 
    with dpg.window(label  = 'Zenite'     , tag = 45_0, width= 495, height= 330, pos = [970,25], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as zenite_config_AT:
        windows['Atuadores'].append( zenite_config_AT )  
        
        with dpg.plot( tag = 45_1_0, label = 'Zenite e angulo de elevação', height = 312, width = 478, anti_aliased = True ): 
            dpg.add_plot_legend()
            dpg.add_plot_axis( dpg.mvXAxis, label = 'Medições [n]', tag = 'x_axis_alt', time = True, no_tick_labels = True  )
            dpg.add_plot_axis( dpg.mvYAxis, label = 'Angulo [º]', tag = 'y_axis_alt' )
            dpg.set_axis_limits_auto( 'x_axis_alt')
            dpg.set_axis_limits( 'y_axis_alt', -5, 370 )
            dpg.add_line_series( [], [], tag = 45_1_1, label = 'Sensor Elevação', parent = 'y_axis_alt' )
            dpg.add_line_series( [], [], tag = 45_1_2, label = 'Zenite sol', parent = 'y_axis_alt' ) 
        
    # General Draw 
    with dpg.window( label = 'Draw_Window', tag = 46_0, width= 995, height= 480, pos = [470,360], no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True) as draw_tracker_AT:
        windows['Atuadores'].append( draw_tracker_AT )  
    
        def change_menubar_conf( sender, data, user ): 
            dpg.hide_item(46_1_1_1_0)
            dpg.hide_item(46_1_1_2_0)
            dpg.hide_item(46_1_1_3_0)
            dpg.hide_item(46_1_1_4_0)
            dpg.hide_item(46_1_1_5_0)
            if   user == "State":     dpg.show_item(46_1_1_1_0)   
            elif user == "Power":     dpg.show_item(46_1_1_2_0)   
            elif user == "Date/Time": dpg.show_item(46_1_1_3_0)   
            elif user == "Control":   dpg.show_item(46_1_1_4_0)   
            elif user == "Diagnosis": dpg.show_item(46_1_1_5_0)   

        with dpg.group( horizontal = True):
            with dpg.child_window(tag = 46_1_0, width = (dpg.get_item_width(46_0)*0.4), border = False, menubar = True):
                dpg.add_text('Opções padrão de operação do sistema:')
                with dpg.menu_bar(label = "child_menubar_conf"):
                    dpg.add_menu_item( label = "State"       , callback = change_menubar_conf, user_data = "State"     )
                    dpg.add_menu_item( label = "Power"       , callback = change_menubar_conf, user_data = "Power"     )
                    dpg.add_menu_item( label = "Date/Time"   , callback = change_menubar_conf, user_data = "Date/Time" )
                    dpg.add_menu_item( label = "Control"     , callback = change_menubar_conf, user_data = "Control"   )
                    dpg.add_menu_item( label = "Diagnosis"   , callback = change_menubar_conf, user_data = "Diagnosis" )
            
                # STATES 
                with dpg.child_window( tag = 46_1_1_1_0, width = dpg.get_item_width(46_1_0), autosize_y = True, autosize_x = True, border = True ):
                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data='INITSS')
                        dpg.add_text('S -> Parar o tracker')
                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data='INITSD')
                        dpg.add_text('D -> Entra no modo Demo')
                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data='INITSC')
                        dpg.add_text('C -> Continuar processo')
                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data='INITSL')
                        dpg.add_text('L -> Levers')  
                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data='INITSA')
                        dpg.add_text('A -> Automatic')  
                
                # POWER 
                with dpg.child_window( tag = 46_1_1_2_0, width = dpg.get_item_width(46_1_0), autosize_y = True, autosize_x = True, border = True ):
                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data='INITWO')
                        dpg.add_text('O -> Ativar motores')

                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data='INITWF')
                        dpg.add_text('F -> Desativar motores ')
                    
                # DATA E HORA
                with dpg.child_window( tag = 46_1_1_3_0, width = dpg.get_item_width(46_1_0), autosize_y = True, autosize_x = True, border = True ):
                    dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITH' )
                    dpg.group( horizontal = True )
                    dpg.add_text('H -> Trocar a hora')
                
                    dpg.add_input_intx( tag =46_1_1_1, size=3, default_value=[ 12, 5, 2021 ], max_value = 99, callback = serial_write_message, user_data = 'INITH', on_enter = True )
                    dpg.group( horizontal = True )
                    dpg.add_text('dd/mm/yy')
                
                    dpg.add_input_intx( tag =46_1_1_2, size=3, default_value=[ 15, 35, 10  ], max_value = 60, callback = serial_write_message, user_data = 'INITH', on_enter = True ) 
                    dpg.group( horizontal = True )
                    dpg.add_text('hh:mm:ss') 

                    with dpg.group( horizontal = True ):
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITHA' )
                        dpg.add_text('HA -> Enviar datetime atual')

                
                # CONTROL 
                with dpg.child_window( tag = 46_1_1_4_0, width = dpg.get_item_width(46_1_0), autosize_y = True, autosize_x = True, border = True ):
                    with dpg.group( horizontal = True ):
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITCp' )
                        dpg.add_text('P -> Configurar variáveis de processo')
                    dpg.add_input_float ( tag = 46_1_1_4_1, default_value = 0.5, max_value=1, on_enter = True, callback = serial_write_message, user_data = 'INITCp' )
                    with dpg.group( horizontal = True):
                        dpg.add_radio_button( tag = 46_1_1_4_21, items = ['Gir', 'Ele'], default_value = 'Gir', horizontal = True ) 
                        dpg.add_radio_button( tag = 46_1_1_4_22, items = ['D','I','P'], default_value = 'D', horizontal = True ) 

                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITCM' )
                        dpg.add_text('M -> Mover ambos motores')
                    dpg.add_input_floatx( tag = 46_1_1_4_3, size=2, default_value=[ 12.05, 19.99], on_enter = True, callback = serial_write_message, user_data = 'INITMO')
                 
                    with dpg.group( horizontal = True ):
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITCm' )
                        dpg.add_text('m -> Mover um motore')
                    dpg.add_input_float ( tag = 46_1_1_4_4, default_value = 12, on_enter = True, callback = serial_write_message, user_data = 'INITCm' )
                    dpg.add_radio_button( tag = 46_1_1_4_5, items = ['Gir', 'Ele'], default_value = 'Gir', horizontal = True ) 
                    
                    with dpg.group( horizontal = True ): 
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITCP' )
                        dpg.add_text("P -> Envia Zenite e Azimute como PV")
                    
                # DIAGNÓSTICO 
                with dpg.child_window( tag = 46_1_1_5_0, width = dpg.get_item_width(46_1_0), autosize_y = True, autosize_x = True, border = True ):
                    with dpg.group( horizontal = True ):    
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITPA')
                        dpg.add_text('A -> All info')
                    with dpg.group( horizontal = True ):    
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITPS')
                        dpg.add_text('S -> Sensor Diagnosis')
                    with dpg.group( horizontal = True ):    
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITPP')
                        dpg.add_text('P -> Print Positions')
                    with dpg.group( horizontal = True ):    
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITPZ')
                        dpg.add_text('Z -> Zenite')
                    with dpg.group( horizontal = True ):    
                        dpg.add_button(label='send', callback = serial_write_message, user_data = 'INITPH')
                        dpg.add_text('H -> Altitude')
                change_menubar_conf( None, None, 'State')

            with dpg.child_window( tag = 46_2_0, width= (dpg.get_item_width(46_0)*0.6), autosize_y = True, border = False, menubar = True ):
                dpg.add_text( 'PICO_SM: RP2040 Serial Monitor')
                with dpg.menu_bar(label = "child_menubar_cmd"):
                    dpg.add_menu_item( label = "ASCII" , callback = change_menubar_cmd, user_data = "ASCII" )
                    dpg.add_menu_item( label = "HEX"   , callback = change_menubar_cmd, user_data = "HEX"   )
                  
                with dpg.child_window  ( tag = 46_2_1_0, autosize_x = True, border = True ):
                    dpg.add_text( 'CMD:')     
                    dpg.add_text( tag = 46_2_1_1, default_value = 'DESCONECTADO!', tracked = True, track_offset = 1, )
                
                with dpg.child_window     ( tag   = 46_2_2_0  , autosize_x = True , pos=[0, dpg.get_item_height(46_0)-54] ):
                    with dpg.group        ( tag   = 46_2_2_1_0, horizontal = True ):
                        dpg.add_text      ( tag   = 46_2_2_1  , default_value =  "To send: "    )
                        dpg.add_input_text( tag   = 46_2_2_2  , on_enter =  True , callback = serial_write_message, user_data = 'manual_send' )
                        dpg.add_button    ( label = 'send'    , callback =  serial_write_message, user_data = 'manual_send' )
    
    # Aply handlers 
    handlers_and_themes_atuador()

def resize_atuador(): 
    cw = dpg.get_item_width( 'mainWindow' )/ 1474
    ch = dpg.get_item_height( 'mainWindow')/ 841 

    # General Draw              46_0
    dpg.configure_item( 46_0     , width  = cw*995, height = ch*480, pos = [cw*470, ch*360] ) #[995, 480] -> Draw 
    dpg.configure_item( 46_1_0   , width  = (cw*995)*0.4     ) 
    dpg.configure_item( 46_2_0   , width  = (cw*995)*0.575   )
    dpg.configure_item( 46_2_1_0 , height = (cw*480)-100     )
    dpg.configure_item( 46_2_2_0 , pos    = [0, (cw*480)-54] )
    dpg.configure_item( 46_2_2_2 , width  = (cw*995)*0.525   )
    # Zenite / Altitude Draw    45_0 
    dpg.configure_item( 45_0  , width = cw*495, height = ch*330, pos = [cw*970, ch*25 ] ) #[495, 330] -> Zenite 
    dpg.configure_item( 45_1_0, width = cw*478, height = ch*312 )
    # Azimute Draw              44_0
    dpg.configure_item( 44_0  , width = cw*495, height = ch*330, pos = [cw*470, ch*25 ] ) #[495, 330] -> Azimue
    dpg.configure_item( 44_1_0, width = cw*478, height = ch*312 )
    # Step Motors Config        43_0 
    dpg.configure_item( 43_0, width = cw*455, height = ch*520, pos = [cw*10 , ch*320] ) #[455, 480] -> Motores
    # Serial Config             42_0 
    dpg.configure_item( 42_0, width = cw*455, height = ch*298, pos = [cw*10 , ch*25 ] ) #[455, 330] -> Serial

def render_atuador() : 
    serial_verify_connection()
    serial_atualize_actuator_cmd()

    
# SENSORES
def resize_sensores(): 
    new_w, new_h = dpg.get_item_width('mainWindow'), dpg.get_item_height('mainWindow')
    dpg.configure_item( 5_1_0, width = new_w*0.65   , height = new_h*0.4   , pos = [10, 25]           )
    dpg.configure_item( 5_2_0, width = new_w*0.65   , height = new_h*0.4   , pos = [10, new_h*0.4+30] )
    dpg.configure_item( 5_3_0, width = new_w*0.65   , height = new_h*0.2-40, pos = [10, new_h*0.8+35] )
    dpg.configure_item( 5_4_0, width = new_w*0.35-20, height = new_h-30    , pos = [new_w*0.65+15,25] )
    dpg.configure_item( 5_1_1, width = new_w*0.639  , height = new_h*0.375                            )
    dpg.configure_item( 5_2_1, width = new_w*0.639  , height = new_h*0.375                            )

def init_sensores( windows : dict ):       
    with dpg.window(tag = 51_0, no_title_bar=True, no_move=True, no_resize=True, no_close=True, no_collapse=True) as WinPltM1:
        windows['Sensores'].append(WinPltM1)
        with dpg.plot(tag = 51_1, label="Sensor do Motor 1 (Giro)", width=700, height=200, anti_aliased=True ) :
            dpg.add_plot_legend()
            with dpg.plot_axis( dpg.mvXAxis, label="Tempo (h)", tag = 51_20 ):
                dpg.set_axis_limits( 51_20, ymin = 0, ymax = 1000 )
            with dpg.plot_axis( dpg.mvYAxis, label="Graus (º)", tag = 51_30 ):
                dpg.set_axis_limits( 51_30, ymin = -5, ymax = 370 )         
                dpg.add_line_series( [ ], [ ] , label = "Posição Motor Giro"   , tag = 51_40 , parent = 51_30 )
                dpg.add_line_series( [ ], [ ] , label = "Posição Sol - Azimute", tag = 51_50 , parent = 51_30 )

    with dpg.window( tag = 52_0,  no_title_bar=True, no_move=True, no_resize=True, no_close=True, no_collapse=True) as WinPltM2:
        windows['Sensores'].append(WinPltM2)
        with dpg.plot( tag = 52_1, label="Sensor do Motor 2 (Elevação)", width=700, height=200, anti_aliased=True) :
            dpg.add_plot_legend()
            with dpg.plot_axis( dpg.mvXAxis, label="Tempo (h)", tag = 52_20 ):
                dpg.set_axis_limits( 52_20, ymin = 0, ymax = 1000 )
            with dpg.plot_axis( dpg.mvYAxis, label="Graus (º)", tag = 52_30 ):
                dpg.set_axis_limits( 52_30, ymin = -5, ymax = 370 )         
                dpg.add_line_series([ ], [ ], label = "Posição Motor Elevação", tag = 52_40 , parent = 52_30 )
                dpg.add_line_series([ ], [ ], label = "Posição Sol - Zenite"  , tag = 52_50 , parent = 52_30 )
                
    with dpg.window(id=5_3_0, no_title_bar=True, no_move=True, no_resize=True, no_close=True, no_collapse=True) as WinPltMx:
        windows['Sensores'].append(WinPltMx)
        dpg.add_text('Log dos sensores (Rasp)')
        dpg.add_text( tag = 53_1, default_value = 'DESCONECTADO!' )

    with dpg.window(id=5_4_0, no_close=True, no_move=True, no_resize=True, no_title_bar=True, no_collapse=True ) as Comandos: 
        windows['Sensores'].append(Comandos)
        with dpg.group( horizontal = True ):    
            dpg.add_text('Diagnósticos:')   
            dpg.add_button( label = 'Solicitar diagnósticos', tag = 5_4_1, callback = serial_request_diagnosis ) 
        dpg.add_text( '', tag = 5_4_2 )
        
        row_names = ["\tGir", '\tPV', "\tError", '\tConf', "\tD", "\tI", "\tP", "\tEle", '\tPV', "\tError", '\tConf', "\tD", "\tI", "\tP" ]
        with dpg.table( tag = 54_3_0, header_row = True, label = 'Diagnosis uC Pico'):
            dpg.add_table_column( label = '\tVariável')
            dpg.add_table_column( label = '\tDiagnostico' )
            dpg.add_table_column( label = '\tMedição' )
            for n, row in enumerate( row_names ):
                with dpg.table_row():
                    # Collum 1 
                    with dpg.table_cell():
                        dpg.add_input_text( tag = 54_3_90 + n, default_value = row, width = -1, enabled = False, track_offset = 0.5  )
                    # Collum 2 
                    with dpg.table_cell():
                        dpg.add_drag_float( tag = 54_3_00 + n, default_value = random.randint(0,1000), width = -1, no_input = True  ) 
                    # Collum 3
                    with dpg.table_cell():
                        dpg.add_drag_float( tag = 54_3_50 + n, default_value = random.randint(0,1000), width = -1, no_input = True  ) 
            
    dpg.set_value( 54353, 0  )
    dpg.set_value( 54354, 0  )
    dpg.set_value( 54355, 0  )
    dpg.set_value( 54356, 0  )
    dpg.set_value( 54360, 0  )
    dpg.set_value( 54361, 0  )
    dpg.set_value( 54362, 0  )
    dpg.set_value( 54363, 0  )

def diagnosis_atualize_window():
    dpg.set_value( 54350, dpg.get_value(MPG) )
    dpg.set_value( 54351, dpg.get_value(AZIMUTE) )
    dpg.set_value( 54352, abs(dpg.get_value(MPG)-dpg.get_value(AZIMUTE)) )
    dpg.set_value( 54357, dpg.get_value(MPE) )
    dpg.set_value( 54358, dpg.get_value(ZENITE) )
    dpg.set_value( 54359, abs(dpg.get_value(MPE)-dpg.get_value(ZENITE)) )

def render_sensores() : 
    
    serial_capture_frames() 
    serial_atualize_actuator_cmd()                
    diagnosis_atualize_window() 


# REDNODE 
class Socket_NodeRed:

    MAX_MESSAGE_LENGTH = 1024   

    def __init__(self, sock : socket = None, name : str = '', timeout : int = 1 ) -> int:
        self.timeout   = timeout
        self.connected = False 
        self.name      = name 
        if sock is None:
            try:
                socket.setdefaulttimeout(timeout)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as e:
                print( e )
                self.sock = -1 
        else:
            self.sock = sock
    
    def is_alive(self) -> bool:
        return self.connected 

    def connect(self, host : str, port : int ) -> int:
        try:    
            self.sock.connect((host, port))
            self.connected = True 
        except socket.error as e : 
            print( "Socket {} connection timeout. Verify connection".format(self.__str__()) )
            self.connected = False 
            
    def send(self, msg : Union[str, bytes]):
        if type(msg) == str: msg = msg.encode() 
        if self.connected: 
            totalsent = 0
            while totalsent < len(msg):
                sent = self.sock.send( msg[totalsent:] )
                if sent == 0:
                    print( "socket connection broken" )
                    self.connected = False
                totalsent = totalsent + sent
        else: 
            print('Socket disconnected') 

    def receive(self):
        if self.connected:
            try:    
                rec = self.sock.recv( self.MAX_MESSAGE_LENGTH ) 
            except socket.error as e : 
                print('Error ', e )
                rec = -1 
            return rec.decode()
        else: 
            print('Socket disconnected' ) 

    def __str__(self) -> str:
        print( self.name )
    
    def close(self): 
        self.sock.close() 

MAX_REC_MENSAGE_TCP = 30 
count_TCP_rec = 0 

TemperaturaTCP : socket = 0 
AltitudeTCP : socket = 0 
AzimuteTCP : socket = 0 
HoraTCP : socket = 0 
CMD_log = [ ]

def att_CMD_redNode(): 
    global CMD_log, count_TCP_rec
    if len(CMD_log) > MAX_REC_MENSAGE_TCP: CMD_log.pop(0)
    if dpg.get_value( TCP_CONNECTED ) == True:    
        aux = ''
        for i in CMD_log:
            aux += i 
        dpg.configure_item( 63_1, default_value = aux )
    else: 
        dpg.configure_item( 63_1, default_value = 'DESCONECTADO' )
        count_TCP_rec = 0 

def init_TCP_connection( sender, data, user ): 
    IP   = "{}.{}.{}.{}".format( dpg.get_value( 6_2_1 )[0], dpg.get_value( 6_2_1 )[1], dpg.get_value( 6_2_1 )[2], dpg.get_value( 6_2_1 )[3])
    global TemperaturaTCP, AltitudeTCP, AzimuteTCP, HoraTCP 
    PORT = int( dpg.get_value( 62_2 ) ) 
    some = [] 
    AzimuteTCP     = Socket_NodeRed( name = 'Azimute'    )
    AltitudeTCP    = Socket_NodeRed( name = 'Altitude'   ) 
    TemperaturaTCP = Socket_NodeRed( name = 'Temperatura')  
    HoraTCP        = Socket_NodeRed( name = 'Hora')  
    if dpg.get_value(62_5) == True :
        if not AzimuteTCP.is_alive():
            AzimuteTCP.connect( IP, PORT )
        some.append(1)
    else: 
        some.append(0)
    if dpg.get_value(62_6) == True :
        if not AltitudeTCP.is_alive():
            AltitudeTCP.connect( IP, PORT+1 )
        some.append(1)
    else: 
        some.append(0)

    if dpg.get_value(62_7) == True :
        if not TemperaturaTCP.is_alive(): 
            TemperaturaTCP.connect( IP, PORT+2 )
        some.append(1)
    else: 
        some.append(0)
    
    if dpg.get_value(62_8) == True :
        if not HoraTCP.is_alive(): 
            HoraTCP.connect( IP, PORT+3 )
        some.append(1)
    else: 
        some.append(0)

    if any(some): dpg.set_value( TCP_CONNECTED, True )
    else:         dpg.set_value( TCP_CONNECTED, False )

def refresh_TCP_connection( sender, data, user ): 
    global CMD_log, count_TCP_rec
    if dpg.get_value( TCP_CONNECTED) == True: 
        aux = '[{}] Recv at: {}'.format( count_TCP_rec, dt.datetime.now().strftime('%d/%m/%Y - %H:%M:%S') ) + '\n'
        global TemperaturaTCP, AzimuteTCP, AltitudeTCP, HoraTCP
        if HoraTCP.is_alive():
            HoraTCP.send( dt.datetime.now().strftime('%d/%m/%Y - %I:%M:%S %p')  ) 
            aux += 'Hora: ' + str(HoraTCP.receive()) + '\n'
        if TemperaturaTCP.is_alive():
            TemperaturaTCP.send( str( dpg.get_frame_count() ))
            aux += 'Counter: ' + str(TemperaturaTCP.receive()) + '\n'
        if AzimuteTCP.is_alive():
            AzimuteTCP.send( str(  '%.2f'%math.degrees(dpg.get_value(AZIMUTE)) ) ) 
            aux += 'Azimute: ' + str(AzimuteTCP.receive()) + '\n'
        if AltitudeTCP.is_alive():
            AltitudeTCP.send( str( '%.2f'%math.degrees(dpg.get_value(ZENITE)) ) ) 
            aux += 'Altitude: ' + str(AltitudeTCP.receive()) + '\n'
        CMD_log.append( aux + '\n' )
        count_TCP_rec += 1 
        att_CMD_redNode() 

def att_TCP_connection(sender, data, user ) : 
    if dpg.get_value( TCP_CONNECTED) == True: 
        init_TCP_connection(sender, data, user ) 
        
def close_TCP_connection( sender, data, user ): 
    global TemperaturaTCP, AzimuteTCP, AltitudeTCP
    if TemperaturaTCP.is_alive():
        TemperaturaTCP.close( )
    if AzimuteTCP.is_alive():
        AzimuteTCP.close()
    if AltitudeTCP.is_alive():
        AltitudeTCP.close()
    if HoraTCP.is_alive():
        HoraTCP.close()
    dpg.set_value( TCP_CONNECTED, False )


## CONFIGURAÇÕES 
def resize_rednodecom( ) -> bool :
    nw, nh = dpg.get_item_width('mainWindow'), dpg.get_item_height( 'mainWindow') 
    dpg.configure_item( 61_10  , width = nw*0.99   , height = nh*0.3       )
    #dpg.configure_item( 61_12  , width = nw*0.99   , height = nh*0.28      )  
    #dpg.configure_item( 61_12  , pmin  = (-30,-30) , pmax = ( nw, nh*0.28 ))
    
    dpg.configure_item( 62_10   , width = nw*0.35    , height = nh*0.7-30    , pos = [10        , nh*0.31+20] )   
    
    dpg.configure_item( 63_10   , width = nw*0.65-20 , height = nh*0.7-30    , pos = [nw*0.35+15, nh*0.31+20] )

def init_rednodecom( windows : dict ):
    # NODE RED HEADER 
    with dpg.window( tag = 61_10, width = -1, height = -1, pos = [10,25]     , no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True ) as winRed: 
        windows['Rednode comunicacao'].append( winRed )
        header = add_image_loaded( PATH + "\\utils\\img\\nodeRed.PNG" )
        dpg.add_drawlist( tag = 61_11, width  = 100  , height = 100  )
        dpg.draw_image  ( tag = 61_12, parent = 61_11, texture_tag = header, pmin = (0,0), pmax = (1,1) )

    # CONFIGURAÇÔES
    with dpg.window( tag = 62_10, width = -1, height = -1, pos = [10, 0], no_resize = True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True   ) as winConfig: 
        windows['Rednode comunicacao'].append( winConfig )

        dpg.add_text      ( 'Configurações de conexão com o NODE RED:')
        with dpg.group( horizontal = True ):
            dpg.add_text      ( 'IP:\t' )
            dpg.add_drag_intx ( tag = 62_1, min_value = 0, max_value = 255   , size = 4, default_value = [127,0,0,1] )
        
        with dpg.group( horizontal = True ):
            dpg.add_text      ( 'Port:  ')
            dpg.add_input_int ( tag = 62_2,  min_value = 0, max_value = 2**16, default_value = 1205  )
    
        dpg.add_spacer    ( height = 5 ) 
        dpg.add_text      ('Tipo de conexão: ') 
        dpg.add_combo     ( tag = 62_3, default_value = 'TCP', items = ['TCP', 'UDP'] )
        dpg.add_text      ('Intervalo de transmissão: ')
        dpg.add_input_int ( tag = 62_4, default_value = 10, label='(seg)' )
        dpg.add_spacer( height = 3 )
        
        with dpg.group( horizontal = True ): 
            dpg.add_checkbox( tag = 62_5, label = 'Azimute'    , default_value = True, callback = att_TCP_connection )
            dpg.add_checkbox( tag = 62_6, label = 'Altitude'   , default_value = True, callback = att_TCP_connection )
            dpg.add_checkbox( tag = 62_7, label = 'Temperatura', default_value = True, callback = att_TCP_connection ) 
            dpg.add_checkbox( tag = 62_8, label = 'Hora'       , default_value = True, callback = att_TCP_connection ) 
        
        dpg.add_spacer( height = 3 ) 
        with dpg.group( horizontal = True ):
            dpg.add_button    ( tag = 62_9, label = 'Try to connect', callback = init_TCP_connection  )
            dpg.add_button    ( tag = 62_10, label = 'Desconnected', callback = close_TCP_connection   )
            dpg.add_button    ( tag = 62_11, label = 'Refresh', callback = refresh_TCP_connection   )
    
        dpg.bind_item_theme( 62_9, theme_button_on)
        dpg.bind_item_theme( 62_10, theme_button_off )

    # LOG
    with dpg.window ( tag = 63_10, width = -1 , height = -1, no_resize=True, no_move = True, no_collapse = True, no_close = True, no_title_bar = True   ) as winRedLog: 
        windows [ 'Rednode comunicacao'].append( winRedLog )
        dpg.add_text( tag = 63_2, default_value = "Log das mensagens comunicadas:")
        dpg.add_text( tag = 63_1, default_value = 'Desconectado', tracked = True, track_offset = 1 )

def render_rednodecom() :
    resize_rednodecom() 

# CALLBACKS 
def theme_color( sender, data, user ):
    with dpg.theme( default_theme=True) as theme_set_color:
        with dpg.theme_component( dpg.mvAll): 
            dpg.add_theme_color( user[0], [data[0]*255, data[1]*255, data[2]*255, data[3]*255], category = user[1])
    #dpg.bind_theme( theme_set_color )
    print( 'Não implementado Themes color ainda' ) 

def theme_style( sender, data, user ):  
    with dpg.theme() as theme_set_style:
        with dpg.theme_component( dpg.mvAll ):
            if type(data) == int or type(data) == bool : 
                dpg.add_theme_style( user[0], data, category = dpg.mvThemeCat_Core)
            elif type(data) == list:
                dpg.add_theme_style( user[0], x = data[0], y = data[1], category = dpg.mvThemeCat_Core)
            else:
                print( data, user, len(data), type(data)) 
    print( 'Não implementado Themes style ainda' ) 
    ##dpg.bind_theme( theme_set_style )

# MAIN FUNCTIONS 
def init_configuracoes( windows : dict ): 
    with dpg.window( label = 'Configurações_Estilo'  , tag = 9_1_0, pos = [50,50], width = 500, height = 500, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as style_CONFG:
        windows['Configuracoes'].append( style_CONFG )
        dpg.add_text( 'Configurações de janela' )
        dpg.add_checkbox     ( label = 'WindowBorderSize'   , tag = 101_99_1 ,callback = theme_style, user_data = [dpg.mvStyleVar_WindowBorderSize], default_value = True                                                  )
        dpg.add_slider_int   ( label = 'WindowMinSize   '   , tag = 101_99_2 ,callback = theme_style, user_data = [dpg.mvStyleVar_WindowMinSize]   , default_value = 0        , min_value = 0 , max_value = 1400           )
        dpg.add_slider_intx  ( label = 'WindowPadding'      , tag = 101_99_3 ,callback = theme_style, user_data = [dpg.mvStyleVar_WindowPadding]   , default_value = [5,5]    , size = 2, min_value = 0 , max_value = 25   )
        dpg.add_slider_floatx( label = 'WindowTitleAlign'   , tag = 101_99_4 ,callback = theme_style, user_data = [dpg.mvStyleVar_WindowTitleAlign], default_value = [0.5,0.5], size = 2, min_value = 0 , max_value = 2    )
        dpg.add_slider_floatx( label = 'WindowRouding'      , tag = 101_99_5 ,callback = theme_style, user_data = [dpg.mvStyleVar_WindowRounding]  , default_value = [1,1]    , size = 2, min_value = 0 , max_value = 1    )
        dpg.add_spacer() 
        dpg.add_text( 'Configurações de Childs')
        dpg.add_checkbox     ( label = 'ChildBorderSize'    , tag = 101_99_6 ,callback = theme_style, user_data = [dpg.mvStyleVar_ChildBorderSize], default_value = True)        
        dpg.add_slider_int   ( label = 'ChildRounding'      , tag = 101_99_7 ,callback = theme_style, user_data = [dpg.mvStyleVar_ChildRounding]  , default_value = 5 , min_value = 0  , max_value = 10   )    
        dpg.add_spacer() 
        dpg.add_text( 'Configurações de PopUp')
        dpg.add_checkbox     ( label = 'PopupBorderSize'    , tag = 101_99_8 ,callback = theme_style, user_data = [dpg.mvStyleVar_PopupBorderSize], default_value = False )        
        dpg.add_slider_int   ( label = 'PopupRounding'      , tag = 101_99_9 ,callback = theme_style, user_data = [dpg.mvStyleVar_PopupRounding], default_value = 5 , min_value = 0  , max_value = 10    )    
        dpg.add_spacer() 
        dpg.add_text( 'Configurações de Frames')
        dpg.add_checkbox     ( label = 'FrameBorderSize'    , tag = 101_99_10 ,callback = theme_style, user_data = [dpg.mvStyleVar_FrameBorderSize], default_value = False )        
        dpg.add_slider_floatx( label = 'FramePadding'       , tag = 101_99_11 ,callback = theme_style, user_data = [dpg.mvStyleVar_FramePadding], default_value = [5,4], size = 2, min_value=0, max_value = 10 )    
        dpg.add_slider_float ( label = 'FrameRounding'      , tag = 101_99_12 ,callback = theme_style, user_data = [dpg.mvStyleVar_FrameRounding], default_value = 5    , min_value = 0, max_value = 10   )   
        dpg.add_spacer() 
        dpg.add_text( 'Configurações de Itens')
        dpg.add_slider_intx  ( label = 'ItemSpacing'        , tag = 101_99_13 ,callback = theme_style, user_data = [dpg.mvStyleVar_ItemSpacing], default_value = [10,4], size = 2,  min_value = 5, max_value = 25 )    
        dpg.add_slider_intx  ( label = 'ItemInnerSpacing'   , tag = 101_99_14 ,callback = theme_style, user_data = [dpg.mvStyleVar_ItemInnerSpacing], default_value = [5,5] , size = 2,  min_value = 0, max_value = 10 )        
        dpg.add_spacer() 
        dpg.add_text( 'Configurações de Scroll')
        dpg.add_slider_int   ( label = 'ScrollbarSize'      , tag = 101_99_15 ,callback = theme_style, user_data = [dpg.mvStyleVar_ScrollbarSize], default_value = 15 , min_value = 0, max_value = 20 )    
        dpg.add_slider_int   ( label = 'ScrollbarRounding'  , tag = 101_99_16 ,callback = theme_style, user_data = [dpg.mvStyleVar_ScrollbarRounding], default_value = 2  , min_value = 0, max_value = 20 )        
        dpg.add_spacer() 
        dpg.add_text( 'Outras configurações')
        dpg.add_slider_intx  ( label = 'CellPadding'        , tag = 101_99_17 ,callback = theme_style, user_data=[dpg.mvStyleVar_CellPadding]       , default_value = [5,5]     , size = 2, min_value = 0, max_value = 20 )    
        dpg.add_slider_int   ( label = 'IndentSpacing'      , tag = 101_99_18 ,callback = theme_style, user_data=[dpg.mvStyleVar_IndentSpacing]     , default_value = 5                                                   )    
        dpg.add_slider_int   ( label = 'GrabMinSize'        , tag = 101_99_19 ,callback = theme_style, user_data=[dpg.mvStyleVar_GrabMinSize]       , default_value = 20                                                  )    
        dpg.add_slider_int   ( label = 'GrabRounding'       , tag = 101_99_20 ,callback = theme_style, user_data=[dpg.mvStyleVar_GrabRounding]      , default_value = 3                   , min_value = 0, max_value = 10 )    
        dpg.add_slider_floatx( label = 'ButtonAling'        , tag = 101_99_21 ,callback = theme_style, user_data=[dpg.mvStyleVar_ButtonTextAlign]   , default_value = [0.5, 0.5], size = 2, min_value = 0, max_value = 1  )    
        dpg.add_slider_floatx( label = 'SelectableTextAlign', tag = 101_99_22 ,callback = theme_style, user_data=[dpg.mvStyleVar_SelectableTextAlign], default_value = [0.5, 0.5], size = 2, min_value = 0, max_value = 1  )

    with dpg.window( label = 'Configurações_Colors'  , tag = 9_2_0, pos = [50,50], width = 700, height = 500, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as colors_CONFG:
        windows['Configuracoes'].append( colors_CONFG )
        dpg.add_color_edit( label = 'mvThemeCol_Text                 ', tag = 100_99_1 , default_value = (1.00 * 255, 1.00 * 255, 1.00 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_Text,                 dpg.mvThemeCat_Core] ) 
        dpg.add_color_edit( label = 'mvThemeCol_TextDisabled         ', tag = 100_99_2 , default_value = (0.50 * 255, 0.50 * 255, 0.50 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TextDisabled,         dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_WindowBg             ', tag = 100_99_3 , default_value = (0.06 * 255, 0.06 * 255, 0.06 * 255, 0.94 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_WindowBg,             dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ChildBg              ', tag = 100_99_4 , default_value = (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ChildBg,              dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_PopupBg              ', tag = 100_99_5 , default_value = (0.08 * 255, 0.08 * 255, 0.08 * 255, 0.94 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_PopupBg,              dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_Border               ', tag = 100_99_6 , default_value = (0.43 * 255, 0.43 * 255, 0.50 * 255, 0.50 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_Border,               dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_BorderShadow         ', tag = 100_99_7 , default_value = (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_BorderShadow,         dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_FrameBg              ', tag = 100_99_8 , default_value = (0.16 * 255, 0.29 * 255, 0.48 * 255, 0.54 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_FrameBg,              dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_FrameBgHovered       ', tag = 100_99_9 , default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.40 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_FrameBgHovered,       dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_FrameBgActive        ', tag = 100_99_10, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.67 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_FrameBgActive,        dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TitleBg              ', tag = 100_99_11, default_value = (0.04 * 255, 0.04 * 255, 0.04 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TitleBg,              dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TitleBgActive        ', tag = 100_99_12, default_value = (0.16 * 255, 0.29 * 255, 0.48 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TitleBgActive,        dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TitleBgCollapsed     ', tag = 100_99_13, default_value = (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.51 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TitleBgCollapsed,     dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_MenuBarBg            ', tag = 100_99_14, default_value = (0.14 * 255, 0.14 * 255, 0.14 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_MenuBarBg,            dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ScrollbarBg          ', tag = 100_99_15, default_value = (0.02 * 255, 0.02 * 255, 0.02 * 255, 0.53 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ScrollbarBg,          dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ScrollbarGrab        ', tag = 100_99_16, default_value = (0.31 * 255, 0.31 * 255, 0.31 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ScrollbarGrab,        dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ScrollbarGrabHovered ', tag = 100_99_17, default_value = (0.41 * 255, 0.41 * 255, 0.41 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ScrollbarGrabHovered, dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ScrollbarGrabActive  ', tag = 100_99_18, default_value = (0.51 * 255, 0.51 * 255, 0.51 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ScrollbarGrabActive,  dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_CheckMark            ', tag = 100_99_19, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_CheckMark,            dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_SliderGrab           ', tag = 100_99_20, default_value = (0.24 * 255, 0.52 * 255, 0.88 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_SliderGrab,           dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_SliderGrabActive     ', tag = 100_99_21, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_SliderGrabActive,     dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_Button               ', tag = 100_99_22, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.40 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_Button,               dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ButtonHovered        ', tag = 100_99_23, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ButtonHovered,        dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ButtonActive         ', tag = 100_99_24, default_value = (0.06 * 255, 0.53 * 255, 0.98 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ButtonActive,         dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_Header               ', tag = 100_99_25, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.31 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_Header,               dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_HeaderHovered        ', tag = 100_99_26, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.80 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_HeaderHovered,        dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_HeaderActive         ', tag = 100_99_27, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_HeaderActive,         dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_Separator            ', tag = 100_99_28, default_value = (0.43 * 255, 0.43 * 255, 0.50 * 255, 0.50 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_Separator,            dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_SeparatorHovered     ', tag = 100_99_29, default_value = (0.10 * 255, 0.40 * 255, 0.75 * 255, 0.78 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_SeparatorHovered,     dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_SeparatorActive      ', tag = 100_99_30, default_value = (0.10 * 255, 0.40 * 255, 0.75 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_SeparatorActive,      dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ResizeGrip           ', tag = 100_99_31, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.20 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ResizeGrip,           dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ResizeGripHovered    ', tag = 100_99_32, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.67 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ResizeGripHovered,    dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ResizeGripActive     ', tag = 100_99_33, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.95 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ResizeGripActive,     dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_Tab                  ', tag = 100_99_34, default_value = (0.18 * 255, 0.35 * 255, 0.58 * 255, 0.86 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_Tab,                  dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TabHovered           ', tag = 100_99_35, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.80 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TabHovered,           dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TabActive            ', tag = 100_99_36, default_value = (0.20 * 255, 0.41 * 255, 0.68 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TabActive,            dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TabUnfocused         ', tag = 100_99_37, default_value = (0.07 * 255, 0.10 * 255, 0.15 * 255, 0.97 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TabUnfocused,         dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TabUnfocusedActive   ', tag = 100_99_38, default_value = (0.14 * 255, 0.26 * 255, 0.42 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TabUnfocusedActive,   dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_DockingPreview       ', tag = 100_99_39, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.70 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_DockingPreview,       dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_DockingEmptyBg       ', tag = 100_99_40, default_value = (0.20 * 255, 0.20 * 255, 0.20 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_DockingEmptyBg,       dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_PlotLines            ', tag = 100_99_41, default_value = (0.61 * 255, 0.61 * 255, 0.61 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_PlotLines,            dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_PlotLinesHovered     ', tag = 100_99_42, default_value = (1.00 * 255, 0.43 * 255, 0.35 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_PlotLinesHovered,     dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_PlotHistogram        ', tag = 100_99_43, default_value = (0.90 * 255, 0.70 * 255, 0.00 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_PlotHistogram,        dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_PlotHistogramHovered ', tag = 100_99_44, default_value = (1.00 * 255, 0.60 * 255, 0.00 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_PlotHistogramHovered, dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TableHeaderBg        ', tag = 100_99_45, default_value = (0.19 * 255, 0.19 * 255, 0.20 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TableHeaderBg,        dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TableBorderStrong    ', tag = 100_99_46, default_value = (0.31 * 255, 0.31 * 255, 0.35 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TableBorderStrong,    dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TableBorderLight     ', tag = 100_99_47, default_value = (0.23 * 255, 0.23 * 255, 0.25 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TableBorderLight,     dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TableRowBg           ', tag = 100_99_48, default_value = (0.00 * 255, 0.00 * 255, 0.00 * 255, 0.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TableRowBg,           dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TableRowBgAlt        ', tag = 100_99_49, default_value = (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.06 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TableRowBgAlt,        dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_TextSelectedBg       ', tag = 100_99_50, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 0.35 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_TextSelectedBg,       dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_DragDropTarget       ', tag = 100_99_51, default_value = (1.00 * 255, 1.00 * 255, 0.00 * 255, 0.90 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_DragDropTarget,       dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_NavHighlight         ', tag = 100_99_52, default_value = (0.26 * 255, 0.59 * 255, 0.98 * 255, 1.00 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_NavHighlight,         dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_NavWindowingHighlight', tag = 100_99_53, default_value = (1.00 * 255, 1.00 * 255, 1.00 * 255, 0.70 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_NavWindowingHighlight,dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_NavWindowingDimBg    ', tag = 100_99_54, default_value = (0.80 * 255, 0.80 * 255, 0.80 * 255, 0.20 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_NavWindowingDimBg,    dpg.mvThemeCat_Core]  )
        dpg.add_color_edit( label = 'mvThemeCol_ModalWindowDimBg     ', tag = 100_99_55, default_value = (0.80 * 255, 0.80 * 255, 0.80 * 255, 0.35 * 255), callback = theme_color, user_data=[dpg.mvThemeCol_ModalWindowDimBg,     dpg.mvThemeCat_Core]  )
    
    with dpg.window( label = 'Configurações_Diversos', tag = 9_3_0, pos = [50,50], width = 300, height = 500, no_move = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as others_CONFG:
        windows['Configuracoes'].append( others_CONFG ) 
        w, h = dpg.get_item_width(9_3_0), dpg.get_item_height(9_3_0)
        dpg.add_text( 'Área de visualização das configurações', bullet = True ) 
        dpg.add_button(       label = 'Isto é um botão '        , width = w*0.9 , height = 50 )
        with dpg.group( horizontal = True ):
            dpg.add_button(       label = 'E isso é um botão '      , width = w*0.44, height = 50 )
            dpg.add_button(       label= 'lado a lado '             , width = w*0.44, height = 50 )
        dpg.add_color_button( label = 'Isto é um botão colorido', width = w*0.9 , height = 50 , default_value = (55,102, 231,200) )
        dpg.add_spacer()
        dpg.add_radio_button( label = 'Radio button', items=['Isto', 'é', 'um', 'Radio', 'button'], horizontal = True )
        dpg.add_spacer()
        with dpg.group( horizontal = True ):
            dpg.add_checkbox(     label = 'CheckBox 1')
            dpg.add_checkbox(     label = 'CheckBox 2')
            dpg.add_checkbox(     label = 'CheckBox 3')
        dpg.add_spacer() 
        with dpg.child_window( width = w*0.9, height = 100, label = 'Isto é um Child', border = True  ):
            dpg.add_text( 'Isto é uma Child')
            dpg.add_drawlist(  tag = 9_3_1, label = 'Isto é um Draw_list' , width = 200     , height = 400  )
            dpg.draw_text( parent = 9_3_1, text  = 'Isto é um Draw_List' , pos   = [10,0]  , size   = 15   )
            dpg.draw_text( parent = 9_3_1, text  = 'Super longo'         , pos   = [10,20] , size   = 15   )
            dpg.draw_text( parent = 9_3_1, text  = 'Viu só'              , pos   = [10,380], size   = 15   )
        
        dpg.add_text('Clique aqui para abrir um ... ', tag = 9_3_2 )
        with dpg.popup( parent = 9_3_2, mousebutton = dpg.mvMouseButton_Left):
            dpg.add_text( 'POPUP')
            dpg.add_button( label = 'Popup Com Botão também')
        
        dpg.add_spacer() 
        dpg.add_text( 'Um exemplo de color picker', bullet = True  ) 
        dpg.add_color_picker() 

def resize_configuracoes():
    w, h = dpg.get_item_width( 'mainWindow' ), dpg.get_item_height( 'mainWindow' ) 
    dpg.configure_item( 91_0, pos = [ 10            , 25 ], width = (w*(1/3))//1, height = (h*0.965)//1 ) 
    dpg.configure_item( 92_0, pos = [ w*(1/3)   + 10, 25 ], width = (w*(7/15)-5 )//1, height = (h*0.965)//1 ) 
    dpg.configure_item( 93_0, pos = [ w*(12/15) + 5 , 25 ], width = (w*(3/15)-10)//1, height = (h*0.965)//1 ) 

def render_configuracao():
    pass 


# CALLBACKs
def change_menu(sender, app_data, user_data ):
    global window_opened 
    window_opened = user_data 
    # CLOSE ALL WINDOWS 
    for k in windows.keys():
        for i in windows[k]:
            dpg.hide_item(i)
    # OPEN THE RIGHT TAB WINDOW 
    to_open = windows[user_data]
    for i in to_open:
        dpg.show_item(i)
    resize_main()

def closing_dpg( sender, data, user ): 
    with dpg.window( pos = [ dpg.get_item_width('mainWindow')/2.5, dpg.get_item_height('mainWindow')/2.5]): 
        dpg.add_text( 'Obrigado por usar nosso programa\nEle irá encerrar em instantes' )
    sleep(2)
    dpg.stop_dearpygui() 

# MAIN FUNTIONS 
def resize_main( ):
    global window_opened
    if   window_opened == 'Inicio'             : resize_inicio()
    elif window_opened == 'Visualizacao geral' : resize_visualizacaoGeral()
    elif window_opened == 'Posicao do sol'     : lambda : print('resize_posicaoDoSol     (  )')
    elif window_opened == 'Atuadores'          : resize_atuador()     
    elif window_opened == 'Sensores'           : resize_sensores() 
    elif window_opened == 'Rednode comunicacao': resize_rednodecom() 
    elif window_opened == 'Configuracoes'      : resize_configuracoes() 

def render_main( ):
    global window_opened
    if   window_opened == 'Inicio'             : render_inicio()
    elif window_opened == 'Visualizacao geral' : render_visualizacaoGeral()
    elif window_opened == 'Posicao do sol'     : lambda : print('resize_posicaoDoSol     (  )')
    elif window_opened == 'Atuadores'          : render_atuador()     
    elif window_opened == 'Sensores'           : render_sensores()  
    elif window_opened == 'Rednode comunicacao': render_rednodecom()
    elif window_opened == 'Configuracoes'      : render_configuracao() 

def init_main( ): 
    # MAIN WINDOW 
    with dpg.window( tag = 'mainWindow', autosize = True, no_close = True, no_move = True, no_resize = True ): 
        with dpg.menu_bar(label = "MenuBar"):
            dpg.add_menu_item( label = "Inicio"             , callback = change_menu, user_data = "Inicio"              )
            dpg.add_menu_item( label = "Visualização geral" , callback = change_menu, user_data = "Visualizacao geral"  )
            dpg.add_menu_item( label = "Atuadores"          , callback = change_menu, user_data = "Atuadores"           )
            dpg.add_menu_item( label = "Sensores"           , callback = change_menu, user_data = "Sensores"            )
            dpg.add_menu_item( label = "RedNode Comunicacao", callback = change_menu, user_data = "Rednode comunicacao" )
            dpg.add_menu_item( label = "Configurações"      , callback = change_menu, user_data = "Configuracoes"       )
            dpg.add_menu_item( label = 'Sair'               , callback = closing_dpg                                    )

# INICIALIZAÇÔES
init_main             (         ) 
init_rednodecom       ( windows )
init_inicio           ( windows, change_menu )
init_atuador          ( windows ) 
init_visualizacaoGeral( windows )
init_sensores         ( windows )
init_configuracoes    ( windows )

# CONFIGURATIONS 
dpg.set_primary_window          ( 'mainWindow', True          )
dpg.set_viewport_large_icon     ( PATH + 'utils\\ico\\large_ico.ico' )
dpg.set_viewport_small_icon     ( PATH + 'utils\\ico\\small_ico.ico' )
dpg.set_viewport_resize_callback( resize_main                 )
dpg.maximize_viewport           (                             ) 

# SETA A JANELA INICIAL 
change_menu  ( None, None, 'Inicio' )

# START OF DPG VIEW 
dpg.show_viewport( )

while dpg.is_dearpygui_running(): 
    dpg.render_dearpygui_frame() 
    render_main() 
    
    # COM 60FPS TEM-SE 0.01667s PARA DAR 1 FRAME
    # A CADA 60 FRAME SE PASSAM 1 SEGUNDO 
    if dpg.get_frame_count() % 60 == 0: 
        if not dpg.get_value( HORA_MANUAL ): 
            SUN_DATA.set_date( dt.datetime.utcnow() )
            dpg.set_value( ZENITE , math.degrees(SUN_DATA.alt) ) 
            dpg.set_value( AZIMUTE, math.degrees(SUN_DATA.azi) )
            dpg.set_value( YEAR   , SUN_DATA.year   )
            dpg.set_value( MONTH  , SUN_DATA.month  )
            dpg.set_value( DAY    , SUN_DATA.day    )
            dpg.set_value( HOUR   , SUN_DATA.hour   )
            dpg.set_value( MINUTE , SUN_DATA.minute )
            dpg.set_value( SECOND , SUN_DATA.second )
            dpg.set_value( TOT_SECONDS, SUN_DATA.total_seconds )
            dpg.set_value( JULIANSDAY , SUN_DATA.dia_juliano )

        if dpg.get_frame_count() % 600 == 0: 
            if serial_comp_is_open():
                if dpg.get_value( WRONG_DATETIME ):
                    serial_write_message( None, None, 'INITHA')
                    print( 'mudamos a hora ')
                
        # PARA DAR 3.600 FRAMES TEM-SE 1 MINUTO  
        if dpg.get_frame_count() % 3_6000 == 0:
            if serial_comp_is_open():
                serial_write_message( None, None, 'INITCP')
                serial_request_diagnosis( None, None, None)
# CLOSE DPG 
dpg.destroy_context() 



