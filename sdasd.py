from math import * 

def get_semi_circle_points( center, radius, angle_i, angle_f, segments = 360, closed = False ):
    points_close = [[ center[0], center[1]-radius ] ,  center, [ center[0] + radius, center[1] + radius ] ] 
    angles = [ ((angle_f - angle_i)/segments)*n for n in range(segments) ] 
    points =  [ [ center[0] + radius*cos(ang), center[1] - radius*sin(ang) ] for ang in angles ] 
    if closed: 
        points_close.extend( points )
        return points_close 
    else:      
        return points 
        
points = get_semi_circle_points( center = [ 100, 10 + 20], radius = 20, angle_i = 0, angle_f = radians(91), segments= 90, closed = True  ) 
print( points )
