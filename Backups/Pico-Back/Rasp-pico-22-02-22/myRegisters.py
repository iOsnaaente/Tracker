import machine
import time

# INTERFACE
class Registers:
    
    STACK = []
    ADDR  = 0
    
    def __init__(self, reg_type : [int, float, bool], reg_len : int ):
        self.TYPE  = reg_type
        self.STACK = [ self.TYPE( 0 ) for _ in range( reg_len ) ]
        self.ADDRS = reg_len 
    
    def set_reg(self, addr : int , reg : [int, float, bool ] ) -> [int, float, bool] :
        if addr > len(self.STACK) or type(reg) != self.TYPE :
            return False
        else:
            self.STACK[ addr ] = reg
            return reg 
    
    def set_regs(self, addr : int, regs : list ) -> bool :
        if (addr + len(regs)) > len(self.STACK) or type(regs[0]) is not self.TYPE:
            return False
        else:
            for n in range( len(regs)):
                self.set_reg( addr + n, regs[n] )
            return len(regs) 
    
    def add_reg(self, addr : int = -1 ) -> int :
        if addr == -1 : 
            self.STACK.append( self.TYPE(0) )
            self.ADDRS = len(self.STACK) 
        else:
            if addr <= len(self.STACK) :
                self.STACK.insert( addr, self.TYPE(0) )
            else:
                return -1
        return self.ADDRS
    
    def add_regs(self, addr : int = -1 , num : int = 1 ) -> bool:
        if addr == -1:
            for _ in range( num ):
                self.add_reg()
        elif addr <= len(self.STACK):
             for _ in range( num ):
                 self.add_reg( addr )
        else:
            return False
        return True 
                 
        
    def remove_reg(self, addr : int ) -> [int, float, bool]:
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
        
    def get_reg(self, addr : int ) -> [int, float, bool] :
        if addr <= len(self.STACK):
            return self.STACK[addr] 
    
    def get_regs(self, addr : int, num : int ) -> list :
        if addr + num <= len(self.STACK):
            return self.STACK[addr:addr+num] 
    
    
# ---------------------------------------- #
# To call the main function 
def mainRegisters():
    a = Registers( int, 10)
    a.set_regs( 5, [123,1,23,56,6] )
    a.add_regs( 5, 5 )
    a.remove_regs(0, 5)
    print( a.get_regs( 0, 10 )  ) 
    
if __name__ == '__main__' :
    mainRegisters()
# ---------------------------------------- #
