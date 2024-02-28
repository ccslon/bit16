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
    FP = 4
    SP = 5
    LR = 6
    PC = 7

class Op(IntEnum):
    ADD = 0
    CMN = 1
    SUB = 2
    CMP = 3
    MUL = 4
    NOT = 5
    AND = 6
    TST = 7
    OR = 8
    XOR = 10
    TEQ = 11
    SHR = 12
    NEG = 13
    SHL = 14
    MOV = 15

class Cond(IntEnum):
    JNV = 0
    JEQ = 1
    JNE = 2
    JGT = 3
    JLT = 4
    JGE = 5
    JLE = 6
    JR = 7
    
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
        self.str = f'x{value:04x}'
        self._dec = value,
        if value < 0:
            value = negative(value, 16)
        self._bin = f'{value:016b}',
    def int(self):
        return int(''.join(self._bin).replace('X','0'), base=2)    
    def hex(self):
        return f'{self.int():04x}'
    def dec(self):
        return ' '.join(map(str,map(int,self._dec)))
    def bin(self):
        return ' '.join(self._bin)
    def __str__(self):
        return self.str

class Char(Data):
    def __init__(self, char):
        self.str = f"'{INV_ESCAPE.get(char, char)}'"
        char = ESCAPE.get(char, char)
        assert 0 <= ord(char) < 128
        self._dec = 0,ord(char)
        self._bin = 'XXXXXXXXX',f'{ord(char):07b}'

class Inst(Data):
    pass
        
class Jump(Inst):
    def __init__(self, cond, const10):
        assert -512 <= const10 < 512
        if const10 < 0:
            self.str = f'{cond.name} -x{-const10:03x}'
        else:
            self.str = f'{cond.name} x{const10:03x}'
        self._dec = 0,const10,cond
        if const10 < 0:
            const10 = negative(const10, 10)
        self._bin = '000',f'{const10:010b}',f'{cond:03b}'
class LdByte(Inst):
    def __init__(self, byte, rd):
        if isinstance(byte, str):
            self.str = f"LD {rd.name}, '{INV_ESCAPE.get(byte, byte)}'"
            char = ESCAPE.get(byte, byte)
            self._dec = 1,0,ord(char),rd
            self._bin = '001','XX',f'{ord(char):08b}',f'{rd:03b}'
        else:
            assert -128 <= byte < 128
            self.str = f'LD {rd.name}, {byte:02x}'
            self._dec = 1,0,byte,rd
            self._bin = '001','XX',f'{byte:08b}',f'{rd:03b}'
class Op2(Inst):
    def __init__(self, op, rd, rs):
        if op in [Op.NOT, Op.NEG]:
            self.str = f'{op.name} {rd.name}'
        else:
            self.str = f'{op.name} {rd.name}, {rs.name}'
        self._dec = 2,op,0,rs,rd
        self._bin = '010',f'{op:04b}','XXX',f'{rs:03b}',f'{rd:03b}'
class Op2Const6(Inst):
    def __init__(self, op, rd, const6):
        assert -32 <= const6 < 32
        self.str = f'{op.name} {rd.name}, {const6}'
        self._dec = 3,op,const6,rd
        if const6 < 0:
            const6 = negative(const6, 6)
        self._bin = '011',f'{op:04b}',f'{const6:06b}',f'{rd:03b}'
class Op3(Inst):
    def __init__(self, op, rd, rs, rs2):
        self.str = f'{op.name} {rd.name}, {rs.name}, {rs2.name}'
        op = op >> 1
        self._dec = 4,op,0,rs2,rs,rd
        self._bin = '100',f'{op:03b}','X',f'{rs2:03b}',f'{rs:03b}',f'{rd:03b}'
class Op3Const4(Inst):
    def __init__(self, op, rd, rs, const4):
        assert -8 <= const4 < 8
        self.str = f'{op.name} {rd.name}, {rs.name}, {const4}'
        op = op >> 1
        self._dec = 5,op,const4,rs,rd
        if const4 < 0:
            const4 = negative(const4, 4)
        self._bin = '101',f'{op:03b}',f'{const4:04b}',f'{rs:03b}',f'{rd:03b}'
class LdReg(Inst):
    def __init__(self, storing, rd, rb, ro):
        if storing:
            self.str = f'LD [{rb.name}, {ro.name}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {ro.name}]'
        self._dec = 6,0,int(storing),0,ro,rb,rd
        self._bin = '110','0',str(int(storing)),'XX',f'{ro:03b}',f'{rb:03b}',f'{rd:03b}'
class Ld(Inst):
    def __init__(self, storing, rd, rb, offset5):
        assert 0 <= offset5 < 32
        if storing:
            self.str = f'LD [{rb.name}, {offset5}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {offset5}]'
        self._dec = 6,1,int(storing),offset5,rb,rd
        self._bin = '110','1',str(int(storing)),f'{offset5:05b}',f'{rb:03b}',f'{rd:03b}'    
class LdWord(Inst):
    def __init__(self, rd):
        self.str = f'LD {rd.name}'
        self._dec = 7,0,rd
        self._bin = '111','XXXXXXXXXX',f'{rd:03b}'
