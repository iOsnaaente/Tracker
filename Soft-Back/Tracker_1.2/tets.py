

from distutils.log import error
import struct as s

try: 
    s.unpack( 'f', 123 )

except: 
    print( 'Deu o erro: ' )

