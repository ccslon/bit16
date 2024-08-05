# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:49:03 2023

@author: ccslon
"""

import re
from bit16 import Reg, Op, Cond, Data, Char, Jump, OpByte, Op4, Offset, OffsetFP, Load, LoadFP, LoadReg, StackOp, Word, unescape

TOKENS = {
    'const': r'-?(0x[0-9a-f]+|0b[01]+|\d+)',
    'string': r'"[^"]*"',
    'char': r"'\\?[^']'",
    'ldm': r'^(ldm)\b',
    'ld': r'^(ld)\b',
    'nop': r'^(nop)\b',
    'push': r'^(push)\b',
    'pop': r'^(pop)\b',
    'call': r'^(call)\b',
    'ret': r'^(ret)\b',
    'halt': r'^(halt)\b',
    'space': r'\b(space)\b',
    'reg': r'\b('+r'|'.join(reg.name for reg in Reg)+r')\b',
    'label': r'\.?[a-z_]\w*\s*:',
    'op': r'^('+r'|'.join(op.name for op in Op)+r')\b',
    'cond': r'^('+'|'.join(cond.name for cond in Cond)+r')\b',
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
    def load_reg(self, rd, rb, ro):
        self.new_inst(LoadReg, False, rd, rb, ro)
    def load(self, rd, rb, offset):
        if rb == Reg.FP:
            self.new_inst(LoadFP, False, rd, offset)
        else:
            self.new_inst(Load, False, rd, rb, offset)
    def store0(self, rb, rd):
        self.new_inst(Load, True, rd, rb, 0)
    def store_reg(self, rb, ro, rd):
        self.new_inst(LoadReg, True, rd, rb, ro)
    def store(self, rb, offset, rd):
        if rb == Reg.FP:
            self.new_inst(LoadFP, True, rd, offset)
        else:
            self.new_inst(Load, True, rd, rb, offset)
    def pop(self, rd):
        self.new_inst(StackOp, False, rd)
    def push(self, rd):
        self.new_inst(StackOp, True, rd)
    def load_word(self, rd, value):
        self.new_inst(Word, rd)
        self.new_imm(value)
    def op_byte(self, op, rd, byte):
        assert op in [Op.MOV, Op.ADD, Op.SUB, Op.CMP]
        self.new_inst(OpByte, op, byte, rd)
    def op1(self, op, rd):
        self.new_inst(Op4, False, op, rd, rd)
    def op4(self, op, rd, rs):
        self.new_inst(Op4, False, op, rd, rs)
    def op_const(self, op, rd, const):
        if -16 <= const < 16:
            self.new_inst(Op4, True, op, rd, const)
        elif 0 <= const < 256:
            assert op in [Op.MOV, Op.ADD, Op.SUB, Op.CMP]
            self.op_byte(op, rd, const)
        else:
            assert op == Op.MOV
            self.load_word(rd, const)
    def offset(self, op, rd, rs, const):
        assert op in [Op.ADD, Op.SUB]
        if rs == Reg.FP:
            self.new_inst(OffsetFP, op, rd, const)
        else:
            self.new_inst(Offset, op, rd, rs, const)
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
                        self.op1(*self.values())
                    elif self.match('op', 'reg', ',', 'reg'):
                        self.op4(*self.values())
                    elif self.match('op', 'reg', ',', 'const'):
                        self.op_const(*self.values())
                    elif self.match('op', 'reg', ',', 'char'):
                        self.op_byte(*self.values())
                    elif self.match('op', 'reg', ',', 'reg', ',', 'const'):
                        self.offset(*self.values())
                            
                    elif self.match('ld', 'reg', ',', '[', 'reg', ']'):
                        self.load(*self.values(), 0)
                    elif self.match('ld', 'reg', ',', '[', 'reg', ',', 'reg', ']'):
                        self.load_reg(*self.values())
                    elif self.match('ld', 'reg', ',', '[', 'reg', ',', 'const', ']'):
                        self.load(*self.values())
                                            
                    elif self.match('ld', '[', 'reg', ']', ',', 'reg'):
                        self.store0(*self.values())
                    elif self.match('ld', '[', 'reg', ',', 'reg', ']', ',', 'reg'):
                        self.store_w_reg_offset(*self.values())
                    elif self.match('ld', '[', 'reg', ',', 'const', ']', ',', 'reg'):
                        self.store(*self.values())
                        
                    elif self.match('ld', 'reg', ',', 'const'):
                        self.load_word(*self.values())
                    elif self.match('ld', 'reg', ',', '=', 'id'):
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
                        self.op4(Op.MOV, Reg.PC, *self.values())
                        
                    elif self.match('call', 'id'):
                        self.offset(Op.ADD, Reg.LR, Reg.PC, 3)
                        self.load_word(Reg.PC, *self.values())
                        
                    elif self.match('ret'):
                        self.op4(Op.MOV, Reg.PC, Reg.LR)
                    
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
                        self.op4(Op.MOV, Reg.PC, Reg.PC)
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
    assemble('main:\nMOV A, \'\\n\'')
    # assemble('testall.s')
    # assemble(ASM)