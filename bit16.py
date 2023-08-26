# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 19:28:14 2023

@author: ccslon
"""
from enum import IntEnum
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
    JMP = 0
    JEQ = 1
    JNE = 2
    JGT = 3
    JLT = 4
    JGE = 5
    JLE = 6
    JNV = 7
    
class Inst:     
    def int(self):
        return int(''.join(self.bin).replace('X','0'), base=2)    
    def hex(self):
        return f'{self.int():04x}'    

class Nop(Inst):
    def __init__(self):
        self.bin = '000','XXXXXXXXXXXXX'
class Inst1(Inst):
    def __init__(self, op, rd, rs):
        self.bin = '001',f'{op:04b}','XXX',f'{rs:03b}',f'{rd:03b}'
class Inst2(Inst):
    def __init__(self, op, rd, const6):
        self.bin = '010',f'{op:04b}',f'{const6:06b}',f'{rd:03b}'
class Inst3(Inst):
    def __init__(self, op, rd, rs, rs2):
        self.bin = '011',f'{op:03b}','X',f'{rs2:03b}',f'{rs:03b}',f'{rd:03b}'
class Inst4(Inst):
    def __init__(self, op, rd, rs, const4):
        self.bin = '100',f'{op:03b}',f'{const4:04b}',f'{rs:03b}',f'{rd:03b}'
class Inst5(Inst):
    def __init__(self, op, rd):
        self.bin = '101',f'{op:01b}','XXXXXXXXX',f'{rd:03b}'        
class Load0(Inst):
    def __init__(self, storing, rd, rb, ro):
        self.bin = '110',str(int(storing)),'0','XX',f'{ro:03b}',f'{rb:03b}',f'{rd:03b}'
class Load1(Inst):
    def __init__(self, storing, rd, rb, offset5):
        if offset5 < 0:
            offset5 = (-offset5 ^ (2**5 - 1)) + 1
        self.bin = '110',str(int(storing)),'1',f'{offset5:05b}',f'{rb:03b}',f'{rd:03b}'    
class Jump(Inst):
    def __init__(self, cond, const10):
        self.bin = '111', f'{cond:03b}', f'{const10:010b}'