from dearpygui.dearpygui    import *
from .menuVisualizacaoGeral import sun_data, AZI_Angle, ALT_Angle
from numpy                  import array

import math 
import os 

PATH      = os.path.dirname( __file__ ).removesuffix('\\views')
PATH_IMG  = PATH + '\\img\\fundo.jpg'

def add_image_loaded( img_path : str ):
    w, h, c, d = load_image( img_path )
    with texture_registry() as reg_id : 
        return add_static_texture( w, h, d, parent = reg_id )

sun_data.update()
sunrise   = math.degrees(sun_data.azimute_sunrise   )
culminant = math.degrees(sun_data.elevation_transit )

# FUNÇÕES        
def draw_semi_circle( parent : Union[str, int], id : Union[str, int], center : list, radius : float, angle_i : float , angle_f : float, color : list, segments : int = 360, closed : bool = False, thickness : int = 1 ):
        angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
        points = [ [ center[0] + radius*math.cos(ang), center[1] - radius*math.sin(ang) ] for ang in angles ]
        draw_id = draw_polyline ( parent = parent, id = id, points = points, color= color, closed = closed, thickness= thickness )

def circle_angles( angle_initial : float , angle_final : float , points_number : int, convert_to_radians : bool = True ):
    if convert_to_radians: 
        angle_initial = math.radians(angle_initial)
        angle_final = math.radians(angle_final)
    dif_dom = (angle_final-angle_initial)/points_number
    dom = [ angle_initial+(i*dif_dom) for i in range(points_number)]
    points = [ [math.cos(angle), math.sin(angle)] for angle in dom ]
    return points

def rotate_x( angles_to_convert : list , angle_to_rotate : float, convert_to_3D : bool = False, convert_to_radians : bool = False ): 
    if convert_to_radians:  angle_to_rotate = math.radians( angle_to_rotate )
    ROT_X = array([ [ 1,                         0,                          0 ],
                    [ 0, math.cos(angle_to_rotate), -math.sin(angle_to_rotate) ],
                    [ 0, math.sin(angle_to_rotate),  math.cos(angle_to_rotate) ]])
    if convert_to_3D:
        angles_to_convert = array([ [x,y,0] for x, y in angles_to_convert ])
        angles_converted = [ angles.dot(ROT_X) for angles in angles_to_convert ]
        angles_converted = [ [x,y] for x, y, _ in angles_converted ]
        return angles_converted 
    else:
        angles_to_convert = array( angles_to_convert ) 
        angles_converted = [ angles.dot(ROT_X) for angles in angles_to_convert ]
        return angles_converted 

def rotate_y( angles_to_convert : list, angle_to_rotate : float, convert_to_3D : bool = False, convert_to_radians : bool = False ): 
    if convert_to_radians:  angle_to_rotate = math.radians( angle_to_rotate )
    ROT_Y = array([ [ math.cos(angle_to_rotate), 0, -math.sin(angle_to_rotate) ],
                    [ 0,                         1,                          0 ],
                    [ math.sin(angle_to_rotate), 0, math.cos(angle_to_rotate) ]])
                    
    if convert_to_3D:
        angles_to_convert = array([ [x,y,0] for x, y in angles_to_convert ])
        angles_converted = [ angles.dot(ROT_Y) for angles in angles_to_convert ]
        angles_converted = [ [x,y] for x, y, _ in angles_converted ]
        return angles_converted
    else:
        angles_to_convert = array( angles_to_convert ) 
        angles_converted = [ angles.dot(ROT_Y) for angles in angles_to_convert ]
        return angles_converted 

def ellipse_points( rmax : float, rmin : float, z_axis : bool = False  ): 
    c_angles = circle_angles( 0, 360, 360, convert_to_radians=True ) 
    if z_axis: 
        c_rotated = rotate_x( c_angles, (math.pi/2-2*math.atan(rmin/rmax )), False )
        return c_rotated 
    else: 
        c_rotated = rotate_x( c_angles, (math.pi/2-2*math.atan(rmin/rmax )), True )
        return c_rotated 

