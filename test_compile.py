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
  PSH A
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
MULTI = '''
multi() {
    foo = 3
    bar = 2 - foo
    baz = bar + foo * 4
}
'''


'''
baz = bar + foo * 4
bif = -(foo + bar) * (baz + 10)
foo = 3 * foo


a * 2
LD A, [SP, 0]
MUL A, 2

2 * a
MOV A, 2
LD B, [SP, 0]
MUL A, B
'''

MULTI_ASM = '''
nonsense:
  PSH A, B
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

if __name__ == '__main__':
    main()