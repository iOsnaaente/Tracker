def serial_in():
   while sys.stdin in select.select( [sys.stdin], [], [], 0 )[0]:        
        cmd = sys.stdin.read(1)
        if (cmd == 'h'): 
            get_time = struct.unpack( 'BBBBBB', sys.stdin.read(6) )
            DS.set_time( get_time[0], get_time[1], get_time[2], 1, get_time[3], get_time[4], get_time[5] )
            if debug:
                TIME = DS.now() 
                sys.stdout.write( 'Input = h : Correção da Hora' )
                sys.stdout.write( 'Nova data/hora = %i/%i/%i - %i:%i:%i ' %(TIME[0],TIME[1],TIME[2],TIME[3],TIME[4],TIME[5]) ) 
        
