# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 21:52:15 2023

@author: ccslon
"""

import assembler
import parse

ass = '''
print(n) {
}

main() {
    i = 0
    while i < 5 {
        print(i)
    }
}
'''

if __name__ == '__main__':
    assembler = assembler.Assembler(parse.Parser)
    assembler.assemble(ass)