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
    MUL = 4
    NOT = 5
    DIV = 6
    MOD = 7
    AND = 8
    OR =  9
    XOR = 10
    # = 11
    # = 12
    NEG = 13
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
    '\t': r'\t',
    '\n': r'\n',
    '\b': r'\b',
    '\\': r'\\'
}
UNESCAPE = {
    r'\n': '\n',
    r'\0': '\0',
    r'\t': '\t',
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
        
class OpByte(Inst):
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
            
class Op4(Inst):
    def __init__(self, imm, op, rd, src):
        if op in [Op.NOT, Op.NEG]:
            self.str = f'{op.name} {rd.name}'
            self.dec = 1,0,op,rd,rd
            self.bin = '001','0',f'{op:04b}','XX',f'{rd:03b}',f'{rd:03b}'
        else:
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

class Offset(Inst):
    def __init__(self, op, rd, rs, const5):
        assert -16 <= const5 < 16
        self.str = f'{op.name} {rd.name}, {rs.name}, {const5}'
        self.dec = 3,0,0,rs,const5,rd
        if op == Op.SUB:
            const5 = negative(-const5, 5)
        self.bin = '011','0','X',f'{rs:03b}',f'{const5:05b}',f'{rd:03b}'

class OffsetFP(Inst):
    def __init__(self, op, rd, byte):
        assert 0 <= byte < 256
        self.str = f'{op.name} {rd.name}, FP, 0x{byte:02X}'
        self.dec = 3,1,0,byte,rd
        self.bin = '011','1','X',f'{byte:08b}',f'{rd:03b}'

class Load(Inst):
    def __init__(self, storing, rd, rb, offset5):
        assert 0 <= offset5 < 32
        if storing:
            self.str = f'LD [{rb.name}, {offset5}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {offset5}]'
        self.dec = 4,0,int(storing),rb,offset5,rd
        self.bin = '100','0',str(int(storing)),f'{rb:03b}',f'{offset5:05b}',f'{rd:03b}'

class LoadFP(Inst):
    def __init__(self, storing, rd, offset8):
        assert 0 <= offset8 < 256
        if storing:
            self.str = f'LD [FP, {offset8}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [FP, {offset8}]'
        self.dec = 4,1,int(storing),offset8,rd
        self.bin = '100','1',str(int(storing)),f'{offset8:08b}',f'{rd:03b}'

class LoadReg(Inst):
    def __init__(self, storing, rd, rb, ro):
        if storing:
            self.str = f'LD [{rb.name}, {ro.name}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {ro.name}]'
        self.dec = 5,0,int(storing),0,ro,rb,rd
        self.bin = '101','0',str(int(storing)),'XX',f'{ro:03b}',f'{rb:03b}',f'{rd:03b}'

class StackOp(Inst):
    def __init__(self, pushing, rd):
        if pushing:
            self.str = f'PUSH {rd.name}'
        else:
            self.str = f'POP {rd.name}'
        self.dec = 6,0,int(pushing),0,rd
        self.bin = '110','X',str(int(pushing)),'XXXXXXXX',f'{rd:03b}'

class Word(Inst):
    def __init__(self, rd):
        self.str = f'LD {rd.name}, ...'
        self.dec = 7,0,rd
        self.bin = '111','XXXXXXXXXX',f'{rd:03b}'