# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 14:37:22 2023

@author: ccslon
"""
import os
from unittest import TestCase, main
import cpreproc
import cparser

MAIN_ASM = '''
main:
  MOV FP, SP
  MOV SP, FP
  HALT
'''
CONST_ASM = '''
foo:
  PUSH A, FP
  SUB SP, 1
  MOV FP, SP
  MOV A, 3
  LD [FP, 0], A ; foo
  MOV SP, FP
  ADD SP, 1
  POP A, FP
  RET
'''
RCONST_ASM = '''
rconst:
  PUSH A, B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 3
  LD [FP, 0], A ; foo
  MOV A, 2
  LD B, [FP, 0] ; foo
  SUB A, B
  LD [FP, 1], A ; bar
  MOV SP, FP
  ADD SP, 2
  POP A, B, FP
  RET
'''
MULTI_ASM = '''
multi:
  PUSH A, B, FP
  SUB SP, 3
  MOV FP, SP
  MOV A, 3
  LD [FP, 0], A ; foo
  MOV A, 2
  LD B, [FP, 0] ; foo
  SUB A, B
  LD [FP, 1], A ; bar
  LD A, [FP, 1] ; bar
  LD B, [FP, 0] ; foo
  MUL B, 4
  ADD A, B
  LD [FP, 2], A ; baz
  MOV SP, FP
  ADD SP, 3
  POP A, B, FP
  RET
'''
PAREN_ASM = '''
paren:
  PUSH A, B, FP
  SUB SP, 4
  MOV FP, SP
  MOV A, 3
  LD [FP, 0], A ; foo
  MOV A, 2
  LD B, [FP, 0] ; foo
  SUB A, B
  LD [FP, 1], A ; bar
  LD A, [FP, 1] ; bar
  LD B, [FP, 0] ; foo
  MUL B, 4
  ADD A, B
  LD [FP, 2], A ; baz
  LD A, [FP, 0] ; foo
  LD B, [FP, 1] ; bar
  ADD A, B
  NEG A
  LD B, [FP, 2] ; baz
  ADD B, 10
  MUL A, B
  LD [FP, 3], A ; bif
  MOV SP, FP
  ADD SP, 4
  POP A, B, FP
  RET
'''
PARAMS_ASM = '''
params0:
  PUSH FP
  MOV FP, SP
  MOV A, 0
  JR .L0
.L0:
  MOV SP, FP
  POP FP
  RET
params1:
  PUSH FP
  MOV FP, SP
  LD A, [FP, 1] ; foo
  JR .L1
.L1:
  MOV SP, FP
  POP FP
  ADD SP, 1
  RET
params2:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; foo
  LD B, [FP, 3] ; bar
  ADD A, B
  JR .L2
.L2:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
params3:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; foo
  LD B, [FP, 3] ; bar
  ADD A, B
  LD B, [FP, 4] ; baz
  ADD A, B
  JR .L3
.L3:
  MOV SP, FP
  POP B, FP
  ADD SP, 3
  RET
'''
FACT_ASM = '''
fact:
  PUSH LR, B, C, FP
  MOV FP, SP
  LD B, [FP, 4] ; n
  CMP B, 0
  JNE .L1
  MOV B, 1
  JR .L0
.L1:
  LD B, [FP, 4] ; n
  LD C, [FP, 4] ; n
  SUB C, 1
  PUSH C
  CALL fact
  MOV C, A
  MUL B, C
  JR .L0
.L0:
  MOV A, B
  MOV SP, FP
  POP LR, B, C, FP
  ADD SP, 1
  RET
'''
FIB_ASM = '''
fib:
  PUSH LR, B, C, FP
  MOV FP, SP
  LD B, [FP, 4] ; n
  CMP B, 1
  JNE .L2
  MOV B, 0
  JR .L0
.L2:
  LD B, [FP, 4] ; n
  CMP B, 2
  JNE .L3
  MOV B, 1
  JR .L0
.L3:
  LD B, [FP, 4] ; n
  SUB B, 1
  PUSH B
  CALL fib
  MOV B, A
  LD C, [FP, 4] ; n
  SUB C, 2
  PUSH C
  CALL fib
  MOV C, A
  ADD B, C
  JR .L0
.L0:
  MOV A, B
  MOV SP, FP
  POP LR, B, C, FP
  ADD SP, 1
  RET
fib2:
  PUSH LR, B, C, FP
  MOV FP, SP
  LD B, [FP, 4] ; n
  CMP B, 1
  JEQ .L7
  CMP B, 2
  JEQ .L8
  JR .L9
.L7:
  MOV B, 0
  JR .L4
.L8:
  MOV B, 1
  JR .L4
.L9:
  LD B, [FP, 4] ; n
  SUB B, 1
  PUSH B
  CALL fib
  MOV B, A
  LD C, [FP, 4] ; n
  SUB C, 2
  PUSH C
  CALL fib
  MOV C, A
  ADD B, C
  JR .L4
.L6:
.L4:
  MOV A, B
  MOV SP, FP
  POP LR, B, C, FP
  ADD SP, 1
  RET
'''
SUM_ASM = '''
sum:
  PUSH B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 0
  LD [FP, 0], A ; s
  MOV A, 0
  LD [FP, 1], A ; i
.L1:
  LD A, [FP, 1] ; i
  LD B, [FP, 4] ; n
  CMP A, B
  JGE .L3
  LD A, [FP, 0] ; s
  LD B, [FP, 1] ; i
  ADD A, B
  LD [FP, 0], A ; s
.L2:
  LD A, [FP, 1] ; i
  ADD B, A, 1
  LD [FP, 1], B ; i
  JR .L1
.L3:
  LD A, [FP, 0] ; s
  JR .L0
.L0:
  MOV SP, FP
  ADD SP, 2
  POP B, FP
  ADD SP, 1
  RET
'''
GETSET_ASM = '''
get:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; g
  LD B, [FP, 3] ; i
  ADD A, B
  LD A, [A]
  JR .L0
.L0:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
set:
  PUSH A, B, C, FP
  MOV FP, SP
  LD A, [FP, 6] ; t
  LD B, [FP, 4] ; g
  LD C, [FP, 5] ; i
  ADD B, C
  LD [B], A
  MOV SP, FP
  POP A, B, C, FP
  ADD SP, 3
  RET
'''
GETSET2_ASM = '''
get2:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; g
  LD B, [FP, 3] ; i
  ADD A, B
  LD A, [A]
  LD B, [FP, 4] ; j
  ADD A, B
  LD A, [A]
  JR .L0
.L0:
  MOV SP, FP
  POP B, FP
  ADD SP, 3
  RET
set2:
  PUSH A, B, C, FP
  MOV FP, SP
  LD A, [FP, 7] ; t
  LD B, [FP, 4] ; g
  LD C, [FP, 5] ; i
  ADD B, C
  LD B, [B]
  LD C, [FP, 6] ; j
  ADD B, C
  LD [B], A
  MOV SP, FP
  POP A, B, C, FP
  ADD SP, 4
  RET
'''
CALLS_ASM = '''
baz:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; y
  LD B, [FP, 3] ; z
  MUL A, B
  JR .L0
.L0:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
bar:
  PUSH B, FP
  MOV FP, SP
  LD A, [FP, 2] ; x
  LD B, [FP, 3] ; y
  MUL A, B
  JR .L1
.L1:
  MOV SP, FP
  POP B, FP
  ADD SP, 2
  RET
foo:
  PUSH LR, B, C, FP
  MOV FP, SP
  LD B, [FP, 5] ; y
  PUSH B
  LD B, [FP, 4] ; x
  PUSH B
  CALL bar
  MOV B, A
  LD C, [FP, 6] ; z
  PUSH C
  LD C, [FP, 5] ; y
  PUSH C
  CALL baz
  MOV C, A
  ADD B, C
  JR .L2
.L2:
  MOV A, B
  MOV SP, FP
  POP LR, B, C, FP
  ADD SP, 3
  RET
'''
HELLO_ASM = '''
.S0: "Hello world!\\n\\0"
main:
  MOV FP, SP
  LD B, =.S0
  PUSH B
  CALL printf
  MOV B, A
  MOV SP, FP
  HALT
'''
ARRAY_ASM = '''
foo:
  PUSH A, B, C, FP
  SUB SP, 9
  MOV FP, SP
  MOV A, 2
  LD [FP, 5], A ; i
  MOV A, 2
  ADD B, FP, 0
  LD C, [FP, 5] ; i
  ADD B, C
  LD [B], A
  ADD A, FP, 6
  MOV B, 1
  LD [A, 0], B
  MOV B, 2
  LD [A, 1], B
  MOV B, 3
  LD [A, 2], B
  MOV SP, FP
  ADD SP, 9
  POP A, B, C, FP
  RET
'''
STRUCTS_ASM = '''
.S0: "Cloud\\0"
.S1: "Colin\\0"
.S2: "ccslon@gmail.com\\0"
.S3: "ccs@email.com\\0"
.S4: "Nick\\0"
.S5: "nickel@email.com\\0"
.S6: "Nicole\\0"
stack_cat:
  PUSH A, B, FP
  SUB SP, 6
  MOV FP, SP
  MOV A, 10
  ADD B, FP, 0
  LD [B, 1], A ; age
  LD A, =.S0
  ADD B, FP, 0
  LD [B, 0], A ; name
  LD A, =.S1
  ADD B, FP, 0
  ADD B, 2
  LD [B, 0], A ; name
  LD A, =.S2
  ADD B, FP, 0
  ADD B, 2
  LD [B, 1], A ; email
  ADD A, FP, 0
  LD A, [A, 1] ; age
  LD [FP, 4], A ; age
  ADD A, FP, 0
  ADD A, 2
  LD A, [A, 0] ; name
  LD [FP, 5], A ; name
  MOV SP, FP
  ADD SP, 6
  POP A, B, FP
  RET
init_cat:
  PUSH A, B, FP
  SUB SP, 6
  MOV FP, SP
  ADD A, FP, 0
  LD B, =.S1
  LD [A, 0], B
  LD B, =.S3
  LD [A, 1], B
  ADD A, FP, 2
  LD B, [FP, 9] ; name
  LD [A, 0], B
  MOV B, 10
  LD [A, 1], B
  LD B, =.S1
  LD [A, 2], B
  LD B, =.S3
  LD [A, 3], B
  MOV SP, FP
  ADD SP, 6
  POP A, B, FP
  ADD SP, 1
  RET
array:
  PUSH A, B, C, FP
  SUB SP, 5
  MOV FP, SP
  ADD A, FP, 0
  LD B, =.S1
  LD [A, 0], B
  LD B, =.S3
  LD [A, 1], B
  LD B, =.S4
  LD [A, 2], B
  LD B, =.S5
  LD [A, 3], B
  ADD A, FP, 0
  MOV B, 0
  MUL B, 2
  ADD A, B
  LD A, [A, 0] ; name
  LD [FP, 4], A ; name
  LD A, =.S6
  ADD B, FP, 0
  MOV C, 1
  MUL C, 2
  ADD B, C
  LD [B, 0], A ; name
  MOV SP, FP
  ADD SP, 5
  POP A, B, C, FP
  RET
'''
GLOB_STRUCT_ASM = '''
.S0: "Cloud\\0"
.S1: "Colin\\0"
.S2: "Mom\\0"
owners:
  .S1
  34
  .S2
  21
cats: space 9
name: "Cats Ya!\\0"
num: 69
main:
  SUB SP, 1
  MOV FP, SP
  LD B, =cats
  MOV C, 0
  MUL C, 3
  ADD B, C
  LD [FP, 0], B ; cat1
  LD B, =.S0
  LD C, [FP, 0] ; cat1
  LD [C, 0], B ; name
  MOV B, 10
  LD C, [FP, 0] ; cat1
  LD [C, 1], B ; age
  LD B, =owners
  MOV C, 0
  MUL C, 2
  ADD B, C
  LD C, [FP, 0] ; cat1
  LD [C, 2], B ; owner
  LD B, [FP, 0] ; cat1
  PUSH B
  CALL print_cat
  MOV B, A
  MOV SP, FP
  ADD SP, 1
  HALT
print_cat:
  PUSH A, FP
  SUB SP, 5
  MOV FP, SP
  LD A, =name
  LD [FP, 0], A ; store
  LD A, =num
  LD A, [A]
  LD [FP, 1], A ; n
  LD A, [FP, 7] ; cat
  LD A, [A, 0] ; name
  LD [FP, 2], A ; mycat
  LD A, [FP, 7] ; cat
  LD A, [A, 1] ; age
  LD [FP, 3], A ; age
  LD A, [FP, 7] ; cat
  LD A, [A, 2] ; owner
  LD A, [A, 0] ; name
  LD [FP, 4], A ; owner
  MOV SP, FP
  ADD SP, 5
  POP A, FP
  ADD SP, 1
  RET
'''
GOTO_ASM = '''
foo:
  PUSH FP
  MOV FP, SP
  LD A, [FP, 1] ; bar
  CMP A, 3
  JLE .L1
  MOV A, 3
  LD [FP, 1], A ; bar
  JR baz
.L1:
  LD A, [FP, 1] ; bar
  MUL A, 3
  LD [FP, 1], A ; bar
baz:
  LD A, [FP, 1] ; bar
  JR .L0
.L0:
  MOV SP, FP
  POP FP
  ADD SP, 1
  RET
'''
RETURN_STRUCT_ASM = '''
div:
  PUSH B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 3
  ADD B, FP, 0
  LD [B, 0], A ; quot
  MOV A, 4
  ADD B, FP, 0
  LD [B, 1], A ; rem
  ADD A, FP, 0
  JR .L0
.L0:
  MOV SP, FP
  ADD SP, 2
  POP B, FP
  ADD SP, 2
  RET
print_int:
  PUSH LR, A, B, C, D, FP
  SUB SP, 2
  MOV FP, SP
  MOV B, 10
  PUSH B
  LD B, [FP, 8] ; num
  PUSH B
  CALL div
  MOV B, A
  ADD C, FP, 0
  LD D, [B, 0]
  LD [C, 0], D
  LD D, [B, 1]
  LD [C, 1], D
  MOV SP, FP
  ADD SP, 2
  POP LR, A, B, C, D, FP
  ADD SP, 1
  RET
'''
POINTERS_ASM = '''
change:
  PUSH A, B, FP
  MOV FP, SP
  LD A, [FP, 3] ; n
  LD A, [A]
  ADD A, 10
  LD B, [FP, 3] ; n
  LD [B], A
  MOV SP, FP
  POP A, B, FP
  ADD SP, 1
  RET
foo:
  PUSH LR, A, B, FP
  SUB SP, 1
  MOV FP, SP
  LD B, [FP, 5] ; m
  MUL B, 5
  LD [FP, 0], B ; n
  ADD B, FP, 0
  PUSH B
  CALL change
  MOV B, A
  MOV SP, FP
  ADD SP, 1
  POP LR, A, B, FP
  ADD SP, 1
  RET
print:
  PUSH FP
  MOV FP, SP
  MOV SP, FP
  POP FP
  ADD SP, 1
  RET
bar:
  PUSH LR, A, B, C, FP
  MOV FP, SP
  LD B, [FP, 5] ; str
  PUSH B
  CALL print
  MOV B, A
  LD B, [FP, 5] ; str
  LD C, [FP, 6] ; i
  ADD B, C
  PUSH B
  CALL print
  MOV B, A
  MOV SP, FP
  POP LR, A, B, C, FP
  ADD SP, 2
  RET
'''
DEFINES_ASM = '''
test:
  PUSH A, B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 0
  LD [FP, 0], A ; i
.L0:
  LD A, [FP, 0] ; i
  CMP A, 10
  JGE .L2
  LD A, [FP, 1] ; minN
  LD B, [FP, 0] ; i
  CMP A, B
  JLE .L4
  LD A, [FP, 0] ; i
  JR .L3
.L4:
  LD A, [FP, 1] ; minN
.L3:
  LD [FP, 1], A ; minN
  LD A, [FP, 1] ; minN
  ADD B, A, 1
  LD [FP, 1], B ; minN
.L1:
  LD A, [FP, 0] ; i
  ADD B, A, 1
  LD [FP, 0], B ; i
  JR .L0
.L2:
  MOV SP, FP
  ADD SP, 2
  POP A, B, FP
  RET
'''
INCLUDES_ASM = '''
foo: 9
test:
  PUSH A, B, FP
  SUB SP, 1
  MOV FP, SP
  MOV A, 10
  LD B, 100
  MUL A, B
  LD [FP, 0], A ; num
  MOV SP, FP
  ADD SP, 1
  POP A, B, FP
  RET
'''
ENUMS_ASM = '''
main:
  SUB SP, 2
  MOV FP, SP
  MOV A, 10
  LD [FP, 0], A ; day
  MOV A, 4
  LD [FP, 1], A ; today
  MOV SP, FP
  ADD SP, 2
  HALT
'''
UNIONS_ASM = '''
.S0: "Hello!\\0"
.S1: "(STR, %s)\\0"
.S2: "(NUM, %d)\\0"
main:
  SUB SP, 4
  MOV FP, SP
  MOV B, 5
  PUSH B
  CALL intToken
  MOV B, A
  ADD C, FP, 0
  LD D, [B, 0]
  LD [C, 0], D
  LD D, [B, 1]
  LD [C, 1], D
  ADD B, FP, 0
  PUSH B
  CALL printToken
  MOV B, A
  LD B, =.S0
  PUSH B
  CALL strToken
  MOV B, A
  ADD C, FP, 2
  LD D, [B, 0]
  LD [C, 0], D
  LD D, [B, 1]
  LD [C, 1], D
  ADD B, FP, 2
  PUSH B
  CALL printToken
  MOV B, A
  MOV SP, FP
  ADD SP, 4
  HALT
intToken:
  PUSH B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 1
  ADD B, FP, 0
  LD [B, 0], A ; type
  LD A, [FP, 4] ; num
  ADD B, FP, 0
  ADD B, 1
  LD [B, 0], A ; num
  ADD A, FP, 0
  JR .L0
.L0:
  MOV SP, FP
  ADD SP, 2
  POP B, FP
  ADD SP, 1
  RET
strToken:
  PUSH B, FP
  SUB SP, 2
  MOV FP, SP
  MOV A, 0
  ADD B, FP, 0
  LD [B, 0], A ; type
  LD A, [FP, 4] ; str
  ADD B, FP, 0
  ADD B, 1
  LD [B, 0], A ; str
  ADD A, FP, 0
  JR .L1
.L1:
  MOV SP, FP
  ADD SP, 2
  POP B, FP
  ADD SP, 1
  RET
printToken:
  PUSH LR, A, B, FP
  MOV FP, SP
  LD B, [FP, 4] ; token
  LD B, [B, 0] ; type
  CMP B, 0
  JEQ .L4
  CMP B, 1
  JEQ .L5
  JR .L3
.L4:
  LD B, [FP, 4] ; token
  ADD B, 1
  LD B, [B, 0] ; str
  PUSH B
  LD B, =.S1
  PUSH B
  CALL printf
  ADD SP, 1
  MOV B, A
  JR .L3
.L5:
  LD B, [FP, 4] ; token
  ADD B, 1
  LD B, [B, 0] ; num
  PUSH B
  LD B, =.S2
  PUSH B
  CALL printf
  ADD SP, 1
  MOV B, A
  JR .L3
.L3:
  MOV SP, FP
  POP LR, A, B, FP
  ADD SP, 1
  RET
'''
class TestCompiler(TestCase):
    
    def code_eq_asm(self, file_name, target):
        text = cpreproc.preprocess('tests'+os.path.sep+file_name)
        ast = cparser.parse(text)
        asm = ast.generate()
        self.assertEqual(asm, target.strip('\n'))
    
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
        
    def test_structs(self):
        self.code_eq_asm('structs.c', STRUCTS_ASM)
        
    def test_glob_struct(self):
        self.code_eq_asm('globs.c', GLOB_STRUCT_ASM)
        
    def test_goto(self):
        self.code_eq_asm('goto.c', GOTO_ASM)
    
    def test_return_struct(self):
        self.code_eq_asm('returns.c', RETURN_STRUCT_ASM)
        
    def test_pointers(self):
        self.code_eq_asm('pointers.c', POINTERS_ASM)
        
    def test_defines(self):
        self.code_eq_asm('defines.c', DEFINES_ASM)
    
    def test_includes(self):
        self.code_eq_asm('include.c', INCLUDES_ASM)
    
    def test_enums(self):
        self.code_eq_asm('enums.c', ENUMS_ASM)
        
    def test_unions(self):
        self.code_eq_asm('unions.c', UNIONS_ASM)

if __name__ == '__main__':
    main()