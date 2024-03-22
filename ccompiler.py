# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 21:52:15 2023

@author: ccslon
"""

import assembler
import cpreproc
import cparser

def compile(name, iflag=False, sflag=False, fflag=True):
    if name.endswith('.c') or name.endswith('.h'):
        text = cpreproc.preprocess(name)
        if iflag:
            print(text)
            with open(f'{name[:-2]}.i', 'w+') as file:
                file.write(text)
        else:
            ast = cparser.parse(text)
            asm = ast.generate()
            if sflag:
                print(asm)
                if fflag:
                    with open(f'{name[:-2]}.s', 'w+') as file:
                        file.write(asm)
            else:
                assembler.assemble(asm, fflag, name[:-2])
    else:
        print("Wrong file type")