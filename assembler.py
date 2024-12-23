# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:49:03 2023

@author: ccslon
"""

import re
from enum import IntEnum
from bit16 import Reg, Op, Cond, Data, Char, Jump, Unary, Binary, Byte, Offset, Load, LoadReg, PushPop, LoadWord, unescape

RE_OP = r'|'.join(op.name for op in Op)
RE_COND = r'|'.join(cond.name for cond in Cond)
RE_REG = r'|'.join(reg.name for reg in Reg)

TOKENS = {
    'const': r'-?(0x[0-9a-f]+|0b[01]+|\d+)',
    'string': r'"(\\"|[^"])*"',
    'char': r"'\\?[^']'",
    # 'ldm': r'^(ldm)\b',    
    'ldw': r'^(ldw)\b',
    'ld': r'^(ld)\b',
    'st': r'^(st)\b',
    'nop': r'^(nop)\b',
    'push': r'^(push)\b',
    'pop': r'^(pop)\b',
    'call': r'^(call)\b',
    'ret': r'^(ret)\b',
    'halt': r'^(halt)\b',
    'space': r'\b(space)\b',
    'reg': rf'\b({RE_REG})\b',
    'label': r'\.?[a-z_]\w*\s*:',
    'op': rf'^({RE_OP})\b',
    'cond': rf'^({RE_COND})\b',
    'id': r'\.?[a-z_]\w*',
    'equal': r'=',
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
        self.new_char(char)
    def string(self, label, string):
        self.label(label)
        for char in string:
            self.new_char(char)
    def space(self, label, size):
        self.label(label)
        for _ in range(size):
            self.new_data(0)
    def jump(self, cond, label):
        self.new_inst(Jump, cond, label)
    def unary(self, op, rd):
        self.new_inst(Unary, op, rd)
    def binary(self, op, rd, src, imm):
        if imm:
            if -16 <= src < 16:
                self.new_inst(Binary, True, op, src, rd)
            elif 0 <= src < 256:
                assert op in [Op.MOV, Op.ADD, Op.SUB, Op.CMP]
                self.byte(op, rd, src)
            else:
                assert op == Op.MOV
                self.load_word(rd, src)
        else:
            self.new_inst(Binary, False, op, src, rd)
    def offset(self, op, rd, rs, offset):
        assert op in [Op.ADD, Op.SUB]
        self.new_inst(Offset, op, rd, rs, offset)
    def byte(self, op, rd, byte):
        assert op in [Op.MOV, Op.ADD, Op.SUB, Op.CMP]
        self.new_inst(Byte, op, byte, rd)
    def load(self, rd, rb, offset):
        if rb == Reg.FP:
            assert -16 <= offset < 256
        else:
            assert -16 <= offset < 16
        self.new_inst(Load, False, rd, rb, offset)
    def load_reg(self, rd, rb, ro):
        self.new_inst(LoadReg, False, rb, ro, rd)
    def store(self, rb, offset, rd):
        if rb == Reg.FP:
            assert -16 <= offset < 256
        else:
            assert -16 <= offset < 16 
        self.new_inst(Load, True, rd, rb, offset)
    def store0(self, rb, rd):
        self.new_inst(Load, True, rd, rb, 0)
    def store_reg(self, rb, ro, rd):
        self.new_inst(LoadReg, True, rb, ro, rd)
    def pop(self, rd):
        self.new_inst(PushPop, False, rd)
    def push(self, rd):
        self.new_inst(PushPop, True, rd)
    def load_word(self, rd, value):
        self.new_inst(LoadWord, rd)
        self.new_imm(value)
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
    def name(self, name, value):
        self.names[name] = value

    def assemble(self, asm):
        with open('boot.s') as bios:
            base = bios.read()
        self.inst = []
        self.data = []
        self.labels = []
        self.names = {}
        for self.line_no, line in enumerate(map(str.strip, (base+'\n'+asm).strip().split('\n'))):
            if ';' in line:
                line, comment = map(str.strip, line.split(';', 1))
            if line:
                self.tokens = lex(line)
                self.index = 0
                
                if self.match('id', '=', 'const'):
                    print(f'{self.line_no: >2}|{line}')
                    self.name(*self.values())
                    
                elif self.peek('label'):
                    print(f'{self.line_no: >2}|{line}')
                    
                    if self.match('label'):
                        self.label(*self.values())                        
                    elif self.match('label', 'const'):
                        self.const(*self.values())                        
                    elif self.match('label', 'id'):
                        self.const(*self.values())                        
                    elif self.match('label', 'char'):
                        self.char(*self.values())                        
                    elif self.match('label', 'string'):
                        self.string(*self.values())                        
                    elif self.match('label', 'space', 'const'):
                        self.space(*self.values())                        
                    else:
                        self.error()
                else:
                    print(f'{self.line_no: >2}|  {line}')
                    
                    if self.match('nop'):
                        self.jump(Cond.JNV, 0)
                    
                    elif self.match('id'):
                        self.new_data(*self.values())
                    elif self.match('const'):
                        self.new_data(*self.values())
                    elif self.match('char'):
                        self.new_char(*self.values())
                        
                    elif self.match('cond', 'id'):
                        self.jump(*self.values())
                        
                    elif self.match('op', 'reg'):
                        self.unary(*self.values())
                    elif self.match('op', 'reg', ',', 'reg'):
                        self.binary(*self.values(), False)
                    elif self.match('op', 'reg', ',', 'const'):
                        self.binary(*self.values(), True)
                    elif self.match('op', 'reg', ',', 'char'):
                        self.byte(*self.values())
                    elif self.match('op', 'reg', ',', 'reg', ',', 'const'):
                        self.offset(*self.values())
                            
                    elif self.match('ld', 'reg', ',', '[', 'reg', ']'):
                        self.load(*self.values(), 0)
                    elif self.match('ld', 'reg', ',', '[', 'reg', ',', 'reg', ']'):
                        self.load_reg(*self.values())
                    elif self.match('ld', 'reg', ',', '[', 'reg', ',', 'const', ']'):
                        self.load(*self.values())
                                            
                    elif self.match('st', '[', 'reg', ']', ',', 'reg'):
                        self.store0(*self.values())
                    elif self.match('st', '[', 'reg', ',', 'reg', ']', ',', 'reg'):
                        self.store_reg(*self.values())
                    elif self.match('st', '[', 'reg', ',', 'const', ']', ',', 'reg'):
                        self.store(*self.values())
                        
                    elif self.match('ldw', 'reg', ',', 'const'):
                        self.load_word(*self.values())
                    elif self.match('ldw', 'reg', ',', '=', 'id'):
                        self.load_word(*self.values())
                        
                    elif self.accept('push'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        self.expect('end')
                        for reg in args:
                            self.push(reg)
                            
                    elif self.accept('pop'):
                        args = [self.expect('reg')]
                        while self.accept(','):
                            args.append(self.expect('reg'))
                        self.expect('end')
                        for reg in reversed(args):
                            self.pop(reg)
                        
                    elif self.match('jump', 'id'):
                        self.load_word(Reg.PC, *self.values())
                        
                    elif self.match('call','reg'):
                        self.offset(Op.ADD, Reg.LR, Reg.PC, 2)
                        self.binary(Op.MOV, Reg.PC, *self.values(), False)
                        
                    elif self.match('call', 'id'):
                        self.offset(Op.ADD, Reg.LR, Reg.PC, 3)
                        self.load_word(Reg.PC, *self.values())
                        
                    elif self.match('ret'):
                        self.binary(Op.MOV, Reg.PC, Reg.LR, False)
                    
                    elif self.accept('ldm'):
                        if self.accept('{'):
                            regs = [self.expect('reg')]
                            while self.accept(','):
                                regs.append(self.expect('reg'))
                            self.expect('}')
                            self.expect(',')
                            dest = self.expect('reg')
                            for i, reg in enumerate(regs):
                                self.load(reg, dest, i)
                        else:
                            dest = self.expect('reg')
                            self.expect(',')
                            self.expect('{')
                            regs = [self.expect('reg')]
                            while self.accept(','):
                                regs.append(self.expect('reg'))
                            self.expect('}')
                            for i, reg in enumerate(regs):
                                self.store(dest, i, reg)
                        
                    elif self.match('halt'):
                        self.binary(Op.MOV, Reg.PC, Reg.PC, False)
                    else:
                        self.error()
        return self.inst + self.data

    def trans(self, type, value):
        if type == 'const':
            if value.startswith('0x'):
                return int(value, base=16)
            elif value.startswith('0b'):
                return int(value, base=2)
            else:
                return int(value)
        elif type in ['string', 'char']:
            return unescape(value[1:-1])
        elif type == 'reg':
            return Reg[value.upper()]
        elif type == 'cond':
            return Cond[value.upper()]
        elif type == 'op':
            return Op[value.upper()]
        elif type == 'label':
            return value[:-1].strip()
        elif type == 'id':
            if value in self.names:
                return self.names[value]
            return value

    def values(self):
        for type, value in self.tokens:
            if type in ['const','string','char','reg','cond','op','label','id']:
                yield self.trans(type, value)

    def match(self, *pattern):
        pattern = (*pattern, 'end')
        return len(self.tokens) == len(pattern) and all(self.peek(symbol, offset=i) for i, symbol in enumerate(pattern))

    def __next__(self):
        type, value = self.tokens[self.index]
        self.index += 1
        if type in ['const','string','char','reg','cond','op','label','id']:
            return self.trans(type, value)
        return value

    def peek(self, *symbols, offset=0):
        type, value = self.tokens[self.index+offset]
        return type in symbols or (not value.isalnum() and value in symbols)

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
        for i, (labels, type, args) in enumerate(objects):
            for label in labels:
                targets[label] = i
                indices.add(i)
            objects[i] = (type, args)
        print('-'*67)
        contents = []
        for i, (type, args) in enumerate(objects):
            if args and type is not Char:
                *args, last = args
                if isinstance(last, str):
                    last = targets[last]
                    if type is Jump:
                        last -= i
                args = *args, last
            data = type(*args)
            contents.append(data.hex())
            print('>>' if i in indices else '  ', f'{i:04x}', f'{data.str: <15}', f'| {data.format_dec(): <13}', f'{data.format_bin(): <22}', data.hex())
        print('\n', ' '.join(contents))
        print(len(contents))
        return contents

assembler = Assembler()

class Color(IntEnum):
    ITAL = 3
    GREY = 30
    RED = 31
    GREEN = 32
    ORANGE = 33
    BLUE = 34
    PURPLE = 35
    CYAN = 36
    WHITE = 37

PATTERNS = {
    r'"(\\"|[^"])*"': Color.GREEN, #string
    r"'\\?[^']'": Color.GREEN, #char
    r'\b-?(0x[0-9a-f]+|0b[01]+|\d+)\b': Color.ORANGE, #const
    rf'\b({RE_REG})\b': Color.ITAL, #register
    rf'\b(ldw|ld|st|nop|push|pop|call|ret|halt|{RE_OP}|{RE_COND})\b': Color.BLUE, #ops
    r'\.?[a-z_]\w*': Color.CYAN, #id
    r';.*$': Color.GREY #comment
}

def repl(match, color):
    if color:
        return f'\33[1;{color}m{match[0]}\33[0m'
    return match[0]

def display(asm):
    for line in asm.split('\n'):
        new = ""
        while line:
            for pattern, color in PATTERNS.items():
                match = re.match(pattern, line, re.I)
                if match:
                    new += repl(match, color)
                    line = line[len(match[0]):]
                    break
            if match is None:
                new += line[0]
                line = line[1:]
        print(new)

def assemble(program, fflag=True, name='out'):
    if program.endswith('.s'):
        name = program[:-2]
        with open(program) as file:
            program = file.read()
    objects = assembler.assemble(program)
    bit16 = Linker.link(objects)
    if fflag:
        with open(f'{name}.bit16', 'w+') as file:
            file.write('v2.0 raw\n' + ' '.join(bit16))

if __name__ == '__main__':
    ASM = '''
    main:
        ret
    '''
    assemble(ASM)