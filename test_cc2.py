# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 14:37:22 2023

@author: ccslon
"""
from unittest import TestCase, main, expectedFailure
import cpreproc
import cparser

class TestCompiler(TestCase):
    
    def code_eq_asm(self, name):
        text = cpreproc.preprocess(f'tests/{name}.c')
        ast = cparser.parse(text)
        out = ast.generate()
        with open(f'tests/{name}.s') as file:
            asm = file.read()
        self.assertEqual(out, asm)
    
    @expectedFailure
    def test_bad_const(self):
        text = cpreproc.preprocess('tests/bad_const.c')
        ast = cparser.parse(text)
        ast.generate()
    
    def test_init(self):
        self.code_eq_asm('init')
        
    def test_main(self):
        self.code_eq_asm('main')
        
    def test_const(self):
        self.code_eq_asm('const')
        
    def test_rconst(self):
        self.code_eq_asm('rconst')
        
    def test_multi(self):
        self.code_eq_asm('multi')
    
    def test_paren1(self):
        self.code_eq_asm('paren')
        
    def test_params(self):
        self.code_eq_asm('params')
        
    def test_fact(self):
        self.code_eq_asm('fact')
        
    def test_fib(self):
        self.code_eq_asm('fib')
        
    def test_sum(self):
        self.code_eq_asm('sum')
        
    def test_getset(self):
        self.code_eq_asm('getset')
        
    def test_getset2(self):
        self.code_eq_asm('getset2')
    
    def test_calls(self):
        self.code_eq_asm('calls')
        
    def test_hello(self):
        self.code_eq_asm('hello')
        
    def test_array(self):
        self.code_eq_asm('array')
        
    def test_structs(self):
        self.code_eq_asm('structs')
        
    def test_glob_struct(self):
        self.code_eq_asm('globs')
        
    def test_goto(self):
        self.code_eq_asm('goto')
    
    def test_return_struct(self):
        self.code_eq_asm('returns')
        
    def test_pointers(self):
        self.code_eq_asm('pointers')
        
    def test_defines(self):
        self.code_eq_asm('defines')
    
    def test_includes(self):
        self.code_eq_asm('include')
    
    def test_enums(self):
        self.code_eq_asm('enums')
        
    def test_unions(self):
        self.code_eq_asm('unions')
        
    def test_func_ptrs(self):
        self.code_eq_asm('func_ptrs')
    
    def test_neg_nums(self):
        self.code_eq_asm('neg_nums')
        
    def test_unsigned(self):
        self.code_eq_asm('unsigned')
    
    def test_logic(self):
        self.code_eq_asm('logic')
        
    def test_cstrings(self):
        self.code_eq_asm('cstrings')

if __name__ == '__main__':
    main()