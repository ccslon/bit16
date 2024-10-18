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

class Data:
    def __init__(self, value):
        assert -32768 <= value < 65536
        self.str = f'0x{value:04x}'
        self.dec = value,
        if value < 0:
            value = negative(value, 16)
        self.bin = f'{value:016b}',
    def __int__(self):
        return int(''.join(self.bin).replace('X','0'), base=2)
    def hex(self):
        return f'{int(self):04x}'
    def format_bin(self):
        return ' '.join(self.bin)
    def format_dec(self):
        return ' '.join(map(str,map(int,self.dec)))

class Char(Data):
    def __init__(self, char):
        self.str = f"'{escape(char)}'"
        assert 0 <= ord(char) < 128
        self.dec = 0,ord(char)
        self.bin = 'XXXXXXXXX',f'{ord(char):07b}'

class Inst(Data):
    pass

class Jump(Inst):
    def __init__(self, cond, const9):
        assert -256 <= const9 < 256
        if const9 < 0:
            self.str = f'{cond.name} -0x{-const9:03X}'
        else:
            self.str = f'{cond.name} 0x{const9:03X}'
        self.dec = 0,cond,const9
        if const9 < 0:
            const9 = negative(const9, 9)
        self.bin = '000',f'{cond:04b}',f'{const9:09b}'

class Unary(Inst):
    def __init__(self, op, rd):
        self.str = f'{op.name} {rd.name}'
        self.dec = 1,0,op,rd,rd
        self.bin = '001','0',f'{op:04b}','XX',f'{rd:03b}',f'{rd:03b}'
            
class Binary(Inst):
    def __init__(self, imm, op, src, rd):
        if imm:
            assert -16 <= src < 16
            self.str = f'{op.name} {rd.name}, {src}'
            self.dec = 1,imm,op,src,rd
            if src < 0:
                src = negative(src, 5)
            self.bin = '001','1',f'{op:04b}',f'{src:05b}',f'{rd:03b}'
        else:
            self.str = f'{op.name} {rd.name}, {src.name}'
            self.dec = 1,imm,op,0,src,rd
            self.bin = '001','0',f'{op:04b}','XX',f'{src:03b}',f'{rd:03b}'

class Byte(Inst):
    def __init__(self, op, byte, rd):
        if isinstance(byte, str):
            self.str = f"{op.name} {rd.name}, '{escape(byte)}'"
            self.dec = 2,op,ord(byte),rd
            self.bin = '010',f'{op:02b}',f'{ord(byte):08b}',f'{rd:03b}'
        else:
            assert 0 <= byte < 256
            self.str = f'{op.name} {rd.name}, 0x{byte:02X}'
            self.dec = 2,op,byte,rd
            self.bin = '010',f'{op:02b}',f'{byte:08b}',f'{rd:03b}'

class Offset(Inst):
    def __init__(self, op, rd, rs, offset):
        if -16 <= offset < 16:
            self.str = f'{op.name} {rd.name}, {rs.name}, {offset}'
            self.dec = 3,0,0,rs,offset,rd
            if op == Op.SUB:
                offset = negative(-offset, 5)
            self.bin = '011','0','X',f'{rs:03b}',f'{offset:05b}',f'{rd:03b}'
        else:            
            assert 0 <= offset < 256
            assert rs == Reg.FP
            self.str = f'{op.name} {rd.name}, FP, 0x{offset:02X}'
            self.dec = 3,1,0,offset,rd
            self.bin = '011','1','X',f'{offset:08b}',f'{rd:03b}'

class LoadStore(Inst):
    def __init__(self, storing, rd, rb, offset):
        if storing:
            self.str = f'ST [{rb.name}, {offset}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {offset}]'
        if -16 <= offset < 16:
            if offset < 0:
                offset = negative(-offset, 5)
            self.dec = 4,0,storing,rb,offset,rd
            self.bin = '100','0',str(storing),f'{rb:03b}',f'{offset:05b}',f'{rd:03b}'
        else:
            assert 0 <= offset < 256
            assert rb == Reg.FP
            self.dec = 4,1,storing,offset,rd
            self.bin = '100','1',str(storing),f'{offset:08b}',f'{rd:03b}'

class LoadStoreReg(Inst):
    def __init__(self, storing, rb, ro, rd):
        if storing:
            self.str = f'ST [{rb.name}, {ro.name}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {ro.name}]'
        self.dec = 5,0,storing,rb,0,ro,rd
        self.bin = '101','0',str(storing),f'{rb:03b}','XX',f'{ro:03b}',f'{rd:03b}'

class PushPop(Inst):
    def __init__(self, pushing, rd):
        if pushing:
            self.str = f'PUSH {rd.name}'
        else:
            self.str = f'POP {rd.name}'
        self.dec = 6,0,pushing,0,rd
        self.bin = '110','X',str(pushing),'XXXXXXXX',f'{rd:03b}'

class LoadWord(Inst):
    def __init__(self, rd):
        self.str = f'LDW {rd.name}, ...'
        self.dec = 7,0,rd
        self.bin = '111','XXXXXXXXXX',f'{rd:03b}'