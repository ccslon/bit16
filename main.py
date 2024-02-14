# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 09:26:08 2023

@author: ccslon
"""

from ccompiler import compile as ccompile

if __name__ == '__main__':
    # ccompile('tests//defines.c', sflag=True, fflag=False)
    # ccompile('tests//globs.c')
    # ccompile('std//stdio.h')
    # ccompile('std//stdbool.h', sflag=True, fflag=False)
    # ccompile('c//strcat.c')
    # ccompile('c//in.c')
    ccompile('c//testall.c')
    # ccompile('c//test.c', sflag=True, fflag=True)
    # ccompile('c//bsearch.c', sflag=True, fflag=True)
    # ccompile('c//fib.c', sflag=True, fflag=False, iflag=True)
    
# sum:
#   PUSH B, FP
#   SUB SP, 2
#   MOV FP, SP
#   MOV A, 0
#   LD [FP, 0], A ; s
#   MOV A, 0
#   LD [FP, 1], A ; i
# .L1:
#   LD A, [FP, 1] ; i
#   LD B, [FP, 4] ; n
#   CMP A, B
#   JGE .L3
#   LD A, [FP, 0] ; s
#   LD B, [FP, 1] ; i
#   ADD A, B
#   LD [FP, 0], A ; s
# .L2:
#   LD A, [FP, 1] ; i
#   ADD B, A, 1
#   LD [FP, 1], B ; i
#   JR .L1
# .L3:
#   LD A, [FP, 0] ; s
#   JR .L0
# .L0:
#   MOV SP, FP
#   ADD SP, 2
#   POP B, FP
#   ADD SP, 1
#   RET