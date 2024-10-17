# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 12:05:47 2023

@author: Colin
"""
from typing import NamedTuple
import re

class Token(NamedTuple):
    type: str
    lexeme: str
    line: int

class MetaLexer(type):
    def __init__(self, name, bases, attrs):
        self.action = {}
        regex = []
        for attr in attrs:
            if attr.startswith('RE_'):
                name = attr[3:]
                if callable(attrs[attr]):
                    pattern = attrs[attr].__doc__
                    self.action[name] = attrs[attr]
                else:
                    pattern = attrs[attr]
                    self.action[name] = lambda self, match: match
                regex.append((name, pattern))
        self.regex = re.compile('|'.join(rf'(?P<{name}>{pattern})' for name, pattern in regex))

class LexerBase(metaclass=MetaLexer):
    def lex(self, text):
        self.line = 1
        return [Token(match.lastgroup, result, self.line) for match in self.regex.finditer(text) if (result := self.action[match.lastgroup](self, match.group())) is not None] + [Token('end','',self.line)]

class CLexer(LexerBase):

    RE_num = r'0x[0-9a-f]+|0b[01]+|\d+'
    RE_char = r"'\\?[^']'"
    def RE_string(self, match):
        r'"(\\"|[^"])*"'
        return match[1:-1]
    def RE_eof(self, match):
        r'@\n'
        self.line = 1
    RE_typedef  = r'\b(typedef)\b'
    RE_const = r'\b(const)\b'
    RE_void = r'\b(void)\b'
    RE_word = r'\b(int|char)\b'
    RE_unsigned = r'\b(unsigned)\b'
    RE_signed = r'\b(signed)\b'
    RE_struct = r'\b(struct)\b'
    RE_enum = r'\b(enum)\b'
    RE_union = r'\b(union)\b'
    RE_sizeof = r'\b(sizeof)\b'
    RE_return = r'\b(return)\b'
    RE_if = r'\b(if)\b'
    RE_else = r'\b(else)\b'
    RE_switch = r'\b(switch)\b'
    RE_case = r'\b(case)\b'
    RE_default = r'\b(default)\b'
    RE_while = r'\b(while)\b'
    RE_do = r'\b(do)\b'
    RE_for = r'\b(for)\b'
    RE_break = r'\b(break)\b'
    RE_continue = r'\b(continue)\b'
    RE_goto = r'\b(goto)\b'
    RE_include = r'\b(include)\b'
    RE_id = r'[A-Za-z_]\w*'
    def RE_new_line(self, match):
        r'\n'
        self.line += 1
    RE_semi = r';'
    RE_colon = ':'
    RE_lparen = r'\('
    RE_rparen = r'\)'
    RE_lbrack = r'{'
    RE_rbrack = r'}'
    RE_lbrace = r'\['
    RE_rbrace = r'\]'
    RE_dplus = r'\+\+'
    RE_ddash = r'--'
    RE_arrow = r'->'
    RE_pluseq = r'\+='
    RE_dasheq = r'-='
    RE_stareq = r'\*='
    RE_slasheq = r'/='
    RE_percenteq = r'%='
    RE_lshifteq = r'<<='
    RE_rshifteq = r'>>='
    RE_careteq = r'\^='
    RE_pipeeq = r'\|='
    RE_ampeq = r'&='
    RE_plus =  r'\+'
    RE_dash = r'-'
    RE_star = r'\*'
    RE_slash = r'/'
    RE_percent = r'%'
    RE_lshift = r'<<'
    RE_rshift = r'>>'
    RE_caret = r'\^'
    RE_dpipe = r'\|\|'
    RE_damp = '\&\&'
    RE_pipe = r'\|'
    RE_amp = r'\&'
    RE_deq = r'=='
    RE_ne = r'!='
    RE_ge = r'>='
    RE_le = r'<='
    RE_eq = r'='
    RE_gt = r'>'
    RE_lt = r'<'
    RE_exp = r'!'
    RE_ques = r'\?'
    RE_tilde = r'~'
    RE_elipsis = r'\.\.\.'
    RE_dot = r'\.'
    RE_comma = r','
    def RE_error(self, match):
        r'\S'
        raise SyntaxError(f'line {self.line}: Invalid symbol "{match}"')

lexer = CLexer()

def lex(text):
    return lexer.lex(text)