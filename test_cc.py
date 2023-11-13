# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 14:37:22 2023

@author: ccslon
"""

from unittest import TestCase, main
import cc


'''
define int fact(int n)
    t1 = int n
    t2 = int 0
    t1 = int t1 == t2
    if t1 then else .L0


'''
MAIN_ASM = '''
  HALT
'''
CONST_ASM = '''
foo:
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
  LD [SP, 0], A ; foo
  LD [SP, 1], B ; bar
  LD [SP, 2], C ; baz
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
  LD [SP, 0], A ; n
  LD B, [SP, 0] ; n
  CMP B, 0
  JNE .L1
  MOV B, 1
  JR .L0
.L1:
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
  LD [SP, 0], A ; n
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
  ADD B, A, 1
  LD [SP, 2], B ; i
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
  LD [SP, 0], A ; g
  LD [SP, 1], B ; i
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
  LD [SP, 0], A ; g
  LD [SP, 1], B ; i
  LD [SP, 2], C ; t
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
  LD [SP, 0], A ; g
  LD [SP, 1], B ; i
  LD [SP, 2], C ; j
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
  LD [SP, 0], A ; g
  LD [SP, 1], B ; i
  LD [SP, 2], C ; j
  LD [SP, 3], D ; t
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
baz:
  SUB SP, 2
  LD [SP, 0], A ; y
  LD [SP, 1], B ; z
  LD A, [SP, 0] ; y
  LD B, [SP, 1] ; z
  MUL A, B
  JR .L0
.L0:
  ADD SP, 2
  RET
bar:
  SUB SP, 2
  LD [SP, 0], A ; x
  LD [SP, 1], B ; y
  LD A, [SP, 0] ; x
  LD B, [SP, 1] ; y
  MUL A, B
  JR .L1
.L1:
  ADD SP, 2
  RET
foo:
  PUSH LR, D, E
  SUB SP, 3
  LD [SP, 0], A ; x
  LD [SP, 1], B ; y
  LD [SP, 2], C ; z
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
  JR .L2
.L2:
  MOV A, C
  ADD SP, 3
  POP PC, D, E
'''
HELLO_ASM = '''
.S0: "Hello world!\\0"
  LD B, =.S0
  MOV A, B
  CALL puts
  MOV B, A
  HALT
STDOUT: 32767
putchar:
  SUB SP, 1
  LD [SP, 0], A
  LD A, [SP, 0] ; c
  LD B, =STDOUT
  LD B, [B]
  LD [B], A
  MOV A, 0
  JR .L0
.L0:
  ADD SP, 1
  RET
puts:
  PUSH LR, B, C
  SUB SP, 1
  LD [SP, 0], A
.L2:
  LD B, [SP, 0] ; str
  LD B, [B]
  LD C, '\\0'
  CMP B, C
  JEQ .L3
  LD B, [SP, 0] ; str
  LD B, [B]
  MOV A, B
  CALL putchar
  MOV B, A
  LD B, [SP, 0] ; str
  ADD C, B, 1
  LD [SP, 0], C ; str
  JR .L2
.L3:
  LD B, '\\n'
  MOV A, B
  CALL putchar
  MOV B, A
  MOV B, 0
  JR .L1
.L1:
  MOV A, B
  ADD SP, 1
  POP PC, B, C
'''

ARRAY_ASM = '''
foo:
  PUSH A, B, C, D
  SUB SP, 9
  MOV A, 2
  LD [SP, 5], A ; i
  MOV A, 2
  ADD B, SP, 0
  LD C, [SP, 5] ; i
  ADD B, C
  LD [B], A
  MOV A, 1
  MOV B, 2
  MOV C, 3
  ADD D, SP, 6
  LDM D, {A, B, C}
  ADD SP, 9
  POP A, B, C, D
  RET
'''

STRUCTS_ASM = '''
.S0: "Cloud\\0"
.S1: "Colin\\0"
.S2: "ccslon@gmail.com\\0"
stack_cat:
  PUSH A, B
  SUB SP, 6
  MOV A, 10
  ADD B, SP, 0
  LD [B, 1], A ; age
  LD A, =.S0
  ADD B, SP, 0
  LD [B, 0], A ; name
  LD A, =.S1
  ADD B, SP, 0
  ADD B, 2
  LD [B, 0], A ; name
  LD A, =.S2
  ADD B, SP, 0
  ADD B, 2
  LD [B, 1], A ; email
  ADD A, SP, 0
  LD A, [A, 1] ; age
  LD [SP, 4], A ; age
  ADD A, SP, 0
  ADD A, 2
  LD A, [A, 0] ; name
  LD [SP, 5], A ; name
  ADD SP, 6
  POP A, B
  RET
.S3: "ccs@email.com\\0"
init_cat:
  PUSH B, C, D, E
  SUB SP, 7
  LD [SP, 0], A ; name
  LD A, =.S1
  LD B, =.S3
  ADD C, SP, 1
  LDM C, {A, B}
  LD A, [SP, 0] ; name
  MOV B, 10
  LD C, =.S1
  LD D, =.S3
  ADD E, SP, 3
  LDM E, {A, B, C, D}
  ADD SP, 7
  POP B, C, D, E
  RET
.S4: "Nick\\0"
.S5: "nickel@email.com\\0"
.S6: "Nicole\\0"
array:
  PUSH A, B, C, D, E
  SUB SP, 5
  LD A, =.S1
  LD B, =.S3
  LD C, =.S4
  LD D, =.S5
  ADD E, SP, 0
  LDM E, {A, B, C, D}
  ADD A, SP, 0
  MOV B, 0
  MUL B, 2
  ADD A, B
  LD A, [A, 0] ; name
  LD [SP, 4], A ; name
  LD A, =.S6
  ADD B, SP, 0
  MOV C, 1
  MUL C, 2
  ADD B, C
  LD [B, 0], A ; name
  ADD SP, 5
  POP A, B, C, D, E
  RET
'''
GLOB_STRUCT_ASM = '''
  SUB SP, 1
  LD A, 32512
  LD B, =stdout
  LD [B, 0], A ; buffer
  MOV A, 0
  LD B, =stdout
  LD [B, 1], A ; read
  MOV A, 0
  LD B, =stdout
  LD [B, 2], A ; write
  LD A, =stdin
  LD A, [A, 1] ; read
  LD [SP, 0], A ; head
  ADD SP, 1
  HALT
stdout: space 3
stdin:
  32256
  0
  0
'''
GOTO_ASM = '''
foo:
  SUB SP, 1
  LD [SP, 0], A
  LD A, [SP, 0] ; bar
  CMP A, 3
  JLE .L1
  MOV A, 3
  LD [SP, 0], A ; bar
  JR baz
.L1:
  LD A, [SP, 0] ; bar
  MUL A, 3
  LD [SP, 0], A ; bar
baz:
  LD A, [SP, 0] ; bar
  JR .L0
.L0:
  ADD SP, 1
  RET
'''

test = '''
struct Owner {
    int name;
    int phone;
};
struct Cat {
    int name;
    int age;
    struct Owner owner;
};

void test() {
    int foo;
    int bar = 9;
    foo = 8;
    int baz = foo + -bar;
    {
     char foo;
     foo = 'g';
    }
    foo = 5;
    const int* ptr = 6;
}

void test2(int foo) {
    struct Owner me;
    me.name = 100;
    me.phone = 1000;
    int bar = me.name;
}

void tset3() {
    struct Cat cat;
    cat.name = 1;
    cat.age = 10;
    cat.owner.name = 100;
    cat.owner.phone = 1000;
}

void test4(struct Cat* cat) {
    cat->name = 1;
    cat->age = 10;
    cat->owner.name = 100;
}
void test5(struct Cat* cats) {
    cats[0].name = 1;
}
'''

test_ASM = '''
test:
  MOV A, 9
  LD [SP, 1], A
  MOV A, 8
  LD [SP, 0], A
  LD A, [SP, 0]
  LD B, [SP, 1]
  NEG B
  ADD A, B
  LD [SP, 2], A
  LD A, 'g'
  LD [SP, 3], A
  MOV A, 5
  LD [SP, 0], A
  MOV A, 6
  LD [SP, 3], A
  RET
test2:
  LD [SP, 0], A
  LD A, 100
  ADD B, SP, 1
  LD [B, 0], A
  LD A, 1000
  ADD B, SP, 1
  LD [B, 1], A
  ADD A, SP, 1
  LD A, [A, 0]
  LD [SP, 3], A
  RET
tset3:
  MOV A, 1
  ADD B, SP, 0
  LD [B, 0], A
  MOV A, 10
  ADD B, SP, 0
  LD [B, 1], A
  LD A, 100
  ADD B, SP, 0
  ADD B, 2
  LD [B, 0], A
  LD A, 1000
  ADD B, SP, 0
  ADD B, 2
  LD [B, 1], A
  RET
test4:
  LD [SP, 0], A
  MOV A, 1
  ADD B, SP, 0
  LD [B, 0], A
  MOV A, 10
  ADD B, SP, 0
  LD [B, 1], A
  LD A, 100
  ADD B, SP, 0
  ADD B, 2
  LD [B, 0], A
  RET
test5:
  LD [SP, 0], A
  MOV A, 1
  LD B, [SP, 0]
  MOV C, 0
  MUL C, 4
  ADD B, C
  LD [B, 0], A
  RET
'''

RETURN_STRUCT_ASM = '''
div:
  PUSH C
  SUB SP, 4
  LD [SP, 0], A ; num
  LD [SP, 1], B ; den
  MOV A, 3
  ADD B, SP, 2
  LD [B, 0], A ; quot
  MOV A, 4
  ADD B, SP, 2
  LD [B, 1], A ; rem
  ADD C, SP, 2
  LDM {A, B}, C
  JR .L0
.L0:
  ADD SP, 4
  POP C
  RET
print_int:
  PUSH LR, B, C, D
  SUB SP, 3
  LD [SP, 0], A ; num
  LD C, [SP, 0] ; num
  MOV D, 10
  MOV A, C
  MOV B, D
  CALL div
  ADD C, SP, 1
  LDM C, {A, B}
  ADD SP, 3
  POP PC, B, C, D
'''

class TestCompiler(TestCase):
    
    def code_eq_asm(self, file_name, target):
        if file_name.endswith('.c'):
            with open(r'tests/' + file_name) as in_file:
                text = in_file.read()
        cc.env.clear()
        cc.emit.clear()
        ast = cc.parse(text)
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
    
    # def test_assign(self):
    #     self.maxDiff = None
    #     self.code_eq_asm(test, test_ASM)
        
    def test_params(self):
        self.code_eq_asm('params.c', PARAMS_ASM)
        
    def test_fact(self):
        self.code_eq_asm('fact.c', FACT_ASM)
        
    def test_fib(self):
        self.code_eq_asm('fib.c', FIB_ASM)
        
    # def test_sum(self):
    #     self.code_eq_asm('sum.c', SUM_ASM)
        
    def test_getset(self):
        self.code_eq_asm('getset.c', GETSET_ASM)
        
    def test_getset2(self):
        self.code_eq_asm('getset2.c', GETSET2_ASM)
    
    def test_calls(self):
        self.maxDiff = None
        self.code_eq_asm('calls.c', CALLS_ASM)
        
    # def test_hello(self):
    #     self.maxDiff = None
    #     self.code_eq_asm('hello.c', HELLO_ASM)
        
    def test_array(self):
        self.maxDiff = None
        self.code_eq_asm('array.c', ARRAY_ASM)
        
    def test_structs(self):
        self.maxDiff = None
        self.code_eq_asm('structs.c', STRUCTS_ASM)
        
    def test_glob_struct(self):
        self.code_eq_asm('globs.c', GLOB_STRUCT_ASM)
        
    # def test_goto(self):
    #     self.code_eq_asm('goto.c', GOTO_ASM)
    
    def test_return_struct(self):
        self.code_eq_asm('returns.c', RETURN_STRUCT_ASM)

if __name__ == '__main__':
    main()