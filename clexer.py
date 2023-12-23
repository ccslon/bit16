# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 12:05:47 2023

@author: Colin
"""
import re

class Token:
    def __init__(self, type, lexeme, line_no):
        self.type, self.lexeme, self.line_no = type, lexeme, line_no

class MetaLexer(type):
    def __init__(self, name, bases, attrs):
        self.action = {}
        regex = []        
        flag = attrs['flag'] if 'flag' in attrs else 0 #re.NOFLAG
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
        self.regex = re.compile('|'.join(rf'(?P<{name}>{pattern})' for name, pattern in regex), flag)

class LexerBase(metaclass=MetaLexer):
    def lex(self, text):
        self.line_no = 1
        return [Token(match.lastgroup, result, self.line_no) for match in self.regex.finditer(text) if (result := self.action[match.lastgroup](self, match.group())) is not None] + [Token('end','',self.line_no)]

class CLexer(LexerBase):
    
    RE_num = r'0x[0-9a-f]+|0b[01]+|\d+|NULL'
    RE_char = r"'\\?[^']'"
    RE_string = r'"[^"]*"'
    def RE_eof(self, match):
        r'@\n'
        self.line_no = 1
    RE_const = r'\b(const)\b'
    RE_type = r'\b(void|int|char)\b'
    RE_struct = r'\b(struct)\b'
    RE_return = r'\b(return)\b'
    RE_if = r'\b(if)\b'
    RE_else = r'\b(else)\b'
    RE_switch = r'switch'
    RE_case = r'case'
    RE_default = r'default'
    RE_while = r'while'
    RE_do = r'\b(do)\b'
    RE_for = r'for'
    RE_break = r'break'
    RE_continue = r'continue'
    RE_goto = r'goto'
    RE_include = r'include'
    RE_id = r'[A-Za-z_]\w*'
    def RE_new_line(self, match):
        r'\n'
        self.line_no += 1
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
    RE_pip = r'\|'
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
    RE_dot = r'\.'
    RE_comma = r','
    def RE_error(self, match):
        r'\S'
        raise SyntaxError(f'line {self.line_no}: Invalid symbol "{match}"')

lexer = CLexer()

def lex(text):
    return lexer.lex(text)