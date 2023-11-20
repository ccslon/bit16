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
#include "test.c"
#define n 5
#define BUFSIZE 10
#define FILE struct _FILE_
#define min(a, b) (a > b ? b : a)
#define binary(a, op, b) (a op b)
#define thing() (*(++i))
/* #define n 1111
*/
int t; //#define t 2222

char* lmao = "#define n 555";

int m = min(4, n);
int o = binary(h, +, j)
int buffer[BUFSIZE];
binary(BUFSIZE, **, n)
FILE f;

int x = thing();

'''

class CPreProc:
    COMMENT = re.compile(r'(/\*(.|\n)*?\*/)|(//.*\n)', re.M)
    STD = re.compile(r'^#include (?P<file><\w+\.h>)$', re.M)
    INCLUDE = re.compile(r'^#include (?P<file>"\w+\.[ch]")$', re.M)
    OBJ = re.compile(r'^#define (?P<name>\w(\w|\d)*) (?P<expr>.+)$', re.M)
    FUNC = re.compile(r'^#define (?P<name>\w(\w|\d)*)\((?P<args>(\w+(,\s*\w+)*)?)\) (?P<expr>\(.+\))$', re.M)
    
    def comments(self, text):
        return self.COMMENT.sub(self.repl_comment, text)
    
    def include(self, regex, text, ext=''):
        for match in regex.finditer(text):
            file_name = match.group('file')[1:-1]
            text = regex.sub(self.repl_macro, text)
            if file_name not in self.included:
                with open(f'{ext}{file_name}', 'r') as file:
                    text = file.read() + '@\n' + text
                self.included.add(file_name)
        return text
    
    def includes(self, text):
        self.included = set()
        while self.STD.search(text) or self.INCLUDE.search(text):
            text = self.include(self.STD, text, 'std\\')
            text = self.include(self.INCLUDE, text, 'c\\')
        return text
    
    def defines(self, text):
        self.defined = {}
        for match in self.OBJ.finditer(text):
            self.defined[match.group('name')] = None, match.group('expr')
        text = self.OBJ.sub(self.repl_macro, text)
        for match in self.FUNC.finditer(text):
            self.defined[match.group('name')] = tuple(filter(len, map(str.strip, match.group('args').split(',')))), match.group('expr')
        text = self.FUNC.sub(self.repl_macro, text)
        for defn, (args, expr)  in self.defined.items():
            if args is None:
                text = re.sub(rf'\b{defn}\b', expr, text)
            else:
                args = r'\s*,\s*'.join(map(r'(?P<{}>\S+)'.format, args))
                text = re.sub(rf'\b(?P<name>{defn})\({args}\)', self.repl_define, text)
        return text
    
    def preproc(self, text):
        text = self.comments(text)
        text = self.includes(text)
        text = self.defines(text)
        return text
    
    def repl_comment(self, match):
        return '\n' * match.group().count('\n')
    
    def repl_define(self, match):
        args, expr = self.defined[match.group('name')]
        for arg in args:
            expr = re.sub(rf'\b{arg}\b', match.group(arg), expr)
        return expr
    
    def repl_macro(self, match):
        return ''
    
preproc = CPreProc()

def preprocess(text):
    return preproc.preproc(text)

if __name__ == '__main__':
    print(preprocess(test))