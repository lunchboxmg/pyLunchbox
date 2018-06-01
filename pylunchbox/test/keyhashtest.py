from random import randint

keybinds = {}

class KeyBind(object):
    
    def __init__(self, command, key=0, button=0, mod1=0, mod2=0):
        
        self.command = command
        self.key = key
        self.button = button
        self.mod1 = mod1
        self.mod2 = mod2
        
    def __hash__(self):
        
        return (self.key << 8) | ((self.button + 1) << 4) | (self.mod1 | self.mod2)
    
    def __eq__(self, other):
        
        if self == other: return True
        if not isinstance(other, KeyBind): return False
        if self.command != other.command: return False
        if self.key != other.key: return False
        if self.button != other.button: return False
        if self.mod1 != other.mod1: return False
        if self.mod2 != other.mod2: return False
        return True
    


class InputMgr(object):
    
    def __init__(self):

        self.keybinds = k = {}
        kb = KeyBind("test1", 65, 0, 0x01, 0x04)
        k[kb] = self.test1
        self.kb2 =  KeyBind("test2", 78, 1, 0x02)
        self.kb3 =  KeyBind("test3", 248)
        self.kb4 =  KeyBind("test4", 248)
        

    def process(self, keys):
        
        for key in keys:
        

    def test1(self):
        print "Test 1"
        
    def test2(self):
        print "Test 2"

    def test3(self):
        print "Test 3"

test_mgr = InputMgr()


