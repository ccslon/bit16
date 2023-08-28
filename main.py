# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 09:26:08 2023

@author: ccslon
"""

from asssembler import Assembler

fact = '''
mov A, 6
call fact
mov B, 0
ld [B], A
halt:
    jmp halt

fact:
    psh lr, B, C
    sub sp, 1
    ld [sp, 0], A
    ld B, [sp, 0]
    cmp B, 0
    jne .L0
    mov B, 0
    jmp .L1
.L0:
    ld B, [sp, 0]
    ld A, [sp, 0]
    sub A, 1
    call fact
    mov C, A
    mul B, C    
.L1:
    mov A, B
    pop pc, B, C
'''

halt = '''
mov B, 5
mov A, B
add A, B
'''
test = '''
; nop
mov A, 5 ; 2
mov B, 3
add A, B ; 1
mov C, A

add D, A, B ; 3
sub E, C, 3 ; 4

neg B ; 5
'''

ldtest = '''
mov A, 10
mov B, 11
mov C, 3
mov D, 1
mov E, 12
ld [C], A
ld [C, D], B
ld [C, 2], E

ld A, [C]
ld B, [C, D]
ld C, [C, 2]
'''

jmptest = '''
mov A, 0
mov B, 5
loop:
    cmp A, B
    jge end
    add A, 1
    jmp loop
end:
    jmp end
'''

if __name__ == '__main__':
    assembler = Assembler()
    assembler.assemble(test)