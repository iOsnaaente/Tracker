from collections import defaultdict 

values = defaultdict( None )

def read_arq( name : str = 'CONFIG.txt'): 
    values = defaultdict( None )
    with open( name, 'r') as f:
        lines = f.readlines()
        for line in lines: 
            val = line.replace('\n','').replace(' ','').split('=') 
            if len(val) > 1 : 
                values[val[0]] = val[1]
    return values 

def write_arq(dic : dict, name : str = 'CONFIG.txt'):
    with open( name , 'w') as f: 
        for key in dic.keys():
            if key == 'POS_M1_GIR':
                dic[key] = str( int(dic[key]) + 1) 
            txt = key + '=' + dic[key] + '\n' 
            f.write( txt )

values = read_arq( 'CONFIG.txt' ) 
write_arq( values, 'CONFIG.txt' )

