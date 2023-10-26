# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:49:03 2023

@author: ccslon
"""

import re
from bit16 import Reg, Op, Cond, Data, Char, Jump, Inst1, Inst2, Inst3, Inst4, Load0, Load1, Imm, ESCAPE

TOKENS = {'const': r'(-?\d+)|(x[0-9a-f]+)|(b[01]+)',
          'string': r'"[^"]*"',
          'char': r"'\\?[^']'",
          'ld': r'ld',
          'nop': r'nop',
          'op': '|'.join(map(r'\b{}\b'.format, (op.name for op in Op))),
          'cond': '|'.join(map(r'\b{}\b'.format, (cond.name for cond in Cond))),
          'push': r'push',
          'pop': r'pop',
          'call': r'call',
          'ret': r'ret',
          'halt': r'halt',
          'space': r'space',
          'reg': r'|'.join(map(r'\b{}\b'.format, (reg.name for reg in Reg))),
          'label': r'\.?[a-z](\w|\d)*',
          'equal': r'=',
          'colon': r':',
          'dash': r'-',
          'lbrace': r'\[',
          'rbrace': r'\]',
          'lbrack': r'\{',
          'rbrack': r'\}',
          'comma': r',',
          'end': r'$',
          'error': r'\S+'}

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
    def load0(self, rd, rb, ro):
        self.new_inst(Load0, False, rd, rb, ro)
    def load1(self, rd, rb, offset5):
        self.new_inst(Load1, False, rd, rb, offset5)
    def store(self, rb, rd):
        self.new_inst(Load1, True, rd, rb, 0)
    def store0(self, rb, ro, rd):
        self.new_inst(Load0, True, rd, rb, ro)
    def store1(self, rb, offset5, rd):
        self.new_inst(Load1, True, rd, rb, offset5)
    def imm(self, rd, value):
        self.new_inst(Imm, rd)
        self.new_imm(value)
    def imm_char(self, rd, value):
        self.new_inst(Imm, rd)
        self.new_imm_char(value)
    def inst1(self, op, rd, rs):
        self.new_inst(Inst1, op, rd, rs)
    def inst2(self, op, rd, const6):
        self.new_inst(Inst2, op, rd, const6)
    def inst3(self, op, rd, rs, rs2):
        self.new_inst(Inst3, op, rd, rs, rs2)
    def inst4(self, op, rd, rs, const4):
        self.new_inst(Inst4, op, rd, rs, const4)
    def new_inst(self, inst, *args):
        self.inst.append((self.labels, inst, args))
        self.labels = []
    def new_imm(self, value):
        self.inst.append((self.labels, Data, (value,)))
        self.labels = []
    def new_imm_char(self, value):
        self.inst.append((self.labels, Char, (value,)))
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
        
    def assemble(self, asm):        
        self.inst = []
        self.data = []
        self.labels = []
        for self.line_no, line in enumerate(map(str.strip, asm.strip().split('\n')), 1):
            if ';' in line:
                line, comment = map(str.strip, line.split(';', 1))
            if line:
                self.tokens = lex(line)
                self.index = 0
                
                if self.peek('const'):
                    self.new_data(*self.values())
                elif self.peek('char'):
                    self.new_char(*self.values())
                elif self.peek('string'):
                    pass
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
                    if self.match('nop'):
                        self.jump(Cond.JNV, 0)
                    elif self.match('cond', 'label'):
                        self.jump(*self.values())
                    elif self.match('ld', 'reg', ',', '[', 'reg', ',', 'reg', ']'):
                        self.load0(*self.values())
                    elif self.match('ld', 'reg', ',', '[', 'reg', ']'):
                        self.load1(*self.values(), 0)
                    elif self.match('ld', 'reg', ',', '[', 'reg', ',', 'const', ']'):
                        self.load1(*self.values())
                    elif self.match('ld', '[', 'reg', ',', 'reg', ']', ',', 'reg'):
                        self.store0(*self.values())
                    elif self.match('ld', '[', 'reg', ']', ',', 'reg'):
                        self.store(*self.values())
                    elif self.match('ld', '[', 'reg', ',', 'const', ']', ',', 'reg'):
                        self.store1(*self.values())
                    elif self.match('ld', 'reg', ',', 'const'):
                        self.imm(*self.values())
                    elif self.match('ld', 'reg', ',', 'char'):
                        self.imm_char(*self.values())
                    elif self.match('ld', 'reg', ',', '=', 'label'):
                        self.imm(*self.values())
                    elif self.match('op', 'reg'):
                        self.inst1(*self.values(), Reg.A)
                    elif self.match('op', 'reg', ',', 'reg'):                    
                        self.inst1(*self.values())
                    elif self.match('op', 'reg', ',', 'const'):
                        self.inst2(*self.values())                    
                    elif self.match('op', 'reg', ',', 'reg', ',', 'reg'):
                        self.inst3(*self.values())                    
                    elif self.match('op', 'reg', ',', 'reg', ',', 'const'):
                        self.inst4(*self.values())
                    elif self.accept('push'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        self.expect('end')
                        for reg in args:
                            self.inst2(Op.SUB, Reg.SP, 1)
                            self.store(Reg.SP, reg)                                            
                    elif self.accept('pop'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        self.expect('end')
                        for reg in reversed(args):
                            self.inst2(Op.ADD, Reg.SP, 1)
                            self.load1(reg, Reg.SP , -1)                                                        
                    elif self.match('jump', 'label'):
                        self.imm(*self.values())
                    elif self.match('call', 'label'):
                        self.inst4(Op.ADD, Reg.LR, Reg.PC, 2)
                        self.jump(Cond.JR, *self.values())
                    elif self.match('ret'):
                        self.inst1(Op.MOV, Reg.PC, Reg.LR)
                    elif self.match('out', 'reg'):
                        pass
                    elif self.match('halt'):
                        self.inst1(Op.MOV, Reg.PC, Reg.PC)
                    else:
                        self.error()                    
        objects = []
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
        
    def error(self, expected=None, offset=0):
        etype, evalue = self.tokens[self.index-offset]
        raise SyntaxError(f'Unexpected {etype} token "{evalue}" at token #{self.index} in line {self.line_no}')# + 'Expected {}'.format(' or '.join(map('"{}"'.format, expected))) if expected else '')

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