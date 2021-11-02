# FILE CONFIGURATIONS 
FILE_PATH   = 'mem_pico.txt'
FILE_RW     = 'rw' 
FILE_READ   = 'r'
FILE_WRITE  = 'wo'
FILE_APPEND = 'a'

def file_write( file_path, data, where = 0, OP = 'w'  ):
    with open( file_path, OP ) as file:
        file.seek(where, 0)
        file.write( data )

def file_readlines( file_path, OP = 'r'  ):
    with open( file_path, OP ) as file: 
        lines = file.readlines()
    return lines

def file_size( file_path, OP = 'r'  ) :
    with open( file_path, OP ) as file:
        return file.tell() 

