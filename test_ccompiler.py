# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 14:37:22 2023

@author: ccslon
"""

from unittest import TestCase, main
import cparser

MAIN_ASM = '''
  HALT
'''
CONST_ASM = '''
const:
  PUSH A
  SUB SP, 1
  MOV A, 3
  LD [SP, 0], A ; foo
  ADD SP, 1
  POP A
  RET
'''
RCONST_ASM = '''
rconst:
  PUSH A, B
  SUB SP, 2
  MOV A, 3
  LD [SP, 0], A ; foo
  MOV A, 2
  LD B, [SP, 0] ; foo
  SUB A, B
  LD [SP, 1], A ; bar
  ADD SP, 2
  POP A, B
  RET
'''
MULTI_ASM = '''
multi:
  PUSH A, B
  SUB SP, 3
  MOV A, 3
  LD [SP, 0], A ; foo
  MOV A, 2
  LD B, [SP, 0] ; foo
  SUB A, B
  LD [SP, 1], A ; bar
  LD A, [SP, 1] ; bar
  LD B, [SP, 0] ; foo
  MUL B, 4
  ADD A, B
  LD [SP, 2], A ; baz
  ADD SP, 3
  POP A, B
  RET
'''
PAREN_ASM = '''
paren:
  PUSH A, B
  SUB SP, 4
  MOV A, 3
  LD [SP, 0], A ; foo
  MOV A, 2
  LD B, [SP, 0] ; foo
  SUB A, B
  LD [SP, 1], A ; bar
  LD A, [SP, 1] ; bar
  LD B, [SP, 0] ; foo
  MUL B, 4
  ADD A, B
  LD [SP, 2], A ; baz
  LD A, [SP, 0] ; foo
  LD B, [SP, 1] ; bar
  ADD A, B
  NEG A
  LD B, [SP, 2] ; baz
  ADD B, 10
  MUL A, B
  LD [SP, 3], A ; bif
  ADD SP, 4
  POP A, B
  RET
'''
PARAMS_ASM = '''
params:
  SUB SP, 3
  LD [SP, 0], A
  LD [SP, 1], B
  LD [SP, 2], C
  LD A, [SP, 0] ; foo
  LD B, [SP, 1] ; bar
  ADD A, B
  LD B, [SP, 2] ; baz
  ADD A, B
  JR .L0
.L0:
  ADD SP, 3
  RET
'''
FACT_ASM = '''
fact:
  PUSH LR, B, C
  SUB SP, 1
  LD [SP, 0], A
  LD B, [SP, 0] ; n
  CMP B, 0
  JNE .L1
  MOV B, 1
  JR .L0
  LD B, [SP, 0] ; n
  LD C, [SP, 0] ; n
  SUB C, 1
  MOV A, C
  CALL fact
  MOV C, A
  MUL B, C
  JR .L0
.L0:
  MOV A, B
  ADD SP, 1
  POP PC, B, C
'''
FIB_ASM = '''
fib:
  PUSH LR, B, C
  SUB SP, 1
  LD [SP, 0], A
  LD B, [SP, 0] ; n
  CMP B, 1
  JNE .L2
  MOV B, 0
  JR .L0
.L2:
  LD B, [SP, 0] ; n
  CMP B, 2
  JNE .L3
  MOV B, 1
  JR .L0
.L3:
  LD B, [SP, 0] ; n
  SUB B, 1
  MOV A, B
  CALL fib
  MOV B, A
  LD C, [SP, 0] ; n
  SUB C, 2
  MOV A, C
  CALL fib
  MOV C, A
  ADD B, C
  JR .L0
.L0:
  MOV A, B
  ADD SP, 1
  POP PC, B, C
'''
SUM_ASM = '''
sum:
  PUSH B
  SUB SP, 3
  LD [SP, 0], A
  MOV A, 0
  LD [SP, 1], A ; s
  MOV A, 0
  LD [SP, 2], A ; i
.L1:
  LD A, [SP, 2] ; i
  LD B, [SP, 0] ; n
  CMP A, B
  JGE .L2
  LD A, [SP, 1] ; s
  LD B, [SP, 2] ; i
  ADD A, B
  LD [SP, 1], A ; s
  LD A, [SP, 2] ; i
  ADD A, 1
  LD [SP, 2], A ; i
  JR .L1
.L2:
  LD A, [SP, 1] ; s
  JR .L0
.L0:
  ADD SP, 3
  POP B
  RET
'''
GETSET_ASM = '''
get:
  SUB SP, 2
  LD [SP, 0], A
  LD [SP, 1], B
  LD A, [SP, 0] ; g
  LD B, [SP, 1] ; i
  ADD A, B
  LD A, [A]
  JR .L0
.L0:
  ADD SP, 2
  RET
set:
  SUB SP, 3
  LD [SP, 0], A
  LD [SP, 1], B
  LD [SP, 2], C
  LD A, [SP, 2] ; t
  LD B, [SP, 0] ; g
  LD C, [SP, 1] ; i
  ADD B, C
  LD [B], A
  ADD SP, 3
  RET
'''
GETSET2_ASM = '''
get2:
  SUB SP, 3
  LD [SP, 0], A
  LD [SP, 1], B
  LD [SP, 2], C
  LD A, [SP, 0] ; g
  LD B, [SP, 1] ; i
  ADD A, B
  LD A, [A]
  LD B, [SP, 2] ; j
  ADD A, B
  LD A, [A]
  JR .L0
.L0:
  ADD SP, 3
  RET
set2:
  SUB SP, 4
  LD [SP, 0], A
  LD [SP, 1], B
  LD [SP, 2], C
  LD [SP, 3], D
  LD A, [SP, 3] ; t
  LD B, [SP, 0] ; g
  LD C, [SP, 1] ; i
  ADD B, C
  LD B, [B]
  LD C, [SP, 2] ; j
  ADD B, C
  LD [B], A
  ADD SP, 4
  RET
'''
CALLS_ASM = '''
foo:
  PUSH LR, D, E
  SUB SP, 3
  LD [SP, 0], A
  LD [SP, 1], B
  LD [SP, 2], C
  LD C, [SP, 0] ; x
  LD D, [SP, 1] ; y
  MOV A, C
  MOV B, D
  CALL bar
  MOV C, A
  LD D, [SP, 1] ; y
  LD E, [SP, 2] ; z
  MOV A, D
  MOV B, E
  CALL baz
  MOV D, A
  ADD C, D
  JR .L0
.L0:
  MOV A, C
  ADD SP, 3
  POP PC, D, E
'''
HELLO_ASM = '''
.S0: "Hello world!\0"
  LD B, =.S0
  MOV A, B
  CALL print
  MOV B, A
  HALT
OUT: 32767
put:
  SUB SP, 1
  LD [SP, 0], A
  LD A, [SP, 0] ; c
  LD B, =OUT
  LD B, [B]
  LD [B], A
  ADD SP, 1
  RET
print:
  PUSH LR, B, C
  SUB SP, 1
  LD [SP, 0], A
.L0:
  LD B, [SP, 0] ; str
  LD B, [B]
  LD C, '\\0'
  CMP B, C
  JEQ .L1
  LD B, [SP, 0] ; str
  LD B, [B]
  MOV A, B
  CALL put
  MOV B, A
  LD B, [SP, 0] ; str
  ADD B, 1
  LD [SP, 0], B ; str
  JR .L0
.L1:
  ADD SP, 1
  POP PC, B, C
'''

ARRAY_ASM = '''
foo:
  PUSH A, B, C
  SUB SP, 6
  MOV A, 2
  LD [SP, 5], A ; i
  MOV A, 2
  ADD B, SP, 0
  LD C, [SP, 5] ; i
  ADD B, C
  LD [B], A
  ADD SP, 6
  POP A, B, C
  RET
'''

class TestCompiler(TestCase):
    
    def code_eq_asm(self, FILE_NAME, ASM):
        if FILE_NAME.endswith('.c'):
            with open(r'tests/' + FILE_NAME) as in_file:
                text = in_file.read()
        ast = cparser.parse(text)
        asm = ast.compile()
        self.assertEqual(asm, ASM.strip('\n'))
    
    def test_init(self):
        self.code_eq_asm('init.c', '')
        
    def test_main(self):
        self.code_eq_asm('main.c', MAIN_ASM)
        
    def test_const(self):
        self.code_eq_asm('const.c', CONST_ASM)
        
    def test_rconst(self):
        self.code_eq_asm('rconst.c', RCONST_ASM)
        
    def test_multi(self):
        self.code_eq_asm('multi.c', MULTI_ASM)
    
    def test_paren1(self):
        self.code_eq_asm('paren.c', PAREN_ASM)
        
    def test_params(self):
        self.code_eq_asm('params.c', PARAMS_ASM)
        
    def test_fact(self):
        self.code_eq_asm('fact.c', FACT_ASM)
        
    def test_fib(self):
        self.code_eq_asm('fib.c', FIB_ASM)
        
    def test_sum(self):
        self.code_eq_asm('sum.c', SUM_ASM)
        
    def test_getset(self):
        self.code_eq_asm('getset.c', GETSET_ASM)
        
    def test_getset2(self):
        self.code_eq_asm('getset2.c', GETSET2_ASM)
    
    def test_calls(self):
        self.code_eq_asm('calls.c', CALLS_ASM)
        
    def test_hello(self):
        self.code_eq_asm('hello.c', HELLO_ASM)
        
    def test_array(self):
        self.code_eq_asm('array.c', ARRAY_ASM)

if __name__ == '__main__':
    main()