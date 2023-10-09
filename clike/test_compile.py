# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 14:37:22 2023

@author: ccslon
"""

from unittest import TestCase, main
import parse

MAIN = '''
main() {
}
'''
MAIN_ASM = '''
  HALT
'''

CONST = '''
const() {
    foo = 3
}
'''
CONST_ASM = '''
const:
  PUSH A
  SUB SP, 1
  MOV A, 3
  LD [SP, 0], A
  ADD SP, 1
  POP A
  RET
'''

RCONST = '''
rconst() {
    foo = 3
    bar = 2 - foo
}
'''
RCONST_ASM = '''
rconst:
  PUSH A, B
  SUB SP, 2
  MOV A, 3
  LD [SP, 0], A
  MOV A, 2
  LD B, [SP, 0]
  SUB A, B
  LD [SP, 1], A
  ADD SP, 2
  POP A, B
  RET
'''

MULTI = '''
multi() {
    foo = 3
    bar = 2 - foo
    baz = bar + foo * 4
}
'''
MULTI_ASM = '''
multi:
  PUSH A, B
  SUB SP, 3
  MOV A, 3
  LD [SP, 0], A
  MOV A, 2
  LD B, [SP, 0]
  SUB A, B
  LD [SP, 1], A
  LD A, [SP, 1]
  LD B, [SP, 0]
  MUL B, 4
  ADD A, B
  LD [SP, 2], A
  ADD SP, 3
  POP A, B
  RET
'''

PAREN = '''
paren() {
    foo = 3
    bar = 2 - foo
    baz = bar + foo * 4
    bif = -(foo + bar) * (baz + 10)
}
'''
PAREN_ASM = '''
paren:
  PUSH A, B
  SUB SP, 4
  MOV A, 3
  LD [SP, 0], A
  MOV A, 2
  LD B, [SP, 0]
  SUB A, B
  LD [SP, 1], A
  LD A, [SP, 1]
  LD B, [SP, 0]
  MUL B, 4
  ADD A, B
  LD [SP, 2], A
  LD A, [SP, 0]
  LD B, [SP, 1]
  ADD A, B
  NEG A
  LD B, [SP, 2]
  ADD B, 10
  MUL A, B
  LD [SP, 3], A
  ADD SP, 4
  POP A, B
  RET
'''

PARAMS = '''
add3(foo, bar, baz) {
    return foo + bar + baz
}
'''
PARAMS_ASM = '''
add3:
  SUB SP, 3
  LD [SP, 0], A
  LD [SP, 1], B
  LD [SP, 2], C
  LD A, [SP, 0]
  LD B, [SP, 1]
  ADD A, B
  LD B, [SP, 2]
  ADD A, B
  JR .L0
.L0:
  ADD SP, 3
  RET
'''

FACT = '''
fact(n) {
    if n == 0 {
        return 1
    }
    return n * fact(n-1)
}
'''
FACT_ASM = '''
fact:
  PUSH LR, B, C
  SUB SP, 1
  LD [SP, 0], A
  LD B, [SP, 0]
  CMP B, 0
  JNE .L1
  MOV B, 1
  JR .L0
  LD B, [SP, 0]
  LD C, [SP, 0]
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

FIB = '''
fib(n) {
    if n == 1 {
        return 0
    } else if n == 2 {
        return 1
    } else {
        return fib(n-1) + fib(n-2)
    }
}
'''
FIB_ASM = '''
fib:
  PUSH LR, B, C
  SUB SP, 1
  LD [SP, 0], A
  LD B, [SP, 0]
  CMP B, 1
  JNE .L2
  MOV B, 0
  JR .L0
.L2:
  LD B, [SP, 0]
  CMP B, 2
  JNE .L3
  MOV B, 1
  JR .L0
.L3:
  LD B, [SP, 0]
  SUB B, 1
  MOV A, B
  CALL fib
  MOV B, A
  LD C, [SP, 0]
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

SUM = '''
sum(n) {
    s = 0
    for i = 0, i < n, i = i + 1 {
        s = s + i
    }
    return s
}
'''
SUM_ASM = '''
sum:
  PUSH B
  SUB SP, 3
  LD [SP, 0], A
  MOV A, 0
  LD [SP, 1], A
  MOV A, 0
  LD [SP, 2], A
.L1:
  LD A, [SP, 2]
  LD B, [SP, 0]
  CMP A, B
  JGE .L2
  LD A, [SP, 1]
  LD B, [SP, 2]
  ADD A, B
  LD [SP, 1], A
  LD A, [SP, 2]
  ADD A, 1
  LD [SP, 2], A
  JR .L1
.L2:
  LD A, [SP, 1]
  JR .L0
.L0:
  ADD SP, 3
  POP B
  RET
'''

GETSET = '''
get(g, i) {
    return g[i]
}
set(g, i, t) {
    g[i] = t
}
'''
GETSET_ASM = '''
get:
  SUB SP, 2
  LD [SP, 0], A
  LD [SP, 1], B
  LD A, [SP, 0]
  LD B, [SP, 1]
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
  LD A, [SP, 2]
  LD B, [SP, 0]
  LD C, [SP, 1]
  ADD B, C
  LD [B], A
  ADD SP, 3
  RET
'''

GETSET2 = '''
get2(g, i, j) {
    return g[i][j]
}
set2(g, i, j, t) {
    g[i][j] = t
}
'''
GETSET2_ASM = '''
get2:
  SUB SP, 3
  LD [SP, 0], A
  LD [SP, 1], B
  LD [SP, 2], C
  LD A, [SP, 0]
  LD B, [SP, 1]
  ADD A, B
  LD A, [A]
  LD B, [SP, 2]
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
  LD A, [SP, 3]
  LD B, [SP, 0]
  LD C, [SP, 1]
  ADD B, C
  LD B, [B]
  LD C, [SP, 2]
  ADD B, C
  LD [B], A
  ADD SP, 4
  RET
'''
CALLS = '''
foo (x,y,z) {
    return bar(x,y) + baz(y,z)
}
'''
CALLS_ASM = '''
foo:
  PUSH LR, D, E
  SUB SP, 3
  LD [SP, 0], A
  LD [SP, 1], B
  LD [SP, 2], C
  LD C, [SP, 0]
  LD D, [SP, 1]
  MOV A, C
  MOV B, D
  CALL bar
  MOV C, A
  LD D, [SP, 1]
  LD E, [SP, 2]
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

class TestCompiler(TestCase):
    
    def code_eq_asm(self, CODE, ASM):
        ast = parse.Parser().parse(CODE)
        asm = ast.compile()
        self.assertEqual(asm, ASM.strip('\n'))
    
    def test_init(self):
        self.code_eq_asm('', '')
        
    def test_main(self):
        self.code_eq_asm(MAIN, MAIN_ASM)
        
    def test_const(self):
        self.code_eq_asm(CONST, CONST_ASM)
        
    def test_rconst(self):
        self.code_eq_asm(RCONST, RCONST_ASM)
        
    def test_multi(self):
        self.code_eq_asm(MULTI, MULTI_ASM)
    
    def test_paren1(self):
        self.code_eq_asm(PAREN, PAREN_ASM)
        
    def test_params(self):
        self.code_eq_asm(PARAMS, PARAMS_ASM)
        
    def test_fact(self):
        self.code_eq_asm(FACT, FACT_ASM)
        
    def test_fib(self):
        self.code_eq_asm(FIB, FIB_ASM)
        
    def test_sum(self):
        self.code_eq_asm(SUM, SUM_ASM)
        
    def test_getset(self):
        self.code_eq_asm(GETSET, GETSET_ASM)
        
    def test_getset2(self):
        self.code_eq_asm(GETSET2, GETSET2_ASM)
    
    def test_calls(self):
        self.code_eq_asm(CALLS, CALLS_ASM)

if __name__ == '__main__':
    main()