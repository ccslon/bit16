# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:47:39 2023

@author: Colin
"""

import re
from cnodes import Decl, Array, StructType, PointerType, Type, Conditional, Cast, Arrow, Id, Const, Unary, Binary, Compare, Call, Args, Func, Assign, If, Block, Program, Return, While, For, Break, Continue, Script, Struct, Params, Fields, Logic, Attr, Pointer, Address, Main, Global, Char, String

'''
TODO
[ ] Type checking
[ ] '.' vs '->' checking
[ ] Allocating arrays
'''

TOKENS = {'const': r'(0x[0-9a-f]+)|(0b[01]+)|(\d+)|(NULL)',
          'char': r"'\\?[^']'",
          'string': r'"[^"]*"',
          'type' : r'(void)|(int)|(char)',
          'sign': r'(signed)|(unsigned)',
          'struct': r'struct',
          'union': r'union',
          'enum': r'enum',
          'if': r'if',
          'else': r'else',
          'while': r'while',
          'for': r'for',
          'do': r'do',
          'case': r'case',
          'default': r'default',
          'switch': r'switch',
          'return': r'return',
          'continue': r'continue',
          'break': r'break',
          'id': r'\w(\w|\d)*',
          'semi': r';',
          'colon': r':',
          'dplus': r'\+\+',
          'ddash': r'--',
          'pluseq': r'\+=',
          'dasheq': r'-=',
          'stareq': r'\*=',
          'slasheq': r'/=',
          'percenteq': r'%=',
          'lshifteq': r'<<=',
          'rshifteq': r'>>=',
          'careteq': r'\^=',
          'pipeeq': r'\|=',
          'ampeq': r'&=',
          'plus': r'\+',
          'dash':r'-',
          'star': r'\*',
          'slash': r'/',
          'percent': r'%',
          'lshift': r'<<',
          'rshift': r'>>',
          'caret': '\^',
          'dpipe': r'\|\|',
          'damp': r'\&\&',
          'pipe': r'\|',
          'amp': r'\&',
          'ptr_op': r'->',
          'deq': r'==',
          'ge': r'>=',
          'le': r'<=',
          'eq': r'=',
          'ne': r'!=',
          'gt': r'>',
          'lt': r'<',
          'tilde': r'~',
          'lparen': r'\(',
          'rparen': r'\)',
          'lbrack': r'{',
          'rbrack': r'}',
          'lbrace': r'\[',
          'rbrace': r'\]',
          'comma': r',',
          'dot': r'\.',
          'error': r'\S+'}

RE = re.compile('|'.join(rf'(?P<{token}>{pattern})' for token, pattern in TOKENS.items()), re.M)

def lex(text):    
    return [(match.lastgroup, match.group()) for match in RE.finditer(text)] + [('end', '')]

class Parser:    
    def primary(self):
        '''
        PRIMARY -> id|const|char|string|'(' EXPR ')'
        '''
        if self.peek('id'):
            return Id(next(self))
        elif self.peek('const'):
            return Const(next(self))
        elif self.peek('char'):
            return Char(next(self))
        elif self.peek('string'):
            return String(next(self))
        elif self.accept('('):
            primary = self.expr()
            self.expect(')')
        else:
            self.error()
        return primary
    
    def postfix(self):
        '''
        POST -> PRIMARY {'[' EXPR ']'|'(' ARGS ')'|'.' id|'->' id|'++'|'--'}
        '''
        postfix = self.primary()
        if self.peek('[','(','.','->','++','--'):
            assert type(postfix) is Id
            while self.peek('[','(','.','->','++','--'):
                if self.accept('['):
                    if not self.accept(']'):
                        postfix = Script(postfix, self.expr())
                        self.expect(']')
                    else:
                        postfix = Script(postfix, None)
                elif self.accept('('):
                    if not self.accept(')'):
                        postfix = Call(postfix, self.args())
                        self.expect(')')
                    else:
                        postfix = Call(postfix, Args())
                elif self.accept('.'):
                    postfix = Attr(postfix, self.expect('id'))
                elif self.accept('->'):
                    postfix = Arrow(postfix, self.expect('id'))
                elif self.peek('++','--'):
                    postfix = Assign(postfix, Binary(next(self), postfix, Const('1')))
        return postfix
    
    def args(self):
        '''
        ARGS -> ASSIGN {',' ASSIGN}
        '''
        args = Args([self.assign()])
        while self.accept(','):
            args.append(self.assign())
        return args
    
    def unary(self):
        '''
        UNARY -> POSTFIX
                |('++'|'--') UNARY
                |('+'|'-'|'~'|'!'|'*'|'&') CAST
                |'sizeof' UNARY
                |'sizeof' '(' TYPE_SPEC ')'
        '''
        if self.peek('++','--'):
            op = next(self)
            unary = self.unary()
            return Assign(unary, Binary(op, unary, Const('1')))
        elif self.peek('+','-','~','!'):
            return Unary(next(self), self.unary())
        elif self.accept('*'):
            return Pointer(self.unary())
        elif self.accept('&'):
            return Address(self.unary())
        elif self.accept('sizeof'):
            if self.accept('('):
                self.type_spec()
                self.expect(')')
            else:
                self.unary()
        else:
            return self.postfix()
            
    def cast(self):
        '''
        CAST -> '(' TYPE_SPEC ')' CAST
               |UNARY
        '''
        if self.accept('('):
            target = self.type_spec()
            self.expect(')')
            return Cast(target, self.cast())
        else:
            return self.unary()
    
    def type_spec(self):
        if self.peek('type'):
            type_spec = Type(next(self))
        elif self.accept('struct','union'):
            type_spec = StructType(self.expect('id'), 3) #TODO
        while self.accept('*'):
            type_spec = PointerType(type_spec)
        return type_spec
    
    def mul(self):
        '''
        mul -> CAST {('*'|'/'|'%') CAST}
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
            self.add()
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
        LOGIC_AND -> BIT_OR {'&&' BIT_OR}
        '''
        logic_and = self.bit_or()
        while self.peek('&&'):
            logic_and = Logic(next(self), logic_and, self.bit_or())
        return logic_and
    
    def logic_or(self):
        '''
        LOGIC_OR -> LOGIC_AND {'||' LOGIC_AND}
        '''
        logic_or = self.logic_and()
        while self.peek('||'):
            logic_or = Logic(next(self), logic_or, self.logic_and())
        return logic_or
    
    def cond(self):
        '''
        COND -> LOGIC_OR ['?' EXPR ':' COND]
        '''
        cond = self.logic_or()
        if self.accept('?'):
            expr = self.expr()
            self.expect(':')
            cond = Conditional(cond, expr, self.cond())
        return cond
    
    def assign(self):
        '''
        ASSIGN -> UNARY ['+'|'-'|'*'|'/'|'%'|'<<'|'>>'|'^'|'|'|'&']'=' ASSIGN
                 |COND
        '''
        assign = self.cond()
        if self.accept('='):
            if isinstance(assign, (Id, Script, Attr, Pointer)):
                assign = Assign(assign, self.assign())
            else:
                self.error()
        elif self.peek('+=','-=','*=','/=','%=','<<=','>>=','^=','|=','&='):
            if isinstance(assign, (Id, Script, Attr, Pointer)):
                assign = Assign(assign, Binary(next(self), assign, self.assign()))
            else:
                self.error()
        return assign
    
    def expr(self):
        '''
        EXPR -> ASSIGN
        '''
        return self.assign()
        # while self.accept(','):
        #     self.assign()
    
    def const(self):
        return self.cond()
  
    def statement(self):
        '''
        STATE -> CALL
                |ASSIGN
                |IF
                |LOOP
                |JUMP
                |'{' BLOCK '}'
        CALL -> id '(' ARGS ')' ';'
        IF -> 'if' '(' EXPR ')' STATE ['else' STATE]
        LOOP -> 'while' '(' EXPR ')' STATE|'for' '(' EXPR ';' EXPR ';' EXPR ')' STATE
        JUMP -> 'return' [EXPR] ';' |'break' ';' |'continue' ';'
        '''
        if self.accept('{'):
            statement = self.block()
            self.expect('}')
            
        elif self.peek('*','id','++','--'):
            statement = self.unary()
            if self.accept('='):
                if isinstance(statement, (Id, Script, Attr, Pointer, Arrow)):
                    statement = Assign(statement, self.assign())
                else:
                    self.error()
            elif self.peek('+=','-=','*=','/=','%=','<<=','>>=','^=','|=','&='):
                if isinstance(statement, (Id, Script, Attr, Pointer, Arrow)):
                    statement = Assign(statement, Binary(next(self), statement, self.assign()))
                else:
                    self.error()
            else:
                if not isinstance(statement, (Call, Assign)):
                    self.error()
            self.expect(';')
            
        elif self.peek('type'):
            type_spec = Type(next(self))
            while self.accept('*'):
                type_spec = PointerType(type_spec)
            id_ = Id(self.expect('id'))
            while self.accept('['):
                type_spec = Array(type_spec, Const(self.expect('const')))
                self.expect(']')
                # if not self.accept(']'):
                #     sub = self.expect('const')
                #     self.expect(']')
                # else:
                #     sub = None
                # local = Script(local, sub)
            statement = Decl(type_spec, id_)
            if self.accept('='):
                statement = Assign(statement, self.assign())
            self.expect(';')
            
        elif self.accept('struct'):
            self.expect('id')
            while self.accept('*'):
                pass
            self.expect('id')
            if self.accept('='):
                self.const() #TODO make struct specific 
            self.expect(';')
            
        elif self.accept('union'):
            self.expect('id')
            while self.accept('*'):
                pass
            self.expect('id')
            if self.accept('='):
                self.const() #TODO make union specific 
            self.expect(';')
            
        elif self.accept('if'):
            self.expect('(')
            expr = self.expr()
            self.expect(')')
            statement = If(expr, self.statement())
            if self.accept('else'):
                statement.false = self.statement()
            
        elif self.accept('case'): #TODO
            self.const()
            self.expect(':')
            self.statement()
        elif self.accept('default'):
            self.expect(':')
            self.statement()        
        elif self.accept('switch'):
            self.expect('(')
            self.expr()
            self.expect(')')
            self.statement()
            
        elif self.accept('while'):
            self.expect('(')
            expr = self.expr()
            self.expect(')')
            statement = While(expr, self.statement())
            
        elif self.accept('do'): #TODO
            self.statement()
            self.expect('while')
            self.expect('(')
            self.expr()
            self.expect(')')
            self.expect(';')
            
        elif self.accept('for'):
            self.expect('(')
            init = self.expr()
            self.expect(';')
            cond = self.expr()
            self.expect(';')
            step = self.expr()
            self.expect(')')
            statement = For(init, cond, step, self.statement())
            
        elif self.accept('continue'):
            statement = Continue()
            self.expect(';')
            
        elif self.accept('break'):
            statement = Break()
            self.expect(';')
            
        elif self.accept('return'):
            statement = Return()
            if not self.accept(';'):
                statement.expr = self.expr()
                self.expect(';')
                
        return statement

    def block(self):
        '''
        BLOCK -> {STATE}
        '''
        block = Block()
        while self.peek('{','*','id','++','--','type','struct','union','if','switch','while','do','for','return','break','continue'):
            block.append(self.statement())
        return block
 
    def params(self):
        '''
        PARAMS -> TYPE_SPEC id {',' TYPE_SPEC id}
        '''
        params = Params()
        params.append(Decl(self.type_spec(), Id(self.expect('id'))))
        while self.accept(','):
            params.append(Decl(self.type_spec(), Id(self.expect('id'))))
        return params
    
    def decl(self):
        '''
        DECL -> TYPE_SPEC id {'[' [CONST] ']'} ['=' CONST] ';'
        '''
        type_spec = self.type_spec()
        id_ = self.expect('id')
        while self.accept('['):
            type_spec = Array(type_spec, Const(self.expect('const')))
            self.expect(']')
        decl = Decl(type_spec, id_)
        if self.accept('='):
            decl = Assign(decl, self.const())
        self.expect(';')
        return decl
 
    def program(self):
        program = Program()
        while self.peek('type','struct','union'):
            if self.peek('type'):
                type_spec = next(self),
                while self.accept('*'):
                    type_spec += '*',
                id_ = Id(self.expect('id'))
                if self.accept('('):
                    if not self.accept(')'):
                        params = self.params()
                        self.expect(')')
                    else:
                        params = Params()
                    if not self.accept(';'):
                        self.expect('{')
                        block = self.block()
                        self.expect('}')
                    else:
                        block = Block()
                    if id_.name == 'main':
                        program.insert(0, Main(block))
                    else:
                        program.append(Func(type_spec, id_, params, block))
                else:
                    while self.accept('['):
                        if not self.accept(']'):
                            self.const()
                            self.expect(']')
                    if self.accept('='): #TODO Allow uninitialized globals i.e. No '=' e.g. "int error;"
                        if self.peek('const'):
                            program.append(Global(id_, Const(next(self))))
                        elif self.peek('char'):
                            program.append(Global(id_, Char(next(self))))
                        elif self.peek('string'):
                            program.append(Global(id_, String(next(self))))
                        else:
                            self.error()
                    self.expect(';')
            elif self.accept('struct'):
                self.expect('id')
                while self.accept('*'):
                    pass
                if self.peek('id'):
                    next(self)
                    if self.accept('('):
                        if not self.accept(')'):
                            self.parameters()
                            self.expect(')')
                        if not self.accept(';'):
                            self.expect('{')
                            self.block()
                            self.expect('}')
                    else:
                        while self.accept('['):
                            if not self.accept(']'):
                                self.const()
                                self.expect(']')
                        if self.accept('='):
                            self.const()
                        self.expect(';')
                else:
                    if not self.accept(';'):
                        self.expect('{')
                        while not self.accept('}'):
                            self.decl()
                        self.expect(';')               
            elif self.accept('union'):
                self.expect('id')
                while self.accept('*'):
                    pass
                self.expect('id')
                if self.accept('('):
                    if not self.accept(')'):
                        self.parameters()
                        self.expect(')')
                    if not self.accept(';'):
                        self.expect('{')
                        self.block()
                        self.expect('}')
                elif self.accept('{'):
                    while not self.accept('}'):
                        self.decl()
        return program
    
    
    def parse(self, text):
        self.tokens = lex(text)
        #for i, (t, v) in enumerate(self.tokens): print(i, t, v)
        self.index = 0
        program = self.program()
        self.expect('end')
        return program
        
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
        
parser = Parser()

def parse(text):
    return parser.parse(text)