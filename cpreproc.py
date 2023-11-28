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
#define foo(bar) (bar + 1)
#define thing() (*(++i))
/*
#define n 1111 
*/

int /* lol */ t; //#define t 2222

char* lmao = "#define n 555";

int m = min(4, n);
int o = binary(h, +, j)
int buffer[BUFSIZE];
binary(BUFSIZE, **, n)
FILE f;
z = min(a +  28, * p);

c = ( foo((2 * c)) + 55);

int x = thing();
'''
ID = r'\w(\w|\d)*'
ARG = r'(([^,]|"[^"]*")+'
class CPreProc:
    COMMENT = re.compile(r'''
                         /\*(.|\n)*?\*/
                         |
                         //.*\n
                         ''', re.M | re.X)
    STD = re.compile(r'''
                     ^
                     \s*
                     \#
                     \s*
                     include
                     \s+
                     (?P<file><\w+\.h>)
                     \s*
                     $
                     ''', re.M | re.X)
    INCLUDE = re.compile(r'''
                         ^
                         \s*
                         \#
                         \s*
                         include
                         \s+
                         (?P<file>"\w+\.[ch]")
                         \s*
                         $
                         ''', re.M | re.X)
    OBJ = re.compile(rf'''
                     ^
                     \s*
                     \#
                     \s*
                     define
                     \s+
                     (?P<name>{ID})
                     \s+
                     (?P<expr>.+)
                     \s*
                     $
                     ''', re.M | re.X)
    FUNC = re.compile(rf'''
                      ^
                      \s*
                      \#
                      \s*
                      define
                      \s+
                      (?P<name>{ID})
                      \(
                          \s*
                          (?P<args>({ID}(\s*,\s*{ID})*)?)
                          \s*
                      \)
                      \s+
                      (?P<expr>\(.+\))
                      \s*
                      $
                      ''', re.M | re.X)
      
    ELIP = re.compile(r'^#define (?P<name>\w(\w|\d)*)\((?P<args>(\w+(,\s*\w+)*,)?)\s*(?P<elip>\.\.\.)\) (?P<expr>\(.+\))$', re.M)
    
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
                args = r'\s*,\s*'.join(map(r'(?P<{}>([^,\n]|"[^"]*")+)'.format, args))
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
        return '\n'
    
preproc = CPreProc()

def preprocess(text):
    return preproc.preproc(text)

if __name__ == '__main__':
    print(preprocess(test))
    
'''
int a = 1;@

struct _FILE_ {
    int* buffer;
    int read;
    int write;
};
struct _FILE_ stdout = {0x7f00, 0, 0};
int fputc(char c, struct _FILE_* stream) {
    stream->buffer[stream->write++] = c;
    return 0;
}
int putchar(char c) {
    fputc(c, &stdout);
    return 0;
}
int fputs(const char* str, struct _FILE_* stream) {
    while (*str != '\0') {
        fputc(*str, stream);
        str++;
    }
    return 0;
}
int puts(const char* str) {
    fputs(str, &stdout);
    putchar('\5');
    return 0;
}@



int  t; 

char* lmao = "#define 5 555";

int m = (4 > 5 ? 5 : 4);
int o = (h + j)
int buffer[10];
(10 ** 5)
struct _FILE_ f;
z = min(a + 28, *p);
int x = (*(++i));
'''