def draw_solar_sphere( parent : Union[int, str], id : Union[int, str], center : list, rmax : float, rmin : float ): 
    e_points_naked   = ellipse_points( rmax = rmax, rmin = rmin)
    c_points_naked   = circle_angles( 180, 360, 180, convert_to_radians = True)
    e_points_ajusted = [ [center[0]+e_x*rmax, center[1]+e_y*rmax] for e_x, e_y in e_points_naked ]
    c_points_ajusted = [ [center[0]+c_x*rmax, center[1]+c_y*rmax] for c_x, c_y in c_points_naked ]
    draw_polyline( parent= parent, id = id, points= e_points_ajusted, closed=True )
    draw_polyline( parent= parent, id = id, points= c_points_ajusted, closed=False )
    
def draw_ecliptica( parent : Union[int, str], id : Union[int, str], center : list , angle_sunrise : float, angle_culminant : float , radius : Union[float, int], draw_sun : bool = False      ):
    sunrise    = angle_sunrise
    sunset     = abs(sunrise)+180
    culminant  = angle_culminant

    c_angles = circle_angles( sunset, sunrise, 100, convert_to_radians=True ) 
    c_rotated = rotate_x( c_angles, culminant, True, True )
    c_rotated = rotate_y( c_rotated, sunrise, True, True )

    c_points_ajusted = [[center[0]+c_x*radius, center[1]+c_y*radius] for c_x, c_y in c_rotated  ]
    draw_polyline( parent = parent, id = id, points = c_points_ajusted, closed=False)

def init_posicaoDoSol( windows : dict ):
    with window( label = 'Posição do Sol', id = 3_1_0, no_move  = True, no_resize = True, no_collapse = True, no_close = True, no_title_bar= True ) as Posicao_sol_PS:
        windows["Posicao do sol"].append( Posicao_sol_PS )
        w, h = get_item_width( Posicao_sol_PS ), get_item_height( Posicao_sol_PS)

        add_drawlist( id = 3_1_1_0, width = w*0.9, height = h*0.9, pos = [w*0.025, h*0.025] )
        center = [w*0.35,h*0.75] 
        radius = 500 
        draw_solar_sphere( 3_1_1_0, 3_1_1_1, center, radius, radius/5 )
        draw_ecliptica( 3_1_1_0, 3_1_1_2, center, 178, 42, radius  )

        add_slider_floatx( max_value=360, size=2, min_value=0, default_value=[178,42], indent=0.001, callback=configure_draw_ecliptica )
        
def configure_draw_ecliptica(sender, data, user): 
    delete_item(3112)
    w0, h0 = get_item_width( 1_0 ), get_item_height( 1_0 ) 
    rmax, rmin = w0*0.34, h0*0.12 
    center = [w0*0.35,h0*0.75 - rmin] 
    radius = rmax
    draw_ecliptica( 3_1_1_0, 3_1_1_2, center, data[0], data[1], radius  )

def resize_posicaoDoSol():
    w0, h0 = get_item_width( 1_0 ), get_item_height( 1_0 ) 
    configure_item( 3_1_0  , width = w0-15, height = h0 -35   , pos = [ 10, 25] )
    configure_item( 3_1_1_0, width = w0*0.9, height = h0*0.9, pos = [w0*0.025, h0*0.025] )

    rmax, rmin = w0*0.34, h0*0.12 
    center = [w0*0.35,h0*0.75 - rmin] 
    radius = rmax 
    delete_item( 3_1_1_1 )
    draw_solar_sphere( 3_1_1_0, 3_1_1_1, center , rmax, rmin )
    
    global AZI_Angle
    global ALT_Angle
    global sun_data
    
    sun_data.update() 

    AZI_Angle = math.degrees( sun_data.azi )  
    ALT_Angle = math.degrees( sun_data.alt ) 

    delete_item( 3_1_1_2)
    draw_ecliptica( 3_1_1_0, 3_1_1_2, center, AZI_Angle, ALT_Angle, radius, draw_sun = True   )
    
def render_posicaoDoSol():
    global AZI_Angle
    global ALT_Angle
