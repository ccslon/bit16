# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 09:26:08 2023

@author: ccslon
"""

from ccompiler import compile as ccompile

if __name__ == '__main__':
    # ccompile('tests/globs.c', sflag=True, fflag=True)
    # ccompile('tests/fact.c', sflag=True, fflag=False)
    # ccompile('tests/hello.c')
    # ccompile('std/stdio.h')
    # ccompile('std/stdio.h', sflag=True)
    # ccompile('std/stdio.h', sflag=True, fflag=False)
    # ccompile('c/strcat.c')
    # ccompile('c/ack.c')
    ccompile('c/testall.c')
    # ccompile('c/glob_ptrs.c', sflag=True)
    # ccompile('c/unsigned.c', sflag=True, fflag=True)
    # ccompile('c/ack.c', sflag=True, fflag=False)
    # ccompile('c/fib.c', sflag=True, fflag=False, iflag=True)