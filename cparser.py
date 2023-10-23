# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:47:39 2023

@author: Colin
"""

import re
from cnodes import Const, Do, Decl, Array, StructType, PointerType, Type, Conditional, Cast, Arrow, Id, Num, Unary, Binary, Compare, Call, Args, Func, Assign, If, Block, Program, Return, While, For, Break, Continue, Script, Struct, Params, Fields, Logic, Dot, Pointer, Address, Main, Global, Char, String

'''
TODO
[ ] Type checking
[ ] '.' vs '->' checking
[X] Allocating arrays
'''

TOKENS = {'num': r'(0x[0-9a-f]+)|(0b[01]+)|(\d+)|(NULL)',
          'char': r"'\\?[^']'",
          'string': r'"[^"]*"',
          'const': r'const',
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
          'include': r'include',
          'id': r'\w(\w|\d)*',
          'semi': r';',
          'colon': r':',
          'arrow': r'->',
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
          'deq': r'==',
          'ge': r'>=',
          'le': r'<=',
          'eq': r'=',
          'ne': r'!=',
          'gt': r'>',
          'lt': r'<',
          'hash': r'#',
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
        PRIMARY -> id|Num|char|string|'(' EXPR ')'
        '''
        if self.peek('id'):
            return Id(next(self))
        elif self.peek('num'):
            return Num(next(self))
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
                    postfix = Dot(postfix, self.expect('id'))
                elif self.accept('->'):
                    postfix = Arrow(postfix, self.expect('id'))
                elif self.peek('++','--'):
                    postfix = Assign(postfix, Binary(next(self), postfix, Num('1')))
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
            return Assign(unary, Binary(op, unary, Num('1')))
        elif self.peek('+','-','~',):
            return Unary(next(self), self.unary())
        elif self.accept('!'):
            unary = Call(Id('not'), Args([self.unary()]))
            self.include('stdlib')
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
            
    def cast(self): #TODO
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
        '''
        TYPE_SPEC -> (type|(('struct'|'union') id)) {'*'}
        '''
        if self.peek('type'):
            type_spec = Type(next(self))
        elif self.accept('struct','union'):
            type_spec = StructType(self.expect('id'))
        else:
            self.error()
        while self.accept('*'):
            type_spec = PointerType(type_spec)
        return type_spec
    
    def type_qual(self):
        '''
        TYPE_QUAL -> 'const' TYPE_SPEC
        '''
        if self.accept('const'):
            return Const(self.type_spec())
        return self.type_spec()
    
    def mul(self):
        '''
        MUL -> UNARY {('*'|'/'|'%') UNARY}
        '''
        mul = self.unary()
        while self.peek('*','/','%'):
            if self.peek('/','%'):
                mul = Call(Id('div' if next(self) == '/' else 'mod'), Args([mul, self.unary()]))
                self.include('stdlib')
            else:
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
    
    def cond(self): #TODO
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
            assert isinstance(assign, (Id, Script, Dot, Pointer, Arrow))
            assign = Assign(assign, self.assign())
        elif self.peek('+=','-=','*=','/=','%=','<<=','>>=','^=','|=','&='):
            assert isinstance(assign, (Id, Script, Dot, Pointer, Arrow))
            assign = Assign(assign, Binary(next(self), assign, self.assign()))
        return assign
    
    def expr(self):
        '''
        EXPR -> ASSIGN
        '''
        return self.assign()
        # while self.accept(','):
        #     self.assign()
    
    def const_expr(self):
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
                       
        elif self.accept('if'):
            self.expect('(')
            expr = self.expr()
            self.expect(')')
            statement = If(expr, self.statement())
            if self.accept('else'):
                statement.false = self.statement()
            
        elif self.accept('case'): #TODO
            self.Num()
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
            
        elif self.accept('do'):
            statement = self.statement()
            self.expect('while')
            self.expect('(')
            statement = Do(statement, self.expr())
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
        else:
            statement = self.assign()
            assert isinstance(statement, (Assign, Call))
            self.expect(';')
        return statement    

    def block(self):
        '''
        BLOCK -> {DECL} {STATE} [BLOCK]
        '''
        block = Block()        
        while self.peek('const','type','struct','union'):
            block.append(self.init())
        while self.peek('{','*','id','++','--','if','switch','while','do','for','return','break','continue'):
            block.append(self.statement())
        if not self.peek('}'):
            block.extend(self.block())
        return block
 
    def params(self):
        '''
        PARAMS -> [DECL {',' DECL}]
        '''
        params = Params()
        if self.peek('const','type','struct','union'):    
            params.append(self.decl())
            while self.accept(','):
                params.append(self.decl())
        return params
    
    def init(self):
        '''
        INIT -> DECL ['=' EXPR] ';'
        '''
        init = self.decl()
        if self.accept('='):
            init = Assign(init, self.expr())
        self.expect(';')
        return init
    
    def decl(self):
        '''
        DECL -> TYPE_QUAL id {'[' [num] ']'}
        '''
        type_qual = self.type_qual()
        iden = Id(self.expect('id'))
        while self.accept('['):
            type_qual = Array(type_qual, Num(self.expect('num')))
            self.expect(']')
        return Decl(type_qual, iden)
    
    def fields(self):
        '''
        FIELDS = '{' {DECL ';'} '}'
        '''
        fields = Fields()
        if self.accept('{'):    
            while not self.accept('}'):
                fields.append(self.decl())
                self.expect(';')
        return fields
 
    def program(self):
        program = Program()
        while self.accept('#'):
            if self.accept('include'):
                if self.accept('<'):
                    lib = self.expect('id')
                    self.expect('.')
                    assert self.expect('id') == 'h'
                    self.expect('>')
                    self.include(lib)
                elif self.peek('string'):
                    self.include_h(next(self))
                else:
                    self.error()
        while self.peek('type','struct','union','const'):
            type_qual = self.type_qual()
            if self.accept('{'):
                assert type(type_qual) not in [PointerType, Const]
                program.append(Struct(type_qual.name, self.fields()))
                self.expect('}')
                self.expect(';')
            else:
                iden = Id(self.expect('id'))
                if self.accept('('):
                    params = self.params()
                    self.expect(')')
                    self.expect('{')
                    block = self.block()
                    self.expect('}')
                    if iden.name == 'main':
                        program.insert(0, Main(block))
                    else:
                        program.append(Func(type_qual, iden, params, block))
                else:
                    while self.accept('['):
                        type_qual = Array(type_qual, Num(self.expect('num')))
                        self.expect(']')
                    init = Decl(type_qual, iden)
                    if self.accept('='):
                        init = Global(init, self.const_expr())
                    self.expect(';')
                    program.append(init)                     
        return program        
    
    def include_h(self, h):
        if h not in self.included:
            with open(h) as h_file:
                self.tokens[-1:] = lex(h_file.read())
            self.included.add(h)
    
    def include(self, lib):
        if lib not in self.included:
            with open(f'std\\{lib}.h') as lib_file:
                self.tokens[-1:] = lex(lib_file.read())
            self.included.add(lib)
    
    def parse(self, text):
        self.included = set()
        self.tokens = lex(text)
        # for i, (t, v) in enumerate(self.tokens): print(i, t, v)
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
        return type_ in symbols or (not value.isalnum() and value in symbols)
    
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