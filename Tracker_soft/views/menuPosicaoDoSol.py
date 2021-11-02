from dearpygui.dearpygui import *
from utils.Model         import SunPosition

import datetime as dt 
import ephem
import math 
import sys 
import os 

cos     = lambda x : math.cos( x )
sin     = lambda x : math.sin( x )
tg      = lambda x : math.tan( x )

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

MG_Angle  = 30.0
ME_Angle  = 40.0  

AZI_Angle = 0.0 
ALT_Angle = 0.0 

LATITUDE  = '-29.16530765942215'
LONGITUDE = '-54.89831672609559'
ALTITUDE  = 425
UTC_HOUR  = -3

sun_data  = SunPosition( LATITUDE, LONGITUDE, ALTITUDE )
sun_data.update_date()


# FUNÇÕES
def get_semi_circle_points( center, radius, angle_i, angle_f, segments = 360, closed = False ):
    points_close = [ center ] 
    angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
    points =  [ [ center[0] + radius*cos(ang), center[1] - radius*sin(ang) ] for ang in angles ] 
    if closed: 
        points_close.extend( points )
        return points_close 
    else:      
        return points 


def init_posicaoDoSol( windows : dict ):
    with window( label = 'Painel de log' , id = 3_1_0, no_move  = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar = True ) as log_PS:
        windows["Posição do Sol"].append( 3_1_0 )
        w, h = get_item_width(3_1_0), get_item_height(3_1_0)
        add_text( 'Log da posição do sol')

    with window( label = 'Posição do Sol', id = 3_2_0, no_move  = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as Posicao_sol_PS:
        windows["Posição do Sol"].append( 3_2_0 )
        w, h = get_item_width(3_2_0), get_item_height(3_2_0)

        center = [ w//2, h//2 ]
        add_drawlist(  id     = 3_2_1_0, width = w*1.95, height = h*1.95, pos = [5,5] )
        draw_polyline( parent = 3_2_1_0, id = 3_2_1_1  , points = get_semi_circle_points( center = [center[0], center[1]*1.75 ], radius = h*4/3, angle_i = 1, angle_f = 180, segments = 180, closed = True  ), color = (255,255,255,255) )
        draw_arrow( parent= 3210, p1 = [ 10, 10], p2 = [50,55] )

def resize_posicaoDoSol():
    w0, h0 = get_item_width( 1_0 ), get_item_height( 1_0 ) 
    configure_item( 3_1_0, width = w0-15, height = h0*0.25   , pos = [ 10, 25] )
    configure_item( 3_2_0, width = w0-15, height = h0*0.75-35, pos = [ 10, h0*0.25 + 30] )

def render_posicaoDoSol():
    global MG_Angle 
    global ME_Angle 
    global AZI_Angle
    global ALT_Angle
