# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 12:18:26 2023

@author: ccslon
"""

import re
import os

ID = r'[A-Za-z]\w*'
ARG = r'(([^,]|"[^"]*")+'
class CPreProc:
    COMMENT = re.compile(r'''
                         /\*(.|\n)*?\*/     #multi line comment
                         |
                         //.*\n             #single line comment
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
    CONCAT = re.compile('''
                        "([^"]*)"
                        \s*
                        "([^"]*)"
                        ''', re.X)
    ELIP = re.compile(r'^#define (?P<name>\w(\w|\d)*)\((?P<args>(\w+(,\s*\w+)*,)?)\s*(?P<elip>\.\.\.)\) (?P<expr>\(.+\))$', re.M)

    def comments(self, text):
        return self.COMMENT.sub(self.repl, text)

    def include(self, regex, text, ext=''):
        for match in regex.finditer(text):
            file_name = match['file'][1:-1]
            text = regex.sub(self.repl, text)
            if file_name not in self.included:
                with open(f'{ext}{os.path.sep}{file_name}') as file:
                    text = file.read() + '\n@\n' + text
                self.included.add(file_name)
        return text

    def includes(self, text):
        self.included = set()
        while self.STD.search(text) or self.INCLUDE.search(text):
            text = self.include(self.STD, text, f'{os.getcwd()}{os.path.sep}std')
            text = self.include(self.INCLUDE, text, self.path)
        return text

    def defines(self, text):
        self.defined = {}
        for match in self.OBJ.finditer(text):
            self.defined[match['name']] = None, match.group('expr')
        text = self.OBJ.sub(self.repl, text)
        for match in self.FUNC.finditer(text):
            self.defined[match.group('name')] = tuple(filter(len, map(str.strip, match.group('args').split(',')))), match.group('expr')
        text = self.FUNC.sub(self.repl, text)
        for defn, (args, expr)  in self.defined.items():
            if args is None:
                text = re.sub(rf'\b{defn}\b', expr, text)
            else:
                args = r'\s*,\s*'.join(map(r'(?P<{}>([^,\n]|"[^"]*")+)'.format, args))
                text = re.sub(rf'\b(?P<name>{defn})\({args}\)', self.repl_define, text)
        return text

    def concat(self, text):
        return self.CONCAT.sub(self.repl_concat, text)

    def preproc(self, file_name):
        with open(file_name) as file:
            self.path = os.path.dirname(os.path.abspath(file.name))
            text = file.read()
        text = self.includes(text)
        text = self.comments(text)
        text = self.defines(text)
        text = self.concat(text)
        return text

    def repl(self, match):
        return '\n' * match.group().count('\n')

    def repl_define(self, match):
        args, expr = self.defined[match['name']]
        for arg in args:
            expr = re.sub(rf'#\s*\b{arg}\b', f'"{match[arg]}"', expr)
            expr = re.sub(rf'\b{arg}\b', match[arg], expr)
        return expr

    def repl_concat(self, match):
        return f'"{match[1]}{match[2]}"'

preproc = CPreProc()

def preprocess(file_name):
    return preproc.preproc(file_name)