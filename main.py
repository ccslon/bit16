# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 09:26:08 2023

@author: ccslon
"""

import assembler

fact = '''
mov A, 6
call fact
halt

fact:
    push lr, B, C
    sub sp, 1
    ld [sp, 0], A
    ld B, [sp, 0]
    cmp B, 0
    jne .L0
    mov B, 1
    jr .L1
.L0:
    ld B, [sp, 0]
    ld A, [sp, 0]
    sub A, 1
    call fact
    mov C, A
    mul B, C    
.L1:
    mov A, B
    add sp, 1
    pop pc, B, C
'''

test = '''
nop
mov A, 5 ; 2
mov B, 3
add A, B ; 1
mov C, A

add D, A, B ; 3
sub E, C, 3 ; 4

neg B ; 5
'''

ld_test = '''
lol: 34
nop
nop
nop
ld A, =lol
mov B, 1
mov C, 10
mov D, 11
mov E, 12
ld [A], C
ld [A, B], D
ld [A, 2], E

ld C, [A, 2]
ld B, [A, B]
ld A, [A]
'''

jmp_test = '''
mov A, 0
mov B, 5
loop:
  cmp A, B
  jge end
  add A, 1
  jr loop
end:
  halt
'''

string_test = '''
msg: "Hello world!\0"
ld A, =msg
call print
halt
print:
  push B, C, D
  mov B, 0
  ld D, x7fff
.L0:
  ld C, [A, B]
  cmp C, 0
  jeq .L1
  ld [D], C
  add B, 1
  jr .L0
.L1:
  pop B, C, D
  ret
'''
bin2dec = '''
out:
    push B
    ld B, x7fff
    ld [B], A
    pop B
    ret
print:
    push lr, B
    mov B, A
print_loop:
    LD A, [B]
    cmp A, 0
    jeq print_end
    call out
    add B, 1
    jr print_loop
print_end:
    pop pc, B
    
    


num: 1729
ld A, =num
ld A, [A]
ld B, 10
call divmod

cmp A, 0

heap: 0
calloc:
    push B, C
    ld B, =heap
    ld C, [B]
    add C, A
    ld [B], C
    
    


divmod: ; A / B
    push C
    mov C, 0
divmod_loop:
    cmp A, B
    jlt divmod_end
    sub A, B
    add C, 1
    jr divmod_loop
divmod_end:
    mov B, A ; rem
    mov A, C ; quot
    pop C
    ret
    
'''
global_struct = '''
stdout:
    x7f00
    0
    0
.S0: "Cloud\\0"
.S1: "Colin\\0"
.S2: "ccs@email.com"
cloud:
    .S0
    10
    .S1
    .S2
ld A, =cloud
ld B, [A, 1]
add B, 1
LD [A, 1], B
halt
    
'''


if __name__ == '__main__':
    assembler.assemble(global_struct)