import machine
import time

# INTERFACE
class Registers:
    
    ''' STACK é a fila de registradores. Utiliza uma lista para ordenação dos registradores'''
    STACK = []
    
    ''' ADDR é responsável por guardar o tamanho da lista STACK''' 
    ADDRS  = 0
    
    
    ''' CONSTRUTOR DO OBJETO REGISTRADOR 
        O construtor é responsável pela definição do tipo de registrador e da
          quantidade de registradores ::
            >>> reg_type : [int, float, bool] => Tipos de registradores
            >>> reg_len : int => Quantidade de registradores. Podem ser adicionados
                a medida do necessário. 
        >>> No return.
    '''
    def __init__(self, reg_type : [int, float, bool], reg_len : int ):
        self.TYPE  = reg_type
        self.STACK = [ self.TYPE( 0 ) for _ in range( reg_len ) ]
        self.ADDRS = reg_len
        self.DEBUG = False 
    
    
    ''' RESPONSÁVEL POR DEFINIR UM REGISTRADOR ESPECÍFICO COM UM VALOR ESPECÍFICO 
        Seta um endereço da lista com um valor específico. Faz a validação se o 
        endereço é válido::
            >>> addr : int => Endereço de escrita;
            >>> reg : [int, float, bool] => Valor para ser escrito no endereço.
                Esse valore deve ser do mesmo tipo dos valores da lista. 
        Return:: 
            >>> True : bool => Se o valor estiver de acordo retorna um booleano True;
            >>> False : bool => Se o valor estiver em desacordo ou o endereço for
                inválido, retorna um booleano False. 
    '''
    def set_reg(self, addr : int , reg  ) :
        if addr > len(self.STACK):
            if self.DEBUG: print('Set_reg error: ADDR > LEN( STACK ) ')
            return False
        
        elif type(reg) is not self.TYPE :
            if self.DEBUG: print('Set_reg error: DATA TYPE != STACK TYPE')
            return False
        
        else:
            self.STACK[ addr ] = reg
            if self.DEBUG: print('Set_reg[{}] = {}'.format( addr, reg ))
            return True 
    
    ''' ESPECIALIZAÇÃO DO MÉTODO set_reg PARA VÁRIOS REGISTRADORES 
        Escreve em vários registradores de uma única vez::
            >>> addr : int => Endereço inicial de escrita;
            >>> regs : list => Lista de registradores. Deve conter o mesmo
            tipo de dados que a os dados da lista STACK. 
        O tamanho da lista definira o número de registradores para ser escrito
        na lista STACK.
        
        Return::
            >>> len(regs) : int => Número de registradores escritos se os endereços
                forem escritos com sucesso.
            >>> False : bool => Retorna o Booleano False caso dê algum erro de escrita
                nos registradores. Pode ser erro de estouro de registradores ou por 
                tipo de dado de escrita errado. 
    '''
    def set_regs(self, addr : int, regs : list ) -> bool :
        if (addr + len(regs)) > len(self.STACK):
            if self.DEBUG: print('Set_regs error: ADDR > LEN( STACK )')
            return False
        elif type(regs[0]) is not self.TYPE:
            if self.DEBUG: print('Set_regs error: DATA TYPE != STACK TYPE')
            return False
        else:
            for n in range( len(regs)):
                status = self.set_reg( addr + n, regs[n] )
                if status == False:
                    if self.DEBUG: print('Set_regs error: Erro no self.set_reg')
                    return False
            if self.DEBUG: print('Set_regs Success')
            return len(regs) 


    ''' RESPONSÁVEL POR ADICIONAR UM REGISTRADOR À LISTA DE REGISTRADORES  
        Adiciona um novo registrador com um endereço específico caso necessário::
            >>> addr : int = -1 => Endereço do novo registrador adicionado.
        Return:: 
            >>> self.ADDRS : int => Novo valor de registradores cadastrados se a
                operação foi bem sucedida;
            >>> False : bool => Se o valor do endereço passado for inválido,
                retorna um booleano False. 
    '''
    def add_reg(self, addr : int = -1 ) -> int :
        if addr == -1 :
            self.STACK.append( self.TYPE(0) )
            self.ADDRS = len(self.STACK)
            if self.DEBUG: print('Add_reg: ADDR DEFAULT {-1}\nAdicionado 1 registrador no endereço ', self.ADDRS )
        else:
            if addr <= len(self.STACK):
                self.STACK.insert( addr, self.TYPE(0) )
                if self.DEBUG: print('Add_reg: ADDR {}\nAdicionado 1 registrador no endereço {}'.format( addr, addr ) )
            else:
                if self.DEBUG: print('Add_reg error: ADDR INVÁLIDO')
                return False
        return self.ADDRS
    
    ''' ESPECIALIZAÇÃO DA FUNÇÃO self.add_reg  
        Adiciona um conjunto de novos registradores com um endereço específico caso necessário::
            >>> addr : int = -1 => Endereço do novo registrador adicionado;
            >>> num : int = 1 => Número de registradores para adicionar.
        Return:: 
            >>> True : bool => Se a operação foi bem sucedida, retorna True;
            >>> False : bool => Se o valor do endereço passado ou o número de registradores
                for inválido, retorna um booleano False. 
    '''
    def add_regs(self, addr : int = -1 , num : int = 1 ) -> bool:
        if num <= 0:   return False
        if addr == -1:
            for _ in range( num ):
                self.add_reg()
        elif addr <= len(self.STACK):
             for _ in range( num ):
                 self.add_reg( addr )
        else:
            return False
        return True 
        
        
    def remove_reg(self, addr : int ):
        if addr <= len(self.STACK):
            pop = self.STACK.pop( addr )
            self.ADDRS = len(self.STACK) 
        else:
            return False
        return pop 
    
    
    def remove_regs(self, addr : int, num : int ) -> list:
        pops = [] 
        if addr + num <= len(self.STACK):
            for _ in range(num):
                pops.append( self.remove_reg(addr) ) 
            return True 
        else:
            return pops
        
        
    def get_reg(self, addr : int ) :
        if addr <= len(self.STACK):
            return self.STACK[addr] 
    
    
    def get_regs(self, addr : int, num : int ) -> list :
        if addr + num <= len(self.STACK):
            return self.STACK[addr:addr+num] 
    
    
    ''' VERIFICA SE NÃO HÁ ESTOURO DE MEMÓRIA
        Faz a verificação se a posição ADDR + quantidade de registradores não excede
        o limite de registradores cadastrados
            INPUTS::
                >>> addr : int => Número da posição de memória inicial
                >>> num_regs : int => Quantidade de registradores para leitura/escrita
            RETURN::
                >>> True : boolean => Retornar o boolean True se não houver estouro de registradores
                >>> False : boolean => Retorna o boolean False se houve estouro de memória
        Como a memória para manipulação ocupa um espaço, é necessário usar a equação::
            >>> LEN( STACK ) > ADDR - 1 + NUM_REGS
        Como os valores de indexação de registradores e número de registradores deve ser maior que zero
        deve-se fazer a verificação
            >>> NUM_REGS < 0 ? False : True
            >>> ADDR < 0 ? False : True
        Se o número de registradores for 0 (zero) sempre retornará True
            >>> NUM_REGS == 0 ? True : continue 
    '''
    def check_offset(self, addr : int, num_regs : int ):
        if num_regs == 0:                             return True
        elif num_regs < 0 or addr < 0:                return False
        elif (addr + num_regs ) > len(self.STACK):    return False
        else:                                         return True 
    
    
# ---------------------------------------- #
# To call the main function 
def mainRegisters():
    
    a = Registers( bool, 10)
    a.DEBUG = True 
    print( a.set_regs( 5, [True, False, True] ) )
    print( a.add_regs( 5, 5 ) )
    print( a.remove_regs(0, 5) ) 
    print( a.get_regs( 0, 10 )  )
    print( a.STACK )
    
if __name__ == '__main__' :
    mainRegisters()
# ---------------------------------------- #