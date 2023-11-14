# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:47:39 2023

@author: Colin
"""

import re
import clexer
from cnodes import Program, Main, Func, List, Params, Block, Label, Goto, Break, Continue, For, Do, While, Switch, Case, If, Return, Glob, Attr, Local, Assign, Condition, Logic, Compare, Binary, Array, Struct, Pointer, Const, Type, Pre, Post, Deref, AddrOf, Unary, Args, Call, Arrow, SubScr, Dot, String, Char, Num, Frame

'''
TODO
[ ] Type checking
[X] '.' vs '->' checking
[ ] Cast
[X] Allocating local arrays
[X] Globals overhaul including global structs and arrays
[X] Init lists 
[X] Proper ++/--
[ ] Unions
[ ] Enums
[X] peekn
[X] labels and goto
[ ] Typedef
[ ] Error handling
[X] Generate vs Reduce
[X] Scope in Parser
[ ] Line numbers in errors
[X] Returning local structs
[ ] PREPROCESSING
    [X] include header files
    [ ] Macros??
'''

class Scope(Frame):
    def __init__(self, old=None):
        if old is None:
            super().__init__()
        else:            
            self.size = old.size
            self.data = old.data.copy()

class CParser:
    def resolve(self, name):
        if name in self.scope:
            return self.scope[name]
        elif name in self.functions:
            return self.functions[name]
        elif name in self.globs:
            return self.globs[name]
        else:
            self.error(f'name "{name}" not found')
    def primary(self):
        '''
        PRIMARY -> id|num|char|string|'(' EXPR ')'
        '''
        if self.peek('id'):
            return self.resolve(next(self).lexeme)
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
            self.error('PRIMARY EXPRESSION')
        return primary
    
    def postfix(self):
        '''
        POST -> PRIMARY {'[' EXPR ']'|'(' ARGS ')'|'.' id|'->' id|'++'|'--'}
        '''
        postfix = self.primary()
        while self.peek('.','[','->','(','++','--'):
            if self.accept('.'):
                postfix = Dot(postfix, postfix.type[self.expect('id').lexeme])
            elif self.accept('['):
                postfix = SubScr(postfix, self.expr())
                self.expect(']')
            elif self.accept('->'):
                postfix = Arrow(postfix, postfix.type.to[self.expect('id').lexeme])
            elif self.accept('('):
                # TODO assert type(postfix) is ...
                postfix = Call(postfix, self.args())
                self.expect(')')
                if self.calls is None:
                    self.calls = 0
                self.calls = max(self.calls, len(postfix.args))
            elif self.peek('++','--'):
                    postfix = Post(next(self), postfix)
            else:
                self.error('POSTFIX EXPRESSION')
        return postfix
    
    def args(self):
        '''
        ARGS -> ASSIGN {',' ASSIGN}
        '''
        args = Args()
        if not self.peek(')'):
            args.append(self.assign())
            while self.accept(','):
                args.append(self.assign())
        return args
    
    def unary(self):
        '''
        UNARY -> POSTFIX
                |('++'|'--') UNARY
                |('-'|'~'|'!'|'*'|'&') CAST
                |'sizeof' UNARY
                |'sizeof' '(' TYPE_SPEC ')'
        '''
        if self.peek('-','~',):
            return Unary(next(self), self.unary())
        elif self.accept('&'):
            return AddrOf(self.unary())
        elif self.accept('*'):
            return Deref(self.unary())
        elif self.peek('++','--'):
            return Pre(next(self), self.unary())
        else:
            return self.postfix()
    
    def type_spec(self):
        '''
        TYPE_SPEC -> (type|(('struct'|'union') id)) {'*'}
        '''
        if self.peek('type'):
            type_spec = Type(next(self))
        elif self.accept('struct'):
            type_spec = self.structs[self.expect('id').lexeme]
        else:
            self.error('TYPE SPECIFIER')
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
        while self.peek('*'):
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
            cond = Condition(cond, expr, self.cond())
        return cond
    
    def assign(self):
        '''
        ASSIGN -> UNARY ['+'|'-'|'*'|'/'|'%'|'<<'|'>>'|'^'|'|'|'&']'=' ASSIGN
                 |COND
        '''
        assign = self.cond()
        if self.accept('='):
            assert isinstance(assign, (Local,Dot,Arrow,SubScr,Deref))
            assign = Assign(assign, self.assign())
        elif self.peek('+=','-=','*=','/=','%=','<<=','>>=','^=','|=','&='):
            assert isinstance(assign, (Local,Dot,Arrow,SubScr,Deref))
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
        '''
        CONST -> EXPR
        '''
        return self.expr()
             
    def statement(self):
        '''
        STATE -> '{' BLOCK '}'
                |SELECT
                |LOOP
                |JUMP
                |ASSIGN ';'
        SELECT -> 'if' '(' EXPR ')' STATE ['else' STATE]|'switch' '(' EXPR ')' '{' {'case' CONST_EXPR ':' STATEMENT} ['default' ':' STATEMENT] '}'
        LOOP -> 'while' '(' EXPR ')' STATE|'for' '(' EXPR ';' EXPR ';' EXPR ')' STATE|'do' STATEMENT 'while' '(' EXPR ')' ';'
        JUMP -> 'goto' ';'|'return' [EXPR] ';' |'break' ';' |'continue' ';'
        '''
        if self.accept('{'):            
            self.begin_scope()
            statement = self.block()
            self.end_scope()
            self.expect('}')
            
        elif self.accept('if'):
            self.expect('(')
            expr = self.expr()
            self.expect(')')
            statement = If(expr, self.statement())
            if self.accept('else'):
                statement.false = self.statement()
            
        elif self.accept('switch'):
            self.expect('(')
            test = self.expr()
            self.expect(')')
            self.expect('{')
            statement = Switch(test)
            while self.accept('case'):
                const = self.const_expr()
                self.expect(':')
                statement.cases.append(Case(const, self.statement()))
            if self.accept('default'):
                self.expect(':')
                statement.default = self.statement()
            self.expect('}')
            
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
        
        elif self.accept('return'):
            statement = Return()
            if not self.accept(';'):
                statement.expr = self.expr()
                self.expect(';')
            
        elif self.accept('break'):
            statement = Break()
            self.expect(';') 
            
        elif self.accept('continue'):
            statement = Continue()
            self.expect(';')   
        
        elif self.accept('goto'):
            statement = Goto(self.expect('id'))
            self.expect(';') 
        
        elif self.peekn('id',':'):
            statement = Label(next(self))
            next(self)
        
        else:
            statement = self.assign()
            assert isinstance(statement, (Assign, Call, Pre, Post))
            self.expect(';')
            
        return statement

    def block(self):
        '''
        BLOCK -> {DECL} {STATE} [BLOCK]
        '''
        block = Block()
        while self.peek('const','type','struct','union'):
            block.append(self.init())
        while self.peek('{','id','*','++','--','return','if','switch','while','do','for','break','continue','goto'):
            block.append(self.statement())
        if not (self.peek('}') or self.peek('end')):# or (len(block) > 0):
            block.extend(self.block())        
        return block
    
    def init(self):
        '''
        INIT -> DECL ['=' EXPR] ';'
        '''
        init = self.decl()
        if self.accept('='):
            if self.accept('{'):
                init = Assign(init, self.init_list())
                self.expect('}')
            else:
                init = Assign(init, self.expr())
        self.expect(';')
        return init
    
    def abstract(self):
        abstract = self.type_qual()
        while self.accept('*'):
            abstract = Pointer(abstract)
        return abstract
    
    def decl(self):
        '''
        DECL -> TYPE_QUAL id {'[' [num] ']'}
        '''
        type = self.abstract()
        id = self.expect('id')
        while self.accept('['):
            type = Array(type, Num(self.expect('num')))
            self.expect(']')
        local = Local(type, id)
        self.scope[id.lexeme] = local
        self.space += type.size
        return local

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
    
    def init_list(self):
        '''
        INIT_LIST -> CONST|'{' INIT_LIST {',' INIT_LIST} '}'
        '''
        init = List()
        if self.accept('{'):    
            init.extend(self.init_list())
            self.expect('}')
        else:
            init.append(self.const_expr())
        while self.accept(','):
            if self.accept('{'):
                init.extend(self.init_list())
                self.expect('}')
            else:
                init.append(self.const_expr())
        return init
    
    def program(self):
        program = Program()
        while self.peek('type','const','struct'):
            if self.peekn('struct','id','{'):
                next(self)
                id = next(self)
                next(self)
                struct = Struct(id.lexeme)
                self.structs[id.lexeme] = struct
                while not self.accept('}'):
                    type = self.abstract()
                    id = self.expect('id')
                    struct[id.lexeme] = Attr(type, id)
                    self.expect(';')
                self.expect(';')
            else:
                type = self.abstract()
                id = self.expect('id')
                if self.accept('('):                    #Function
                    self.begin_func()
                    self.calls = None
                    self.space = 0
                    self.begin_scope()
                    params = self.params()
                    self.expect(')')
                    self.functions[id.lexeme] = Local(type, id)
                    self.expect('{')
                    block = self.block()
                    self.end_scope()
                    self.expect('}')
                    if id.lexeme == 'main':
                        program.insert(0, Main(block, self.space))
                    else:
                        program.append(Func(type, id, params, block, self.calls, self.space))
                else:                                   #Global
                    while self.accept('['):
                        type = Array(type)
                        self.expect(']')
                    glob = Glob(type, id)
                    if self.accept('='):
                        if self.accept('{'):
                            glob.init = self.init_list()
                            self.expect('}')
                        else:
                            glob.init = self.expr()
                    self.expect(';')
                    self.globs[id.lexeme] = glob
                    program.append(glob)
        return program
    
    def preprocess(self):
        self.index = 0
        while self.index < len(self.tokens):
            if self.peek('#'):
                start = self.index
                next(self)
                if self.accept('include'):
                    if self.peek('string'):
                        file_name = next(self).lexeme[1:-1]
                        end = self.index
                        with open(file_name, 'r') as header:
                            self.tokens[start:end] = clexer.lex(header.read())[:-1]
                    elif self.accept('<'):
                        file_name = next(self).lexeme
                        self.expect('.')
                        if self.expect('id').lexeme != 'h':
                            self.error('h')
                        self.expect('>')
                        end = self.index
                        with open(f'std\{file_name}.h', 'r') as header:
                            self.tokens[start:end] = clexer.lex(header.read())[:-1]
                    else:
                        self.error()
                    self.index = start
                else:
                    self.error()
            else:
                next(self)
    
    def begin_func(self):
        self.space = 0
        self.returns = False
        self.calls = False
    def begin_scope(self):
        new = Scope(self.scope)
        self.stack.append(self.scope)
        self.scope = new
    def end_scope(self):
        self.scope = self.stack.pop() 
    
    def parse(self, text):
        self.included = set()
        self.scope = Scope()
        self.stack = []
        self.functions = {}
        self.structs = {}
        self.globs = {}
        self.tokens = clexer.lex(text)
        self.preprocess()
        # for i, t in enumerate(self.tokens): print(i, t.type, t.lexeme)
        self.index = 0
        program = self.program()
        self.expect('end')
        return program
        
    def __next__(self):
        token = self.tokens[self.index]
        self.index += 1
        return token
        
    def peek(self, *symbols, offset=0):
        token = self.tokens[self.index+offset]
        return token.type in symbols or (not token.lexeme.isalnum() and token.lexeme in symbols)
    
    def peekn(self, *buckets):
        if self.index+len(buckets) < len(self.tokens)-1:
            for i, bucket in enumerate(buckets):
                if type(bucket) is str:
                    bucket = (bucket,)
                if not self.peek(*bucket, offset=i):
                    return False
            return True
        return False          
    
    def peek2(self, sym1, sym2):
        if self.index < len(self.tokens) - 1:            
            return self.peek(sym1) and self.peek(sym2, offset=1)
    
    def accept(self, *symbols):
        if self.peek(*symbols):
            return next(self)
    
    def expect(self, symbol): 
        if self.peek(symbol):
            return next(self)
        self.error(symbol)
        
    def error(self, expected=None):
        error = self.tokens[self.index]
        raise SyntaxError(f'Line {error.line_no}: Unexpected {error.type} token "{error.lexeme}".'+ (f' Expected "{expected}"' if expected is not None else ''))
        
parser = CParser()

def parse(text):
    return parser.parse(text)