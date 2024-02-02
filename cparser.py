# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:47:39 2023

@author: Colin
"""

import clexer
from cnodes import Program, Main, Defn, Params, Block, Label, Goto, Break, Continue, For, Do, While, Switch, Case, If, Statement, Return, Func, Glob, Attr, Param, Local, InitList, Assign, Condition, Logic, Compare, Binary, Array, Struct, Pointer, Const, VoidPtr, Type, Void, Pre, Cast, SizeOf, Deref, AddrOf, Not, Unary, Args, Call, Arrow, SubScr, Dot, Post, String, Char, Num, Frame

'''
TODO
[X] Type checking
[X] '.' vs '->' checking
[X] Cast
[X] Allocating local arrays
[X] Globals overhaul including global structs and arrays
[X] Init lists 
[X] Proper ++/--
[ ] Unions
[ ] Enums
[X] peekn
[X] Labels and goto
[X] Division/Modulo
[X] Different calling convention. Went with stdcall-like
[X] Fix void and void*
[ ] Fix compile function?
[X] Update Docs
[ ] Typedef
[ ] Error handling
[X] Generate vs Reduce
[X] Scope in Parser
[X] Line numbers in errors
[X] Returning local structs
[X] PREPROCESSING
    [X] include header files
    [X] Macros
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
        if name in self.param_scope:
            return self.param_scope[name]
        elif name in self.scope:
            return self.scope[name]
        elif name in self.functions:
            return self.functions[name]
        elif name in self.globs:
            return self.globs[name]
        else:
            self.error(f'Name "{name}" not found')
    
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
            if self.peek('.'):
                postfix = Dot(next(self), postfix, postfix.type[self.expect('id').lexeme])
            elif self.peek('['):
                postfix = SubScr(next(self), postfix, self.expr())
                self.expect(']')
            elif self.peek('->'):
                postfix = Arrow(next(self), postfix, postfix.type.to[self.expect('id').lexeme])
            elif self.accept('('):
                assert type(postfix) is Func
                postfix = Call(postfix, self.args())
                self.expect(')')
                self.calls = True
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
                |'sizeof' '(' ABSTRACT ')'
        '''
        if self.peek('-','~',):
            return Unary(next(self), self.unary())
        if self.peek('!'):
            return Not(next(self), self.unary())
        elif self.peek('&'):
            return AddrOf(next(self), self.unary())
        elif self.peek('*'):
            return Deref(next(self), self.unary())
        elif self.peek('++','--'):
            return Pre(next(self), self.unary())
        elif self.accept('sizeof'):
            unary = SizeOf(self.expect('('), self.abstract())
            self.expect(')')
            return unary
        else:
            return self.postfix()
    
    def cast(self):
        '''
        CAST -> UNARY
               |'(' ABSTRACT ')' CAST
        '''
        if self.peekn('(', ('type','voidptr','struct','union','enum','const')):
            token = next(self)
            type = self.abstract()
            self.expect(')')
            return Cast(type, token, self.cast())
        else:
            return self.unary()
    
    def spec(self):
        '''
        TYPE_SPEC -> type|('struct'|'union') id
        '''
        if self.peek('type'):
            spec = Type(next(self).lexeme)
        elif self.accept('voidptr'):
            spec = VoidPtr(None)
        elif self.accept('struct'):
            spec = self.structs[self.expect('id').lexeme]
        elif self.accept('union') :
            spec = ...
        elif self.accept('enum') :
            spec = ...
        else:
            self.error('TYPE SPECIFIER')
        return spec
    
    def qual(self):
        '''
        TYPE_QUAL -> ['const'] TYPE_SPEC
        '''
        if self.accept('const'):
            return Const(self.spec())
        return self.spec()
    
    def abstract(self):
        '''
        ABSTRACT -> TYPE_QUAL {'*'}
        '''
        abstract = self.qual()
        while self.accept('*'):
            abstract = Pointer(abstract)
        return abstract
    
    def include_divmod(self, op):
        op = {'/':'div',
              '%':'mod'}.get(op[0])
        if not getattr(self, op):
            with open(f'std//{op}.h') as file:
                self.tokens[-1:] = clexer.lex(file.read())
            setattr(self, op, True)
    
    def mul(self):
        '''
        MUL -> UNARY {('*'|'/'|'%') UNARY}
        '''
        mul = self.cast()
        while self.peek('*','/','%'):
            token = next(self)
            if token.lexeme in ['/','%']:
                self.include_divmod(token.lexeme)
            mul = Binary(token, mul, self.cast())
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
        if self.peek('='):
            assert isinstance(assign, (Local,Glob,Dot,Arrow,SubScr,Deref)), f'Line {self.tokens[self.index].line_no}: {type(assign)}'
            assign = Assign(next(self), assign, self.assign())
        elif self.peek('+=','-=','*=','/=','%=','<<=','>>=','^=','|=','&=','/=','%='):
            assert isinstance(assign, (Local,Glob,Dot,Arrow,SubScr,Deref))
            token = next(self)
            if token.lexeme in ['/=','%=']:
                self.include_divmod(token.lexeme)
            assign = Assign(token, assign, Binary(token, assign, self.assign()))
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
        SELECT -> 'if' '(' EXPR ')' STATEMENT ['else' STATEMENT]
                 |'switch' '(' EXPR ')' '{' {'case' CONST_EXPR ':' STATEMENT} ['default' ':' STATEMENT] '}'
        LOOP -> 'while' '(' EXPR ')' STATEMENT
               |'for' '(' EXPR ';' EXPR ';' EXPR ')' STATEMENT
               |'do' STATEMENT 'while' '(' EXPR ')' ';'
        JUMP -> 'goto' id ';'
               |'return' [EXPR] ';'
               |'break' ';'
               |'continue' ';'
        '''
        
        if self.accept(';'):
            statement = Statement()
        
        elif self.accept('{'):            
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
        
        elif self.peek('return'):
            self.returns = True
            token = next(self)
            if self.accept(';'):
                statement = Return(token, None)
            else:                
                statement = Return(token, self.expr())
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
        return local
    
    def init(self):
        '''
        INIT -> DECL ['=' (EXPR|INIT_LIST)] ';'
        '''
        init = self.decl()
        if self.peek('='):
            token = next(self)
            if self.accept('{'):
                assert type(init.type) in [Array, Struct]
                init = InitList(token, init, self.list())
                self.expect('}')
            else:
                init = Assign(token, init, self.expr())
        self.expect(';')
        return init
    
    def list(self):
        '''
        INIT_LIST -> CONST|'{' INIT_LIST {',' INIT_LIST} '}'
        '''
        init = []
        if self.accept('{'):    
            init.extend(self.list())
            self.expect('}')
        else:
            init.append(self.expr())
        while self.accept(','):
            if self.accept('{'):
                init.extend(self.list())
                self.expect('}')
            else:
                init.append(self.expr())
        return init

    def param(self):
        type = self.abstract()
        id = self.expect('id')
        while self.accept('['):
            type = Pointer(type)
            self.expect(']')
        param = Param(type, id)
        self.param_scope[id.lexeme] = param
        return param

    def params(self):
        '''
        PARAMS -> [DECL {',' DECL}]
        '''
        params = Params()
        params.variable = False
        if not self.peek(')'):
            params.append(self.param())
            while self.accept(','):
                if self.accept('...'):
                    params.variable = True
                    break
                params.append(self.param())
        return params

    def block(self):
        '''
        BLOCK -> {DECL} {STATE} [BLOCK]
        '''
        block = Block()
        while self.peek('const','type','voidptr','struct','union','enum'):
            block.append(self.init())
        while self.peek(';','{','(','id','*','++','--','return','if','switch','while','do','for','break','continue','goto'):
            block.append(self.statement())
        if not (self.peek('}') or self.peek('end')):# or (len(block) > 0):
            block.extend(self.block())        
        return block
    
    def program(self):
        program = Program()
        while self.peek('const','voidptr','void','type','struct','union','enum'):
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
                if self.accept('void'):
                    type = Void()
                else:
                    type = self.abstract()
                id = self.expect('id')
                if self.accept('('):                    #Function
                    self.begin_func()
                    params = self.params()
                    self.expect(')')
                    self.functions[id.lexeme] = Func(type, id, params)
                    self.expect('{')
                    block = self.block()
                    self.end_func()
                    self.expect('}')
                    if id.lexeme == 'main':
                        program.insert(0, Main(block, self.calls, self.space))
                    else:
                        program.append(Defn(type, id, params, block, self.returns, self.calls, self.space))
                else:                                   #Global
                    while self.accept('['):
                        type = Array(type, Num(self.expect('num')))
                        self.expect(']')
                    glob = Glob(type, id)
                    if self.accept('='):
                        if self.accept('{'):
                            glob.init = self.list()
                            self.expect('}')
                        else:
                            glob.init = self.expr()
                    self.expect(';')
                    self.globs[id.lexeme] = glob
                    program.append(glob)
        return program
    
    def begin_func(self):
        self.space = 0
        self.returns = False
        self.calls = False
        self.scope = None
        self.param_scope = Scope()
        self.stack = []
        self.begin_scope()
        
    def end_func(self):
        self.end_scope()
        
    def begin_scope(self):
        new = Scope(self.scope)
        self.stack.append(self.scope)
        self.scope = new
    
    def end_scope(self):
        self.space = max(self.space, self.scope.size)
        self.scope = self.stack.pop() 
    
    def parse(self, text):
        self.scope = None
        self.stack = []
        self.functions = {}
        self.structs = {}
        self.globs = {}
        self.div = False
        self.mod = False
        self.tokens = clexer.lex(text)
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
    
    def accept(self, *symbols):
        if self.peek(*symbols):
            return next(self)
    
    def expect(self, symbol): 
        if self.peek(symbol):
            return next(self)
        self.error(f'Expected "{symbol}"')
        
    def error(self, msg=None):
        error = self.tokens[self.index]
        raise SyntaxError(f'Line {error.line_no}: Unexpected {error.type} token "{error.lexeme}".'+(f' {msg}.' if msg is not None else ''))
        
parser = CParser()

def parse(text):
    return parser.parse(text)