# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 21:52:15 2023

@author: ccslon
"""

import assemble
import parse

test1 = '''
print(n) {
}
main() {
    i = 0
    while i < 5 {
        print(i)
    }
}
'''
test2 = '''
fact(n) {
    if n == 0 {
        return 1
    }
    return n * fact(n-1)
}
'''
test3 = '''
fib(n) {
    if n == 1 {
        return 0
    } else if n == 2 {
        return 1
    } else {
        return fib(n-1) + fib(n-2)
    }    
}
'''
abs_ = '''
abs(n) {
    if n < 0 {
        return -n
    } else {
        return n
    }
}
'''

if __name__ == '__main__':
    assembler = assemble.Assembler(parse.Parser)
    assembler.assemble(abs_)