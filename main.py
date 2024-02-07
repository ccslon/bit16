# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 09:26:08 2023

@author: ccslon
"""

from ccompiler import compile as ccompile

if __name__ == '__main__':
    # ccompile('tests//unions.c', sflag=True, fflag=False)
    # ccompile('tests//globs.c')
    # ccompile('std//stdio.h')
    # ccompile('std//stdlib.h', sflag=True, fflag=False)
    # ccompile('c//strcat.c')
    # ccompile('c//in.c')
    # ccompile('c//testall.c')
    ccompile('c//funcptrs.c', sflag=True, fflag=False)
    # ccompile('c//bsearch.c', sflag=True, fflag=True)
    # ccompile('c//fib.c', sflag=True, fflag=False, iflag=True)