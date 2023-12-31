# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 21:52:15 2023

@author: ccslon
"""

import assembler
import cpreproc
import cparser

def ccompile(file_name, sflag=False, fflag=True, iflag=False):
    if file_name.endswith('.c') or file_name.endswith('.h'):
        text = cpreproc.preprocess(file_name)
        if iflag:
            print(text)
            return
        ast = cparser.parse(text)
        asm = ast.generate()
        if sflag:
            print(asm)
            if fflag:
                with open(f'{file_name[:-2]}.s', 'w+') as out_file:
                    out_file.write(asm)
        else:
            bit16 = assembler.assemble(asm)
            if fflag:
                with open(f'{file_name[:-2]}.bit16', 'w+') as out_file:
                    out_file.write('v2.0 raw\n'+' '.join(bit16))
    else:
        print("Wrong file type")

if __name__ == '__main__':
    # ccompile('hello.c', sflag=True, oflag=False)
    # ccompile('tests//var.c', sflag=True, fflag=False, iflag=False)
    # ccompile('tests//globs.c')
    ccompile('std//ctype.h', sflag=True, fflag=False)
    # ccompile('c//strcat.c')
    # ccompile('c//var.c')
    # ccompile('c//test.c', sflag=True, fflag=False)
    # ccompile('c//var.c', sflag=True, fflag=False, iflag=True)