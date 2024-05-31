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
    JR = 15

ESCAPE = {
    '\\0': '\0',
    '\\t': '\t',
    '\\n': '\n',
    '\\b': '\b'
}
INV_ESCAPE = {
    '\0': '\\0',
    '\t': '\\t',
    '\n': '\\n',
    '\b': '\\b'
}

class Data:
    def __init__(self, value):
        assert -32768 <= value < 65536
        self.s = f'0x{value:04x}'
        self.d = value,
        if value < 0:
            value = negative(value, 16)
        self.b = f'{value:016b}',
    def int(self):
        return int(''.join(self.b).replace('X','0'), base=2)
    def hex(self):
        return f'{self.int():04x}'
    def bin(self):
        return ' '.join(self.b)
    def dec(self):
        return ' '.join(map(str,map(int,self.d)))

class Char(Data):
    def __init__(self, char):
        self.s = f"'{INV_ESCAPE.get(char, char)}'"
        char = ESCAPE.get(char, char)
        assert 0 <= ord(char) < 128
        self.d = 0,ord(char)
        self.b = 'XXXXXXXXX',f'{ord(char):07b}'

class Inst(Data):
    pass

class Jump(Inst):
    def __init__(self, cond, const9):
        assert -256 <= const9 < 256
        if const9 < 0:
            self.s = f'{cond.name} -0x{-const9:03X}'
        else:
            self.s = f'{cond.name} 0x{const9:03X}'
        self.d = 0,const9,cond
        if const9 < 0:
            const9 = negative(const9, 9)
        self.b = '000',f'{const9:09b}',f'{cond:04b}'
class OpByte(Inst):
    def __init__(self, op, byte, rd):
        if isinstance(byte, str):
            self.s = f"{op.name} {rd.name}, '{INV_ESCAPE.get(byte, byte)}'"
            char = ESCAPE.get(byte, byte)
            self.d = 2,op,ord(char),rd
            self.b = '010',f'{op:02b}',f'{ord(char):08b}',f'{rd:03b}'
        else:
            assert 0 <= byte < 256
            self.s = f'{op.name} {rd.name}, 0x{byte:02X}'
            self.d = 2,op,byte,rd
            self.b = '010',f'{op:02b}',f'{byte:08b}',f'{rd:03b}'
class Op4(Inst):
    def __init__(self, imm, op, rd, src):
        if op in [Op.NOT, Op.NEG]:
            self.s = f'{op.name} {rd.name}'
            self.d = 1,0,op,rd,rd
            self.b = '001','0',f'{op:04b}','XX',f'{rd:03b}',f'{rd:03b}'
        else:
            if imm:
                assert -16 <= src < 16
                self.s = f'{op.name} {rd.name}, {src}'
                self.d = 1,imm,op,src,rd
                if src < 0:
                    src = negative(src, 5)
                self.b = '001','1',f'{op:04b}',f'{src:05b}',f'{rd:03b}'
            else:
                self.s = f'{op.name} {rd.name}, {src.name}'
                self.d = 1,imm,op,0,src,rd
                self.b = '001','0',f'{op:04b}','XX',f'{src:03b}',f'{rd:03b}'

class Offset(Inst):
    def __init__(self, op, rd, rs, const5):
        assert -16 <= const5 < 16
        self.s = f'{op.name} {rd.name}, {rs.name}, {const5}'
        self.d = 3,0,0,rs,const5,rd
        if op == Op.SUB:
            const5 = negative(-const5, 5)
        self.b = '011','0','X',f'{rs:03b}',f'{const5:05b}',f'{rd:03b}'

class OffsetFP(Inst):
    def __init__(self, op, rd, byte):
        assert 0 <= byte < 256
        self.s = f'{op.name} {rd.name}, FP, 0x{byte:02X}'
        self.d = 3,1,0,byte,rd
        self.b = '011','1','X',f'{byte:08b}',f'{rd:03b}'

class Load(Inst):
    def __init__(self, storing, rd, rb, offset5):
        assert 0 <= offset5 < 32
        if storing:
            self.s = f'LD [{rb.name}, {offset5}], {rd.name}'
        else:
            self.s = f'LD {rd.name}, [{rb.name}, {offset5}]'
        self.d = 4,0,int(storing),rb,offset5,rd
        self.b = '100','0',str(int(storing)),f'{rb:03b}',f'{offset5:05b}',f'{rd:03b}'

class LoadFP(Inst):
    def __init__(self, storing, rd, offset8):
        assert 0 <= offset8 < 256
        if storing:
            self.s = f'LD [FP, {offset8}], {rd.name}'
        else:
            self.s = f'LD {rd.name}, [FP, {offset8}]'
        self.d = 4,1,int(storing),offset8,rd
        self.b = '100','1',str(int(storing)),f'{offset8:08b}',f'{rd:03b}'

class LoadReg(Inst):
    def __init__(self, storing, rd, rb, ro):
        if storing:
            self.s = f'LD [{rb.name}, {ro.name}], {rd.name}'
        else:
            self.s = f'LD {rd.name}, [{rb.name}, {ro.name}]'
        self.d = 5,0,int(storing),0,ro,rb,rd
        self.b = '101','0',str(int(storing)),'XX',f'{ro:03b}',f'{rb:03b}',f'{rd:03b}'

class StackOp(Inst):
    def __init__(self, pushing, rd):
        if pushing:
            self.s = f'PUSH {rd.name}'
        else:
            self.s = f'POP {rd.name}'
        self.d = 6,0,int(pushing),0,rd
        self.b = '110','X',str(int(pushing)),'XXXXXXXX',f'{rd:03b}'

class Word(Inst):
    def __init__(self, rd):
        self.s = f'LD {rd.name}, ...'
        self.d = 7,0,rd
        self.b = '111','XXXXXXXXXX',f'{rd:03b}'