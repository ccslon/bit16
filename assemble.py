# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:49:03 2023

@author: ccslon
"""

import re
from bit16 import Reg, Op, Cond, Data, Char, Jump, Inst1, Inst2, Inst3, Inst4, Load0, Load1, Imm

TOKENS = {'const': r'(-?\d+)|(x[0-9a-f]+)|(b[01]+)',
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
          'dash': r'-',
          'lbrace': r'\[',
          'rbrace': r'\]',
          'lbrack': r'\{',
          'rbrack': r'\}',
          'comma': r',',
          'error': r'\S+'}
RE = re.compile('|'.join(rf'(?P<{token}>{pattern})' for token, pattern in TOKENS.items()), re.I)
def lex(text):
    return [(match.lastgroup , match.group()) for match in RE.finditer(text)]

class Pattern:
    def __init__(self, text):
        self.tokens = lex(text)
        self.values = self._values()
    def match(self, *pattern):
        return len(self.tokens) == len(pattern) and all(pattern[i] in (type_, value) for i, (type_, value) in enumerate(self.tokens))
    def _values(self):
        for type_, value in self.tokens:
            if type_ == 'const':
                if value.startswith('x'):
                    yield int(value[1:], base=16)
                elif value.startswith('b'):
                    yield int(value[1:], base=2)
                else:
                    yield int(value)
            elif type_ in ['string', 'char']:
                yield value[1:-1]
            elif type_ == 'reg':
                yield Reg[value.upper()]
            elif type_ == 'cond':
                yield Cond[value.upper()]
            elif type_ == 'op':
                yield Op[value.upper()]
            elif type_ == 'label':
                yield value

class Assembler:
    def label(self, label):
        self.labels.append(label)
    def const(self, label, value):
        self.label(label)
        self.new_data(value)
    def char(self, label, char):
        self.label(label)
        self.new_char(char)
    def string(self, label, string):
        self.label(label)
        for char in string:
            self.new_char(char)
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
    def new_data(self, value):
        self.data.append((self.labels, Data, (value,)))
        self.labels = []
    def new_char(self, char):
        self.data.append((self.labels, Char, (char,)))
        self.labels = []
    def assemble(self, asm):        
        self.inst = []
        self.data = []
        self.labels = []
        for line in map(str.strip, asm.strip().split('\n')):
            if ';' in line:
                line, comment = map(str.strip, line.split(';', 1))
            if line:
                pattern = Pattern(line)
                if pattern.match('label', ':'):
                    self.label(*pattern.values)
                elif pattern.match('label', 'const'):
                    self.const(*pattern.values)
                elif pattern.match('label', 'char'):
                    self.char(*pattern.values)
                elif pattern.match('label', 'string'):
                    self.string(*pattern.values)
                elif pattern.match('nop'):
                    self.jump(Cond.JNV, 0)
                elif pattern.match('cond', 'label'):
                    self.jump(*pattern.values)
                elif pattern.match('ld', 'reg', ',', '[', 'reg', ',', 'reg', ']'):
                    self.load0(*pattern.values)
                elif pattern.match('ld', 'reg', ',', '[', 'reg', ']'):
                    self.load1(*pattern.values, 0)
                elif pattern.match('ld', 'reg', ',', '[', 'reg', ',', 'const', ']'):
                    self.load1(*pattern.values)
                elif pattern.match('ld', '[', 'reg', ',', 'reg', ']', ',', 'reg'):
                    self.store0(*pattern.values)
                elif pattern.match('ld', '[', 'reg', ']', ',', 'reg'):
                    self.store(*pattern.values)
                elif pattern.match('ld', '[', 'reg', ',', 'const', ']', ',', 'reg'):
                    self.store1(*pattern.values)
                elif pattern.match('ld', 'reg', ',', 'const'):
                    self.imm(*pattern.values)
                elif pattern.match('ld', 'reg', ',', '=', 'label'):
                    self.imm(*pattern.values)
                elif pattern.match('op', 'reg'):
                    self.inst1(*pattern.values, Reg.A)
                elif pattern.match('op', 'reg', ',', 'reg'):                    
                    self.inst1(*pattern.values)
                elif pattern.match('op', 'reg', ',', 'const'):
                    self.inst2(*pattern.values)                    
                elif pattern.match('op', 'reg', ',', 'reg', ',', 'reg'):
                    self.inst3(*pattern.values)                    
                elif pattern.match('op', 'reg', ',', 'reg', ',', 'const'):
                    self.inst4(*pattern.values)
                elif pattern.match('push', 'reg'):
                    self.inst2(Op.SUB, Reg.SP, 1)
                    self.store(Reg.SP, *pattern.values)
                elif pattern.match('push', '{', 'reg', '-', 'reg', '}'):
                    start, end = pattern.values
                    for reg in range(start, end+1):
                        self.inst2(Op.SUB, Reg.SP, 1)
                        self.store(Reg.SP, Reg(reg))
                elif pattern.match('push', 'lr', ',', '{', 'reg', '-', 'reg', '}'):
                    lr, start, end = pattern.values
                    self.inst2(Op.SUB, Reg.SP, 1)
                    self.store(Reg.SP, lr)
                    for reg in range(start, end+1):
                        self.inst2(Op.SUB, Reg.SP, 1)
                        self.store(Reg.SP, Reg(reg))
                elif pattern.match('pop', 'reg'):
                    self.inst2(Op.ADD, Reg.SP, 1)
                    self.load1(Reg(reg), Reg.SP , -1)
                elif pattern.match('pop', '{', 'reg', '-', 'reg', '}'):
                    start, end = pattern.values
                    for reg in reversed(range(start, end+1)):
                        self.inst2(Op.ADD, Reg.SP, 1)
                        self.load1(Reg(reg), Reg.SP , -1)
                elif pattern.match('pop', 'pc', ',', '{', 'reg', '-', 'reg', '}'):
                    pc, start, end = pattern.values
                    for reg in reversed(range(start, end+1)):
                        self.inst2(Op.ADD, Reg.SP, 1)
                        self.load1(Reg(reg), Reg.SP , -1)
                    self.inst2(Op.ADD, Reg.SP, 1)
                    self.load1(pc, Reg.SP, -1)
                elif pattern.match('jump', 'label'):
                    self.imm(*pattern.values)
                elif pattern.match('call', 'label'):
                    self.inst1(Op.MOV, Reg.LR, Reg.PC)
                    self.inst2(Op.ADD, Reg.LR, 3)
                    self.jump(Cond.JR, *pattern.values)
                elif pattern.match('ret'):
                    self.inst1(Op.MOV, Reg.PC, Reg.LR)
                elif pattern.match('out', 'reg'):
                    pass
                elif pattern.match('halt'):
                    self.inst1(Op.MOV, Reg.PC, Reg.PC)
                else:
                    self.error(line)
                    
        objects = []
        objects.extend(self.inst)
        objects.extend(self.data)
        return objects
        
    def error(self, line):
        raise SyntaxError(f'Syntax error in line : "{line}"')

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
    
def assemble(program):
    objects = Assembler().assemble(program)
    Linker.link(objects)