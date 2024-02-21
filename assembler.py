# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:49:03 2023

@author: ccslon
"""

import re
from bit16 import Reg, Op, Cond, Data, Char, Jump, LoadB, Inst2, Inst2c, Inst3, Inst3c, Load, Loadc, LoadW, ESCAPE

TOKENS = {
    'const': r'-?\d+|x[0-9a-f]+|b[01]+',
    'string': r'"[^"]*"',
    'char': r"'\\?[^']'",
    'ldm': r'\b(ldm)\b',
    'ld': r'\b(ld)\b',
    'nop': r'\b(nop)\b',
    'op': r'\b('+r'|'.join(op.name for op in Op)+r')\b',
    'cond': r'\b('+'|'.join(cond.name for cond in Cond)+r')\b',
    'push': r'\b(push)\b',
    'pop': r'\b(pop)\b',
    'call': r'\b(call)\b',
    'ret': r'\b(ret)\b',
    'halt': r'\b(halt)\b',
    'space': r'\b(space)\b',
    'reg': r'\b('+r'|'.join(reg.name for reg in Reg)+r')\b',
    'label': r'\.?[a-z_]\w*',
    'equal': r'=',
    'colon': r':',
    'dash': r'-',
    'lbrace': r'\[',
    'rbrace': r'\]',
    'lbrack': r'\{',
    'rbrack': r'\}',
    'comma': r',',
    'end': r'$',
    'error': r'\S+'
}

RE = re.compile('|'.join(rf'(?P<{token}>{pattern})' for token, pattern in TOKENS.items()), re.I)

def lex(text):
    return [(match.lastgroup , match.group()) for match in RE.finditer(text)]

class Assembler:
    def label(self, label):
        self.labels.append(label)
    def const(self, label, value):
        self.label(label)
        self.new_data(value)
    def char(self, label, char):
        self.label(label)
        char = ESCAPE.get(char, char)
        self.new_char(char)
    def string(self, label, string):
        self.label(label)
        for escape in ESCAPE:
            string = string.replace(escape, ESCAPE[escape])
        for char in string:
            self.new_char(char)
    def space(self, label, size):
        self.label(label)
        for _ in range(size):
            self.new_data(0)
    def jump(self, cond, label):
        self.new_inst(Jump, cond, label)
    def load(self, rd, rb, ro):
        self.new_inst(Load, False, rd, rb, ro)
    def loadc(self, rd, rb, offset5):
        self.new_inst(Loadc, False, rd, rb, offset5)
    def store(self, rb, rd):
        self.new_inst(Loadc, True, rd, rb, 0)
    def store0(self, rb, ro, rd):
        self.new_inst(Load, True, rd, rb, ro)
    def store1(self, rb, offset5, rd):
        self.new_inst(Loadc, True, rd, rb, offset5)
    def word(self, rd, value):
        self.new_inst(LoadW, rd)
        self.new_word(value)
    def byte(self, rd, byte):
        self.new_inst(LoadB, byte, rd)
    def unary(self, op, rd):
        self.new_inst(Inst2, op, rd, rd)
    def inst2(self, op, rd, rs):
        self.new_inst(Inst2, op, rd, rs)
    def inst2c(self, op, rd, const6):
        self.new_inst(Inst2c, op, rd, const6)
    def inst3(self, op, rd, rs, rs2):
        self.new_inst(Inst3, op, rd, rs, rs2)
    def inst3c(self, op, rd, rs, const4):
        self.new_inst(Inst3c, op, rd, rs, const4)
    def new_inst(self, inst, *args):
        self.inst.append((self.labels, inst, args))
        self.labels = []
    def new_word(self, value):
        self.inst.append((self.labels, Data, (value,)))
        self.labels = []
    def new_data(self, value):
        self.data.append((self.labels, Data, (value,)))
        self.labels = []
    def new_char(self, char):
        self.data.append((self.labels, Char, (char,)))
        self.labels = []
    def new_string(self, string): #TODO
        for char in string:
            self.new_char(char)
    def name(self, name, value):
        self.names[name] = value
        
    def assemble(self, asm):        
        self.inst = []
        self.data = []
        self.labels = []
        self.names = {}
        for self.line_no, line in enumerate(map(str.strip, asm.strip().split('\n')), 1):
            if ';' in line:
                line, comment = map(str.strip, line.split(';', 1))
            if line:
                self.tokens = lex(line)
                self.index = 0                
                if self.match('label'):
                    self.new_data(*self.values())
                elif self.match('label', '=', 'const'):
                    self.name(*self.values())
                elif self.peek('label'):
                    print(f'{self.line_no: >2}|{line}')
                    if self.match('label', ':'):
                        self.label(*self.values())
                    elif self.match('label', ':', 'const'):
                        self.const(*self.values())
                    elif self.match('label', ':', 'char'):
                        self.char(*self.values())
                    elif self.match('label', ':', 'string'):
                        self.string(*self.values())
                    elif self.match('label', ':', 'space', 'const'):
                        self.space(*self.values())
                    else:
                        self.error()
                else:
                    print(f'{self.line_no: >2}|  {line}')
                    if self.match('const'):
                        self.new_data(*self.values())
                    elif self.match('char'):
                        self.new_char(*self.values())
                    elif self.match('nop'):
                        self.jump(Cond.JNV, 0)
                    elif self.match('cond', 'label'):
                        self.jump(*self.values())
                    elif self.match('ld', 'reg', ',', '[', 'reg', ',', 'reg', ']'):
                        self.load(*self.values())
                    elif self.match('ld', 'reg', ',', '[', 'reg', ']'):
                        self.loadc(*self.values(), 0)
                    elif self.match('ld', 'reg', ',', '[', 'reg', ',', 'const', ']'):
                        self.loadc(*self.values())
                    elif self.match('ld', '[', 'reg', ',', 'reg', ']', ',', 'reg'):
                        self.store0(*self.values())
                    elif self.match('ld', '[', 'reg', ']', ',', 'reg'):
                        self.store(*self.values())
                    elif self.match('ld', '[', 'reg', ',', 'const', ']', ',', 'reg'):
                        self.store1(*self.values())
                    elif self.match('ld', 'reg', ',', 'const'):
                        self.word(*self.values())
                    elif self.match('ld', 'reg', ',', 'char'):
                        self.byte(*self.values())
                    elif self.match('ld', 'reg', ',', '=', 'label'):
                        self.word(*self.values())
                    elif self.match('op', 'reg'):
                        self.unary(*self.values())
                    elif self.match('op', 'reg', ',', 'reg'):                    
                        self.inst2(*self.values())
                        
                    elif self.match('op', 'reg', ',', 'const'):
                        self.inst2c(*self.values())
                        
                    elif self.match('op', 'reg', ',', 'reg', ',', 'reg'):
                        self.inst3(*self.values())        
                        
                    elif self.match('op', 'reg', ',', 'reg', ',', 'const'):
                        self.inst3c(*self.values())
                        
                    elif self.accept('push'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        self.expect('end')
                        self.inst2c(Op.SUB, Reg.SP, len(args))
                        for i, reg in enumerate(args):
                            self.store1(Reg.SP, len(args)-1-i, reg)
                            
                    elif self.accept('pop'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        self.expect('end')
                        for i, reg in enumerate(reversed(args)):
                            self.loadc(reg, Reg.SP , i)
                        self.inst2c(Op.ADD, Reg.SP, len(args))
                                                     
                    elif self.match('jump', 'label'):
                        self.word(Reg.PC, *self.values())
                        
                    elif self.match('call','reg'):
                        self.inst3c(Op.ADD, Reg.LR, Reg.PC, 2)
                        self.inst2(Op.MOV, Reg.PC, *self.values())
                        
                    elif self.match('call', 'label'):
                        self.inst3c(Op.ADD, Reg.LR, Reg.PC, 3)
                        self.word(Reg.PC, *self.values())
                        
                    elif self.match('ret'):
                        self.inst2(Op.MOV, Reg.PC, Reg.LR)
                        
                    elif self.match('out', 'reg'):
                        pass
                    
                    elif self.accept('ldm'):
                        if self.peek('reg'): #ldm A, {B, C}
                            dest = next(self)
                            self.expect(',')
                            self.expect('{')
                            regs = [self.expect('reg')]
                            while self.accept(','):
                                regs.append(self.expect('reg'))
                            self.expect('}')
                            for i, reg in enumerate(regs):
                                self.store1(dest, i, reg)
                            #store??
                        elif self.accept('{'): #ldm {B, C}, A
                            regs = [self.expect('reg')]
                            while self.accept(','):
                                regs.append(self.expect('reg'))
                            self.expect('}')
                            self.expect(',')
                            dest = self.expect('reg')
                            for i, reg in enumerate(regs):
                                self.loadc(reg, dest, i)                            
                        else:
                            self.error()
                        
                    elif self.match('halt'):
                        self.inst2(Op.MOV, Reg.PC, Reg.PC)
                    else:
                        self.error()                    
        objects = [([], Jump, (Cond.JNV, 0))]
        objects.extend(self.inst)
        objects.extend(self.data)
        return objects
    
    def match(self, *pattern):
        pattern += ('end',)
        return len(self.tokens) == len(pattern) and all(pattern[i] in (type_, value) for i, (type_, value) in enumerate(self.tokens))
    
    def trans(self, type_, value):
        if type_ == 'const':
            if value.startswith('x'):
                return int(value[1:], base=16)
            elif value.startswith('b'):
                return int(value[1:], base=2)
            else:
                return int(value)
        elif type_ in ['string', 'char']:
            return value[1:-1]
        elif type_ == 'reg':
            return Reg[value.upper()]
        elif type_ == 'cond':
            return Cond[value.upper()]
        elif type_ == 'op':
            return Op[value.upper()]
        elif type_ == 'label':
            if value in self.names:
                return self.names[value]
            return value
    
    def values(self):
        for type_, value in self.tokens:
            if type_ in ['const','string','char','reg','cond','op','label']:
                yield self.trans(type_, value)
    
    def __next__(self):
        type_, value = self.tokens[self.index]
        self.index += 1
        if type_ in ['const','string','char','reg','cond','op','label']:
            return self.trans(type_, value)
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
        self.error(expected=symbols)
        
    def error(self):
        etype, evalue = self.tokens[self.index]
        raise SyntaxError(f'Unexpected {etype} token "{evalue}" at token #{self.index} in line {self.line_no}')

class Linker:
    def link(objects):
        targets = {}
        indices = set()
        for i, (labels, type_, args) in enumerate(objects):
            for label in labels:
                targets[label] = i
                indices.add(i)
            objects[i] = (type_, args)
        print('-'*67)
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
            print('>>' if i in indices else '  ', f'{i:04x}', f'{data.str: <15}', f'| {data.dec(): <13}', f'{data.bin(): <22}', data.hex())
        print('\n', ' '.join(contents))
        return contents
    
assembler = Assembler()    

def assemble(program):
    objects = assembler.assemble(program)
    return Linker.link(objects)

asm = '''
begin:
    LD A, 'a'
    MOV B, 6
    ADD A, B
    SUB SP, 1
    LD [SP, 0], A
    LD C, [SP, 0]
    LD D, xFFFF
    JR begin
'''