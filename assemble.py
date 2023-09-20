# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:49:03 2023

@author: ccslon
"""

from re import compile as re_compile, I
from bit16 import Reg, Op, Cond, Nop, Inst1, Inst2, Inst3, Inst4, Inst5, Load0, Load1, Jump

TOKENS = {'dec': r'-?\d+',
          'hex': r'x[0-9a-f]+',
          'bin': r'b[01]+',
          'ld': r'ld',
          'nop': r'nop',
          'op': '|'.join(op.name for op in Op),
          'cond': '|'.join(cond.name for cond in Cond),
          'push': r'push',
          'pop': r'pop',
          'call': r'call',
          'ret': r'ret',
          'halt': r'halt',
          'reg': r'|'.join(map(r'\b{}\b'.format, (reg.name for reg in Reg))),
          'label': r'\.?[a-z](\w|\d)*',
          'colon': r':',
          'lbrace': r'\[',
          'rbrace': r'\]',
          'comma': r',',
          'error': r'\S+'}

def lex(text):
    regexp = re_compile('|'.join(rf'(?P<{token}>{pattern})' for token, pattern in TOKENS.items()), I)
    return [(match.lastgroup, match.group()) for match in regexp.finditer(text)] + [('end', '')]

class ASMParser:
    def new_inst(self, op, args):
        self.objects.append((self.labels, op, args))
        self.labels = []    
    def parse(self, program):        
        self.objects = []
        self.labels = []
        for line in map(str.strip, program.strip().split('\n')):
            if ';' in line:
                line, comment = map(str.strip, line.split(';', 1))
            if line:
                self.tokens = lex(line)
                #for i_, (t, v) in enumerate(self.tokens): print(i_, t, v)
                self.index = 0
                if self.peek('label'):
                    print(line)
                    self.labels.append(next(self))
                    self.expect(':')
                else:
                    print(f'  {line}')
                    if self.accept('nop'):
                        self.new_inst(Nop, ())
                    elif self.peek('cond'):
                        self.new_inst(Jump, (next(self), self.expect('label')))
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
                        self.new_inst(inst, (storing, rd, rb, o))
                    elif self.peek('op'):
                        op = next(self)
                        rd = self.expect('reg')
                        if self.accept(','):                
                            if self.peek('reg'):
                                rs = next(self)
                                if self.accept(','):
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
                            inst, args = Inst5, (op, rd) #Inst5
                        self.new_inst(inst, args)
                    elif self.accept('push'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        for reg in args:
                            self.new_inst(Inst2, (Op.SUB, Reg.SP, 1))
                            self.new_inst(Load1, (True, reg, Reg.SP, 0))
                    elif self.accept('pop'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        for reg in reversed(args):
                            self.new_inst(Inst2, (Op.ADD, Reg.SP, 1))
                            self.new_inst(Load1, (False, reg, Reg.SP, -1))
                    elif self.accept('call'):
                        self.new_inst(Inst1, (Op.MOV, Reg.LR, Reg.PC ))
                        self.new_inst(Inst2, (Op.ADD, Reg.LR, 3))
                        self.new_inst(Jump, (Cond.JMP, self.expect('label')))
                    elif self.accept('ret'):
                        self.new_inst(Inst1, (Op.MOV, Reg.PC, Reg.LR))
                    elif self.accept('halt'):
                        self.new_inst(Inst1, (Op.MOV, Reg.PC, Reg.PC))
                    else:
                        self.error()
                self.expect('end')
        return self.objects            
                
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
    def assemble(self, program):
        rom = ASMParser().parse(program)
        targets = {}
        indices = set()
        for i, (labels, inst, args) in enumerate(rom):
            for label in labels:
                targets[label] = i
                indices.add(i)
            rom[i] = (inst, args)
        print('-'*65)
        contents = []
        for i, (inst, args) in enumerate(rom):
            if inst is Jump:
                cond, target = args
                target = targets[target]
                args = cond, target
            inst = inst(*args)
            contents.append(inst.hex())
            print('>>' if i in indices else '  ', f'{i:03x}', f'{inst.str: <15}', f'| {inst.dec(): <12}', f'{inst.bin(): <22}', inst.hex())
        print('\n', ' '.join(contents))
        return contents