# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:47:39 2023

@author: Colin
"""

import re
from nodes import Var, Const, Unary, Binary, Compare, Call, Args, Func, Assign, If, Block, Program, Return, While, For, Break, Continue, Script, Struct, Params, Fields, Logic, Attr, Pointer, Address, Main, Global

TOKENS = {'const': r"(\"[^\"]*\")|(\'[^\']*\')|(\d+(\.\d+)?)|(true)|(false)|(null)",
          'main': r'main',
          'if': r'if',
          'else': r'else',
          'while': r'while',
          'for': r'for',
          'return': r'return',
          'continue': r'continue',
          'break': r'break',
          'not': r'not',
          'and': r'and',
          'or': r'or',
          'var': r'\w(\w|\d)*',
          'plus': r'\+',
          'dash':r'-',
          'star': r'\*',
          'slash': r'/',
          'at': r'@',
          'hash': r'#',
          'percent': r'%',
          'lshift': r'<<',
          'rshift': r'>>',
          'caret': '\^',
          'deq': r'==',
          'ge': r'>=',
          'le': r'<=',
          'eq': r'=',
          'ne': r'!=',
          'gt': r'>',
          'lt': r'<',
          'tilde': r'~',
          'pipe': '\|',
          'amp': '&',
          'lparen': r'\(',
          'rparen': r'\)',
          'lbrack': r'{',
          'rbrack': r'}',
          'lbrace': r'\[',
          'rbrace': r'\]',
          'comma': r',',
          'dot': r'\.',
          'error': r'\S+'}

def lex(text):
    regexp = re.compile('|'.join(rf'(?P<{token}>{pattern})' for token, pattern in TOKENS.items()), re.M)
    return [(match.lastgroup, match.group()) for match in regexp.finditer(text)] + [('end', '')]

class Parser:
    
    def primary(self):
        '''
        PRIMARY -> const|'(' EXPR ')'|var ('(' ARGS ')'|{'[' EXPR ']'|'.' var})
        '''
        if self.peek('const'):
            primary = Const(next(self))
        elif self.accept('('):
            primary = self.expr()
            self.expect(')')
        elif self.peek('var'):
            primary = Var(next(self))
            if self.accept('('):
                primary = Call(primary, self.args())
                self.expect(')')
            else:
                while self.peek('[','.'):
                    if self.accept('['):
                        primary = Script(primary, self.expr())
                        self.expect(']')
                    elif self.accept('.'):
                        primary = Attr(primary, self.expect('var'))
        else:
            self.error()
        return primary
    
    def unary(self):
        '''
        UNARY -> ['-'|'+'|'not'|'~'|'@'|'#'] primary
        '''
        if self.peek('-','+','not','~'):
            return Unary(next(self), self.unary())
        elif self.accept('@'):
            return Pointer(self.unary())
        elif self.accept('#'):
            return Address(self.unary())
        return self.primary()
    
    def mul(self):
        '''
        MUL -> UNARY {('*'|'/'|'%') UNARY}
        '''
        mul = self.unary()
        while self.peek('*','/','%'):
            mul = Binary(next(self), mul, self.unary())
        return mul
    
    def add(self):
        '''
        ADD -> MUL {('+'|'-') MUL}
        '''
        add = self.mul()
        while self.peek('+','-'):
            add = Binary(next(self), add, self.mul())
        return add
            
    def shift(self):
        '''
        SHIFT -> ADD {('<<'|'>>') ADD}
        '''
        shift = self.add()
        while self.peek('<<','>>'):
            shift = Binary(next(self), shift, self.add())
        return shift
    
    def relation(self):
        '''
        RELA -> SHIFT {('>'|'<'|'>='|'<=') SHIFT}
        '''
        relation = self.shift()
        while self.peek('>','<','>=','<='):
            relation = Compare(next(self), relation, self.shift())
        return relation
    
    def equality(self):
        '''
        EQUA -> RELA {('=='|'!=') RELA}
        '''
        equality = self.relation()
        while self.peek('==','!='):
            equality = Compare(next(self), equality, self.relation())
        return equality
    
    def bit_and(self):
        '''
        BIT_AND -> EQUA {'&' EQUA}
        '''
        bit_and = self.equality()
        while self.peek('&'):
            bit_and = Binary(next(self), bit_and, self.equality())
        return bit_and
    
    def bit_xor(self):
        '''
        BIT_XOR -> BIT_AND {'^' BIT_AND}
        '''
        bit_xor = self.bit_and()
        while self.peek('^'):
            bit_xor = Binary(next(self), bit_xor, self.bit_and())
        return bit_xor
    
    def bit_or(self):
        '''
        BIT_OR -> BIT_XOR {'|' BIT_XOR}
        '''
        bit_or = self.bit_xor()
        while self.peek('|'):
            bit_or = Binary(next(self), bit_or, self.bit_xor())
        return bit_or
    
    def logic_and(self):
        '''
        LOGIC_AND -> BIT_OR {'and' BIT_OR}
        '''
        logic_and = self.bit_or()
        while self.peek('and'):
            logic_and = Logic(next(self), logic_and, self.bit_or())
        return logic_and
    
    def logic_or(self):
        '''
        LOGIC_OR -> LOGIC_AND {'or' LOGIC_AND}
        '''
        logic_or = self.logic_and()
        while self.peek('or'):
            logic_or = Logic(next(self), logic_or, self.logic_and())
        return logic_or
    
    def assign(self):
        '''
        ASSIGN -> LEFT '=' ASSIGN
                 |LOGIC_OR
        '''
        assign = self.logic_or()
        if self.accept('='):
            if isinstance(assign, (Var, Script, Attr, Pointer)):
                assign = Assign(assign, self.assign())
            else:
                self.error()        
        return assign
    
    def expr(self):
        '''
        EXPR -> ASSIGN
        '''
        return self.assign()
    
    def args(self):
        '''
        ARGS -> [EXPR {',' EXPR}]        
        '''
        args = Args()
        if self.peek('const','var','(','-','+','not','~','@','#'):
            args.append(self.expr())
            while self.accept(','):
                args.append(self.expr())
        return args
    
    def state(self):
        '''
        STATE -> CALL
                |ASSIGN
                |IF
                |LOOP
                |JUMP
                |'{' BLOCK '}'
        CALL -> var '(' ARGS ')'
        IF -> 'if' EXPR STATE ['else' STATE]
        LOOP -> 'while' EXPR STATE|'for' ASSIGN EXPR ASSIGN STATE
        JUMP -> 'return' [EXPR]|'break'|'continue'
        '''
        if self.peek('var'):
            left = Var(next(self))
            if self.accept('('):
                state = Call(left, self.args())
                self.expect(')')
            else:
                while self.peek('[','.'):
                    if self.accept('['):
                        left = Script(left, self.expr())
                        self.expect(']')
                    elif self.accept('.'):
                        left = Attr(left, self.expect('var'))
                self.expect('=')
                state = Assign(left, self.expr())
        elif self.accept('@'):
            left = Var(self.expect('var'))
            while self.peek('[','.'):
                if self.accept('['):
                    left = Script(left, self.expr())
                    self.expect(']')
                elif self.accept('.'):
                    left = Attr(left, self.expect('var'))
            self.expect('=')
            state = Assign(Pointer(left), self.expr())
        elif self.accept('if'):
            state = If(self.expr(), self.state())
            if self.accept('else'):
                state.false = self.state()
        elif self.accept('while'):
            state = While(self.expr(), self.state())
        elif self.accept('for'):
            init = self.assign()
            self.expect(',')
            cond = self.expr()
            self.expect(',')
            state = For(init, cond, self.assign(), self.state())
        elif self.accept('return'):
            state = Return()
            if self.peek('const','var','(','-','+','not','~','@'):
                state.expr = self.expr()
        elif self.accept('break'):
            state = Break()
        elif self.accept('continue'):
            state = Continue()
        elif self.accept('{'):
            state = self.block()
            self.expect('}')
        else:
            self.error()
        return state
    
    def block(self):
        '''
        BLOCK -> {STATE}
        '''
        block = Block()
        while self.peek('var','@','if','while','for','return','break','continue','{'):
            block.append(self.state())
        return block
    
    def params(self):
        '''
        PARAMS -> [var {',' var}]
        '''
        params = Params()
        if self.peek('var'):
            params.append(Var(next(self)))
            while self.accept(','):
                params.append(Var(self.expect('var')))
        return params
    
    def fields(self):
        '''
        FIELDS -> {var ['=' const]}
        '''
        fields = Fields()
        while self.peek('var'):
            field = Var(next(self))
            if self.accept('='):
                self.expect('const')
            fields.append(field)
    
    def program(self):
        '''
        PROGRAM -> {STRUCT|FUNC|GLOBAL} ['main' '(' ')' '{ BLOCK '}'] {STRUCT|FUNC|GLOBAL}
                  
        // IMPORT -> 'from' var 'import' PARAMS
        STRUCT -> var '{' FIELDS '}'
        FUNC ->   var '(' PARAMS ')' '{' BLOCK '}'
        '''
        program = Program()
        while self.peek('var'):
            var = Var(next(self))
            if self.accept('{'): #Struct definision
                program.append(Struct(var, self.fields()))
                self.expect('}')
            elif self.accept('('): #Func definition
                params = self.params()
                self.expect(')')
                self.expect('{')
                program.append(Func(var, params, self.block()))
                self.expect('}')
            elif self.accept('='):
                program.append(Global(self.expect('const')))
            else:
                self.error()
        if self.accept('main'):
            self.expect('(')
            self.expect(')')
            self.expect('{')
            program.insert(0, Main(self.block()))
            self.expect('}')
        while self.peek('var'):
            var = Var(next(self))
            if self.accept('{'): #Struct definision
                program.append(Struct(var, self.fields()))
                self.expect('}')
            elif self.accept('('): #Func definition
                params = self.params()
                self.expect(')')
                self.expect('{')
                program.append(Func(var, params, self.block()))
                self.expect('}')
            elif self.accept('='):
                program.append(Global(self.expect('const')))
            else:
                self.error()
        return program
    
    def parse(self, text):
        self.tokens = lex(text)
        #for i, (t, v) in enumerate(self.tokens): print(i, t, v)
        self.index = 0
        ast = self.program()
        self.expect('end')
        return ast
        
    def __next__(self):
        _, value = self.tokens[self.index]
        self.index += 1
        return value
        
    def peek(self, *symbols):
        type_, value = self.tokens[self.index]
        return type_ in symbols or value in symbols
    
    def accept(self, *symbols):
        if self.peek(*symbols):
            return next(self)
    
    def expect(self, *symbols):
        if self.peek(*symbols):
            return next(self)
        self.error()
        
    def error(self):
        etype, evalue = self.tokens[self.index]
        raise SyntaxError(f'Unexpected {etype} token "{evalue}" at {self.index}') 