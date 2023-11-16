# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 12:18:26 2023

@author: ccslon
"""

import re


test1 = '''#define n 5
#define m 6
n n n nightn m
'''
'''(?P<args>\(\w+(,\s*\w+)*\))'''
test = '''
#include <stdio.h>
#define n 5
#define BUFSIZE 10
#define FILE struct _FILE_
#define min(a, b) (a > b ? b : a)
#define binary(a, op, b) a op b
int m = min(4, n);
int o = binary(h, +, j)
int buffer[BUFSIZE];
binary(BUFSIZE, **, n)
FILE f;
'''

class CPreProc:
    
    STD = re.compile(r'#include (?P<file><\w+\.h>)\n')
    INCLUDE = re.compile(r'#include (?P<file>"\w\.[ch]")\n')
    DEFINE = re.compile(r'#define (?P<name>(\w|\.)+)(\((?P<args>\w+(,\s*\w+)*)\))? (?P<expr>.+)\n')
    
    def include(self, regex, text, ext=''):
        for match in regex.finditer(text):
            file_name = match.group('file')[1:-1]
            text = regex.sub(self.repl_macro, text)
            if file_name not in self.included:
                with open(f'{ext}{file_name}', 'r') as file:
                    text = file.read() + '@' + text
                self.included.add(file_name)
        return text
    
    def includes(self, text):
        self.included = set()
        while '#include' in text: #self.STD.match(text) or self.INCLUDE.match(text):
            text = self.include(self.STD, text, 'std\\')
            text = self.include(self.INCLUDE, text)
        return text
    
    def defines(self, text):
        self.defined = {}
        for match in self.DEFINE.finditer(text):
            self.defined[match.group('name')] = (tuple(map(str.strip, args.split(','))) if (args := match.group('args')) else None), match.group('expr')
        text = self.DEFINE.sub(self.repl_macro, text)
        for defn, (args, expr)  in self.defined.items():
            if args is None:
                text = re.sub(rf'\b{defn}\b', expr, text)
            else:                
                args = r'\s*,\s*'.join(map(r'(?P<{}>\S+)'.format, args))
                text = re.sub(rf'\b(?P<name>{defn})\({args}\)', self.repl_define, text)
        return text
    
    def preproc(self, text):
        text = self.includes(text)       
        text = self.defines(text)
        return text
    
    def repl_define(self, match):
        args, expr = self.defined[match.group('name')]
        for arg in args:
            expr = re.sub(rf'\b{arg}\b', match.group(arg), expr)
        return expr
    
    def repl_macro(self, match):
        return '\n'
    
preproc = CPreProc()

def preprocess(text):
    return preproc.preproc(text)
