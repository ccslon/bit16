# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 09:26:08 2023

@author: ccslon
"""

import assemble

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



if __name__ == '__main__':
    assemble.assemble(string_test)