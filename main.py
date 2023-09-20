# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 09:26:08 2023

@author: ccslon
"""

from assemble import Assembler

fact = '''
mov A, 6
call fact
mov B, 0
ld [B], A
halt

fact:
    push lr, B, C
    sub sp, 1
    ld [sp, 0], A
    ld B, [sp, 0]
    cmp B, 0
    jne .L0
    mov B, 1
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
mov A, 3
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
    jmp loop
end:
    jmp end
'''
clear_ram = '''
mov A, 0
mov B, 0
mov C, 0
not C
loop:
    cmp B, C
    jge end
    ld [B], A
    add B, 1
    jmp loop
end:
'''

if __name__ == '__main__':
    Assembler().assemble(fact)