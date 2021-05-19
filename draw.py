from pil import Image 
import numpy as np 
 

def get_image_dimensions(px):
    string = ''
    x = 0
    y = 0
    for j in range(100000):
        try:
            string = str( px[ 0, j ] )
        except:
            y = j 
            break

    for i in range(100000):
        try:
            string = str( px[i, 0])
        except:
            x = i 
            break
    return [x,y] 


string = ''

with Image.open('clock.png') as img :
    px = img.load()
   
    x,y = get_image_dimensions( px )

    print( img.read(920) )