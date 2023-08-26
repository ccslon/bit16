# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:49:03 2023

@author: ccslon
"""

import re
from bit16 import Reg, Op, Cond, Inst1, Inst2, Inst3, Inst4, Inst5, Load0, Load1, Jump

TOKENS = {'dec': r'-?\d+',
          'hex': r'x[0-9a-f]+',
          'bin': r'b[01]+',
          'ld': r'ld',
          'op': '|'.join(op.name for op in Op),
          'cond': '|'.join(cond.name for cond in Cond),
          'psh': r'psh',
          'pop': r'pop',
          'call': r'call',
          'ret': r'ret',
          'reg': r'|'.join(map(r'\b{}\b'.format, (reg.name for reg in Reg))),
          'label': r'\.?[a-z](\w|\d)*',
          'colon': r':',
          'lbrace': r'\[',
          'rbrace': r'\]',
          'comma': r',',
          'error': r'\S+'}

def lex(text):
    regexp = re.compile('|'.join(rf'(?P<{token}>{pattern})' for token, pattern in TOKENS.items()), re.I)
    return [(match.lastgroup, match.group()) for match in regexp.finditer(text)] + [('end', '')]

class Parser:
    def parse(self, program):        
        rom = []
        label = None
        for line in map(str.strip, program.strip().split('\n')):
            if ';' in line:
                line, comment = map(str.strip, line.split(';', 1))
            if line:
                self.tokens = lex(line)
                #for i_, (t, v) in enumerate(self.tokens): print(i_, t, v)
                self.index = 0
                if self.peek('label'):
                    label = next(self)
                    self.expect(':')
                else:
                    if self.peek('cond'):
                        rom.append((label, line[:3], Jump, (next(self), self.expect('label'))))  
                    elif self.accept('ld'):
                        if self.peek('reg'): #load
                            storing = False
                            rd = next(self)
                            self.expect(',')
                            self.expect('[')
                            rb = self.expect('reg')
                            if self.accept(','):
                                if self.peek('reg'):
                                    inst = Load0
                                elif self.peek('dec','hex','bin'):
                                    inst = Load1
                                else:
                                    self.error()
                                o = next(self)
                            else:
                                inst, o  = Load1, 0
                            self.expect(']')
                        elif self.accept('['): #store
                            storing = True
                            rb = self.expect('reg')
                            if self.accept(','):
                                if self.peek('reg'):
                                    inst = Load0
                                elif self.peek('dec','hex','bin'):
                                    inst = Load1
                                else:
                                    self.error()
                                o = next(self)
                            else:
                                inst, o = Load1, 0
                            self.expect(']')
                            self.expect(',')
                            rd = self.expect('reg')
                        else:
                            self.error()
                        rom.append((label, line, inst, (storing, rd, rb, o)))                     
                    elif self.peek('op'):
                        op = next(self)
                        rd = self.expect('reg')
                        if self.accept(','):                
                            if self.peek('reg'):
                                rs = next(self)
                                if self.accept(','):
                                    op >>= 1
                                    if self.peek('reg'):
                                        inst, args = Inst3, (op, rd, rs, next(self)) #Inst3
                                    elif self.peek('dec','hex','bin'):
                                        inst, args = Inst4, (op, rd, rs, next(self)) #Inst4
                                    else:
                                        self.error()
                                else:
                                    inst, args = Inst1, (op, rd, rs) #Inst1
                            elif self.peek('dec','hex','bin'):
                                const = next(self)
                                inst, args = Inst2, (op, rd, const) #Inst2
                            else:
                                self.error()
                        else:
                            op >>= 3
                            inst, args = Inst5, (op, rd) #Inst5
                        rom.append((label, line, inst, args))
                    elif self.accept('psh'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        rom.append((label, line, Inst2, (Op.SUB, Reg.SP, 1)))
                        rom.append((None, '', Load1, (True, args[0], Reg.SP, 0)))
                        for reg in args[1:]:
                            rom.append((None, '', Inst2, (Op.SUB, Reg.SP, 1)))
                            rom.append((None, '', Load1, (True, reg, Reg.SP, 0)))                            
                    elif self.accept('pop'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        rom.append((label, line, Inst2, (Op.SUB, Reg.SP, 1))) 
                        rom.append((None, '', Load1, (False, args[-1], Reg.SP, -1)))
                        for reg in reversed(args[:-1]):
                            rom.append((None, '', Inst2, (Op.ADD, Reg.SP, 1))) 
                            rom.append((None, '', Load1, (False, reg, Reg.SP, -1)))                            
                    elif self.accept('call'):
                        rom.append((label, line, Inst1, (Op.MOV, Reg.LR, Reg.PC )))
                        rom.append((None, '', Inst2, (Op.ADD, Reg.LR, 3)))
                        rom.append((None, 'jmp', Jump, (Cond.JMP, self.expect('label'))))                        
                    elif self.accept('ret'):
                        rom.append((label, line, Inst1, (Op.MOV, Reg.PC, Reg.LR)))                        
                    else:
                        self.error()      
                    label = None
                self.expect('end')
        return rom            
                
    def __next__(self):
        type_, value = self.tokens[self.index]
        self.index += 1
        if type_ == 'dec':
            return int(value)
        elif type_ == 'hex':
            return int(value[1:], base=16)
        elif type_ == 'bin':
            return int(value[1:], base=2)
        elif type_ == 'reg':
            return Reg[value.upper()]
        elif type_ == 'cond':
            return Cond[value.upper()]
        elif type_ == 'op':
            return Op[value.upper()]
        return value
        
    def peek(self, *symbols):
        type_, value = self.tokens[self.index]
        return type_ in symbols or value in symbols
    
    def accept(self, *symbols):
        if self.peek(*symbols):
            return next(self)
    
    def expect(self, *symbols):
        if self.peek(*symbols):
            return next(self)
        self.error()
        
    def error(self, offset=0):
        etype, evalue = self.tokens[self.index-offset]
        raise SyntaxError(f'Unexpected {etype} token "{evalue}" at {self.index}')

class Assembler:
    def __init__(self):
        self.parser = Parser()
        
    def assemble(self, program):
        rom = self.parser.parse(program)
        labels = {}
        indices = {}
        maxl = 8
        for i, (label, orig, inst, args) in enumerate(rom):
            maxl = max(maxl, len(orig))
            if label:
                labels[label] = i
                indices[i] = label
        contents = []
        for i, (label, orig, inst, args) in enumerate(rom):
            if inst is Jump:
                cond, target = args
                target = labels[target]
                orig = f'{orig} x{target:03x}'
                args = cond, target
            inst = inst(*args)
            hex_ = inst.hex()
            contents.append(hex_)
            bin_ = ' '.join(inst.bin)
            print('>>' if i in indices else '  ', f'{i:03x}', f'{orig: <{maxl}}', f'{bin_: <22}', hex_)   
        print('\n', ' '.join(contents))

fact = '''
mov A, 6
call fact
mov B, 0
ld [B], A
halt:
    jmp halt

fact:
    psh lr, B, C
    sub sp, 1
    ld [sp, 0], A
    ld B, [sp, 0]
    cmp B, 0
    jne .L0
    mov B, 0
    jmp .L1
.L0:
    ld B, [sp, 0]
    ld A, [sp, 0]
    sub A, 1
    call fact
    mov C, A
    mul B, C    
.L1:
    mov A, B
    pop pc, B, C
'''

halt = '''
mov B, 5
mov A, B
add A, B
'''
test = '''
; nop
mov A, 5 ; 2
mov B, 3
add A, B ; 1
mov C, A

add D, A, B ; 3
sub E, C, 3 ; 4

neg B ; 5
'''

ldtest = '''
mov A, 10
mov B, 11
mov C, 3
mov D, 1
mov E, 12
ld [C], A
ld [C, D], B
ld [C, 2], E

ld A, [C]
ld B, [C, D]
ld C, [C, 2]
'''

jmptest = '''
mov A, 0
mov B, 5
loop:
    cmp A, B
    jge end
    add A, 1
    jmp loop
end:
    jmp end
'''

if __name__ == '__main__':
    assembler = Assembler()
    assembler.assemble(test)