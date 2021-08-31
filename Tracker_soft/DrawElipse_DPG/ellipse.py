from dearpygui.dearpygui import * 
from numpy import linspace 
from math import * 

screen_dimension = [ 880, 720 ]

with window( label = 'Main window', id = 1_0, no_resize = True ) as main_window : 
   pass 

def draw_semi_circle( parent, id, center, radius, angle_i, angle_f, color, segments = 360, closed = False, thickness = 1 ):
        angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
        points = [ [ center[0] + radius*cos(ang), center[1] - radius*sin(ang) ] for ang in angles ]
        draw_id = draw_polyline ( parent = parent, id = id, points = points, color= color, closed = closed, thickness= thickness )

with window( id = 2_0, width= 500, height= 500, pos = [0,0]):
    w, h = get_item_width(2_0)*0.9, get_item_height(2_0)*0.9
    add_drawlist( id     = 21, width  = w*0.95 , height = h*0.95 , pos  = [100,100] )
    draw_ellipse( parent = 21, id     = 22     , pmin=[w/3,h-50] , pmax = [w*2/3,h-100], color = (255,255,255,255), thickness= 2               )



setup_viewport ( )
set_viewport_title ( title = 'Ellipse' )
set_viewport_pos ( [75, 0] )
maximize_viewport() 

set_primary_window ( main_window, True )


while is_dearpygui_running():
    render_dearpygui_frame() 

    w, h = get_item_width( 1_0 )*0.9, get_item_height( 1_0 )*0.9   
    configure_item( 20 , width = w          , height =  h )
    configure_item( 21 , width = w*0.95     , height =  h*0.95       )
    configure_item( 22 , pmin  = [w/3, h-50], pmax   = [w*2/3,h-100], color = (w%255, (h*w)%255, h%255, 255) )
