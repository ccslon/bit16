# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 19:47:39 2023

@author: Colin
"""

import clexer
from cnodes import Program, Main, Defn, Block, Label, Goto, Break, Continue, For, Do, While, Switch, Case, If, Statement, Return, Glob, Attr, Local, InitList, Assign, Condition, Logic, Compare, Binary, Func, Array, Union, Struct, Pointer, Const, Type, Void, Pre, Cast, SizeOf, Deref, AddrOf, Not, Unary, Args, Call, Arrow, SubScr, Dot, Post, String, Char, EnumConst, Num, Frame

'''
TODO
[X] Type checking
[X] '.' vs '->' checking
[X] Cast
[X] Allocating local arrays
[X] Globals overhaul including global structs and arrays
[X] Init lists
[X] Proper ++/--
[X] Unions. But could be better
[X] Enums
[X] peekn
[X] Labels and goto
[X] Division/Modulo
[X] Different calling convention. Went with stdcall-like
[ ] Fix void and void*
[X] Fix compile function?
[X] Update Docs
[X] Typedef
[ ] Const expressions
[X] Function pointers
[ ] Function defs in function defs
[ ] Error handling
[X] Generate vs Reduce
[X] Scope in Parser
[X] Line numbers in errors
[X] Returning local structs
[X] PREPROCESSING
    [X] Include header files
    [X] Macros
'''

class Scope(Frame):
    def copy(self):
        copy = Scope()
        copy.size = self.size
        copy.data = self.data.copy()
        return copy

class CParser:

    def resolve(self, name):
        if name in self.param_scope:
            return self.param_scope[name]
        elif name in self.scope:
            return self.scope[name]
        elif name in self.globs:
            return self.globs[name]
        elif name in self.enum_consts:
            return self.enum_consts[name]
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
            if self.peek('['):
                postfix = SubScr(next(self), postfix, self.expr())
                self.expect(']')
            elif self.accept('('):
                assert isinstance(postfix.type, Func)
                postfix = Call(postfix, self.args())
                self.expect(')')
                self.calls = True
            elif self.peek('.'):
                postfix = Dot(next(self), postfix, postfix.type[self.expect('id').lexeme])
            elif self.peek('->'):
                postfix = Arrow(next(self), postfix, postfix.type.to[self.expect('id').lexeme])
            elif self.peek('++','--'):
                    postfix = Post(next(self), postfix)
        return postfix

    def args(self):
        '''
        ARGS -> [ASSIGN {',' ASSIGN}]
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
                |('-'|'~'|'*'|'&'|'!') CAST
                |'sizeof' '(' TYPE_NAME ')'
                |'sizeof' UNARY
        '''
        if self.peek('++','--'):
            return Pre(next(self), self.unary())
        elif self.peek('-','~'):
            return Unary(next(self), self.cast())
        elif self.peek('*'):
            return Deref(next(self), self.cast())
        elif self.peek('&'):
            return AddrOf(next(self), self.cast())
        elif self.peek('!'):
            return Not(next(self), self.cast())
        elif self.peek('sizeof'):
            token = next(self)
            if self.accept('('):
                unary = SizeOf(token, self.type_name())
                self.expect(')')
            else:
                unary = SizeOf(token, self.unary().type)
            return unary
        else:
            return self.postfix()

    def cast(self):
        '''
        CAST -> UNARY
               |'(' TYPE_NAME ')' CAST
        '''
        if self.peekn('(', ('type','struct','void','const','union','enum')) or self.peek('(') and self.peek_typedefs(1):
            token = next(self)
            type = self.type_name()
            self.expect(')')
            return Cast(type, token, self.cast())
        else:
            return self.unary()

    def mul(self):
        '''
        MUL -> CAST {('*'|'/'|'%') CAST}
        '''
        mul = self.cast()
        while self.peek('*','/','%'):
            mul = Binary(next(self), mul, self.cast())
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
        RELA -> SHIFT {('<'|'>'|'<='|'>=') SHIFT}
        '''
        relation = self.shift()
        while self.peek('<','>','<=','>='):
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
            assert isinstance(assign, (Local,Glob,Dot,Arrow,SubScr,Deref)), f'Line {self.tokens[self.index].line}: {type(assign)}'
            assign = Assign(next(self), assign, self.assign())
        elif self.peek('+=','-=','*=','/=','%=','<<=','>>=','^=','|=','&=','/=','%='):
            assert isinstance(assign, (Local,Glob,Dot,Arrow,SubScr,Deref))
            token = next(self)
            assign = Assign(token, assign, Binary(token, assign, self.assign()))
        return assign

    def expr(self):
        '''
        EXPR -> ASSIGN
        '''
        return self.assign()
        # while self.accept(','): #TODO
        #     self.assign()

    def const(self): #TODO
        '''
        CONST -> COND
        '''
        return self.cond()

    def enum(self, value):
        '''
        ENUM -> id ['=' num]
        '''
        id = self.expect('id')
        if self.accept('='):
            value = Num(self.expect('num')).value
        self.enum_consts[id.lexeme] = EnumConst(id, value)
        return value

    def attr(self, spec, type):
        '''
        ATTR -> {'*'} [id] {'[' num ']'}
               |{'*'} '(' '*' [id] ')' '(' PARAMS ')'
        '''
        while self.accept('*'):
            type = Pointer(type)
        if self.accept('('):
            self.expect('*')
            id = self.accept('id')
            self.expect(')')
            self.expect('(')
            params, variable = self.params()
            type = Pointer(Func(type, [param.type for param in params], variable))
            self.expect(')')
        else:
            id = self.accept('id')
            while self.accept('['):
                type = Array(type, Num(self.expect('num')))
                self.expect(']')
        spec[id.lexeme] = Attr(type, id)

    def spec(self):
        '''
        TYPE_SPEC -> type
                    |void
                    |id
                    |('struct'|'union') id '{' {QUAL ATTR {',' ATTR} ';'} '}'
                    |'enum' id '{' ENUM {',' ENUM}'}'
        '''
        if self.peek('type'):
            spec = Type(next(self).lexeme)
        elif self.accept('void'):
            spec = Void()
        elif self.peek('id'):
            spec = self.typedefs[next(self).lexeme]
        elif self.accept('struct'):
            id = self.accept('id')
            if self.accept('{'):
                spec = Struct(id.lexeme)
                if id:
                    self.structs[id.lexeme] = spec
                while not self.accept('}'):
                    type = self.qual()
                    self.attr(spec, type)
                    while self.accept(','):
                        self.attr(spec, type)
                    self.expect(';')
            else:
                spec = self.structs[id.lexeme]
        elif self.accept('union'):
            id = self.accept('id')
            if self.accept('{'):
                spec = Union(id.lexeme)
                if id:
                    self.unions[id.lexeme] = spec
                while not self.accept('}'):
                    type = self.qual()
                    self.attr(spec, type)
                    while self.accept(','):
                        self.attr(spec, type)
                    self.expect(';')
            else:
                spec = self.unions[id.lexeme]
        elif self.accept('enum'):
            id = self.accept('id')
            if self.accept('{'):
                if id:
                    self.enums.append(id.lexeme)
                value = self.enum(0)
                while self.accept(','):
                    value += 1
                    value = self.enum(value)
                self.expect('}')
            else:
                assert id and id.lexeme in self.enums
            spec = Type('int')
        else:
            self.error('TYPE SPECIFIER')
        return spec

    def qual(self):
        '''
        TYPE_QUAL -> ['const'] SPEC
        '''
        if self.accept('const'):
            return Const(self.spec())
        return self.spec()

    def type_name(self):
        '''
        TYPE_NAME -> QUAL {'*'}
        '''
        type_name = self.qual()
        while self.accept('*'):
            type_name = Pointer(type_name)
        while self.accept('['):
            type_name = Array(type_name, Num(self.expect('num')))
            self.expect(']')
        return type_name

    def declr(self, type):
        '''
        DECLR -> {'*'} id {'[' num ']'}
        '''
        while self.accept('*'):
            type = Pointer(type)
        id = self.expect('id')
        while self.accept('['):
            type = Array(type, Num(self.expect('num')))
            self.expect(']')
        declr = self.scope[id.lexeme] = Local(type, id)
        return declr

    def init(self, type, inits):
        '''
        INIT -> DECLR ['=' (EXPR|'{' INIT_LIST '}')]
        '''
        declr = self.declr(type)
        if self.peek('='):
            token = next(self)
            if self.accept('{'):
                assert isinstance(declr.type, (Array, Struct))
                inits.append(InitList(token, declr, self.list()))
                self.expect('}')
            else:
                inits.append(Assign(token, declr, self.expr()))
    def decln(self):
        '''
        DECLN -> QUAL [INIT {',' INIT}] ';'
        '''
        type = self.qual()
        inits = []
        if not self.accept(';'):
            self.init(type, inits)
            while self.accept(','):
                self.init(type, inits)
            self.expect(';')
        return inits

    def list(self):
        '''
        INIT_LIST -> EXPR|'{' INIT_LIST {',' INIT_LIST} '}'
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
        '''
        PARAM -> QUAL [id] {'[' ']'}
                |QUAL '(' '*' [id] ')' '(' PARAMS ')'
        '''
        type = self.qual()
        while self.accept('*'):
            type = Pointer(type)
        if self.accept('('):
            self.expect('*')
            id = self.accept('id')
            self.expect(')')
            self.expect('(')
            params, variable = self.params()
            type = Pointer(Func(type, [param.type for param in params], variable))
            self.expect(')')
        else:
            id = self.accept('id')
            while self.accept('['):
                type = Pointer(type)
                self.expect(']')
        param = Local(type, id)
        if id:
            self.param_scope[id.lexeme] = param
        return param

    def params(self):
        '''
        PARAMS -> [PARAM {',' PARAM} [',' '...']]
        '''
        params = []
        variable = False
        if not self.peek(')'):
            params.append(self.param())
            while self.accept(','):
                if self.accept('...'):
                    variable = True
                    break
                params.append(self.param())
        return params, variable

    def statement(self):
        '''
        STATE -> ';'
                |'{' BLOCK '}'
                |SELECT
                |LOOP
                |JUMP
                |id ':'
                |ASSIGN ';'
        SELECT -> 'if' '(' EXPR ')' STATEMENT ['else' STATEMENT]
                 |'switch' '(' EXPR ')' '{' {'case' CONST_EXPR ':' STATEMENT} ['default' ':' STATEMENT] '}'
        LOOP -> 'while' '(' EXPR ')' STATEMENT
               |'for' '(' [EXPR {',' EXPR}] ';' EXPR ';' [EXPR {',' EXPR}] ')' STATEMENT
               |'do' STATEMENT 'while' '(' EXPR ')' ';'
        JUMP -> 'return' [EXPR] ';'
               |'break' ';'
               |'continue' ';'
               |'goto' id ';'
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
                const = self.const()
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

        elif self.accept('for'):
            self.expect('(')
            inits = []
            if not self.accept(';'):
                inits.append(self.expr())
                while self.accept(','):
                    inits.append(self.expr())
                self.expect(';')
            cond = self.expr()
            self.expect(';')
            steps = []
            if not self.accept(')'):
                steps.append(self.expr())
                while self.accept(','):
                    steps.append(self.expr())
                self.expect(')')
            statement = For(inits, cond, steps, self.statement())

        elif self.accept('do'):
            statement = self.statement()
            self.expect('while')
            self.expect('(')
            statement = Do(statement, self.expr())
            self.expect(')')
            self.expect(';')

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
            statement = self.expr()
            self.expect(';')

        return statement

    def block(self):
        '''
        BLOCK -> {'typedef' ('void'|QUAL) id ';'} {DECL} {STATE} [BLOCK]
        '''
        block = Block()
        while self.accept('typedef'):
            type = self.qual()
            while self.accept('*'):
                type = Pointer(type)
            id = self.accept('id')
            self.typedefs[id.lexeme] = type
            self.expect(';')
        while self.peek('type','struct','void','const','union','enum') or self.peek_typedefs():
            block.extend(self.decln())
        while self.peek(';','{','(','id','*','++','--','return','if','switch','while','do','for','break','continue','goto') and not self.peek_typedefs():
            block.append(self.statement())
        if block:
            block.extend(self.block())
        return block

    def program(self):
        program = Program()
        while not self.peek('end'):
            if self.accept('typedef'):
                type = self.qual()
                while self.accept('*'):
                    type = Pointer(type)
                id = self.accept('id')
                self.typedefs[id.lexeme] = type
                self.expect(';')
            else:
                type = self.qual()
                while self.accept('*'):
                    type = Pointer(type)
                id = self.accept('id')
                if self.accept('('):                    #Function
                    assert id is not None
                    self.begin_func()
                    params, variable = self.params()
                    type = Func(type, [param.type for param in params], variable)
                    self.expect(')')
                    self.globs[id.lexeme] = Glob(type, id)
                    if self.accept('{'):
                        assert not any(param.token is None for param in params)
                        block = self.block()
                        self.expect('}')
                        self.end_func()
                        if id.lexeme == 'main':
                            program.append(Main(block, self.calls, self.space))
                        else:
                            program.append(Defn(type, id, params, block, self.returns, self.calls, self.space))
                    else:
                        self.expect(';')
                        self.end_func()
                else:
                    if id:                              #Global
                        assert not isinstance(type, Void)
                        while self.accept('['):
                            type = Array(type, Num(self.expect('num')))
                            self.expect(']')
                        glob = Glob(type, id)
                        if self.accept('='):
                            if self.accept('{'):
                                assert isinstance(glob.type, (Array, Struct))
                                glob.init = self.list()
                                self.expect('}')
                            else:
                                glob.init = self.const()
                        self.globs[id.lexeme] = glob
                        program.append(glob)
                    self.expect(';')
        return program

    def peek_typedefs(self, offset=0):
        return self.peek('id', offset=offset) and self.tokens[self.index+offset].lexeme in self.typedefs

    def begin_func(self):
        self.space = 0
        self.returns = False
        self.calls = False
        self.scope = Scope()
        self.param_scope = Scope()
        self.stack = []
        self.begin_scope()

    def end_func(self):
        self.end_scope()

    def begin_scope(self):
        self.stack.append((self.scope, self.structs, self.typedefs, self.unions, self.enums, self.enum_consts))
        self.scope = self.scope.copy()
        self.structs = self.structs.copy()
        self.typedefs = self.typedefs.copy()
        self.unions = self.unions.copy()
        self.enums = self.enums.copy()
        self.enum_consts = self.enum_consts.copy()

    def end_scope(self):
        self.space = max(self.space, self.scope.size)
        self.scope, self.structs, self.typedefs, self.unions, self.enums, self.enum_consts = self.stack.pop()

    def parse(self, text):
        self.stack = []
        self.structs = {}
        self.typedefs = {}
        self.unions = {}
        self.enums = []
        self.enum_consts = {}
        self.globs = {}
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
        raise SyntaxError(f'Line {error.line}: Unexpected {error.type} token "{error.lexeme}".'+(f' {msg}.' if msg is not None else ''))

parser = CParser()

def parse(text):
    return parser.parse(text)