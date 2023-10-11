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
    E = 4
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
        if char == '\\0':
            char = '\0'
        assert 0 <= ord(char) < 128
        self.str = char
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
        self._dec = 0,cond,const10
        if const10 < 0:
            const10 = negative(const10, 10)
        self._bin = '000', f'{cond:03b}', f'{const10:010b}'
class Inst1(Inst):
    def __init__(self, op, rd, rs):
        if op in [Op.NOT, Op.NEG]:
            self.str = f'{op.name} {rd.name}'
        else:
            self.str = f'{op.name} {rd.name}, {rs.name}'
        self._dec = 1,op,0,rs,rd
        self._bin = '001',f'{op:04b}','XXX',f'{rs:03b}',f'{rd:03b}'
class Inst2(Inst):
    def __init__(self, op, rd, const6):
        assert -32 <= const6 < 64
        self.str = f'{op.name} {rd.name}, {const6}'
        self._dec = 2,op,const6,rd
        if const6 < 0:
            const6 = negative(const6, 6)
        self._bin = '010',f'{op:04b}',f'{const6:06b}',f'{rd:03b}'
class Inst3(Inst):
    def __init__(self, op, rd, rs, rs2):
        self.str = f'{op.name} {rd.name}, {rs.name}, {rs2.name}'
        op = op >> 1
        self._dec = 3,op,0,rs2,rs,rd
        self._bin = '011',f'{op:03b}','X',f'{rs2:03b}',f'{rs:03b}',f'{rd:03b}'
class Inst4(Inst):
    def __init__(self, op, rd, rs, const4):
        assert -8 <= const4 < 8
        self.str = f'{op.name} {rd.name}, {rs.name}, {const4}'
        op = op >> 1
        self._dec = 4,op,const4,rs,rd
        if const4 < 0:
            const4 = negative(const4, 4)
        self._bin = '100',f'{op:03b}',f'{const4:04b}',f'{rs:03b}',f'{rd:03b}'
class Inst5(Inst):
    pass      
class Load0(Inst):
    def __init__(self, storing, rd, rb, ro):
        if storing:
            self.str = f'LD [{rb.name}, {ro.name}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {ro.name}]'
        self._dec = 6,int(storing),0,0,ro,rb,rd
        self._bin = '110',str(int(storing)),'0','XX',f'{ro:03b}',f'{rb:03b}',f'{rd:03b}'
class Load1(Inst):
    def __init__(self, storing, rd, rb, offset5):
        assert -16 <= offset5 < 16
        if storing:
            self.str = f'LD [{rb.name}, {offset5}], {rd.name}'
        else:
            self.str = f'LD {rd.name}, [{rb.name}, {offset5}]'
        self._dec = 6,int(storing),1,offset5,rb,rd
        if offset5 < 0:
            offset5 = negative(offset5, 5)
        self._bin = '110',str(int(storing)),'1',f'{offset5:05b}',f'{rb:03b}',f'{rd:03b}'    
class Imm(Inst):
    def __init__(self, rd):
        self.str = f'LD {rd.name}'
        self._dec = 7,0,rd
        self._bin = '111','XXXXXXXXXX',f'{rd:03b}'
