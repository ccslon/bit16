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
    if n < 0 return -n
    return n
}
'''
div = '''
div(n, d):
    q = 0
    while n >= d {
        n = n - d
        q = q + 1
    }
    return q
'''
mod = '''
mod(n, d):
    while n >= d {
        n = n - d
    }
    return n
'''
pow_ = '''
pow(b, e) {
    p = 1
    while e > 0 {
        p = p * b
        e = e - 1
    }
    return p
}
'''

test = '''
foo(n) {
    bar = 5 * n
}
'''
set_ = '''
set(g, i, t) {
    g[i] = t
}
'''
get2 = '''
get2(g, i, j) {
    return g[i][j]
}
'''

def compile(program):
    ast = parse.Parser().parse(program)
    asm = ast.compile()
    objects = assemble.Assembler().assemble(asm)
    assemble.Linker.link(objects)

if __name__ == '__main__':
    compile(get2)