# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 19:28:14 2023

@author: ccslon
"""
from enum import IntEnum

def negative(num, base):
    return (-num ^ (2**base - 1)) + 1

class Reg(IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3
    LR = 4
    FP = 5
    SP = 6
    PC = 7

class Op(IntEnum):
    MOV = 0
    ADD = 1
    SUB = 2
    CMP = 3
    NOT = 4
    NEG = 5
    # = 6
    # = 7
    MUL = 8
    DIV = 9
    MOD = 10
    AND = 11
    OR =  12
    XOR = 13
    SHR = 14
    SHL = 15

class Cond(IntEnum):
    JNV = 0
    JEQ = 1
    JNE = 2
    JMI = 3
    JPL = 4
    JVS = 5
    JVC = 6
    JCS = JHS = 7
    JCC = JLO = 8
    JHI = 9
    JLS = 10
    JLT = 11
    JGE = 12
    JLE = 13
    JGT = 14
    JR = JMP = 15

class InstOp(IntEnum):
    JUMP = 0
    ALU = 1
    BYTE = 2
    OFFSET = 3
    LOAD = 4
    LOAD_REG = 5
    PUSH_POP = 6
    LOAD_WORD = 7

ESCAPE = {
    '\0': r'\0',
    '\"': r'\"',
    '\'': r'\'',
    '\t': r'\t',
    '\n': r'\n',
    '\b': r'\b',
    '\\': r'\\'
}
UNESCAPE = {
    r'\0': '\0',
    r'\"': '\"',
    r'\'': '\'',
    r'\t': '\t',
    r'\n': '\n',
    r'\b': '\b',
    r'\\': '\\'
}
def unescape(text):
    for k, v in UNESCAPE.items():
        text = text.replace(k, v)
    return text
def escape(char):
    return ESCAPE.get(char, char)

class Word:
    def __init__(self):
        self.bin = 0
        self.dec = []
    def __setitem__(self, item, value):
        if isinstance(item, slice):
            assert item.step is None
            self.bin |= (value or 0) << item.stop
            self.dec.append((value, item.start-item.stop+1))
        else:
            self.bin |= (value or 0) << item
            self.dec.append((value, 1))    
    def hex(self):
        return f'{self.bin:04x}'
    def format_bin(self):
        return ' '.join('X'*size if value is None else f'{value:0{size}b}' for value, size in self.dec)
    def format_dec(self):
        return ' '.join('0' if value is None else f'{value:d}' for value, _ in self.dec)

class Data(Word):
    def __init__(self, value):
        super().__init__()
        assert -32768 <= value < 65536
        self.str = f'0x{value:04x}'
        if value < 0:
            value = negative(value, 16)
        self[15:0] = value

class Char(Word):
    def __init__(self, char):
        super().__init__()
        assert 0 <= ord(char) < 128
        self.str = f"'{escape(char)}'"
        self[15:7] = None
        self[6:0] = ord(char)
        
class Inst(Word):
    pass

class Jump(Inst):
    def __init__(self, cond, const9):
        super().__init__()
        assert -256 <= const9 < 256
        if const9 < 0:
            self.str = f'{cond.name} -0x{-const9:03X}'
            const9 = negative(const9, 9)
        else:
            self.str = f'{cond.name} 0x{const9:03X}'
        self[15:13] = InstOp.JUMP
        self[12:9] = cond
        self[8:0] = const9

class Unary(Inst):
    def __init__(self, op, rd):
        super().__init__()
        self.str = f'{op.name} {rd.name}'
        self[15:13] = InstOp.ALU
        self[12] = 0
        self[11:8] = op
        self[7:6] = None
        self[5:3] = rd
        self[2:0] = rd
            
class Binary(Inst):
    def __init__(self, imm, op, src, rd):
        super().__init__()
        self[15:13] = InstOp.ALU
        self[12] = imm
        self[11:8] = op
        if imm:
            assert -16 <= src < 16
            if src < 0:
                src = negative(src, 5)
            self[7:3] = src
        else:
            self[7:6] = None
            self[5:3] = src
            src = src.name
        self[2:0] = rd
        self.str = f'{op.name} {rd.name}, {src}'        

class Byte(Inst):
    def __init__(self, op, byte, rd):
        super().__init__()
        self[15:13] = InstOp.BYTE
        self[12:11] = op
        if isinstance(byte, str):
            self[10:3] = ord(byte)
            byte = f"'{escape(byte)}'"
        else:
            assert 0 <= byte < 256
            self[10:3] = byte
            byte = f'0x{byte:02X}'            
        self[2:0] = rd
        self.str = f"{op.name} {rd.name}, {byte}"

class Offset(Inst):
    def __init__(self, op, rd, rb, offset):
        super().__init__()
        self[15:13] = InstOp.OFFSET
        if -16 <= offset < 16:
            self[12] = 0
            self[11] = None
            self[10:8] = rb            
            if op == Op.SUB:
                offset = negative(-offset, 5)
            self[7:3] = offset
        else:            
            assert 0 <= offset < 256
            assert rb == Reg.FP
            self[12] = 1
            self[11] = None
            self[10:3] = offset
            offset = f'0x{offset:02X}'
        self[2:0] = rd
        self.str = f'{op.name} {rd.name}, {rb.name}, {offset}'

class Load(Inst):
    def __init__(self, storing, rd, rb, offset):
        super().__init__()
        self[15:13] = InstOp.LOAD
        if -16 <= offset < 16:
            self[12] = 0
            self[11] = storing
            self[10:8] = rb        
            if offset < 0:
                offset = negative(offset, 5)
            self[7:3] = offset
        else:            
            assert 0 <= offset < 256
            assert rb == Reg.FP
            self[12] = 1
            self[11] = storing
            self[10:3] = offset
        self[2:0] = rd        
        if storing:
            self.str = f'ST [{rb.name}, {offset}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {offset}]'

class LoadReg(Inst):
    def __init__(self, storing, rb, ro, rd):
        super().__init__()
        self[15:13] = InstOp.LOAD_REG
        self[12] = 0
        self[11] = storing
        self[10:8] = rb
        self[7:6] = None
        self[5:3] = ro
        self[2:0] = rd
        if storing:
            self.str = f'ST [{rb.name}, {ro.name}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {ro.name}]'

class PushPop(Inst):
    def __init__(self, pushing, rd):
        super().__init__()
        self[15:13] = InstOp.PUSH_POP
        self[12] = None
        self[11] = pushing
        self[10:3] = None
        self[2:0] = rd
        if pushing:
            self.str = f'PUSH {rd.name}'
        else:
            self.str = f'POP {rd.name}'

class LoadWord(Inst):
    def __init__(self, rd):
        super().__init__()
        self[15:13] = InstOp.LOAD_WORD
        self[12:3] = None
        self[2:0] = rd
        self.str = f'LDW {rd.name}, ...'