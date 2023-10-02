# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:49:03 2023

@author: ccslon
"""

from re import compile as re_compile, I
from bit16 import Reg, Op, Cond, Data, Char, Jump, Inst1, Inst2, Inst3, Inst4, Load0, Load1, Imm

TOKENS = {'dec': r'-?\d+',
          'hex': r'x[0-9a-f]+',
          'bin': r'b[01]+',
          'string': r'"[^"]*"',
          'char': r"'[^']'",
          'ld': r'ld',
          'nop': r'nop',
          'op': '|'.join(map(r'\b{}\b'.format, (op.name for op in Op))),
          'cond': '|'.join(map(r'\b{}\b'.format, (cond.name for cond in Cond))),
          'push': r'push',
          'pop': r'pop',
          'call': r'call',
          'ret': r'ret',
          'halt': r'halt',
          'reg': r'|'.join(map(r'\b{}\b'.format, (reg.name for reg in Reg))),
          'label': r'\.?[a-z](\w|\d)*',
          'equal': r'=',
          'colon': r':',
          'lbrace': r'\[',
          'rbrace': r'\]',
          'comma': r',',
          'error': r'\S+'}

def lex(text):
    regexp = re_compile('|'.join(rf'(?P<{token}>{pattern})' for token, pattern in TOKENS.items()), I)
    return [(match.lastgroup, match.group()) for match in regexp.finditer(text)] + [('end', '')]

class Assembler:
    def new_inst(self, inst, args):
        self.data.append((self.labels, inst, args))
        self.labels = []
    def new_data(self, value):
        self.data.append((self.labels, Data, (value,)))
        self.labels = []
    def new_global(self, value):
        self.data.append((self.labels, Data, (value,)))
        self.globals = []
    def new_global_char(self, value):
        self.globals.append((self.labels, Char, (value,)))
        self.labels = []
    def new_char(self, char):
        self.data.append((self.labels, Char, (char,)))
        self.labels = []
    def assemble(self, asm):        
        self.data = []
        self.globals = []
        self.labels = []
        for line in map(str.strip, asm.strip().split('\n')):
            if ';' in line:
                line, comment = map(str.strip, line.split(';', 1))
            if line:
                self.tokens = lex(line)
                #for i_, (t, v) in enumerate(self.tokens): print(i_, t, v)
                self.index = 0
                if self.peek('label'):
                    print(line)
                    self.labels.append(next(self))
                    if self.peek('dec','hex','bin'):
                        self.new_data(next(self))
                    elif self.peek('string'):
                        for char in next(self)[1:-1]:
                            self.new_global_char(char)
                    elif self.accept(':'):
                        pass
                    else:
                        self.error()
                else:
                    print(f'  {line}')
                    if self.accept('nop'):
                        self.new_inst(Jump, (Cond.JNV, 0))
                    elif self.peek('cond'):
                        self.new_inst(Jump, (next(self), self.expect('label')))
                    elif self.accept('ld'):
                        if self.peek('reg'): #load
                            storing = False
                            rd = next(self)
                            self.expect(',')
                            if self.accept('['):
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
                            elif self.accept('='):
                                self.new_inst(Imm, (rd,))
                                self.new_data(self.expect('label'))
                                self.expect('end')
                                continue
                            elif self.peek('dec','hex','bin'):
                                self.new_inst(Imm, (rd,))
                                self.new_data(next(self))
                                self.expect('end')
                                continue
                            elif self.peek('char'):
                                self.new_inst(Imm, (rd,))
                                self.new_char(next(self))
                                self.expect('end')
                                continue
                            else:
                                self.error()
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
                                    elif self.peek('dec','hex','bin','label'):
                                        inst, args = Inst4, (op, rd, rs, next(self)) #Inst4
                                    else:
                                        self.error()
                                else:
                                    inst, args = Inst1, (op, rd, rs) #Inst1
                            elif self.peek('dec','hex','bin','label'):
                                inst, args = Inst2, (op, rd, next(self)) #Inst2
                            else:
                                self.error()
                        else:
                            inst, args = Inst1, (op, rd, 0) #Unary
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
                        self.new_inst(Jump, (Cond.JR, self.expect('label')))
                    elif self.accept('ret'):
                        self.new_inst(Inst1, (Op.MOV, Reg.PC, Reg.LR))
                    elif self.accept('out'):
                        rd = self.expect('reg')
                        self.new_inst(Inst1, (Op.Mov, rd, 1))
                        self.new_inst(Load1, (True, ))
                    elif self.accept('halt'):
                        self.new_inst(Inst1, (Op.MOV, Reg.PC, Reg.PC))
                    elif self.accept('jump'):
                        self.new_inst(Imm, (Reg.PC,))
                        self.new_data(self.expect('label'))
                    else:
                        self.error()
                self.expect('end')
        objects = []
        objects.extend(self.data)
        objects.extend(self.globals)
        return objects            
                
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

class Linker:
    def link(objects):
        targets = {}
        indices = set()
        for i, (labels, type_, args) in enumerate(objects):
            for label in labels:
                targets[label] = i
                indices.add(i)
            objects[i] = (type_, args)
        print('-'*66)
        contents = []
        for i, (type_, args) in enumerate(objects):
            if args and type_ is not Char:
                *args, last = args
                if type(last) is str:
                    last = targets[last]
                if type_ is Jump:
                    last -= i
                args = *args, last
            data = type_(*args)
            contents.append(data.hex())
            print('>>' if i in indices else '  ', f'{i:03x}', f'{data.str: <15}', f'| {data.dec(): <13}', f'{data.bin(): <22}', data.hex())
        print('\n', ' '.join(contents))
        return contents
    
def assemble(program):
    objects = Assembler().assemble(program)
    Linker.link(objects)